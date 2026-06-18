# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cq.c

## Purpose
`cq.c` implements mlx4 completion queue lifecycle, resizing, polling, arming, CQE decoding, software flush completions, and CQ cleanup for QP teardown.

## Important APIs, Types, And Functions
Creation APIs are `mlx4_ib_create_cq()` and `mlx4_ib_create_user_cq()`. `mlx4_ib_resize_cq()` handles kernel and user CQ resizing. `mlx4_ib_destroy_cq()` frees hardware and memory resources. Runtime APIs include `mlx4_ib_poll_cq()`, `mlx4_ib_arm_cq()`, `mlx4_ib_modify_cq()`, `mlx4_ib_cq_clean()`, and `__mlx4_ib_cq_clean()`. Internal helpers handle CQE ownership (`get_sw_cqe()`), buffer allocation/Mtt setup, outstanding CQE count, resize CQE copying, error syndrome mapping, IPoIB checksum flags, tunnel metadata extraction, and single-CQE translation in `mlx4_ib_poll_one()`.

## Control Flow
CQ creation rounds requested entries to a power-of-two-plus-one ring, initializes locks and QP lists, maps user memory/doorbell or allocates kernel doorbell/buffer, writes MTTs, and calls `mlx4_cq_alloc()`. Resizing allocates a new buffer or user umem, asks hardware to resize, then swaps buffers; kernel resize copies outstanding CQEs after a resize marker. Polling locks the CQ, emits software flush completions if the device is in internal error, otherwise repeatedly checks owner bits, handles resize markers, finds the QP, advances send/recv/SRQ tails, maps errors or opcodes into `ib_wc`, fills addressing/checksum metadata, updates consumer index, and unlocks. Cleanup sweeps unpolled CQEs for a QPN and compacts the ring.

## State And Persistence
`struct mlx4_ib_cq` owns an mlx4 CQ object, buffer/MTT, doorbell, resize buffer/umem, consumer index, lock, resize mutex, and send/recv QP lists. CQE ownership bits and consumer index coordinate hardware/software ring state. No state persists after CQ destruction.

## Dependencies And Integration Points
The file depends on mlx4 core CQ, MTT, buffer, doorbell, QP, and SRQ APIs; RDMA uverbs CQ ABI; mlx4 QP/SRQ driver structures; IPoIB checksum semantics; proxy SQP tunnel headers for SR-IOV; and RDMA core CQ polling/arming callbacks.

## Risks
CQE parsing is highly hardware-specific, especially 64-byte CQE offset handling, owner-bit logic, resize markers, and opcode/status decoding. User CQ creation rejects pre-provided umem when software CQ init is required, which must match userspace ABI expectations. `mlx4_ib_poll_one()` assumes QP lookup succeeds; stale CQEs during teardown depend on CQ locking and cleanup ordering. Internal-error software completions require accurate QP list maintenance. CQ clean ring compaction must preserve owner bits or polling can lose/duplicate CQEs.

## Test Signals
Test kernel and user CQ creation, timestamp flag validation, doorbell mapping failure, MTT write failure, resize up/down with outstanding CQEs, poll of send/recv/SRQ/XRC completions, every error syndrome, immediate/invalidate/atomic/LSO/FMR opcodes, RoCE VLAN/SMAC and IP checksum flags, proxy SQP tunnel completions, internal-error software flush, arm modes, CQ clean during QP reset, and destroy after resize failure.
