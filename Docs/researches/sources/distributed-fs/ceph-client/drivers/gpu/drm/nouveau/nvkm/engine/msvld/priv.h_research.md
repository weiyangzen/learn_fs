
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/priv.h

Purpose: private MSVLD declarations.

Important APIs/types/functions: declares `nvkm_msvld_new_()`, `g98_msvld_init()`, and `gf100_msvld_init()`; includes public `engine/msvld.h`.

Control flow/state: header-only contract.

Dependencies/integration: depends on Falcon function types and public engine API. Risks are prototype drift. Test signals are compile/link coverage for MSVLD variants.
