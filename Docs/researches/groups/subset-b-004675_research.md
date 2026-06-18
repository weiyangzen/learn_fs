# subset-b-004675 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/skfddi.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/skfddi.c

## Purpose
`skfddi.c` is the Linux PCI/netdevice adapter layer for SysKonnect SK-55xx/SK-58xx FDDI adapters. It binds the old SysKonnect hardware module and SMT/CMT stack to Linux PCI probing, IRQ handling, DMA allocation, `struct net_device` operations, FDDI receive/transmit framing, multicast filtering, statistics, and private ioctl handling.

## Important APIs and Functions
The PCI surface is `skfp_init_one()`, `skfp_remove_one()`, `skfddi_pci_tbl`, and `module_pci_driver()`. The netdevice surface is `skfp_netdev_ops`, with `skfp_open()`, `skfp_close()`, `skfp_send_pkt()`, `skfp_ctl_get_stats()`, `skfp_ctl_set_multicast_list()`, `skfp_ctl_set_mac_address()`, and `skfp_siocdevprivate()`. Hardware-module callbacks include `mac_drv_get_space()`, `mac_drv_get_desc_mem()`, `mac_drv_virt2phys()`, `dma_master()`, `dma_complete()`, `mac_drv_tx_complete()`, `llc_restart_tx()`, `mac_drv_rx_complete()`, `mac_drv_requeue_rxd()`, `mac_drv_fill_rxd()`, `mac_drv_clear_rxd()`, and `mac_drv_rx_init()`. State indications are surfaced through `ring_status_indication()`, `smt_stat_counter()`, `cfm_state_change()`, `ecm_state_change()`, `rmt_state_change()`, and `drv_reset_indication()`.

## Control Flow
Probe enables the PCI device, requests BARs, maps MMIO or PIO space, allocates an FDDI netdev with `struct s_smc` private data, initializes queues and bus metadata, calls `skfp_driver_init()`, then registers the netdev. Driver initialization allocates a coherent local RX fallback buffer and hardware-module shared memory, stops the card, runs `mac_drv_init()`, reads the adapter address, sets `dev_addr`, and seeds SMT defaults. Opening requests the shared IRQ, restores the factory address, initializes SMT via `init_smt()`, brings SMT online, enables adapter interrupts, clears multicast filters, disables promiscuous mode, and starts the queue. Closing disables adapter interrupts, resets SMT defaults, stops the card, clears hardware queues, stops TX, frees the IRQ, and purges queued SKBs.

TX enqueues valid FDDI LLC frames into `SendSkbQueue`; `send_queued_packets()` selects async/sync queue from the frame-control byte, asks the hardware module for TX descriptors, patches missing source addresses, maps the SKB for DMA, and hands the fragment to `hwm_tx_frag()`. TX completion unmaps DMA, updates stats, and frees the SKB. RX completion expects one fragment, uses DMA already unmapped by `dma_complete()`, removes any routing information field, updates stats, translates the FDDI header with `fddi_type_trans()`, and injects the SKB with `netif_rx()`.

## State, Dependencies, and Integration
Persistent runtime state lives in `smc->os`: coherent shared memory heap, local RX fallback, `SendSkbQueue`, queue credit counter, netdev pointer, PCI device copy, driver lock, statistics, and reset flag. It depends heavily on the SysKonnect hardware/SMT headers under `h/` plus Linux PCI, DMA, FDDI, SKB, netdevice, and capability APIs. IRQs call `fddi_isr()` under `DriverLock`; hardware callbacks may temporarily drop/reacquire the lock around queued TX.

## Risks and Test Signals
High-risk areas are DMA lifecycle correctness, lock ordering around `llc_restart_tx()`, RX RIF removal, reset from interrupt context via `ResetRequested`, private ioctl user-copy handling, and fallback RX buffers shared by multiple descriptors. Compile coverage should catch API signature drift; runtime tests need PCI probe/open/close, IRQ sharing, TX under descriptor exhaustion, RX with and without RIF, multicast/allmulti/promisc changes, MAC address reset, and ioctl stats/clear permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/skfddi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smt.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smt.c

## Purpose
`smt.c` implements the FDDI Station Management (SMT) frame manager. It builds, sends, receives, validates, byte-swaps, and reacts to SMT NIF, SIF, ECF, RDF, SRF, PMF, and related frames while maintaining neighbor discovery, duplicate-address state, counters, timestamps, token-count emulation, and state-machine actions.

## Important APIs and Functions
Initialization and periodic work are `smt_agent_init()`, `smt_agent_task()`, `smt_event()`, and optional `smt_emulate_token_ct()`. Frame ingress is `smt_received_pack()`, which dispatches by SMT class and type. Frame egress helpers include `smt_send_frame()`, `smt_build_frame()`, `smt_send_rdf()`, `smt_send_nif()`, `smt_send_ecf()`, `smt_send_sif_config()`, and `smt_send_sif_operation()`. Parameter helpers include many `smt_fill_*()` functions, `smt_check_para()`, `sm_to_para()`, `smt_swap_para()`, `smt_get_tid()`, and `smt_set_timestamp()`. Management action dispatch is `smt_action()`.

## Control Flow
`smt_agent_init()` derives the SMT address from hardware, builds the station ID from the burned-in address, resets pending transaction IDs, clears UNA/DNA state, and initializes duplicate-address flags. `smt_event()` is periodically driven by the timer package: it services reconnect countdowns, driver cleanup/watchdog hooks, SRF polling, LEM/error-ratio evaluation, periodic NIF announcements, UNA/DNA expiry, and token counter emulation before rescheduling its timer.

On receive, `smt_received_pack()` filters by frame-control value, destination address, NSA/A-indicator rules, SMT version, and length; it swaps parameters into host order on little-endian systems. NIF requests update upstream neighbor and duplicate-address indicators and may trigger NIF replies. NIF replies validate transaction IDs, update downstream neighbor and duplicate-address results, and queue RMT duplicate-address events. SIF requests generate configuration or operation responses. ECF requests echo back data, while ECF replies validate pending echo tests. Unsupported or invalid request classes get RDF responses.

## State, Dependencies, and Integration
The file mutates `smc->mib`, `smc->sm`, `smc->r`, and related state-machine fields. It depends on SMT parameter definitions in `h/smt_p.h`, FDDI address constants, the event queue, PCM/ECM/CFM/RMT state machines, SRF (`smt_srf_event()`), PMF (`smt_pmf_received_pack()`), optional ESS/SBA hooks, and the lower SMT buffer send path (`smt_send_mbuf()`). Transaction state is in `smc->sm.pend[]`; neighbor timestamps are `smt_tvu` and `smt_tvd`; duplicate-address conditions are represented in MIB flags and RMT events.

## Risks and Test Signals
Risks include untrusted frame length and parameter parsing, endian conversion table coverage, neighbor/duplicate-address state races, optional feature ifdefs, and frame construction length accounting. Test signals should include NIF announce/request/reply flows, duplicate-address A-indicator handling, SIF config/operation replies, ECF echo request/reply, malformed length/version RDF generation, PMF dispatch, little-endian swap round trips, and timeout-driven UNA/DNA expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtdef.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtdef.c

## Purpose
`smtdef.c` centralizes default SMT/CMT configuration and MIB initialization for the SysKonnect FDDI stack. It seeds station, MAC, path, and port attributes, operational timer values, policy defaults, link error thresholds, and MAC operational values used by later SMT initialization and state machines.

## Important APIs and Functions
The public functions are `smt_reset_defaults()`, `smt_set_mac_opvalues()`, and `smt_fixup_mib()`. Internal helpers are `smt_init_mib()` and `set_min_max()`. Compile-time constants define microsecond/millisecond/second defaults for PCM, ECM, RMT, MAC, LCT, LEM, polling, and path-test behavior.

## Control Flow
`smt_reset_defaults()` calls `smt_init_mib()`, records `SMC_VERSION`, initializes token emulation timestamps from `smt_get_time()`, and sets the `smc->s` configuration block for DAS defaults, number of PHYs, PCM timers, ECM timers, RMT timers, MAC limits, and LCT thresholds. Optional ESS/SBA/TAG_MODE sections reset feature-specific state at cold-start or reset level.

`smt_init_mib()` zeroes the non-OS/non-hardware portion of `struct s_smc` on level 0, or clears selected transient SMT flags on later resets. It then fills station version/manufacturer/user data, station policies, available paths, notification/report settings, MAC indexes and timers, path bounds, and port attributes. It deliberately leaves PHY MIB pointers for `init_smt()` phase two and ends by applying MAC operational values.

`smt_set_mac_opvalues()` reconciles requested MIB values with path lower bounds using two's-complement FDDI timer representations, emits an AIX remote T-Req event when T-Req changes, and returns whether any operational value changed. `smt_fixup_mib()` finalizes master/non-master counts after the SAS/DAS/NAC mode is known.

## State, Dependencies, and Integration
The file persists defaults into `smc->mib`, `smc->s`, `smc->sm.last_tok_time[]`, optional `smc->ess`, and optional hardware tag fields. It is called by `skfddi.c` during driver initialization and reset, and by `smtinit.c` before hardware/state-machine startup. It depends on FDDI MIB layouts and event macros such as `AIX_EVENT()`.

## Risks and Test Signals
The main risk is reset-level semantics: level 0 wipes most of `struct s_smc`, while later levels preserve selected state. Timer values are negative two's-complement BCLK values, so boundary comparisons are easy to regress. Tests should verify cold reset versus warm reset MIB preservation, default MAC/path/port values, SAS/DAS master-count fixups, operational timer clamping, and expected T-Req change events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtdef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtinit.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtinit.c

## Purpose
`smtinit.c` sequences full SMT subsystem initialization after defaults and hardware resources are available. It connects MIB port pointers, applies OEM policy quirks, initializes the hardware driver, event/timer packages, SMT agent, and all FDDI state machines.

## Important APIs and Functions
The exported entry point is `init_smt(struct s_smc *smc, const u_char *mac_addr)`. It calls external or cross-module functions including `init_fddi_driver()`, `smt_set_mac_opvalues()`, `smt_fixup_mib()`, `ev_init()`, `smt_init_evc()`, `smt_timer_init()`, `smt_agent_init()`, `pcm_init()`, `ecm_init()`, `cfm_init()`, `rmt_init()`, `pcm()`, `ecm()`, `cfm()`, `rmt()`, `smt_agent_task()`, and `PNMI_INIT()`. `set_oem_spec_val()` is the local OEM customization helper.

## Control Flow
`init_smt()` first resets debug masks when built with global debug support. It then wires each `smc->y[p].mib` pointer to `smc->mib.p[p]`, because `smtdef.c` intentionally leaves those pointers unset during raw MIB initialization. `set_oem_spec_val()` applies an IBM OEM marker rule by restricting the connection policy to `POLICY_MM`. MAC operational timer values are recalculated before the hardware driver is initialized with the optional canonical MAC override.

After hardware setup, `smt_fixup_mib()` updates counts that depend on station attachment mode. The function then initializes event queues, SRF event-control blocks, timers, the SMT frame agent, PCM, ECM, CFM, and RMT. It explicitly kicks each state machine once so initial states are materialized, starts the SMT agent periodic NIF/timer flow, and initializes PNMI.

## State, Dependencies, and Integration
This file is the bridge from netdev open/reset paths into the SysKonnect SMT core. It depends on defaults from `smtdef.c`, EVC logic from `srf.c`, timer services from `smttimer.c`, the hardware driver, and the PCM/ECM/CFM/RMT modules. It mutates MIB pointers, OEM-dependent connection policy, state-machine internals, and timer/event queues.

## Risks and Test Signals
Initialization order is the central risk: hardware, MIB pointers, EVCs, timers, and state machines all assume earlier steps have completed. Tests should assert that every PHY MIB pointer is valid, IBM OEM policy overrides apply only when expected, state machines can be initialized from both open and reset paths, and repeated `init_smt()` calls after `smt_reset_defaults(level=1)` do not retain stale event/timer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smttimer.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smttimer.c

## Purpose
`smttimer.c` implements the SMT timer queue used by the FDDI state machines and SMT agent. It multiplexes many logical `struct smt_timer` objects onto the hardware timer hooks `hwt_start()`, `hwt_stop()`, and `hwt_read()` using a delta-ordered linked list.

## Important APIs and Functions
The public timer API is `smt_timer_init()`, `smt_timer_stop()`, `smt_timer_start()`, `smt_force_irq()`, and `smt_timer_done()`. The internal engine is `timer_done(struct s_smc *smc, int restart)`. Expired timers are delivered through `timer_event(smc, token)`.

## Control Flow
Initialization clears the queue and fast timer state, then initializes the hardware timer. Starting a timer converts microseconds to 16 microsecond hardware ticks, clamps zero to one tick, removes any existing instance of the same timer, stores the token and owning SMC, then inserts it into the delta list. If the queue was empty, the hardware timer is started directly; otherwise `timer_done(..., restart=0)` first accounts for elapsed ticks so insertion is relative to current time.

Stopping a timer marks it inactive, unlinks it from the delta queue, repairs the next timer's delta by adding the removed delta, and stops the hardware timer if the removed timer was the only queued timer. `smt_force_irq()` schedules the special fast timer after 32 microseconds with an `SM_FAST` token. When the hardware timer expires, `smt_timer_done()` calls `timer_done(..., restart=1)`, which reads elapsed ticks, detaches all expired timers, delivers their tokens, and restarts the hardware timer for the next queued delta.

## State, Dependencies, and Integration
State lives in `smc->t.st_queue` and `smc->t.st_fast`, plus the per-timer `tm_active`, `tm_next`, `tm_delta`, `tm_token`, and `tm_smc` fields. The module integrates with SMT event dispatch, state-machine timers, and hardware-specific timer primitives.

## Risks and Test Signals
Risks are delta-list corruption, double-start/double-stop behavior, elapsed-time correction before insertion, and reentrant timer callbacks that mutate the queue. Tests should cover inserting before/middle/after existing timers, stopping head/middle/tail timers, stopping the only timer, forced fast IRQ delivery, multiple expirations in one hardware tick, and callback-driven timer restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smttimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/srf.c -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/srf.c

## Purpose
`srf.c` implements FDDI SMT 7.2 Status Report Frame handling. It maps MIB conditions/events to event-control blocks, rate-limits report generation with the SR0/SR1/SR2 state machine, builds SRF announce frames, and clears report-required state after successful reporting.

## Important APIs and Functions
The public functions are `smt_init_evc()` and `smt_srf_event()`. Internal helpers are `smt_get_evc()`, `clear_all_rep()`, `clear_reported()`, and `smt_send_srf()`. Static `evc_inits[]` defines supported SMT/MAC/PORT conditions and events and maps them to SMT parameter IDs such as `SMT_P208C`, `SMT_P4050`, and `SMT_P4053`.

## Control Flow
`smt_init_evc()` clears `smc->evcs`, expands the initializer table by index count, assigns code/parameter/index fields, and then binds condition or multiple-event pointers to the relevant MIB fields. It initializes SRF timing (`TSR`) and puts the SRF state machine in `SR0_WAIT`.

`smt_srf_event()` is called with a code, index, and condition state. For conditions, unchanged state is ignored; asserted conditions set the MIB condition bit, mark the EVC report-required, and set `any_report`; deassertions clear the MIB bit. For events, repeated events set the corresponding "multiple" MIB flag while first events mark the EVC report-required. The function records transition timestamps, optionally reports to SNMP, then applies the SRF rate-limiting state machine: immediate report after the threshold window, holdoff inside the two-second window, exponential re-report threshold up to 32 seconds, and disabled state when `fddiSMTStatRptPolicy` is false.

`smt_send_srf()` builds an SMT SRF announce to the SRF multicast destination, adds timestamp/status parameters and all required event parameters, sends it through `smt_send_frame()`, and calls `clear_reported()`.

## State, Dependencies, and Integration
State is in `smc->evcs[]`, `smc->srf`, and MIB condition/multiple fields. The module depends on SMT frame building/sending, SMT parameter construction (`smt_add_para()`), ring-status macros, timestamps, and optional SNMP hooks. It is initialized by `init_smt()` and driven by `smt_event()` and other SMT/MAC/PORT modules.

## Risks and Test Signals
Risks include EVC table capacity assumptions, pointer binding correctness, threshold/holdoff timing, disabled-policy transitions, and parameter buffer length handling in `smt_send_srf()`. Tests should assert each supported code/index maps to the right MIB field, condition assert/deassert behavior, event multiple flags, policy disable/enable clearing, SRF exponential backoff, and generated SRF length/parameter contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/srf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/Makefile

## Purpose
This Makefile wires the Fujitsu Extended Socket network driver into the kernel build. It defines the `fjes` composite object and gates it behind `CONFIG_FUJITSU_ES`.

## Important APIs and Functions
There are no C APIs. The important build declarations are `obj-$(CONFIG_FUJITSU_ES) += fjes.o` and `fjes-objs := fjes_main.o fjes_hw.o fjes_ethtool.o fjes_trace.o fjes_debugfs.o`.

## Control Flow
When `CONFIG_FUJITSU_ES` is enabled, Kbuild links the listed objects into `fjes.o`. `fjes_main.o` supplies module/platform/netdev lifecycle, `fjes_hw.o` supplies register/shared-memory protocol, `fjes_ethtool.o` supplies ethtool operations, `fjes_trace.o` instantiates tracepoints, and `fjes_debugfs.o` is compiled as part of the object with its own `CONFIG_DEBUG_FS` guards.

## State, Dependencies, and Integration
The Makefile integrates with the parent kernel networking build and depends on a Kconfig symbol named `CONFIG_FUJITSU_ES`. Object ordering matters for tracepoint instantiation and symbol resolution but no persistent runtime state is defined here.

## Risks and Test Signals
Risks are missing object entries when new FJES files are added, stale object names after refactors, and tracepoint build failures if `fjes_trace.o` is omitted. Test signals are successful `CONFIG_FUJITSU_ES=y` and `m` builds, plus builds with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes.h -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes.h

## Purpose
`fjes.h` defines the top-level adapter state and cross-file interfaces for the Fujitsu Extended Socket network driver. It connects platform/netdev state, NAPI, statistics, workqueues, debugfs, and the lower `struct fjes_hw` hardware/shared-memory layer.

## Important APIs and Types
The central type is `struct fjes_adapter`, containing `net_device`, `platform_device`, `napi_struct`, `rtnl_link_stats64`, TX retry timestamps/counters, RX polling timestamps, force-close/reset flags, IRQ registration state, TX/RX and control workqueues, work items, delayed interrupt-watch work, unshare bitmask, embedded `struct fjes_hw`, and optional debugfs dentries. Constants include `FJES_ACPI_SYMBOL`, `FJES_MAX_QUEUES`, TX retry/stall timeouts, open-zone wait time, and IRQ-watch delay. Declared functions include `fjes_set_ethtool_ops()` and debugfs init/exit hooks with no-op inline stubs when debugfs is disabled.

## Control Flow
The header is consumed by `fjes_main.c`, `fjes_hw.c`, `fjes_ethtool.c`, and `fjes_debugfs.c`. `fjes_probe()` allocates a netdev with `struct fjes_adapter` as private data, fills the fields declared here, initializes the work items, embeds hardware state, and registers the netdev. Open/close, interrupt handlers, NAPI, and workqueue callbacks mutate the fields defined here.

## State, Dependencies, and Integration
This header depends on Linux ACPI/netdevice infrastructure and `fjes_hw.h`. It publishes external driver name/version/support-MTU symbols. It is the integration point between the upper Linux network interface and lower endpoint shared-memory protocol.

## Risks and Test Signals
Risks are lifetime ordering of workqueues, NAPI, IRQ registration, and hardware cleanup fields. Because many booleans and bitmasks coordinate asynchronous close/reset/unshare behavior, tests should cover probe failure unwinds, open/close races, forced close scheduling, debugfs enabled/disabled builds, and TX stall/retry state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_debugfs.c

## Purpose
`fjes_debugfs.c` exposes a debugfs status view for FJES endpoint connectivity when `CONFIG_DEBUG_FS` is enabled. It creates a driver root directory and per-adapter status file that reports each endpoint's share state, zone relationship, and connection status.

## Important APIs and Functions
The file defines `fjes_dbg_init()`, `fjes_dbg_exit()`, `fjes_dbg_adapter_init()`, `fjes_dbg_adapter_exit()`, and the seq-file show function `fjes_dbg_status_show()`. `DEFINE_SHOW_ATTRIBUTE(fjes_dbg_status)` supplies file operations for the read-only `status` file. `ep_status_string[]` maps `enum ep_partner_status` values to display strings.

## Control Flow
Module init calls `fjes_dbg_init()` to create the root debugfs directory named after `fjes_driver_name`. Probe calls `fjes_dbg_adapter_init()`, which creates a child directory named after the platform device and a `status` file with the adapter as private data. Reads call `fjes_dbg_status_show()`, which iterates all EPIDs, prints placeholders for the local endpoint, and for remote endpoints queries `fjes_hw_get_partner_ep_status()`, `fjes_hw_epid_is_same_zone()`, and `fjes_hw_epid_is_shared()`.

## State, Dependencies, and Integration
Global state is `fjes_debug_root`; per-adapter state is `adapter->dbg_adapter`. The file depends on debugfs, seq_file, platform device names, and the hardware status helpers in `fjes_hw.c`. It is compiled into the driver object but entirely guarded by `CONFIG_DEBUG_FS`.

## Risks and Test Signals
Risks include indexing `ep_status_string[]` if partner status ever exceeds the enum range, stale debugfs dentries after probe/remove failures, and status reads racing with endpoint teardown. Test signals are clean builds with debugfs enabled and disabled, correct `/sys/kernel/debug/fjes/<device>/status` output for shared/unshared/waiting/complete endpoints, and safe removal while the file is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_ethtool.c

## Purpose
`fjes_ethtool.c` provides ethtool integration for FJES. It exposes driver info, static link settings, adapter and per-endpoint statistics, MMIO register dumps, and device debug trace dump controls.

## Important APIs and Functions
The public hook is `fjes_set_ethtool_ops()`. The ethtool callbacks are `fjes_get_ethtool_stats()`, `fjes_get_strings()`, `fjes_get_sset_count()`, `fjes_get_drvinfo()`, `fjes_get_link_ksettings()`, `fjes_get_regs_len()`, `fjes_get_regs()`, `fjes_set_dump()`, `fjes_get_dump_flag()`, and `fjes_get_dump_data()`. `struct fjes_stats` plus `FJES_STAT()` maps adapter statistic fields to ethtool string/data rows.

## Control Flow
`fjes_set_ethtool_ops()` installs a static `ethtool_ops` table on the netdev during setup. Stats callbacks first copy global adapter counters, then iterate all remote endpoints and append 14 endpoint-specific command/interrupt/drop counters per endpoint. Register dump callbacks read selected FJES information, command, buffer-address, and interrupt registers through `rd32()`. Dump control uses `dump->flag` to start or stop hardware debug tracing under `hw_info.lock`; dump data copies `hw->hw_info.trace` to the ethtool buffer.

## State, Dependencies, and Integration
The file reads `struct fjes_adapter`, `struct fjes_hw`, per-endpoint `ep_stats`, `stats64`, MMIO register accessors from `fjes_regs.h`, and debug commands from `fjes_hw.c`. It reports a fixed synthetic full-duplex 20 Gb/s link with no autonegotiation. Debug trace state is `hw->debug_mode`, `hw->hw_info.trace`, and `trace_size`.

## Risks and Test Signals
Risks include stats/string count mismatches when `max_epid` changes, register reads while hardware is unavailable, trace start/stop error handling, and stale debug mode on failed commands. There is also a likely typo in the stat table where `"tx_bytes"` reads `stats64.rx_bytes`. Tests should compare `get_sset_count()` with emitted strings/data, validate register dump length, exercise dump enable/disable/data paths, and check stats on devices with multiple EPIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.c

## Purpose
`fjes_hw.c` implements the low-level FJES hardware and shared-memory endpoint protocol. It maps registers, resets the device, allocates command buffers/shared status/endpoint rings, issues device commands, manages endpoint sharing and unsharing, manipulates RX/TX ring metadata, handles zone changes and endpoint stop work, and starts/stops hardware debug tracing.

## Important APIs and Functions
Initialization and teardown are `fjes_hw_init()`, `fjes_hw_exit()`, `fjes_hw_reset()`, and internal `fjes_hw_setup()`/`fjes_hw_cleanup()`. Command APIs are `fjes_hw_request_info()`, `fjes_hw_register_buff_addr()`, `fjes_hw_unregister_buff_addr()`, and `fjes_hw_init_command_registers()`. Interrupt/register helpers are `fjes_hw_rd32()`, `fjes_hw_raise_interrupt()`, `fjes_hw_capture_interrupt_status()`, and `fjes_hw_set_irqmask()`. Endpoint helpers include `fjes_hw_setup_epbuf()`, `fjes_hw_get_partner_ep_status()`, `fjes_hw_epid_is_same_zone()`, `fjes_hw_epid_is_shared()`, stop coordination functions, VLAN/MTU/version checks, RX dequeue helpers, TX enqueue helper, and debug commands.

## Control Flow
`fjes_hw_init()` maps MMIO, resets the device, masks interrupts, initializes work/locks, reads max/local EPIDs, allocates per-endpoint memory, writes command-buffer physical addresses to registers, and allocates the trace buffer. `fjes_hw_setup()` allocates `ep_shm_info`, request/response command buffers, shared status memory, and vmalloc endpoint TX/RX buffers for all remote EPIDs; each ring is initialized with `fjes_hw_setup_epbuf()`.

Device commands fill a request union, clear the response union, write `XSCT_CR`, poll `XSCT_CS` for completion, validate response lengths/codes, map busy/timeouts to errno, and update share bits on success. Zone update work requests current endpoint info, computes share/unshare/interrupt actions, registers buffers for same-zone endpoints, unregisters stale endpoints, or raises TXRX stop requests. Ring TX copies a frame into the tail slot and advances tail; RX reads the head slot and advances head on drop.

## State, Dependencies, and Integration
State lives in `struct fjes_hw`: MMIO base/resource, EPID bounds, endpoint shared memory, shared status region, command buffers, trace buffer, share/unshare bitmasks, stop-request bitmasks, locks, and work items. The file depends on Linux MMIO, vmalloc/page-to-phys translation, workqueues, mutexes/spinlocks, register definitions, tracepoints, and adapter callbacks through `hw->back`.

## Risks and Test Signals
Risks include command timeout handling, vmalloc page physical-address lists, ring-full/empty math, endpoint stop races, zone update forced-close paths, cleanup after partial allocation, and debug trace lifecycle. Test signals should include reset timeout behavior, request-info validation, share/unshare busy retries, same-zone transitions, ring enqueue/dequeue boundaries, MTU/VLAN checks, endpoint stop handshakes, forced reset on command failures, and trace start/stop under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.h

## Purpose
`fjes_hw.h` defines the hardware-facing data model for FJES: endpoint buffer layout, ring sizing macros, command request/response formats, shared status, per-endpoint statistics, trace buffer layout, hardware resource state, and the public low-level API used by `fjes_main.c`, ethtool, debugfs, and tracepoints.

## Important APIs and Types
Important macros include endpoint buffer sizes, ring helpers (`EP_RING_INDEX`, `EP_RING_FULL`, `EP_RING_EMPTY`), MTU/frame conversions, command buffer length formulas, command timeouts, zoning constants, TX/RX status bits, and debug buffer sizes. Core types are `struct esmem_frame`, `enum ep_partner_status`, `struct fjes_device_shared_info`, `union fjes_device_command_req`, `union fjes_device_command_res`, `enum fjes_dev_command_request_type`, `struct fjes_device_command_param`, `enum fjes_dev_command_response_e`, `union ep_buffer_info`, `struct fjes_drv_ep_stats`, `struct ep_share_mem_info`, `struct es_device_trace`, `struct fjes_hw_info`, and `struct fjes_hw`.

## Control Flow
The header itself has no executable flow, but its structures define the control protocol. `fjes_hw.c` writes command request unions, device firmware fills response unions and shared endpoint status, TX writes `esmem_frame` entries into a peer's shared ring, RX consumes peer-written frames, and endpoint status bits coordinate MTU changes, polling, and stop handshakes.

## State, Dependencies, and Integration
`struct fjes_hw_info` owns command buffers, shared status, trace memory, locks, and share bitmaps. `struct fjes_hw` embeds runtime hardware resource identifiers, MMIO base, endpoint memory, stop bits, work items, and debug mode. The header depends on Linux netdevice/VLAN/vmalloc primitives and `fjes_regs.h`.

## Risks and Test Signals
Risks are ABI/layout drift with device firmware, endian assumptions in command unions, ring macro off-by-one behavior, and bitmask size limits if `max_epid` exceeds an `unsigned long`. Tests should validate structure sizes/offsets against firmware expectations, ring helper behavior for wrap/full/empty, MTU-to-frame calculations, command buffer length calculations, and status-bit transitions for stop and MTU changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_main.c

## Purpose
`fjes_main.c` is the main Linux driver for Fujitsu Extended Socket networking. It discovers the ACPI-described device, registers a platform device/driver, creates the Ethernet netdev, manages open/close/probe/remove, handles interrupts, NAPI RX, TX to shared-memory endpoint rings, MTU/VLAN operations, workqueues, and forced reset/close flows.

## Important APIs and Functions
Module/platform lifecycle functions are `fjes_init_module()`, `fjes_exit_module()`, `fjes_probe()`, `fjes_remove()`, `acpi_find_extended_socket_device()`, and resource parsers. Netdev operations are `fjes_open()`, `fjes_close()`, `fjes_xmit_frame()`, `fjes_get_stats64()`, `fjes_change_mtu()`, `fjes_tx_retry()`, VLAN add/kill hooks, and `fjes_netdev_setup()`. IRQ/work/NAPI paths include `fjes_intr()`, `fjes_rx_irq()`, stop/update IRQ handlers, `fjes_poll()`, `fjes_force_close_task()`, `fjes_tx_stall_task()`, `fjes_raise_intr_rxdata_task()`, `fjes_watch_unshare_task()`, and `fjes_irq_watch_task()`.

## Control Flow
Module init walks ACPI `PNP0C02` devices, selects one whose `_STR` begins with `"Extended Socket"` and whose `_STA` is usable, extracts MMIO/IRQ resources, registers a platform device, initializes debugfs, then registers the platform driver. Probe allocates `es%d`, initializes NAPI/workqueues/resources, initializes hardware, synthesizes a locally administered MAC address ending in the local EPID, registers the netdev, and creates debugfs.

Open requests endpoint info, announces zone updates, initializes per-peer buffers, registers buffers for same-zone endpoints, enables NAPI, requests IRQ, unmasks interrupts, starts queues, and turns carrier on. TX routes multicast to all endpoints and unicast local FJES MACs to a specific EPID, validating partner share status, endpoint version, MTU, VLAN filter, and TX ring space before copying frames and scheduling interrupt work. RX NAPI scans remote endpoint rings, builds SKBs, updates stats, drops consumed frames, and re-enables RX interrupts after a short polling window. Close stops queues, raises endpoint stop, disables NAPI/IRQs/work, waits for stop completion, and unregisters shared buffers.

## State, Dependencies, and Integration
State is in `struct fjes_adapter` and embedded `struct fjes_hw`. The file integrates ACPI, platform devices, netdev, NAPI, workqueues, interrupts, VLAN filtering, ethtool/debugfs setup, and low-level FJES hardware helpers. Endpoint sharing/unsharing is coordinated through `buffer_share_bit`, `buffer_unshare_reserve_bit`, `txrx_stop_req_bit`, `epstop_req_bit`, and `unshare_watch_bitmask`.

## Risks and Test Signals
Risks include ACPI resource matching, asynchronous work versus remove/close ordering, TX retry/stall behavior, multicast accounting, endpoint stop/unshare races, forced close on hardware command failure, and IRQ watch polling. Test signals should cover ACPI discovery failure/success, probe unwinds, open/close cycles, unicast/multicast TX to shared and unshared EPIDs, NAPI budget behavior, MTU changes while running, VLAN filter capacity, IRQ handling for each mask, and removal with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_regs.h

## Purpose
`fjes_regs.h` defines the FJES MMIO register map, register bitfield unions, interrupt masks, and small read/write helper macros used by the hardware layer and ethtool register dumps.

## Important APIs and Types
Register offsets cover information registers (`XSCT_OWNER_EPID`, `XSCT_MAX_EP`), device control (`XSCT_DCTL`), command control (`XSCT_CR`, `XSCT_CS`, command/shared/request/response buffer address registers), and interrupt control (`XSCT_IS`, `XSCT_IMS`, `XSCT_IMC`, `XSCT_IG`, `XSCT_ICTL`). Bitfield unions include `REG_OWNER_EPID`, `REG_MAX_EP`, `REG_DCTL`, `REG_CR`, `REG_CS`, and `REG_ICTL`. Interrupt masks are `REG_ICTL_MASK_INFO_UPDATE`, `DEV_STOP_REQ`, `TXRX_STOP_REQ`, `TXRX_STOP_DONE`, `RX_DATA`, and `ALL`; interrupt status masks include assert and EPID extraction bits. `rd32()` and `wr32()` are convenience accessors around `fjes_hw_rd32()` and `writel()`.

## Control Flow
The header has no standalone execution, but `fjes_hw.c` uses the offsets and unions to reset the device, issue commands, program physical buffer addresses, mask/unmask interrupts, capture status, and generate peer interrupts. `fjes_ethtool.c` uses the same offsets to produce a register dump.

## State, Dependencies, and Integration
It depends on Linux bit operations and forward-declares `struct fjes_hw`. The accessor macros assume a local variable named `hw` with a valid MMIO `base`, so call sites must maintain that convention.

## Risks and Test Signals
Risks are register offset drift against hardware/firmware, C bitfield layout assumptions with `__le32`, accessor macro misuse without a local `hw`, and interrupt mask overlap errors. Tests should validate register dumps, reset bit polling, command request/status decoding, interrupt status EPID extraction, and mask/unmask operations on real or emulated hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.c

## Purpose
`fjes_trace.c` instantiates the FJES tracepoint definitions. It is intentionally small: including `fjes_trace.h` with `CREATE_TRACE_POINTS` causes the trace events declared in the header to emit storage and registration code in exactly one object.

## Important APIs and Functions
There are no runtime functions in this file. The important symbols are generated by the Linux tracepoint framework from `TRACE_EVENT()` declarations in `fjes_trace.h`. The file includes `fjes_hw.h` so tracepoint prototypes can see FJES hardware and command types.

## Control Flow
At build time, this object expands tracepoint definitions unless `__CHECKER__` is set. At runtime, the generated tracepoints are called from `fjes_hw.c` and `fjes_main.c` through functions such as `trace_fjes_hw_issue_request_command()`, `trace_fjes_hw_register_buff_addr()`, and stop-request trace helpers.

## State, Dependencies, and Integration
This file depends on Linux module and tracepoint infrastructure. It must be linked into the composite `fjes.o` exactly once; otherwise the driver either lacks tracepoint storage or risks duplicate tracepoint definitions.

## Risks and Test Signals
Risks are build-only: missing object linkage, duplicate `CREATE_TRACE_POINTS`, and sparse/checker incompatibility. Test signals are successful kernel builds with tracing enabled, visibility of FJES trace events under tracing facilities, and no duplicate symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.h

## Purpose
`fjes_trace.h` declares FJES tracepoints for hardware command execution, endpoint buffer registration/unregistration, debug trace commands, and endpoint stop-request interrupt handling. These tracepoints provide structured observability around the driver's most failure-prone hardware protocol transitions.

## Important APIs and Trace Events
Hardware command events include `fjes_hw_issue_request_command`, `fjes_hw_request_info`, and request-info error tracing. Buffer command events include register/unregister request, result, and error events. Debug events include start-debug request/result/error and stop-debug result/error. Main-driver events include pre/post traces for TXRX stop request IRQs and device stop request IRQs. The footer sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>`.

## Control Flow
When included normally, the header declares tracepoint call sites. When included by `fjes_trace.c` with `CREATE_TRACE_POINTS`, it emits definitions. The `TP_fast_assign` blocks copy register fields, response codes, endpoint statuses, zones, vmalloc-backed buffer physical addresses, stop bitmasks, and RX status values into trace records; `TP_printk` formats them for human-readable trace output.

## State, Dependencies, and Integration
The tracepoints depend on `struct fjes_hw`, command unions, register unions, endpoint shared-memory structures, `vmalloc_to_page()`, and tracepoint macros. They integrate directly with `fjes_hw.c` command paths and `fjes_main.c` interrupt stop-handshake paths.

## Risks and Test Signals
Risks include tracepoint ABI churn, dereferencing endpoint arrays while hardware is tearing down, costly physical-address derivation in trace assignment, and mismatches between dynamic array lengths and `max_epid`. Test signals should include enabling each tracepoint while issuing info/share/unshare/debug commands, triggering stop-request IRQ paths, validating dynamic zone/status arrays, and building with tracing/sparse configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.h -->
