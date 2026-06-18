
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/Kbuild

Purpose: build manifest for MSPPP Falcon-based video post-processing engines.

Important APIs/types/functions: builds `base.o`, `g98.o`, `gt215.o`, and `gf100.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are missing linked constructors for chipsets. Test signals are successful build and probe of G98/GT215/GF100 MSPPP support.
