
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/Kbuild

Purpose: build manifest for legacy PMPEG engine support.

Important APIs/types/functions: adds `nv31.o`, `nv40.o`, `nv44.o`, `nv50.o`, and `g84.o` to `nvkm-y`.

Control flow/state: no runtime behavior; it controls which implementations are compiled into the NVKM driver.

Dependencies/integration: Kbuild integrates with the parent Nouveau build. Risks are omitted objects producing unresolved chipset constructor references or missing engine support. Test signals are kernel build/link and probe paths for NV31/NV40/NV44/NV50/G84 PMPEG chips.
