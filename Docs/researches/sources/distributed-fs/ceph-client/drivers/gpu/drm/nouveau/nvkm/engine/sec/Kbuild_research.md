
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/Kbuild

Purpose: build manifest for SEC Falcon engine support.

Important APIs/types/functions: builds `nvkm/engine/sec/g98.o`.

Control flow/state: no runtime behavior; it selects the G98 SEC implementation for compilation.

Dependencies/integration: parent Nouveau Kbuild and SEC constructor references. Risks are missing SEC object support if this line is altered. Test signals are successful build/link and SEC engine probe on G98-class hardware.
