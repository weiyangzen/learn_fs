<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S

## Purpose
This Acorn-specific decompressor helper writes characters to the early low-level display path and carries the character conversion table used by that path.

## Important APIs, Types, and Functions
Assembly-visible symbols include `ll_write_char`, `con_charconvtable`, `LC0`, `Lrow4bpplp`, `Lrow8bpplp`, `Lrow1bpp`. Included source files are `<linux/linkage.h>`, `<asm/assembler.h>`. Embedded binary inputs are none.

## Control Flow
`ll_write_char` converts or emits character data using the table symbols before normal console drivers are available.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are display memory assumptions, conversion table mismatches, and debug output faults before the kernel console is initialized.

## Test Signals
Build an Acorn/RPC-style compressed boot with debug output and confirm early characters appear correctly.

Source read size: 131 lines, 2722 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S -->
