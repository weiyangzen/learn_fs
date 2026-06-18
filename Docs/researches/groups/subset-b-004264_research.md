# subset-b-004264 research

This grouped report covers selected Linux `drivers/misc` sources under `sources/distributed-fs/ceph-client`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_uv.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_uv.c

## Purpose
`xpc_uv.c` is the UV architecture backend for SGI/HPE Cross Partition Communication. It implements the `xpc_arch_operations` table for UV systems, using GRU message queues, UV BIOS watchlists, global physical addressing, heartbeat cachelines, and inter-partition activation/notification IRQs to support partition activation and channel payload delivery.

## Important APIs, Types, and Functions
The main exported entry points are `xpc_init_uv()` and `xpc_exit_uv()`, which install `xpc_arch_ops_uv` and create/destroy activation and notify GRU message queues. Queue construction is handled by `xpc_create_gru_mq_uv()`, `xpc_destroy_gru_mq_uv()`, `xpc_gru_mq_watchlist_alloc_uv()`, `xpc_get_gru_mq_irq_uv()`, and `xpc_send_gru_msg()`. Activation control uses `xpc_handle_activate_IRQ_uv()`, `xpc_handle_activate_mq_msg_uv()`, `xpc_send_activate_IRQ_uv()`, and local activation injection through `xpc_send_local_activate_IRQ_uv()`. Channel data flow uses `xpc_handle_notify_IRQ_uv()`, `xpc_handle_notify_mq_msg_uv()`, `xpc_send_payload_uv()`, `xpc_get_deliverable_payload_uv()`, and `xpc_received_payload_uv()`. UV-specific partition/channel state is stored in `struct xpc_partition_uv`, `struct xpc_channel_uv`, GRU descriptors, and FIFO lists.

## Control Flow
Initialization selects a NUMA node, creates two GRU message queues with IRQ handlers, publishes the local activation GRU descriptor and heartbeat GPA in the reserved page, and assigns the UV operation table. Remote activation messages update remote reserved-page data, heartbeat GPA, cached activation queue GPA, requested activation state, and channel-control flags before waking the heartbeat checker or channel manager. Channel open/close control is sent over the activation queue; payloads and ACKs are sent over the notify queue. Incoming notify messages either complete a sender slot when `size == 0` or copy a payload into a receive slot, enqueue it, and wake delivery kthreads or the channel manager.

## State and Persistence
All state is volatile kernel and UV partition state. Per-partition flags include cached remote activation queue descriptor validity and engaged/disengaged state. Heartbeat state is a cacheline-sized UV heartbeat value plus offline flag. Send slots, receive slots, cached notify descriptors, FIFO heads, and message queue pages live in kernel memory and are torn down on partition/channel or module exit. Remote accessibility is granted with `xp_expand_memprotect()` and revoked with `xp_restrict_memprotect()`.

## Dependencies and Integration Points
The file depends on UV hub and BIOS APIs, GRU kernel services, XPC common code, NUMA CPU/node selection, IRQ setup through UV MMR routing, remote memory copy helpers, and the global `xpc_partitions`/`xpc_rsvd_page` structures. It integrates with XPC channel management through `xpc_arch_ops`, with partition activation/deactivation through `XPC_DEACTIVATE_PARTITION()`, and with message delivery through XPC kthread wakeups.

## Risks and Edge Cases
`xpc_send_gru_msg()` retries indefinitely on queue-full or congestion conditions, which depends on eventual remote progress. Cached remote GRU descriptors can become stale and are invalidated only on activation updates or failed sends. Several paths use `BUG_ON()` for BIOS/watchlist/memory-protection failures, so unexpected platform errors are fatal. `xpc_init_mq_node()` passes the node id where a CPU argument is expected in the queue creation loop, making CPU/node assumptions worth reviewing. Locking spans mutexes, spinlocks, and channel locks; send failures can drop and reacquire channel locks around partition deactivation.

## Test Signals
Useful validation signals include successful UV-only initialization, creation of both GRU queues on the selected node, activation/deactivation handshakes across partitions, heartbeat change/offline detection, channel open/close flags, payload delivery and ACK slot recycling, stale descriptor recovery after remote restart, queue-full/congestion behavior under load, and clean `xpc_exit_uv()` teardown without memory-protection or IRQ leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpnet.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpnet.c

## Purpose
`xpnet.c` implements the XPNET virtual Ethernet device layered on XPC. It presents `xp0` as an Ethernet-like interface where MAC destination bytes identify SGI UV partition IDs and packets are transferred either embedded in an XPC message or by remote DMA-style copy from a cacheline-aligned buffer.

## Important APIs, Types, and Functions
`struct xpnet_message` is the XPC payload describing version, magic, embedded bytes, source physical address, size, and cacheline lead/tail ignore counts. `struct xpnet_pending_msg` tracks an skb and outstanding asynchronous XPC notifications. Network callbacks are `xpnet_dev_open()`, `xpnet_dev_stop()`, `xpnet_dev_hard_start_xmit()`, and `xpnet_dev_tx_timeout()`. XPC integration flows through `xpnet_connection_activity()`, `xpnet_receive()`, `xpnet_send()`, and `xpnet_send_completed()`. Module setup/teardown is `xpnet_init()` and `xpnet_exit()`.

## Control Flow
Module init runs only on UV systems, allocates the broadcast partition bitmap and Ethernet netdev, sets a locally administered MAC containing `xp_partition_id`, disables multicast, and registers the device. Opening the interface calls `xpc_connect()` on `XPC_NET_CHANNEL`. XPC connection events add/remove partition IDs from the broadcast bitmap and update carrier state. Transmit builds an `xpnet_message`, chooses broadcast or a single destination from MAC bytes, increments the pending count for each `xpc_send_notify()`, and frees the skb after all completion callbacks run. Receive validates version/magic, allocates an aligned skb, either copies embedded payload bytes or calls `xp_remote_memcpy()`, then submits the skb with `netif_rx()` and ACKs through `xpc_received()`.

## State and Persistence
The persistent runtime state is the registered `net_device`, its stats, carrier state, the broadcast bitmap protected by `xpnet_broadcast_lock`, and per-transmit pending-message counters. No durable state exists; partition connectivity is rebuilt from XPC events after interface open.

## Dependencies and Integration Points
The driver depends on XPC/XPNET constants from `xp.h`, Linux networking core, Ethernet address helpers, UV detection, remote physical address helpers, and XPC notify/receive callbacks. It integrates directly with `xpc_connect()`, `xpc_send_notify()`, `xpc_received()`, and the network stack `net_device_ops`.

## Risks and Edge Cases
The receive path can leak or strand an skb if `xp_remote_memcpy()` fails after `skb_put()`, as the source comment notes it cannot simply free the skb. IPv6 multicast destination byte `0x33` is dropped outright, and Ethernet multicast is disabled. Transmit stats are incremented even when no destination partition accepts a unicast/broadcast send. Cacheline alignment fields are critical: incorrect lead/tail values would expose extra bytes or truncate data.

## Test Signals
Exercise interface open/close, XPC connection/disconnection carrier changes, partition-ID MAC addressing, broadcast delivery to multiple connected partitions, embedded small packets, large remote-copy packets, completion callback skb lifetime, remote copy failure handling, MTU bounds, and packet stats under no-destination traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/smpro-errmon.c -->
# sources/distributed-fs/ceph-client/drivers/misc/smpro-errmon.c

## Purpose
`smpro-errmon.c` exposes Ampere Altra SMpro/PMPRO RAS error, warning, event, overflow, and DIMM syndrome data through sysfs attributes backed by the parent SMpro regmap.

## Important APIs, Types, and Functions
`struct smpro_errmon` stores the parent `regmap`. `struct smpro_error_hdr` maps count/length/data registers and maximum counts for 48-byte CE/UE classes. `struct smpro_int_error_hdr` maps internal SMpro/PMPRO error and warning registers. Read helpers are `smpro_event_data_read()`, `smpro_overflow_data_read()`, `smpro_error_data_read()`, `smpro_internal_err_read()`, `smpro_internal_warn_read()`, and `smpro_dimm_syndrome_read()`. Attribute macros generate overflow, error, event, and DIMM syndrome sysfs files. `smpro_errmon_probe()` obtains the parent regmap and the driver uses `ATTRIBUTE_GROUPS(smpro_errmon)`.

## Control Flow
Probe allocates private data, attaches it to the platform device, and retrieves the parent regmap. Sysfs reads perform direct register transactions: event reads fetch and clear nonzero event data; overflow reads inspect bit 8 in the count register; 48-byte error reads validate count and length, perform a no-increment block read, then clear by writing `0x100` to the count register. Internal error/warning reads first check `GPI_RAS_ERR`, inspect the type register, assemble high/low words, optionally read extended data, and clear the consumed bit. DIMM syndrome reads only proceed in boot stage 4, select a DIMM slot, and emit the syndrome register.

## State and Persistence
State is almost entirely device-register backed. Several sysfs reads are destructive because they clear event, error, or warning bits after reporting them. The driver keeps only a regmap pointer and static register tables; no cache or suspend persistence is implemented.

## Dependencies and Integration Points
It is a platform child named `smpro-errmon`, integrated with an MFD or parent device that exposes a regmap. It depends on Linux sysfs device attribute groups, `regmap_read()`, `regmap_write()`, and `regmap_noinc_read()`.

## Risks and Edge Cases
`smpro_error_data_read()` masks `err_count` before checking `ret`, so a failed `regmap_read()` leaves `err_count` undefined before the function returns the error. Reads returning `0` for absent events produce empty sysfs reads rather than formatted zero values in some paths. Destructive read semantics can surprise polling tools and lose events if multiple readers race. Count and length validation relies on firmware-provided limits.

## Test Signals
Validate each generated sysfs file against known register fixtures, destructive clear-on-read behavior, overflow bit reporting, max-count and length clamping, SMpro/PMPRO internal warning/error formatting, DIMM syndrome stage gating, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/smpro-errmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/smpro-misc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/smpro-misc.c

## Purpose
`smpro-misc.c` provides miscellaneous Ampere Altra SMpro sysfs controls for boot progress reporting and SoC power limit access through a parent regmap.

## Important APIs, Types, and Functions
`struct smpro_misc` stores the parent `regmap`. `boot_progress_show()` reads current boot-stage registers and emits a packed six-byte progress value. `soc_power_limit_show()` and `soc_power_limit_store()` expose register `SOC_POWER_LIMIT` as a read/write sysfs value. `smpro_misc_probe()` allocates private data and retrieves the parent regmap. Attributes are grouped with `ATTRIBUTE_GROUPS(smpro_misc)`.

## Control Flow
Probe binds the regmap from the parent. Reading `boot_progress` compares the firmware-reported boot stage with the current stage, rejects impossible stage advancement, reads low/high progress words, and writes an acknowledgement bit when firmware should advance to the next boot stage. Reading or writing `soc_power_limit` directly maps to a single SMpro register.

## State and Persistence
The only software state is the regmap pointer. Boot progress and power-limit state are firmware/register backed. Reading boot progress can mutate firmware-visible state by writing the bootstage register when the reported stage lags the current stage.

## Dependencies and Integration Points
The driver is a platform child named `smpro-misc` and depends on a parent regmap provider, sysfs attribute groups, and SMpro firmware register semantics.

## Risks and Edge Cases
`soc_power_limit_store()` accepts any unsigned long value and casts it to `unsigned int` without range validation. `boot_progress_show()` returns `-EINVAL` when boot stage exceeds current stage, making firmware ordering bugs visible to userspace. The boot-progress output uses byte-swapped 16-bit words, so consumers need to know the firmware format.

## Test Signals
Check sysfs file creation, boot progress output across stage transitions, acknowledgement writes when `boot_stage < cur_stage`, invalid stage rejection, power-limit read/write success, and regmap error mapping to sysfs errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/smpro-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram-exec.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sram-exec.c

## Purpose
`sram-exec.c` adds protected executable SRAM support to the generic SRAM driver. It lets SRAM partitions marked `protect-exec` be copied into safely while preserving a write-xor-execute policy.

## Important APIs, Types, and Functions
`sram_check_protect_exec()` validates that a protected executable partition is page-aligned. `sram_add_protect_exec()` records a partition in the global executable-pool list. The exported `sram_exec_copy()` finds the matching partition for a `gen_pool`, verifies the target range, temporarily switches memory attributes with `set_memory_nx()` and `set_memory_rw()`, performs architecture-specific `fncpy()`, and restores `set_memory_rox()`.

## Control Flow
During SRAM probe, `sram.c` calls the check/add helpers for `protect-exec` reserved blocks. A later client calls `sram_exec_copy()` with a pool and destination inside that pool. The helper locates the partition under `exec_pool_list_mutex`, validates the destination using `gen_pool_has_addr()`, locks the partition, flips the entire relevant page range non-executable and writable, copies the function body with `fncpy()`, restores read-only executable attributes, and returns the callable copied address.

## State and Persistence
The file maintains a global list of executable SRAM partitions protected by a mutex. Per-partition serialization uses `part->lock`. There is no durable state; memory permissions and copied code live only for the current boot and depend on page-attribute state.

## Dependencies and Integration Points
It depends on `CONFIG_SRAM_EXEC`, genalloc pools, `set_memory_*()` page attribute APIs, `asm/fncpy.h`, and the structures declared in `sram.h`. It integrates with the main SRAM driver through `sram_check_protect_exec()` and `sram_add_protect_exec()`, and exports `sram_exec_copy()` to other kernel clients.

## Risks and Edge Cases
The page count is based on `PAGE_ALIGN(size)` from the partition base, not the destination offset, so callers copying near the end of a page range need careful review. If `set_memory_rox()` fails after making memory writable, the function returns `NULL` but may leave weaker permissions. The helper requires architecture support for `fncpy()` and rejects non-page-aligned partitions.

## Test Signals
Validate DT `protect-exec` partitions with aligned and unaligned ranges, `sram_exec_copy()` range rejection, permission transitions through architecture page tables, callable returned addresses, concurrent copy serialization, and error handling for failed `set_memory_*()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sram.c

## Purpose
`sram.c` is the generic on-chip SRAM platform driver. It maps SRAM resources, parses reserved child regions from device tree, creates genalloc pools for allocatable SRAM, optionally exports reserved partitions as sysfs binary files, and supports platform-specific initialization for Atmel secure RAM and Tegra SYSRAM.

## Important APIs, Types, and Functions
Core helpers include `sram_add_pool()`, `sram_add_export()`, `sram_add_partition()`, `sram_free_partitions()`, `sram_reserve_regions()`, `sram_read()`, and `sram_write()`. Platform configuration is described by `struct sram_config` with `atmel_securam_config` and `tegra_sysram_config`. Driver entry points are `sram_probe()`, `sram_remove()`, and `sram_init()` registered as a `postcore_initcall()`.

## Control Flow
Probe reads match data and `no-memory-wc`, maps the whole SRAM unless the platform requires mapping only reserved child regions, creates a root gen_pool when applicable, enables an optional clock, and calls `sram_reserve_regions()`. Reservation parsing converts DT children to sorted `struct sram_reserve` blocks, detects out-of-range or overlapping regions, creates exported/pool/protect-exec partitions, and adds gaps between reserved blocks to the root pool. Platform `init()` runs after reservation setup; Atmel waits for SECUMOD RAM ready through regmap polling. Remove tears down sysfs exports and warns if pools still have allocated SRAM.

## State and Persistence
`struct sram_dev` holds mapped base, root pool, partition array, config, and flags. Each `struct sram_partition` holds its base, optional pool, sysfs binary attribute, mutex, and list hook. SRAM contents are persistent only as hardware RAM across power domains; the driver does not save or restore contents.

## Dependencies and Integration Points
The driver depends on platform resources, OF address parsing, `gen_pool`, sysfs bin attributes, memory-mapped IO, optional clocks, syscon/regmap for Atmel SECUMOD, and the optional `CONFIG_SRAM_EXEC` helper declared in `sram.h`. Device-tree properties include child `export`, `pool`, `protect-exec`, `label`, and top-level `no-memory-wc`.

## Risks and Edge Cases
Overlap detection reports "starts after current offset" even though it detects `block->start < cur_start`. Exported sysfs files permit raw root read/write of SRAM partitions, so DT exposure is security-sensitive. `map_only_reserved` platforms rely on every usable child being mapped separately to avoid speculative access faults. Removing with allocated gen_pool memory only logs an error; consumers must release allocations.

## Test Signals
Test root pool gap creation, sorted overlapping reservation rejection, child labels and sysfs bin file names, exported read/write locking, pool allocation/free accounting, `protect-exec` handoff, `no-memory-wc` mapping choice, Tegra map-only-reserved behavior, Atmel RAM-ready polling, and remove-time allocation warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sram.h

## Purpose
`sram.h` is the private header shared by the generic SRAM driver and its executable-SRAM helper. It defines the driver-private configuration, device, partition, and reservation structures plus conditional prototypes for protected executable SRAM support.

## Important APIs, Types, and Functions
`struct sram_config` provides optional platform initialization and the `map_only_reserved` policy. `struct sram_partition` contains a mapped partition base, optional `gen_pool`, sysfs binary attribute, mutex, and list node. `struct sram_dev` stores per-device configuration, base mapping, root pool, partition array, and count. `struct sram_reserve` describes a parsed reserved child block with start/size/resource and export/pool/protect-exec flags. `sram_check_protect_exec()` and `sram_add_protect_exec()` are declared when `CONFIG_SRAM_EXEC` is enabled and otherwise return `-ENODEV`.

## Control Flow
The header has no runtime flow. Its structures are filled by `sram.c` during platform probe and consumed by `sram-exec.c` when protected executable partitions are enabled.

## State and Persistence
The header defines in-memory state containers only. Persistence behavior is determined by SRAM hardware and the implementation files.

## Dependencies and Integration Points
It assumes Linux kernel definitions for `struct device`, `struct gen_pool`, `struct bin_attribute`, `struct mutex`, `struct list_head`, and `struct resource` are included by users. It is internal to `drivers/misc` SRAM code and not a UAPI contract.

## Risks and Edge Cases
The `CONFIG_SRAM_EXEC` stubs make `protect-exec` reservations fail with `-ENODEV` when executable SRAM support is disabled. The single `list_head` in `struct sram_partition` is used for executable pool tracking, so additional list uses would need a new member.

## Test Signals
Build both with and without `CONFIG_SRAM_EXEC`, verify `protect-exec` DT behavior in each configuration, and check structure users initialize mutexes/list hooks before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ti_fpc202.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ti_fpc202.c

## Purpose
`ti_fpc202.c` drives the TI FPC202 dual-port controller. It combines I2C address translation for two downstream ports, a 28-line GPIO controller, optional LED class devices on LED-capable GPIO outputs, and an optional enable GPIO.

## Important APIs, Types, and Functions
`struct fpc202_priv` stores the I2C client, ATR object, enable GPIO, gpiochip, LED objects, mutexes, address caches, and probed-port bitmap. `struct fpc202_led` wraps LED class state and the GPIO line claimed for LED ownership. I2C helpers are `fpc202_read()`, `fpc202_write()`, and `fpc202_write_dev_addr()`. GPIO callbacks are `fpc202_gpio_get()`, `fpc202_gpio_set()`, `fpc202_gpio_direction_input()`, and `fpc202_gpio_direction_output()`. ATR hooks are `fpc202_attach_addr()` and `fpc202_detach_addr()`. LED hooks include `fpc202_led_blink_set()`, `fpc202_led_brightness_get()`, `fpc202_led_brightness_set()`, and registration helpers. Probe/remove are `fpc202_probe()` and `fpc202_remove()`.

## Control Flow
Probe allocates private data, initializes mutexes, enables the chip, registers the gpiochip, creates an I2C ATR, registers child LED nodes, then iterates child nodes with `reg` values for FPC202 ports. Each port gets two aliases derived from the FPC202 self address and port ID, is added as an ATR adapter, and has both translation entries reset to invalid. ATR attach writes the target address into MOD and AUX registers for the device number implied by alias parity; detach scans the address cache and invalidates matching entries. GPIO writes either program simple output bits or switch LED-capable lines between on/off LED modes. LED brightness and blink operations program mode, PWM, and blink timing registers.

## State and Persistence
Runtime state includes cached translated addresses per port/device, probed port bitmap, LED modes, claimed GPIO descriptors for LED lines, and device registers. `reg_dev_lock` serializes translation register/cache updates and `led_mode_lock` serializes shared LED mode register updates. Hardware register state is not restored after driver removal except translation invalidation during probe and enable GPIO deassertion during remove.

## Dependencies and Integration Points
The driver depends on SMBus byte data access, the Linux I2C ATR framework, gpiolib, LED classdev registration, OF child nodes, devres groups, and optional enable GPIO. It imports the `I2C_ATR` namespace and matches `ti,fpc202`.

## Risks and Edge Cases
The LED child offset validation allows `offset == FPC202_GPIO_COUNT`, which is one past the valid 0..27 GPIO range and can index beyond the eight LED entries. Error unwinding after `gpiochip_add_data()` may call `gpiochip_remove()` even when ATR creation failed after the chip was added, which is intended, but the `disable_gpio` label name obscures ownership. GPIO get is unsupported on LED-capable outputs. The AUX register write is empirical, so hardware variants may need confirmation.

## Test Signals
Validate two downstream ATR adapters, alias assignment by I2C address and port, attach/detach register writes and cache invalidation, all GPIO direction/value paths, LED brightness/PWM/blink timing including rounding and saturation, invalid LED offsets, enable GPIO behavior, and remove/unwind freeing own GPIO descriptors and ATR adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ti_fpc202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tifm_7xx1.c -->
# sources/distributed-fs/ceph-client/drivers/misc/tifm_7xx1.c

## Purpose
`tifm_7xx1.c` is the PCI host driver for TI FlashMedia controllers. It discovers card sockets, powers media sockets, handles controller interrupts, registers media devices with the TIFM core bus, and manages suspend/resume for TI xx21/xx12/xx20 devices.

## Important APIs, Types, and Functions
Key functions are `tifm_7xx1_probe()`, `tifm_7xx1_remove()`, `tifm_7xx1_isr()`, `tifm_7xx1_switch_media()`, `tifm_7xx1_toggle_sock_power()`, `tifm_7xx1_sock_power_off()`, `tifm_7xx1_suspend()`, `tifm_7xx1_resume()`, `tifm_7xx1_eject()`, and `tifm_7xx1_has_ms_pif()`. It uses `struct tifm_adapter` and `struct tifm_dev` from the TIFM core and maps PCI BAR0 as the controller register base.

## Control Flow
Probe enables the PCI device, requests regions, enables INTx, allocates a TIFM adapter with two or four sockets depending on PCI ID, maps BAR0, requests a shared IRQ, adds the adapter, and enables socket-change interrupts. The ISR masks global interrupt delivery, dispatches FIFO/card events to registered sockets, records socket-change bits, acknowledges status, and either completes resume, re-enables interrupts, or queues `media_switcher`. The work function unregisters removed socket devices, powers sockets off/on, detects media IDs, allocates/registers new TIFM devices, and re-enables per-socket FIFO/card interrupts. Suspend powers off sockets; resume powers sockets, compares detected media with existing devices, waits for good sockets to settle, and queues changes for bad sockets.

## State and Persistence
Adapter state includes mapped registers, socket pointers, socket-change bitmask, lock, media switch work item, and optional resume completion pointer. Socket devices are dynamically registered and unregistered. No persistent storage is maintained; hardware state is reprogrammed at probe/resume.

## Dependencies and Integration Points
The driver depends on PCI, DMA mask setup, TIFM core exported functions, workqueues, shared IRQs, memory-mapped controller registers, and PM callbacks. It registers as a PCI driver for TI FlashMedia device IDs.

## Risks and Edge Cases
The ISR disables global interrupt enable while processing and relies on later paths to re-enable it; missed re-enable can stall media detection. Device unregister occurs outside the adapter lock, so socket pointer transitions must remain carefully ordered. Resume uses a one-second completion wait and bitmask reconciliation that can race with real card changes. Power sequencing uses fixed delays and media-specific xD delay.

## Test Signals
Test probe/remove resource ordering, interrupt status acknowledgement, card insert/remove on every socket, FIFO/card event callbacks to media drivers, manual eject, suspend/resume with unchanged and changed cards, two- and four-socket device IDs, shared IRQ behavior, and adapter removal while work is queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tifm_7xx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tifm_core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/tifm_core.c

## Purpose
`tifm_core.c` implements the TI FlashMedia bus, adapter class, workqueue, media-device allocation, driver registration, and DMA helper APIs used by TIFM host and media drivers.

## Important APIs, Types, and Functions
Exported APIs include `tifm_alloc_adapter()`, `tifm_add_adapter()`, `tifm_remove_adapter()`, `tifm_free_adapter()`, `tifm_alloc_device()`, `tifm_free_device()`, `tifm_eject()`, `tifm_has_ms_pif()`, `tifm_map_sg()`, `tifm_unmap_sg()`, `tifm_queue_work()`, `tifm_register_driver()`, and `tifm_unregister_driver()`. Bus callbacks are `tifm_bus_match()`, `tifm_uevent()`, `tifm_device_probe()`, `tifm_device_remove()`, and optional PM callbacks. Global state includes `workqueue`, `tifm_adapter_idr`, and `tifm_adapter_lock`.

## Control Flow
`tifm_init()` creates a freezable workqueue, registers the `tifm` bus, and registers the `tifm_adapter` class. Host drivers allocate an adapter, add it to the IDR/class, and allocate/register socket devices as media appears. The bus matches socket type against a `tifm_driver` ID table, calls media driver probe/remove, and emits `TIFM_CARD_TYPE` uevents. Removing an adapter flushes pending work, unregisters all socket devices, removes the IDR entry, and deletes the adapter device.

## State and Persistence
Adapter IDs are allocated from an IDR protected by a spinlock. The workqueue persists for the module lifetime. Socket devices hold type, socket ID, event callbacks, and device-core references. State is dynamic only and disappears at driver unload or adapter removal.

## Dependencies and Integration Points
The core depends on Linux device model bus/class APIs, IDR, workqueues, PCI DMA helpers for scatter-gather mapping, and TIFM structures from `<linux/tifm.h>`. It is consumed by `tifm_7xx1.c` and media-specific MemoryStick/SD/xD drivers.

## Risks and Edge Cases
`type_show()` uses `sprintf()` without a newline and older sysfs style. `tifm_device_probe()` takes an extra reference and leaves it until remove, so probe failure must correctly drop it. DMA helpers assume the socket parent is a PCI device. Adapter removal flushes the global workqueue, affecting work for all adapters.

## Test Signals
Validate bus/class registration, media type matching and uevents, probe/remove reference balance, adapter ID allocation/removal, global workqueue flushing, DMA map/unmap through socket parent, eject delegation, and PM callback forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tifm_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tps6594-esm.c -->
# sources/distributed-fs/ceph-client/drivers/misc/tps6594-esm.c

## Purpose
`tps6594-esm.c` enables and monitors the Error Signal Monitor block in TI TPS6594/TPS6593/LP8764 PMICs. It configures ESM registers, reports named ESM IRQs, and handles suspend/resume start/stop.

## Important APIs, Types, and Functions
The IRQ handler is `tps6594_esm_isr()`. Driver lifecycle is `tps6594_esm_probe()` and `tps6594_esm_remove()`. Power-management callbacks are `tps6594_esm_suspend()` and `tps6594_esm_resume()`. It uses the parent `struct tps6594`, its `regmap`, platform resources for named IRQs, and register bits `TPS6594_BIT_ESM_SOC_EN`, `TPS6594_BIT_ESM_SOC_ENDRV`, and `TPS6594_BIT_ESM_SOC_START`.

## Control Flow
Probe reads PMIC revision and rejects revision 1 because GPIO3 cannot be used for SoC ESM there. It loops over platform resources, resolves each named IRQ, and requests threaded one-shot handlers. It then enables ESM SOC mode/driver bits, starts the ESM block, enables runtime PM, and takes a runtime PM reference. Remove stops ESM, clears enable bits, and releases runtime PM. Suspend clears the start bit and drops the runtime PM reference; resume reacquires runtime PM and sets the start bit.

## State and Persistence
No private data is allocated. State is held in parent PMIC registers and devm-managed IRQ registrations. Runtime PM reference state is maintained by the PM core.

## Dependencies and Integration Points
The driver is a platform child named `tps6594-esm` under the TPS6594 MFD. It depends on parent drvdata, regmap, platform IRQ resources named by the MFD, and runtime PM.

## Risks and Edge Cases
The ISR calls `platform_get_irq_byname()` for every resource on every interrupt, which is simple but inefficient and can return errors during interrupt handling. `pm_runtime_get_sync()` return values are ignored. Revision filtering only checks exact `0x08`, so future errata variants require updates.

## Test Signals
Validate revision-1 rejection, successful enable/start register writes, named IRQ logging, suspend clears start and resume restarts, remove disables ESM, and regmap/IRQ request failures return `dev_err_probe()` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tps6594-esm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tps6594-pfsm.c -->
# sources/distributed-fs/ceph-client/drivers/misc/tps6594-pfsm.c

## Purpose
`tps6594-pfsm.c` exposes the PMIC Pre-configurable Finite State Machine for TPS6594/TPS6593/LP8764/TPS65224/TPS652G1 devices. It provides a misc character device for register read/write and ioctl commands that trigger standby, low-power standby, firmware update, active, MCU-only, and retention-state transitions.

## Important APIs, Types, and Functions
`struct tps6594_pfsm` stores the miscdevice, parent regmap, and chip ID. File operations are `tps6594_pfsm_read()`, `tps6594_pfsm_write()`, and `tps6594_pfsm_ioctl()`. Retention trigger setup is handled by `tps6594_pfsm_configure_ret_trig()`. IRQ reporting uses `tps6594_pfsm_isr()`. Lifecycle functions are `tps6594_pfsm_probe()` and `tps6594_pfsm_remove()`. UAPI commands come from `<linux/tps6594_pfsm.h>`.

## Control Flow
Probe allocates private data, names a misc device as `pfsm-<chip_id>-0x<reg>`, registers one-shot handlers for each platform IRQ resource, stores drvdata, and registers the misc device. Reads and writes expose PMIC register offsets from 0 to `0x1ff` one byte at a time. Ioctl switches on PMIC commands, updating RTC/FSM trigger registers and chip-specific startup destination fields, with TPS65224/TPS652G1 exclusions for unsupported low-power or MCU-only states. Remove deregisters the miscdevice.

## State and Persistence
The driver stores only miscdevice/regmap/chip ID in software. PMIC FSM trigger, NSLEEP, RTC, startup, and firmware registers persist according to PMIC hardware behavior. The misc file position controls read/write offset within the two-page PMIC window.

## Dependencies and Integration Points
It integrates with the TPS6594 MFD parent, regmap, miscdevice core, platform IRQ resources, and the PFSM ioctl UAPI. Userspace tooling can read/write PMIC page 0 and page 1 registers for firmware-update flows.

## Risks and Edge Cases
Raw register write access through the misc device is powerful and can alter PMIC/NVM state; permissions and userspace tools are critical. `char val` in write may sign-extend before `regmap_write()` depending on architecture/compiler, though only low bits should matter. Unsupported ioctls and unsupported states return `-ENOIOCTLCMD`, which userspace must handle. Register read/write loops are byte-at-a-time and not atomic across multi-byte sequences.

## Test Signals
Validate miscdevice naming, bounded reads/writes and file offsets, each ioctl's register writes for TPS6594-family versus TPS65224/TPS652G1 chips, retention option copying from userspace, IRQ event logging, misc deregistration, and error propagation from `copy_from_user()` and regmap calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tps6594-pfsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tsl2550.c -->
# sources/distributed-fs/ceph-client/drivers/misc/tsl2550.c

## Purpose
`tsl2550.c` is an I2C ambient light sensor driver for the TAOS TSL2550. It manages power and standard/extended range modes, converts two ADC channels to lux using lookup tables, and exposes legacy sysfs attributes.

## Important APIs, Types, and Functions
`struct tsl2550_data` stores the client, update mutex, power state, and operating mode. Device control helpers are `tsl2550_set_operating_mode()`, `tsl2550_set_power_state()`, `tsl2550_get_adc_value()`, `tsl2550_calculate_lux()`, and `tsl2550_init_client()`. Sysfs handlers expose `power_state`, `operating_mode`, and `lux1_input`. I2C lifecycle functions are `tsl2550_probe()` and `tsl2550_remove()`, with optional PM callbacks `tsl2550_suspend()` and `tsl2550_resume()`.

## Control Flow
Probe verifies SMBus byte functionality, allocates private data, reads optional platform-data operating mode, initializes the mutex, powers up the chip by reading the power-up command response, programs the default range, and creates the sysfs group. Lux reads require the sensor to be powered, read ADC0 and ADC1 command values, require the valid bit, convert compressed channel codes through `count_lut` and `ratio_lut`, and multiply by five in extended mode. Suspend powers down; resume powers up and restores mode.

## State and Persistence
Power and operating mode are cached in `tsl2550_data` and mirrored to the sensor. Sensor ADC data is read live. No nonvolatile state is managed. The update mutex serializes sysfs power/mode/lux transactions.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte operations, legacy sysfs attributes, optional platform data, OF compatible `taos,tsl2550`, and PM sleep hooks.

## Risks and Edge Cases
`tsl2550_set_operating_mode()` and `tsl2550_set_power_state()` update cached state even if the SMBus write fails. `tsl2550_set_power_state()` calls `tsl2550_set_operating_mode()` after power-up but ignores that return. `tsl2550_init_client()` uses `i2c_smbus_read_byte_data()` with a command value to probe power-up behavior, which is device-specific. ADC not-ready returns `-EAGAIN` to sysfs readers.

## Test Signals
Validate SMBus functionality rejection, probe power-up response, sysfs power/mode read/write bounds, lux conversion for table edge values, extended-mode multiplier, ADC invalid-bit `-EAGAIN`, suspend/resume state restoration, and failure paths where SMBus writes fail but cached state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/tsl2550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/uacce/Kconfig

## Purpose
`uacce/Kconfig` declares the build option for UACCE, the Accelerator Framework for User Land.

## Important APIs, Types, and Functions
The single symbol is `CONFIG_UACCE`, a tristate option labelled "Accelerator Framework for User Land". It depends on `IOMMU_API` and points users to the UAPI header `include/uapi/misc/uacce/uacce.h` and documentation `Documentation/misc-devices/uacce.rst`.

## Control Flow
Kconfig has no runtime control flow. Selecting `CONFIG_UACCE=y` builds the framework into the kernel; `m` builds it as a module; `n` excludes it.

## State and Persistence
No runtime state is defined here. The selected Kconfig value controls compilation and availability.

## Dependencies and Integration Points
The dependency on `IOMMU_API` reflects UACCE's use of IOMMU/SVA features for userspace accelerator access. The symbol is consumed by the local Makefile to build `uacce.o`.

## Risks and Edge Cases
If accelerator drivers expect UACCE but `IOMMU_API` is disabled, the framework cannot be selected. The help text explicitly advises unsure users to say no because the option exposes direct userspace accelerator interfaces.

## Test Signals
Check Kconfig visibility with and without `IOMMU_API`, built-in and module builds, and accelerator-driver dependency chains that select or depend on `UACCE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/uacce/Makefile

## Purpose
`uacce/Makefile` wires the UACCE framework object into the kernel build when `CONFIG_UACCE` is enabled.

## Important APIs, Types, and Functions
The file contains one build rule: `obj-$(CONFIG_UACCE) += uacce.o`.

## Control Flow
There is no runtime flow. Kbuild includes `uacce.o` as built-in or module according to the tristate value of `CONFIG_UACCE`.

## State and Persistence
No runtime state is defined.

## Dependencies and Integration Points
The Makefile is paired with `uacce/Kconfig` and the implementation in `uacce.c`. It integrates with standard Linux Kbuild object selection.

## Risks and Edge Cases
The file has no subobject composition; any future split of the framework would require adding composite object rules.

## Test Signals
Verify `CONFIG_UACCE=y` links `uacce.o` into vmlinux, `CONFIG_UACCE=m` produces the module, and disabled builds omit the object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/uacce.c -->
# sources/distributed-fs/ceph-client/drivers/misc/uacce/uacce.c

## Purpose
`uacce.c` implements the UACCE userspace accelerator framework. It registers accelerator devices as character devices with sysfs metadata, creates per-open queues, optionally binds queues to IOMMU SVA/PASID, exposes queue control ioctls, allows queue regions to be mmaped, and handles safe device removal while file descriptors remain open.

## Important APIs, Types, and Functions
Public framework APIs are `uacce_alloc()`, `uacce_register()`, and `uacce_remove()`. File operations are `uacce_fops_open()`, `uacce_fops_release()`, `uacce_fops_unl_ioctl()`, optional `uacce_fops_compat_ioctl()`, `uacce_fops_mmap()`, and `uacce_fops_poll()`. Queue helpers include `uacce_start_queue()`, `uacce_stop_queue()`, `uacce_put_queue()`, `uacce_queue_is_valid()`, `uacce_bind_queue()`, and `uacce_unbind_queue()`. Sysfs attributes expose API version, flags, available instances, algorithms, MMIO/DUS region sizes, isolation state, and isolation threshold strategy.

## Control Flow
Subsystem init registers the UACCE class and allocates a char-device major. Accelerator drivers call `uacce_alloc()` with an interface, then `uacce_register()` to add the cdev/device. Opening a device locates it by minor in an xarray, allocates a queue, locks the UACCE device, checks that the parent still exists, binds SVA if requested, calls the driver `get_queue()` hook, initializes waitqueue/mapping/mutex, and links it into the device queue list. Ioctls start or stop queues or delegate to driver-specific ioctl handlers. Mmap validates one queue file region per type and delegates MMIO/DUS mapping to the accelerator driver. Poll waits on the queue and delegates update detection. Release stops and puts the queue, unbinds SVA, unlinks it, and frees it. Removal locks out new opens, zombifies all queues, unmaps user mappings, removes the cdev/device, clears ops/parent, erases the xarray entry, and drops the final device reference.

## State and Persistence
Global state includes `uacce_devt`, `uacce_class`, and an allocating xarray of devices. Each `struct uacce_device` has a mutex, queue list, ops, parent pointer, device ID, cdev, flags, algorithms, API string, and region page counts. Each queue has state (`INIT`, `STARTED`, `ZOMBIE`), optional SVA handle and PASID, waitqueue, mmap file mapping, and per-region mappings. State is runtime-only and tied to device and file lifetimes.

## Dependencies and Integration Points
The framework depends on char devices, device classes, sysfs groups, xarray allocation, IOMMU SVA APIs, DMA/IOMMU headers, VM operations, poll, compat ioctl support, and accelerator-driver-provided `struct uacce_ops`. It integrates with the UACCE UAPI commands `UACCE_CMD_START_Q` and `UACCE_CMD_PUT_Q`.

## Risks and Edge Cases
Lock ordering is delicate: ioctl uses the device mutex to avoid mmap-lock cycles, while mmap uses the queue mutex. Removal must handle concurrent open and live file descriptors without use-after-free; it nulls `ops` and `parent` after disabling queues. `uacce_register()` leaks the allocated cdev object on `cdev_device_add()` failure unless the caller's later cleanup handles it. Sysfs visibility depends on optional ops but `isolate_strategy` is visible if either read or write hook exists, while show/store individually require their hook.

## Test Signals
Test class/major registration, device ID allocation, open/close queue lifecycle, SVA bind failures and PASID invalid handling, start/stop ioctls, delegated ioctls, mmap duplicate-region rejection and vma close cleanup, poll readiness, sysfs visibility for optional ops, concurrent remove with open fds and mmap, xarray erasure, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/uacce/uacce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vcpu_stall_detector.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vcpu_stall_detector.c

## Purpose
`vcpu_stall_detector.c` drives a virtual per-vCPU watchdog/stall detector device, intended for QEMU. It periodically reloads per-CPU MMIO counters and panics the guest if the virtual device raises a stall interrupt.

## Important APIs, Types, and Functions
`struct vcpu_stall_detect_config` stores global clock, timeout, IRQ, MMIO base, platform device, and CPU hotplug state. `struct vcpu_stall_priv` stores a per-CPU hrtimer and initialization flag. Runtime callbacks are `vcpu_stall_detect_timer_fn()`, `vcpu_stall_detector_irq()`, `start_stall_detector_cpu()`, and `stop_stall_detector_cpu()`. Platform lifecycle is `vcpu_stall_detect_probe()` and `vcpu_stall_detect_remove()`.

## Control Flow
Probe allocates per-CPU detector state, maps MMIO, reads optional `clock-frequency` and `timeout-sec` DT properties with range validation, optionally requests a percpu PPI, and installs a dynamic CPU hotplug online state. When a CPU starts, the driver writes that vCPU's clock frequency, load count, and status registers, initializes a pinned hrtimer, and starts it at half the timeout. The hrtimer reloads the per-vCPU counter and re-arms itself. If the device interrupt fires, the ISR panics the kernel. Remove unregisters the hotplug state, frees the percpu IRQ, and stops all initialized timers.

## State and Persistence
Global config is a single static instance, so the driver assumes one device. Per-CPU hrtimer initialization state is allocated devm-percpu. Hardware state is per-vCPU MMIO register blocks. No persistent state exists.

## Dependencies and Integration Points
The driver depends on platform devices, OF matching for `qemu,vcpu-stall-detector`, MMIO access, hrtimers, CPU hotplug, percpu IRQs, and kernel panic handling.

## Risks and Edge Cases
`start_stall_detector_cpu()` uses `this_cpu_ptr()` instead of `per_cpu_ptr(..., cpu)`, relying on CPU hotplug callback execution context matching the target CPU. Remove calls `cpuhp_remove_state()` before stopping timers, which should offline callbacks but still deserves race testing. The IRQ handler unconditionally panics, so false positives are severe. Property validation rejects values equal to the max constants because it uses `<`, not `<=`.

## Test Signals
Validate DT property defaults and range warnings, per-CPU MMIO offsets, CPU hotplug start/stop behavior, hrtimer reload cadence, optional PPI request/free, panic on injected stall interrupt, remove-time timer cancellation, and multi-device rejection assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vcpu_stall_detector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_balloon.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_balloon.c

## Purpose
`vmw_balloon.c` is VMware's guest memory balloon driver. It communicates with the VMware hypervisor through the backdoor I/O port to inflate and deflate guest memory, supports batched and 2 MB balloon operations, optional VMCI doorbell wakeups, optional shrinker-based memory pressure relief, debugfs statistics, and balloon page migration.

## Important APIs, Types, and Functions
`struct vmballoon` holds target/current size, capabilities, batching page, page lists, work item, locks, VMCI doorbell, balloon migration info, and optional shrinker/stats. Hypervisor commands are sent with `__vmballoon_cmd()` and `vmballoon_cmd()`, with setup helpers `vmballoon_send_start()`, `vmballoon_send_guest_id()`, and `vmballoon_send_get_target()`. Page lifecycle is handled by `vmballoon_alloc_page_list()`, `vmballoon_lock()`, `vmballoon_inflate()`, `vmballoon_deflate()`, `vmballoon_pop()`, `vmballoon_enqueue_page_list()`, and `vmballoon_dequeue_page_list()`. Batching and VMCI helpers are `vmballoon_init_batching()`, `vmballoon_deinit_batching()`, `vmballoon_vmci_init()`, and `vmballoon_vmci_cleanup()`. Periodic control is `vmballoon_work()`. Optional hooks include `vmballoon_shrinker_scan()`, `vmballoon_debug_show()`, and `vmballoon_migratepage()`.

## Control Flow
Late init verifies the VMware hypervisor, initializes balloon state, optional shrinker, balloon migration info, locks, doorbell handle, and queues the worker immediately. The worker resets the protocol when required, negotiates capabilities, initializes batching if available, registers VMCI doorbell, sends guest ID, then periodically gets the host target and inflates or deflates toward it. Inflation allocates pages at the largest supported size, sends lock commands to the host, enqueues accepted pages, splits refused 2 MB pages down to 4 KB candidates, and stops on allocation/lock limits. Deflation dequeues pages, optionally unlocks them with the host, frees accepted pages, and returns refused pages to the balloon. VMCI doorbells reschedule the worker immediately when host target changes. Exit disables shrinker/debugfs/doorbell, resets host capabilities to zero, and pops all pages without coordinated unlock.

## State and Persistence
The singleton `balloon` keeps volatile target/current size, reset flag, negotiated capabilities, batch communication page, huge-page list, standard balloon page list, shrink timeout, stats pointer, and VMCI handle. The host's balloon target is refreshed through backdoor commands. Ballooned pages are marked offline and held until deflation; there is no durable persistence across unload or reboot.

## Dependencies and Integration Points
The driver depends on x86 VMware hypervisor detection, VMware backdoor port I/O, VMCI doorbell APIs, Linux balloon compaction/migration infrastructure, memory allocation and page offline flags, delayed work on `system_freezable_wq`, static keys, debugfs, shrinker APIs, and module parameters. It aliases VMware DMI and `vmware_vmmemctl`.

## Risks and Edge Cases
Backdoor command failures can set `reset_required`, causing asynchronous protocol reset. 2 MB pages are kept out of migration lists, while 4 KB pages integrate with balloon migration. Shrinker-driven deflation delays later inflation to avoid churn. Batching state uses a static key, so reset paths must keep `batch_page`, `batch_max_pages`, and host capabilities consistent. Exit calls `vmballoon_send_start()` after worker cancellation but without a guaranteed successful reset path if the host is gone. Page migration can deflate the old page and fail to inflate the new page, intentionally shrinking the balloon by one frame.

## Test Signals
Validate VMware-only init, start capability negotiation for basic/batched/2 MB/64-bit targets, periodic target polling, inflation and deflation size accounting, refused-page splitting, host reset recovery, VMCI doorbell wakeups, shrinker deflation and inflation delay, debugfs stat enabling/output, balloon migration outcomes, suspend-freezable work behavior, and unload returning all pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_balloon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Kconfig

## Purpose
`vmw_vmci/Kconfig` declares the VMware VMCI driver option, enabling Virtual Machine Communication Interface support for host-guest and guest-guest communication through VMware's virtual device.

## Important APIs, Types, and Functions
The single symbol is `CONFIG_VMWARE_VMCI`, a tristate option labelled "VMware VMCI Driver". It depends on `(X86 || ARM64) && !CPU_BIG_ENDIAN && PCI` and documents that the module name is `vmw_vmci`.

## Control Flow
Kconfig has no runtime flow. The symbol controls whether the VMCI driver is omitted, built in, or built as a module.

## State and Persistence
No runtime state is present. The selected Kconfig value determines build inclusion.

## Dependencies and Integration Points
The architecture, endian, and PCI dependencies match the VMCI virtual PCI device support. Other drivers, such as the VMware balloon driver, can use VMCI APIs when the VMCI driver is available.

## Risks and Edge Cases
Big-endian and non-PCI configurations cannot select the driver. Built-in users that want VMCI services must consider init ordering; the balloon driver explicitly uses `late_initcall()` partly to allow VMCI to probe first.

## Test Signals
Check Kconfig visibility on x86 and arm64 little-endian PCI builds, module output as `vmw_vmci`, and dependent VMware features with built-in versus module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Makefile

## Purpose
`vmw_vmci/Makefile` defines how the VMware VMCI driver is built and which implementation objects compose the `vmw_vmci` module or built-in object.

## Important APIs, Types, and Functions
The Makefile selects `vmw_vmci.o` with `obj-$(CONFIG_VMWARE_VMCI)` and composes it from `vmci_context.o`, `vmci_datagram.o`, `vmci_doorbell.o`, `vmci_driver.o`, `vmci_event.o`, `vmci_guest.o`, `vmci_handle_array.o`, `vmci_host.o`, `vmci_queue_pair.o`, `vmci_resource.o`, and `vmci_route.o`.

## Control Flow
There is no runtime control flow. Kbuild links the listed objects into the VMCI driver when `CONFIG_VMWARE_VMCI` is enabled.

## State and Persistence
No runtime state is defined here. State resides in the listed VMCI implementation files.

## Dependencies and Integration Points
The file integrates the VMCI subdirectory with Kbuild and the `CONFIG_VMWARE_VMCI` symbol from the adjacent Kconfig.

## Risks and Edge Cases
All VMCI subcomponents are always included when the symbol is enabled; partial feature builds are not represented. Adding new VMCI implementation files requires updating this composite object list.

## Test Signals
Verify built-in and module builds include all listed VMCI objects, disabled builds omit the composite object, and dependency changes in Kconfig remain aligned with this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Makefile -->
