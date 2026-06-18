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
