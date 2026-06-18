# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.h

## Purpose
This header declares the reset map and provider state used by sunxi-ng CCU reset controllers.

## Important APIs, Types, And Functions
It defines `struct ccu_reset_map`, `struct ccu_reset`, `rcdev_to_ccu_reset()`, and `ccu_reset_ops`.

## Control Flow
No runtime flow exists here; provider code fills the map and `ccu_common.c` registers the controller.

## State And Persistence
State fields include MMIO base, reset map pointer, shared lock, and embedded `reset_controller_dev`.

## Dependencies And Integration Points
It depends on reset-controller and spinlock headers. Integration is through every sunxi-ng SoC descriptor exposing resets.

## Risks
The map is indexed by public reset IDs, so missing or reordered entries break DT reset specifiers.

## Test Signals
Build and reset-controller probe/use tests validate it.
