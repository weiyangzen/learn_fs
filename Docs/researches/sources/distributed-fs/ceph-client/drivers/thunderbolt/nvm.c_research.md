<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c` provides generic and vendor-specific Thunderbolt/USB4 NVM helper logic. It allocates `struct tb_nvm`, determines vendor support, reads active NVM versions, validates new images, registers active/non-active nvmem devices, caches writes before authentication, and provides block-oriented read/write helpers for switches and retimers. The source was read as a complete 644-line file.

## Important APIs, Types, and Functions

Vendor dispatch uses `struct tb_nvm_vendor_ops` and `struct tb_nvm_vendor`. Public helpers include `tb_nvm_alloc()`, `tb_nvm_read_version()`, `tb_nvm_validate()`, `tb_nvm_write_headers()`, `tb_nvm_add_active()`, `tb_nvm_write_buf()`, `tb_nvm_add_non_active()`, `tb_nvm_free()`, `tb_nvm_read_data()`, `tb_nvm_write_data()`, and `tb_nvm_exit()`. Intel switch and retimer paths parse `INTEL_NVM_FLASH_SIZE`, `INTEL_NVM_VERSION`, FARB/header offsets, digital section size, and device IDs. ASMedia switch versioning reads date/version offsets and assumes a 512 KiB active image.

## Control Flow

`tb_nvm_alloc()` first determines whether the device is a switch or retimer, matches its vendor against supported tables, allocates a unique ID from `nvm_ida`, and stores the selected ops. Version reading delegates to vendor ops. Validation first checks that a buffer exists and the image is between 32 KiB and 1 MiB, then lets vendor validation adjust `buf_data_start` and `buf_data_size` to skip headers when required. Intel validation checks header pointer bounds, 4 KiB alignment, digital-section size, and device ID unless a switch is in safe mode. Header writing is special for pre-generation-3 Intel switches, where CSS headers are written before the data section.

Nvmem registration exposes `nvm_active` as read-only and `nvm_non_active` as root-only writable. Writes to `nvm_non_active` are buffered by `tb_nvm_write_buf()` and later authenticated by switch or retimer code. Generic `tb_nvm_read_data()` and `tb_nvm_write_data()` split byte-oriented requests into 16-dword blocks, handle unaligned offsets, and retry selected failures.

## State and Persistence Behavior

Persistent hardware state is the device flash, but this file only stages data in memory and registers nvmem devices. `nvm->buf`, `buf_data_size`, `buf_data_start`, `major`, `minor`, `active_size`, `flushed`, and `id` represent current kernel-side state. The global `nvm_ida` persists for the module lifetime and is destroyed by `tb_nvm_exit()`.

## Dependencies and Integration Points

The file depends on `tb.h`, Linux IDA, nvmem provider callbacks, `vmalloc`, and vendor-specific switch/retimer read/write functions supplied by `switch.c`, `retimer.c`, DMA-port code, and USB4 helpers. It is not a standalone updater: actual flash writes/authentication are driven by sysfs flows in switch and retimer code.

## Risks and Edge Cases

Image validation does raw unaligned casts from the uploaded buffer and trusts vendor layout assumptions. `tb_nvm_write_buf()` does not enforce `offset + bytes <= NVM_MAX_SIZE` locally, relying on nvmem bounds. In `tb_nvm_write_data()`, partial unaligned writes need careful scrutiny because `nbytes` includes the offset and the copied region starts at `data + offset`; callers should avoid sizes that produce non-dword write counts. Vendor tables intentionally disable upgrades for unknown vendors. Safe-mode switches skip device-ID matching because active NVM may be inaccessible.

## Test Signals

Nvmem read/write smoke tests, validation tests for too-small/too-large images, bad FARB offsets, misalignment, wrong device ID, Intel generation-2 CSS header writes, ASMedia version parsing, retimer validation, retry behavior for `-ENODEV`/`-ETIMEDOUT`, and memory-leak checks around add/remove are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c -->
