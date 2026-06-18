
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/priv.h

Purpose: private NVENC definitions for firmware-interface based engines.

Important APIs/types/functions: defines `struct nvkm_nvenc_func`, `struct nvkm_nvenc_fwif`, and declares `nvkm_nvenc_new_()`.

Control flow/state: header-only contract consumed by base and chip files.

Dependencies/integration: includes public `engine/nvenc.h`. Risks are firmware-interface signature drift. Test signals are compile/link coverage for GM107/TU102 NVENC.
