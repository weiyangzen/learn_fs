<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h

## Purpose
Declares private FSP subdevice types and generation hooks.

## Important APIs, Types, And Functions
Defines `nvkm_fsp(p)` and `struct nvkm_fsp_func`, including `wait_secure_boot` and nested `cot` metadata and `boot_gsp_fmc` hook. Declares `nvkm_fsp_new_`, `gh100_fsp_wait_secure_boot`, and `gh100_fsp_boot_gsp_fmc`.

## Control Flow
No runtime flow. It provides the function-table contract consumed by FSP base and generation files.

## State And Persistence
The function table persists in each `struct nvkm_fsp`; certificate sizes and COT version are immutable generation metadata.

## Dependencies And Integration Points
Includes public `subdev/fsp.h` and bridges base code, GH100 implementation, and Blackwell wrappers.

## Risks And Edge Cases
Function pointer contracts are not enforced at compile time beyond type checks; missing hooks can crash through null calls in base code.

## Test Signals
Successful compilation and correct constructor wiring for each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h -->
