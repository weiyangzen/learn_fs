# subset-b-004311 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_can.c

Purpose: this is the classical CAN SocketCAN netdev driver for Renesas R-Car CAN controllers. It exposes one `struct net_device` backed by a memory-mapped controller, uses the Linux CAN core for bit timing, error frames, echo skb handling, bus-off recovery, and registers as a platform driver for Renesas `renesas,*-can` compatibles.

Important types and APIs: `struct rcar_can_regs` models the device register layout, including 64 mailbox slots and FIFO/control/error registers. `struct rcar_can_priv` embeds `struct can_priv` first, then stores the netdev, NAPI object, MMIO register base, CAN clock, FIFO echo indices, selected clock source, and cached interrupt-enable byte. The main netdev entry points are `rcar_can_open()`, `rcar_can_close()`, and `rcar_can_start_xmit()`. CAN core callbacks are `rcar_can_do_set_mode()` and `rcar_can_get_berr_counter()`. Probe/remove integrate with `alloc_candev()`, `register_candev()`, `netif_napi_add_weight()`, runtime PM, device tree clock selection, and `platform_driver`.

Control flow: probe maps registers, validates `renesas,can-clock-select`, gets the selected clock (`clkp1`, `clkp2`, or `can_clk`), fills CAN timing constraints, and registers the CAN netdev. Open resumes runtime PM, enables the CAN clock, opens the CAN core device, enables NAPI, requests the IRQ, calls `rcar_can_start()`, and starts the queue. `rcar_can_start()` leaves sleep, forces reset, programs bit timing, selects mixed-ID FIFO mailbox mode, accepts all IDs, enables FIFO and error interrupts, enters operation mode, and enables RX/TX FIFOs. TX encodes SFF/EFF/RTR into mailbox 56, writes data/DLC, stores the echo skb in a four-entry FIFO ring, advances the hardware FIFO pointer, and stops the queue when the ring is full. IRQ handling services error and TX completion directly and disables RX FIFO interrupts before scheduling NAPI. RX polling drains mailbox 60 until the RX FIFO is empty, builds CAN skbs, advances the RX FIFO pointer, then re-enables RX interrupts.

State and persistence: persistent runtime state is in `rcar_can_priv`: CAN state, NAPI, `tx_head`/`tx_tail`, cached `ier`, and `clock_select`. Hardware state is programmed on every start/resume and reset/slept on stop/suspend. There is no disk persistence. Error counters are read from `tecr`/`recr`; TX echo slots are cleaned during bus-off. Suspend detaches the netdev, halts and sleeps the controller, and releases runtime PM; resume reinitializes the controller and restarts the queue.

Dependencies and integration points: the driver depends on SocketCAN (`linux/can/dev.h`), netdev, ethtool timestamp info, platform resources, clocks, device tree, interrupts, MMIO helpers, and runtime PM. It assumes the R-Car register access endian behavior described by the `rcar_can_set_bittiming()` comment and uses 8-bit accesses for byte registers.

Risks: reset/operation-mode transitions poll a bounded number of reads but do not return an error if the bit never changes. FIFO accounting relies on hardware `TFUST` matching software echo indices. Error clearing writes inverted masks to factor registers and is register-semantics-sensitive. RX allocation failure drops frames without advancing stats beyond `rx_dropped`. Tests should cover open/close error unwinds, bus-off cleanup, error-frame mapping, mixed SFF/EFF/RTR RX/TX, queue stop/wake at FIFO depth, NAPI re-enable, runtime PM get/put balance, and suspend/resume with an active interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_canfd.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_canfd.c

Purpose: this is the Renesas R-Car/RZ CAN FD platform driver. It supports classical-only, CAN FD, and FD-only operating modes across several hardware generations, exposes one SocketCAN netdev per enabled device-tree child channel, and manages global controller resources shared by channels.

Important types and APIs: `struct rcar_canfd_hw_info` captures per-SoC register offsets, bitfield shifts, timing constants, channel counts, IRQ topology, clock postdividers, and feature flags. `struct rcar_canfd_global` owns shared MMIO base, CAN FD channel register base, clocks, resets, mode flags, channel mask, and channel pointers. `struct rcar_canfd_channel` embeds `struct can_priv`, the netdev, channel number, NAPI, optional PHY transceiver, TX ring indices, and a TX spinlock. Netdev methods are `rcar_canfd_open()`, `rcar_canfd_close()`, and `rcar_canfd_start_xmit()`. CAN callbacks include `rcar_canfd_do_set_mode()`, `rcar_canfd_get_berr_counter()`, and CAN FD TDC `do_get_auto_tdcv`.

Control flow: probe selects hardware data from OF match, interprets `renesas,no-can-fd` and `renesas,fd-only`, discovers available `channelN` children and optional PHYs, acquires resets/clocks/resources, requests either shared or split global IRQs, initializes the global controller, then registers each enabled channel. Global init resets both reset lines, enables peripheral/RAM clocks, waits for RAM init, puts global and channel blocks into reset, selects classical/FD interface mode, programs global config, per-channel RX FIFO, TX common FIFO, one accept-all AFL rule per channel, enables global interrupts, and enters global operation mode. Channel open powers PHY, enables the CAN clock, opens the CAN core device, enables NAPI, programs bit timing/TDC, enables channel interrupts, enters communication mode, enables common/RX FIFOs, and starts the queue.

TX/RX flow: TX writes ID, DLC, FD status, BRS/ESI flags, and payload into either FD or classical FIFO address spaces based on control mode and hardware register sharing. It stores echo skbs in an eight-entry FIFO and advances the common FIFO pointer. TX completion compares software `tx_head`/`tx_tail` with hardware unsent count, completes echo skbs, updates stats, wakes the queue when space exists, and clears the FIFO interrupt. RX global FIFO IRQ schedules per-channel NAPI after disabling that channel's RX FIFO interrupt. NAPI drains the channel's Rx FIFO, allocates CAN or CAN FD skbs depending on hardware FDF status and requested mode, decodes IDs/RTR/BRS/ESI, copies payload, advances the FIFO pointer, updates stats, and re-enables RX interrupts when complete.

State and persistence: persistent driver state is in global and per-channel structures: mode flags, channel mask, clocks/resets, NAPI state, TX ring cursors, CAN state, and TDC configuration. Hardware is reset and reconfigured on probe/resume and reset/slept on remove/suspend. No storage persists across driver reload. Suspend closes running netdevs and deinitializes global state; resume reinitializes globals and reopens running channels.

Dependencies and integration points: integrates with SocketCAN, CAN FD and TDC core APIs, device tree child nodes, PHY framework, reset framework, clocks, platform IRQ naming, NAPI, ethtool timestamp reporting, and `readl_poll_timeout()`. OF compatibles map to Gen3, Gen4, RZ/G2L, and RZ/V2H style hardware capability tables.

Risks: one shared global error register is cleared wholesale after per-channel handling; correctness depends on hardware channel bit behavior. Shared vs multi-channel IRQ modes have different paths that need SoC-specific testing. Mode selection (`fdmode`, `fd_only_mode`, shared registers) changes register address families, so regressions can be generation-specific. RX allocation failure leaves the FIFO pointer advancement to the code path after allocation only when allocation succeeds, so sustained allocation failure can stall hardware consumption. Tests should cover all OF compatible families, classical-only vs FD vs FD-only, TDC auto/manual, shared and per-channel IRQ layouts, multi-channel simultaneous RX/TX, bus-off recovery, global message-lost/ECC flags, suspend/resume, and error unwind from clock/reset/IRQ/channel registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/rcar_canfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Kconfig

Purpose: this Kconfig fragment declares the Rockchip CAN FD controller option, `CONFIG_CAN_ROCKCHIP_CANFD`. It makes the driver available as built-in or module code and places it under the CAN driver configuration hierarchy.

Important symbols and dependencies: `CAN_ROCKCHIP_CANFD` is a tristate labeled "Rockchip CAN-FD controller". It depends on device tree support (`OF`) and either `ARCH_ROCKCHIP` or `COMPILE_TEST`. It selects `CAN_RX_OFFLOAD`, matching the implementation's use of `struct can_rx_offload`, timestamp-ordered RX queuing, and echo skb timestamp handling.

Control flow and integration: the file has no runtime control flow. At build-configuration time, selecting the symbol allows `Makefile` to compile the multi-object `rockchip_canfd.o` module from core, ethtool, RX, timestamp, and TX source files. The help text identifies Rockchip SoC CAN FD controllers as the hardware target.

State and persistence: Kconfig state persists only in the kernel configuration. It indirectly controls whether OF matching for `rockchip,rk3568v2-canfd` and `rockchip,rk3568v3-canfd` can register a runtime platform driver.

Risks and test signals: because the implementation currently disables CAN FD mode when `RKCANFD_QUIRK_CANFD_BROKEN` is present, the Kconfig help's CAN-FD wording can overstate usable functionality on affected RK3568 revisions. Configuration tests should verify `CAN_RX_OFFLOAD` is selected, compilation works under `COMPILE_TEST`, and module/built-in builds include all listed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Makefile

Purpose: this Makefile builds the Rockchip CAN FD driver as a composite object named `rockchip_canfd.o` when `CONFIG_CAN_ROCKCHIP_CANFD` is enabled.

Important build units: `rockchip_canfd-objs` includes `rockchip_canfd-core.o`, `rockchip_canfd-ethtool.o`, `rockchip_canfd-rx.o`, `rockchip_canfd-timestamp.o`, and `rockchip_canfd-tx.o`. The core file owns platform probe/remove, runtime PM, bit timing, interrupts, and netdev operations. The other files provide exported internal helpers declared in `rockchip_canfd.h`.

Control flow and integration: there is no runtime flow. The object list defines link-time integration, so cross-file functions such as `rkcanfd_handle_rx_int()`, `rkcanfd_start_xmit()`, `rkcanfd_timestamp_*()`, and `rkcanfd_ethtool_init()` resolve inside the single module.

State and persistence: only build state is affected. No generated files or runtime state are created by this Makefile.

Risks and test signals: missing any listed object would break link-time symbols or silently drop functionality such as hardware timestamps or ethtool stats. Build tests should compile the driver as a module and built-in, with `W=1` or equivalent to catch missing prototypes and unused symbol drift when implementation files change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-core.c

Purpose: this is the central Rockchip CAN FD platform driver. It owns device matching, resource setup, runtime PM, bit timing, controller start/stop, interrupt dispatch, CAN error handling, netdev registration, and integration with the RX/TX/timestamp/ethtool helper files.

Important APIs and types: the file uses `struct rkcanfd_priv` from the header as the netdev private object. It defines RK3568 v2/v3 `struct rkcanfd_devtype_data` quirk tables, nominal/data `struct can_bittiming_const`, netdev ops, PM ops, OF match table, and a platform driver. The CAN callbacks are `rkcanfd_set_mode()` and `rkcanfd_get_berr_counter()`. Internal hardware helpers include `rkcanfd_chip_set_reset_mode()`, `rkcanfd_chip_start()`, `rkcanfd_chip_stop[_sync]()`, interrupt mask helpers, FIFO setup, and corrected bus-error-counter handling.

Control flow: probe allocates a CAN netdev with two echo slots, gets the IRQ, all clocks, MMIO, reset array, fills CAN timing and ctrlmode capabilities, applies OF quirk data, adds manual CAN RX offload, then registers the CAN device. Registration enables runtime PM, resumes the device so clocks are on, initializes ethtool, registers the netdev, logs RTL revision and errata, then releases runtime PM. Open calls `open_candev()`, resumes runtime PM, starts the chip, enables CAN RX offload, requests the IRQ, unmasks interrupts, and starts the queue. Stop masks interrupts, frees the IRQ, disables offload, stops the chip synchronously, closes CAN core state, and drops runtime PM.

Interrupt flow: `rkcanfd_irq()` reads pending unmasked interrupt bits, acknowledges them before handling to avoid lost reoccurring IRQs, then dispatches RX, bus protocol error, state-error/bus-off, and RX FIFO overflow handlers. RX work is delegated to `rkcanfd_handle_rx_int()`. Error handling reads `RKCANFD_REG_ERROR_CODE`, optionally creates timestamped CAN error skbs when BERR reporting is enabled, maps protocol location/type bits, queues errors through CAN RX offload, and maintains stats. State handling uses corrected bus-error counters, calls `can_change_state()`, stops the chip and calls `can_bus_off()` on bus-off, and queues timestamped state-change skbs.

State and persistence: `rkcanfd_priv` stores runtime controller mode defaults, interrupt mask, corrected error counters, TX ring cursors, timecounter state, devtype quirks, and stats. The driver does not persist to disk. Runtime PM gates the bulk clocks. The reset line is asserted/deasserted during start and stop to force known hardware state.

Dependencies and integration points: depends on SocketCAN, CAN RX offload, netdev queue accounting, platform OF matching, reset controls, runtime PM, bulk clocks, and the Rockchip helper modules. It intentionally hides CAN FD support for quirked devices marked `RKCANFD_QUIRK_CANFD_BROKEN`, despite the CAN FD register programming being present.

Risks and test signals: error-counter correction is compensating for unreliable hardware reads and must match RX/TX decrement paths in other files. Interrupt ack-before-handle is deliberate and should not be reordered casually. Runtime PM assumes clock 0 is the CAN system clock. Tests should cover probe failure unwinds, runtime PM balance, IRQ storms, bus-off restart via `CAN_MODE_START`, BERR reporting on/off, RX overflow, loopback, quirked v2/v3 capability exposure, and netdev queue accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-ethtool.c

Purpose: this file wires Rockchip-specific ethtool support into the netdev, exposing hardware timestamp capability and two driver statistics tied to documented RK3568 errata workarounds.

Important APIs and types: `enum rkcanfd_stats_type` indexes `rx_fifo_empty_errors` and `tx_extended_as_standard_errors`. `rkcanfd_stats_strings` supplies the ethtool stat names. `rkcanfd_ethtool_ops` uses `can_ethtool_op_get_ts_info_hwts` plus custom `get_strings`, `get_sset_count`, and `get_ethtool_stats`. `rkcanfd_ethtool_init()` installs the ops and initializes `u64_stats_sync`.

Control flow: core registration calls `rkcanfd_ethtool_init()` before `register_candev()`. At ethtool query time, the driver copies stat names for `ETH_SS_STATS`, reports the stat count, and reads the two `u64_stats_t` counters under the sequence-counter retry loop required for lockless 64-bit stats.

State and persistence: stats live in `priv->stats` for the life of the netdev and are not persisted across unregister. The counters are incremented in RX/TX paths for erratum 5 empty-FIFO observations and erratum 6 extended-as-standard transmit failures.

Dependencies and integration points: depends on `linux/ethtool.h`, SocketCAN hardware timestamp ethtool helper, `u64_stats_sync`, and the shared `rkcanfd_priv` structure. It integrates with user-visible `ethtool -S` and timestamp capability reporting.

Risks and test signals: stat ordering must stay synchronized between the enum and string array. Any new stats need matching names, count, and fetch logic. Tests should verify `ethtool -S canX` exposes stable names, concurrent stat updates are read without torn values, and `ethtool -T` reports hardware timestamp support through the CAN helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-rx.c

Purpose: this file handles Rockchip CAN FD RX FIFO draining, CAN/CAN FD frame decoding, timestamp assignment, CAN RX offload queuing, and RX-side workarounds for RK3568 errata.

Important APIs and functions: `rkcanfd_handle_rx_int()` is called from the core IRQ handler and drains frames while the RX FIFO count is nonzero. `rkcanfd_handle_rx_int_one()` reads one FIFO header and payload, filters self-received TX frames, allocates the right skb type, timestamps it, and queues it through CAN RX offload. `rkcanfd_rxstx_filter()` uses self-reception to detect normal TX completion and erratum 6 extended-frame corruption. Helper functions compare frame headers/data and convert `struct rkcanfd_fifo_header` into `struct canfd_frame` metadata.

Control flow: for each received FIFO entry, the driver reads a separate 12-byte FIFO header followed by up to 64 bytes of data from `RKCANFD_REG_RX_FIFO_RDATA`. Erratum 5 is detected by the "empty header" signature where frameinfo, id, and timestamp are equal, in which case a counter is incremented and no skb is produced. Valid headers are decoded into CAN ID, EFF flag, RTR, FDF, BRS, and DLC/length. CAN FD frames are dropped when the interface is not in CAN FD mode. If TX is pending, self-received frames are compared with the echo skb at `tx_tail`: matching frames complete TX through `rkcanfd_handle_tx_done_one()`, and corrupted extended-as-standard frames update erratum stats and trigger `rkcanfd_xmit_retry()`.

State and persistence: RX state is transient except for `priv->bec.rxerr`, ethtool erratum counters, TX tail updates for self-reception completion, and netdev stats. Hardware timestamps are converted later by the timestamp helper. There is no durable persistence.

Dependencies and integration points: depends on `netdev_queues.h`, SocketCAN skb allocators, CAN RX offload timestamp queues, TX helper functions, timestamp helper, and the shared register definitions. It is tightly coupled to core's choice to enable `RKCANFD_REG_MODE_RXSTX_MODE`.

Risks and test signals: wrong FIFO count hardware is expected, so handling must avoid consuming bogus frames. Erratum 6 retry logic assumes the pending echo skb exists and represents the next transmitted frame. Loopback mode intentionally allows self-received frames to continue to RX delivery. Tests should cover classical and FD RX, RTR behavior, disabled-FD drops, FIFO empty false positives, self-reception TX completion, corrupted EFF-to-SFF retransmit, loopback delivery, RX allocation failure, and CAN RX offload queue errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-timestamp.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-timestamp.c

Purpose: this file converts the Rockchip controller's 32-bit hardware timestamp counter into skb hardware timestamps using Linux cyclecounter/timecounter infrastructure and a delayed wrap-prevention worker.

Important APIs and functions: `rkcanfd_timestamp_init()` programs the timestamp prescaler, configures `struct cyclecounter`, computes safe delayed-work cadence, and initializes the worker. `rkcanfd_timestamp_start()` initializes `struct timecounter` from real time and schedules work. `rkcanfd_timestamp_stop()` and `_stop_sync()` cancel the delayed worker. `rkcanfd_skb_set_timestamp()` converts a raw controller timestamp into `skb_shared_hwtstamps`.

Control flow: start-up chooses the larger of nominal and data bitrate, divides the CAN clock down to at least twice that bitrate subject to the register field maximum, enables the timestamp counter, computes mult/shift with `clocks_calc_mult_shift()`, and schedules periodic reads before the 32-bit counter can wrap unnoticed. RX, TX echo, and error paths pass raw timestamps to `rkcanfd_skb_set_timestamp()`, which uses `timecounter_cyc2time()` and writes `hwtstamp`.

State and persistence: timestamp state lives in `priv->cc`, `priv->tc`, `priv->timestamp`, and `priv->work_delay_jiffies`. It resets on chip start and stops on interface shutdown. It is not persisted. The timecounter base is real time at each start, so timestamps are meaningful for the running interface session.

Dependencies and integration points: depends on `linux/clocksource.h`, delayed work, the controller timestamp register, CAN bit timing already calculated by the CAN core, and ethtool timestamp reporting from `rockchip_canfd-ethtool.c`.

Risks and test signals: `rkcanfd_timestamp_init()` reads data bit timing even when CAN FD is disabled; callers must ensure fields are initialized enough for the max operation. Work delay calculation must remain conservative for high clock rates; missed delayed work can corrupt timestamp extension across wraps. Tests should verify hardware timestamps are monotonic across RX/TX/error skbs, wrap handling at high clock rates, stop vs stop_sync race behavior during close/remove, and ethtool timestamp reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-tx.c

Purpose: this file implements Rockchip CAN FD transmit submission, queue throttling, hardware command writes, TX retry for errata, and TX completion accounting.

Important APIs and functions: `rkcanfd_start_xmit()` is the netdev transmit method used by core. `rkcanfd_get_effective_tx_free()` reports queue space while honoring erratum 6 constraints. `rkcanfd_xmit_retry()` resends the current TX FIFO slot. `rkcanfd_handle_tx_done_one()` is called by RX self-reception filtering to complete one transmitted frame with the hardware timestamp.

Control flow: TX first drops invalid skbs through `can_dev_dropped_skb()`, then uses `netif_subqueue_maybe_stop()` with an effective free count. It builds frameinfo and ID registers from SFF/EFF/RTR/FDF/BRS/DLC, writes payload words into `RKCANFD_REG_FD_TXDATA*`, stores an echo skb with frame length, advances `tx_head`, and writes the appropriate TX request bit to `RKCANFD_REG_CMD`. Erratum 12 is handled by temporarily enabling `SPACE_RX_MODE` around command writes. Completion is not driven by the masked TX_FINISH interrupt; instead RX self-reception supplies the timestamp and calls `rkcanfd_handle_tx_done_one()`, which updates error counters, timestamps the echo skb, completes it through CAN RX offload, and updates tx stats.

State and persistence: TX state is `tx_head`, `tx_tail`, echo skb slots, netdev queue state, corrected `bec.txerr`, and ethtool erratum counters updated elsewhere. It persists only while the interface is registered/open. Queue state depends on the two-slot hardware FIFO depth.

Dependencies and integration points: integrates with netdev queue helpers, CAN echo skb APIs, CAN RX offload echo timestamp completion, RX erratum filtering, and shared register definitions. It assumes core enabled RX self-transmit mode and masked normal TX_FINISH interrupts.

Risks and test signals: payload writes cast unaligned byte data to `u32 *`, so architecture alignment behavior matters. Effective free count can return zero for pending extended frames under erratum 6, intentionally serializing TX. Completion depends on RX path correctness; if self-reception is lost, queues can stall. Tests should cover SFF/EFF/RTR/CAN FD/BRS TX encoding, queue busy/stop/wake behavior, erratum 12 command wrapping, erratum 6 retry, timestamped echo completion, bus-off cleanup interactions, and loopback/self-reception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd.h

Purpose: this header is the shared contract for all Rockchip CAN FD driver objects. It defines the register map, bitfields, hardware errata flags, core private structures, inline MMIO helpers, TX ring helpers, and cross-file function prototypes.

Important definitions: register macros cover classic/FD mode control, command, state, interrupt, bit timing, error-code, error counters, acceptance filters, TX/RX frame registers, timestamp registers, TX event/RX FIFO controls, and FIFO data windows. Constants define `DEVICE_NAME`, NAPI weight, two-entry TX FIFO depth, queue thresholds, timestamp worker limit, and a minimum clock warning for erratum 5. Quirk macros describe RK3568 errata and a `RKCANFD_QUIRK_CANFD_BROKEN` flag that disables exposed CAN FD capability.

Important types and APIs: `enum rkcanfd_model` distinguishes RK3568 v2/v3. `struct rkcanfd_devtype_data` stores model and quirk bits. `struct rkcanfd_fifo_header` mirrors FIFO header reads. `struct rkcanfd_stats` contains sequence-protected 64-bit erratum counters. `struct rkcanfd_priv` embeds `can_priv`, `can_rx_offload`, netdev, MMIO base, TX cursors, default mode/mask registers, devtype data, timecounter/cyclecounter, delayed timestamp work, corrected bus-error counters, stats, reset, and bulk clocks. Inline helpers wrap `readl`/`writel`/`readsl` and derive TX head/tail/pending/free.

Control flow and integration: the header has no runtime flow but defines how files call each other: core calls ethtool init and RX handling, TX exposes start_xmit and completion helpers, timestamp exposes skb timestamp and lifecycle helpers. Register macros are consumed throughout the split module.

State and persistence: state layout in `rkcanfd_priv` is the authoritative in-memory driver state. No data is persistent across unload. The header documents hardware errata in comments, including reproduction commands that are useful as validation signals.

Risks and test signals: register definitions are hardware ABI; mistakes silently corrupt MMIO access. Notable risk signal: `RKCANFD_REG_FD_RXDATA5` and `RKCANFD_REG_FD_RXDATA6` both define `0x320`, though RX data is read through the FIFO window rather than these macros in current code. Tests should include compile coverage for all split objects, sparse/endianness checks, RX/TX register encoding audits, and validation of quirk flags against OF match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Kconfig

Purpose: this Kconfig fragment declares the SJA1000 CAN controller family and a set of bus/card-specific drivers that adapt PCI, PCMCIA, ISA, platform, and PC104 hardware to the shared SJA1000 SocketCAN core.

Important symbols and dependencies: `CAN_SJA1000` is a tristate menu depending on `HAS_IOMEM`. Under it, the researched symbols include `CAN_EMS_PCI`, `CAN_EMS_PCMCIA`, `CAN_F81601`, `CAN_KVASER_PCI`, `CAN_PEAK_PCI`, `CAN_PEAK_PCIEC`, `CAN_PEAK_PCMCIA`, and `CAN_PLX_PCI`. PCI drivers depend on `PCI`, PCMCIA drivers depend on `PCMCIA`, PEAK PCMCIA also requires `HAS_IOPORT_MAP`, and PEAK ExpressCard support selects `I2C` and `I2C_ALGOBIT`.

Control flow and integration: there is no runtime flow. Build selection controls which adapter modules are compiled and all selected adapter modules rely on the common `sja1000.o` core via `alloc_sja1000dev()`, `register_sja1000dev()`, and common interrupt handling.

State and persistence: configuration state persists in `.config` only. The menu hierarchy prevents adapter options unless the base SJA1000 family is enabled.

Risks and test signals: dependencies must match implementation requirements; for example PEAK ExpressCard code is conditionally compiled around I2C bit-banging support. Build tests should cover representative PCI-only, PCMCIA-only, and all-enabled configurations, plus `COMPILE_TEST` where available for unrelated architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Makefile

Purpose: this Makefile maps each SJA1000 Kconfig option to its corresponding adapter object and builds the shared SJA1000 core object when `CONFIG_CAN_SJA1000` is enabled.

Important build units: researched entries include `ems_pci.o`, `ems_pcmcia.o`, `f81601.o`, `kvaser_pci.o`, `peak_pci.o`, `peak_pcmcia.o`, and `plx_pci.o`. The file also lists `sja1000.o`, `sja1000_isa.o`, `sja1000_platform.o`, and `tscan1.o`.

Control flow and integration: no runtime flow exists here. The build graph ensures board adapters link independently while sharing the exported SJA1000 core implementation.

State and persistence: only kernel build state is affected. Runtime netdev state is created by adapter probe functions in the corresponding `.c` files.

Risks and test signals: a stale object mapping would break module availability even if Kconfig permits selection. Tests should compile each adapter as built-in and module where the dependency bus is enabled and verify the module names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pci.c

Purpose: this PCI adapter driver supports EMS CPC-PCI, CPC-104P, and CPC-PCIe cards containing one or more SJA1000-compatible CAN channels. It maps board-specific PCI bridge resources and registers each detected channel with the common SJA1000 SocketCAN core.

Important types and APIs: `struct ems_pci_card` stores version, channel count, PCI device, per-channel netdevs, configuration MMIO, and CAN controller MMIO. Version-specific register accessors handle PITA-2 v1, PLX9030 v2, and ASIX99100 v3 layouts. `ems_pci_check_chan()` probes each channel by switching to PeliCAN mode. The PCI driver entry points are `ems_pci_add_card()` and `ems_pci_del_card()`.

Control flow: probe enables the PCI device, allocates card state, determines hardware version from vendor/device IDs, maps configuration and CAN BARs, validates the EMS signature for v1, deasserts ASIX local reset for v3, resets the board, then iterates possible channels. For each channel it allocates an SJA1000 netdev, sets board private data, IRQ flags, IRQ number, register base and accessors, probes channel presence, assigns clock/OCR/CDR, enables bridge interrupts, and calls `register_sja1000dev()`. Remove unregisters/free all registered netdevs, unmaps resources, frees card state, and disables PCI.

State and persistence: driver state is per-card and per-channel in memory only. Hardware configuration includes bridge interrupt status/control, ASIX reset/interrupt enables, and SJA1000 OCR/CDR settings. No persistent storage is used.

Dependencies and integration points: depends on PCI, MMIO, SocketCAN SJA1000 helper APIs, shared IRQs, and version-specific bridge registers. `priv->post_irq` clears bridge-level interrupt latches after the common SJA1000 ISR handles a channel.

Risks and test signals: cleanup assumes `pci_set_drvdata()` card state exists even on partial failures. The maximum channel define is tied to v2, while v3 also supports four channels; code currently uses `EMS_PCI_MAX_CHAN` from v2. Hardware signature/probe paths are version-specific. Tests should cover all three card generations, absent-channel detection, shared IRQ ack behavior, partial registration failure cleanup, and hot remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pcmcia.c

Purpose: this PCMCIA adapter driver supports EMS CPC-CARD devices with up to two SJA1000 channels. It configures the PCMCIA socket, maps the card memory window, detects channels, registers them with the SJA1000 core, and supplies a custom shared interrupt demultiplexer.

Important types and APIs: `struct ems_pcmcia_card` stores channel count, the PCMCIA device, per-channel netdevs, and mapped base address. Register accessors are byte MMIO helpers. `ems_pcmcia_interrupt()` loops over registered channels and calls `sja1000_interrupt()` until no channel handles more work. Probe/remove entry points are `ems_pcmcia_probe()` and `ems_pcmcia_remove()`.

Control flow: PCMCIA probe configures IO resources and an attribute/common memory window, maps the selected page, enables the device, then calls `ems_pcmcia_add_card()`. The card add path allocates card state, maps 4 KiB of card memory, verifies the `0xAA55` signature, resets and maps CAN controllers, allocates up to two SJA1000 netdevs, probes PeliCAN mode, assigns clock/OCR/CDR, marks `SJA1000_CUSTOM_IRQ_HANDLER`, registers channels, and finally requests the shared IRQ for the card-level demux handler. Remove frees IRQ, unregisters/free channels, unmaps controllers, sends unmap command, frees state, and disables PCMCIA.

State and persistence: card state and channel netdevs are in memory. Hardware state includes mapping/reset commands written to card base and SJA1000 mode/CDR/OCR registers. No data persists across unplug/reload.

Dependencies and integration points: depends on PCMCIA core, memory window mapping, SocketCAN SJA1000 common APIs, and shared IRQ support. It relies on the card signature to avoid calling SJA1000 handlers after card removal.

Risks and test signals: `ems_pcmcia_probe()` logs some setup errors but returns 0 in those branches, which can hide probe failure from the bus core. `ems_pcmcia_del_card()` unconditionally calls `free_irq()`, so partial failure before request_irq needs careful validation. Tests should cover card insertion/removal, one- and two-channel cards, IRQ demux under high load, signature loss during ISR, and failed PCMCIA resource setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/f81601.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/f81601.c

Purpose: this PCI driver supports the Fintek F81601 PCIe-to-dual-CAN adapter, exposing one or two SJA1000 channels through SocketCAN.

Important types and APIs: `struct f81601_pci_card` holds the mapped BAR, a spinlock for serialized writes, the PCI device, and two netdev pointers. Module parameters `internal_clk` and `external_clk` choose CAN clock source. `f81601_pci_probe()` and `f81601_pci_remove()` are the PCI entry points. `f81601_pci_write_reg()` serializes writes and posts them with a readback.

Control flow: probe uses managed PCI enable, allocates card state, writes config byte `F81601_DECODE_REG` to enable IO/memory/config decode and both CAN channels, optionally selects the internal 24 MHz clock, maps BAR0, reads a strap bit to determine whether CAN2 exists, then allocates/registers each channel. Each SJA1000 netdev gets shared IRQ flags, BAR offset `0x80 * channel`, read/write callbacks, clock frequency (`24 MHz / 2` or `external_clk / 2`), OCR/CDR, dev_id, and PCI IRQ. Remove unregisters/free all registered channels; devm/pcim resources handle PCI/MMIO cleanup.

State and persistence: runtime state is the card object and registered netdevs. Hardware state includes PCI config decode bits and SJA1000 registers. Module parameters persist only for the loaded module instance.

Dependencies and integration points: depends on PCI managed resource helpers, SocketCAN SJA1000 APIs, shared IRQs, and module parameters. It uses the common SJA1000 core for all CAN protocol behavior.

Risks and test signals: `external_clk` is not validated when `internal_clk=false`, so a zero value would create a zero CAN clock frequency. The write lock only protects writes, not read/write sequences. Tests should cover one-channel strap vs two-channel devices, internal/external clock parameter handling, registration failure cleanup, concurrent register writes under interrupt/TX paths, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/f81601.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/kvaser_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/kvaser_pci.c

Purpose: this PCI driver supports Kvaser PCIcan/PCIcanx boards with up to four SJA1000 channels behind an AMCC S5920/Xilinx interface. It maps common bridge and channel resources, detects channel count, and registers each SJA1000 controller.

Important types and APIs: `struct kvaser_pci` is allocated inside the first channel's SJA1000 private area and tracks PCI device, mapped config/resource windows, Xilinx version, channel count, and slave netdevs. `kvaser_pci_enable_irq()`/`disable_irq()` manipulate S5920 interrupt enable. `number_of_sja1000_chip()` probes channels by setting reset mode. PCI entry points are `kvaser_pci_init_one()` and `kvaser_pci_remove_one()`.

Control flow: probe enables the PCI device, requests regions, maps S5920 config BAR, Xilinx BAR, and channel BAR, counts present SJA1000 chips, then calls `kvaser_pci_add_chan()` for each. Channel 0 initializes Xilinx version, passive PTCR mode, and bridge interrupts; later channels are linked as slaves under the master board object. Each channel gets base address offset by `0x20`, read/write callbacks, shared IRQ, clock/OCR/CDR, dev_id, and registration through `register_sja1000dev()`. Remove calls `kvaser_pci_del_chan()` on the master, then releases regions and disables PCI.

State and persistence: state is anchored in the master netdev's private board structure and slave pointers. Hardware interrupt enable and Xilinx/PTCR state are configured at probe and disabled at removal. No persistence exists beyond device lifetime.

Dependencies and integration points: depends on PCI region management, MMIO, SocketCAN SJA1000 core, and shared interrupts. The master/slave netdev structure means cleanup and drvdata are centered on channel 0.

Risks and test signals: if channel registration fails after one or more slaves, cleanup depends on master linkage being correct. `number_of_sja1000_chip()` uses reset-bit behavior as presence detection. Tests should cover one to four channel cards, registration failure at each channel index, bridge IRQ enable/disable, Xilinx version reporting, and shared IRQ behavior under simultaneous channel traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/kvaser_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pci.c

Purpose: this PCI driver supports PEAK PCAN PCI, PCIe, miniPCI, cPCI, PC/104, OEM, and optionally ExpressCard adapters with up to four SJA1000 channels. It also provides optional ExpressCard LED control via a bit-banged I2C PCA9553 LED controller.

Important types and APIs: `struct peak_pci_chan` is per-channel private data containing config BAR, previous netdev chain link, PITA interrupt mask, and optional ExpressCard card pointer. Under `CONFIG_CAN_PEAK_PCIEC`, `struct peak_pciec_card` owns I2C bit-bang data, LED adapter, delayed LED work, and channel activity snapshots. `peak_pci_probe()`/`peak_pci_remove()` are PCI entry points; `peak_pciec_probe()`/`remove()` manage ExpressCard LEDs.

Control flow: probe enables PCI, requests regions, reads subsystem ID to infer channel count, maps config and channel BARs, toggles PITA reset/mux state, optionally logs FPGA firmware, then loops over channels. For each channel it allocates an SJA1000 netdev with `peak_pci_chan`, assigns shifted-register read/write callbacks, PITA post-IRQ ack, clock/OCR/CDR, shared IRQ, interrupt mask, dev_id, and a linked-list previous-device pointer. ExpressCard variants initialize the I2C LED controller before registration and override the write callback so SJA1000 reset/normal mode changes update LED state. After all channels register, PITA interrupt masks are enabled. Remove disables interrupts, walks the channel chain, removes optional LED resources, unregisters/free netdevs, unmaps BARs, releases regions, and disables PCI.

State and persistence: channel chain state is stored through `pci_set_drvdata()` with the last registered netdev. LED state is cached in memory and periodically updated from netdev byte counters. Hardware state includes PITA GPIO/ICR/misc, optional PCA9553 LED registers, and SJA1000 OCR/CDR. No durable persistence.

Dependencies and integration points: depends on PCI, MMIO, SJA1000 core, optional I2C and `i2c-algo-bit`, delayed work, and shared IRQ post-ack. It integrates channel activity with external LEDs by observing netdev stats and SJA1000 mode writes.

Risks and test signals: channel count inference from subsystem ID is device-contract-sensitive. The linked-list cleanup must remain correct on partial failures. ExpressCard LED code runs only under a Kconfig option and can fail before CAN registration. Tests should cover all device IDs, one to four channels, PITA interrupt ack, FPGA firmware reporting, ExpressCard I2C/LED init and teardown, activity LED timer behavior, and failure cleanup from each channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pcmcia.c

Purpose: this PCMCIA driver supports PEAK-System PCAN-PC Card adapters with one or two SJA1000 channels, including card-level power control and LED activity indication.

Important types and APIs: `struct pcan_pccard` stores the PCMCIA device, channel array, cached common-control register, firmware version, mapped IO window, and LED timer. Per-channel state tracks netdev and previous RX/TX byte counts. The driver provides SJA1000 read/write callbacks, a custom ISR `pcan_isr()`, channel discovery/cleanup helpers, EEPROM write helpers for connector power, and PCMCIA probe/remove.

Control flow: probe negotiates PCMCIA IO config, enables the device, allocates card state, maps IO ports into an iomem-like window, reads firmware version, detects/registers channels, sets up the LED timer, requests the shared IRQ, and powers CAN connectors through EEPROM. `pcan_add_channels()` initializes common CCR reset/LED bits, releases channel reset, allocates each SJA1000 netdev, checks PeliCAN mode presence, assigns callbacks/clock/OCR/CDR, disables CLKOUT on secondary channels, marks custom IRQ handling, and registers the device. The ISR checks card presence and calls `sja1000_interrupt()` for each channel up to a bounded loop count. LED timer changes LED state based on interface up state and RX/TX byte counter deltas.

State and persistence: runtime state includes cached CCR, firmware version for presence checks, channel netdevs, and timer state. The EEPROM write used by `pcan_set_can_power()` may persist connector power configuration on the card, so unlike most files this driver writes device nonvolatile memory. Driver memory state is freed on removal.

Dependencies and integration points: depends on PCMCIA core, IO port mapping, timers, SJA1000 core, shared IRQs, and card EEPROM/SPI registers. It maps ioport resources through `ioport_map()` because the SJA1000 core expects iomem-style accessors.

Risks and test signals: EEPROM power writes include busy-wait loops with schedule and bounded retry; failures leave power state uncertain. Hot-unplug during ISR is handled by firmware-version presence checks. Tests should cover one/two-channel cards, firmware detection, connector power on/off, LED timer transitions, card removal during interrupt, SPI busy timeouts, and no-channel probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/plx_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/plx_pci.c

Purpose: this generic PLX90xx PCI bridge adapter supports many two-channel SJA1000 CAN cards from Adlink, esd, Marathon, TEWS, IXXAT, Connect Tech, Elcus, MOXA, and ASEM. It describes each board's BAR layout, reset routine, clock/OCR/CDR, and PCI IDs, then registers detected channels with the SJA1000 core.

Important types and APIs: `struct plx_pci_card_info` is the board descriptor containing name, channel count, CAN clock, OCR/CDR, config map, per-channel maps, and reset callback. `struct plx_pci_card` stores detected channels, netdevs, mapped config base, and reset callback. Register access is byte MMIO. Reset helpers cover common PLX9030/9050/9052, PLX9056/PEX8311 reload, Marathon PCI/PCIe special reset windows, and ASEM dual-CAN GPIO reset. `plx_pci_check_sja1000()` validates reset-mode register values and PeliCAN transition.

Control flow: probe enables PCI, allocates card state, maps the descriptor-specified config BAR, runs the descriptor reset function, then iterates expected channels. Each channel maps its own BAR/offset, allocates an SJA1000 netdev, assigns shared IRQ, read/write callbacks, private card pointer, clock/OCR/CDR, dev_id, probes channel presence, and registers it. If any channels exist, bridge interrupts are enabled using either PLX INTCSR or PLX9056 INTCSR depending on device ID. Remove unregisters/free channels, unmaps per-channel and config spaces, resets the card, disables bridge interrupts, frees state, and disables PCI.

State and persistence: all driver state is per-card in memory. Hardware state includes PLX interrupt enables, local reset state, optional EEPROM configuration reload, and SJA1000 register configuration. No filesystem persistence.

Dependencies and integration points: depends on PCI IDs/subsystem IDs, PLX bridge registers, SocketCAN SJA1000 core, MMIO, delays, and shared IRQ operation. The descriptor table is the key integration surface for adding supported PLX-based boards.

Risks and test signals: descriptor BAR/offset mistakes can map the wrong hardware without compile-time detection. Some reset paths map extra BARs temporarily and tolerate failures by logging. Failure cleanup calls the remove path, so it assumes partial card fields are initialized safely. Tests should cover each descriptor family, PLX9056 vs non-9056 interrupt setup, absent channels, reset side effects, partial BAR mapping failures, and simultaneous traffic on both channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/plx_pci.c -->
