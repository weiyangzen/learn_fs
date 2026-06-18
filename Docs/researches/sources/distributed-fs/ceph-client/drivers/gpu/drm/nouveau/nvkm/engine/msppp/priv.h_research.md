
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/priv.h

Purpose: private MSPPP declarations.

Important APIs/types/functions: declares `nvkm_msppp_new_()` and `g98_msppp_init()`; includes public `engine/msppp.h`.

Control flow/state: header-only contract for variants.

Dependencies/integration: depends on Falcon function types. Risks are missing prototypes for reused init helpers. Test signals are compile/link coverage.
