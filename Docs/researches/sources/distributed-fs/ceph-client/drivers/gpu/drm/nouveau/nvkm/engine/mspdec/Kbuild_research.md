
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/Kbuild

Purpose: build manifest for MSPDEC Falcon-based video decode engines.

Important APIs/types/functions: adds `base.o`, `g98.o`, `gt215.o`, `gf100.o`, and `gk104.o` to `nvkm-y`.

Control flow/state: no runtime behavior; determines which constructors and init tables are linked.

Dependencies/integration: parent Nouveau Kbuild and chipset constructor references. Risks are missing objects for supported chipsets. Test signals are successful build and probe coverage for G98/GT215/GF100/GK104 MSPDEC.
