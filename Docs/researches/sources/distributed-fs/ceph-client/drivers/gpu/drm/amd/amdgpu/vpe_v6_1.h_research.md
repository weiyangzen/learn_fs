# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.h

## Purpose
`vpe_v6_1.h` is the local interface for installing VPE 6.1 hardware callbacks into an `amdgpu_vpe` instance.

## Important APIs, Types, And Functions
It includes `amdgpu_vpe.h` and declares `void vpe_v6_1_set_funcs(struct amdgpu_vpe *vpe);`.

## Control Flow
Generic VPE initialization includes this header and calls `vpe_v6_1_set_funcs()` when the discovered VPE IP version should use the 6.1 implementation. After that, generic VPE code calls through the installed function table.

## State And Persistence
The header owns no state. The declared function mutates `vpe->funcs` and `vpe->trap_irq.funcs` in `vpe_v6_1.c`.

## Dependencies And Integration Points
This file bridges generic VPE code (`amdgpu_vpe.c`/`amdgpu_vpe.h`) to the version-specific implementation. Its correctness depends on `struct amdgpu_vpe` being defined by `amdgpu_vpe.h`.

## Risks
Direct risk is low. The main risk is interface drift: if generic VPE initialization changes the callback-install contract, this declaration and implementation must stay synchronized.

## Test Signals
Compile coverage catches declaration mismatches. Runtime evidence is successful selection of VPE 6.1 callbacks, firmware load, ring start, and trap IRQ handling on VPE 6.1 hardware.
