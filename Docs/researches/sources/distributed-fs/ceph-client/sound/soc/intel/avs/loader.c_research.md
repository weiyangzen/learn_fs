<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c

Purpose: AVS firmware, library, and module loading framework for CLDMA, HDA DMA, and IMR boot paths.

Important APIs, types, and functions: manifest structs and stripping/verification helpers; CLDMA loaders `avs_cldma_load_basefw/load_library/transfer_modules`; HDA/IMR helpers `avs_hda_init_rom()`, `avs_hda_load_basefw()`, `avs_hda_load_library()`, `avs_hda_transfer_modules()`; library loader `avs_dsp_load_libraries()`; boot entry points `avs_dsp_boot_firmware()` and `avs_dsp_first_boot_firmware()`; resource allocator `avs_dsp_alloc_resources()`.

Control flow: base firmware is requested from `intel/avs/<platform>/dsp_basefw.bin`, optional extended manifest is stripped, manifest magic/offset is validated, minimum version is enforced unless `ignore_fw_version=1`, then platform `load_basefw` is called and waits for FW_READY. CLDMA base loading powers/resets/unstalls main core, waits for ROM init, streams firmware through CLDMA, and waits for ROM status. HDA loading assigns a host playback stream, prepares DMA, enables SPIB, copies firmware, initializes ROM with boot config and purge, triggers DMA, and polls ROM-entered status. IMR boot first tries to start from retained memory when purge is false. Libraries are deduplicated by manifest name and loaded into firmware library slots. First boot initializes CLDMA when needed, disables main core, boots firmware with purge, and queries/allocates hardware, firmware, library, core, and pipeline resources.

State and persistence: firmware objects are cached through `avs_request_firmware()` and `adev->fw_list` so later suspend/resume is insulated from filesystem changes. `adev->lib_names` tracks loaded library slots; slot 0 is `BASEFW`. `adev->core_refs`, `ppl_ida`, and module info are allocated after first boot.

Dependencies and integration points: depends on firmware files declared in `core.c`, CLDMA helper, HDA stream DMA helpers, IPC boot/load-library/module messages, topology library names, power/clock/L1SEN gating controls, and platform attributes CLDMA/IMR/ALTHDA.

Risks: firmware manifest parsing mutates a local firmware copy by advancing data/size, so callers must pass copies when preserving original firmware cache. Library slot capacity check uses `id + num_libs >= max_libs_count`, which rejects filling the last nominal slot; verify intent before changing. Loading failures after caching libraries can require full driver reload. Power/clock gating must be restored on all error paths.

Test signals: minimum firmware version warnings/errors, successful FW_READY within 3 seconds, IMR resume path works when purge is false, HDA/CLDMA transfer status reaches expected ROM codes, library deduplication avoids duplicate loads, and module info initializes after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/loader.c -->
