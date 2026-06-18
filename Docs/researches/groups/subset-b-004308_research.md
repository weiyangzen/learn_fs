# Research Report: subset-b-004308

This grouped report covers the requested CAN driver and SocketCAN support files. Each section preserves its source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.c

Purpose: core SocketCAN network driver for Bosch CC770 and Intel AN82527 CAN controllers. It exports `alloc_cc770dev()`, `free_cc770dev()`, `register_cc770dev()`, and `unregister_cc770dev()` for bus-specific wrappers.

Important APIs and functions: `cc770_set_bittiming()` programs BTR0/BTR1 from `can_bittiming`; `cc770_start_xmit()` validates SKBs, stops the queue, and fills the TX message object through `cc770_tx()`; `cc770_rx()`, `cc770_err()`, and the RX/RTR/TX interrupt helpers translate hardware message objects and status bits into CAN SKBs, echo SKBs, statistics, and CAN error frames. `cc770_interrupt()` demultiplexes status interrupt id `1` and message-object interrupts, bounded by `CC770_MAX_IRQ`.

Control flow and state: registration probes register read/write behavior, initializes the chipset, sets reset mode, and registers the candev. Open transitions reset to normal, requests IRQ, and starts the netdev queue; close reverses that path. Persistent runtime state is in `struct cc770_priv`: CAN state, register callbacks, message-object flags, `control_normal_mode`, and a single pending `tx_skb`. Integration points include `linux/can/dev.h`, echo-SKB helpers, netdevice ops, ethtool timestamp info, and lower-layer register callbacks. Risks are hardware-specific message-object semantics, RTR identifier loss, queue lock assumptions delegated to lower layers, and TX retry behavior when an RTR response overwrites the TX object. Test signals include probe pattern failures, unexpected interrupt ids, bus-off/error counters, echo skb accounting, and RX overrun stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.h

Purpose: private hardware contract for the CC770/AN82527 core and its bus wrappers. It defines the memory layout, bit masks, object mapping, and private data shared by `cc770.c`, `cc770_isa.c`, and `cc770_platform.c`.

Important types and APIs: `struct cc770_msgobj` models one packed message object, `struct cc770_regs` overlays message objects with controller registers, and `struct cc770_priv` embeds `struct can_priv` as its first field for SocketCAN compatibility. The file declares register access macros `cc770_read_reg()` and `cc770_write_reg()`, object flags such as `CC770_OBJ_FLAG_RX`, `CC770_OBJ_FLAG_RTR`, and `CC770_OBJ_FLAG_EFF`, and exported allocation/registration helpers.

Control flow and state: no executable flow lives here, but every core state transition depends on these offsets and masks. The `obj2msgobj()` macro maps logical driver objects to hardware objects 11..15, and the private structure persists the selected CPU interface, clock-out, bus configuration, IRQ flags, register base, and TX skb pointer. Dependencies are Linux CAN device definitions and `offsetof()`-based MMIO/PIO access. Risks are ABI-like: bad packing, offsets, or flag definitions would corrupt hardware programming. Test signals come indirectly through register probe patterns, message-object interrupt behavior, and successful bus-wrapper registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_isa.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_isa.c

Purpose: legacy ISA/PC-104 bus wrapper for the shared CC770 core. It creates platform devices from module parameters and supplies memory, direct I/O-port, or indirect I/O-port register access.

Important APIs and functions: module parameters `port`, `mem`, `irq`, `clk`, `cir`, `cor`, `bcr`, and `indirect` describe up to `MAXDEV` devices. `cc770_isa_probe()` reserves I/O or memory regions, maps memory, allocates a CC770 netdev, selects read/write callbacks, computes clock divisor bits, sets platform data in `struct cc770_priv`, and calls `register_cc770dev()`. `cc770_isa_remove()` unregisters and releases resources. Indirect port access is serialized by `cc770_isa_port_lock`.

Control flow and state: module init walks parameter arrays, creates platform devices only for complete address/IRQ tuples, then registers a platform driver. Remove and exit unwind registered platform devices. Persistent state is the module-parameter arrays plus `cc770_isa_devs[]`; per-device state is stored in the netdev private structure. Dependencies include ISA I/O APIs, platform devices, shared CC770 helpers, and SocketCAN. Risks include misconfigured module parameters, shared IRQ behavior, correct fallback from per-device to index-0 defaults, and cleanup symmetry for direct versus indirect I/O sizes. Test signals include probe logs, insufficient-parameter errors, region conflicts, registration failures, and successful multi-device module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_platform.c

Purpose: platform-bus wrapper for CC770/AN82527 controllers using either device tree properties or legacy platform data.

Important APIs and functions: `cc770_platform_probe()` obtains the memory resource and IRQ, reserves and maps registers, allocates the CC770 netdev, installs `ioread8`/`iowrite8` callbacks, fills timing and bus configuration, and registers the device through `register_cc770dev()`. `cc770_get_of_node_data()` parses Bosch-specific properties for oscillator frequency, clock division, comparator bypass, pin disconnects, polarity, clock output, and slew rate. `cc770_get_platform_data()` mirrors the legacy `cc770_platform_data` path.

Control flow and state: probe validates resources before allocation, stores the netdev as platform driver data, and on failures releases in reverse order. Remove unregisters, unmaps, frees the CAN device, and releases the memory region. Runtime behavior after registration is delegated to `cc770.c`; this file persists only mapped base and config bits in `struct cc770_priv`. Dependencies include OF, platform resources, MMIO, `include/linux/can/platform/cc770.h`, and the shared core. Risks are device-tree property interpretation, clock-output divisor validation, shared IRQ assumptions, and manual non-devm resource cleanup. Test signals include OF match for `bosch,cc770`/`intc,82527`, debug output of clock/config values, and probe unwind coverage for missing resources or failed core registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/cc770_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Kconfig

Purpose: Kconfig entries for the CTU CAN FD open-source IP core and its PCI and platform bindings.

Important symbols: `CAN_CTUCANFD` builds the common base driver and is visible mainly for `COMPILE_TEST`. `CAN_CTUCANFD_PCI` depends on `PCI` and selects the common core. `CAN_CTUCANFD_PLATFORM` depends on `HAS_IOMEM && OF` and also selects the common core.

Control flow and state: this file has no runtime control flow; it controls which objects are compiled by the Makefile and enforces that bus-specific drivers pull in `ctucanfd_base.o`. Integration points are the kernel Kconfig dependency graph, PCI, OF platform probing, and SocketCAN. Risks are build coverage gaps if the base symbol is not selected, and hardware support being split across bus-specific symbols. Test signals are configuration matrix builds: common-only compile testing, PCI module builds with `CONFIG_PCI`, and platform builds with OF and I/O memory enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Makefile

Purpose: object composition for CTU CAN FD drivers.

Important build targets: `obj-$(CONFIG_CAN_CTUCANFD) := ctucanfd.o` creates the common module from `ctucanfd_base.o`. `obj-$(CONFIG_CAN_CTUCANFD_PCI) += ctucanfd_pci.o` and `obj-$(CONFIG_CAN_CTUCANFD_PLATFORM) += ctucanfd_platform.o` add bus wrappers when configured.

Control flow and state: no runtime behavior exists, but the build graph enforces the architecture seen in the sources: common CAN logic in `ctucanfd_base.c`, separate PCI enumeration in `ctucanfd_pci.c`, and separate OF platform binding in `ctucanfd_platform.c`. Dependencies are the Kconfig symbols and kernel module build system. Risks are link/export mismatches for `ctucan_probe_common()`, `ctucan_suspend()`, and `ctucan_resume()` if object membership changes. Test signals include successful modular and built-in builds for each symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd.h

Purpose: shared private interface for the CTU CAN FD common driver and bus wrappers.

Important types and APIs: `struct ctucan_priv` embeds `struct can_priv`, stores the mapped register base, endian-aware register callbacks, TX buffer head/tail and priority state, NAPI context, runtime PM device/clock handles, IRQ flags, buffered first RX frame word, and PCI peer list linkage. The file declares `ctucan_probe_common()`, `ctucan_suspend()`, and `ctucan_resume()`.

Control flow and state: executable flow is implemented elsewhere, but all persistent driver state is shaped here. `ctucan_probe_common()` is designed as the bus-independent registration entry: bus drivers pass device, MMIO address, IRQ, TX buffer count, clock rate or clock lookup mode, runtime PM policy, and a driver-data callback. Dependencies include netdevice, SocketCAN, clocks, list management, and the generated register enum. Risks are concurrency and lifecycle coupling around `tx_lock`, NAPI, PM state, and `peers_on_pdev` for multi-core PCI cards. Test signals are successful common probe from both PCI and platform paths and clean suspend/resume transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_base.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_base.c

Purpose: bus-independent SocketCAN driver for the CTU CAN FD IP core. It owns register access, bit timing, mode control, TX buffer management, RX/NAPI, interrupts, error reporting, PM hooks, and candev registration.

Important APIs and functions: `ctucan_probe_common()` allocates the CAN netdev, sets capabilities, detects register endianness, enables runtime PM, resets hardware, adds NAPI, and registers the candev. `ctucan_chip_start()` initializes TX priorities, programs nominal/data bit timing and secondary sample point, maps SocketCAN ctrlmodes to hardware mode bits, and enables interrupts and the core. `ctucan_start_xmit()` inserts CAN/CAN FD frames into the next hardware TX buffer and stores echo SKBs by buffer index. `ctucan_rx_poll()` drains RX FIFO through `ctucan_rx()`, and `ctucan_interrupt()` masks/schedules RX, handles TX completion, and processes error interrupts.

Control flow and state: open performs runtime PM get, reset, `open_candev()`, IRQ request, chip start, NAPI enable, and queue start; close disables queue/NAPI, stops chip, frees IRQ, closes candev, and runtime-PM puts. Persistent state includes TX head/tail/priorities, CAN state, RX first-word buffering when SKB allocation fails, endian callbacks, and NAPI queues. Dependencies include generated CTU register/frame headers, `FIELD_GET/PREP`, SocketCAN netlink-driven timing callbacks, runtime PM, clocks, and echo SKBs. Risks are interrupt storm handling, TX buffer priority rotation, unaligned payload word access, RX FIFO first-word buffering under memory pressure, and PM/error unwinds. Test signals include CTU signature detection, endian fallback, TX echo/stat correctness, RX overflow error frames, bus-off recovery, and NAPI re-enable of level-triggered RBNEI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kframe.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kframe.h

Purpose: autogenerated frame-format register definitions for CTU CAN FD TX/RX frame words.

Important definitions: `enum ctu_can_fd_can_frame_format` defines frame-format, identifier, timestamp, and data-word offsets. Masks such as `REG_FRAME_FORMAT_W_DLC`, `RTR`, `IDE`, `FDF`, `BRS`, `ESI_RSV`, and `RWCNT` are used by `ctucanfd_base.c` to encode TX frames and decode RX frames. Identifier masks split extended and base identifiers, and data masks document byte positions inside 32-bit payload words.

Control flow and state: no runtime code; it is a source of truth for register offsets and bitfields consumed by `FIELD_GET()` and `FIELD_PREP()`. Dependencies are only `linux/bits.h`, but semantic integration is tight with the hardware IP core and generated register map. Risks are stale autogenerated definitions versus FPGA RTL, especially around word count, FD flags, and payload offsets. Test signals include correct TX frame layout, accurate RX DLC/ID/flag decoding, and interoperability with CAN FD frames using BRS/ESI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kregs.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kregs.h

Purpose: autogenerated CTU CAN FD memory-map and register bitfield header.

Important definitions: `enum ctu_can_fd_can_registers` defines control/status, interrupt, bit timing, error, filter, RX, TX, timestamp, and TX buffer data offsets. Bit masks cover mode control (`REG_MODE_*`), status (`REG_STATUS_*`), command bits, interrupt bits, nominal/data bit timing, error counters, RX/TX FIFO state, TX command/status, error capture, secondary sample point, and timestamp registers.

Control flow and state: no executable code, but all CTU base-driver hardware I/O depends on these constants. The generated map drives reset, core enable, interrupt mask/clear, TX buffer commands, NAPI RX reads, error-state detection, endian probing, and bit timing programming. Dependencies are `linux/bits.h` and hardware RTL compatibility. Risks include offset drift, invalid mask widths, and assumptions that all registers are 32-bit accessible despite byte-level conceptual fields. Test signals are broad: CTU signature reads, bit timing writes accepted by hardware, interrupt handling, TX/RX register sequencing, and error-counter/reporting correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_kregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_pci.c

Purpose: PCI/PCIe wrapper for CTU CAN FD FPGA implementations, including multi-core cards.

Important APIs and functions: `ctucan_pci_probe()` enables the PCI device, requests regions, optionally enables MSI, maps BAR1 for CAN core memory and BAR0 for control registers, detects core count from CTU ID when available, allocates board data, calls `ctucan_probe_common()` for each core, and enables the Avalon-MM to PCIe interrupt bit. `ctucan_pci_remove()` disables card interrupts, walks `peers_on_pdev`, unregisters each candev, removes NAPI, frees netdevs, unmaps BARs, disables MSI, and releases PCI resources. `ctucan_pci_set_drvdata()` links each netdev private structure into board state and selects shared IRQ flags.

Control flow and state: probe treats the first common-core registration as required and later cores as best effort. Persistent board state stores BAR pointers, per-device netdev list, and MSI status. Dependencies include PCI, CTU common exports, shared IRQ/MSI handling, and runtime PM ops. Risks include pointer arithmetic on `void __iomem *`, cleanup asymmetry around `cra_addr` versus `bar0_base`, shared IRQ behavior across multiple cores, and partial multi-core initialization. Test signals include PCI ID match, BAR logging, CTU ID core count, common probe success per core, interrupt enable register writes, and remove-time list drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_platform.c

Purpose: OF platform wrapper for CTU CAN FD IP cores in FPGA/SoC systems.

Important APIs and functions: `ctucan_platform_probe()` devm-maps the first memory resource, obtains the IRQ, assumes four TX buffers, and delegates to `ctucan_probe_common()` with runtime PM enablement and a callback that stores the netdev in platform driver data. `ctucan_platform_remove()` unregisters the candev, disables runtime PM, deletes NAPI, and frees the CAN netdev. PM operations reuse `ctucan_suspend()` and `ctucan_resume()`.

Control flow and state: probe is short and relies on devm resource ownership for MMIO mapping. All runtime controller behavior is delegated to the base driver. Persistent state is the platform drvdata netdev and `struct ctucan_priv` initialized by the common probe. Dependencies include OF matching for `ctu,ctucanfd-2` and `ctu,ctucanfd`, platform IRQ/resource helpers, runtime PM, and SocketCAN common registration. Risks include hard-coded TX buffer count pending future DT property support, remove assuming drvdata is non-NULL, and clock acquisition being deferred to common probe when `can_clk_rate` is zero. Test signals include OF probe, clock lookup in common code, PM enable/disable symmetry, and successful NAPI cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/Makefile

Purpose: builds the shared SocketCAN device support library.

Important build targets: `can-dev.o` always includes `skb.o` under `CONFIG_CAN_DEV`. Optional pieces are added by feature symbols: `calc_bittiming.o` for `CONFIG_CAN_CALC_BITTIMING`, `bittiming.o`, `dev.o`, `length.o`, and `netlink.o` for `CONFIG_CAN_NETLINK`, and `rx-offload.o` for `CONFIG_CAN_RX_OFFLOAD`.

Control flow and state: no runtime logic, but the object membership defines which helper APIs are available to CAN controller drivers and rtnetlink. Integration points include Kconfig feature selection and exported symbols used across CAN drivers. Risks are unresolved symbols when drivers rely on helpers gated behind optional config, and behavior changes when CAN netlink or RX offload are not configured. Test signals include allmodconfig builds, minimal CAN_DEV builds with only skb helpers, and link coverage for drivers using RX offload or netlink timing support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/bittiming.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/bittiming.c

Purpose: validation and fixup for SocketCAN bit timing supplied through netlink or driver constants.

Important APIs and functions: `can_sjw_set_default()` derives a default SJW from phase segment values; `can_sjw_check()` validates SJW against controller limits and phase segments; `can_get_bittiming()` selects calculation from bitrate, direct timing fixup from time quantum, or validation against fixed bitrate tables. `can_validate_pwm_bittiming()` validates CAN XL PWM symbol timing against nominal and XL data bit times.

Control flow and state: direct timing flow checks segment ranges, sets SJW, computes BRP from clock frequency and TQ, validates BRP, and derives realized bitrate/sample point/TQ. No persistent state is stored except modifications to the passed `struct can_bittiming` or PWM validation result. Dependencies include `struct can_priv`, `can_calc_bittiming()`, netlink extack messages, and CAN XL timing helpers. Risks include rounding behavior in BRP calculation, mutation of user-provided timing fields by drivers, and consistency across FD/XL timing paths. Test signals include extack strings for invalid SJW, segment, BRP, fixed bitrate, and PWM constraints; iproute2 `ip link set canX type can ...` exercises the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/bittiming.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/calc_bittiming.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/calc_bittiming.c

Purpose: calculates CAN nominal, FD data, and XL data timing parameters from requested bitrate/sample-point constraints.

Important APIs and functions: `can_calc_bittiming()` searches valid TSEG/BRP combinations, chooses the lowest bitrate and sample-point error under `CAN_CALC_MAX_ERROR`, sets prop/phase segments, TQ, SJW, BRP, sample point, and actual bitrate. `can_calc_tdco()` derives automatic transmitter delay compensation offset when data BRP is 1 or 2. `can_calc_pwm()` derives CAN XL PWM short/long symbol settings that divide the XL data bit time.

Control flow and state: the main loop iterates doubled TSEG values to account for rounding, clamps sample-point splits with `can_update_sample_point()`, and emits extack diagnostics for bitrate error. The function mutates the caller-provided timing structures and may set TDC control-mode flags. Dependencies include controller timing constants, `struct can_priv` clock, CAN XL/PWM helpers, and `can_sjw_check()`. Risks are edge-case arithmetic around high bitrates, sample-point preference changes, TDC enablement assumptions, and integer division rounding. Test signals include requested versus realized bitrate/sample point, extack error percentages above 5%, TDC auto activation, and PWM divisibility validation for CAN XL TMS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/calc_bittiming.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/dev.c

Purpose: central SocketCAN netdevice support: CAN netdev setup/allocation, registration, common open/close, bus-off restart, state accounting, ctrlmode/capability helpers, transceiver termination, and timestamp operations.

Important APIs and functions: `alloc_candev_mqs()` builds the private memory layout with driver private data, CAN mid-layer private data, and echo skb slots. `register_candev()` validates bit timing/termination metadata, loads optional GPIO termination, sets rtnl link ops, drops carrier, and registers the netdev. `open_candev()` validates configured timing and CAN FD data timing. `can_bus_off()`, `can_restart_now()`, and delayed restart work coordinate bus-off recovery. `can_change_state()` updates state, stats, and optional error frame content.

Control flow and state: CAN state and statistics persist in `struct can_priv`; restart delay persists as delayed work; echo SKBs are flushed on close. Device MTU/capability state is recalculated when ctrlmode changes. Dependencies include rtnetlink `can_link_ops`, GPIO descriptors, OF transceiver child nodes, workqueues, echo SKB helpers, and ethtool/hwtstamp APIs. Risks are strict metadata consistency in `register_candev()`, restart races around carrier state, termination GPIO defaults, and correct MTU transitions for FD/XL/static modes. Test signals include netdev registration, bus-off restart logs, xstats counters, GPIO termination configuration, and `safe_candev_priv()` rejecting non-CAN devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/length.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/length.c

Purpose: CAN FD DLC/length conversion helpers and rough on-wire frame length estimation for BQL/statistics.

Important APIs and functions: `can_fd_dlc2len()` maps the 4-bit CAN FD DLC field to canonical payload length. `can_fd_len2dlc()` maps sanitized payload lengths back to DLC, capping oversized inputs. `can_skb_get_frame_len()` estimates frame length in bytes for CAN or CAN FD SKBs, excluding RTR payload and using `can_frame_bytes()`.

Control flow and state: no persistent state exists; static lookup tables drive conversions. The BQL helper inspects skb protocol shape through `can_is_canfd_skb()`, EFF flag, RTR flag, and payload length. Dependencies include CAN frame layout helpers and exported symbols used by CAN drivers and echo SKB accounting. Risks are table correctness for non-linear CAN FD lengths and the deliberate approximation that ignores bit stuffing and separate CAN FD BRS bitrate. Test signals include boundary conversions for lengths 0, 8, 9, 12, 64, invalid lengths above 64, RTR frames, and FD/EFF frame byte estimates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/length.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/netlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/netlink.c

Purpose: rtnetlink implementation for configuring and reporting CAN netdevices through `ip link type can`.

Important APIs and functions: `can_validate()` and helpers reject invalid combinations before changes: sample point range, FD/XL data timing dependencies, TDC auto/manual exclusivity, PWM requiring XL TMS, listen-only versus restricted mode, and XL/TMS conflicts. `can_changelink()` applies ctrlmode, nominal timing, restart delay/manual restart, FD/XL data timing, PWM, and termination. `can_fill_info()` and size helpers export timing constants, clock, state, ctrlmode, restart, error counters, termination, bitrate limits, TDC, XL, and PWM attributes.

Control flow and state: `changelink` runs under RTNL and forbids timing/mode/restart-delay changes while the netdev is up. It mutates `struct can_priv`, invokes driver timing callbacks, clears stale FD/XL/TDC/PWM state when top-level modes are disabled, recalculates MTU/capabilities, and uses extack diagnostics for user-visible failures. Dependencies include `can_get_bittiming()`, `can_calc_tdco()`, `can_calc_pwm()`, `can_validate_pwm_bittiming()`, `can_restart_now()`, and `can_link_ops`. Risks include complex dependency masks, stale configuration when modes are toggled, size/fill mismatches for nested attributes, and drivers with incomplete callback/constant combinations. Test signals are iproute2 netlink validation errors, dump output completeness, manual bus-off restart behavior, and FD/XL/TDC/PWM configuration matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/rx-offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/rx-offload.c

Purpose: generic RX offload helper for CAN drivers that collect frames in IRQ context and deliver them through NAPI, optionally preserving timestamp order.

Important APIs and functions: `can_rx_offload_irq_offload_timestamp()` reads pending mailboxes, attaches timestamps, and inserts SKBs sorted by timestamp. `can_rx_offload_irq_offload_fifo()` drains FIFO-style hardware. `can_rx_offload_queue_timestamp()` and `can_rx_offload_queue_tail()` allow manual queueing. Echo helpers queue TX echo SKBs into RX offload ordering. `can_rx_offload_irq_finish()` and threaded variant splice IRQ queues to the NAPI queue and schedule polling. Add/enable/delete functions initialize NAPI and queues.

Control flow and state: interrupt code fills `skb_irq_queue`; finish splices it into the locked `skb_queue`; NAPI poll updates RX stats and calls `netif_receive_skb()`, rescheduling if more packets arrived. Persistent state lives in `struct can_rx_offload`: mailbox range/order, queue length cap, NAPI, and driver `mailbox_read` callback. Dependencies include SKB queues, NAPI, CAN echo helpers, and timestamp storage in `skb->cb`. Risks are queue overflow policy, timestamp sorting across u32 wrap, mailbox direction setup, and correct bottom-half handling for threaded IRQ scheduling. Test signals include ordered delivery under timestamp wrap, overflow/drop counters, NAPI quota behavior, and echo SKB offload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/rx-offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/skb.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dev/skb.c

Purpose: common SocketCAN SKB allocation, validation, local echo, echo completion/freeing, and error-frame allocation.

Important APIs and functions: `alloc_can_skb()`, `alloc_canfd_skb()`, `alloc_canxl_skb()`, and `alloc_can_err_skb()` allocate protocol-specific frames, attach CAN skb extensions, initialize checksum/pkt type, and populate default frame flags. `can_put_echo_skb()` clones and stores an outgoing skb for later local echo. `__can_get_echo_skb()`, `can_get_echo_skb()`, and `can_free_echo_skb()` complete or discard echo slots and handle timestamps/stat lengths. `can_dropped_invalid_skb()` validates outgoing CAN/CAN FD/CAN XL SKBs and initializes AF_PACKET-originated SKBs.

Control flow and state: echo state persists in the `can_priv::echo_skb[]` array created by `alloc_candev*()`. Drivers call put during TX submission and get/free during TX completion or failure. Dependencies include `can_skb_ext`, netdevice stats, `IFF_ECHO`, PF_CAN fallback behavior, and frame length helpers. Risks are echo slot out-of-bounds or already-occupied bugs, dropped SKBs when devices lack local echo, extension allocation failure, and correct initialization for raw packet injection. Test signals include echo loopback delivery, hardware timestamp completion, tx_dropped/tx_aborted counters on flush, invalid skb drops, and CAN XL length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dev/skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dummy_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/dummy_can.c

Purpose: dummy CAN network driver primarily used to exercise the CAN netlink interface without hardware.

Important APIs and functions: module init allocates one CAN device with one echo slot, registers generous nominal, FD, and XL timing constants, FD/XL TDC constants, PWM constants, supported ctrlmodes, 160 MHz clock, and 20 Mbps bitrate limit. `dummy_can_netdev_open()` prints current timing/control settings, calls `open_candev()`, and starts the queue. `dummy_can_start_xmit()` validates SKBs, stores them in echo slot 0, immediately completes local echo, and updates TX stats.

Control flow and state: the module keeps a single global `dummy_can` pointer. Runtime state is almost entirely `struct can_priv` configured through netlink; no hardware state exists. Close stops queue and calls `close_candev()`. Dependencies include shared CAN dev, bit timing, TDC/PWM, skb echo helpers, ethtool timestamp info, and string choice helpers. Risks are single-instance limitation, no real bus-off/error behavior, immediate echo not modeling hardware latency, and use mainly as a configuration smoke test. Test signals are successful `ip link` FD/XL/TDC/PWM mode changes, debug timing output on open, immediate echo of transmitted frames, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/dummy_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/esd/Kconfig

Purpose: Kconfig entry for the esd electronics CAN-PCI(e)/402 family driver.

Important symbol: `CAN_ESD_402_PCI` builds support for C402 card family devices based on the ESDACC CAN controller. It depends on `PCI && HAS_DMA`, matching the PCIe and coherent DMA requirements in the implementation.

Control flow and state: no runtime code; it enables the `esd_402_pci` module and documents supported form factors. Integration points are PCI enumeration, DMA API availability, and the Makefile that links `esdacc.o` with `esd_402_pci-core.o`. Risks are limited configurability: the driver is only available where PCI and DMA are present. Test signals are Kconfig visibility under PCI/HAS_DMA, module build as `esd_402_pci`, and dependency-driven exclusion on non-PCI or no-DMA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/esd/Makefile

Purpose: object composition for the esd electronics 402 PCI driver.

Important build targets: `esd_402_pci-objs := esdacc.o esd_402_pci-core.o` links shared ESDACC core behavior with PCI card glue. `obj-$(CONFIG_CAN_ESD_402_PCI) += esd_402_pci.o` emits the module or built-in object when configured.

Control flow and state: no runtime flow; the Makefile encodes the split between card resource management and CAN controller logic. Dependencies are the Kconfig symbol and exported-internal functions declared in `esdacc.h`. Risks are link breakage if either object is omitted because PCI code calls `acc_*` functions and core code relies on structures initialized by PCI code. Test signals include module build, modpost symbol resolution, and load-time module metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esd_402_pci-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/esd/esd_402_pci-core.c

Purpose: PCIe card driver for esd CAN-PCI(e)/402 family devices with ESDACC FPGA cores. It handles card discovery, FPGA initialization, DMA/MSI setup, per-core netdev allocation, and teardown.

Important APIs and functions: `pci402_probe()` enables the PCI device, maps BAR0, initializes the card, DMA, interrupts, and CAN cores. `pci402_init_card()` resets the FPGA, reads overview metadata, validates version, timestamp frequency, and active core count, and configures endian conversion. `pci402_init_dma()` allocates a 64 KiB coherent DMA buffer, initializes bus-master FIFO pointers, programs DMA address registers, and enables bus mastering. `pci402_init_cores()` allocates one candev per active core, configures timing constants/capabilities, and registers via `register_candev()`.

Control flow and state: probe has layered unwind labels for PCI regions, BAR mapping, DMA, interrupts, and cores. Remove reverses interrupt, core, DMA, BAR, region, and PCI enablement. Persistent card state is `struct pci402_card`: mapped I/O, DMA buffer/handle, overview, core array, and MSI flag. Dependencies include PCI config/MSI, DMA coherent memory, ESDACC helpers, SocketCAN, hardware timestamp ops, and big-endian register access. Risks include fixed 80 MHz timestamp support, unsupported CAN-FD warning despite FD-like timing constants, DMA alignment assumptions, MSI setup from FPGA endpoint registers, and active-core limits. Test signals include PCI ID match, FPGA version/frequency validation, DMA/MSI enable logs, per-core `registered` logs, and cleanup paths after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esd_402_pci-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.c

Purpose: shared CAN behavior for ESDACC cores: open/close, TX FIFO submission, bit timing, bus-master message processing, timestamp conversion, error handling, and card interrupt demultiplex.

Important APIs and functions: `acc_open()` configures interrupts and listen-only mode, leaves reset, syncs TX FIFO indices, and starts the queue. `acc_start_xmit()` validates SKBs, checks TX FIFO space, encodes CAN ID/DLC/RTR/one-shot flags, stores echo SKB by FIFO index, advances the software head, and writes TX data. `acc_set_bittiming()` programs classic or CAN-FD-style BRP/BTR registers. `acc_card_interrupt()` compares DMA-written IRQ counters, masks pending sources, processes per-core bus-master messages, acknowledges counters, and unmasks all.

Control flow and state: hardware communicates events through coherent DMA FIFOs described by `acc_bmfifo`. Message handlers distinguish RX/TX done, TX abort, overrun, bus error, and error-state changes. TX completion attaches hardware timestamps to echo SKBs; RX/error frames also receive converted timestamps. Bus-off aborts pending TX and uses `can_bus_off()`, while restart waits for an error-active message before waking the queue. Persistent state includes overview/core metadata, FIFO head/tail, DMA message tails, and CAN state. Dependencies include `esdacc.h`, SocketCAN echo/error helpers, timestamp/hwtstamp APIs, and big-endian MMIO. Risks include DMA counter synchronization, FIFO wrap, TX abort mask handling, timestamp fixed-frequency assumptions, and ignored unsupported message types. Test signals include timestamped echo/RX frames, overrun and bus-error CAN error frames, TX FIFO wake/stop behavior, bus-off recovery, and IRQ_NONE versus IRQ_HANDLED decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.h

Purpose: private ESDACC hardware/register/data contract shared by PCI card glue and core CAN behavior.

Important types and definitions: register offsets cover overview and CAN core modules, mode bits, CAN control interrupts, bit timing masks, DMA message sizes, and bus-master message IDs. `union acc_bmmsg` and its variants model fixed 32-byte DMA messages for RX/TX done, TX abort, overrun, bus errors, error-state changes, timeslice, hardware timer, and hotplug. `struct acc_bmfifo`, `struct acc_core`, `struct acc_ov`, and `struct acc_net_priv` hold DMA FIFO pointers/counters, per-core netdev/FIFO state, card overview metadata, and SocketCAN private data.

Control flow and state: inline helpers read/write big-endian registers, set/clear bits, detect reset mode, read overview registers, and reset the FPGA. Function declarations expose the core operations implemented in `esdacc.c`. Persistent runtime state defined here includes DMA FIFO tails, IRQ counters, TX FIFO indices, active core counts, feature flags, and frequencies. Dependencies include CAN dev structures, netdevice, units, and MMIO accessors. Risks are structure size/alignment for DMA messages, endian assumptions, register mask correctness, and DMA memory layout consistency with FPGA bus-mastering. Test signals include static assertion on message size, overview metadata reads, correct core FIFO pointer initialization, reset completion, and interrupt message decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/esd/esdacc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/flexcan/Makefile

Purpose: build definition for the FlexCAN driver objects.

Important build targets: `obj-$(CONFIG_CAN_FLEXCAN) += flexcan.o` creates the FlexCAN module or built-in object. The composite object includes `flexcan-core.o` and `flexcan-ethtool.o`.

Control flow and state: no runtime code is present; the file declares the split between core controller behavior and ethtool support. Dependencies are the `CONFIG_CAN_FLEXCAN` Kconfig symbol and the kernel build system. Risks are minimal but include link failures if either object’s internal symbols drift, and missing ethtool support if object composition changes. Test signals are successful builds for built-in and module configurations and presence of FlexCAN ethtool operations after linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/Makefile -->
