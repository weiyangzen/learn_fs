<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h

## Purpose
`nic0_umr0_0_completion_queue_ci_1_regs.h` defines a two-register NIC UMR aperture used to submit or expose completion-queue consumer-index updates for NIC0 UMR0_0 lane/index 1.

## Important APIs, types, and functions
The exported macros are `mmNIC0_UMR0_0_COMPLETION_QUEUE_CI_1_CQ_NUMBER` and `mmNIC0_UMR0_0_COMPLETION_QUEUE_CI_1_CQ_CONSUMER_INDEX`. There are no C functions or types.

## Control flow
No code executes in the header. Runtime queue completion handling writes or maps a completion queue number and its consumer index through this UMR window so hardware can observe CQ progress. Correct sequencing is generally CQ selection followed by CI update, with ordering handled by the register access path or mapped doorbell semantics.

## State and persistence
The hardware aperture holds the currently written CQ number and consumer index. It is transient queue state and is reset or overwritten as completions are consumed. The header stores no software state.

## Dependencies and integration points
The file is included by `gaudi2_regs.h` and is related to NIC QPC/QMAN completion handling. It pairs with `nic0_umr0_0_unsecure_doorbell0_regs.h` for user-mapped or unsecure NIC submission/control apertures and with replicated UMR offsets via `NIC_UMR_OFFSET`.

## Risks and test signals
The risk is off-by-instance or off-by-CQ writes: updating the wrong consumer index can stall a CQ or falsely free entries. Test signals include CQ CI movement visible to hardware, no CQ overflow under high completion rates, correct behavior for UMR0_0 versus replicated UMR windows, and completion processing recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h -->
