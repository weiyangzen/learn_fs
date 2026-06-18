
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/Kbuild

Purpose: build manifest for MSVLD Falcon-based video decode engines.

Important APIs/types/functions: builds `base.o`, `g98.o`, `gt215.o`, `mcp89.o`, `gf100.o`, and `gk104.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are omitted constructor objects for supported chipsets. Test signals are build/link and probe coverage for listed MSVLD variants.
