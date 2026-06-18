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
