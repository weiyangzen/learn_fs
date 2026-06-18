# Research: subset-b-004674

Grouped source research for the SysKonnect FDDI `skfp` hardware/SMT subset. Each section is source-tree aligned for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/supern_2.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/supern_2.h

Purpose: Defines the AMD Supernet II/Supernet III FORMAC+ MAC, PLC/ELM physical-layer, descriptor, register, bitfield, command, status, timing, and BIST constants used by the `skfp` FDDI adapter driver. It is the hardware ABI map for the lower-level MAC/PHY code.

Important APIs/types/functions: This header exports no functions, but defines descriptor unions `rx_descr`, `tx_descr`, `tx_pointer`, and `struct tx_queue`; FORMAC register offsets such as `FM_ST1U`, `FM_ST2U`, `FM_MDREG1`, `FM_MDREG2`, `FM_MDREG3`, queue pointer registers, address-filter registers, and command registers; descriptor masks such as `RD_S_MSVALID`, `RX_FS_LLC`, `TD_C_MORE`, and `TD_C_XDONE`; PLC registers such as `PL_CNTRL_A`, `PL_CNTRL_B`, `PL_STATUS_A`, `PL_INTR_EVENT`; PLC state and interrupt masks; timing defaults `TP_C_MIN`, `TP_T_OUT`, `TP_LC_LENGTH`, `TP_NS_MAX`; and conversion macros `MSTOBCLK()` and `MSTOTVX()`.

Control flow: There is no executable control flow. Runtime code uses these symbolic constants to pack/unpack DMA descriptors, drive FORMAC commands, interpret MAC/PLC interrupts, configure receive queues and frame filtering, and program physical connection timers.

State and persistence behavior: The header owns no runtime state. Its constants describe persistent hardware-visible state in device registers, descriptor rings, PLC state machines, address filter CAMs, and MAC counters. Endianness-dependent bitfield layouts in the descriptor unions mirror how 32-bit status/control words appear in memory.

Dependencies and integration points: Used by `hwmtm.c`, `hwt.c`, `pcmplc.c`, MAC code, and board I/O helpers via `ADDR()`, `FM_A()`, and `PLC()`. It depends on compile-time feature switches such as `PCI`, `SUPERNET_3`, `MOT_ELM`, `LITTLE_ENDIAN`, and `TAG_MODE`. Its register constants also align with `targethw.h`, `skfbi.h`, `fplus.h`, and `fplustm.h`.

Risks: Bit positions and register offsets are correctness-critical; a wrong value can corrupt DMA ownership, miss interrupts, or misprogram physical-layer signaling. The descriptor bitfields depend on compiler bitfield layout and endian guards, so most code also uses explicit masks. Several Supernet III notes document changed or reserved meanings, making mixed-chip support risky. Interrupt event registers that clear on read require callers to use these definitions in the right order.

Test signals: Build coverage for both Supernet II/III and endian configurations; descriptor ring init and DMA completion tests; MAC receive status decoding for LLC/SMT/MAC/error frames; PLC interrupt decoding for PCM code, break, enabled, LEM, and elasticity errors; hardware bring-up that verifies BIST signatures and address-filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/supern_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targethw.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targethw.h

Purpose: Defines target hardware configuration and the `struct s_smt_hw` hardware state block embedded in the SMT context for the FDDI adapter.

Important APIs/types/functions: Provides PCI watermarks `RX_WATERMARK`/`TX_WATERMARK`, board IDs `SK_ML_ID_1`/`SK_ML_ID_2`, default `HW_PTR` as `void __iomem *`, optional `struct s_oem_ids`, and `struct s_smt_hw`. The state block stores I/O base, DMA channel, IRQ, flash state, PCI slot/handle/masks, hardware start/stop state, 64-bit adapter flag, hardware timer fields, PIC snapshots, FDDI home/canonical/physical addresses, MAC parameters/counters, ring-up flag, FORMAC state `struct s_smt_fp`, and optional OEM identity pointers.

Control flow: No executable flow. The structure layout is initialized by probe/board setup and then consumed by hardware modules. The `STARTED`/`STOPPED` constants gate destructive operations such as descriptor repair and queue clear.

State and persistence behavior: `struct s_smt_hw` is runtime adapter state. Register and descriptor code mutates `hw_state`, `mac_ring_is_up`, `t_start`, `t_stop`, `timer_activ`, MAC counters, address fields, and FORMAC queue state. The values are not durable, but some mirror persistent adapter configuration such as factory address and OEM ID selection.

Dependencies and integration points: Includes `skfbi.h` plus `fplus.h` or `fplustm.h` depending on `TAG_MODE`. The state is referenced by `hwt.c`, `hwmtm.c`, `pcmplc.c`, MAC/RMT code, and OS glue from `targetos.h`. PCI-specific members integrate with the Linux PCI driver and interrupt source masking.

Risks: This is a cross-module ABI inside the driver; field order and conditional compilation must match all users. The OS-specific and hardware-specific parts share one structure, so stale or partially initialized fields can affect interrupts, DMA, or state-machine decisions. `hw_state` assertions are used to prevent queue cleanup while BMUs are active.

Test signals: Adapter probe and reset should populate I/O, IRQ, address, and FORMAC fields; timer APIs should update `t_start/t_stop/timer_activ`; ring transitions should toggle `mac_ring_is_up`; queue clear/repair paths should reject calls when `hw_state != STOPPED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targethw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targetos.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targetos.h

Purpose: Supplies Linux OS integration definitions for the `skfp` driver, including PCI/FDDI constants, I/O address mapping, ioctl definitions, and the per-adapter OS-private state structure.

Important APIs/types/functions: Defines SysKonnect PCI IDs, FDDI MAC/header/source-routing constants, `ADDR(a)` for MMIO or indexed I/O register addressing, `TICKS_PER_SECOND`, driver limits such as `SKFP_MAX_NUM_BOARDS`, `FP_IO_LEN`, `MAX_TX_QUEUE_LEN`, and `MAX_FRAME_SIZE`, ioctl command wrapper `struct s_skfp_ioctl`, `SKFP_GET_STATS`, `SKFP_CLR_STATS`, and `struct s_smt_os`/`skfddi_priv`. `struct s_smt_os` stores the Linux netdev, PCI device data, shared DMA memory, skb send queue, local fallback RX buffer, FDDI statistics, hardware module state, version, reset flag, and driver spinlock.

Control flow: No direct executable flow. The `ADDR()` macro determines how every register access resolves. In non-MMIO mode it writes the RAP register before returning a banked I/O address, so read/write call sites indirectly trigger I/O side effects through address calculation.

State and persistence behavior: The OS-private structure tracks runtime ownership of netdev, DMA memory, skb queues, local receive buffers, and statistics. It persists for the life of the adapter instance and is the bridge between Linux networking state and the portable SMT/hardware modules.

Dependencies and integration points: Includes Linux headers for I/O, netdev, FDDI, skb, PCI, and socket ioctls, plus `hwmtm.h`. The structure is consumed by OS glue such as `skfddi.c`, by hardware module callbacks in `hwmtm.c`, and by SMT code that expects `smc->os.hwm` and `smc_version`.

Risks: `ADDR()` has side effects in port-I/O mode, so expressions must not evaluate it unexpectedly or multiple times. The embedded `struct pci_dev pdev` reflects older driver style and can be fragile if modernized. Shared memory and DMA addresses must stay coherent with descriptor ownership. ioctl data uses a user pointer and requires careful copy validation in caller code.

Test signals: Build under MMIO and non-MMIO configurations; netdev open/close and reset should preserve `s_smt_os` invariants; ioctl paths should return and clear stats; TX skb queue limits should backpressure; RX fallback buffer should be used only when skb allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targetos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/types.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/types.h

Purpose: Provides small portability definitions for the SMT/hardware code on Linux, mainly legacy memory qualifiers and I/O accessor aliases.

Important APIs/types/functions: Includes `<linux/types.h>`, defines `_packed`, `far`, and `_far` as compatibility no-ops, and maps `inp/inpw/inpd/outp/outpw/outpd` to `ioread8/16/32` and `iowrite8/16/32`.

Control flow: No direct control flow. Calls through the accessor macros perform MMIO or I/O memory reads and writes wherever the legacy code uses DOS/NDIS-style function names.

State and persistence behavior: No owned state. The I/O macros mutate hardware registers and read clear-on-read status registers through call sites in the rest of the driver.

Dependencies and integration points: Included by nearly every `skfp` C file before hardware headers. It lets older portable code compile in the Linux kernel without rewriting all register access calls.

Risks: Accessor argument order differs between read and write wrappers and must match the Linux APIs. These wrappers do not add locking or barriers beyond what `ioread/iowrite` provide. The no-op packing/near/far definitions may hide assumptions from non-Linux source origins.

Test signals: Compile coverage for all files using `inp/outp` aliases; hardware smoke tests that read/write timer, FORMAC, and PLC registers; static review for any call sites expecting old `outp(value, port)` order rather than the defined `outp(port, value)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwmtm.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwmtm.c

Purpose: Implements the hardware module for FORMAC+ transmit/receive descriptor rings, SMT mbuf allocation, interrupt service, frame receive classification, SMT/LLC frame handoff, transmit fragmentation, and queue cleanup/repair.

Important APIs/types/functions: Public entry points include `mac_drv_check_space()`, `mac_drv_init()`, `init_driver_fplus()`, `init_fddi_driver()`, `fddi_isr()`, `process_receive()`, `mac_drv_rx_mode()`, `hwm_rx_frag()`, `hwm_tx_init()`, `hwm_tx_frag()`, `smt_send_mbuf()`, `smt_get_mbuf()`, `smt_free_mbuf()`, `mac_drv_repair_descr()`, `mac_drv_clear_rx_queue()`, and `mac_drv_clear_tx_queue()`. Important internal helpers are `init_descr_ring()`, `init_txd_ring()`, `init_rxd_ring()`, `repair_txd_ring()`, `repair_rxd_ring()`, `queue_llc_rx()`, `get_llc_rx()`, `queue_txd_mb()`, `get_txd_mb()`, and `mac_drv_clear_txd()`.

Control flow: Initialization allocates descriptor memory and mbufs, initializes board/MAC state, aligns the descriptor area, builds circular RX/TX rings, fills RX descriptors through OS callbacks, and initializes PLCs. `fddi_isr()` polls interrupt sources, dispatches slow PLC/MAC/timer/token events, handles fast TX/RX BMU completions, drains queued LLC receives, and runs the SMT event dispatcher. `process_receive()` walks RX descriptors until it finds a hardware-owned descriptor or no complete frame, validates fragment/STF/EOF status, completes DMA, checks FORMAC frame status and length, rejects frames sent by the local MAC, then routes LLC frames to the OS receive callback or copies SMT/NSA/beacon frames into SMT mbufs and optionally duplicates them to LLC. Transmit setup chooses LAN/local delivery from frame control, verifies ring-up state and descriptor availability, maps fragments into TxDs, starts the BMU, and frees/indicates buffers on completion.

State and persistence behavior: Mutates descriptor ring cursors and counters (`rx_curr_get`, `rx_curr_put`, `rx_free`, `rx_used`, `tx_curr_get`, `tx_curr_put`, `tx_free`, `tx_used`), mbuf free and queued lists, receive mode flags (`pass_SMT`, `pass_NSA`, `pass_DB`, `pass_llc_promisc`), error counters, MAC MIB counters, `isr_flag`, `detec_count`, `rx_break`, and `rx_len_error`. No durable persistence exists, but descriptor ownership and DMA mappings persist until hardware or cleanup callbacks complete them.

Dependencies and integration points: Relies on OS-provided allocation, DMA, RX/TX completion, descriptor fill/requeue/clear, and virtual-to-physical callbacks. Uses register constants from `supern_2.h` and board register macros from `skfbiinc.h`. Integrates with FORMAC/PLC interrupt handlers (`mac1_irq`, `mac2_irq`, `mac3_irq`, `plc1_irq`, `plc2_irq`), SMT receive/send (`smt_received_pack`, `smt_send_frame` path), LLC restart, timer/token handlers, and the event dispatcher.

Risks: DMA ownership transitions are delicate; missing `DRV_BUF_FLUSH()` or wrong endian conversion can race hardware. Fragment handling has Supernet errata workarounds and abort paths that must requeue or clear exactly the right descriptor count. ISR loops can process events and deliver frames while hardware interrupts are disabled, so reentrancy and queue overflow matter. Local duplication of SMT frames uses `sm_use_count`; mistakes can double-free or leak mbufs. Queue clear/repair must only run with BMUs stopped.

Test signals: Descriptor allocation alignment; RX of LLC, SMT INFO, SMT NSA, direct beacon, local-source, CRC/error, aborted, too-long, zero-length, and fragmented frames; pass mode toggles; out-of-RxD detection; TX completion for LLC and SMT mbufs; ring-down transmit behavior; descriptor repair after BMU reset; ISR dispatch for PLC/MAC/timer/token and fast BMU interrupts; DMA map/unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwmtm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwt.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwt.c

Purpose: Implements the FBI board hardware timer driver for the 82C54-style timer block used by SMT timers and interrupt forcing.

Important APIs/types/functions: Provides `hwt_start()`, `hwt_stop()`, `hwt_init()`, `hwt_restart()`, `hwt_read()`, and PCI-only `hwt_quick_read()`/`hwt_wait_time()`. `HWT_MAX` caps requested 16 microsecond ticks at 65000.

Control flow: `hwt_start()` clamps the requested 16 us interval, stores `t_start`, programs `B2_TI_INI` with `count * 200`, starts the timer, and marks it active. `hwt_stop()` stops the timer, clears the timer IRQ, and marks it inactive. `hwt_read()` stops an active timer, reads the remaining value, checks ISR timer expiry/wrap, stores elapsed time in `t_stop`, and returns it. The PCI quick-read path briefly stops/reloads/restarts the current timer value and can busy-wait until a duration has elapsed.

State and persistence behavior: Uses `smc->hw.t_start`, `smc->hw.t_stop`, and `smc->hw.timer_activ`. Hardware timer registers hold the active countdown until stopped or expired. Values are runtime-only and reset during hardware initialization.

Dependencies and integration points: Uses `ADDR()`, timer register constants such as `B2_TI_INI`, `B2_TI_CRTL`, `B2_TI_VAL`, `TIM_START`, `TIM_STOP`, `TIM_CL_IRQ`, and `GET_ISR()/IS_TIMINT`. Timer expiry is consumed by `timer_irq()` and then converted into SMT events by the timer package.

Risks: Unit conversion is easy to misread: API time is 16 us ticks, while programmed hardware values are multiplied by 200. `hwt_read()` stops the timer, so callers expecting a non-destructive read must use PCI `hwt_quick_read()`. Busy-wait logic returns immediately if the timer appears stopped, and wrap handling depends on monotonic countdown behavior.

Test signals: Start with zero, small, and above-maximum intervals; verify interrupt clear on stop; read before expiry and after expiry; PCI quick-read should preserve the programmed interval; `hwt_wait_time()` should handle non-wrapped and wrapped countdown cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pcmplc.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pcmplc.c

Purpose: Implements Physical Connection Management (PCM), PLC initialization/control, physical signaling, link error monitoring (LEM), PHY line-state handling, and PLC interrupt translation for FDDI ports.

Important APIs/types/functions: Public entry points include `pcm_init()`, `init_plc()`, `sm_pm_get_ls()`, `plc_config_mux()`, `pcm()`, `sm_lem_evaluate()`, `pcm_status_twisted()`, `pcm_status_state()`, `pcm_rooted_station()`, `plc_irq()`, and debug helpers `pcm_get_state()`, `get_pcm_state()`, `get_linestate()`, `get_pcmstate()`, `list_phy()`, and `pcm_lem_dump()`. Internal helpers include `plc_init()`, `real_init_plc()`, `plc_go_state()`, `plc_send_bits()`, `pcm_fsm()`, `pc_rcode_actions()`, `pc_tcode_actions()`, `lem_evaluate()`, `lem_check_lct()`, `sm_ph_lem_start()`, `sm_ph_lem_stop()`, and `sm_ph_linestate()`.

Control flow: `pcm_init()` initializes each PHY MIB record, port type, PMD class, requested paths, flags, LEM state, PLC state, and then programs the PLCs. `pcm()` runs an action-flag FSM until stable and emits path-change/SNMP/state-change notifications. `pcm_fsm()` handles global start/stop/disable/LCT-timeout transitions plus OFF, BREAK, SIGNAL, JOIN, ACTIVE, TRACE, and MAINT states. BREAK resets PLC signaling and starts the hardware PCM; SIGNAL sequences bit exchanges, LCT start/end, remote/local LCT failure checks, and join negotiation; JOIN raises configuration-manager events; ACTIVE enables LEM and active interrupt masks. `plc_irq()` records PLC errors, updates LEM counters, queues PCM events for code/enabled/break/noise, and queues ECM trace/path-test/reset events.

State and persistence behavior: Mutates per-PHY `struct s_phy` fields such as `pc_mode`, `cf_loop`, `cf_join`, `pc_lem_fail`, `lc_test`, `twisted`, `tr_flag`, signaling bit arrays, PLC substate, timers, LEM counters, and PLC error counters. Updates MIB port fields including `fddiPORTPCMState`, `PCMStateX`, `ConnectState`, `My_Type`, `NeighborType`, `PMDClass`, `RequestedPaths`, `MacIndicated`, `Ler_Estimate`, `Lem_Ct`, and failure counters. Hardware PLC registers persist programmed timers, masks, line-state controls, and PCM commands.

Dependencies and integration points: Uses `supern_2.h` PLC register definitions, SMT timer APIs, event queue, CFM/ECM events, selection criteria (`all_selection_criteria()`), SRF/SNMP/AIX notification hooks, path-test and disconnect flags, and CFM join decisions. It also cooperates with concentrator-specific `plc_is_installed()` and Supernet III/Motorola ELM feature guards.

Risks: The software FSM overlays a hardware PCM that also advances states, so ordering of vector writes, start commands, and errata workarounds is critical. LCT and LEM thresholds directly decide whether a port rejoins or restarts. Supernet III elasticity-buffer error mitigation disables an interrupt and forces disconnect/reset indication after repeated errors. SAS/DAS port-index mapping and path policy can silently withhold connections. PLC interrupt registers may clear on read, so event extraction must be ordered carefully.

Test signals: PCM start/stop/disable/maint transitions; SAS and DAS PHY type/path initialization; signaling against each neighbor type; policy rejection and withhold cases; short/medium/long/extended LCT success and failure; LEM alarm/cutoff events; noise and trace propagation interrupts; Supernet III continuous elasticity error path; mux wrap configuration; debug state snapshots matching PLC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pcmplc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pmf.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pmf.c

Purpose: Implements SMT 7.2 Parameter Management Frame (PMF) GET/SET processing against the FDDI MIB, including parameter table lookup, response construction, authorization, set-count validation, byte-order conversion, parameter validation, and side effects from MIB changes.

Important APIs/types/functions: Primary entry point is `smt_pmf_received_pack()`. Core helpers are `smt_build_pmf_response()`, `smt_authorize()`, `smt_check_set_count()`, `smt_add_para()`, `smt_set_para()`, `smt_get_ptab()`, `smt_mib_phys()`, and `port_to_mib()`. Debug builds expose `dump_smt()` and `dump_hex()`. The central data structure is `p_tab[]`, mapping SMT parameter IDs to access flags, MIB offsets, and swap/format strings.

Control flow: PMF receive validates class, starts the watchdog, builds a reply, and sends it as an SMT INFO frame. Response construction allocates an mbuf, copies addressing/TID metadata, adds reason/timestamp/set-count/station parameters, then walks request parameters. Group GET expands all readable members; indexed MAC/path/port requests can expand index zero to all instances; SET requests authorize remote callers, check set count, validate and apply each parameter, echo parameters in the reply, and on success increment `fddiSMTSetCount`, update timestamp, and store the last-set station ID. `smt_add_para()` serializes parameters from MIB to wire format. `smt_set_para()` parses wire values into temporary native values, validates ranges/policies, mutates MIB fields when `set` is true, and queues side-effect events.

State and persistence behavior: Mutates FDDI MIB configuration and management state, including station policy, connection policy, notification/trace settings, PMF password/station filters, MAC requested paths, frame/not-copied thresholds, unitdata enable, path SBA/timer bounds, port requested paths, maintenance line state, LER thresholds, set count, timestamps, and last-set station ID. Some changes trigger runtime side effects such as RMT enable events, RTM timer reprogramming, ESS/SBA parameter updates, MAC operational value recalculation, and ECM disconnect/reconnect.

Dependencies and integration points: Depends on `smt_p.h` parameter structures, MIB layout from `smc.h`/FDDI headers, `smt_send_frame()`, `smt_get_mbuf()`, `smt_set_timestamp()`, `sm_to_para()`, `mac_update_counter()`, `sm_pm_get_ls()`, `cem_build_path()`, `smt_action()`, `smt_set_mac_opvalues()`, `rtm_set_timer()`, `queue_event()`, and optional ESS/SBA hooks. It is excluded under `SLIM_SMT`.

Risks: The table-driven offset/swap machinery is powerful but fragile: wrong offsets or format strings can leak or corrupt MIB data. Remote SET authorization depends on configured station/password values; all-zero values effectively disable that check. Length validation must reject malformed parameters before pointer advancement. SET side effects can disconnect the ring or alter timers, so accepting invalid ranges would affect live connectivity. Index mapping differs for SAS versus DAS, which can cause wrong port mutation if mishandled.

Test signals: PMF GET for station, MAC, path, port, and group parameters; index-zero expansion for MAC/path/port groups; malformed length and unaligned parameter handling; remote SET with and without authorization/password; stale set-count rejection; range rejection for policies, trace timeout, LER thresholds, SBA values, and actions; successful SET updates reason code, set count, timestamp, last-set station, and queues expected RMT/ECM/timer side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/pmf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/queue.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/queue.c

Purpose: Provides the SMT event queue used to serialize hardware, timer, and management events into ECM, CFM, RMT, SMT, and PCM state machines.

Important APIs/types/functions: Exports `ev_init()`, `queue_event()`, `timer_event()`, `ev_dispatcher()`, and `smt_online()`. Concentrator debug builds also expose `do_smt_flag()`.

Control flow: `ev_init()` resets producer/consumer pointers. `queue_event()` stores class/event at `ev_put`, advances and wraps the ring pointer, and logs an overrun if producer catches consumer. `timer_event()` decodes a timer token into class/event and queues it. `ev_dispatcher()` drains queued events, dispatching by class to `ecm()`, `cfm()`, `rmt()`, `smt_event()`, or `pcm()` for PHY classes, and updates `ev_get` after each event so nested `queue_event()` calls can detect overflow. `smt_online()` queues ECM connect/disconnect and immediately dispatches.

State and persistence behavior: Mutates `smc->q.ev_put`, `smc->q.ev_get`, and `smc->q.ev_queue[]`. The queue is runtime-only, but it is the ordering mechanism for state-machine transitions that update persistent MIB state and hardware controls.

Dependencies and integration points: Integrates with the SMT timer package, ISR path in `hwmtm.c`, and all major SMT state machines. Event class constants and queue storage come from `smc.h`/FDDI headers. `smt_online()` is the public control path for connecting to or disconnecting from the ring.

Risks: On overflow it logs but does not stop insertion, so old unprocessed events may be overwritten. Dispatch is synchronous and can enqueue more events recursively, making ordering important. Unknown classes panic. There is no visible locking in this file; callers must provide serialization appropriate to ISR/task context.

Test signals: Queue wraparound; overrun logging; timer token decoding; connect/disconnect through `smt_online()`; dispatch to each state machine class; nested event production during dispatch; invalid class panic path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/rmt.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/rmt.c

Purpose: Implements SMT Ring Management (RMT), controlling MAC ring operational state, duplicate address handling, directed beacon/trace behavior, ring indications, and MAC availability flags.

Important APIs/types/functions: Public functions are `rmt_init()` and `rmt()`. Internal helpers are `rmt_fsm()`, `start_rmt_timer0/1/2()`, `stop_rmt_timer0/1/2()`, `rmt_dup_actions()`, `rmt_reinsert_actions()`, `rmt_leave_actions()`, and `rmt_new_dup_actions()`. The FSM states are `RM0_ISOLATED`, `RM1_NON_OP`, `RM2_RING_OP`, `RM3_DETECT`, `RM4_NON_OP_DUP`, `RM5_RING_OP_DUP`, `RM6_DIRECTED`, and `RM7_TRACE`.

Control flow: `rmt_init()` sets the initial isolated action state and clears duplicate/ring flags. `rmt()` repeatedly invokes `rmt_fsm()` until the state stabilizes, then reports state change. The FSM globally falls back to isolated if join/loop availability disappears. ISOLATED disables the MAC; NON_OP starts the non-operational timer and sends beacon; RING_OP exposes MAC unitdata availability and ring-up indication; DETECT polls claim/beacon state and waits for duplicate-address or stuck-beacon conditions; NON_OP_DUP announces/acts on duplicate address; RING_OP_DUP waits for duplicate test pass or ring down; DIRECTED sends directed beacons and can move to TRACE; TRACE queues ECM trace propagation.

State and persistence behavior: Mutates `smc->mib.m[MAC0].fddiMACRMTState`, `fddiMACMA_UnitdataAvailable`, and RMT fields such as `dup_addr_test`, `da_flag`, `bn_flag`, `jm_flag`, `no_flag`, `loop_avail`, `sm_ma_avail`, and timer expiry flags. Uses three SMT timers stored in `smc->r`. Hardware state changes are made through `sm_ma_control()` modes such as offline, reset, beacon, and directed.

Dependencies and integration points: Consumes events from `queue.c` and timers from the SMT timer package. Calls MAC hardware abstractions `sm_ma_control()`, `sm_mac_check_beacon_claim()`, and `sm_mac_get_tx_state()`. Reports ring status through `rmt_indication()`, `rmt_state_change()`, `smt_stat_counter()`, `RS_SET/RS_CLEAR`, and ECM events. Non-Supernet III builds call `restart_trt_for_dbcn()` to keep directed beaconing alive.

Risks: Duplicate MAC behavior can either leave or reinsert depending on configuration; reinsertion is noted as non-conformant with the SMT spec. Timer interactions are subtle, especially D_MAX restart on transmit state change and stuck-beacon detection only when local station is beaconing. Incorrect ring-up/down transitions can expose MAC unitdata too early or fail to clear it. Directed beacon workarounds differ by chipset.

Test signals: Join/loop loss should isolate; ring operational/non-operational transitions; D_MAX, non-op, stuck, announce, direct, and poll timer expirations; duplicate address failed/passed flows; configured leave versus reinsert behavior; directed beacon to trace; unitdata enable toggles via `RM_ENABLE_FLAG`; non-Supernet II directed-beacon restart path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/rmt.c -->
