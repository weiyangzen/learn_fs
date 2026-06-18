# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_loader.c

## Purpose
This file controls SST DSP reset/start and firmware loading. It parses Intel SST firmware containers, builds a list of memory-copy operations for IRAM/DRAM/DDR blocks, caches firmware in host memory, transfers parsed blocks to DSP memory, writes Merrifield DCCM configuration, starts the DSP, and waits for firmware initialization.

## Important APIs, types, and functions
MMIO copy helpers are `memcpy32_toio()` and `memcpy32_fromio()`. DSP control is `intel_sst_reset_dsp_mrfld()` and `sst_start_mrfld()`. Firmware validation/parsing is performed by `sst_validate_fw_image()`, `sst_parse_module_memcpy()`, and `sst_parse_fw_memcpy()`. Copy-list management is `sst_fill_memcpy_list()`, `sst_do_memcpy()`, and `sst_memcpy_free_resources()`. Firmware cache/load entry points are `sst_firmware_load_cb()`, `sst_request_fw()`, `sst_post_download_mrfld()`, and `sst_load_fw()`.

## Control flow
Firmware can be requested asynchronously during context init or synchronously on first runtime power-up if not already cached. The loader validates `$SST` signature and file size, iterates module headers and block headers, skips custom-info blocks, and records IO copies for IRAM, DRAM, or DDR destinations. `sst_load_fw()` requires the device in reset, creates a firmware-download block, raises CPU latency QoS, resets the DSP, copies all firmware blocks, writes DDR base/BSS reset data into DCCM, starts the DSP, waits for firmware init completion, restores QoS, frees the block, optionally restores DSP context, and marks firmware running.

## State and persistence behavior
Cached firmware bytes live in `ctx->fw_in_mem`; parsed copy operations live in `ctx->memcpy_list`; both persist until context cleanup. Firmware load mutates DSP IRAM/DRAM/DDR and `ctx->sst_state`. No filesystem writes occur.

## Dependencies and integration points
It depends on the Linux firmware loader, QoS APIs, MMIO helpers, IPC block waits from `sst_pvt.c`, firmware init wakeup from `sst_ipc.c`, and platform memory ranges in `intel_sst_drv`.

## Risks and edge cases
Firmware parsing validates top-level signature/size but otherwise trusts module sizes and block offsets. `sst_load_fw()` logs success even when `ret_val` is an error after the restore label. `sst_start_mrfld()` contains an unusual debug string. Copy sizes are divided by four, so non-32-bit-aligned firmware blocks would be truncated by copy helpers. Multiple cache parses can append duplicate copy-list entries if not guarded by state.

## Test signals
Test missing firmware, invalid signature/size, valid firmware parse, IRAM/DRAM/DDR block copies, custom-info skip, DSP reset/start register writes, firmware init timeout, QoS update/restore, DCCM DDR-base write, and repeated runtime power cycles using cached firmware.
