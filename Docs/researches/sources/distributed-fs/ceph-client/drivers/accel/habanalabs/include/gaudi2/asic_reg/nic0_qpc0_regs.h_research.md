<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h

## Purpose
`nic0_qpc0_regs.h` is the generated register map for NIC0 QPC0, the queue-pair context/control block used by Gaudi2 NIC offload. It defines request/response QPC cache controls, gateway access to QPC entries, congestion-control tuning, doorbell handling, event and congestion queues, work-queue bases, interrupt controls, and debug counters.

## Important APIs, types, and functions
The file exports `mmNIC0_QPC0_*` macros. Major groups are request/response QPC cache invalidate/status/static/base/clean-list registers; error FIFO configuration, indices, masks, credits, and base addresses; gateway busy/control/data/mask registers; congestion-control parameters (`CC_*` alpha, threshold, window, timeout, rollback); doorbell FIFO override/config arrays; secured and privileged doorbell words; QPC debug/status counters; interrupt base/data/cause/mask/clear/en/config registers; response/request ring PI/CI/CFG registers; event and congestion queue base/log-size/producer/consumer/index callback registers; QMAN doorbell bridge registers; TX/RX WQ base, size, MMU bypass, thresholds, and backpressure registers; and static/dynamic WQE template registers.

## Control flow
No code executes here. NIC bring-up configures QPC static state, cache bases, error/event/congestion queues, doorbell security, and WQ templates. Runtime packet submission or RDMA-like operation updates doorbells and queue indices; hardware uses the QPC cache and gateway state to fetch/modify queue-pair contexts. Error and congestion flows push records into FIFOs or queues and raise interrupts through the mapped interrupt registers.

## State and persistence
Hardware persists QPC cache content, queue-pair context pointers, doorbell FIFO state, congestion windows, retry counters, event/congestion queue indices, and WQ configuration until reset or reinitialization. Gateway registers provide a transient read/modify/write path into internal QPC state. The header itself has no software-owned state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block integrates with NIC firmware, kernel NIC setup, userspace queue provisioning, MSI/MSI-X interrupt routing, security/privilege doorbell policy, and MMU bypass decisions for work queues.

## Risks and test signals
Misconfigured QPC registers can corrupt queue-pair state, lose doorbells, disable congestion control, or misroute event completions. Cache invalidation requires polling the correct status bits; proceeding early can use stale QP state. Test signals include QPC cache invalidation completion, successful secured and privileged doorbell paths, event/congestion queue PI/CI movement, interrupts on injected QP errors, and stable TX/RX WQ operation under congestion and timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h -->
