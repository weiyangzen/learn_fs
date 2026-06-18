# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp10b.c

## Purpose
Adapts GP100 fault handling for GP10B/Tegra by using a physical memory address pin instead of BAR2 while reusing GP100 buffer control.

## Important APIs, types, and functions
Exports `gp10b_fault_new()` and `gp10b_fault_buffer_pin()`.

## Control flow
Construction installs a function table identical to GP100 except the pin hook returns `nvkm_memory_addr()` for the instance memory. Init/fini/info/intr reuse GP100 helpers.

## State and persistence
State is inherited from common fault and GP100 buffer metadata. Persistent hardware state is the GP100-style buffer registers programmed with a direct memory address.

## Dependencies and integration points
Depends on common fault base, GP100 helper exports, and Tegra-compatible memory addressing.

## Risks
Using BAR2 on Tegra would be wrong; using direct physical address on non-Tegra would also be wrong. The distinction is entirely in this pin hook.

## Test signals
GP10B fault buffer initialization, correct memory address programmed, event notification on GPU faults, and absence of BAR2 dependency.
