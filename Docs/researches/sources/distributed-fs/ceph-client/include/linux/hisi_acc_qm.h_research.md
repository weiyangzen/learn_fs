# sources/distributed-fs/ceph-client/include/linux/hisi_acc_qm.h

## Purpose
`hisi_acc_qm.h` is the shared framework header for HiSilicon accelerator Queue Manager devices. It defines hardware register constants, mailbox and doorbell encodings, capabilities, queue-manager and queue-pair state, DMA buffers, debugfs/DFX state, error recovery hooks, SR-IOV/uacce integration, scatter-gather mapping helpers, and common lifecycle APIs.

## Important APIs, Types, And Functions
Major types include `struct hisi_qm`, `struct hisi_qp`, `struct hisi_qm_status`, `struct hisi_qp_status`, `struct hisi_qm_err_ini`, `struct hisi_qm_err_info`, `struct qm_debug`, `struct qm_err_isolate`, `struct qm_rsv_buf`, `struct hisi_qm_list`, and `struct hisi_qm_cap_tables`. Public APIs include `hisi_qm_init()`, `hisi_qm_start()`, `hisi_qm_stop()`, `hisi_qp_send()`, SR-IOV configure helpers, error handlers, mailbox helpers, SGL map/unmap and pool helpers, QP allocation/free, algorithm register/unregister, PM hooks, DFX access/register dump helpers, capability query helpers, and PF driver accessors for migration.

## Control Flow And State
PCI accelerator drivers initialize `hisi_qm`, allocate DMA rings for SQC/CQC/EQ/AEQ and queue pairs, configure capabilities, start the QM, register algorithms/uacce, and submit messages through QPs. Completion/event queues and polling work update queue state. Reset/error flows stop QPs or functions, collect DFX registers, isolate devices after thresholds, and recover or request reset based on `hisi_qm_err_ini` callbacks. SR-IOV paths configure PF/VF resources and VF state. Persistent runtime state spans MMIO bases, DMA addresses, IDR-managed QPs, locks, workqueues, debugfs files, atomic flags/counters, and capability tables.

## Dependencies And Integration Points
It depends on PCI, DMA, debugfs, iopoll, module parameters, bitfield helpers, uacce, crypto accelerator drivers, VFIO ACC live migration, workqueues, IDR, scatterlists, and PCI error recovery.

## Risks
Risks include hardware register bit drift between QM versions, queue-depth/base mismatch, mailbox timeout/deadlock, DMA mapping leaks, QP state races during reset, SR-IOV PF/VF resource accounting errors, uacce SVA mode validation, debugfs access during reset, and module parameter bounds. Error isolation state needs correct locking to avoid masking recoverable devices or continuing on fatal ECC.

## Test Signals
Run accelerator driver probe/remove, QP allocation/send/completion, mailbox read/write timeout injection, SR-IOV enable/disable/configure, PCI error recovery, suspend/resume, reset storms, debugfs DFX reads/clears, SGL map/unmap under DMA API debug, uacce mode validation, and VFIO migration PF driver lookup.
