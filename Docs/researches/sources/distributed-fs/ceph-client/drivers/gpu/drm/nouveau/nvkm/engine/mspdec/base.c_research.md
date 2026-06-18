
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/base.c

Purpose: common constructor for MSPDEC Falcon engines.

Important APIs/types/functions: `nvkm_mspdec_new_()` delegates to `nvkm_falcon_new_()` with `enable=true`, base address `0x085000`, and the chip-specific `nvkm_falcon_func`.

Control flow/state: no local state; all engine state is allocated by the Falcon framework at the supplied MMIO base.

Dependencies/integration: depends on `priv.h` and common Falcon engine support. Risks are wrong MMIO base or enable flag causing all MSPDEC variants to fail. Test signals are Falcon probe/init at `0x085000`, interrupt routing, and class creation for each variant.
