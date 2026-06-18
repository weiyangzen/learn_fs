# sources/distributed-fs/ceph-client/include/linux/mlx4/driver.h

## Purpose
Defines mlx4 auxiliary-driver and event-notifier interfaces used by protocol drivers layered on mlx4_core.

## Important APIs/Types
Defines `MLX4_ADEV_NAME`, `MLX4_MAC_MASK`, `enum mlx4_dev_event`, `MLX4_INTFF_BONDING`, and `struct mlx4_adrv` embedding `auxiliary_driver` with protocol and flags. APIs register/unregister auxiliary drivers and event notifiers and return devlink ports.

## Control Flow
Protocol drivers register `mlx4_adrv` and bind to auxiliary devices. Event subscribers register notifier blocks and receive port, catastrophic, and slave lifecycle events.

## State And Persistence
Registered drivers and notifier blocks persist until unregister. Devlink port objects are core-owned.

## Dependencies And Integration Points
Depends on devlink, auxiliary bus, notifier infrastructure, and mlx4 device definitions. Integrates with mlx4_en, mlx4_ib, bonding-aware protocols, devlink, and mlx4_core event dispatch.

## Risks
Notifier lifetime bugs, unregister while events are in flight, protocol mismatches, and stale devlink port pointers.

## Test Signals
Aux driver probe/remove, notifier delivery, bonding flag behavior, devlink port lookup, and teardown during event generation.
