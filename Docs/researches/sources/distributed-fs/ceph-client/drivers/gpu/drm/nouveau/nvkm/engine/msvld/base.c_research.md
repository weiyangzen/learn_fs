
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/base.c

Purpose: common constructor for MSVLD Falcon engines.

Important APIs/types/functions: `nvkm_msvld_new_()` delegates to `nvkm_falcon_new_()` with MMIO base `0x084000`.

Control flow/state: no local state; common Falcon engine owns memory, interrupt, and lifecycle state.

Dependencies/integration: depends on `priv.h` and Falcon support. Risks are wrong MMIO base or enabled flag. Test signals are Falcon readiness and class creation for all MSVLD variants.
