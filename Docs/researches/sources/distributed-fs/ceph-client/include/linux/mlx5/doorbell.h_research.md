# sources/distributed-fs/ceph-client/include/linux/mlx5/doorbell.h

## Purpose
Defines mlx5 BlueFlame/CQ doorbell offsets and a low-level 64-bit MMIO write helper.

## Important APIs/Types
`MLX5_BF_OFFSET` and `MLX5_CQ_DOORBELL` are UAR offsets. `mlx5_write64` writes two big-endian 32-bit words as one raw 64-bit write on 64-bit builds or two raw 32-bit writes on 32-bit builds.

## Control Flow
Callers prepare doorbell words, perform needed ordering, and call `mlx5_write64` to notify hardware. The helper itself does not lock on 32-bit systems.

## State And Persistence
No software state is stored. MMIO writes update hardware UAR state and trigger CQ/send processing.

## Dependencies And Integration Points
Integrates with mlx5 CQ arming, send queue ringing, BlueFlame writes, and UAR mappings.

## Risks
Assuming 32-bit atomicity, missing caller-side locking, missing memory barriers, and raw write ordering mistakes.

## Test Signals
CQ doorbells, BlueFlame/send ringing, 32-bit locking review, concurrent doorbell stress, and hardware progress after barriers.
