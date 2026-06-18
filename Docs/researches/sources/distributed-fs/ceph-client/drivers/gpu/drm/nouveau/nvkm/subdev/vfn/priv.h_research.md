# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/priv.h

## Purpose
Defines private VFN function tables and helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_vfn_func` includes optional dtor, interrupt function/data, and user aperture/class metadata. It declares `r535_vfn_new()`, `nvkm_vfn_new_()`, `tu102_vfn_intr`, and `nvkm_uvfn_new()`.

## Control Flow
Chip files populate this table and base construction consumes it to build subdevices and user objects.

## State, Persistence, And Dependencies
No runtime state is held in the header; it defines the ABI for `struct nvkm_vfn` construction.

## Integration Points
Integrates VFN chip wrappers, R535 RM-backed construction, interrupt helpers, and UVFN object mapping.

## Risks
Function table changes affect native and RM-managed VFN paths. User aperture fields must remain consistent with mapping code.

## Test Signals
Compile-time coverage and creation of usermode objects across Volta/Turing/Ampere are the primary signals.
