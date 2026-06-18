# Research: subset-b-004979

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/interface.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/interface.c

Purpose: This file owns the Linux `net_device` interface layer for Xen netback VIFs. It allocates and registers backend Ethernet devices, routes host TX packets into per-queue guest RX queues, exposes queue statistics through ethtool, and connects/disconnects Xen data and control rings to IRQs, NAPI, and backend kthreads.

Important APIs, types, and functions: `xenvif_alloc()` builds the `vif<domid>.<handle>` netdev and initializes `struct xenvif`; `xenvif_init_queue()` reserves grant-table mapping pages and queue rings; `xenvif_connect_data()` maps frontend TX/RX rings, creates RX and deallocation kthreads, installs NAPI, and binds split or shared event channels; `xenvif_connect_ctrl()` maps the control ring; `xenvif_start_xmit()` queues host SKBs for delivery to the frontend; `xenvif_up()`, `xenvif_down()`, `xenvif_carrier_on()`, and `xenvif_carrier_off()` bridge netdev state to backend queue state.

Control flow: Xenbus creates a `xenvif`, later calls data/control connect helpers, and finally turns carrier on. Host-originated packets enter `ndo_start_xmit`, are mapped to a queue via hash or netdev queue selection, filtered by multicast control if enabled, timestamped, and appended to the guest RX queue before the RX kthread is kicked. Guest TX interrupts schedule NAPI, while guest RX interrupts wake the RX kthread. Close/disconnect reverses this by disabling IRQs/NAPI, stopping kthreads, unmapping rings, freeing multicast state, and dropping carrier.

State and persistence behavior: State is in memory only: VIF feature flags, queue pointers, per-queue grant page pools, pending rings, interrupt numbers, RX/TX SKB queues, kthread handles, inflight zerocopy counters, credit timers, status bits, hash/multicast state, and aggregate stats. There is no persistent storage; XenStore negotiation reconstructs everything on reconnect.

Dependencies and integration points: The file depends on Linux netdev, NAPI, ethtool, RCU, kthreads, grant tables, Xen event channels with late EOI, Xenbus ring mapping, and helper APIs implemented in `netback.c`, `rx.c`, and hash/control code.

Risks: The main risks are lifecycle races between IRQ handlers, NAPI, kthreads, and disconnect; queue selection when `num_queues` changes under RCU; grant page leaks on partial setup failures; and zerocopy inflight accounting that must wake the deallocation thread after each completion. Event-channel EOI flags must be cleared exactly when no work is pending.

Test signals: Exercise hotplug/probe/remove, open/close, split and shared event channels, multi-queue queue selection, carrier transitions, multicast filtering, RX queue overflow/drop, kthread teardown with inflight zerocopy SKBs, ethtool stats aggregation, and reconnect paths after frontend or backend restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/netback.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/netback.c

Purpose: Implements the Xen netback backend datapath from frontend TX ring requests into Linux networking receive, plus the control-ring hash commands, grant unmap/deallocation thread, multicast control, credit rate limiting, and module initialization.

Important APIs, types, and functions: `xenvif_tx_action()` is the NAPI TX budget entry; `xenvif_tx_build_gops()` validates frontend requests, handles extras, allocates SKBs, and builds grant copy/map operations; `xenvif_tx_submit()` checks grant results and submits SKBs via `netif_receive_skb()`; `xenvif_tx_dealloc_action()` unmaps zerocopy grants after network stack completion; `process_ctrl_request()` dispatches Xen control-ring hash operations. Module parameters include `separate_tx_rx_irq`, RX drain/stall timeouts, queue count, `fatal_skb_slots`, hash cache size, and XDP headroom support.

Control flow: NAPI detects guest TX work, copies request records from the shared ring, applies credit throttling, parses extra-info records for GSO, hash, and multicast commands, counts/validates grant slots, copies the leading bytes into the SKB head, maps remaining slots as frags, then batches grant operations. Submit checks every copy/map status, releases or unmaps failed slots, fills SKB frags, sets checksum/GSO metadata, records stats, and injects the packet into the host stack. Later zerocopy callbacks enqueue pending indexes for the deallocation kthread, which unmaps grants and pushes frontend TX responses.

State and persistence behavior: Per-queue state includes credit windows, pending/free rings, grant handles, map/copy/unmap operation arrays, SKB queues, deallocation ring cursors, multicast RCU lists, hash configuration, and counters. State is volatile and is recreated on queue setup; module parameters affect future queue behavior.

Dependencies and integration points: Integrates with Xen grant tables, Xen rings and event notifications, NAPI, `ubuf_info` zerocopy callbacks, Linux SKB/GSO/checksum helpers, multicast RCU lists, and `xenvif_*` lifecycle from `interface.c` and Xenbus.

Risks: Guest-controlled ring contents are hostile input. Slot count overflow, page-boundary violations, impossible producer indexes, malformed extra-info chains, bad GSO fields, grant-map failures, or excessive slots can disable the VIF. Error paths must consume the right requests and return responses without leaking grant refs. Zerocopy callback ordering and memory barriers protect deallocation ring consistency.

Test signals: Use frontend fuzzing for malformed rings/extras, oversized packets, slot overflows, cross-page requests, grant failures, checksum/GSO variants, multicast add/delete, hash control commands, credit rate limits, deallocation under zerocopy stress, and module load/unload in Xen and non-Xen domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/netback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/rx.c

Purpose: Implements the backend-to-frontend receive path: packets queued by the backend netdev are copied into guest-provided RX grant slots, decorated with Xen extra-info records for GSO/XDP/hash, and completed through the frontend RX ring.

Important APIs, types, and functions: `xenvif_rx_queue_tail()` enqueues host SKBs and manages internal byte limits; `xenvif_kthread_guest_rx()` is the per-queue RX worker; `xenvif_rx_action()` drains queued SKBs while frontend slots are available; `xenvif_rx_skb()` writes data and extra slots for one packet; `xenvif_rx_copy_add()` and `xenvif_rx_copy_flush()` batch grant copies; `xenvif_have_rx_work()` drives IRQ/kthread wake logic and stall detection.

Control flow: `xenvif_start_xmit()` queues an SKB with an expiry deadline, then wakes the RX kthread. The worker waits for either sufficient RX ring slots, stall/ready transitions, stop requests, or disabled VIF state. For each packet, it computes required slots, dequeues the SKB, builds extra-info records for supported GSO, XDP headroom, and software hash, copies packet chunks into guest grants without crossing guest or source pages, writes RX responses, pushes notifications, and frees completed SKBs.

State and persistence behavior: Queue state includes the internal SKB queue, `rx_queue_len`, byte limit, `rx_slots_needed`, `last_rx_time`, `stalled`, batched grant-copy arrays, and completed SKB list. VIF-wide stall counters gate netdev carrier. All state is volatile and tied to live rings and kthreads.

Dependencies and integration points: Relies on Xen RX ring macros, grant-table copy operations, netdev queue stop/wake, SKB frag traversal, GSO/hash metadata, XDP headroom negotiated by Xenbus, and event-channel late EOI handling shared with `interface.c`.

Risks: Incorrect slot accounting can overrun frontend rings or sleep forever waiting for unavailable slots. Queued SKBs may hold foreign pages, so expiry/drop handling prevents grant starvation. Stall detection affects carrier state across all queues. Copy batching must update response status if individual grant copies fail.

Test signals: Cover packets spanning pages/frags/frag_lists, GSO extra-info, XDP headroom extra-info, hash extra-info, small and full RX rings, queue byte-limit backpressure, packet expiry, guest RX stall and recovery, grant-copy failures, split/shared IRQ EOI behavior, and kthread stop while disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/xenbus.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/xenbus.c

Purpose: Provides the Xenbus control plane for netback. It advertises backend features, creates VIF devices, watches frontend state and configuration, connects rings/event channels, manages hotplug-status deferral, and tears down queues on disconnect.

Important APIs, types, and functions: `netback_probe()` publishes feature keys and creates `backend_info`; `frontend_changed()` maps frontend Xenbus states into backend transitions; `connect()` reads negotiated features, allocates queues, registers watchers, and connects control/data rings; `connect_data_rings()` reads ring refs and event channels; `read_xenbus_vif_flags()` imports frontend offload capabilities; `set_backend_state()` enforces the allowed backend state graph. Debugfs helpers expose ring state and a manual kick.

Control flow: Probe writes backend feature keys in XenStore, switches to `InitWait`, reads hotplug script configuration, and creates the VIF. When the frontend reaches `Connected`, `connect()` validates queue count, reads MAC/rate/features, maps optional control ring, allocates per-queue state, connects each data ring, sets real queue counts, turns carrier on, registers the hotplug-status watch, and wakes TX queues. Closing states call `backend_disconnect()` and move through `Closing` to `Closed`.

State and persistence behavior: XenStore holds negotiated feature and ring keys, rate limits, hotplug status, and frontend/backend states. Runtime state lives in `backend_info`, `xenvif`, watchers, debugfs dentries, hotplug script string, and queue allocations. Reconnect destroys and recreates volatile queue/ring state.

Dependencies and integration points: Integrates Xenbus transactions/watches, XenStore, Linux hotplug uevents, debugfs, RTNL queue count updates, and the data/control connection helpers in `interface.c` and `netback.c`.

Risks: XenStore is frontend-controlled in several places, so queue count, ring refs, event channels, MAC strings, and feature flags need strict validation. Partial failures must unwind already-created queues and the control ring. Hotplug-status deferral can leave state changes pending. Watch callbacks may race disconnect without proper unregistering.

Test signals: Probe/remove with hotplug scripts, frontend state machine transitions, malformed MAC/rate/queue values, single versus multi-queue paths, split versus shared event channels, optional control ring absent/present, feature negotiation combinations, watcher updates for rate and multicast control, debugfs kick/read, and backend restart/reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/xenbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netfront.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netfront.c

Purpose: Implements the Xen virtual Ethernet frontend driver used by guest domains. It creates the guest netdev, negotiates features with netback, allocates grant-backed TX/RX rings and event channels, handles TX/RX NAPI and interrupts, supports multi-queue and XDP, and manages suspend/resume or backend reconnect.

Important APIs, types, and functions: `netfront_probe()` and `xennet_create_dev()` allocate the netdev and frontend private state; `talk_to_netback()` creates queues, rings, event channels, and XenStore keys; `xennet_start_xmit()` grants guest pages to the backend for TX; `xennet_tx_buf_gc()` collects TX responses and releases grants; `xennet_poll()` consumes RX responses, rebuilds SKBs, and runs XDP; `xennet_xdp_set()` negotiates backend headroom; `xennet_disconnect_backend()` unwinds rings, IRQs, grants, buffers, and page pools.

Control flow: Probe waits for backend readiness. On backend `InitWait`, `xennet_connect()` negotiates RX-copy, queue count, split event channels, offloads, trusted/bounce mode, XDP headroom, and registers the netdev if needed. TX maps SKB linear/frags into Xen grant refs, writes request and optional GSO extras, marks request IDs pending, and notifies netback. RX allocates page-pool backed SKBs as grant targets, parses backend responses and extras, ends grants, optionally runs XDP, assembles SKBs/frags, validates checksum/GSO state, and feeds GRO.

State and persistence behavior: Runtime state includes per-queue rings, grant refs, SKB arrays, free/pending TX ids, event channels, NAPI, refill timers, page pools, XDP programs, response counters, and per-CPU stats. XenStore persists negotiated connection keys and state; runtime ring and grant state is rebuilt on resume/reconnect.

Dependencies and integration points: Uses Linux netdev, NAPI, ethtool/sysfs, page_pool, XDP/BPF, GRO, grant tables, Xenbus, Xen event channels with late EOI, and Xen netif protocol structures.

Risks: A malicious or buggy backend can return invalid IDs, producer indexes, offsets, sizes, too many slots, or still-in-use grants; the driver marks the device broken in several such cases. Trusted-backend configuration controls whether TX data is bounced to zeroed pages to avoid data leakage. XDP requires headroom coordination through Xenbus reconfiguration and is currently limited to single-page RX frames.

Test signals: Multi-queue and single-queue negotiation, split/shared event channels, trusted versus bounced TX, SKB linear/frags/compound pages, GSO/checksum offloads, RX extras, malformed backend responses, grant still-in-use failures, XDP PASS/DROP/TX/REDIRECT, suspend/resume, backend restart, sysfs rxbuf compatibility attributes, ethtool stats, and module init on non-Xen systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netfront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/Kconfig

Purpose: Defines the top-level Kconfig menu for NFC device drivers below `drivers/nfc`, gated by the core `NFC` subsystem. It exposes selectable transport/controller drivers and sources subordinate Kconfig files for driver families.

Important APIs, types, and functions: Kconfig symbols include `NFC_TRF7970A`, `NFC_MEI_PHY`, `NFC_SIM`, `NFC_PORT100`, and `NFC_VIRTUAL_NCI`, plus `source` statements for FDP, PN544, PN533, Microread, Marvell, ST, NXP, Samsung, and ST95HF subtrees.

Control flow: There is no runtime control flow. Build-time selection flows from `menu "Near Field Communication (NFC) devices"` through dependencies such as `SPI`, `USB`, `NFC_DIGITAL`, `NFC_HCI`, `NFC_NCI`, `INTEL_MEI`, and `GPIOLIB`.

State and persistence behavior: The file persists user build choices in kernel configuration. It does not create runtime state.

Dependencies and integration points: Integrates NFC driver families with the kernel Kconfig system and controls which Makefile objects can be built. `NFC_MEI_PHY` is a shared transport used by MEI-backed HCI drivers such as Microread.

Risks: Incorrect dependencies can allow build failures or hide valid drivers. Top-level source ordering matters for menus but not runtime. A transport helper like `NFC_MEI_PHY` must remain selectable only with compatible core APIs.

Test signals: Run `make menuconfig`/`olddefconfig` dependency checks, build each symbol as module and built-in where supported, and verify sub-Kconfig source paths remain valid after tree moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/Makefile

Purpose: Maps top-level NFC Kconfig symbols to subdirectories and object files built under `drivers/nfc`.

Important APIs, types, and functions: `obj-$(CONFIG_NFC_FDP) += fdp/`, `obj-$(CONFIG_NFC_MICROREAD) += microread/`, `obj-$(CONFIG_NFC_MEI_PHY) += mei_phy.o`, and similar lines select controller families and standalone drivers such as `nfcsim.o`, `port100.o`, `trf7970a.o`, `virtual_ncidev.o`, and vendor subdirectories.

Control flow: There is no runtime flow. Kbuild evaluates the `obj-*` variables from the kernel configuration and descends into selected subdirectories.

State and persistence behavior: Build products are determined by `.config`; no runtime state is affected.

Dependencies and integration points: Integrates with the top-level NFC Kconfig and subordinate Makefiles. Shared helpers such as `mei_phy.o` are built when `CONFIG_NFC_MEI_PHY` is selected by MEI-based HCI drivers.

Risks: Missing or mismatched object names break module builds. Selecting a subdirectory via a core symbol must align with the subdirectory's own Makefile or transport modules can be omitted.

Test signals: Build all affected NFC configs as modules, verify expected `.ko` names, and run `make drivers/nfc/` after Kconfig symbol changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/fdp/Kconfig

Purpose: Defines build-time options for the Intel Fields Peak NFC controller core and its I2C transport.

Important APIs, types, and functions: `NFC_FDP` is the core NCI driver and depends on `NFC_NCI`, selecting `CRC_CCITT`. `NFC_FDP_I2C` depends on `NFC_FDP && I2C` and builds the I2C physical layer module.

Control flow: Build-time only. Selecting the I2C transport also requires the core driver, and the help text documents module names `fdp` and `fdp_i2c`.

State and persistence behavior: Configuration state persists in `.config`; no runtime state exists here.

Dependencies and integration points: Connects the FDP core in `fdp.c` and I2C transport in `i2c.c` to the NFC NCI subsystem and Kbuild.

Risks: If transport dependencies drift from source includes, builds can fail. `CRC_CCITT` is selected although the visible FDP I2C LRC path does not directly use it, so this dependency should be checked against core firmware/protocol needs before changes.

Test signals: Build `CONFIG_NFC_FDP=m`, `CONFIG_NFC_FDP_I2C=m`, built-in variants, and dependency-disabled configs without `I2C` or `NFC_NCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/fdp/Makefile

Purpose: Provides Kbuild object mapping for the Intel FDP NFC driver family.

Important APIs, types, and functions: `obj-$(CONFIG_NFC_FDP) += fdp.o` builds the core NCI driver, `obj-$(CONFIG_NFC_FDP_I2C) += fdp_i2c.o` builds the transport wrapper, and `fdp_i2c-objs = i2c.o` sets the module object composition.

Control flow: Build-time only; Kbuild turns selected symbols into modules or built-in objects.

State and persistence behavior: No runtime state. The module/object names are the persistent ABI visible to packaging and modprobe users.

Dependencies and integration points: Matches `fdp.c`, `i2c.c`, and the symbols from `fdp/Kconfig`.

Risks: Module name changes would affect userspace autoloading and documentation. Object composition must remain aligned with exported symbols from `fdp.c` consumed by `i2c.c`.

Test signals: Build `fdp.o` alone and with `fdp_i2c.o`, check generated module names, and run modpost for unresolved `fdp_nci_probe`/`fdp_nci_remove` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.c

Purpose: Implements the Intel Fields Peak NFC core NCI driver. It registers an `nci_dev`, controls open/send/setup/post-setup operations, applies OTP/RAM firmware patches through proprietary NCI commands and data connections, parses version/config responses, and exports probe/remove for physical transports.

Important APIs, types, and functions: `struct fdp_nci_info` holds transport, firmware, version, clock, wait-queue, and patch state. `fdp_nci_probe()` allocates/registers the NCI device; `fdp_nci_setup()` initializes NCI, loads firmware, compares versions, applies OTP/RAM patches, verifies versions, and resets; `fdp_nci_post_setup()` sends vendor production data and clock settings; `fdp_nci_send_patch()` segments firmware manually; `fdp_core_ops` and `fdp_prop_ops` register response/notification handlers.

Control flow: Transport probe calls `fdp_nci_probe()`. On NCI setup, the driver initializes the core, requests firmware files, creates a proprietary patch connection when needed, sends patch chunks as data packets, waits until all packets are physically sent, closes the data connection, sends end-of-transfer, waits for patch and reset notifications, then reinitializes and verifies firmware versions. Normal sends decrement the data packet counter before writing through `phy_ops`.

State and persistence behavior: Firmware blobs are transient `request_firmware()` references. Version numbers, key index, setup flags, patch status, data packet counter, wait queue, clock configuration, and transport pointer live in `fdp_nci_info`. Actual firmware persistence is in the NFC controller, not the driver.

Dependencies and integration points: Uses Linux firmware loading, NFC NCI core/proprietary command APIs, wait queues, atomics, and transport `nfc_phy_ops` supplied by `fdp/i2c.c`.

Risks: Firmware header offsets are assumed valid; short firmware files could read beyond data. Waits are interruptible but return values are not always checked, so interrupted setup could continue with stale flags. Data-packet callback ordering is critical because end-of-transfer must follow the last physical I2C write. Proprietary response parsers trust minimum payload lengths.

Test signals: Probe/register/remove, missing RAM or OTP firmware, older/equal/newer firmware versions, patch notification and reset notification ordering, interrupted waits, short/corrupt firmware files, clock/VSC property variants, NCI command failures, and data send/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.h

Purpose: Declares the private interface between the FDP core NCI driver and its I2C physical transport.

Important APIs, types, and functions: `struct fdp_i2c_phy` stores the `i2c_client`, power GPIO, registered `nci_dev`, hard-fault state, and next expected read size. The header declares `fdp_nci_probe()` and `fdp_nci_remove()`.

Control flow: The I2C driver allocates/fills `fdp_i2c_phy`, then calls `fdp_nci_probe()` with transport callbacks, framing head/tail room, clock values, and optional vendor config. The core returns an `nci_dev` pointer that later feeds IRQ receive handling and remove.

State and persistence behavior: The struct records volatile transport state. `hard_fault` suppresses future writes after transport failure, and `next_read_size` tracks the two-step FDP I2C framing protocol.

Dependencies and integration points: Includes NFC NCI core declarations and GPIO consumer APIs. It couples `i2c.c` and `fdp.c` but is not a public kernel subsystem header.

Risks: The struct name is I2C-specific, so adding new transports would require refactoring or a more generic PHY type. `uint16_t` is used instead of kernel `u16`, but only in private state.

Test signals: Compile the core and I2C modules together, verify exported symbols resolve, and exercise probe/remove paths that set and consume `phy->ndev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/fdp/i2c.c

Purpose: Implements the I2C physical layer for Intel Fields Peak NFC. It frames NCI packets with FDP length/LRC bytes, handles reset/power GPIO, reads ACPI/device properties, services IRQ-driven reads, and delegates NCI core registration to `fdp.c`.

Important APIs, types, and functions: `fdp_nci_i2c_probe()` allocates `fdp_i2c_phy`, requests threaded IRQ, maps ACPI GPIOs, reads clock/VSC properties, and calls `fdp_nci_probe()`. `fdp_nci_i2c_write()` adds/removes length+LRC framing and retries standby writes. `fdp_nci_i2c_read()` performs two-stage reads using `next_read_size`; `fdp_nci_i2c_irq_thread_fn()` passes SKBs to `nci_recv_frame()`.

Control flow: Enable/disable both pulse the power GPIO via reset. Writes prepend a 16-bit little-endian length and append XOR LRC, send via `i2c_master_send()`, retry once for `-EREMOTEIO`, and restore the original SKB. Reads first receive either a length packet or data packet, validate XOR LRC, update `next_read_size`, allocate an SKB for data packets, strip framing, and flush on desynchronization.

State and persistence behavior: Runtime state is `hard_fault`, `next_read_size`, power GPIO value, and the core `nci_dev` pointer. Clock and vendor-specific configuration are read at probe and passed to core setup; they are not persisted by the transport.

Dependencies and integration points: Uses I2C core, threaded IRQs, ACPI GPIO mappings, device properties (`clock-type`, `clock-freq`, `fw-vsc-cfg`), GPIO consumer API, NFC NCI receive path, and FDP core exported functions.

Risks: LRC/desync handling uses a broad flush read that may drop valid data. Short writes set `hard_fault` to a positive short count before returning `-EREMOTEIO`, which causes future writes to return that positive value. Property parsing of `fw-vsc-cfg` expects an embedded length and can reject or ignore malformed data. IRQ must be present.

Test signals: Probe with ACPI `INT339A`, missing IRQ/GPIO, I2C adapter lacking `I2C_FUNC_I2C`, normal read/write framing, standby retry, LRC failure resync, short writes, device property defaults and VSC arrays, remove/reset, and NCI receive delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/fdp/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.c

Purpose: Provides a reusable NFC HCI physical layer over Intel MEI client devices. It wraps HCI payloads in MEI NFC headers, performs maintenance version/connect handshakes, waits for send acknowledgements, dispatches inbound HCI frames, and exports `mei_phy_ops` plus allocation/free helpers.

Important APIs, types, and functions: Internal packed structs define MEI NFC headers, maintenance commands, replies, interface version, and connect response. `nfc_mei_phy_enable()` enables the MEI client, reads interface version, connects, and registers RX callback; `nfc_mei_phy_write()` sends an HCI SKB through `mei_nfc_send()`; `nfc_mei_rx_cb()` receives MEI frames and calls `nfc_hci_recv_frame()`; `nfc_mei_phy_alloc()` and `nfc_mei_phy_free()` manage `struct nfc_mei_phy`.

Control flow: A MEI-backed driver allocates the PHY and passes `mei_phy_ops` to an HCI core driver. Enable sends maintenance IF_VERSION and CONNECT commands synchronously through `mei_cldev_send/recv`, then registers a receive callback. Outbound HCI frames are prefixed with `MEI_NFC_CMD_HCI_SEND`, current request id, and payload length; the sender waits up to one second for an acknowledgement frame with matching request id. Inbound non-ack frames become HCI SKBs after the header is stripped.

State and persistence behavior: `nfc_mei_phy` tracks MEI client pointer, HCI device, send wait queue, firmware/vendor/radio identifiers, request and received ids, powered flag, and hard fault. State is volatile and reset by disable/free.

Dependencies and integration points: Uses the MEI client bus, NFC HCI core, wait queues, SKBs, and UUID published in `mei_phy.h`. `microread/mei.c` is a direct consumer.

Risks: Header length and packed layout must match ME firmware. Send acknowledgement is serialized only by request ids and wait queue state; concurrent writes could race. `hard_fault` is checked on RX but not broadly set in this file. Receive size validation is minimal beyond header-size checks.

Test signals: MEI probe/remove, enable handshake failures at send/recv/version/connect stages, send timeout, request id wrap, inbound HCI frame delivery, ack-only frame handling, disable while send waits, and module unload with registered callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.h

Purpose: Defines the private/public header for NFC-over-MEI physical-layer helpers used by MEI-backed NFC HCI drivers.

Important APIs, types, and functions: Provides `MEI_NFC_UUID`, `MEI_NFC_HEADER_SIZE`, `MEI_NFC_MAX_HCI_PAYLOAD`, `struct nfc_mei_phy`, exported `mei_phy_ops`, and prototypes for `nfc_mei_phy_alloc()` and `nfc_mei_phy_free()`.

Control flow: No executable flow. Consumers allocate a PHY for a `mei_cl_device`, pass `mei_phy_ops` into an HCI chipset driver, then free the PHY on MEI remove.

State and persistence behavior: The struct defines runtime-only fields for MEI client ownership, HCI device association, wait queue, firmware/vendor/radio metadata, request counters, powered state, and hard-fault status.

Dependencies and integration points: Includes MEI client bus, NFC HCI, and UUID definitions. It links the shared `mei_phy.c` transport with drivers such as `microread/mei.c`.

Risks: Constants are part of the transport contract; changing header size or payload limit without firmware support breaks framing. Exposed struct fields make consumers capable of direct mutation, so additions should preserve existing initialization assumptions.

Test signals: Compile MEI-backed NFC drivers, verify UUID autoload matching, and exercise allocation/free with MEI client data storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/Kconfig

Purpose: Defines Kconfig options for the Inside Secure Microread HCI NFC core and its I2C and MEI transports.

Important APIs, types, and functions: `NFC_MICROREAD` is a hidden tristate core selecting `CRC_CCITT`. `NFC_MICROREAD_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC` and selects the core. `NFC_MICROREAD_MEI` depends on `NFC_HCI && NFC_MEI_PHY` and also selects the core.

Control flow: Build-time only; choosing a transport selects the shared Microread HCI logic.

State and persistence behavior: Only kernel configuration state persists. Runtime state lives in the built modules.

Dependencies and integration points: Connects transport-specific code to NFC HCI, SHDLC LLC for I2C, and the shared MEI PHY helper for MEI transport.

Risks: Transport dependencies must match the LLC names passed at runtime (`LLC_SHDLC_NAME` for I2C, `LLC_NOP_NAME` for MEI). Missing `CRC_CCITT` would break Type 1 tag transceive CRC generation in core code.

Test signals: Build I2C and MEI transports independently and together, as modules and built-in, and verify selecting transports pulls in `microread.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/Makefile

Purpose: Maps Microread Kconfig symbols to core and transport module objects.

Important APIs, types, and functions: `microread_i2c-objs = i2c.o`, `microread_mei-objs = mei.o`, and `obj-$(CONFIG_NFC_MICROREAD) += microread.o` plus transport `obj-*` lines define module composition.

Control flow: Build-time only. Kbuild emits the core and optional transport modules according to `.config`.

State and persistence behavior: No runtime state; module names are persistent build/user-visible outputs.

Dependencies and integration points: Aligns with `microread.c`, `i2c.c`, `mei.c`, and symbols in `microread/Kconfig`.

Risks: Object/module naming must match documentation and autoloading expectations. Transports depend on exported `microread_probe()`/`microread_remove()` from the core.

Test signals: Build core with each transport, run modpost for exported symbol resolution, and inspect generated `microread_i2c.ko` and `microread_mei.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/i2c.c

Purpose: Implements the I2C transport for Inside Secure Microread HCI NFC chips using SHDLC framing. It adds/removes length and XOR CRC bytes, handles threaded IRQ reads, tracks hard I2C faults, and registers the shared Microread HCI core.

Important APIs, types, and functions: `struct microread_i2c_phy` stores the I2C client, HCI device, and `hard_fault`. `microread_i2c_write()` frames and sends SKBs with standby retry; `microread_i2c_read()` reads length plus payload, validates size and CRC, and strips framing; `microread_i2c_irq_thread_fn()` forwards frames to `nfc_hci_recv_frame()`; `microread_i2c_probe()` registers IRQ and calls `microread_probe()`.

Control flow: Probe allocates PHY state, binds client data, requests a rising-edge threaded IRQ, then registers the HCI core with `LLC_SHDLC_NAME` and I2C framing sizes. Writes delay for chip timing, push length, append XOR CRC, send over I2C, retry `-EREMOTEIO`, restore the SKB, and return 0 or error. IRQ reads validate the length byte, receive the rest, check CRC, strip length/tail, and pass the frame upward. Hard I2C failure stores `-EREMOTEIO` and reports a NULL frame to HCI.

State and persistence behavior: Runtime state is the `hard_fault` latch and HCI device pointer. There is no persistent configuration or firmware state.

Dependencies and integration points: Uses I2C, threaded IRQs, NFC HCI, NFC LLC SHDLC, SKB helpers, and the exported Microread core API.

Risks: Length/CRC errors trigger flush reads that may desynchronize if device timing differs. `hard_fault` permanently blocks future writes until reprobe. Probe does not explicitly validate `client->irq > 0`, relying on `request_threaded_irq` failure. Fixed payload limit of 29 bytes must match the chip/LLC contract.

Test signals: I2C probe/remove, missing/invalid IRQ, normal read/write frames, CRC and length faults, standby retry, hard-fault propagation, SHDLC LLC registration, and remove while IRQ activity is possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/mei.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/mei.c

Purpose: Binds the Microread HCI NFC core to Intel MEI NFC devices through the shared MEI PHY helper.

Important APIs, types, and functions: `microread_mei_probe()` allocates `nfc_mei_phy` and calls `microread_probe()` with `mei_phy_ops`, `LLC_NOP_NAME`, MEI header headroom, and MEI payload limit. `microread_mei_remove()` unregisters the HCI device and frees the PHY. `microread_mei_tbl` matches `MEI_NFC_UUID` under the `microread` MEI client name.

Control flow: The MEI client bus calls probe on UUID match. Probe creates the PHY, registers the Microread HCI device with no LLC framing, and leaves runtime enable/disable to HCI open/close. Remove reverses registration and disables/frees the MEI PHY.

State and persistence behavior: No local persistent state; MEI client driver data points at `nfc_mei_phy`, which stores runtime transport state.

Dependencies and integration points: Depends on the MEI client bus, `mei_phy.h`, NFC HCI/LLC, and exported Microread core functions.

Risks: Probe must free the PHY if Microread core registration fails. The headroom/payload values must align with `mei_phy.c` framing. Autoload depends on the UUID/name table.

Test signals: MEI device match/autoload, probe failure cleanup, HCI open/close over MEI, remove after active device, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/mei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.c

Purpose: Implements the Inside Secure Microread chipset HCI logic independent of physical transport. It defines proprietary gates/pipes/events, registers an NFC HCI device, configures polling subscriptions, translates target discovery and DEP events, handles initiator/target data exchange, and exports probe/remove for I2C and MEI transports.

Important APIs, types, and functions: `struct microread_info` stores transport callbacks and pending async transceive callback. `microread_hci_ops` wires open/close, `hci_ready`, `start_poll`, DEP link up/down, target mapping, initiator transceive, target send, and event receive callbacks. `microread_probe()` allocates/registers the HCI device with gate table and supported protocols; `microread_event_received()` dispatches chipset events; `microread_target_discovered()` converts card-found payloads into `struct nfc_target`.

Control flow: Open enables the PHY. HCI ready subscribes reader gates to card discovery. Polling stops old discovery, sets P2P target mode, configures general bytes for NFC-DEP initiator/target, then starts selected discovery. Initiator transceive either sends P2P exchange events or proprietary reader exchange commands with control bits and optional Type 1 CRC. Async completion strips RF status and invokes the NFC callback. Event receive handles card discovery, P2P activation/deactivation, and target-mode data exchange.

State and persistence behavior: Runtime state includes transport ID/ops, HCI device, async callback type/function/context, HCI gate/pipe table, session id, and HCI core state. No persistent storage is used.

Dependencies and integration points: Uses NFC HCI core, NFC target/DEP APIs, LLC names supplied by transports, CRC-CCITT for Jewel/Type 1 commands, SKBs, and transport `nfc_phy_ops`.

Risks: Many event payload parsers assume minimum lengths before indexing fixed offsets. Async callback state is single outstanding operation state and would not support concurrent transceives. Gate-specific control bits and UID offsets are chipset protocol details; mistakes cause silent RF failures. General bytes allocation can disable NFC-DEP polling if unavailable.

Test signals: HCI registration/removal, I2C and MEI transports, polling protocol masks, ISO A/B/Felica/Jewel target discovery payloads, malformed short payloads, Type 1 CRC transceive, NFC-DEP link up/down and target mode exchange, async error propagation, and event fallthrough to standard HCI handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.h

Purpose: Declares the shared interface for Microread physical transports to register and unregister the common HCI chipset driver.

Important APIs, types, and functions: Defines `DRIVER_DESC`, declares `microread_probe()` with PHY id, `nfc_phy_ops`, LLC name, headroom/tailroom/payload constraints, and output HCI device pointer, plus `microread_remove()`.

Control flow: Transport drivers call `microread_probe()` during their bus probe and `microread_remove()` during remove.

State and persistence behavior: The header itself has no state. Its parameters determine runtime HCI allocation characteristics such as PHY framing room and max payload.

Dependencies and integration points: Includes NFC HCI core declarations and is consumed by `i2c.c`, `mei.c`, and implemented by `microread.c`.

Risks: The API assumes one HCI device per transport PHY and exposes no update path for runtime payload/headroom changes. Incorrect headroom/tailroom arguments can corrupt transport framing.

Test signals: Compile both transports against the header and verify probe/remove signatures stay synchronized with the core implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Kconfig

Purpose: Defines Kconfig options for the Marvell 8897 NFC NCI core and USB, UART, I2C, and SPI transports.

Important APIs, types, and functions: `NFC_MRVL` is the hidden core symbol. `NFC_MRVL_USB` depends on `NFC_NCI && USB`; `NFC_MRVL_UART` depends on `NFC_NCI && NFC_NCI_UART`; `NFC_MRVL_I2C` depends on `NFC_MRVL && I2C`; `NFC_MRVL_SPI` depends on `NFC_MRVL && NFC_NCI_SPI`. Transport selections pull in the core where needed.

Control flow: Build-time only. Users select a bus transport; Kconfig includes or selects the common Marvell core.

State and persistence behavior: Only kernel configuration state persists. Runtime state belongs to the Marvell source files outside this work item.

Dependencies and integration points: Connects Marvell NFC support to NFC NCI core and bus-specific helper subsystems.

Risks: Dependency asymmetry matters: USB/UART select the core directly, while I2C/SPI depend on the core. This can affect menu visibility and build selection. Descriptions should remain aligned with actual device IDs and transport support.

Test signals: Kconfig resolution for each transport, all-modules build, dependency-disabled builds without USB/UART/I2C/SPI helpers, and expected module selection of `nfcmrvl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Makefile

Purpose: Defines Kbuild object composition for Marvell NFC NCI core and transport modules.

Important APIs, types, and functions: `nfcmrvl-y += main.o fw_dnld.o` builds the common core; transport modules map `usb.o`, `uart.o`, `i2c.o`, and `spi.o` into `nfcmrvl_usb`, `nfcmrvl_uart`, `nfcmrvl_i2c`, and `nfcmrvl_spi`.

Control flow: Build-time only. Kbuild emits the selected core and bus modules from Kconfig symbols.

State and persistence behavior: No runtime state in this file; module names and object composition are build outputs visible to userspace.

Dependencies and integration points: Aligns `nfcmrvl/Kconfig` with source files in the same directory. The core object combines main driver logic with firmware download support.

Risks: Module composition must keep common firmware download code linked into the core and avoid unresolved symbols for transport modules. Renaming transport modules affects autoload and packaging.

Test signals: Build each transport as a module, run modpost for unresolved symbols, verify module names, and build with only the core selected where Kconfig permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Makefile -->
