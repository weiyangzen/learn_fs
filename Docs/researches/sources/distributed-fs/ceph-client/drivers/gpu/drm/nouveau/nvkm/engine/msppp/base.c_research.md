
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/base.c

Purpose: common constructor for MSPPP Falcon engines.

Important APIs/types/functions: `nvkm_msppp_new_()` calls `nvkm_falcon_new_()` with MMIO base `0x086000`, enabled, and a chip-specific `nvkm_falcon_func`.

Control flow/state: no local persistence; Falcon framework owns state.

Dependencies/integration: depends on `priv.h` and common Falcon engine support. Risks are incorrect base address affecting all MSPPP variants. Test signals are engine probe at `0x086000` and class availability.
