# sources/distributed-fs/ceph-client/include/linux/mlx4/srq.h

## Purpose
Provides mlx4 shared receive queue WQE next-segment layout and SRQ lookup API.

## Important APIs/Types
`struct mlx4_wqe_srq_next_seg` stores reserved fields and big-endian `next_wqe_index`. `mlx4_srq_lookup` resolves an SRQ number to `struct mlx4_srq`.

## Control Flow
SRQ users build linked receive WQEs and event/completion paths look up SRQs by SRQN.

## State And Persistence
The WQE next segment is DMA-visible queue state. SRQ objects and lookup tables persist from allocation to free.

## Dependencies And Integration Points
Depends on `mlx4_dev` and `mlx4_srq` definitions. Integrates with RDMA receive management, SRQ events, CQ completions, and firmware SRQ commands.

## Risks
Endian mistakes in next indices, corrupted free lists, lookup after teardown, and event handling without a stable reference.

## Test Signals
SRQ allocation/free, WQE chain integrity, SRQN lookup, limit/last-WQE events, and teardown with outstanding completions.
