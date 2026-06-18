
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/base.c

Purpose: common NVENC constructor/destructor for firmware-interface based encoder engines.

Important APIs/types/functions: `nvkm_nvenc_new_()` selects an `nvkm_nvenc_fwif`, calls its load hook, and constructs the engine. `nvkm_nvenc_dtor()` releases firmware through `nvkm_firmware_dtor()`.

Control flow/state: persistent state is loaded firmware in `struct nvkm_nvenc`; class exposure is empty in the base table unless chip-specific layers add it elsewhere.

Dependencies/integration: depends on `core/firmware.h` and chip-specific fwif arrays. Risks are firmware load/cleanup failures and unsupported fwif selection. Test signals are firmware request success, engine construction, destructor cleanup, and encoder Falcon boot.
