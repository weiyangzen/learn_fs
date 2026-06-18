# Research: subset-b-004257

Grouped research for Linux misc-driver files under `sources/distributed-fs/ceph-client/drivers/misc`, covering GenWQE queue/device support, HiSilicon and HMC standalone drivers, HP iLO, and IBM ASM service-processor components. Each file section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.c

## Purpose
`card_ddcb.c` implements GenWQE Device Driver Control Block queueing. It allocates requests, formats DDCBs for the service layer, starts or appends work on the hardware queue, handles completion through interrupt-woken polling, purges timed-out work, and sets up/tears down the service-layer queue and IRQs.

## Important APIs, Types, and Functions
Public entry points include `ddcb_requ_alloc()`, `ddcb_requ_free()`, `__genwqe_enqueue_ddcb()`, `__genwqe_wait_ddcb()`, `__genwqe_execute_raw_ddcb()`, `__genwqe_purge_ddcb()`, `genwqe_ddcbs_in_flight()`, `genwqe_setup_service_layer()`, `genwqe_finish_queue()`, and `genwqe_release_service_layer()`. Internal queue helpers include `queue_empty()`, `queue_enqueued_ddcbs()`, `queue_free_ddcbs()`, `get_next_ddcb()`, `enqueue_ddcb()`, `copy_ddcb_results()`, and `genwqe_check_ddcb_queue()`. Interrupt handlers are split between PF and VF with `genwqe_pf_isr()` checking GFIR error state and `genwqe_vf_isr()` only waking the queue thread.

## Control Flow
Queue setup resets privileged cards, fills queue register offsets, allocates coherent DDCB memory, initializes every entry as completed, starts a kernel thread, configures MSI, requests the IRQ, and finally marks the card used. Execution copies a user/kernel `genwqe_ddcb_cmd` into the next free DDCB, fills command fields, copies ASIV or ATS+ASIV depending on SLU generation, calculates ICRC, optionally enables completion interrupt, then uses compare-and-swap on the previous DDCB's SHI/HSI word to append with NEXT or taps the hardware queue offset register. The card thread calls `genwqe_check_ddcb_queue()`, copies ASV/status/timestamps back to the request, validates VCRC, marks the request finished, wakes the per-DDCB wait queue and busy waiters, and advances the active ring index. Waiters time out via `GENWQE_DDCB_SOFTWARE_TIMEOUT` and must purge failed requests.

## State and Persistence
Persistent runtime state is in `cd->queue`: coherent DDCB ring, request pointer array, per-entry wait queues, sequence numbers, active/next indices, register offsets, and counters for in-flight/completed/busy cases. DDCB state is hardware-shared big-endian memory; request state mirrors completion state in `ddcb_requ.req_state`. There is no disk persistence.

## Dependencies and Integration Points
The file depends on `card_base.h`, `card_ddcb.h`, coherent DMA allocation from `card_utils.c`, GenWQE MMIO helpers, PCI/MSI IRQ services, kernel wait queues, kthreads, and CRC-ITU-T. It is called by `card_dev.c` ioctls and flash helpers, and its debug data feeds user-requested `genwqe_debug_data`.

## Risks and Edge Cases
Queue correctness depends on strict ring invariants and memory barriers around SHI/HSI updates. Timeout and purge paths must avoid reusing fetched-but-not-completed DDCBs. `queue_wake_up_all()` wakes `ddcb_act` repeatedly rather than each index, which is worth reviewing in fatal paths. Completion VCRC mismatches are logged but do not by themselves fail the request after hardware completion. The file contains several old-SLU/new-ATS conditionals, so regressions can be generation-specific.

## Test Signals
Useful signals include DDCB enqueue/completion under interrupt and polling modes, nonblocking `-EBUSY`, timeout plus purge behavior, VCRC/ICRC error injection, card removal with in-flight requests, PF GFIR recovery wakeups, and debug-data copyout. Ring wrap tests should stress `ddcb_act`, `ddcb_next`, full-queue behavior, and busy waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.h -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.h

## Purpose
`card_ddcb.h` defines the GenWQE hardware DDCB wire layout, queue interlock bits, CRC length helpers, and GenWQE scatter-gather entry format used by queue execution and DMA fixups.

## Important APIs, Types, and Functions
The central type is packed `struct ddcb`, containing ICRC/HSI/SHI, preamble, sequence, command fields, old ASIV or new ATS+ASIV union, ASV, VCRC, timestamps, return status, counters, private debug bytes, and dispatch timestamp. `struct sg_entry` is the 16-byte hardware SGL entry. Constants include `ASIV_LENGTH`, `ASIV_LENGTH_ATS`, `ASV_LENGTH`, `DDCB_*_BE32`, `DDCB_PRESET_PRE`, `ICRC_LENGTH()`, `VCRC_LENGTH()`, and SGL flags `SG_CHAINED`, `SG_DATA`, and `SG_END_LIST`.

## Control Flow
The header itself has no control flow, but its layout controls the copy and checksum ranges in `card_ddcb.c` and SGL emission in `card_utils.c`. The 32-bit interlock macros allow atomic compare-and-swap over ICRC/HSI/SHI instead of byte-sized operations.

## State and Persistence
DDCBs live in coherent DMA memory shared with hardware. Fields are big-endian and packed; the private bytes are only driver-visible debug markers. SGL entries persist only for the lifetime of a request's DMA mapping.

## Dependencies and Integration Points
It includes `genwqe_driver.h` and `card_base.h` and is consumed by the GenWQE device, utility, debugfs, and DDCB queue code. Its structure must match service-layer hardware specifications.

## Risks and Edge Cases
Any field movement breaks hardware ABI. The union between legacy ASIV and ATS mode makes length handling generation-sensitive. The spelling/comments around DDCB/ASIV are historical; tests should rely on structure sizes and offsets, not names.

## Test Signals
Build-time or static checks should validate `sizeof(struct ddcb)`, offsets, packed behavior, endian annotations, and SGL entry size. Runtime DDCB CRC and queue-completion tests indirectly validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_debugfs.c

## Purpose
`card_debugfs.c` exposes GenWQE diagnostic state through debugfs. It dumps current and previous FFDC registers, DDCB queue state, job timers, queue working time, and tunables used during recovery and timeout debugging.

## Important APIs, Types, and Functions
Public lifecycle functions are `genwqe_init_debugfs()` and `genqwe_exit_debugfs()`. Show helpers include `curr_dbg_uidn_show()`, `prev_dbg_uidn_show()`, `curr_regs_show()`, `prev_regs_show()`, `jtimer_show()`, `queue_working_time_show()`, `ddcb_info_show()`, and `info_show()`, wrapped with `DEFINE_SHOW_ATTRIBUTE`.

## Control Flow
Initialization creates a per-card directory, common files (`ddcb_info`, `info`, `err_inject`, `ddcb_software_timeout`, `kill_timeout`), and for privileged PFs adds current/previous register dumps, UID debug buffers, VF job-timeout controls, job timer views, queue working time, and recovery toggles. Current FFDC readers stop traps before reading hardware buffers, then restart traps. Exit removes the card debugfs tree recursively.

## State and Persistence
Debugfs files expose live `struct genwqe_dev` state and MMIO register snapshots. Writable debugfs nodes directly modify in-memory fields such as timeout, error injection, and recovery flags. No settings persist across driver reload.

## Dependencies and Integration Points
The file depends on debugfs, seq_file, FFDC helpers from `card_utils.c`, queue definitions from `card_ddcb.h`, and `genwqe_dev` state from `card_base.h`. It is created from `genwqe_device_create()` and removed during device teardown.

## Risks and Edge Cases
Debugfs has intentionally broad debug access, including writable error injection and timeout knobs. `curr_regs_show()` allocates a register array but does not free it after printing, which is a leak on reads. Hardware reads can be unreliable during reset or PCI error recovery; privileged filtering limits some exposure to PFs.

## Test Signals
Mount debugfs and verify all expected files for PF versus VF, queue dumps with active requests, FFDC reads before/after injected GFIR, and teardown without stale dentries. Memory-leak tooling should cover repeated register-dump reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_dev.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_dev.c

## Purpose
`card_dev.c` implements the GenWQE character device. It tracks open files, mmap-created coherent DMA buffers, pinned user pages, DDCB address fixups, flash update/read commands, ioctl register access, async notification, and device-node creation/removal.

## Important APIs, Types, and Functions
The file operations are `genwqe_open()`, `genwqe_release()`, `genwqe_fasync()`, `genwqe_mmap()`, and `genwqe_ioctl()`. Public device lifecycle functions are `genwqe_device_create()` and `genwqe_device_remove()`. Important helpers include mapping/pinning functions `genwqe_search_pin()`, `__genwqe_search_mapping()`, `genwqe_pin_mem()`, `genwqe_unpin_mem()`, `genwqe_remove_mappings()`, `genwqe_remove_pinnings()`, DDCB fixup helpers `ddcb_cmd_fixups()` and `ddcb_cmd_cleanup()`, command dispatch `genwqe_execute_ddcb()`/`do_execute_ddcb()`, and flash helpers `do_flash_update()`/`do_flash_read()`.

## Control Flow
Open allocates a per-file `genwqe_file`, initializes raw-mapping and pinned-memory lists, records the opener PID, and stores it in `filp->private_data`. `mmap()` allocates coherent DMA memory, maps it into user space, records the user/kernel/DMA tuple, and frees it from `genwqe_vma_close()`. DDCB ioctls copy a command from user space, optionally replace ASIV user addresses with DMA addresses or generated SGL pointers, execute the raw DDCB through `card_ddcb.c`, clean temporary mappings, and copy result fields back. Flash update/read chunk user buffers into 256 KiB coherent buffers and send `SLCMD_MOVE_FLASH` DDCBs. Device removal first signals async users, escalates to SIGKILL if descriptors remain, then refuses to continue if the cdev still has unexpected references.

## State and Persistence
Per-open state contains raw DMA mappings, pinned mappings, async queue, opener PID, and client pointer. Kernel state persists only while the device/file is open; flash operations persist data on the accelerator card. The driver writes a DMA address into the first bytes of mmap memory for `CAP_SYS_ADMIN` users when the allocation is larger than a DMA address.

## Dependencies and Integration Points
This file bridges user ABI definitions from `linux/genwqe/genwqe_card.h`, GenWQE DDCB execution, DMA/SGL helpers from `card_utils.c`, sysfs groups from `card_sysfs.c`, debugfs setup, cdev/device core, PCI state, and capabilities checks.

## Risks and Edge Cases
The user ABI allows raw register writes and raw DDCBs to privileged callers, so capability and read-only checks matter. Mapping lookups use user virtual address ranges and must handle overflow and partial ranges correctly. Temporary SGL mappings are cleaned after execution, while explicit pins survive until unpinned or file close. `genwqe_device_remove()` panics on unexpected references, which is severe during hot-unplug or stuck user processes. Flash size and page alignment restrictions are strict, and older SLU versions follow different ASIV layouts.

## Test Signals
Exercise all ioctls for success and permission failures, mmap/unmap cleanup, pin/unpin including killed processes, DDCB flat and SGL ATS fixups, raw DDCB privileged-only behavior, flash read/update errors, PCI offline `-EIO`, nonblocking queue busy paths, and device removal with open descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_sysfs.c

## Purpose
`card_sysfs.c` defines GenWQE device sysfs attributes for card status, IDs, type, temperature, timers, queue working time, clock, bitstream selection, and bitstream reload requests.

## Important APIs, Types, and Functions
Read-only attributes are `status`, `appid`, `version`, `type`, `tempsens`, `freerunning_timer`, `queue_working_time`, `base_clock`, and `curr_bitstream`. Writable or write-only attributes are `next_bitstream` and `reload_bitstream`. `genwqe_is_visible()` filters PF-only attributes from VFs. `genwqe_attribute_groups` is exported for device creation.

## Control Flow
`device_create_with_groups()` installs `genwqe_attribute_groups`. Show functions read `struct genwqe_dev` or MMIO registers and format text. `next_bitstream_store()` parses partition 0 or 1 and writes the softreset register. `reload_bitstream_store()` sets card state to `GENWQE_CARD_RELOAD_BITSTREAM` only from unused/used states. Attribute visibility returns all attributes for privileged PFs and only normal attributes for VFs.

## State and Persistence
Most attributes expose live card registers. `next_bitstream` updates `cd->softreset` and hardware softreset selection; `reload_bitstream` changes in-memory card state to trigger a later reload path. No sysfs text itself is persisted.

## Dependencies and Integration Points
The file depends on GenWQE MMIO helpers, card type/clock/app-id helpers, device core attributes, and `genwqe_is_privileged()` policy. It is integrated by `card_dev.c` when creating the device node.

## Risks and Edge Cases
Some bitstream data is documented as unreliable with older CPLD versions. Sysfs stores parse integers but do not serialize against all other card-state transitions. VF visibility is critical because many registers are PF-only.

## Test Signals
Validate PF versus VF attribute visibility, register formatting, invalid partition/reload writes, reload state transitions, app-id sanitization, and behavior when MMIO reads return all ones during PCI error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_utils.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_utils.c

## Purpose
`card_utils.c` supplies shared GenWQE utilities: endian-aware MMIO accessors with error injection, custom GenWQE CRC32, coherent DMA allocation, user-page pinning and DMA mapping, SGL construction with first/last-page bounce buffers, reset/interrupt helpers, FFDC register collection, VF virtual-window register access, base-clock decoding, and trap control.

## Important APIs, Types, and Functions
Key functions include `__genwqe_writeq()`, `__genwqe_readq()`, `__genwqe_writel()`, `__genwqe_readl()`, `genwqe_read_app_id()`, `genwqe_init_crc32()`, `genwqe_crc32()`, `__genwqe_alloc_consistent()`, `__genwqe_free_consistent()`, `genwqe_user_vmap()`, `genwqe_user_vunmap()`, `genwqe_alloc_sync_sgl()`, `genwqe_setup_sgl()`, `genwqe_free_sync_sgl()`, `genwqe_card_reset()`, `genwqe_set_interrupt_capability()`, `genwqe_read_ffdc_regs()`, `genwqe_ffdc_buff_size()`, `genwqe_ffdc_buff_read()`, `genwqe_read_vreg()`, `genwqe_write_vreg()`, `genwqe_base_clock_frequency()`, `genwqe_stop_traps()`, and `genwqe_start_traps()`.

## Control Flow
MMIO helpers reject injected failures, missing mappings, or offline PCI channels and convert to/from big-endian hardware representation. User mapping pins pages with `pin_user_pages_fast()`, maps each page for DMA, and later unmaps and unpins with dirty marking according to write direction. SGL allocation creates coherent descriptor memory and bounce buffers for partial first/last pages, copies user data into bounce buffers for input, emits chained 8-entry SGL blocks, and copies bounce output back during free. FFDC helpers walk global, unit, secondary, extended-error, trap, and trace registers into arrays used by debugfs.

## State and Persistence
Global CRC32 lookup state lives in `crc32_tab` after initialization. DMA mapping state is held in caller-owned `dma_mapping` and `genwqe_sgl` structures. Reset and trap functions modify hardware registers; no file-system persistence exists.

## Dependencies and Integration Points
This file is used by nearly all GenWQE modules. It depends on PCI DMA APIs, page pinning, I/O accessors, GenWQE register constants, `card_ddcb.h` SGL formats, and debugfs/sysfs/device code that consumes its helpers.

## Risks and Edge Cases
DMA mappings are bidirectional even when comments note read/write refinement. SGL size allocation can fail for large user ranges due to coherent-order limits. Partial-page bounce handling is subtle and must preserve data on writable mappings. MMIO helpers silently return all-ones on failures, so callers must distinguish real register values from error sentinels where possible.

## Test Signals
Run CRC32 known-vector tests, MMIO endian/error-injection tests, pin/unpin leak checks, SGL descriptor decoding for aligned and unaligned buffers, first/last-page copyback tests, FFDC register array bounds tests, reset on old bitstreams, and MSI allocation fallback/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/genwqe_driver.h -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/genwqe_driver.h

## Purpose
`genwqe_driver.h` is the shared GenWQE driver header for versioning, minor-number constants, public DDCB request allocation/free prototypes, CRC32 declaration, and debug hexdump support.

## Important APIs, Types, and Functions
It defines `DRV_VERSION` as `2.0.25`, `GENWQE_MAX_MINOR`, declares `ddcb_requ_alloc()`, `ddcb_requ_free()`, and `genwqe_crc32()`, and provides `genwqe_hexdump()` as a thin wrapper around `print_hex_dump_debug()` with GenWQE/PCI prefixing.

## Control Flow
No standalone control flow exists. Callers include this header to allocate DDCB requests, use the GenWQE-specific CRC, and print debug hex dumps in queue/device paths.

## State and Persistence
The header stores no state. Its constants influence device numbering and user-visible version reporting.

## Dependencies and Integration Points
It includes core kernel structures, PCI/cdev/list/kthread/scatterlist/IOMMU/platform headers, byteorder helpers, and the public user ABI header `linux/genwqe/genwqe_card.h`.

## Risks and Edge Cases
Static minor allocation caps devices at 128. Version changes must remain synchronized with sysfs/debugfs reporting. Header breadth can hide unnecessary dependencies in compile units.

## Test Signals
Build coverage across all GenWQE files, ABI include compatibility, and debug dump invocation under dynamic debug are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/genwqe_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hi6421v600-irq.c -->
# sources/distributed-fs/ceph-client/drivers/misc/hi6421v600-irq.c

## Purpose
`hi6421v600-irq.c` implements a nested interrupt controller for the HiSilicon Hi6421v600 PMIC. It maps PMIC interrupt status bits into Linux virtual IRQs, masks/unmasks bits through regmap, and handles the parent PMIC IRQ.

## Important APIs, Types, and Functions
`struct hi6421v600_irq` holds device, irqdomain, parent IRQ, per-source virtual IRQs, regmap, and a mask spinlock. `enum hi6421v600_irq_list` names 14 PMIC sources. Important functions are `hi6421v600_irq_handler()`, `hi6421v600_irq_mask()`, `hi6421v600_irq_unmask()`, `hi6421v600_irq_map()`, `hi6421v600_irq_init()`, and `hi6421v600_irq_probe()`.

## Control Flow
Probe obtains the parent PMIC regmap from parent driver data, finds the parent IRQ from the PMIC platform device, masks and clears PMIC banks, allocates an irqdomain of 14 hwirqs, creates virtual mappings, and requests a shared low-triggered IRQ. The handler reads two IRQ status bytes, writes them back to acknowledge, dispatches power-key down before up when both bits are present, and calls `generic_handle_irq_safe()` for each pending bit.

## State and Persistence
State is devm-managed and persists while the platform device exists. Hardware mask and pending registers are the persistent PMIC state touched by the driver. No software state survives removal.

## Dependencies and Integration Points
The driver depends on the parent `hi6421-spmi-core` style device to provide regmap and IRQ resources. It integrates with the irqdomain core and downstream child devices that consume PMIC IRQ specifiers via two-cell translation.

## Risks and Edge Cases
Regmap read/write return values are ignored, so bus errors can silently drop masks or events. Removal is devm-assisted but the irqdomain is not explicitly removed on partial mapping failures. The special power-key ordering assumes both bits in bank 0 mean down then up.

## Test Signals
Validate irqdomain mapping for all 14 sources, mask/unmask register bit changes, pending-bit acknowledgement, both-powerkey ordering, shared IRQ `IRQ_NONE` absence by design, and probe deferral/failure when parent drvdata or IRQ is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hi6421v600-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hisi_hikey_usb.c -->
# sources/distributed-fs/ceph-client/drivers/misc/hisi_hikey_usb.c

## Purpose
`hisi_hikey_usb.c` controls USB role routing and hub/type-C power on HiKey boards. It relays a board-level hub role switch to an underlying device role switch while manipulating GPIOs and a hub regulator.

## Important APIs, Types, and Functions
`struct hisi_hikey_usb` stores GPIO descriptors, regulator, role switches, current role, mutex, and work item. Helpers are `hub_power_ctrl()`, `usb_switch_ctrl()`, `usb_typec_power_ctrl()`, `relay_set_role_switch()`, `hub_usb_role_switch_set()`, `hisi_hikey_usb_of_role_switch()`, `hisi_hikey_usb_probe()`, and `hisi_hikey_usb_remove()`.

## Control Flow
Probe allocates state, gets the `hub-vdd` regulator, and if `usb-role-switch` is present, acquires OTG switch/type-C VBUS/reset GPIOs, gets the underlying device role switch, initializes work, and registers a new hub role switch. Role changes store the requested role under mutex and schedule work. The worker powers off/on the correct path, selects hub or Type-C routing, then sets the underlying role switch.

## State and Persistence
State is per platform device and devm-managed. The persistent external state is GPIO level and regulator enablement. The current role is cached in memory until removed.

## Dependencies and Integration Points
It depends on GPIO descriptors, regulator framework, USB role-switch framework, firmware properties, and the `hisilicon,usbhub` compatible. It is board-glue code between the connector/user role-switch consumers and underlying USB controller role switch.

## Risks and Edge Cases
`remove()` unregisters the role switch but does not cancel pending work, so late work could access unregistered state. `relay_set_role_switch()` ignores the return from `usb_role_switch_set_role()`. Regulator `is_enabled` errors are treated like boolean status. Probe without `usb-role-switch` only obtains the regulator and remove powers the hub off.

## Test Signals
Test host, device, and none role transitions, GPIO/regulator ordering, missing optional reset GPIO, probe deferral for regulator or device role switch, removal with queued work, and role-switch error handling through fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hisi_hikey_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hmc6352.c -->
# sources/distributed-fs/ceph-client/drivers/misc/hmc6352.c

## Purpose
`hmc6352.c` is a small I2C sysfs driver for the Honeywell HMC6352 compass. It exposes heading reads and calibration/power commands.

## Important APIs, Types, and Functions
Key helpers are `compass_command()`, `compass_store()`, `compass_calibration_store()`, `compass_power_mode_store()`, `compass_heading_data_show()`, `hmc6352_probe()`, and `hmc6352_remove()`. Sysfs attributes are `hmc6352/heading0_input`, `hmc6352/calibration`, and `hmc6352/power_state`.

## Control Flow
Probe creates the sysfs group. Heading reads send command `A`, sleep 10 ms, read two bytes, and print tenths of degrees. Calibration writes map numeric inputs 0/1 to commands `E`/`C`, and power writes map 0/1 to `S`/`W`; input indices are bounds-checked and passed through `array_index_nospec()`.

## State and Persistence
The driver has no per-device allocation and uses a global mutex to serialize all compass commands. Device calibration or power mode persists in the hardware, not in driver memory.

## Dependencies and Integration Points
It depends on the I2C core, sysfs, sleep timing, and nospec index hardening. It registers as an I2C driver with ID `hmc6352`.

## Risks and Edge Cases
The global mutex serializes all instances unnecessarily. `i2c_master_send()` success is checked as `ret != 1` for heading but store treats any nonnegative result as success; short writes could be accepted in store. No device-tree/of match is provided here.

## Test Signals
Validate sysfs group creation/removal, heading read formatting, I2C transfer failure and short-transfer behavior, calibration/power invalid inputs, concurrent sysfs accesses, and suspend/resume interactions if the adapter powers down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hmc6352.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hpilo.c -->
# sources/distributed-fs/ceph-client/drivers/misc/hpilo.c

## Purpose
`hpilo.c` implements the character-device driver for HP iLO management processors. It maps PCI BARs, creates one device with multiple channel-control-block minors, allocates DMA-backed send/receive FIFOs per open channel, handles doorbells and interrupts, and exposes read/write/poll packet exchange to user space.

## Important APIs, Types, and Functions
File operations are `ilo_open()`, `ilo_close()`, `ilo_read()`, `ilo_write()`, and `ilo_poll()`. PCI/module lifecycle uses `ilo_init()`, `ilo_exit()`, `ilo_probe()`, and `ilo_remove()`. Queue/channel helpers include `fifo_enqueue()`, `fifo_dequeue()`, `fifo_check_recv()`, `ilo_pkt_enqueue()`, `ilo_pkt_dequeue()`, `ilo_ccb_setup()`, `ilo_ccb_open()`, `ilo_ccb_verify()`, `ilo_ccb_close()`, `ilo_isr()`, `ilo_map_device()`, and `ilo_unmap_device()`.

## Control Flow
Module init registers class, char-device range, and PCI driver. Probe filters a blacklist, clamps `max_ccb`, reserves a device slot, enables PCI, maps MMIO/shared RAM/doorbell BARs, clears pending device bits, requests a shared IRQ, enables interrupts, adds a cdev range, and creates `hpilo!d%dccb%d` nodes. Open either creates a new CCB for the minor or shares an existing one unless exclusive flags conflict. CCB setup allocates coherent memory for send/recv FIFOs and descriptor areas, writes a hardware view of the CCB to mapped shared memory, prequeues send and receive descriptors, and verifies iLO consumes a send entry. Write dequeues a send descriptor, copies user data, enqueues it, and rings the doorbell; read waits/retries for a receive descriptor, copies data to user, and returns the descriptor. ISR reads pending doorbell bits, marks all channels reset on reset bit, wakes affected wait queues, and clears handled bits.

## State and Persistence
Global module state tracks the major, max CCB count, and one occupied device slot. Per-device `ilo_hwinfo` stores BAR mappings, cdev, locks, PCI device, and active `ccb_data` pointers. Per-channel `ccb_data` stores software/hardware CCBs, coherent DMA memory, mapped device CCB pointer, wait queue, refcount, and exclusivity. Hardware reset state is mirrored in FIFO reset flags.

## Dependencies and Integration Points
The driver depends on PCI, cdev/device class, coherent DMA, wait queues, poll, shared IRQs, and the hardware layouts in `hpilo.h`. It supports Compaq/HP PCI IDs and avoids disabling the PCI device on remove due to shared interrupt-line behavior with a USB function.

## Risks and Edge Cases
Lock ordering is documented and important: open lock, allocation lock, then FIFO lock. Open failure paths must not leak coherent CCB memory. `ilo_read()` can block up to roughly two seconds via retry sleep even though poll exists. Device reset forces applications to close/reopen channels. `device_create()` errors are logged but do not unwind already created nodes. Shared CCB references rely on open_lock serialization.

## Test Signals
Test probe/remove on both BAR layouts, max/min `max_ccb` clamping, exclusive and shared opens, read/write packet lengths, poll wakeups, IRQ reset handling, close while active, failure injection for DMA allocation and IRQ request, and module unload with open channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hpilo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hpilo.h -->
# sources/distributed-fs/ceph-client/drivers/misc/hpilo.h

## Purpose
`hpilo.h` defines constants, queue bitfields, and shared structures for the HP iLO driver, including hardware info, channel control blocks, per-file channel data, and FIFO descriptors.

## Important APIs, Types, and Functions
Important types are `struct ilo_hwinfo`, `struct ccb`, `struct ccb_data`, and `struct fifo`. Constants define device limits (`MAX_CCB`, `MIN_CCB`, `MAX_ILO_DEV`, `MAX_OPEN`), wait timing, doorbell offsets, CCB sizes, FIFO queue IDs, control bit positions, descriptor entry bitfields, and conversion macro `FIFOBARTOHANDLE()`.

## Control Flow
The header has no executable flow. Its layouts determine how `hpilo.c` allocates coherent memory, fills software and hardware CCB views, manipulates FIFO head/tail entries, and interprets doorbell reset bits.

## State and Persistence
Structures in this header represent per-device state, per-open channel state, and DMA memory shared with iLO hardware. The FIFO `reset` flag is software-visible state used to force close/reopen after device reset.

## Dependencies and Integration Points
It is private to the `hpilo` driver and relies on PCI, cdev, spinlock, wait queue, DMA address, and I/O memory types included by the C file context.

## Risks and Edge Cases
Hardware ABI depends on exact CCB size and field ordering. Descriptor bitfield macros use integer shifts and masks; invalid lengths or descriptor IDs can corrupt queue state if not bounded by callers. `MAX_ILO_DEV` is one, limiting multi-device support.

## Test Signals
Compile-time structure size/offset checks, FIFO entry encode/decode tests, open limit tests, and hardware queue traces are the main signals that the definitions remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/hpilo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/Makefile

## Purpose
The `ibmasm/Makefile` builds the IBM ASM service processor driver object from its component files and conditionally includes UART support.

## Important APIs, Types, and Functions
It defines `obj-$(CONFIG_IBM_ASM) := ibmasm.o`, lists core objects `module.o`, `ibmasmfs.o`, `event.o`, `command.o`, `remote.o`, `heartbeat.o`, `r_heartbeat.o`, `dot_command.o`, and `lowlevel.o`, and adds `uart.o` when `CONFIG_SERIAL_8250` is enabled.

## Control Flow
Kbuild links the listed objects into one `ibmasm.o` module/built-in object. The order reflects module entry points first, then filesystem/event/command/remote/heartbeat/protocol/low-level support.

## State and Persistence
No runtime state exists in the Makefile.

## Dependencies and Integration Points
It integrates with Kbuild configuration symbols `CONFIG_IBM_ASM` and `CONFIG_SERIAL_8250`.

## Risks and Edge Cases
If optional UART code is excluded, the inline stubs in `ibmasm.h` must satisfy all references. Adding new source files requires updating this list or symbols will be missing.

## Test Signals
Build with `CONFIG_IBM_ASM=m/y` and with `CONFIG_SERIAL_8250` enabled and disabled to validate both object compositions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/command.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/command.c

## Purpose
`command.c` serializes dot-command execution to the IBM ASM service processor. It allocates command buffers, queues commands, sends one active command through the low-level I2O path, waits for responses, and advances queued work.

## Important APIs, Types, and Functions
Public functions are `ibmasm_new_command()`, `ibmasm_free_command()`, `ibmasm_exec_command()`, `ibmasm_wait_for_response()`, and `ibmasm_receive_command_response()`. Internal helpers are `enqueue_command()`, `dequeue_command()`, `do_exec_command()`, and `exec_next_command()`.

## Control Flow
Callers allocate a command with bounded buffer size, fill it, and call `ibmasm_exec_command()`. If no command is active, it becomes `sp->current_command`, gains a reference, and is sent with `ibmasm_send_i2o_message()`; otherwise it is appended to `sp->command_queue`. Responses from interrupt context copy data into the current command buffer, mark status complete, wake waiters, drop the active reference, and dispatch the next queued command. Send failure marks the current command failed and also advances the queue.

## State and Persistence
State is in `struct command` buffers, krefs, wait queues, statuses, and the service processor's current/queued command pointers. `command_count` is debug-only global state. Nothing persists beyond memory.

## Dependencies and Integration Points
The file depends on `ibmasm.h`, low-level I2O send support, service-processor spinlock, wait queues, krefs, and dot-command callers from filesystem, heartbeat, and setup code.

## Risks and Edge Cases
`ibmasm_wait_for_response()` ignores the return value from interrupted waits, so callers rely on status inspection. `ibmasm_free_command()` unconditionally `list_del()`s the queue node, making initialization and list state important. Response handling assumes only one current command and that response size fits by truncation to the command buffer.

## Test Signals
Exercise sequential command ordering, queued command advancement after success and send failure, timeout behavior, interrupted waits, oversized buffer rejection, kref balance under filesystem close, and response truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.c

## Purpose
`dot_command.c` dispatches incoming service-processor dot commands and sends built-in driver VPD and OS state dot commands during driver initialization/removal.

## Important APIs, Types, and Functions
Public functions are `ibmasm_receive_message()`, `ibmasm_send_driver_vpd()`, and `ibmasm_send_os_state()`. `struct os_state_command` packages the OS-state command. It uses `struct dot_command_header` and helpers from `dot_command.h`.

## Control Flow
Incoming interrupt data is ignored if empty or malformed, clamped to the inbound message size, and dispatched by header type to event, command-response, or heartbeat handlers. Driver VPD creates a write dot command `4.3.5.10` with the IBMASM driver VPD string, executes it, waits for the normal timeout, and returns `-ENODEV` if incomplete. OS state sends command `4.3.6` with up/down data and waits similarly.

## State and Persistence
The file itself stores no long-lived state. The VPD and OS-state commands temporarily allocate `struct command` objects and affect service-processor state, especially heartbeat behavior.

## Dependencies and Integration Points
It integrates command execution, event handling, heartbeat handling, and module probe/remove. It depends on dot-command wire layout and service-processor command queues.

## Risks and Edge Cases
Incoming command size is trusted after only header-based calculation and clamping; malformed command/data sizes can change dispatch size. `strcat()` into the VPD data buffer relies on the zeroed command allocation and fixed buffer sizing. Unknown message types are logged but otherwise dropped.

## Test Signals
Validate dispatch for event/response/heartbeat, malformed zero or oversized sizes, VPD command buffer bytes, OS up/down during probe/remove, and timeout handling when the service processor does not respond.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.h

## Purpose
`dot_command.h` defines the IBM ASM dot-command protocol header, message type constants, size calculation, and timeout classification.

## Important APIs, Types, and Functions
It defines type values `sp_write`, `sp_write_next`, `sp_read`, `sp_read_next`, `sp_command_response`, `sp_event`, and `sp_heartbeat`. Packed `struct dot_command_header` contains type, command size, data size, status, and reserved fields. Inline helpers are `get_dot_command_size()` and `get_dot_command_timeout()`.

## Control Flow
Callers use `get_dot_command_size()` to validate or size outgoing/incoming buffers. `get_dot_command_timeout()` returns extended timeout for selected long-running commands `6.3.1`, `7.1`, and `8.x`, otherwise normal timeout.

## State and Persistence
No state is stored. The packed header describes transient command buffers exchanged with the service processor.

## Dependencies and Integration Points
The header depends on `IBMASM_CMD_TIMEOUT_*` constants from `ibmasm.h` and is consumed by command, filesystem, heartbeat, and low-level message code.

## Risks and Edge Cases
The inline size helper performs no overflow checking on command and data sizes. Timeout classification assumes command bytes are present according to `command_size`; callers must validate buffer length first.

## Test Signals
Unit-style tests can feed representative headers to verify size and timeout selection, including short buffers, maximum data sizes, and long-running command patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/event.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/event.c

## Purpose
`event.c` stores asynchronous IBM ASM service-processor events in a circular buffer and delivers them to registered ibmasmfs event readers.

## Important APIs, Types, and Functions
Public functions are `ibmasm_event_buffer_init()`, `ibmasm_event_buffer_exit()`, `ibmasm_receive_event()`, `ibmasm_event_reader_register()`, `ibmasm_event_reader_unregister()`, `ibmasm_get_next_event()`, and `ibmasm_cancel_next_event()`. Helpers include `wake_up_event_readers()` and `event_available()`.

## Control Flow
Initialization allocates an `event_buffer`, clears serial numbers, and initializes the reader list. Incoming events from interrupt context are truncated to `IBMASM_EVENT_MAX_SIZE`, copied from I/O memory into the next circular slot, assigned a serial number, and all readers are woken. Readers register with the current next serial, block until an event or cancellation, find the first event at or after their expected serial, copy it into reader-private storage, and advance their serial.

## State and Persistence
The service processor owns one circular buffer with ten events, next index, next serial, and a list of readers. Each reader tracks cancellation, next serial, wait queue, and latest copied event. Old events are overwritten if readers fall behind.

## Dependencies and Integration Points
It depends on `sp->lock`, wait queues, list management, and ibmasmfs event file operations. Incoming data is passed by `dot_command.c` from the low-level interrupt path.

## Risks and Edge Cases
Readers that lag by more than the circular buffer depth lose events silently and resume at the oldest still matching serial scan. `wake_up_event_readers()` walks the reader list without taking the service-processor lock, which relies on surrounding usage not racing with unregister. Cancellation returns zero if no event is available.

## Test Signals
Test reader registration/unregistration, blocking read wakeups, cancellation by write, circular overwrite behavior, max-size truncation, concurrent readers, and interrupt-context receive while readers close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/heartbeat.c

## Purpose
`heartbeat.c` responds to service-processor heartbeats and registers a panic notifier so heartbeats stop after kernel panic, allowing the service processor to reboot the system if expected.

## Important APIs, Types, and Functions
Public functions are `ibmasm_register_panic_notifier()`, `ibmasm_unregister_panic_notifier()`, `ibmasm_heartbeat_init()`, `ibmasm_heartbeat_exit()`, and `ibmasm_receive_heartbeat()`. Internal state is `suspend_heartbeats` and `panic_notifier`.

## Control Flow
Init allocates a reusable heartbeat command buffer. On heartbeat message receipt, if suspension is not active, the driver copies the incoming dot command into the heartbeat command buffer, changes the type to `sp_write`, marks it pending, and executes it as a response. Exit waits for any heartbeat command, sets suspension, and drops the command reference. Panic notification sets suspension without further cleanup.

## State and Persistence
Heartbeat state is per service processor through `sp->heartbeat` plus global `suspend_heartbeats`. Once set, suspension remains until module reload.

## Dependencies and Integration Points
It depends on command execution, dot-command headers, the panic notifier chain, and low-level interrupt dispatch through `ibmasm_receive_message()`.

## Risks and Edge Cases
`suspend_heartbeats` is global, so one panic or exit affects all service processors. Reusing one command object for repeated heartbeats depends on serialized command execution and service-processor timing. Panic-path behavior intentionally stops responding rather than trying to clean up.

## Test Signals
Validate heartbeat response bytes, repeated heartbeats under load, module removal waiting for pending heartbeat, panic notifier registration/unregistration, and behavior with multiple service processors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/i2o.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/i2o.h

## Purpose
`i2o.h` defines the I2O message wrapper used by the IBM ASM low-level mailbox transport.

## Important APIs, Types, and Functions
Packed `struct i2o_header` contains version, flags, size, target/initiator fields, function, and context. `I2O_HEADER_TEMPLATE` supplies default values. `struct i2o_message` combines the header and payload pointer field. Inline helpers are `outgoing_message_size()` and `incoming_data_size()`.

## Control Flow
Outgoing command code calculates a 32-bit-word message size from payload length, capped at `I2O_COMMAND_SIZE`. Incoming interrupt code multiplies the header message-size field by four to get payload span passed to dot-command dispatch.

## State and Persistence
No state is stored. Structures map transient MMIO mailbox frames.

## Dependencies and Integration Points
It is consumed by `lowlevel.c` and depends on packed layout matching the service processor mailbox protocol.

## Risks and Edge Cases
`struct i2o_message` represents `data` as a pointer even though low-level code copies payload bytes to `&message->data`; this relies on the historical memory layout rather than normal pointer semantics. Incoming size calculation trusts hardware-provided `message_size`.

## Test Signals
Validate outgoing word-size rounding, max payload capping, header bytes written to MMIO, and incoming size handling for minimum and maximum mailbox frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/i2o.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasm.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasm.h

## Purpose
`ibmasm.h` is the central private header for the IBM ASM service processor driver. It defines driver metadata, protocol constants, core state structures, debug helpers, and cross-module function prototypes.

## Important APIs, Types, and Functions
Important structures include `struct command`, `struct ibmasm_event`, `struct event_buffer`, `struct event_reader`, `struct reverse_heartbeat`, `struct ibmasm_remote`, and `struct service_processor`. Inline helpers include `get_timestamp()`, `command_put()`, and `command_get()`. The header declares command, event, heartbeat, reverse heartbeat, dot-command, low-level, remote input, filesystem, and optional UART APIs.

## Control Flow
The header defines how modules coordinate through `struct service_processor`: module probe initializes it, low-level interrupts dispatch messages, command/event/heartbeat code uses `sp->lock`, ibmasmfs exposes files, remote input registers input devices, and UART support optionally binds an 8250 port.

## State and Persistence
All driver runtime state is memory-resident under `service_processor` plus per-command/readers. Driver VPD strings and system-state constants are protocol payloads sent to the service processor.

## Dependencies and Integration Points
It includes kernel list, wait, spinlock, kref, device, input, interrupt, and time facilities. It is included by every ibmasm C file.

## Risks and Edge Cases
The global debug macro depends on `ibmasm_debug`. `command_put()` takes the command's service-processor lock around `kref_put()`, so kref callbacks must be lock-compatible. Structure layouts are private but tightly coupled across modules.

## Test Signals
Build all ibmasm configurations, validate command kref lifecycle, multi-service-processor initialization, debug logging, and stubbed UART behavior when serial 8250 is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasmfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasmfs.c

## Purpose
`ibmasmfs.c` implements the `ibmasmfs` pseudo filesystem. When mounted, it creates per-service-processor directories with files for dot-command execution, event reads/cancellation, reverse heartbeat control, and remote-video display settings.

## Important APIs, Types, and Functions
Filesystem registration uses `ibmasmfs_register()`, `ibmasmfs_unregister()`, and `ibmasmfs_add_sp()`. Superblock helpers are `ibmasmfs_init_fs_context()`, `ibmasmfs_fill_super()`, `ibmasmfs_make_inode()`, `ibmasmfs_create_file()`, `ibmasmfs_create_dir()`, and `ibmasmfs_create_files()`. File operations are grouped under `command_fops`, `event_fops`, `r_heartbeat_fops`, and `remote_settings_fops`.

## Control Flow
Mount creates a single anonymous superblock root and then iterates the global service-processor list to create directories and files. Command writes validate one complete dot command, allocate a command, execute it synchronously with the protocol-specific timeout, and command reads return the completed response once. Event reads register a reader at open, allow one active blocking read, and writes cancel a sleeper. Reverse heartbeat reads run the periodic heartbeat loop until failure/interruption; writes stop an active loop. Remote settings read/write directly access MMIO display width, height, and depth registers.

## State and Persistence
The global `service_processors` list determines mount contents. Per-open private data stores command, event reader, or reverse-heartbeat state. The filesystem has no backing storage; remote setting writes persist only in service-processor registers.

## Dependencies and Integration Points
It depends on VFS simple directory helpers, anonymous superblocks, dot-command helpers, command/event/reverse-heartbeat modules, and remote register macros. `module.c` registers the filesystem and adds service processors after successful probe.

## Risks and Edge Cases
Service processors are added to a global list but not removed in `ibmasm_remove_one()`, creating a stale pointer risk for later mounts or mounted files after device removal. The list is not locked during mount creation. `remote_settings_file_write()` uses `simple_strtoul()` and writes unchecked values to MMIO. Command reads clear the stored command before verifying copyout success, so failed user copies lose the response.

## Test Signals
Mount/unmount with zero and multiple service processors, command write/read success and timeout, concurrent command reads/writes, event cancellation, reverse heartbeat stop, remote settings MMIO reads/writes, and hot-remove while mounted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasmfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.c

## Purpose
`lowlevel.c` implements the IBM ASM Condor mailbox transport. It sends current commands as I2O-wrapped dot-command messages and handles service-processor interrupts.

## Important APIs, Types, and Functions
Public functions are `ibmasm_send_i2o_message()` and `ibmasm_interrupt_handler()`. A static `i2o_header` initialized from `I2O_HEADER_TEMPLATE` is reused for outgoing messages.

## Control Flow
Sending computes the dot-command size, rejects commands larger than their allocated buffer, caps to I2O payload size, obtains an inbound MFA, copies the I2O header and command payload into MMIO message memory, and posts the MFA back inbound. The IRQ handler first verifies SP interrupt status, handles pending remote input and clears the mouse interrupt, reads an outbound MFA, dispatches its message data through `ibmasm_receive_message()`, returns the MFA, and reports handled.

## State and Persistence
Transport state is in hardware mailbox queues and the service processor's current command. The static header's `message_size` is updated for each send.

## Dependencies and Integration Points
It depends on `lowlevel.h` mailbox helpers, `i2o.h`, `dot_command.h`, `remote.h`, and the command/event/heartbeat dispatcher. It is registered as the shared IRQ handler by `module.c`.

## Risks and Edge Cases
The static header is shared across all service processors, which is harmless only if sends are serialized or the field is not concurrently observed. If no valid outbound MFA is returned, the handler still calls `set_mfa_outbound()` with the invalid value. Incoming message sizes are hardware-derived and passed through only later dot-command validation.

## Test Signals
Validate inbound MFA unavailable failure, oversized command rejection/capping, exact MMIO bytes for header and payload, interrupt `IRQ_NONE` when not pending, remote-input predispatch, invalid outbound MFA handling, and shared IRQ behavior with UART.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.h

## Purpose
`lowlevel.h` defines Condor service-processor PCI IDs, mailbox registers, interrupt masks, UART base offsets, and inline MMIO helpers for IBM ASM low-level communication.

## Important APIs, Types, and Functions
Constants include IBM vendor/device IDs, inbound/outbound queue ports, interrupt status/control registers, SP/UART masks, Scout COM base offsets, `NO_MFAS_AVAILABLE`, and mailbox bit helpers. Inline functions cover interrupt pending checks, interrupt enable/disable, MFA inbound/outbound get/set, valid-MFA checks, and converting an MFA to an `i2o_message` pointer.

## Control Flow
Higher-level code uses these helpers to mask/unmask SP and UART interrupts, poll for outbound MFAs with a short retry loop, detect full inbound mailbox, and translate mailbox frame addresses into MMIO pointers.

## State and Persistence
No software state is stored; helpers directly read and write MMIO registers.

## Dependencies and Integration Points
It includes `asm/io.h` and is consumed by module setup, low-level transport, heartbeat, command paths, and UART registration.

## Risks and Edge Cases
MMIO helpers have no locking or memory barriers beyond accessor semantics. `get_mfa_outbound()` loops without delay. `get_i2o_message()` trusts the MFA address after masking and maps it into the device BAR window.

## Test Signals
Hardware or emulated tests should verify interrupt mask bit polarity, inbound full handling, outbound invalid retry behavior, MFA address masking, and UART/SP interrupt coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/module.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/module.c

## Purpose
`module.c` is the PCI and module lifecycle for the IBM ASM service processor driver. It enables the RSA PCI device, allocates `service_processor` state, registers interrupts/input/filesystem hooks, sends initial service-processor state, and cleans everything up on removal and module exit.

## Important APIs, Types, and Functions
Primary functions are `ibmasm_init_one()`, `ibmasm_remove_one()`, `ibmasm_init()`, and `ibmasm_exit()`. The file defines `ibmasm_debug`, module parameter metadata, `ibmasm_pci_table`, and `ibmasm_driver`.

## Control Flow
Module init registers the PCI driver, then registers ibmasmfs and panic notifier. Probe enables PCI, requests BAR regions, allocates and initializes `service_processor`, allocates event and heartbeat resources, maps BAR0, requests the shared IRQ, enables SP interrupts, registers remote input devices, sends driver VPD and OS-up dot commands, adds the service processor to ibmasmfs, and optionally registers UART. Remove unregisters UART, sends OS-down, exits heartbeat, disables/free IRQ, frees remote input, unmaps BAR, releases events, frees the service processor, releases PCI regions, and disables the device.

## State and Persistence
Per-device state is held in `struct service_processor` and stored as PCI drvdata. Loading sends persistent service-processor-visible OS-up and VPD state; removal sends OS-down. The global debug flag persists as a module parameter while loaded.

## Dependencies and Integration Points
It coordinates all ibmasm modules, PCI core, low-level register helpers, remote input, ibmasmfs, panic notifier, and optional UART.

## Risks and Edge Cases
PCI driver registration occurs before filesystem registration; a probe could call `ibmasmfs_add_sp()` before successful fs registration. `ibmasm_remove_one()` does not remove `sp->node` from the ibmasmfs service-processor list, leaving stale references. Error unwind is layered but must remain in exact reverse initialization order.

## Test Signals
Test probe success and each failure label, module load/unload, PCI hot-remove, OS-up/down command failures, panic notifier lifecycle, remote input failure unwind, and ibmasmfs mounting before/after devices appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/r_heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/r_heartbeat.c

## Purpose
`r_heartbeat.c` implements reverse heartbeats: user-triggered periodic dot commands from the OS driver to the IBM ASM service processor.

## Important APIs, Types, and Functions
Public functions are `ibmasm_init_reverse_heartbeat()`, `ibmasm_start_reverse_heartbeat()`, and `ibmasm_stop_reverse_heartbeat()`. Static packed `rhb_dot_cmd` is a `sp_read` command `4.3.6`.

## Control Flow
Filesystem read starts a loop that allocates one command, repeatedly copies the reverse-heartbeat command into it, executes it, waits for a normal response, increments a failure count on incomplete responses, then sleeps up to `REVERSE_HEARTBEAT_TIMEOUT` unless stopped. The loop exits on three failures, signal, or explicit stop. Stop sets `rhb->stopped` and wakes the wait queue.

## State and Persistence
Per-open `struct reverse_heartbeat` stores wait queue and stopped flag. No state persists after close; the service processor observes the heartbeat commands.

## Dependencies and Integration Points
It depends on command execution, dot-command layout, wait queues, signal handling, and `ibmasmfs` reverse-heartbeat file operations.

## Risks and Edge Cases
The function returns `1` after three failures rather than a conventional negative errno. Signals and explicit stop both return `-EINTR`. The reusable command object is reset in-place each iteration.

## Test Signals
Validate normal repeated response, three-failure exit, write-triggered stop, signal interruption, command allocation failure, and concurrent read exclusion in ibmasmfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/r_heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.c

## Purpose
`remote.c` converts remote mouse and keyboard events from IBM ASM service-processor MMIO queues into Linux input events.

## Important APIs, Types, and Functions
Public functions are `ibmasm_handle_mouse_interrupt()`, `ibmasm_init_remote_input_dev()`, and `ibmasm_free_remote_input_dev()`. Internal helpers include key translation tables `xlate_high` and `xlate`, `print_input()`, `send_mouse_event()`, and `send_keyboard_event()`.

## Control Flow
Initialization allocates mouse and keyboard input devices, fills PCI IDs and capability bits, registers them, and enables mouse interrupts. The low-level interrupt handler calls `ibmasm_handle_mouse_interrupt()` when the remote queue has an interrupt. That function reads queue reader/writer indices, copies each remote input entry from MMIO, emits absolute mouse/button events or translated key events, advances the queue reader, and stops on invalid queue indices or unknown input type. Cleanup disables mouse interrupts and unregisters devices.

## State and Persistence
State is in `sp->remote.mouse_dev` and `sp->remote.keybd_dev`; queue reader/writer and display settings live in service-processor MMIO. Input state is reported to the kernel input subsystem and not stored by this file beyond registered devices.

## Dependencies and Integration Points
It depends on PCI device metadata, Linux input core, remote register macros from `remote.h`, and low-level interrupt dispatch. `ibmasmfs` separately exposes remote video settings.

## Risks and Edge Cases
Key translation indexes use 8-bit tables; unmapped keysyms report key code 0/`KEY_RESERVED`. Invalid reader/writer indices reset the reader to zero. Cleanup assumes input devices were registered. Mouse maximums are fixed constants rather than read from hardware.

## Test Signals
Feed MMIO queue entries for mouse buttons/movement, standard and high keysyms, unmapped keys, queue wrap, invalid indices, init failure at keyboard registration, and interrupt disable/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.h

## Purpose
`remote.h` defines IBM ASM remote-console MMIO offsets, remote input wire structures, queue helpers, display-setting address macros, and keysym constants.

## Important APIs, Types, and Functions
It defines offsets under `CONDOR_MOUSE_DATA`, display registers, ISR control/status, queue reader/writer/begin, input types, mouse button masks, `struct mouse_input`, `struct keyboard_input`, `struct remote_input`, address macros such as `mouse_addr()`, `display_width()`, and queue helpers like `get_queue_reader()`, `get_queue_writer()`, `get_queue_entry()`, and `advance_queue_reader()`. It also enumerates many X-style keysyms consumed by `remote.c`.

## Control Flow
Inline/macros directly read and write MMIO for interrupts and queue state. `advance_queue_reader()` wraps at `REMOTE_QUEUE_SIZE` and stores the new reader index in hardware.

## State and Persistence
No software state is stored. The macros operate on service-processor MMIO queue and display registers.

## Dependencies and Integration Points
It includes `asm/io.h` and is used by remote input, low-level interrupt handling, and ibmasmfs remote-video settings.

## Risks and Edge Cases
Macros evaluate `sp` and address expressions directly, so callers must pass valid live service-processor state. The many keysym constants are not self-validating; translation coverage must be maintained in `remote.c`.

## Test Signals
Validate queue address calculations, wrap behavior, display register read/write through ibmasmfs, ISR control/status operations, and translation table coverage for declared keysyms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/uart.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/uart.c

## Purpose
`uart.c` optionally registers the IBM ASM service processor's Scout COM B UART as an 8250 serial port when the service processor allows OS ownership.

## Important APIs, Types, and Functions
Public functions are `ibmasm_register_uart()` and `ibmasm_unregister_uart()`. It uses `struct uart_8250_port`, serial 8250 registration helpers, UART scratch register `UART_SCR`, and low-level UART interrupt enable/disable helpers.

## Control Flow
Registration reads the UART scratch register at `SCOUT_COM_B_BASE`; zero means the service processor owns the UART, so the driver records `serial_line = -1` and returns. Otherwise it initializes a memory-mapped shared-IRQ 8250 port with a 3.6864 MHz clock, registers it, stores the line number, and enables UART interrupts. Unregister disables UART interrupts and unregisters the 8250 line if one was registered.

## State and Persistence
The only driver state is `sp->serial_line`. Hardware UART ownership and interrupt mask state persist in device registers while enabled.

## Dependencies and Integration Points
The file is compiled only with `CONFIG_SERIAL_8250`. It depends on serial core/8250 APIs and low-level interrupt helpers, and is called by module probe/remove.

## Risks and Edge Cases
The scratch-register ownership heuristic is hardware-specific. UART shares the service processor IRQ, so interrupt masking must coexist with SP message interrupts. Failure to register leaves interrupts disabled because enabling happens only after success.

## Test Signals
Build with and without 8250, test scratch zero and nonzero cases, successful serial registration, failed registration, IRQ sharing with service-processor interrupts, and remove after no registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmasm/uart.c -->
