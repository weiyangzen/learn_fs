# Research: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003923`: lines 1-8251, `Docs/researches/chunks/subset-b-003923_research.md`
- `subset-b-003924`: lines 8252-15444, `Docs/researches/chunks/subset-b-003924_research.md`

## Chunk Research

### subset-b-003923: lines 1-8251

# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.c lines 1-8251

## Scope And Purpose

This chunk is the first half of the HFI1 chip-specific driver implementation. It defines module tunables, chip and protocol constants, error classification tables, interrupt-source metadata, counter-access infrastructure, low-level CSR access helpers, error handlers, SPC freeze recovery, 8051/LCB ownership helpers, QSFP interrupt handling, link capability negotiation, link up/down/downgrade work handlers, and the interrupt-source dispatch table used by the next chunk's general interrupt dispatcher.

The code is hardware-facing Linux kernel driver code for Intel/Cornelis HFI1 OPA/InfiniBand adapters. Most routines translate chip CSR bits into driver state, counters, workqueue actions, or port management decisions. The chunk does not contain the final device probe/init sequence; it establishes the tables and handlers that later initialization and interrupt paths rely on.

## Important APIs, Types, And Functions

Module parameters and constants:

- `num_vls`, `rcv_intr_timeout`, `rcv_intr_count`, `link_crc_mask`, and `loopback` expose runtime tuning for virtual lanes, receive interrupt moderation, link CRC negotiation, and loopback mode. Static tunables include `crc_14b_sideband`, `use_flr`, and `quick_linkup`.
- RSM instance constants, LRH/BTH/QPN match/select offsets, AIP/16B header selectors, `SC2VL_VAL()`, and `DC_SC_VL_VAL()` define packed hardware-programming values used later for packet steering and SC/VL setup.
- Error consequence bits `SEC_WRITE_DROPPED`, `SEC_PACKET_DROPPED`, `SEC_SC_HALTED`, and `SEC_SPC_FREEZE` annotate send-context and PIO error impacts.

Error and interrupt metadata:

- `struct flag_table` maps hardware status bits to log strings and optional consequence metadata. Tables cover CCE, miscellaneous, PIO, SDMA, egress, egress info, send-context, RXE, DCC, LCB, DC8051, and DC8051 information/host-message status bits.
- Freeze masks such as `ALL_PIO_FREEZE_ERR`, `ALL_SDMA_FREEZE_ERR`, `ALL_TXE_EGRESS_FREEZE_ERR`, `ALL_RXE_FREEZE_ERR`, and `RXE_FREEZE_ABORT_MASK` centralize which hardware errors trigger SPC freeze recovery and which A0 RXE errors abort recovery.
- `struct err_reg_info` describes second-tier interrupt status, clear, mask, handler, and description registers. `misc_errs[]`, `sdma_eng_err`, `various_err[]`, and `dc_errs[]` plug concrete CCE/DC interrupt sources into the common clear-down machinery.
- `is_table[]` maps interrupt-source ranges to name builders and handler functions for general errors, SDMA engine errors, send-context errors, SDMA normal/progress/idle interrupts, various/QSFP/temperature interrupts, DC interrupts, receive available, receive urgent, send credit, and reserved ranges.

CSR and counter infrastructure:

- `hfi1_addr_from_offset()` chooses BAR/base mapping based on `dd->base2_start`; `read_csr()`, `write_csr()`, and `get_csr_addr()` are the core exported CSR helpers for this file. `write_csr()` refuses writes into the receive array address range through a warning guard.
- `struct cntr_entry` describes named counters, their CSR offsets, storage offsets, flags, and read/write accessor callback. Macro families build RXE, TXE, CCE, DC, LCB, and synthetic counter entries.
- `read_write_csr()`, `dev_access_u32_csr()`, `dev_access_u64_csr()`, `port_access_u32_csr()`, `port_access_u64_csr()`, and `dc_access_lcb_cntr()` implement counter reads/writes against chip CSRs, per-VL offsets, per-SDMA engine offsets, and LCB CSRs.
- `read_write_sw()`, `get_all_cpu_total()`, and `read_write_cpu()` expose software and per-CPU counters, including zero-by-writing-zero semantics for per-CPU synthetic counters.
- The many `access_*_err_cnt()` routines expose individual software-maintained error-bit counters stored in arrays on `struct hfi1_devdata` or `struct hfi1_pportdata`.
- `dev_cntrs[]` and `port_cntrs[]` are large indexed tables binding enum counter IDs to hardware counters, synthetic counters, error-bit counters, per-VL counters, and IB port counters. The port table includes 160 receive header overflow counters through `OVR_ELM()`.

Revision, naming, and formatting helpers:

- `is_ax()` and `is_bx()` classify chip revision from `dd->revision`. Several error recovery and link training paths branch on A0/B0 behavior.
- `is_urg_masked()` checks whether a receive urgent interrupt source is masked for a receive context.
- `append_str()` and `flag_string()` build comma-separated error strings, adding unknown remaining bits and appending `*` on truncation.
- `is_misc_err_name()`, `is_sdma_eng_err_name()`, `is_sendctxt_err_name()`, `is_various_name()`, `is_dc_name()`, `is_sdma_eng_name()`, `is_rcv_avail_name()`, `is_rcv_urgent_name()`, `is_send_credit_name()`, and `is_reserved_name()` produce readable interrupt-source names.

Error and interrupt handlers:

- `handle_cce_err()`, `handle_rxe_err()`, `handle_misc_err()`, `handle_pio_err()`, `handle_sdma_err()`, `handle_egress_err()`, and `handle_txe_err()` log decoded error status, increment matching software counters, and trigger freeze handling when their masks require it.
- `handle_send_egress_err_info()` reads `SEND_EGRESS_ERR_SOURCE` and `SEND_EGRESS_ERR_INFO`, clears the info bits quickly, logs decoded integrity failures, and increments aggregate/per-VL transmit discard counters for egress discard classes.
- `interrupt_clear_down()` is the common second-tier error clear loop. It repeatedly reads status, writes the observed value to clear, invokes the handler, and masks repeating bits after `MAX_CLEAR_COUNT`.
- `is_misc_err_int()`, `is_sdma_eng_err_int()`, `is_various_int()`, `is_dc_int()`, `is_send_credit_int()`, `is_sdma_eng_int()`, `is_rcv_avail_int()`, `is_rcv_urgent_int()`, and `is_reserved_int()` are table-driven dispatch endpoints for logical interrupt sources.
- `is_sendctxt_err_int()` halts a send context, logs send-context error flags, processes disallowed-packet info, queues automatic restart for non-user contexts, and updates aggregate send-context error counters.
- `handle_sdma_eng_err()` increments engine error counters and delegates engine-specific recovery to `sdma_engine_error()`.
- `handle_qsfp_int()` handles QSFP module-present and interrupt pins, flips GPIO inversion to catch insertion/removal transitions, invalidates QSFP cache state, updates offline-disabled reasons, and queues QSFP or link-down work.

LCB, DC8051, and link-management helpers:

- `request_host_lcb_access()`, `request_8051_lcb_access()`, `set_host_lcb_access()`, `set_8051_lcb_access()`, `acquire_lcb_access()`, `release_lcb_access()`, and `init_lcb_access()` implement ownership of LCB CSR access between the host and the embedded 8051 firmware.
- `hreq_response()` and `handle_8051_request()` service external-device requests from the 8051, including unsupported request responses, LCB reset, config-done acknowledgement, and interface-test echo.
- `set_up_vau()`, `set_up_vl15()`, and `reset_link_credits()` program credit allocation unit and VL15 credit state and reset CM credit accounting.
- `lcb_shutdown()`, `_dc_shutdown()`, `dc_shutdown()`, `_dc_start()`, `dc_start()`, and `adjust_lcb_for_fpga_serdes()` control DC/LCB shutdown/start behavior and emulator-specific FIFO/address timing workarounds.
- `handle_sma_message()` reads an SMA idle message and reacts to ARM/ACTIVE messages by marking neighbor state and optionally activating the link.
- `handle_link_up()`, `handle_link_down()`, `handle_link_bounce()`, `handle_verify_cap()`, `apply_link_downgrade_policy()`, and `handle_link_downgrade()` are workqueue routines for 8051-reported link events.
- CRC/link-width helpers include `cap_to_port_ltp()`, `port_ltp_to_cap()`, `lcb_to_port_ltp()`, `link_width_to_bits()`, `nibble_to_count()`, `get_link_widths()`, `get_linkup_widths()`, and `get_linkup_link_widths()`.
- `handle_8051_interrupt()` decodes 8051 firmware info and host-message flags, routes SMA, link-up, verify-cap, external-device, link-down, and link-downgrade work, counts unknown frames, suppresses duplicate link-down queueing, and masks lost-heartbeat interrupts after first report.
- `handle_dcc_err()` records first uncorrectable/FM config/port receive error details for management queries, logs decoded errors, increments link-down count, and queues link bounce when `PortErrorAction` policy demands it. `handle_lcb_err()` logs decoded LCB errors.

SPC freeze and receive control:

- `adjust_rcvctrl()`, `add_rcvctrl()`, and `clear_rcvctrl()` serialize RCV_CTRL read-modify-write updates under `dd->rcvctrl_lock`.
- `start_freeze_handling()` enters frozen state, optionally forces SPC freeze, notifies SDMA, halts enabled send contexts, raises a user event, and queues `freeze_work` unless recovery is explicitly aborted.
- `wait_for_freeze_status()` polls CCE freeze bits for freeze/unfreeze completion with timeout logging.
- `rxe_freeze()` disables the receive port and all receive contexts. `rxe_kernel_unfreeze()` reenables kernel receive contexts and the receive port, leaving user contexts to unfreeze through their own driver calls.
- `handle_freeze()` is the deferred freeze-recovery worker: wait frozen, freeze PIO/SDMA/RXE, unfreeze hardware, apply the A0 double-unfreeze sequence, unfreeze kernel PIO/SDMA/RXE, clear `HFI1_FROZEN`, and wake waiters.
- `init_rcverr()`, `update_rcverr_timer()`, and `free_rcverr()` maintain a periodic receive-overflow check that can bounce the link on excessive buffer overrun if configured.

## Control Flow And Runtime Behavior

Error interrupt handling is two-level. A top-level CCE interrupt source points at a second-tier status/clear/mask register through `struct err_reg_info`. `interrupt_clear_down()` drains the second-tier register by repeatedly reading status, writing the same bits to clear, and invoking the specific handler. If the same bits keep reappearing past `MAX_CLEAR_COUNT`, the routine masks those bits to avoid an interrupt storm. This pattern is used for CCE/RXE/misc/PIO/SDMA/egress/TXE errors, per-SDMA-engine errors, QSFP GPIO interrupts, and most DC errors.

Send-context error handling is deliberately different from the generic clear-down path. `is_sendctxt_err_int()` reads a per-context error status after halting the software send context with `SCF_HALTED`. It does not clear immediately because context recovery requires longer work. Kernel and VL15 contexts get `halt_work` queued automatically; user contexts must request restart through the driver.

Egress error processing has a special attribution path. `handle_egress_err()` walks set bits in `SEND_EGRESS_ERR_STATUS`; link-down/incorrect-link-state bits count as inactive-port discards, while SDMA disallowed-packet bits are translated from engine to VL through the RCU-protected SDMA map and then decoded in `SEND_EGRESS_ERR_INFO`. Hardware only records one bit per integrity check, so the driver explicitly accepts lossy attribution when multiple packets or VLs contribute before the handler runs.

Freeze recovery is asynchronous. Error handlers call `start_freeze_handling()` from interrupt context, which marks `HFI1_FROZEN`, halts send contexts, notifies SDMA, and queues `freeze_work`. The worker waits for hardware freeze state, runs PIO/SDMA/RXE freeze hooks, issues unfreeze, waits for hardware, applies an A0 extra freeze/unfreeze workaround, reenables kernel transmit/receive resources, clears the frozen flag, and wakes `dd->event_queue`.

LCB ownership is serialized with the host link-state lock. `acquire_lcb_access()` refuses access while the link is down, requests ownership from the 8051 on the first user, switches the hardware selector to host access, and increments `dd->lcb_access_count`. `release_lcb_access()` switches back to 8051 access and sends a grant command when the final holder releases. Both functions can operate in sleepable or busy-wait locking modes.

The 8051 interrupt path converts firmware status into workqueue actions rather than doing long operations in the handler. `handle_8051_interrupt()` decodes `DC8051_DBG_ERR_INFO_SET_BY_8051`; link-up, verify-cap, SMA idle message, link-down, link-width downgrade, and external-device requests are queued or handled according to host-message bits. LNI failures only trigger link-down handling while the host state is in polling/verify-cap/going-up phases.

Verify-cap processing is the core link-negotiation path in this chunk. `handle_verify_cap()` moves the host state to verify-cap, shuts down/resets LCB state, reads peer PHY/fabric/link-width/device information via helper routines defined later in the file, configures vAU and temporary VL15 credit state, chooses a common CRC mode with priority for the lowest supported common bit, updates sideband credit mode, determines active link speed based on firmware version and remote rate bits, stores supported/enabled/active LTP CRC mode for PortInfo, programs remote credit return tables, applies A0 link-kill workarounds, releases LCB access back to the 8051, and requests transition to link-up.

Link-down and downgrade handling enforce policy. `handle_link_down()` first transitions software state offline, reads firmware link-down details only if the link had been up, stores local/neighbor reason snapshots for SMA, clears neighbor metadata, disables receive port traffic, and either shuts down DC when QSFP is absent or restarts link bring-up. `apply_link_downgrade_policy()` refreshes active widths when needed and bounces the link if downgrade is disabled or outside the enabled mask.

Counter access is table driven. Public counter read/write code later in the file indexes `dev_cntrs[]` or `port_cntrs[]` and calls each entry's `rw_cntr` callback. Callbacks either read/write hardware CSRs, use per-VL CSR spacing, read LCB CSRs, expose software counters, or sum per-CPU counters with zero-on-write behavior. The many status-bit counter callbacks are intentionally simple lookups into arrays incremented by the error handlers in this chunk.

## State And Persistence Behavior

Driver state is held mostly in `struct hfi1_devdata`, `struct hfi1_pportdata`, `struct hfi1_ctxtdata`, send contexts, SDMA engines, and QSFP state. This chunk mutates or reads fields such as `dd->flags`, `dd->revision`, `dd->icode`, `dd->irev`, `dd->base2_start`, `dd->kregbase1`, `dd->kregbase2`, `dd->send_contexts`, `dd->hw_to_sw`, `dd->per_sdma`, `dd->sdma_map`, `dd->lcb_access_count`, `dd->dc_shutdown`, `dd->vl15buf_cached`, error counter arrays, synthetic aggregate counters, per-CPU zero baselines, and receive-overflow timer state.

Per-port state affected here includes `host_link_state`, `driver_link_ready`, `offline_disabled_reason`, `port_error_action`, link width/speed active/enabled/supported fields, CRC mode fields, link-down reason snapshots, neighbor cached identity/security information, QSFP cache/reset/interrupt flags, `unknown_frame_count`, `port_xmit_discards`, per-VL discard counters, link up/down counters, and `current_egress_rate`.

Hardware state persists in CSRs until reset or explicit programming. This chunk writes interrupt masks and clears, CCE freeze/unfreeze controls, RCV_CTRL, send/receive/DC/LCB error registers, SEND_CM credit registers, LCB reset/run/FIFO/CRC registers, DC8051 request/response registers, QSFP invert/mask GPIO CSRs, and various DCC error-info/credit/link registers.

Error information has first-error persistence semantics in several places. `handle_dcc_err()` only records uncorrectable, FM config, and port receive error info if the management status bit is not already set, preserving the first observed condition until higher-level code clears it. Counter arrays accumulate until counter reset/read-write paths later in the file zero or extend them.

The receive overflow timer persists independently of interrupts. Once initialized, it periodically compares the hardware receive overflow counter to `dd->rcv_ovfl_cnt`, optionally queues link bounce, refreshes the cached value, and rearms itself until deleted.

## Dependencies And Integration Points

This chunk depends on kernel facilities for MMIO (`readq`, `writeq`), IRQ/workqueue/timer execution, jiffies timeouts, RCU, mutexes, spinlocks, percpu counters, module parameters, and standard bit operations such as `fls64()` and `hweight64()`.

Internal HFI1 dependencies include CSR definitions and helpers from `hfi.h` and generated register headers; packet management and PIO helpers from `pio.h`; SDMA functions such as `sdma_engine_interrupt()`, `sdma_engine_error()`, `sdma_freeze_notify()`, `sdma_freeze()`, and `sdma_unfreeze()`; link/management helpers from `mad.h`, `platform.h`, `eprom.h`, `efivar.h`, `aspm.h`, `affinity.h`, `debugfs.h`, `fault.h`, and `netdev.h`; and receive context helpers such as `hfi1_rcd_get_by_index()`, `hfi1_rcd_put()`, `hfi1_rcvctrl()`, `handle_user_interrupt()`, and `hfi1_rcvhdrtail_kvaddr()`.

The interrupt-source table at the end of this chunk is consumed immediately after this range by the general interrupt dispatch code. Several prototypes declared early in the chunk are implemented in later lines of `chip.c`, including firmware command helpers, physical/logical state reads/writes, FM table routines, counter export routines, and chip initialization.

Upper-layer integration surfaces include IB/OPA port state and link-down reason reporting, SMA idle message handling, FM `PortErrorAction` policy, PortInfo CRC/link width/speed fields, userspace frozen events through `hfi1_set_uevent_bits()`, sysfs/debugfs-style counter exposure, netdev/AIP receive routing through RSM/QoS constants, and QSFP module management.

## Risks And Edge Cases

- CSR access is guarded only by `HFI1_PRESENT`; callers must avoid using stale `dd` mappings during teardown. `write_csr()` also rejects receive-array writes in the first BAR range, so receive-array programming must use the intended path elsewhere.
- Counter callback tables and accessor functions rely on enum indexes matching hardware bit positions and array sizes. A shifted enum or status bit definition would silently report the wrong software counter.
- `flag_string()` truncation appends `*`, but very small buffers return an empty string. Diagnostic callers need adequate buffers to avoid losing critical hardware error detail.
- `interrupt_clear_down()` masks repeating bits after an arbitrary loop count. This prevents storms but can hide a persistent hardware fault until mask state is inspected.
- Send-context errors are aggregated across all contexts; per-context detail can be lost after the initial log and halt workflow.
- Egress error attribution is inherently lossy because `SEND_EGRESS_ERR_INFO` has one bit per error type, not per packet. Per-VL discard counters can be inaccurate when multiple packets/VLs fail before the handler runs.
- Freeze recovery is global and disruptive. Some A0 RXE errors set `FREEZE_ABORT`, leaving the system in a state that requires reboot rather than attempted recovery.
- `start_freeze_handling()` sets `HFI1_FROZEN` before deferred work completes. Other paths must interpret this as "freeze handling in progress," not merely "hardware freeze bit is set."
- `acquire_lcb_access()` refuses host access when the software link state is down. Callers that need LCB diagnostics during down states must use later cached/8051-mediated paths instead of this ownership API.
- LCB ownership reference counting is sensitive to unbalanced acquire/release calls. `release_lcb_access()` logs and skips if the count is zero, but a missed release can leave LCB ownership with the host.
- QSFP module-present handling changes GPIO inversion depending on insertion/removal. Incorrect inversion state can cause missed future transitions.
- `handle_8051_interrupt()` suppresses duplicate link-down work with `is_link_down_queued`; failure to clear that flag in link-down work would prevent subsequent link-down processing.
- Link speed selection has firmware-version-specific handling. Older 8051 firmware does not set some max-rate fields correctly, so changing version checks can force wrong active speed reporting.
- `handle_verify_cap()` uses common CRC mode priority and optional 14B sideband credit mode. Misconfigured `link_crc_mask` or partner CRC capabilities can select a mode that is legal but unexpected for deployment policy.
- `handle_dcc_err()` preserves first error info until cleared. Later, more actionable packet headers or FM config errors can be ignored for management reporting.

## Test And Validation Signals

- Build the HFI1 driver with this file and related headers enabled; table size/index mismatches, missing CSR symbols, and function prototype drift should surface at compile time.
- Exercise module parameters for `num_vls`, receive interrupt moderation values, `link_crc_mask`, `loopback`, and quick-linkup paths where available.
- Use hardware or fault injection to trigger CCE, RXE, misc, PIO, SDMA, egress, TXE, send-context, SDMA-engine, DCC, LCB, and DC8051 error bits; validate decoded logs, software counter increments, clear-down behavior, and repeated-error masking.
- Validate SPC freeze recovery with PIO, SDMA, egress, and RXE freeze-causing errors, including A0-specific abort and double-unfreeze behavior.
- Check per-context send error handling by forcing kernel and user send-context errors and confirming kernel contexts queue restart while user contexts remain halted until userspace action.
- Verify egress discard accounting under inactive-port errors and SDMA disallowed-packet errors, including per-VL attribution through SDMA engine-to-VL maps.
- Test QSFP insert/remove and module interrupt flows: cache invalidation, GPIO inversion, offline-disabled reason changes, link-down work while polling, and QSFP work scheduling only when present.
- Exercise 8051 host-message handling for SMA idle messages, link-up, verify-cap, external-device requests, link-going-down, width downgrade, unknown frames, LNI failures, and heartbeat loss.
- Validate LCB ownership reference counting with nested acquire/release, non-sleeping callers, link-down rejection, 8051 command failures, and shutdown suppression paths.
- Bring links through verify-cap and link-up on firmware versions before and after the rate-field behavior changes; confirm selected CRC mode, sideband credit bit, vAU/VL15 setup, active speed, active widths, and PortInfo LTP CRC fields.
- Trigger link down and downgrade policy cases with enabled/disabled downgrade masks and confirm local/neighbor reason storage, link bounce, transmit counter width update, and DC shutdown when QSFP is absent.
- Read device and port counters through later export APIs after generated hardware events; verify hardware CSR reads, LCB counter reads, per-CPU zeroing, synthetic aggregate counters, receive overflow counters, and per-VL counters.

## Cross-Chunk Notes

This chunk ends immediately after defining `is_table[]`; the actual `is_interrupt()` dispatcher, top-level IRQ handlers, receive interrupt paths, firmware command implementation, full link-state state machine, counter export/allocation, and device initialization continue in `subset-b-003924` for the same source file. The final merged per-file report should connect this chunk's tables and handler definitions to those later callers.

### subset-b-003924: lines 8252-15444

# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.c lines 8252-15444

## Scope And Purpose

This chunk covers the central HFI1 chip-control path for interrupts, receive context interrupt completion, DC8051/LCB access, physical and logical link state transitions, QSFP events, fabric-manager configuration tables, receive/send register programming, counters, reset/default CSR initialization, receive-side mapping rules, device bring-up, and thermal shutdown handling.

The source is Linux kernel HFI1 InfiniBand/OPA adapter driver code. It is hardware-facing: most functions translate driver state into chip CSR writes, poll hardware state, or expose hardware state to upper layers such as verbs, netdev/AIP, fabric manager MAD handling, sysfs counters, PCIe setup, SDMA, PIO, and firmware-controlled link training.

The chunk begins with interrupt dispatch and receive EOI logic, then moves through 8051 firmware command helpers and link bring-up, then into port state transitions and FM table APIs, then receive context setup and counter infrastructure, and finally the low-level initialization sequence used by `hfi1_init_dd()`.

## Important APIs, Types, And Functions

Interrupt and receive paths:

- `general_interrupt()` scans `CCE_INT_STATUS` CSRs under `dd->gi_mask`, clears handled bits, and dispatches each set source through `is_interrupt()`.
- `sdma_interrupt()` handles SDMA engine MSI-X vectors by reading the SDMA interrupt-source CSR, clearing active bits, and calling `sdma_engine_interrupt()`.
- `receive_context_interrupt()`, `receive_context_thread()`, and `receive_context_interrupt_napi()` are per-receive-context interrupt entry points. They call `rcd->do_interrupt()` and use `hfi1_rcd_eoi_intr()` or `__hfi1_rcd_eoi_intr()` to clear and potentially re-force interrupts if packets remain.
- `hfi1_netdev_rx_napi()` integrates receive interrupt processing with NAPI for netdev/AIP receive queues.
- `clear_recv_intr()`, `force_recv_intr()`, and `check_packet_present()` encode the race-sensitive EOI behavior around receive header tail updates and pending DMA visibility.

8051, LCB, and link capability helpers:

- `do_8051_command()` is the serialized host-command interface to the embedded 8051 firmware. It writes request type/data, waits on completion, extracts return code and response data, handles LCB read/write special packing, and attempts DC restart after a first timeout.
- `read_lcb_csr()` and `write_lcb_csr()` choose between direct host CSR access, 8051-mediated access, and cached read fallback depending on `ppd->host_link_state`.
- `update_lcb_cache()` maintains cached LCB error counters for link states where direct LCB access may be unavailable.
- `load_8051_config()` and `read_8051_config()` write/read 8051 firmware configuration fields such as verify-capability frames, link quality, link-down reasons, TX settings, device IDs, and firmware version.
- `send_idle_sma()` and related idle-message helpers use 8051 commands to exchange idle SMA messages.

Link and QSFP functions:

- `set_local_link_attributes()` programs TX settings, host interface version, verify-capability local PHY/fabric/link-mode values, supported widths, CRC mode, loopback bits, and local device ID before polling/link-up.
- `start_link()`, `try_start_link()`, `handle_start_link()`, `bringup_serdes()`, and `hfi1_quiet_serdes()` manage initial SerDes/link activation, QSFP read retry, and link shutdown.
- `reset_qsfp()`, `init_qsfp_int()`, `qsfp_event()`, and `handle_qsfp_error_conditions()` manage QSFP reset, interrupt masking, module initialization waits, status reads, and alarm/warning logging.
- `goto_offline()` performs the multi-step transition from any active/training state to offline, including 8051 physical-state command, waiting for offline substates, disabling AOC transmitters, restoring host LCB access, logical-state verification, status-page update, FM readiness wait, and link-down bookkeeping.
- `set_link_state()` is the main host link-state state machine for `HLS_UP_INIT`, `HLS_UP_ARMED`, `HLS_UP_ACTIVE`, `HLS_DN_POLL`, `HLS_DN_DISABLE`, `HLS_DN_OFFLINE`, `HLS_VERIFY_CAP`, and `HLS_GOING_UP`.
- `driver_pstate()` and `driver_lstate()` convert internal `HLS_*` states to IB/OPA physical and logical states.

Fabric manager and VL programming:

- `hfi1_get_ib_cfg()` and `hfi1_set_ib_cfg()` expose and apply link width, speed, operational VLs, thresholds, MTU, PKey, and related IB/OPA config values.
- `set_send_length()` programs per-VL send length checks, credit return thresholds, and DC MTU capability.
- `set_lidlmc()` programs DLID/LMC checks for all send contexts and SDMA engines.
- `init_vl_arb_caches()`, `vl_arb_*()` helpers, `set_vl_weights()`, `fm_get_table()`, and `fm_set_table()` cache and program FM tables for VL arbitration, buffer control, SC-to-VLnt mapping, and preemption placeholders.
- `set_buffer_control()` implements the required live credit-change algorithm for per-VL dedicated/shared credits and global shared/total credits, then updates SDMA/PIO maps based on actual operational VLs.
- `stop_drain_data_vls()` and `open_fill_data_vls()` bracket changes to per-VL resources by disabling, draining, and re-enabling data VLs.

Receive context, TID, and mapping APIs:

- `hfi1_put_tid()` writes receive-array TID entries through write-combining memory and flushes eager/flush entries or every fourth expected entry.
- `hfi1_clear_tids()` invalidates eager and expected TID ranges for a context.
- `set_hdrq_regs()`, `encode_rcv_header_entry_size()`, `hfi1_validate_rcvhdrcnt()`, `update_usrhead()`, and `hdrqempty()` program and maintain receive header queues.
- `hfi1_rcvctrl()` is the central per-context receive control routine. It enables/disables receive contexts, interrupts, tail updates, TID flow, one-packet eager mode, RHQ/eager drop behavior, urgent interrupts, and initial header/eager/TID register state.
- `init_qpmap_table()`, RSM map/rule helpers, `init_qos()`, `init_fecn_handling()`, `hfi1_init_aip_rsm()`, and `hfi1_deinit_aip_rsm()` program receive-side packet steering for QOS, FECN, normal QP mapping, and netdev/AIP traffic.

Counters, initialization, and cleanup:

- `hfi1_read_cntrs()` and `hfi1_read_portcntrs()` provide sysfs-style counter name/value buffers.
- `read_dev_cntr()`, `write_dev_cntr()`, `read_port_cntr()`, and `write_port_cntr()` wrap hardware and synthetic counter access, including 32-bit wrap extension and saturation.
- `init_cntrs()` builds device and port counter name/value arrays, per-CPU RC ack counters, and the synthetic counter timer/workqueue. `free_cntrs()` tears them down.
- `init_chip()`, `reset_cce_csrs()`, `reset_txe_csrs()`, `reset_rxe_csrs()`, `reset_misc_csrs()`, `write_uninitialized_csrs_and_memories()`, and `init_early_variables()` establish known chip CSR defaults and initialize hardware memories that need ECC/parity seeding.
- `set_up_context_variables()` sizes kernel, user, netdev receive contexts, RcvArray groups, free user contexts, and send-context pools.
- `hfi1_init_dd()` is the chunk's top-level device initialization routine, sequencing PCIe setup, saved PCI variables, implementation identification, ASIC shared data, chip reset, firmware/platform setup, PCIe Gen3 transition, RX/TX initialization, contexts, SDMA, interrupts, firmware load, thermal initialization, counters, receive-error setup, and user refcount.
- `hfi1_start_cleanup()` starts cleanup by exiting ASPM, freeing counters and receive-error data, and finishing chip resources.
- `create_pbc()` builds packet buffer control words, including optional static-rate delay.
- `thermal_init()`, `hfi1_tempsense_rd()`, and `handle_temp_err()` initialize/read thermal hardware and force emergency freeze/offline/DC shutdown on critical temperature.

## Control Flow And Runtime Behavior

Interrupt control is split between a general MSI-X vector and specialized vectors. `general_interrupt()` reads all masked interrupt status registers, clears pending bits before dispatch, then walks set bits and calls table-driven handlers via `is_interrupt()`. Receive context data IRQs are intentionally excluded from the general handler because their latency/bandwidth behavior is context-specific and may use threaded IRQs or NAPI. SDMA vectors read only the register containing SDMA interrupt sources and pass engine-specific status bits to SDMA core code.

Receive interrupt EOI is deliberately conservative. The driver clears the receive interrupt, then checks both memory-visible packet state and, if needed, the hardware tail CSR. If packets are still present, it forces another interrupt. This covers the race where packets arrive after software's last queue check but before interrupt clear, and the limitation that queued DMA tail writes may not be visible in memory without an interrupt.

The 8051 command path serializes all firmware host commands under `dd->dc8051_lock`. It refuses commands during DC shutdown, treats repeated timeouts as fatal, and after the first timeout tries `_dc_shutdown()` plus `_dc_start()` before later commands. Normal commands are two-phase writes to stabilize request type/data and then set `REQ_NEW`; completion is polled with a jiffies timeout and small `udelay()` sleeps. LCB CSR read/write commands need special packing of data across host command and external-device CSRs.

Link-state control is a state machine protected by `ppd->hls_lock`. `set_link_state()` validates transitions, performs required firmware commands and wait loops, updates `ppd->host_link_state`, updates userspace `statusp`, and dispatches `IB_EVENT_PORT_ACTIVE` when a port enters active. Polling/link-up transitions set local link attributes, optionally do quick link-up, wait for physical and logical state changes, enable receive port traffic, notify PIO/SDMA paths, and update transmit counters. Down/offline transitions route through `goto_offline()`, which updates LCB cache, commands physical offline, waits for firmware readiness, handles AOC transmitter disable, validates logical down, and records link-down reasons.

QSFP handling is workqueue-based and guarded by module-present checks. Initial start retries QSFP reads up to `MAX_QSFP_RETRIES`, spacing attempts by delayed work. QSFP reset temporarily masks `INT_N`, toggles reset, waits for module initialization, reenables interrupt notification, and disables transmitters for AOC setup. `qsfp_event()` restarts DC after reinsertion, refreshes cache if needed, restarts link, and reads 16 status bytes when interrupt flags need checking.

FM table programming is partly cached and partly live hardware mutation. VL arbitration tables are cached with per-table spinlocks and only reprogrammed when values differ. If the port is up and hardware generation requires it, `set_vl_weights()` drains data VLs before changing arbitration weights to avoid packets being stranded in a FIFO whose weight was set to zero. Buffer-control changes follow a stricter algorithm: adjust total credit bracket if needed, zero global/per-VL shared limits, wait on return-credit status, lower dedicated limits before raising, raise shared/global limits, then shrink total credits if needed.

Receive context enablement in `hfi1_rcvctrl()` has a substantial setup phase. On first enable it programs header queue DMA address, optional real tail DMA address, sequence count, cached head, zeroes the header queue to avoid stale sequence false positives, configures eager and expected TID ranges, initializes heads/tails, sets timeout/count after enable, and handles the control context's VL15 routing. Disable redirects tail updates to a dummy DMA address before clearing enable so hardware does not retain a stale user address.

Device initialization in `hfi1_init_dd()` is ordered to prevent hardware from generating traffic during reset and to preserve PCIe state across resets. The sequence first initializes per-port defaults, maps PCIe resources, saves PCI config, identifies implementation and HFI id, initializes shared ASIC/I2C state, resets the chip, reads platform/firmware configuration, performs PCIe Gen3 transition, seeds chip CSRs/memories, allocates AIP RX data, sizes contexts, initializes RXE/TXE/other blocks, initializes affinity and send/receive contexts, sets up ASPM, SDMA, MSI-X, LCB access, firmware load, thermal sensor, counters, and receive error tracking.

## State And Persistence Behavior

Persistent driver state is primarily held in `struct hfi1_devdata`, `struct hfi1_pportdata`, `struct hfi1_ctxtdata`, send contexts, SDMA engines, and shared `struct hfi1_asic_data`. Important fields mutated in this chunk include `dd->gi_mask`, `dd->dc8051_timed_out`, `dd->dc_shutdown`, `dd->vau`, `dd->vcu`, `dd->link_credits`, `dd->vl15_init`, `dd->num_rcv_contexts`, `dd->n_krcv_queues`, `dd->num_user_contexts`, `dd->num_netdev_contexts`, `dd->freectxts`, `dd->rcv_entries`, `dd->num_send_contexts`, `dd->cntrs`, `dd->scntrs`, `dd->last_tx`, `dd->last_rx`, `dd->asic_data`, and user refcount/completion state.

Per-port state includes link width/speed supported/enabled/active values, link-down reasons, `host_link_state`, `driver_link_ready`, `link_enabled`, `is_sm_config_started`, `actual_vls_operational`, `vls_operational`, thresholds, CRC settings, QSFP retry/cache/interrupt flags, status-page pointer, counter arrays, and VL arbitration caches.

Hardware state persists in CSRs until reset, FLR, DC reset, power transition, or explicit reprogramming. This chunk programs interrupt masks/maps/clears, send context checks, SDMA registers, receive context control/address/count registers, RcvArray/TID entries, RSM maps/rules, QP map table, partition keys, SC-to-VL tables, send length checks, credit merge limits, VL arbitration lists, DC port config, QSFP GPIO/mask/invert registers, LCB/DC8051 registers, error masks, counter arrays, and thermal polling state.

Some state is shared across two HFI functions on one ASIC. `init_asic_data()` finds a peer with matching base GUID and shares `dd->asic_data`, including ASIC resources and I2C setup. QSFP and thermal/SBus paths acquire chip resources to serialize hardware access.

Counter state has special persistence semantics. Synthetic counter arrays track extended values across hardware counter wraps; 32-bit counters are extended by remembering upper bits, while saturated counters stop changing at `CNTR_MAX`. A periodic timer checks flit tripwire counters and refreshes all synthetic counters before wrap risk grows too large.

## Dependencies And Integration Points

This code depends on HFI1 hardware CSR accessors and bit definitions from surrounding driver headers: `read_csr()`, `write_csr()`, `read_kctxt_csr()`, `write_kctxt_csr()`, `read_uctxt_csr()`, `write_uctxt_csr()`, CSR offsets, masks, and shift constants. It also depends on kernel primitives such as IRQ handlers, NAPI, workqueues, timers, mutexes, spinlocks, percpu allocation, refcounts, completions, PCI FLR, jiffies timeouts, and IB core event dispatch.

Major internal integration points include:

- SDMA: `sdma_engine_interrupt()`, `sdma_update_lmc()`, `sdma_map_init()`, `sdma_wait()`, `sdma_all_running()`, and `sdma_init()`.
- PIO/send contexts: `pio_select_send_context_vl()`, `sc_set_cr_threshold()`, `pio_send_control()`, `pio_reset_all()`, `pio_kernel_linkup()`, `init_sc_pools_and_sizes()`, `init_send_contexts()`, and `init_pervl_scs()`.
- Receive and packet steering: `hfi1_packet_present()`, receive header helpers, `hfi1_create_kctxts()`, `hfi1_alloc_rx()`, netdev context/RMT helpers, RSM rules, QP map, and TID/RcvArray code.
- Link management and firmware: DC8051 commands, LCB access ownership, firmware initialization/loading, platform config parsing, PCIe speed/transition/tuning, link-quality and link-down reason reads, and FM-ready waits.
- QSFP/I2C: `set_up_i2c()`, `one_qsfp_read()`, `set_qsfp_tx()`, `qsfp_mod_present()`, and chip resource acquisition.
- IB/OPA upper layers: IB port state/event values, OPA link widths/speeds/reasons, FM table get/set, PKey programming, status page updates visible to userspace, and sysfs counter reads.
- Error and power management: ASPM entry/exit/context disable, freeze handling, thermal emergency flow, receive error setup, and chip resource cleanup.

## Risks And Edge Cases

- `general_interrupt()` clears interrupt status before dispatching handlers. Handlers must tolerate edge/race behavior where hardware raises a new event after the clear but before or during handler execution.
- Receive EOI is race-prone by design. Removing the CSR tail fallback or the forced interrupt on packet-present can cause lost receive interrupts when DMA tail writes are not memory-visible.
- `do_8051_command()` is central and can block for firmware timeouts. Calling paths must not run in interrupt context if they may wait for seconds through link-state routines.
- The static `lcb_cache` is global to the compilation unit, not per-device. In multi-device scenarios, the cache content is not naturally partitioned by `dd`, which is safe only if usage expectations or serialization outside this chunk make cross-device contamination irrelevant.
- `goto_offline()` changes `ppd->host_link_state` before all operations complete. Failure paths can leave a transient state if callers do not repair state or retry carefully.
- Link state transitions require exact previous states except for a few explicit exceptions such as poll bounce and simulator quick link-up. Unexpected FM or interrupt-driven transitions return `-EINVAL`.
- `set_link_down_reason()` records reasons only when both latest local and neighbor reasons are zero. Later, potentially more informative reasons are ignored until higher-level code clears them.
- QSFP retry gives up after roughly 10 seconds. Slow or marginal modules may leave the link down without further automatic attempts unless another event restarts the flow.
- VL credit changes continue after `wait_for_vl_status_clear()` timeout, with explicit warning that credit loss may occur and link bounce may be required.
- `set_buffer_control()` mutates `new_bc` by zeroing invalid VL entries. Callers must not assume their input buffer remains unchanged for unsupported VLs.
- Receive context disable intentionally enables tail update to a dummy DMA address. Incorrect dummy DMA initialization would risk hardware writing to an invalid or stale address.
- Counter initialization marks unused receive-header overflow counters as disabled by mutating global `port_cntrs[]` flags based on this device's `num_rcv_contexts`; this is sensitive if heterogeneous devices with different context counts coexist.
- Reset paths are hardware revision and module-parameter dependent. `use_flr`, A0 handling, simulator/emulator branches, and PCI variable restore must stay in the documented order to avoid losing BAR/command state or leaving DC in reset.
- `hfi1_init_dd()` has many partially initialized failure exits. Cleanup labels must match exactly which resources have been allocated, or probe failure can leak resources or double-clean.
- Thermal emergency handling bypasses the full graceful link state machine to shut down quickly. This prioritizes hardware protection over normal link-down sequencing.

## Test Signals

Build and static checks:

- Compile the HFI1 driver with this file and related headers enabled, including configurations with SDMA, TID RDMA, PKey checking, netdev/AIP, and NAPI paths.
- Sparse/lockdep-style review should focus on IRQ context versus sleepable link-state paths, `hls_lock`, `dc8051_lock`, `irq_src_lock`, VL arbitration spinlocks, and chip resource locking.
- Error-injection or fault-injection builds should exercise each `hfi1_init_dd()` failure label after PCI setup, chip init, firmware init, RX allocation, context sizing, RXE init, affinity, send contexts, receive contexts, SDMA, interrupts, firmware load, counters, and receive-error init.

Runtime hardware signals:

- Interrupt tests should verify general, SDMA, receive threaded, and NAPI receive paths, including no-status SDMA interrupts and receive EOI packet-present races.
- Link tests should cover offline to polling to verify-cap to going-up to init/armed/active, active to offline/disabled, poll bounce, quick link-up, simulator/emulator branches, loopback modes, and failed LNI state decoding.
- QSFP tests should cover module absent/present, reset, false `INT_N` during initialization, alarm/warning status bytes, AOC transmitter disable, read retry exhaustion, and reinsertion restart.
- FM/MAD tests should set/get VL arbitration tables, buffer control, SC2VLnt mapping, MTU, PKeys, link widths, link speeds, operational VLs, and LMC while the link is down and up.
- Credit and VL tests should monitor `SEND_CM_CREDIT_USED_STATUS`, SDMA/PIO map updates, drained VL behavior, and packet egress after changing arbitration weights or credit limits.
- Receive context tests should enable/disable contexts repeatedly, validate header queue zeroing, tail update DMA address changes, urgent and available interrupts, one-packet eager mode, TID flow toggles, and dummy tail safety.
- RSM/QOS/FECN/AIP tests should validate packet steering across kernel, user, TID RDMA, netdev, and control contexts, including RMT exhaustion behavior and rule reference counting.
- Counter tests should read sysfs counter names/values, force 32-bit wrap patterns, validate synthetic saturation, and ensure timer/workqueue cleanup races are absent during device removal.
- Reset/probe tests should run with and without FLR, on silicon/simulator/emulator variants, and verify CSR defaults, interrupt mapping self-test in VM-like topologies, PCIe variable restoration, firmware load, and LCB access initialization.
- Thermal tests should validate `hfi1_tempsense_rd()` on silicon, rejection on unsupported implementations, thermal sensor SBus initialization, and critical-temperature freeze/offline/DC-shutdown behavior.

## Cross-Chunk Notes

The chunk starts after earlier interrupt source table definitions and helper declarations, so the final merged per-file research should connect `is_interrupt()` to the `is_table` entries defined before line 8252. Several functions called here, such as wait helpers, DC start/shutdown helpers, counter tables, SDMA/PIO helpers, and firmware/platform routines, are defined elsewhere in `chip.c` or neighboring HFI1 files. The merge lane should reconcile those definitions with this chunk's control-flow summary before producing the final per-file report.
