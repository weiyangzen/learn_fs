# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_init.c

## Purpose

`qlcnic_init.c` handles software ring-buffer allocation/release, ROM/flash reads, hardware pre-initialization from ROM CRB tables, firmware readiness checks, firmware image selection/validation/loading, and firmware heartbeat/reset decision helpers for the qlcnic driver.

## Important APIs, Types, And Functions

- `struct crb_addr_pair` stores ROM-provided CRB initialization address/data pairs.
- `crb_addr_xform[]`, `crb_addr_transform_setup()`, and `qlcnic_decode_crb_addr()` translate internal Phantom CRB addresses to PCI CRB offsets.
- `qlcnic_alloc_sw_resources()` allocates RDS rings, RX buffer arrays, initializes free lists, and binds SDS rings to IRQ/TX rings.
- `qlcnic_free_sw_resources()`, `qlcnic_release_rx_buffers()`, `qlcnic_reset_rx_buffers_list()`, and `qlcnic_release_tx_buffers()` tear down or reset software buffer ownership and DMA mappings.
- ROM helpers (`qlcnic_wait_rom_done()`, `do_rom_fast_read()`, `qlcnic_rom_fast_read()`, `qlcnic_rom_fast_read_words()`) implement serialized flash reads.
- `qlcnic_pinit_from_rom()` halts hardware blocks, reads ROM CRB init tables, filters unsafe registers, writes initialization values, and prepares PEG state.
- `qlcnic_check_fw_status()` waits for command and receive PEG readiness.
- `qlcnic_setup_idc_param()` reads partition type, physical port, and firmware/reset timeouts.
- `qlcnic_get_flt_entry()` and `qlcnic_check_flash_fw_ver()` inspect flash layout and firmware version.
- Unified firmware helpers parse product, bootloader, firmware, version, and BIOS metadata.
- `qlcnic_need_fw_reset()` decides whether firmware reload is needed.
- `qlcnic_load_firmware()` writes bootloader/firmware data into adapter memory.
- `qlcnic_request_firmware()` tries external unified firmware and falls back to flash.

## Control Flow

Software resource allocation creates normal and jumbo receive rings, sizes DMA/SKB buffers, initializes each RX buffer handle, initializes SDS free lists, and connects SDS rings to matching TX rings when multi-TX is active or to TX ring 0 otherwise.

ROM reads acquire the ROM lock, program ROMUSB address/opcode/count registers, wait for the done bit, read data, and release the lock. Multiword reads repeat this word-by-word into little-endian buffers.

`qlcnic_pinit_from_rom()` is the reset pre-init sequence. It disables/halt blocks, resets hardware while preserving selected blocks, verifies the CRB init table magic, reads address/data pairs, decodes CRB addresses, skips registers that should not be reset, writes remaining values with required delays, then clears PEG halt state.

Firmware selection starts as unknown, tries the kernel firmware file, validates unified image headers and selected product entries, checks firmware version and BIOS compatibility, and falls back to flash mode. Firmware load writes 64-bit chunks into device memory using `qlcnic_pci_mem_write_2M()` and releases PEG reset.

Readiness is established by waiting for command PEG and receive PEG states, then writing firmware initialize ACK.

## State And Persistence Behavior

The file owns RX buffer arrays, RX free lists, TX DMA cleanup, SDS metadata, `adapter->fw`, `adapter->file_prd_off`, `adapter->heartbeat`, init/reset timeouts, `adapter->need_fw_reset`, and firmware image type. Persistent hardware state includes ROM contents, flash layout tables, CRB init values, PEG shared registers, firmware image-valid magic, and the loaded firmware image in adapter memory.

## Dependencies And Integration Points

It depends on `qlcnic.h`, `qlcnic_hw.h`, ROMUSB definitions, firmware image layout structures, PCI DMA APIs, the Linux firmware loader, and 64-bit memory access helpers from `qlcnic_hw.c`. `qlcnic_main.c` uses it during probe, firmware start, reset recovery, attach/detach, and open/close.

## Risks

- ROM CRB init writes are powerful; incorrect decoding or skip rules can break hardware initialization.
- Firmware image parsing relies on firmware-provided offsets and must maintain strict bounds checks.
- Partial RX allocation can leave rings underfilled until later repost attempts.
- `qlcnic_need_fw_reset()` intentionally treats a loaded external firmware blob as requiring reset; callers must release firmware after load.
- Heartbeat timing can misclassify slow firmware as failed.

## Test Signals

Exercise flash and external firmware loading, fallback behavior, unsupported firmware versions, bad flash layout handling, PEG readiness, repeated open/close cleanup, firmware heartbeat stalls, ROM read timeout paths, and allocation-failure unwind for RX/TX resources.
