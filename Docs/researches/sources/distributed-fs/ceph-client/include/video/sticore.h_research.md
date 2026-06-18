<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sticore.h -->
# sources/distributed-fs/ceph-client/include/video/sticore.h

## Purpose
This header defines the HP PA-RISC STI graphics firmware interface used by console/framebuffer code. It models STI ROM data, global configuration, firmware call argument blocks, font/block-move operations, and the in-kernel `sti_struct` wrapper.

## Important APIs, Types, And Functions
- Constants define ROM counts, region count, monitor limits, font types, alternate code types, and `STI_WAIT`.
- `region_t` maps STI region descriptors; `REGION_OFFSET_TO_PHYS()` converts region offsets against HPA.
- `struct sti_glob_cfg*`, `sti_init_*`, `sti_conf_*`, `sti_font_*`, and `sti_blkmv_*` mirror firmware ABI argument and result blocks.
- `struct sti_rom` and `struct sti_rom_font` model firmware ROM tables and font descriptors.
- `struct sti_cooked_font`, `sti_cooked_rom`, `sti_all_data`, and `sti_struct` hold converted fonts, firmware entry addresses, region mappings, locks, PCI/device handles, low-memory call data, and selected font.
- Public functions include `sti_get_rom()`, `sti_font_convert_bytemode()`, `sti_call()`, `sti_putc()`, `sti_set()`, `sti_clear()`, and `sti_bmove()`.

## Control Flow
Generic STI code discovers ROMs, parses regions/fonts, allocates `sti_all_data` in suitable memory, initializes firmware through `init_graph`, queries display config through `inq_conf`, and serializes firmware calls with `sti_struct.lock`. Console operations call `sti_putc`, `sti_clear`, and `sti_bmove`, which prepare ABI blocks and invoke `sti_call`.

## State And Persistence
`sti_struct` persists ROM metadata, selected font, regions, global config, firmware entry points, call mode, device path, and shared call buffers. Firmware and device state persist in hardware and STI global memory. `save_addr` and `sti_mem_addr` reserve firmware reentry/global storage.

## Dependencies And Integration Points
It depends on PA-RISC IO translation (`virt_to_phys`, `<asm/io.h>`), spinlocks, PCI/device infrastructure, console/fb code, and low-memory allocation constraints on 64-bit kernels.

## Risks And Edge Cases
The comments warn that STI calls returning busy can require spin-locked wait loops with high interrupt latency. ABI structures must match firmware layout exactly. 32-bit STI code on 64-bit kernels requires low memory. Bad region mapping or font conversion can crash firmware calls.

## Test Signals
Signals include successful ROM discovery, valid `inq_conf` dimensions, visible console text through `sti_putc`, clear/block-move behavior, correct font dimensions/CRC selection, no firmware call busy hangs, and working 32-bit and 64-bit STI call paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sticore.h -->
