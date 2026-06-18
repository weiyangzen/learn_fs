
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/base.c

Purpose: common NVDEC constructor/destructor for firmware-interface based Falcon engines.

Important APIs/types/functions: `nvkm_nvdec_new_()` selects a supported `nvkm_nvdec_fwif`, calls its `load()` hook, and constructs an engine with `nvkm_engine_ctor()`. `nvkm_nvdec_dtor()` releases firmware with `nvkm_firmware_dtor()`.

Control flow/state: persistent state includes loaded firmware in `struct nvkm_nvdec`. The base engine function table has a destructor and empty software class list; chip files provide firmware/load behavior.

Dependencies/integration: depends on `core/firmware.h`, public NVDEC engine API, and chip-specific fwif arrays. Risks are firmware load failure, unsupported fwif selection, or cleanup leaks. Test signals are firmware request/load/unload and engine construction on supported chips.
