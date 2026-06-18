# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.h

## Purpose
`cz_ih.h` is the public header for the Carrizo interrupt handler IP block. It lets VI-family device setup code reference the `cz_ih_ip_block` object implemented in `cz_ih.c`.

## Important APIs, Types, and Data
The header has one declaration: `extern const struct amdgpu_ip_block_version cz_ih_ip_block;`. It uses an include guard `__CZ_IH_H__`. The concrete type is defined elsewhere in AMDGPU core headers included by translation units that include this header.

## Control Flow and Integration
There is no control flow. The integration point is compile-time linkage: `vi.c` includes this header and passes `&cz_ih_ip_block` to `amdgpu_device_ip_block_add()` for relevant Carrizo/Stoney VI devices. The object then supplies lifecycle callbacks from `cz_ih.c`.

## State and Persistence Behavior
The header stores no state and has no persistence behavior. It only exposes a read-only global object defined in the C file.

## Dependencies
Users must include this header in a context where `struct amdgpu_ip_block_version` is declared. It depends on `cz_ih.c` being linked into the driver; otherwise the extern declaration would be unresolved.

## Risks
The main risk is integration mismatch: adding the IP block for unsupported ASICs would bind the wrong IH register programming and IV decode format. Removing or renaming the extern without updating `vi.c` breaks build/link. The header intentionally does not expose private helper functions, keeping the surface small.

## Test Signals
Build coverage should confirm the extern resolves and `vi.c` can add the block. Runtime signals belong mostly to `cz_ih.c`: successful IP block registration, interrupt initialization, and working IRQ delivery on Carrizo/Stoney hardware.
