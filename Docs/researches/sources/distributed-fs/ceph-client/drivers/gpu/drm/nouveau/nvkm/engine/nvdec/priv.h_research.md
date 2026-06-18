
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/priv.h

Purpose: private NVDEC definitions for firmware-interface based constructors.

Important APIs/types/functions: defines `struct nvkm_nvdec_func` with firmware/Falcon behavior, `struct nvkm_nvdec_fwif` with version/load/function pointers, and declares `nvkm_nvdec_new_()`.

Control flow/state: header-only state contract; base code uses these tables to select and load firmware.

Dependencies/integration: includes public `engine/nvdec.h`. Risks are fwif ABI drift. Test signals are compile/link coverage plus firmware selection for GM107/TU102/GA102.
