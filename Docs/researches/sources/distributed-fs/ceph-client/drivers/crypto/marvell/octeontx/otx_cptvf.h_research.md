# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf.h

### Purpose
`otx_cptvf.h` defines the OcteonTX CPT virtual-function runtime state, queue structures, readiness flags, and VF-to-PF mailbox APIs used by the VF driver, request manager, and algorithm layer.

### Important APIs, Types, And Functions
Important macros include `OTX_CPT_FLAG_DEVICE_READY`, `otx_cpt_device_ready()`, command queue length/chunk size, and one queue per VF. Types include `struct otx_cpt_cmd_chunk`, `struct otx_cpt_cmd_queue`, `struct otx_cpt_cmd_qinfo`, `struct otx_cpt_pending_qinfo`, `struct otx_cptvf_wqe`, `struct otx_cptvf_wqe_info`, and `struct otx_cptvf`. Declared APIs send VF up/down, group, priority, queue-size, and ready mailbox messages; handle mailbox interrupts; and ring the VQ doorbell.

### Control Flow, State, And Persistence
The VF probe allocates `struct otx_cptvf`, configures command and pending queues, stores PF-assigned VF ID/type/group data from mailbox replies, and sets the ready flag after hardware queue initialization. Queue state persists while the PCI VF is bound and is consumed by request submission and completion tasklets. Mailbox `pf_acked` and `pf_nacked` fields are transient polling flags.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on interrupt, device, common mailbox, and request-manager definitions. Risks include fixed one-queue assumptions, using `u8` fields for VF and group counts, tasklet lifetime versus PCI remove, and `pf_acked` polling without stronger synchronization. Test signals include VF probe/remove, queue allocation/free, mailbox timeout and NACK paths, request submission only after ready flag, and sysfs reads of VF type and group.
