# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_isr.c

## Purpose
`csio_isr.c` implements the interrupt service layer for CSIostor. It handles non-data/slow-path interrupts, firmware event queue interrupts, SCSI completion queue interrupts, combined INTx/MSI interrupts, MSI-X vector naming and requesting, interrupt mode selection, MSI-X vector reduction/affinity distribution, and interrupt teardown.

## Important APIs and Functions
- `csio_nondata_isr()` handles MSI-X non-data interrupts: slow hardware interrupt causes, mailbox ISR, and scheduling of the event worker.
- `csio_fwevt_handler()` drains the firmware-event ingress queue through `csio_fwevtq_handler()` and schedules `evtq_work`.
- `csio_fwevt_isr()` is the MSI-X firmware-event ISR; `csio_fwevt_intx_handler()` is the work-request callback used in INTx mode.
- `csio_process_scsi_cmpl()` converts SCSI completion WRs into driver request state transitions, including abort/close special handling and protection against double completion after abort timeout races.
- `csio_scsi_isr_handler()` drains an ingress queue with `csio_wr_process_iq()`, invokes each completed request callback, frees DDP buffers if used, and returns ioreqs to the SCSI freelist.
- `csio_scsi_isr()` is the MSI-X SCSI ISR; `csio_scsi_intx_handler()` is the INTx callback.
- `csio_fcoe_isr()` is the shared INTx/MSI ISR for slow-path, forward interrupt queue, mailbox, and firmware event scheduling.
- `csio_request_irqs()` requests either one INTx/MSI line or the MSI-X vector set for non-data, firmware event, and per-port/per-CPU SCSI queues.
- `csio_enable_msix()` allocates MSI-X vectors with affinity sets and reduces queue sets if fewer vectors are available.
- `csio_intr_enable()` chooses MSI-X, MSI, or INTx based on `csio_msi`, firmware queue limits, and vector allocation results.
- `csio_intr_disable()` disables hardware interrupts, frees requested IRQs when asked, frees vectors, and clears host interrupt state.

## Control Flow and State
The preferred MSI-X flow splits work by vector: non-data handles slow hardware and mailbox events, firmware-event handles FCoE/port/mailbox event queue messages, and each SCSI vector handles one ingress queue. In MSI/INTx mode, `csio_fcoe_isr()` disables INTx at the PF if needed, handles slow interrupts, processes the forward interrupt queue, handles mailbox completion, then schedules the event worker when new firmware events are pending.

`CSIO_HWF_FWEVT_PENDING` prevents redundant scheduling of `hw->evtq_work`. `hw->intr_mode`, `hw->msix_entries`, `hw->sqset[*][*].intr_idx`, `hw->fwevt_intr_idx`, and `hw->nondata_intr_idx` persist the interrupt topology selected during queue configuration.

## Dependencies and Integration Points
The file uses Linux interrupt, PCI, CPU affinity, and cpumask APIs. It integrates with `csio_hw_slow_intr_handler()`, mailbox ISR/completions, work-request ingress processing, SCSI completion state machine, and queue/IRQ data allocated by `csio_config_queues()`.

## Risks and Edge Cases
- All ISR paths first reject null device data and offline PCI channels; missing this check in new handlers could touch dead MMIO.
- `csio_process_scsi_cmpl()` explicitly handles abort timeout races by checking whether `csio_scsi_cmnd(ioreq)` is null; regressions could double-complete commands.
- `csio_request_irqs()` frees vectors on partial MSI-X request failure using already assigned `dev_id`s; vector count and `entryp[k]` must remain synchronized.
- `csio_intr_disable(free=true)` loops over `hw->num_sqsets + CSIO_EXTRA_VECS`; this must match the number of successfully requested vectors after any queue-set reduction.
- MSI/INTx fallback can reduce SCSI queue sets when firmware supports fewer IQs; tests should cover low-vector and low-queue firmware configurations.

## Test Signals
Runtime signals include correct interrupt mode log, requested vector names, SCSI completion callbacks firing once per command, firmware events processed by `evtq_work`, and mailbox completions moving from ISR to event worker. Fault tests should inject PCI channel offline, partial IRQ request failure, low MSI-X vector count, abort completion races, and INTx interrupt masking/unmasking behavior.
