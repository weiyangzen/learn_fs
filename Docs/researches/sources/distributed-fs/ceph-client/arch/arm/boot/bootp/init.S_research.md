<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S

## Purpose
This BOOTP wrapper entry moves an embedded initrd to its linked physical destination, appends an `ATAG_INITRD2` record to the boot tag list, and then jumps to the embedded zImage.

## Important APIs, Types, and Functions
Assembly-visible symbols include `_start`, `taglist`, `move`, `data`. Included source files are none. Embedded binary inputs are none.

## Control Flow
`_start` computes its load address, copies the initrd in 32-byte chunks, creates a minimal `ATAG_CORE` if the parameter list is invalid, walks to the ATAG terminator, writes the initrd tag, and branches to `kernel_start`.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are invalid `params_phys`, overlapping initrd copy ranges, missing ATAG terminators, and bootloaders that pass only FDT data when this wrapper expects ATAG mutation.

## Test Signals
Build `bootpImage` with a known initrd and boot it on a legacy ATAG-capable ARM target; inspect the kernel log for initrd discovery and verify no memory overlap with zImage.

Source read size: 85 lines, 2477 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S -->
