# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/priv.h

## Purpose
Defines private ACR function tables, firmware-interface records, HS firmware records, and LSF runtime records.

## Important APIs, types, and functions
`struct nvkm_acr_func` defines firmware load arrays, WPR parse/layout/alloc/build/patch/check hooks, init/fini hooks, and HS bootstrap masks. `struct nvkm_acr_hsfw` and `struct nvkm_acr_hsf_fwif` describe high-secure firmware. `struct nvkm_acr_lsf` records bootstrappable low-secure falcons. The header declares generation helpers and `nvkm_acr_new_()`.

## Control flow, state, and persistence
No code runs here. The contracts determine how `base.c` builds WPR images, boots load/unload firmware, and validates bootstrap capabilities.

## Dependencies and integration points
Includes public `subdev/acr.h` and references falcon firmware functions, SEC2/GSP/PMU owners, and nvfw ACR structures.

## Risks and test signals
Incorrect function pointers cause generation-specific ACR failure. Build coverage catches signature drift; runtime WPR load/bootstrap validates table wiring.
