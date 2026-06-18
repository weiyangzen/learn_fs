# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.c

## Purpose
Implements the MIPS firmware-processor backend: firmware heap initialization, MIPS VM setup/teardown, ELF firmware processing, boot-data patching, wrapper/remap register programming, firmware address conversion, and MIPS IRQ handling.

## Important APIs, types, and functions
- `pvr_mips_init()` initializes a 16 MiB firmware heap with a 1 MiB reserved area and calls `pvr_vm_mips_init()`.
- `pvr_mips_fini()` tears down MIPS VM state.
- `pvr_mips_fw_process()` parses ELF firmware and patches MIPS boot data with DMA addresses, register base, stack address, and page-table pages.
- `pvr_mips_wrapper_init()` configures wrapper mode and boot/data/exception address remaps.
- `pvr_mips_get_fw_addr_with_offset()`, `pvr_mips_irq_pending()`, and `pvr_mips_irq_clear()` complete `pvr_fw_defs_mips`.

## Control flow
Firmware processing first delegates PT_LOAD copying to `pvr_fw_process_elf_command_stream()`, then requires layout entries for boot code, boot data, exception code, and stack. It resolves DMA addresses in code/data GEM objects, writes stack/register/page-table metadata into the bootloader configuration area inside boot data, and handles host page sizes larger than the firmware's expected 4 KiB pages.

Wrapper init requires physical bus width greater than 32 bits, configures microMIPS wrapper mode, maps boot code, boot data, and exception code remap windows to DMA addresses, applies BRN63553 remap5 workaround on 36-bit cores, sets Garten wrapper idle control, and enables EJTAG probe.

## State and persistence
MIPS-specific persistent state is stored in `struct pvr_fw_mips_data`, including page-table pages, CPU mapping, DMA addresses for page tables and boot sections, cache policy, and PFN mask. The firmware heap reserves 1 MiB. MIPS addresses are formed from the firmware heap offset masked by the heap size and ORed with `0xC0000000`.

## Dependencies and integration points
Depends on MIPS firmware ABI definitions, `pvr_vm_mips_*` map/unmap/init/fini functions, common ELF processing, GEM DMA address lookup, PVR feature `phys_bus_width`, and quirk BRN63553. It is selected by `pvr_fw_init()` through the common processor vtable.

## Risks
MIPS support is constrained to wider-than-32-bit physical bus configurations. Missing required layout sections fails boot processing. Remap registers directly use DMA addresses and alignment masks; wrong section offsets or DMA lookup errors become boot failures or WARNs. Host page-size conversion for the firmware page table is a portability-sensitive path.

## Test signals
Validate MIPS firmware boot on supported bus widths, failure on missing layout sections, BRN63553 behavior on 36-bit cores, IRQ pending/clear registers, page-table DMA address population with non-4K host pages, and correct teardown through `pvr_vm_mips_fini()`.
