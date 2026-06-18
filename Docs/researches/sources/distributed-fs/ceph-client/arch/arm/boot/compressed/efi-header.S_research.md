<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S

## Purpose
This assembly include emits the ARM zImage EFI/PE-COFF header metadata used when `CONFIG_EFI_STUB` makes the compressed image bootable by EFI firmware.

## Important APIs, Types, and Functions
Assembly-visible symbols include `pe_header`, `coff_header`, `optional_header`, `extra_header_fields`, `section_table`, `__efi_start`. Included source files are `<linux/pe.h>`, `<linux/sizes.h>`. Embedded binary inputs are none.

## Control Flow
It contributes header fields and size calculations to `head.S`; firmware reads the PE/COFF layout before jumping to the decompressor entry.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are incorrect header sizes, section alignment, or entry metadata that make EFI firmware reject or misload the zImage.

## Test Signals
Build with `CONFIG_EFI_STUB`, inspect the PE header with EFI-aware tools, and boot through UEFI on ARM hardware or QEMU.

Source read size: 136 lines, 4236 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S -->
