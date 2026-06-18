
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/Kbuild

Purpose: build manifest for NVENC engines.

Important APIs/types/functions: builds `base.o`, `gm107.o`, and `tu102.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Kbuild. Risks are missing constructor objects for supported encoder hardware. Test signals are build/link and probe coverage for GM107/TU102 NVENC.
