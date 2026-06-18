# Research: subset-b-004662

This grouped report covers TI Ethernet, CPTS/PTP, DaVinci CPDMA/EMAC/MDIO, and ICSSG helper sources. Each source file section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.c

## Purpose
`cpts.c` implements the TI Common Platform Time Sync helper used by CPSW/EMAC-style Ethernet drivers to expose a PTP hardware clock and attach hardware timestamps to PTP packets. It manages the CPTS event FIFO, converts the 32-bit hardware counter through Linux `cyclecounter`/`timecounter`, registers a PHC through `ptp_clock_register()`, and provides exported RX/TX timestamp hooks for network drivers.

## Important APIs, Types, and Functions
The exported surface is `cpts_create()`, `cpts_release()`, `cpts_register()`, `cpts_unregister()`, `cpts_rx_timestamp()`, `cpts_tx_timestamp()`, and `cpts_misc_interrupt()`. Internally, `cpts_fifo_read()` drains hardware events, `cpts_update_cur_time()` pushes a timestamp event to sync the timecounter, `cpts_match_tx_ts()` matches deferred TX timestamp events against queued SKBs, and `cpts_find_ts()` finds RX events by PTP message type/sequence ID. The PTP callbacks are `cpts_ptp_adjfine()`, `cpts_ptp_adjtime()`, `cpts_ptp_gettimeex()`, `cpts_ptp_settime()`, `cpts_ptp_enable()`, and `cpts_overflow_check()`.

## Control Flow and State
`cpts_create()` allocates state, parses DT clock conversion hints and optional refclock mux data, prepares the CPTS clock, initializes locks/completions, calculates multiplier/shift, and leaves the device disabled. `cpts_register()` initializes the event pool and TX queue, enables the reference clock and CPTS interrupt bit, initializes the timecounter, registers the PHC, and schedules overflow work. Hardware FIFO entries are converted into `struct cpts_event` objects from a fixed pool; RX/TX events move to `cpts->events`, push events update `cur_timestamp`, and hardware events become `PTP_CLOCK_EXTTS` notifications. TX timestamping defers SKBs into `cpts->txq` and the PTP worker later matches them by encoded PTP message type and sequence ID.

## Dependencies and Integration Points
This file depends on Linux PTP, timecounter, clock, workqueue, SKB timestamping, DT clock provider, and packet classification helpers. The owning Ethernet driver must call RX/TX timestamp hooks around packet handling and call `cpts_misc_interrupt()` if using interrupt-driven CPTS FIFO draining. `cpts_set_irqpoll()` from the header selects completion-based interrupt mode versus direct polling.

## Risks and Test Signals
The event pool is fixed at `CPTS_MAX_EVENTS`; high timestamp rates can exhaust it and depend on timeout purging. TX timestamp matching is by PTP mtype/sequence ID plus event type, so duplicate sequence IDs in flight can misassociate timestamps. `cpts_ptp_adjfine()` applies `mult_new` only after a push event, making timestamp-push failure visible as clock adjustment lag. Test signals include PHC registration/index, `phc2sys`/`ptp4l` stability, RX/TX hardware timestamp delivery, external timestamp events, FIFO overflow/purge warnings, suspend/remove unregister cleanup, and timeout logs from `cpts_update_cur_time()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.h

## Purpose
`cpts.h` defines the public data structures, register layout, constants, and inline/no-op helpers for the TI CPTS module. It is the contract between CPTS implementation code and Ethernet drivers that optionally enable `CONFIG_TI_CPTS`.

## Important APIs, Types, and Functions
`struct cpsw_cpts` maps the CPTS register block, including control, refclock select, timestamp push/load, interrupt status, FIFO pop, and event high/low registers. `struct cpts_event` represents a queued FIFO event with timeout and converted timestamp. `struct cpts` holds device state: register base, PHC metadata, cyclecounter/timecounter, reference clock, event pool, TX SKB queue, lock/mutex, IRQ-poll mode, completion, and external timestamp enable bits. The header declares `cpts_rx_timestamp()`, `cpts_tx_timestamp()`, lifecycle functions, `cpts_misc_interrupt()`, and inline helpers `cpts_can_timestamp()` and `cpts_set_irqpoll()`.

## Control Flow and State
The header documents the state model used by `cpts.c`: hardware emits typed events encoded in `EVENT_HIGH`, with event type, port, PTP message type, and sequence ID masks. The software pool is bounded by `CPTS_MAX_EVENTS`, while the hardware FIFO depth is `CPTS_FIFO_DEPTH`. `cpts_can_timestamp()` is a fast packet-classification gate that checks `ptp_classify_raw()` before drivers spend work on CPTS timestamping.

## Dependencies and Integration Points
When CPTS is enabled, consumers need Linux clock, timecounter, PTP clock kernel, SKB, list, OF, and PTP classifier types. When disabled, the header supplies no-op stubs so callers can compile without scattered `#ifdef`s; `cpts_create()` returns `NULL`, registration succeeds, timestamp hooks do nothing, and `cpts_can_timestamp()` returns false.

## Risks and Test Signals
Because `struct cpts` is exposed to companion drivers, field lifetime and locking assumptions are part of the ABI inside the kernel tree. Callers must not use no-op mode as though a PHC exists. Tests should cover both `CONFIG_TI_CPTS=y/m` and disabled builds, verify callers handle `NULL` from stub `cpts_create()`, and validate that inline classification does not alter SKB state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.c

## Purpose
`davinci_cpdma.c` implements the TI CPDMA/CPPI 3.0 descriptor engine used by DaVinci EMAC and related Ethernet blocks. It abstracts descriptor memory allocation, TX/RX channel state, DMA mapping, queue submission, completion processing, channel teardown, interrupt masking, descriptor weighting, and TX rate limiting.

## Important APIs, Types, and Functions
Important internal types are `struct cpdma_desc`, `struct cpdma_desc_pool`, `struct cpdma_ctlr`, and `struct cpdma_chan`. The exported controller API is `cpdma_ctlr_create()`, `cpdma_ctlr_start()`, `cpdma_ctlr_stop()`, `cpdma_ctlr_destroy()`, `cpdma_ctlr_int_ctrl()`, `cpdma_ctlr_eoi()`, and channel-state readers. The exported channel API includes `cpdma_chan_create()`, `cpdma_chan_destroy()`, `cpdma_chan_start()`, `cpdma_chan_stop()`, submit variants for mapped/unmapped and idle/active paths, `cpdma_chan_process()`, `cpdma_check_free_tx_desc()`, stats, weight, and TX rate helpers.

## Control Flow and State
`cpdma_ctlr_create()` copies parameters, builds a descriptor pool backed either by internal SRAM/ioremap or coherent DMA memory, and initially splits descriptors equally between RX and TX. `cpdma_ctlr_start()` optionally soft-resets hardware, clears HDP/CP registers, disables stale interrupts, enables TX/RX control, activates existing channels, and programs shapers. `cpdma_chan_submit_si()` enforces per-channel descriptor limits, allocates one descriptor, maps or syncs the packet buffer, fills hardware and software descriptor fields, appends it to the channel chain, and writes RX free count when needed. `cpdma_chan_process()` pops completed descriptors up to a quota, checks ownership, acknowledges completion, handles EOQ requeue, unmaps/syncs data, frees the descriptor, and calls the client handler outside the channel lock. `cpdma_chan_stop()` enters teardown, disables channel interrupts, writes teardown, waits for teardown completion, drains completed descriptors, then frees any remaining descriptors with `-ENOSYS`.

## Dependencies and Integration Points
This code depends on DMA mapping APIs, `gen_pool`, MMIO accessors, CPDMA register offsets, and client callbacks supplied through `cpdma_handler_fn`. DaVinci EMAC consumes it for packet TX/RX, NAPI polling, and TX timeout recovery. Extended-register operations are gated by `has_ext_regs`; callers on older hardware must tolerate `-ENOTSUPP`.

## Risks and Test Signals
The most sensitive paths are descriptor pool sizing, teardown waits, DMA sync/unmap correctness for externally mapped buffers, EOQ misqueue recovery, and TX rate/weight configuration under nested controller/channel locks. `cpdma_control_get()` and `_set()` index `controls[control]` before range validation, so invalid enum values are a latent bounds risk if externally reachable. Test signals include RX/TX under descriptor exhaustion, active/idle submit behavior, teardown during traffic, host-error recovery, interrupt mask toggling, SRAM versus coherent descriptor pools, weighted descriptor split failures, and BQL/queue wake behavior in EMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.h

## Purpose
`davinci_cpdma.h` is the public interface for the DaVinci CPDMA engine. It defines controller parameters, channel statistics, callback types, descriptor status helpers, EOI codes, control enums, and lifecycle/TX/RX function prototypes.

## Important APIs, Types, and Functions
`struct cpdma_params` describes platform resources: device, DMA register windows, HDP/CP/RX free registers, channel count, reset capability, minimum packet size, descriptor memory location/size/alignment, bus frequency, optional descriptor-pool override, and extended-register support. `struct cpdma_chan_stats` records enqueue/dequeue/resource counters useful for diagnostics. `cpdma_handler_fn` is the completion callback signature. The header exposes controller creation/start/stop/destroy, channel create/start/stop/destroy/process/submit, interrupt control, rate and weight configuration, descriptor count tuning, and low-level controls such as `CPDMA_TX_RLIM` and `CPDMA_RX_BUFFER_OFFSET`.

## Control Flow and State
Callers create one `cpdma_ctlr`, then one or more TX/RX channels. RX channels are identified by `rx_type` at creation and submit buffers before or after controller start. State is opaque to callers; all channel/controller internals are hidden behind forward declarations. Status bits exposed through macros are used by completion handlers to interpret RX source port and VLAN encapsulation data.

## Dependencies and Integration Points
The header depends on Linux device, DMA, and bit helper types through included users. DaVinci EMAC supplies `cpdma_params` from platform resources and uses the exported functions in open/stop/NAPI/TX timeout paths. Other TI drivers can share the same abstraction when their hardware matches CPDMA semantics.

## Risks and Test Signals
Because the interface supports both mapped and unmapped buffer submission, callers must match ownership expectations: mapped submit paths require the CPDMA layer to sync rather than unmap. Descriptor count setters can repartition channel resources, so tests should verify RX/TX descriptor accounting after channel creation and after `cpdma_set_num_rx_descs()`. Build coverage should include consumers with and without extended registers and validate enum ordering against `davinci_cpdma.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_emac.c

## Purpose
`davinci_emac.c` is the platform network driver for TI DaVinci EMAC hardware. It wires the EMAC register block, CPDMA channels, PHY/MDIO integration, NAPI polling, IRQ handling, multicast filtering, ethtool coalescing, netdev operations, runtime PM, and platform/OF probing into a Linux Ethernet device.

## Important APIs, Types, and Functions
The central state type is `struct emac_priv`, containing netdev/platform pointers, NAPI, mapped EMAC/control registers, CPDMA controller/channels, link state, speed/duplex, multicast hash state, coalescing interval, bus frequency, RMII/version flags, PHY references, lock, and optional platform interrupt callbacks. Netdev operations are implemented by `emac_dev_open()`, `emac_dev_stop()`, `emac_dev_xmit()`, `emac_dev_setmac_addr()`, `emac_dev_mcast_set()`, `emac_devioctl()`, `emac_dev_tx_timeout()`, and `emac_dev_getnetstats()`. Probe/remove and PM are handled by `davinci_emac_probe()`, `davinci_emac_remove()`, suspend/resume callbacks, and `late_initcall()`.

## Control Flow and State
Probe obtains the EMAC clock, allocates a netdev, parses platform/OF data, maps register resources, creates a CPDMA controller and one TX/RX channel, derives or randomizes the MAC address, adds NAPI, enables runtime PM, and registers the netdev. Open resumes the device, resets local MAC filter state, pre-fills RX descriptors through `cpdma_chan_idle_submit()`, requests all platform IRQs, soft-resets and configures EMAC hardware, enables NAPI/interrupts, starts CPDMA, connects a PHY by phandle or bus scan, or falls back to fixed 100/full operation. IRQ handling only disables interrupts and schedules NAPI. NAPI reads `MACINVECTOR`, processes bounded TX/RX CPDMA completions, handles fatal host errors, and reenables interrupts when budget is not exhausted. Stop disables queue/NAPI/interrupts, stops CPDMA, soft-resets EMAC, disconnects PHY, frees IRQs, and drops the runtime PM reference.

## Dependencies and Integration Points
The driver depends on `davinci_cpdma`, PHYLIB, OF MDIO/fixed-link helpers, TI control-module MAC ID helpers, platform resources, runtime PM, ethtool, and optional platform interrupt enable/disable hooks. It expects a separate MDIO provider (`ti,davinci_mdio`) unless a fixed link is used.

## Risks and Test Signals
Risk areas include open rollback after partial IRQ allocation, RX descriptor prefill failure, CPDMA stop while NAPI/IRQ state is changing, fatal host-error recovery that disables NAPI without full device reset, multicast hash collisions/counters, coalescing math across EMAC versions, and MAC address acquisition fallbacks. `davinci_emac_remove()` destroys CPDMA channels before `unregister_netdev()`, which is unusual if the interface can still be up; removal tests should exercise opened devices. Test signals include probe/remove under OF and platform data, link up/down and speed changes, TX timeout restart, RX refill after allocation failure, ethtool coalesce boundaries, multicast/promiscuous/allmulti transitions, runtime suspend/resume, and CPDMA stats under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_mdio.c

## Purpose
`davinci_mdio.c` implements the DaVinci/CPSW MDIO bus driver. It supports normal hardware user-access transactions and a manual bitbang mode used on selected K3 SoCs, registers an `mii_bus`, integrates runtime PM/autosuspend, scans or registers DT-described PHYs, and handles system/runtime suspend.

## Important APIs, Types, and Functions
`struct davinci_mdio_regs` maps the MDIO register block, including control, alive/link status, user interrupt registers, manual interface, poll/manual mode, and user access/physel entries. `struct davinci_mdio_data` stores platform data, optional `mdiobb_ctrl`, registers, clock, device, bus, access timing, scan policy, divider, and manual-mode flag. Core functions include `davinci_mdio_init_clk()`, enable/disable/manual-mode helpers, `wait_for_user_access()`, `wait_for_idle()`, `davinci_mdio_read()`, `davinci_mdio_write()`, bitbang C22/C45 wrappers, reset helpers, probe/remove, and runtime/system PM callbacks.

## Control Flow and State
Probe allocates driver state and either a bitbang or normal MDIO bus, reads DT/platform bus frequency, chooses manual mode through SoC family matching, maps registers, computes the MDIO clock divider and conservative access time, enables runtime PM, optionally skips alive-register scan when DT child PHYs are present, and registers the bus with `of_mdiobus_register()`. Each hardware read/write resumes the device, waits for the user-access engine, issues a transaction, handles `-EAGAIN` when an idled controller must be re-enabled after EMAC reset interference, then autosuspends. Reset resumes the device, enables manual mode if needed, waits for scan logic to settle, logs version/frequency, and updates `phy_mask` from the alive register unless scan is skipped.

## Dependencies and Integration Points
This driver depends on PHYLIB, OF MDIO, `mdio-bitbang`, runtime PM, clocks, pinctrl sleep/default states, and SoC matching. DaVinci EMAC may locate this bus via `of_find_compatible_node()` when no PHY handle is provided.

## Risks and Test Signals
Clock-divider math assumes a valid input clock and nonzero bus frequency. Hardware access can time out or be reset mid-transaction by EMAC soft reset, so retry behavior and logs matter. Manual mode changes bus operations and uses bitbang C45 support, requiring coverage on AM62/AM64/AM65/J72 families. Test signals include bus registration with explicit DT PHY children and legacy scan-only DTs, alive mask correctness, runtime autosuspend around reads/writes, EMAC reset during MDIO access, C22/C45 bitbang transactions, suspend pinctrl state changes, and remove cleanup including `free_mdio_bitbang()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.c

## Purpose
`icss_iep.c` implements the TI ICSS/ICSSG Industrial Ethernet Peripheral timer driver. It exposes the IEP counter as a PTP hardware clock, supports firmware-provided clock operations, PPS/perout/external timestamp features, variant-specific register maps, exclusive client acquisition by DT phandle, and raw firmware timer initialization.

## Important APIs, Types, and Functions
Exported APIs include `icss_iep_get()`, `icss_iep_get_idx()`, `icss_iep_put()`, `icss_iep_init()`, `icss_iep_exit()`, `icss_iep_init_fw()`, `icss_iep_exit_fw()`, `icss_iep_get_count_low()`, `icss_iep_get_count_hi()`, and `icss_iep_get_ptp_clock_idx()`. PTP callbacks are `icss_iep_ptp_adjfine()`, `icss_iep_ptp_adjtime()`, `icss_iep_ptp_gettimeex()`, `icss_iep_ptp_settime()`, and `icss_iep_ptp_enable()`. Perout/PPS work is handled by compare register programming, `icss_iep_cap_cmp_irq()`, and `icss_iep_cap_cmp_work()`.

## Control Flow and State
Probe maps the IEP register resource, optionally requests the compare/capture IRQ, reads the clock rate, calculates default nanosecond increment, initializes a regmap using SoC-specific offsets and valid-register callbacks, copies base PTP info, initializes the PHC mutex, stores drvdata, and disables the counter. Client drivers acquire a single IEP through `icss_iep_get_idx()`, which rejects concurrent owners via `client_np`. `icss_iep_init()` programs default and compensation increments, optional slow compensation, shadow mode for cyclic operation, sets time to real time, derives supported PTP features from hardware flags/clockops/IRQ, and registers the PHC. `icss_iep_exit()` unregisters the PHC, disables the counter, and tears down PPS/perout state.

## Dependencies and Integration Points
The file depends on PTP clock kernel APIs, regmap with custom MMIO callbacks, platform/OF helpers, clocks, workqueues, and PRU Ethernet firmware clockops (`prueth_iep_clockops` declared in the header). ICSSG Ethernet drivers use this for PHC indices, firmware time sync, RX/TX timestamp conversion, and perout/PPS.

## Risks and Test Signals
`icss_iep_ptp_adjfine()` divides by `ppb`; a zero adjustment can produce a divide-by-zero path unless guarded elsewhere. PPS and perout are mutually exclusive and share compare 1/sync registers, so state transitions need lock coverage. Register writes mix `regmap` and direct `readl/writel` for timing, so variant offset tables must be exact. Test signals include PHC registration across AM335x/AM437x/AM57xx/AM654 variants, 32-bit versus 64-bit counter reads, adjfine positive/negative/zero, PPS/perout enable/disable and IRQ work, exclusive get/put behavior, firmware clockops delegation, and invalid slow clock rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.h

## Purpose
`icss_iep.h` defines the public ICSS IEP timer interface for PRU/ICSSG Ethernet drivers. It provides logical register IDs, platform-data shape, runtime state, firmware clockops, and exported function prototypes.

## Important APIs, Types, and Functions
The register enum gives stable logical IDs for global config/status, compensation, count, capture, compare, sync, period, delay, and start registers; SoC-specific code maps those IDs to offsets. `struct icss_iep_plat_data` holds a regmap config, offset table, and feature flags. `struct icss_iep` holds device and MMIO state, regmap, exclusive client node, reference clock data, PHC info/clock, mutex, increment/compensation fields, optional firmware `struct icss_iep_clockops`, cycle time, PPS/perout/latch state, IRQ, period, and work item. `struct icss_iep_clockops` lets firmware-specific users override settime, adjtime, gettime, perout, and external timestamp behavior.

## Control Flow and State
Consumers obtain an IEP with `icss_iep_get()` or indexed `icss_iep_get_idx()`, initialize either raw firmware mode with `icss_iep_init_fw()` or PHC mode with `icss_iep_init()`, query counts/PHC index, then call exit and put in reverse. The state is intentionally not opaque; ICSSG code can inspect fields such as `ptp_clock`, but should respect `ptp_clk_mutex` for clock operations and exclusive ownership through `client_np`.

## Dependencies and Integration Points
The header depends on mutex, PTP clock kernel, and regmap types. It is included by `icss_iep.c` and ICSSG Ethernet files needing PTP and firmware timer integration. `prueth_iep_clockops` is declared here for the PRU Ethernet implementation.

## Risks and Test Signals
Because `struct icss_iep` is exposed, changes to field names or semantics can break companion drivers. Register enum additions must remain synchronized with all offset tables in `icss_iep.c`. Tests should cover build integration for PHC and firmware users, indexed phandle acquisition, and feature combinations where perout, PPS, external timestamp, or 64-bit counters are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_classifier.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_classifier.c

## Purpose
`icssg_classifier.c` programs the ICSSG MII-G real-time classifier tables and gates used to accept, drop, or classify Ethernet frames for PRU Ethernet slices. It handles host/port MAC programming, default filtering, promiscuous mode, SR1 multicast filtering, source-address validation setup, and HSR/PRP PTP filter table programming.

## Important APIs, Types, and Functions
The file defines filter table constants for FT1 and FT3, classifier gate/select bitfields, slice-specific MII-G register offsets, and helpers that write FT1 destination-address slots, masks, config types, classifier AND/OR masks, selection modes, and gates. Exported functions are `icssg_class_set_host_mac_addr()`, `icssg_class_set_mac_addr()`, `icssg_class_disable()`, `icssg_class_default()`, `icssg_class_promiscuous_sr1()`, `icssg_class_add_mcast_sr1()`, `icssg_ft1_set_mac_addr()`, and `icssg_ft3_hsr_configurations()`.

## Control Flow and State
Classifier programming is direct regmap writes into per-slice offsets. `icssg_class_disable()` enables the L2 gateway, clears all classifier AND/OR matches, sets selection to OR, configures gates to allow filtered flow, disables all FT1 slots, clears their address/mask registers, and clears CFG2. `icssg_class_default()` starts from disabled state and enables broadcast plus PRU destination MAC matching, optionally multicast, for either five SR1 classifiers or one newer classifier. `icssg_class_promiscuous_sr1()` bypasses filters by setting RAW gates. `icssg_class_add_mcast_sr1()` reserves two FT1 slots for standard multicast prefixes, then adds netdev multicast addresses until slots are exhausted, falling back to allmulti.

## Dependencies and Integration Points
The file depends on `regmap`, Ethernet address helpers, `net_device` multicast iteration, and `icssg_prueth.h` for PRU mode/version data. It is invoked by ICSSG netdev setup, RX mode changes, and HSR/PRP offload configuration.

## Risks and Test Signals
The offset table is hardware-contract critical; wrong slice offsets silently program the wrong classifier. Slot exhaustion in SR1 multicast forces allmulti, so multicast-heavy workloads should be tested. HSR/PRP FT3 setup uses different EtherType offsets for PRP versus HSR and configures dedicated classifier indices, so mode switching needs validation. Test signals include unicast/broadcast/multicast acceptance, allmulti/promiscuous toggles, reserved multicast prefix handling, SAV FT1 MAC setup, SR1 versus non-SR1 default behavior, and PTP detection inside HSR/PRP tagged frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_classifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_common.c

## Purpose
`icssg_common.c` provides shared ICSSG Ethernet runtime logic: K3 UDMA TX/RX channel setup and cleanup, descriptor pools, page-pool RX, AF_XDP zero-copy, XDP actions, NAPI/IRQ handlers, TX/RX timestamp support, netdev timestamp/stat helpers, device-tree port mapping, PRU/RTU/TX_PRU core acquisition, and system sleep PM.

## Important APIs, Types, and Functions
Exported channel lifecycle functions include `prueth_init_tx_chns()`, `prueth_cleanup_tx_chns()`, `prueth_ndev_add_tx_napi()`, `prueth_ndev_del_tx_napi()`, `prueth_init_rx_chns()`, `prueth_cleanup_rx_chns()`, `prueth_prepare_rx_chan()`, `prueth_reset_tx_chan()`, and `prueth_reset_rx_chan()`. Packet paths are `icssg_ndo_start_xmit()`, `emac_tx_complete_packets()`, `icssg_napi_rx_poll()`, `prueth_rx_irq()`, `emac_xmit_xdp_frame()`, `prueth_xmit_free()`, `prueth_tx_cleanup()`, and `prueth_rx_cleanup()`. Timestamp/stat helpers include `icssg_ts_to_ns()`, `emac_rx_timestamp()`, `icssg_ndo_set_ts_config()`, `icssg_ndo_get_ts_config()`, and `icssg_ndo_get_stats64()`.

## Control Flow and State
TX initialization requests one K3 UDMA TX channel per queue, creates CPPI5 host descriptor pools, obtains IRQs, and later registers per-queue TX NAPI. RX initialization requests a UDMA RX channel, creates a descriptor pool and page pool, initializes all flows, records flow IDs, and obtains flow IRQs. RX preparation fills the free descriptor queue with page-pool pages or AF_XDP buffers. TX builds CPPI5 descriptors for the linear SKB and page frags, encodes queue/port tags, handles HSR offload tags, optionally reserves a TX timestamp cookie, accounts BQL, pushes to UDMA, and stops the queue if descriptors fall below `MAX_SKB_FRAGS`. Completion pops TX descriptors, handles teardown completions, frees SKB/XDP/XSK resources, updates stats/BQL, wakes queues, and services XSK TX.

## Dependencies and Integration Points
The file depends on K3 UDMA glue, CPPI5 descriptors, K3 descriptor pools, page_pool, XDP/AF_XDP, PHY/OF helpers, PRUSS/remoteproc, shared memory timestamp registers, ICSSG firmware stats/config helpers, and netdev queues/NAPI. Other ICSSG mode-specific drivers use this as a common library through exported symbols.

## Risks and Test Signals
Risk areas include descriptor leak/unmap mismatches across SKB, XDP frame, XDP_TX page-pool, and XSK paths; TX timestamp cookie reservation cleanup on error; queue stop/wake races; teardown completion accounting; RX page replacement failure and requeue behavior; firmware CRC stripping; SR1 versus newer timestamp conversion; and IRQ pacing timers that defer re-enable. `prueth_reset_rx_chan()` currently uses a fixed flow count from callers, so SR1 flow-count mismatches are worth testing. Test signals include multi-queue TX with frags, descriptor exhaustion, XDP_PASS/TX/REDIRECT/DROP, AF_XDP zero-copy wakeups, RX/TX teardown while traffic runs, hardware timestamp configuration and delivery, HSR offload TX tags, stats aggregation, suspend/resume with running netdevs, and PRU core acquire/release failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_common.c -->
