
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/priv.h

Purpose: private PMPEG declarations shared across MPEG engine implementations.

Important APIs/types/functions: declares `nv31_mpeg_init`, `nv31_mpeg_tile`, `nv31_mpeg_object`, `nv40_mpeg_mthd_dma`, `nv50_mpeg_init`, `nv50_mpeg_intr`, and `nv50_mpeg_cclass`.

Control flow/state: header only; it wires common routines to variant descriptors.

Dependencies/integration: includes public `engine/mpeg.h` and forward-declares `struct nvkm_chan`. Risks are prototype drift. Test signals are build coverage for all MPEG objects listed in Kbuild.
