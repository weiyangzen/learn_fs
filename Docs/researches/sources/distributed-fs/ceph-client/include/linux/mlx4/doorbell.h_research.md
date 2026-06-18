# sources/distributed-fs/ceph-client/include/linux/mlx4/doorbell.h

## Purpose
Defines mlx4 send/CQ doorbell offsets and portable 64-bit MMIO doorbell write support.

## Important APIs/Types
`MLX4_SEND_DOORBELL` and `MLX4_CQ_DOORBELL` are UAR offsets. On 64-bit builds, doorbell locks are no-ops and `mlx4_write64` emits a raw 64-bit write. On 32-bit builds, macros declare/init/pass a spinlock and `mlx4_write64` serializes two 32-bit writes.

## Control Flow
Callers compose two big-endian words, perform ordering as needed, then call `mlx4_write64` to ring hardware.

## State And Persistence
No persistent software state except caller-owned locks on 32-bit. MMIO writes update device state.

## Dependencies And Integration Points
Depends on IO accessors and types. Integrates with CQ arming, send queue ringing, UAR mappings, and architecture word-size handling.

## Risks
Missing ordering, no 32-bit lock, endian mistakes, and raw MMIO ordering assumptions.

## Test Signals
CQ/send doorbell delivery on 64/32-bit, lockdep for 32-bit lock use, CQ interrupt generation, send progress, and concurrent doorbell stress.
