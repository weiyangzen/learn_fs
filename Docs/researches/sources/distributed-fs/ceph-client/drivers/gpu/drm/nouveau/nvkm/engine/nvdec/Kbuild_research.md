
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/Kbuild

Purpose: build manifest for modern NVDEC engines.

Important APIs/types/functions: builds `base.o`, `gm107.o`, `tu102.o`, and `ga102.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are missing object files for constructor references. Test signals are build/link and probe coverage for GM107/TU102/GA102 NVDEC.
