# Research: subset-b-004673

This grouped report covers the SysKonnect FDDI `skfp` SMT, FORMAC+, board glue, register, descriptor, and protocol headers. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/cfm.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/cfm.c

## Purpose
`cfm.c` implements SMT Configuration Management for a single-MAC FDDI station. It decides whether the station is isolated, wrapped on A/B/S, or through-connected, updates MIB path state, programs the PHY mux through `config_mux()`, and tells Ring Management whether the MAC should join or loop.

## Important APIs, Types, And Functions
The public entry points are `cfm_init()`, `cfm()`, `all_selection_criteria()`, `cfm_get_mac_input()`, `cfm_get_mac_output()`, and `cem_build_path()`. The core implementation is `cfm_fsm()`, with action-state tagging via `AFLAG`, `GO_STATE()`, and `ACTIONS_DONE()`. `selection_criteria()` computes per-port withhold flags, and `cem_priv_state()` maintains private CEM port states (`DOWN`, `UP`, `HOLD`) for DAS dual-homing behavior.

## Control Flow
`cfm()` recomputes all port selection criteria, applies CEM private-port state transitions for join/loop events, then repeatedly calls `cfm_fsm()` until the MIB CFM state stabilizes. Action states perform hardware and MIB side effects: set `fddiPORTCurrentPath`, `fddiPORTMACPlacement`, `fddiSMTStationStatus`, mux mode, RMT join/loop flags, and queued RMT events. Stable states evaluate transitions from `cf_join`, `cf_loop`, `wc_flag`, `pc_mode`, `attach_s`, and station type. SAS stations enter `SC11_C_WRAP_S`; DAS stations use `SC9_C_WRAP_A`, `SC10_C_WRAP_B`, `SC4_THRU_A`, or `SC5_THRU_B`.

## State And Persistence
State is runtime-only in `smc->mib.fddiSMTCF_State`, per-port `smc->y[]` flags (`cf_join`, `cf_loop`, `wc_flag`, `scrub`, `cem_pst`), and RMT flags (`rm_join`, `rm_loop`). The file has no disk persistence. Its persistent hardware-visible effects are mux programming and updated SMT MIB values that other frame services expose.

## Dependencies And Integration Points
It depends on `smtstate.h`, `smc.h`, queue dispatch, RMT, PCM port flags, `config_mux()`, and optional SRF reporting through `smt_srf_event()`. RMT consumes the queued `RM_JOIN`/`RM_LOOP` events. ECM uses `cfm_get_mac_input()` and `cfm_get_mac_output()` for trace propagation. SMT path reporting uses `cem_build_path()`.

## Risks And Edge Cases
The state array indexing assumes CFM states fit the sparse SMT values in `smtstate.h`; new states can break `cfm_states[]` or `cf_to_ptype[]`. Withhold logic only gives A-port special handling and deliberately lets B take precedence. `cem_build_path()` ignores `path_index` and omits `SC5_THRU_B`, so through-B reports use the default isolated path unless callers map it elsewhere. CFM action state bits must not leak into MIB consumers.

## Test Signals
Exercise SAS and DAS attach modes, join/loop events on A and B, tree/peer PCM modes, `attach_s` toggles, peer-wrap SRF condition transitions, mux calls for isolate/wrap/through, `scrub` flag setting during wrap-to-through changes, RMT event generation, and path descriptor output from `cem_build_path()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/cfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/drvfbi.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/drvfbi.c

## Purpose
`drvfbi.c` is the board-dependent FBI glue for SMT and LLC. It resets and starts/stops PCI FDDI hardware, reads board identity and MAC address data, handles top-level MAC/PLC/timer interrupt entry points, controls the optical bypass, updates LEDs, and bridges protocol-state changes to OS or driver callbacks.

## Important APIs, Types, And Functions
Key entry points are `init_board()`, `card_stop()`, `read_address()`, `mac1_irq()`, `plc1_irq()`, `plc2_irq()`, `timer_irq()`, `sm_pm_bypass_req()`, `sm_pm_bypass_present()`, `pcm_state_change()`, `rmt_indication()`, `driver_get_bia()`, and `smt_start_watchdog()`. `card_start()` and `smt_stop_watchdog()` are internal reset helpers. Optional `set_oi_id_def()` validates the MULT_OEM ID table.

## Control Flow
`init_board()` calls `card_start()`, reads MAC/PMD metadata, then sets SAS/DAS and bypass-present MIB state from `B0_DAS`. `card_start()` stops the watchdog, quiesces FORMAC, resets HPI/master/chips, clears PCI status errors, detects 64-bit-capable board revisions, initializes BMU watermarks, LED state, watchdog interval, interrupt mask, and `hw_state`. `card_stop()` performs the quiesce/reset path and clears LEDs.

Interrupt dispatch is thin: `mac1_irq()` handles FORMAC status-1 transmit/parity/underrun conditions and restarts transmit paths; `plc1_irq()`/`plc2_irq()` read PLC interrupt status and call `plc_irq()` for B/A respectively; `timer_irq()` restarts the hardware timer and drains SMT timers. LED updates follow PCM active states and RMT ring-up indications.

## State And Persistence
Runtime state lives in `smc->hw` (`hw_state`, `is_imask`, `hw_is_64bit`, MAC addresses, watchdog use, ring-up flag) plus MIB fields for bypass presence and station type. It reads board PROM/config registers but does not persist changes across resets except hardware latch state such as bypass insert/remove and LED/watchdog registers.

## Dependencies And Integration Points
The file depends on `skfbiinc.h`, `supern_2.h`, `skfbi.h` register macros, Linux PCI and bit reversal helpers, FORMAC helpers (`formac_tx_restart()`), PLC handling (`plc_irq()`), SMT timer code, LLC restart callbacks, and optional driver hooks `DRV_PCM_STATE_CHANGE`/`DRV_RMT_INDICATION`.

## Risks And Edge Cases
Reset order is hardware-sensitive: FORMAC init, HPI reset, PCI status clearing, and BMU watermarks are sequenced deliberately. MAC addresses are stored in both FDDI physical bit order and canonical order; wrong bit reversal breaks address matching. `mac1_irq()` loops after restart until status clears, so unhandled sticky bits can spin. `sm_pm_bypass_present()` reads hardware directly and assumes PCI register access is valid.

## Test Signals
Validate cold init and stop, SAS versus DAS detection, optional bypass insert/deinsert, watchdog start/stop, physical and canonical MAC address reads, green/yellow LED changes during PCM/RMT transitions, transmit abort recovery calling `llc_restart_tx()`, parity/underrun panic paths, PLC interrupt routing, timer interrupt draining SMT timers, and MULT_OEM table validation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/drvfbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ecm.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ecm.c

## Purpose
`ecm.c` implements SMT Entity Coordination Management. It inserts or removes the station from the ring, coordinates PCM start/stop across PHYs, handles trace propagation and path-test sequencing, controls optical bypass insertion/deinsertion, and reports ring/status events.

## Important APIs, Types, And Functions
The public API is `ecm_init()` and `ecm()`. The internal engine is `ecm_fsm()` with action-state macros mirroring CFM. `prop_actions()` propagates trace events through MAC/PHY topology. `start_ecm_timer()` and `stop_ecm_timer()` wrap SMT timer operations using `EV_TOKEN(EVENT_ECM, event)`.

## Control Flow
`ecm()` loops `ecm_fsm()` until `fddiSMTECMState` stabilizes, then calls `ecm_state_change()`. `EC0_OUT` waits for `EC_CONNECT`; if bypass exists on a DAS, it enters `EC5_INSERT`, otherwise `EC1_IN`. `EC1_IN` clears trace state, sends `MA_TREQ`, and queues `PC_START` for present PHYs. Trace propagation moves to `EC2_TRACE`, starts the Trace_Max timer, and either propagates upstream or marks a path test pending. Disconnects enter `EC3_LEAVE`, stop PCM, wait `TD_Min`, then either go out, path-test, or deinsert bypass. Bypass check polls QLS/HLS line states in `EC6_CHECK`; stuck bypass is reported once through AIX/ring-status hooks.

## State And Persistence
The state machine uses `smc->mib.fddiSMTECMState`, `fddiSMTBypassPresent`, `fddiSMTRemoteDisconnectFlag`, and `smc->e` fields (`path_test`, `trace_prop`, `sb_flag`, `DisconnectFlag`, `ecm_line_state`, `ecm_timer`). There is no storage persistence. Hardware side effects are MAC control commands, PCM events, timer state, and bypass control requests.

## Dependencies And Integration Points
ECM depends on SMT timers, queue dispatch, PCM, CFM topology helpers, RMT/MAC control, bypass hardware functions from `drvfbi.c`, line-state reads from PM/PLC code, `ring_status_indication()` via `RS_SET`, and optional `AIX_EVENT` reporting.

## Risks And Edge Cases
The bypass check state polls through a timer event value of `0`; dispatcher behavior must keep invoking ECM without confusing it with a named timeout. `trace_prop` needs enough bits for all PHY entities and the MAC; `NUMPHYS` above 31 is invalid per `smc.h`. Disconnect during pending path test changes `path_test` to `PT_EXITING`; mishandling this can incorrectly reinsert. Concentrator and SAS/DAS trace logic diverge under `CONCENTRATOR`.

## Test Signals
Cover connect/disconnect with and without bypass, DAS-only bypass insertion and deinsertion, `EC6_CHECK` success and stuck-bypass paths, trace initiated by MAC and each PHY, Trace_Max expiry causing path test, path-test pass/fail routing, PCM start/stop event fanout, remote disconnect event reporting, and timer cancellation when returning to `EC0_OUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ecm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ess.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ess.c

## Purpose
`ess.c` implements End Station Support for FDDI Synchronous Bandwidth Allocation RAF frames when `ESS` and non-`SLIM_SMT` are enabled. It receives allocation/change/report RAF frames, updates local synchronous bandwidth MIB state, sends RAF replies or requests, and reconfigures FORMAC TSYNC/FIFO layout.

## Important APIs, Types, And Functions
Public functions are `ess_raf_received_pack()`, `ess_timer_poll()`, and `ess_para_change()`. Internal helpers are `process_bw_alloc()`, `ess_send_response()`, `ess_send_alc_req()`, `ess_send_frame()`, and `ess_config_fifo()`. Static parameter lists validate required RAF parameters for allocation responses and change requests.

## Control Flow
Incoming RAF processing first checks resource type (`SMT_P0015`) and command (`SMT_P0016`). Allocation requests are processed only when local and no static ESS payload is configured; the frame is either returned to local SBA or copied and sent to the network. Allocation replies must pass `smt_check_para()`, primary-ring/resource/reason/TID checks, then `P320F`/`P3210` payload and overhead are applied through `process_bw_alloc()`. Change requests are accepted only as requests with valid path/resource parameters, then replied to if bandwidth update succeeds. Report requests return the current allocation.

`process_bw_alloc()` bounds payload and overhead, computes bytes per `T_NEG` (`sync_bw`), updates PATH SBA MIBs, configures FIFO, and writes FORMAC TSYNC. `ess_timer_poll()` periodically sends allocation requests until desired ESS static values match current path allocation.

## State And Persistence
ESS state is in `smc->ess` (`sync_bw_available`, `sync_bw`, `alloc_trans_id`, timer poll flags, pending local reply) and MIB fields (`fddiESSPayload`, `fddiESSOverhead`, `fddiPATHSbaPayload`, `fddiPATHSbaOverhead`). There is no disk persistence. Hardware-visible persistence is transient FORMAC TSYNC and FIFO split configuration.

## Dependencies And Integration Points
The file depends on SMT frame construction/parsing, `smt_p.h` RAF parameter IDs, `sba.h`/`sba_def.h` constants, `smt_send_frame()`, `smt_build_frame()`, `smt_get_mbuf()`, `smt_free_mbuf()`, FORMAC TSYNC/FIFO functions, MIB state, and optional local SBA handoff through `sba_reply_pend`.

## Risks And Edge Cases
Some parameter pointers in the change path are used after `smt_check_para()` without individual null checks. The allocation-request address validation checks only five of six address bytes. The bandwidth equation uses signed arithmetic and can produce negative TSYNC values intentionally; overflow or unit mistakes affect synchronous service. Reinitializing TX FIFO while traffic is active depends on `formac_reinit_tx()` being safe.

## Test Signals
Test malformed RAF frames, missing parameters, non-primary path, wrong resource type, wrong transaction ID, success and denied reason codes, payload zero deallocation, payload/overhead bounds, timer-driven allocation requests, local SBA pending reply handling, network reply sending, TSYNC register update, FIFO reinit when sync bandwidth first appears, and static ESS target convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/fplustm.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/fplustm.c

## Purpose
`fplustm.c` is the FORMAC+ tag-mode hardware driver. It initializes FORMAC/RBC memory and BMU queues, builds claim/beacon frames in adapter memory, manages ring-up/down and MAC interrupts, maintains MAC counters and multicast CAM state, controls receive modes, handles restricted-token monitoring, and supports ESS FIFO/TSYNC changes.

## Important APIs, Types, And Functions
Major entry points include `init_fplus()`, `mac_update_counter()`, `set_formac_tsync()`, `formac_tx_restart()`, `mac2_irq()`, `mac3_irq()`, `config_mux()`, `sm_mac_check_beacon_claim()`, `sm_ma_control()`, `sm_mac_get_tx_state()`, multicast functions, `mac_set_rx_mode()`, `rtm_irq()`, `rtm_set_timer()`, and `formac_reinit_tx()`. Internal setup helpers include `init_mac()`, `init_ram()`, `smt_split_up_fifo()`, `init_tx()`, `init_rx()`, `init_rbc()`, `build_claim_beacon()`, and `set_formac_addr()`.

## Control Flow
`init_fplus()` seeds default receive mode, group address, register pointers, counters, PCI fixups, then calls `init_mac(all=1)`. `init_mac()` places FORMAC in init/memory mode, optionally clears RBC RAM, splits FIFO space, initializes TX/RX queues and RBC pointers, builds claim/beacon/directed-beacon frames, programs thresholds, mode registers, timers, RTM, and BMU reset/repair for partial resets. Ring events in `mac2_irq()` update cached status, toggle receive/transmit through `mac_ring_up()`, and queue RMT events for ring op/non-op, beacons, claims, TRT expiry, duplicate address, and TX state changes. `sm_ma_control()` is the RMT-facing MAC command interface.

## State And Persistence
State is in `smc->hw.fp` (FIFO layout, receive mode, error stats, multicast table, FORMAC status shadows, queue pointers), `smc->hw.mac_ring_is_up`, MAC counters in `smc->mib.m[MAC0]`, and ESS TSYNC/FIFO flags. Hardware state persists only while the adapter is running: FORMAC registers, adapter buffer memory, CAM entries, BMU queues, and RTM timer.

## Dependencies And Integration Points
It depends on `supern_2.h` FORMAC bits, `skfbi.h` register access macros, Linux bit reversal and Ethernet address helpers, descriptor/queue types from `fplustm.h`, OS-specific descriptor repair/fill callbacks, LLC TX restart, SMT/RMT/CFM/ESS events, and hardware timer helpers.

## Risks And Edge Cases
Register sequencing and busy waits (`CHECK_NPP`, `CHECK_CAM`) are timing-sensitive. FIFO splitting assumes valid descriptor counts and exact 32 KB/64 KB FORMAC memory layout. Multicast accounting separates permanent SMT slots from OS slots and can leak counts if deletion support is added incorrectly. Receive mode changes rewrite hardware address filters immediately. Counter high-word handling depends on interrupts catching 16-bit hardware counter wrap.

## Test Signals
Validate full and partial MAC initialization, adapter RAM clearing, claim/beacon frame content, ring-up/down RMT events, duplicate-address handling, receive overflow counters, parity/error panic paths, TX restart after abort/lock, multicast add/clear/update including canonical conversion, promisc/allmulti/NSA modes, restricted token timer interrupt, ESS TSYNC/FIFO reinit, and descriptor repair after partial reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/fplustm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/cmtdef.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/cmtdef.h

## Purpose
`cmtdef.h` is the core SMT/CMT definition header. It fixes station sizing constants, event classes and event IDs, PCM/RMT/CFM/ECM state constants, mux/MAC control values, timer conversions, shared protocol structures, prototypes, debug macros, and SMT error identifiers.

## Important APIs, Types, And Functions
Important definitions include `NUMPHYS`, `NUMMACS`, `NUMPATHS`, port IDs (`PA`, `PB`, `PS`), policy bits, `EVENT_*`, `EV_TOKEN()` helpers, all `EC_*`, `CF_*`, `PC_*`, and `RM_*` events, path-test and duplicate-address enums, mux values, `MA_*` commands, entity bit helpers, `struct smt_timer`, `struct mac_parameter`, `struct mac_counter`, `struct s_pcon`, `struct lem_counter`, and `struct s_plc`. It also declares most cross-module functions.

## Control Flow
This header does not execute code, but it defines the control vocabulary for the dispatcher and all SMT state machines. Events are encoded as class/event tokens for timers and queue dispatch. State files such as `ecm.c`, `cfm.c`, PCM, RMT, SMT frame services, and FORMAC code use these constants to coordinate behavior.

## State And Persistence
It declares in-memory state types and constants only. The closest persistence boundary is the MIB/state enum compatibility comments: CFM values must match SMT specifications because they are reported externally in management frames.

## Dependencies And Integration Points
It includes `mbuf.h` and `smtstate.h` under normal builds and prototypes functions from hardware timer, SMT frame, PCM/RMT/CFM/ECM, PLC, FORMAC, PNMI, ESS/SBA, and OS-specific modules. Debug macros integrate with `struct smt_debug`.

## Risks And Edge Cases
Changing numeric event/state constants breaks wire-visible MIB values, dispatcher routing, timer tokens, and array indexing in implementation files. `NUMPHYS > 2` switches on `CONCENTRATOR`, changing structures and trace logic. Many prototypes are conditional and legacy-style; mismatched config macros can hide declarations.

## Test Signals
Build with normal DAS/SAS config, `CONC`/`CONC_II`, `ESS`, `SBA`, debug, and boot/slim variants. Runtime tests should verify queue dispatch by event class, timer token decode, state-machine transitions, debug macro compilation, and panic/error IDs in hardware error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/cmtdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddi.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddi.h

## Purpose
`fddi.h` defines the basic FDDI address and MAC frame layout plus frame-control and frame-status indicator constants shared by SMT, hardware, and OS-specific paths.

## Important APIs, Types, And Functions
The central types are `struct fddi_addr` and `struct fddi_mac`. Constants include FDDI frame sizes (`FDDI_MAC_SIZE`, `FDDI_RAW_MTU`, `FDDI_RAW`), FC values for SMT, MAC, claim, beacon, sync/async LLC, and indicator bits (`C_INDICATOR`, `A_INDICATOR`, `E_INDICATOR`, `I_INDICATOR`, `L_INDICATOR`).

## Control Flow
There is no executable flow. Consumers use FC constants to classify received frames, construct SMT/MAC special frames, select sync versus async transmit queues, and interpret local/network indicators from the receive frame status.

## State And Persistence
No state is stored here. The header defines wire-format shapes and constants that must match FDDI frame encoding.

## Dependencies And Integration Points
Included by `smc.h`, CFM/ECM/ESS/FORBMAC files, SMT frame definitions, and hardware modules. `fplustm.c` uses `FC_CLAIM`, `FC_BEACON`, and `DBEACON_INFO`; `ess.c` uses `FC_SMT_INFO` and local indicators.

## Risks And Edge Cases
`struct fddi_mac` omits the FC byte and stores only destination, source, and payload, while some FORMAC paths prepend FC separately. Confusing canonical versus FDDI bit order is a recurring risk because address storage is handled outside this header.

## Test Signals
Frame parsing/building tests should confirm FC classification, max frame sizing, beacon/claim construction, local indicator handling, sync-bit queue selection, and multicast/group address detection through `GROUP_ADDR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddimib.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddimib.h

## Purpose
`fddimib.h` defines the in-memory FDDI SMT MIB. It provides standard SMT, MAC, PATH, and PORT attributes plus private ESS/SBA and SysKonnect counters used by state machines, frame services, and management interfaces.

## Important APIs, Types, And Functions
It defines MIB scalar typedefs (`Counter`, `TimeStamp`, `Timer`, `SMTEnum`, `SMTFlag`), path and PMD enums, `SetCountType`, and `struct fddi_mib`. The MIB contains station identity/config/status, MAC array `m[NUMMACS]`, path array `a[NUMPATHS]`, port array `p[NUMPHYS]`, and private counters. It also defines statistic OIDs such as `SMT_OID_CF_STATE`, `SMT_OID_RMT_STATE`, and private ECF/PMF/RDF OIDs.

## Control Flow
The header has no code. CFM writes path/current placement/status fields, ECM writes ECM state and bypass flags, FORMAC updates MAC timers and counters, ESS writes SBA payload/overhead, and SMT/PMF code serializes these fields into management frames.

## State And Persistence
The `struct fddi_mib` instance inside `struct s_smc` is the driver’s authoritative runtime management state. It is not persisted to disk, but many fields mirror hardware state and are exposed externally through SMT frames or OS management APIs.

## Dependencies And Integration Points
It depends on `struct fddi_addr`, `struct smt_sid`, and sizing macros from `cmtdef.h`. It is included by `smc.h` and reached by nearly every SMT and hardware module.

## Risks And Edge Cases
Field units vary: FDDI timers often use 80 ns units, ESS payload uses bytes per 8000 bytes/s, and overhead uses bytes per `T_NEG`. Some fields are private shadows rather than directly standards-visible. Array sizes are compile-time, so concentrator builds alter structure footprint and serialization assumptions.

## Test Signals
Verify default MIB initialization, state updates from CFM/ECM/RMT/PCM, MAC counter wrap accounting, ESS payload/overhead reporting, SMT/PMF get/set serialization, OID lookup correctness, and multi-port builds with larger `NUMPHYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddimib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fplustm.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fplustm.h

## Purpose
`fplustm.h` defines FORMAC+ tag-mode descriptor, queue, FIFO, error, multicast, and receive-mode structures used by `fplustm.c` and OS-specific descriptor management.

## Important APIs, Types, And Functions
Important types are `struct err_st`, `struct s_smt_fp_txd`, `struct s_smt_fp_rxd`, `union s_fp_descr`, `struct s_smt_tx_queue`, `struct s_smt_rx_queue`, `struct s_smt_fifo_conf`, and `struct s_smt_fp`. Constants define special frame offsets, RBC memory size, FIFO split sizes, queue indices, multicast table limits, receive-mode commands, and endian conversion macros (`AIX_REVERSE`, `MDR_REVERSE`).

## Control Flow
The header provides data layout only. `fplustm.c` fills queue pointers, FIFO starts/sizes, CAM tables, error stats, and FORMAC status shadows from these definitions. OS-specific TX/RX paths use descriptor fields and queue state to hand buffers to BMUs.

## State And Persistence
`struct s_smt_fp` is embedded in hardware state and persists for the adapter lifetime. Descriptor rings and FIFO configuration are runtime state mirrored into hardware registers; multicast table entries are reprogrammed after reset.

## Dependencies And Integration Points
It requires OS-specific `struct s_txd_os` and `struct s_rxd_os` from `osdef1st.h`/target headers, FDDI address types, FORMAC bit definitions, and descriptor access macros in `hwmtm.h`.

## Risks And Edge Cases
Descriptor layout is ABI-sensitive for DMA and 64-bit address support. FIFO constants assume the adapter memory map used by FORMAC+. `AIX_REVERSE` is overloaded by Linux to perform little-endian conversion, so direct descriptor reads without the macros can break endian behavior.

## Test Signals
Compile-time structure size checks, TX/RX descriptor ring initialization, 64-bit descriptor builds, FIFO splits for sync and async traffic, multicast table saturation, receive mode toggles, and endian-correct descriptor ownership/length/address reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fplustm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/hwmtm.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/hwmtm.h

## Purpose
`hwmtm.h` defines the hardware-module abstraction for SMT mbuf pools, receive/transmit queues, OS-visible descriptor accessor macros, DMA sync placeholders, receive pass modes, frame status bits, debug hooks, and HWM error IDs.

## Important APIs, Types, And Functions
Key types are `struct s_mbuf_pool`, `struct hwm_r`, and `struct hw_modul`. Important macros include `HWM_GET_TX_PHYS()`, `HWM_GET_TX_LEN()`, `HWM_GET_TX_USED()`, `HWM_GET_CURR_TXD()`, `HWM_GET_RX_FRAG_LEN()`, `HWM_GET_RX_PHYS()`, `HWM_GET_RX_USED()`, `HWM_GET_RX_FREE()`, `HWM_GET_CURR_RXD()`, and `HWM_RX_CHECK()`.

## Control Flow
No code runs here, but OS-specific driver paths use these macros to inspect current descriptor positions, refill RX rings at low-water thresholds, track queued LLC/SMT mbufs, and decide whether frames are local, LAN-bound, first/last fragments, or failed due to ring/descriptor shortage.

## State And Persistence
`struct hw_modul` is runtime state under `smc->hw`: mbuf pool, descriptor base pointer, receive pass flags, RX/TX queues, ISR flags, current TX frame cursor, and error counters. It is rebuilt on driver init and reset.

## Dependencies And Integration Points
It includes `mbuf.h` and relies on descriptor types from `fplustm.h`, endian macros, OS-specific DMA synchronization, and `mac_drv_fill_rxd()` provided outside this header.

## Risks And Edge Cases
`DRV_BUF_FLUSH()` defaults to a no-op unless the OS layer overrides it; DMA coherency depends on the target integration. `HWM_GET_RX_FREE()` subtracts one descriptor for an ASIC workaround, so callers must not “fix” the apparent off-by-one. `HWM_RX_CHECK()` expands to code and depends on a valid `smc` expression.

## Test Signals
Descriptor accessor unit tests, RX low-water refill behavior, DMA sync override compilation, local/SMT/LAN frame status handling, no-buffer and out-of-TxD paths, ISR entry/exit state, and build checks for HWM error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/hwmtm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/mbuf.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/mbuf.h

## Purpose
`mbuf.h` defines the small SMT mbuf abstraction used for internal SMT/RAF/management frames independent of Linux `sk_buff` data paths.

## Important APIs, Types, And Functions
It defines `M_SIZE`, `MAX_MBUF`, `struct s_mbuf`, typedef `SMbuf`, compatibility aliases (`sm_next`, `sm_off`, `sm_len`, `sm_data`, `SMbuf`, `mtod`, `mtodoff`), and pointer conversion macros `smtod()` and `smtodoff()`.

## Control Flow
No code executes here. SMT builders allocate an `SMbuf`, set offset and length, write a typed frame with `smtod()`, and transmit or free it through SMT/HWM functions.

## State And Persistence
Each mbuf stores next pointer, data offset, length, optional PCI use count, and a fixed 4504-byte data buffer. Pools live in HWM state or outside `smc` when configured.

## Dependencies And Integration Points
Used by SMT frame construction, ESS RAF handling, HWM mbuf pools, and TX/RX queues. It depends on base integer types from `types.h`.

## Risks And Edge Cases
The fixed buffer size must cover maximum SMT/FDDI management frames. `smtod()` trusts `sm_off` and requested type alignment. `NO_STD_MBUF` changes compatibility aliases and can affect legacy code.

## Test Signals
Allocate/free pool behavior, SMT frame construction at max sizes, offset handling, PCI use-count behavior, and typed access with aligned `struct smt_header`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/mbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/osdef1st.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/osdef1st.h

## Purpose
`osdef1st.h` supplies Linux-specific definitions that must be visible before the generic SysKonnect headers: endian selection, feature macros, descriptor counts, SMT buffer counts, OS-specific descriptor payloads, panic logging, and byte-order conversion shims.

## Important APIs, Types, And Functions
Important macros include `LITTLE_ENDIAN`/`BIG_ENDIAN`, `USE_CAN_ADDR`, `MB_OUTSIDE_SMC`, `SYNC`, `ESS`, `SMT_PANIC`, `NUM_RECEIVE_BUFFERS`, `NUM_TRANSMIT_BUFFERS`, `NUM_SMT_BUF`, `HWM_ASYNC_TXD_COUNT`, `HWM_SYNC_TXD_COUNT`, `SMT_R1_RXD_COUNT`, `SMT_R2_RXD_COUNT`, `AIX_REVERSE`, and `MDR_REVERSE`. It defines `struct s_txd_os` and `struct s_rxd_os` with `sk_buff *` and `dma_addr_t`.

## Control Flow
The header gates compile-time behavior. Enabling `ESS` brings in ESS code and MIB fields; disabling `SBA` excludes allocator source; descriptor counts determine FIFO split and ring initialization behavior.

## State And Persistence
Descriptor OS extensions hold per-buffer Linux skb and DMA mapping addresses for runtime unmap/free operations. No state is persisted beyond driver lifetime.

## Dependencies And Integration Points
It depends on Linux byteorder, `sk_buff`, DMA address types, and kernel logging. It is pulled in by `smc.h` when `PCI` requires `OSDEF`.

## Risks And Edge Cases
Structure-size rules in comments are important for descriptor alignment. Changing RX/TX buffer counts affects hardware ring sizing and the ASIC workaround extra RXD. `SMT_PANIC` only logs at info level here, so fatal generic-driver paths may not stop execution by themselves.

## Test Signals
Build on little- and big-endian configurations if supported, descriptor size/alignment checks, DMA map/unmap paths using `s_txd_os`/`s_rxd_os`, ESS-enabled compilation, and RX/TX ring count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/osdef1st.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba.h

## Purpose
`sba.h` declares Synchronous Bandwidth Allocation state when the optional full SBA allocator is enabled and always declares ESS runtime state used by `ess.c`.

## Important APIs, Types, And Functions
Under `SBA`, it defines `struct timer_cell`, `struct s_sba_node_vars`, `struct s_sba_sessions`, and `struct s_sba` for nodes, sessions, timers, received RAF message fields, allocator totals, and SBA state machine variables. Always-relevant `struct s_ess` stores ESS flags, timer state, pending local reply, `sync_bw`, and `alloc_trans_id`.

## Control Flow
The full SBA structs support allocator state machines outside this subset. ESS uses `struct s_ess` for timer polling, local SBA reply handoff, and matching allocation responses by transaction ID.

## State And Persistence
All state is in-memory under `struct s_smc`. SBA session/node arrays and ESS allocation values are reset with the adapter and are not persisted to disk.

## Dependencies And Integration Points
It includes `mbuf.h` and `sba_def.h`, references SMT headers and FDDI addresses, and is included by `smc.h` when `ESS` is enabled.

## Risks And Edge Cases
`SBA` is disabled in the Linux config comments, so only ESS is commonly compiled; stale full-SBA declarations can drift from unavailable implementation code. Fixed `MAX_NODES`/`MAX_SESSIONS` arrays can cap allocator scale.

## Test Signals
ESS builds without `SBA`, optional SBA builds where available, local SBA pending reply behavior, allocation response TID tracking, and session/node array initialization in full allocator configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba_def.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba_def.h

## Purpose
`sba_def.h` provides constants for ESS/SBA bandwidth allocation, RAF command inputs, default overhead, payload/path limits, and optional full-SBA states and status values.

## Important APIs, Types, And Functions
Common constants include `PHYS`, `PERM_ADDR`, `SB_STATIC`, `MAX_PAYLOAD`, `PRIMARY_RING`, `UNKNOWN_SYNC_SOURCE`, `REQ_ALLOCATION`, `REPORT_RESP`, `CHANGE_RESP`, `TNEG`, `NIF`, `SB_STOP`, `SB_START`, `REPORT_TIMER`, `CHANGE_REQUIRED`, and `DEFAULT_OV`. Under `SBA`, it defines allocator states, capacities, timers, node/session limits, and deallocation flags.

## Control Flow
There is no code. `ess.c` uses `MAX_PAYLOAD`, `PRIMARY_RING`, and `DEFAULT_OV` to validate and build RAF allocation behavior.

## State And Persistence
No runtime state is declared. Constants define accepted wire/protocol values and allocator bounds.

## Dependencies And Integration Points
Included by `sba.h` and indirectly by `smc.h`/`ess.c`. Values must match the Synchronous Bandwidth Allocation Implementer's Agreement and SMT RAF parameter handling.

## Risks And Edge Cases
`MAX_PAYLOAD` and `DEFAULT_OV` are protocol policy values; changing them can make RAF negotiation incompatible. `PRIMARY_RING` is encoded as a 32-bit value while some RAF fields are swapped specially in `smt.h`.

## Test Signals
ESS allocation bounds, primary-ring filtering, default overhead when static payload is set, zero-payload deallocation, and optional full-SBA state transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbi.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbi.h

## Purpose
`skfbi.h` defines the PCI FDDI adapter register map, interrupt bits, BMU control/status bits, address translation macros, FORMAC/PLC register access helpers, timer bits, descriptor control bits, and low-level I/O macros used by board and FORMAC code.

## Important APIs, Types, And Functions
Major groups include banked register offsets (`B0_*` through `B6_*`), control bits (`CTRL_*`, `DAS_*`, `LED_*`, `TIM_*`), interrupt source/mask bits (`IS_*`, `IRQ_*`, `ALL_IRSR*`), BMU reset/start bits (`CSR_*`), descriptor flags (`BMU_OWN`, `BMU_STF`, `BMU_EOF`, `BMU_BBC`), address helpers (`ADDR`, `ADDRS`, `PCI_C`, `FM_A`, `PLC`, `GET_ISR`), interrupt mask helpers, `MARW`, `MARR`, `MDRW`, and `GET_ST*`.

## Control Flow
This header is macro-only but controls every hardware access path. Board reset uses `B0_CTRL`, `B0_DAS`, LEDs, PCI config, and masks. FORMAC code uses `FM_A`, `MARW`, `MDRW`, and status registers. ISR code uses `GET_ISR()` and masks.

## State And Persistence
No C state is declared, but macros read and write persistent device registers, EEPROM/PROM windows, timers, BMU descriptors, and adapter memory while powered.

## Dependencies And Integration Points
It depends on `PCI`, optional memory-mapped I/O, low-level `inp/outp/inpw/outpw/inpd/outpd`, and FORMAC/PLC constants from `supern_2.h`. Included by `drvfbi.c`, `fplustm.c`, and hardware modules.

## Risks And Edge Cases
`ADDR()` changes the RAP bank register as a side effect, so concurrent or reordered register access can hit the wrong bank. Memory-mapped and I/O-port modes differ. Interrupt mask constants differ for adapter variants. BMU reset/start sequencing is hardware-sensitive.

## Test Signals
Register access smoke tests, bank switching across high offsets, interrupt mask setup, reset control sequencing, DAS/bypass and LED writes, BMU reset/clear/start, descriptor ownership flags, FORMAC MDR writes, and ISR source decoding on Da Vinci versus Monalisa-style hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbiinc.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbiinc.h

## Purpose
`skfbiinc.h` provides assembler-friendly and shared include definitions for the FBI hardware layer: interrupt masks, FORMAC physical register aliases, transfer modes, and default empty driver callback hooks.

## Important APIs, Types, And Functions
Important definitions are `ERR_FLAGS`, `IMASK_FAST`, `ISR_MASK`, `FMA_FM_*` aliases, transfer mode aliases (`TMODE_RRQ`, `TMODE_WAQ0`, `TMODE_WAQ2`, `TMODE_WSQ`), `HSRA`, and default `DRV_PCM_STATE_CHANGE()`/`DRV_RMT_INDICATION()` macros.

## Control Flow
`drvfbi.c` uses `ISR_MASK` during `card_start()` to initialize board interrupts. Optional platform code can override the driver callback macros to receive PCM/RMT notifications.

## State And Persistence
No state is declared. Interrupt mask constants are written into `smc->hw.is_imask` and hardware interrupt mask registers.

## Dependencies And Integration Points
It includes `supern_2.h` and uses `skfbi.h` address macros such as `FMA()`. It is included by board-dependent driver code and legacy assembly-oriented paths.

## Risks And Edge Cases
Mask definitions must include all fast interrupt sources required by timer, RTM, PLC, MAC, RX, and TX error handling. Missing a bit can silently suppress state-machine progress. Default empty callbacks can hide OS integration if an expected override is absent.

## Test Signals
Interrupt mask validation during init, callback override builds, assembler/include consumers, and ISR coverage for timer, token, PLC, MAC, RX parity/encoding, and TX encoding sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbiinc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smc.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smc.h

## Purpose
`smc.h` is the central context header for the SysKonnect SMT driver. It pulls target, protocol, MIB, hardware, OS, and ESS/SBA headers together and defines `struct s_smc`, the shared state block used by all SMT and hardware modules.

## Important APIs, Types, And Functions
It defines event queue structures, module state structs (`s_ecm`, `s_rmt`, `s_cfm`, `s_pcm`, `s_phy`, `s_timer`, `s_srf`, `s_srf_evc`, `smt_values`, `smt_config`, optional debug), ring-status bits and `RS_SET`/`RS_CLEAR`, station attach types (`SMT_DAS`, `SMT_SAS`, `SMT_NAC`), and the aggregate `struct s_smc`. It also declares board and interrupt entry points such as `init_board()`, `init_fplus()`, `mac*_irq()`, `plc*_irq()`, and `timer_irq()`.

## Control Flow
The header itself has no code, but its structures define the runtime graph. State machines share one `struct s_smc`; events move through `struct s_queue`; timers use `struct s_timer`; hardware and OS state must be the first fields because default initialization zeroes everything after `hw`.

## State And Persistence
`struct s_smc` contains all runtime state: OS and hardware state, configuration constants, SMT values, ECM/RMT/CFM/PCM/PHY state, event queue, timers, SRF data, MIB, and optional ESS/SBA/debug state. Nothing here is disk-persistent, but much of the MIB is externally reported and must remain coherent.

## Dependencies And Integration Points
It conditionally includes `osdef1st.h`, `smt.h`, `cmtdef.h`, `fddimib.h`, `targethw.h`, `targetos.h`, and `sba.h`. Every C file in this subset includes it directly or indirectly.

## Risks And Edge Cases
The field-order comment for `os` and `hw` is a hard initialization contract. `NUMPHYS` changes affect array sizes, trace bitmaps, event queue size, and MIB serialization. Ring status macros invoke callbacks as side effects. Conditional compilation can materially change structure layout.

## Test Signals
Initialization/default reset of `struct s_smc`, build variants for PCI/TAG_MODE/SUPERNET_3/ESS/CONCENTRATOR/debug, event queue wraparound, timer list behavior, ring-status callbacks, MIB pointer setup for each PHY, and state-machine interactions sharing one context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt.h

## Purpose
`smt.h` defines SMT 7.2 frame headers, parameter structures, class/type constants, reason codes, SBA/RAF frame layouts, notification parameters, and station/port action constants.

## Important APIs, Types, And Functions
Important types are `struct smt_header`, `struct smt_para`, `struct smt_sid`, many `struct smt_p_*` parameter layouts, `struct smt_nif`, `struct smt_sif_config`, `struct smt_sif_operation`, `struct smt_ecf`, `struct smt_rdf`, and SBA RAF frame structs. Constants define SMT versions, classes (`SMT_NIF`, `SMT_RAF`, `SMT_PMF_GET`, etc.), request/reply types, parameter IDs, reason codes, sync-bandwidth commands, and swap strings.

## Control Flow
No code runs here. SMT frame builders allocate an `SMbuf`, lay out `struct smt_header` and parameters, set `p_type`/`p_len`, and send it. Parsers use parameter IDs and lengths to locate fields and optionally byte-swap based on the `SWAP_*` strings.

## State And Persistence
The header declares wire-format data only. These structs become transmitted management frames and therefore form a persistent protocol ABI with other FDDI stations.

## Dependencies And Integration Points
It depends on FDDI address types and packing macros from platform headers. `ess.c` uses RAF frame structures; SMT core and PMF/SRF code use NIF/SIF/RDF/notification parameter layouts; MIB code maps fields into these structures.

## Risks And Edge Cases
Alignment is explicitly documented: `struct smt_header` must be 32 bytes and parameters long-aligned. Flexible or variable-size parameter tails require careful length handling. `SBAPATHINDEX` is endian-specific to avoid double swapping RAF path indexes.

## Test Signals
Serialize/parse NIF, SIF config/operation, ECF, RDF, RAF allocation/change/report frames; verify parameter lengths, swap strings, endian behavior, maximum echo/info lengths, and refusal/reason code generation for unsupported or malformed frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt_p.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt_p.h

## Purpose
`smt_p.h` is a generated-style list of SMT attribute and parameter identifiers used by PMF, RAF, ESS/SBA, SRF, and management code.

## Important APIs, Types, And Functions
The file defines hundreds of `SMT_Pxxxx` constants, including base reason/resource/SBA parameters (`SMT_P0012`, `SMT_P0015` through `SMT_P001D`), station/MAC/PORT/PATH MIB parameters in the `0x1000`, `0x2000`, `0x3200`, and `0x4000` ranges, and ESS/SBA-conditional parameters.

## Control Flow
There is no executable logic. Code passes these IDs to helpers such as `sm_to_para()`, `smt_check_para()`, PMF get/set dispatch, and RAF validation lists.

## State And Persistence
No state is declared. Numeric values are protocol-visible identifiers and must remain stable.

## Dependencies And Integration Points
Included by `ess.c` and management/SMT modules. Conditional `ESS` and `SBA` blocks must match enabled MIB fields and frame layouts.

## Risks And Edge Cases
Because the file is just constants, typos or duplicate values compile but break parameter lookup. Conditional IDs can disappear under different build flags while source code still references them if guards are inconsistent.

## Test Signals
Compile all feature variants, verify PMF/RAF parameter lookup tables, malformed-frame handling for missing IDs, and management get/set coverage for station, MAC, path, port, ESS, and SBA attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt_p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smtstate.h -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smtstate.h

## Purpose
`smtstate.h` defines SMT state constants for PCM, port modes/types, CFM, ECM, and RMT when not building kernel internals, plus compact snapshot structures for reporting PCM state.

## Important APIs, Types, And Functions
Constants include `PC0_OFF` through `PC9_MAINT`, `PM_*`, `TA`/`TB`/`TS`/`TM`/`TNONE`, CFM states (`SC0_ISOLATED`, `SC4_THRU_A`, etc.), ECM states (`EC0_OUT` through `EC7_DEINSERT`), and RMT states (`RM0_ISOLATED` through `RM7_TRACE`). Runtime report types are `struct pcm_state` and `struct smt_state`.

## Control Flow
No executable code is present. CFM and ECM include it with `KERNEL` defined, so they rely on `cmtdef.h` values instead of duplicate non-kernel constants. State-reporting code uses `struct smt_state` snapshots.

## State And Persistence
The structs are transient snapshots of PCM state for all PHYs: type, state, mode, neighbor, flags, line-state receive value, and signaling bits. Numeric constants are externally meaningful state IDs.

## Dependencies And Integration Points
It depends on `NUMPHYS` from `cmtdef.h` when declaring `struct smt_state`. Included by `cmtdef.h` and state-machine/reporting code.

## Risks And Edge Cases
Duplicate state constants must stay aligned with `cmtdef.h` and SMT MIB values. `KERNEL` changes which constants are visible, so include order matters. `struct pcm_state` uses narrow fields and can truncate if future values exceed current ranges.

## Test Signals
Build with and without `KERNEL`, PCM snapshot generation, state-name mapping in CFM/ECM/RMT/PCM diagnostics, and MIB/report consumers expecting standard numeric state values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smtstate.h -->
