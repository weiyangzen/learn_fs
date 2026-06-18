
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/priv.h

Purpose: private MSPDEC declarations.

Important APIs/types/functions: declares `nvkm_mspdec_new_`, `g98_mspdec_init`, and `gf100_mspdec_init`; includes public `engine/mspdec.h`.

Control flow/state: header-only integration contract for MSPDEC variants.

Dependencies/integration: depends on Falcon function types from public engine headers. Risks are missing prototypes for variant reuse. Test signals are compile/link coverage for all MSPDEC files.
