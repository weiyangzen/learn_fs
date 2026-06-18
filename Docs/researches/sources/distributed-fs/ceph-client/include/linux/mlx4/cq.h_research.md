# sources/distributed-fs/ceph-client/include/linux/mlx4/cq.h

## Purpose
Defines mlx4 CQE layouts, status/opcode/syndrome masks, CQ moderation limits, and inline CQ doorbell helpers.

## Important APIs/Types
Structures include `mlx4_cqe`, `mlx4_err_cqe`, and packed `mlx4_ts_cqe`. Enums define tunnel/VLAN/QPN flags, owner/send/opcode masks, error syndromes, L3/L4 status bits, bad-FCS/LLC/SNAP flags, and CQ doorbell request commands. `mlx4_cq_arm` updates the arm record, issues `wmb()`, and rings MMIO via `mlx4_write64`; `mlx4_cq_set_ci` updates CI. APIs modify and resize CQs.

## Control Flow
Consumers process CQEs, advance `cons_index`, write CI, and arm interrupts. Arming persists host memory before ringing device MMIO.

## State And Persistence
CQ state lives in `struct mlx4_cq`: CQN, consumer index, arm sequence, doorbell records, vector, callbacks, refcount, and tasklet/reset context. Rings and doorbells are DMA-visible.

## Dependencies And Integration Points
Depends on mlx4 device and doorbell headers plus Ethernet constants. Integrates with EQ interrupts, RDMA/Ethernet completions, timestamping, resize/moderation commands, and tasklet dispatch.

## Risks
Missing memory barrier, owner-bit wrap mistakes, endian errors, timestamp/64-byte CQE layout mismatches, and invalid moderation limits.

## Test Signals
Send/receive completions, error syndromes, VLAN/tunnel checksum flags, timestamp CQEs, interrupt arming, CI updates, moderation, resize, and wraparound handling.
