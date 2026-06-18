<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c

## Purpose
Firmware image parser/loader and Dx context store/restore implementation for CATPT. It manages SRAM resource allocation, loads module blocks into IRAM/DRAM through DMA, records module metadata, preserves firmware and stream state over D3, and coordinates boot completion.

## APIs, Types, and Functions
Exports `catpt_sram_init()`, `catpt_sram_free()`, `catpt_request_region()`, `catpt_store_streams_context()`, `catpt_store_module_states()`, `catpt_store_memdumps()`, `catpt_boot_firmware()`, and `catpt_first_boot_firmware()`. Internal firmware structures are `catpt_fw_hdr`, `catpt_fw_mod_hdr`, and `catpt_fw_block_hdr`; helper paths include `catpt_restore_streams_context()`, `catpt_restore_memdumps()`, `catpt_restore_fwimage()`, `catpt_load_block()`, `catpt_restore_basefw()`, `catpt_restore_module()`, `catpt_load_module()`, `catpt_restore_firmware()`, `catpt_load_firmware()`, `catpt_load_image()`, and `catpt_load_images()`.

## Control Flow, State, and Persistence
SRAM is modeled as root resources with child allocations; firmware module blocks optionally reserve regions during initial load, and loaded module metadata stores entry point, persistent size, scratch size, and instance-state window. Initial boot stalls the DSP, requests firmware, verifies `$SST` signatures, copies the image to coherent DMA memory, loads each module/block, releases stall, waits up to 250 ms for firmware ready, updates SRAM power gating, restricts reserved DRAM areas, queries mixer stream info, arms stream templates, and allocates shared scratch. Restore boot reloads IRAM, overlays saved firmware-image memory ranges, restores memory dumps, restores module instance blocks from `dxbuf`, and then restores per-stream persistent contexts.

## Dependencies and Integration
Uses Linux firmware loading, DMA coherent allocation, resource trees, CATPT DMA helpers, firmware IPC ready notification, `catpt_ipc_get_mixer_stream_info()`, `catpt_arm_stream_templates()`, and register offset conversion helpers. Called from probe and resume after DSP power-up and before ALSA stream operation resumes.

## Risks and Test Signals
Risks include trusting firmware header block sizes and offsets, no global image-size boundary validation while walking modules, `catpt_request_region()` assuming existing child ordering and a non-empty child list for some paths, state restore depending on firmware-provided Dx memory info, and entry point adjustment by subtracting 4. Test signals are valid/invalid firmware signature handling, first boot loading all modules and arming templates, DRAM/IRAM resource maps after load, suspend/resume with offload/capture streams, memdump range filtering, and restore failure propagation before SSP reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c -->
