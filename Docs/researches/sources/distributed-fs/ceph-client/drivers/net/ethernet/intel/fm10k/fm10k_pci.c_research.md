# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pci.c

## Purpose
`fm10k_pci.c` implements PCI driver binding and the hardware lifecycle for fm10k devices. It contains PCI IDs, MMIO/config-space accessors, service and MAC/VLAN work scheduling, reset and detach recovery, watchdog/statistics subtasks, hardware Tx/Rx ring programming, MSI-X interrupt request/free logic, mailbox IRQ handlers and TLV handlers, interface up/down sequencing, software initialization, PCI probe/remove, power management, PCI error recovery, SR-IOV hooks, and PCI driver registration.

## Important APIs, types, and functions
PCI binding is defined by `fm10k_pci_tbl`, `fm10k_driver`, `fm10k_register_pci_driver()`, and `fm10k_unregister_pci_driver()`. Register access uses `fm10k_read_pci_cfg_word()` and `fm10k_read_reg()`, both of which handle surprise removal indicators.

Work and reset orchestration is handled by `fm10k_service_event_schedule()`, `fm10k_service_task()`, `fm10k_macvlan_schedule()`, `fm10k_macvlan_task()`, `fm10k_prepare_for_reset()`, `fm10k_handle_reset()`, `fm10k_detach_subtask()`, `fm10k_reset_subtask()`, and watchdog helpers for host state, stats, Tx flushing, and hang checks.

Hardware programming uses `fm10k_configure_tx_ring()`, `fm10k_enable_tx_ring()`, `fm10k_configure_tx()`, `fm10k_configure_rx_ring()`, `fm10k_update_rx_drop_en()`, `fm10k_configure_dglort()`, `fm10k_configure_rx()`, `fm10k_up()`, and `fm10k_down()`. Interrupt and mailbox handling use `fm10k_mbx_request_irq()`, `fm10k_mbx_free_irq()`, `fm10k_qv_request_irq()`, `fm10k_qv_free_irq()`, `fm10k_msix_clean_rings()`, `fm10k_msix_mbx_vf()`, and `fm10k_msix_mbx_pf()`.

Probe/remove and platform integration are provided by `fm10k_sw_init()`, `fm10k_probe()`, `fm10k_remove()`, `fm10k_suspend()`, `fm10k_resume()`, `fm10k_io_error_detected()`, `fm10k_io_slot_reset()`, `fm10k_io_resume()`, `fm10k_io_reset_prepare()`, and `fm10k_io_reset_done()`.

## Control flow
Probe validates PCI error state, enables memory access, sets a 48-bit or 32-bit coherent DMA mask, claims BARs, enables bus mastering, allocates a netdev, maps BAR0, initializes hardware/software state, initializes queueing and mailbox IRQs, confirms hardware readiness, registers the netdev, starts the service timer/work, logs link status/MAC, configures SR-IOV, and schedules initial service work. Error unwinds release mailbox IRQs, queueing, debugfs, mappings, netdev, BARs, and the PCI device in reverse order.

Service work is the long-running control loop. The timer schedules `fm10k_service_task()`, which checks surprise detach/recovery, processes upstream and downstream mailboxes, handles requested resets, updates link carrier based on host readiness, updates stats once per second, flushes Tx by reset if link is down with pending DMA, and periodically arms Tx hang detection plus interrupt strobes.

Reset preparation stops MAC/VLAN work, takes rtnl, suspends SR-IOV, closes the netdev if running, frees mailbox IRQs and queueing scheme, records a reset delay, and releases rtnl. Reset handling restores bus mastering, resets and initializes hardware, rebuilds queueing, requests mailbox IRQs, checks hardware, updates VF MAC/VLAN feature state, reopens the netdev if it was running, resumes SR-IOV, resumes MAC/VLAN work, and clears `__FM10K_RESETTING`.

`fm10k_up()` starts hardware DMA, programs Tx/Rx descriptor rings, programs interrupt moderation, enables NAPI, restores Rx filters, starts netdev queues, and kicks the service timer. `fm10k_down()` stops carrier/queues, resets Rx filters, disables NAPI, captures stats, waits out concurrent stats updates, attempts graceful Tx DMA drain, stops hardware, and cleans all rings.

Mailbox IRQ flow differs for PF and VF. VF mailbox IRQs process the upstream mailbox, mark host-state refresh, schedule service work, and reenable the VF ITR. PF mailbox IRQs read/ack EICR, report hardware faults, reset drop-on-empty queues after max-hold-time events, process the switch-manager mailbox and VF events under mailbox lock, handle switch ready/not-ready transitions, schedule service work, and reenable mailbox ITR.

## State and persistence behavior
PCI state lives in `struct fm10k_intfc` and `struct fm10k_hw`: mapped MMIO addresses, PCI device pointer, netdev pointer, service timer/work, delayed MAC/VLAN work, interface flags/state bits, host readiness, link-down debounce time, reset timestamps, hardware statistics, queue/ring arrays, MSI-X entries, mailbox state, RSS/RETA state, and SR-IOV data. The state is runtime-only and reconstructed on reset, resume, error recovery, and probe.

The service scheduler uses bit flags (`__FM10K_SERVICE_DISABLE`, `__FM10K_SERVICE_SCHED`, `__FM10K_SERVICE_REQUEST`) to avoid lost work while coalescing requests. The MAC/VLAN scheduler uses analogous bits to throttle mailbox submissions. Surprise removal is represented by clearing `hw->hw_addr` and detaching the netdev; recovery restores it from `uc_addr` and runs the reset path.

Hardware persistent effects are MMIO register writes for descriptor base/len/head/tail, interrupt mapping/masking, DGLORT/RSS/RETA, mailbox interrupt causes, and logical port/VF state through hardware ops. These are replayed after reset rather than stored on disk.

## Dependencies and integration points
The file depends on the Linux PCI, MSI-X, interrupt, PM, PCI error recovery, DMA, timer/workqueue, rtnl, netdev carrier/queue, NAPI, and SR-IOV frameworks. It integrates with `fm10k_main.c` for queueing scheme and datapath cleanup, `fm10k_netdev.c` for open/close/filter state, `fm10k_mbx.c` for mailbox ops, IOV support for VF lifecycle and mailbox events, DCB support for priority mapping, debugfs hooks, and hardware-specific MAC/IOV operation tables from `fm10k_info`.

The PCI driver registration is invoked by module init in `fm10k_main.c`. `fm10k_mbx_request_irq()` binds mailbox TLV handlers for VF or PF mode, so mailbox message handling is coupled to PCI role.

## Risks and edge cases
Reset and remove paths have high concurrency risk: service work, MAC/VLAN delayed work, netdev open/close, mailbox IRQs, SR-IOV, and PM/error recovery all interact. The code uses state bits, rtnl, work cancellation, mailbox spinlocks, and detach checks to serialize key paths. A missed bit clear can suppress future service or MAC/VLAN processing.

Surprise PCIe removal is handled by detecting all-ones MMIO reads, clearing `hw_addr`, detaching the netdev, and later probing `uc_addr` for recovery; any register access path that bypasses `fm10k_read_reg()` could violate that model. Tx DMA drain can time out, leading to warning and forced stop. PF fault handling resets VF resources and reconnects VF mailboxes, but malicious or repeatedly faulty VFs may require administrator intervention.

Mailbox IRQ setup must register sorted TLV handlers before connecting. `fm10k_mbx_free_irq()` disconnects mailbox before masking/freeing IRQ, so callers must avoid holding locks that the disconnect process may need. Traffic-class or reset failures can leave the netdev detached and require user-visible recovery.

## Test signals
Validation should include PCI probe/remove, module unload, open/close, reset request via Tx timeout, mailbox IRQ activity for PF and VF, SR-IOV enable/disable and VF FLR, suspend/resume, PCI AER slot reset, manual function reset, surprise-removal simulation, host ready/not-ready link transitions, DGLORT/RSS programming after reset, max-hold-time/drop-on-empty recovery, and service/MACVLAN rescheduling under mailbox pressure. Logs to watch include PCIe link lost/restored, reset failures, Tx DMA drain warnings, mailbox request IRQ failures, logical port map failures, fault reports, and invalid MAC/VLAN reset triggers.
