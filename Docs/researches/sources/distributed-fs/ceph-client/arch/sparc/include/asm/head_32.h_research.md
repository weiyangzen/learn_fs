<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h

## Purpose
This header defines SPARC32 boot-header constants shared with early boot code and image tools.

## Important APIs, Types, and Functions
It describes magic/signature fields, boot loader visible offsets, and early kernel image metadata used by boot assembly and tools such as `piggyback`.

## Control Flow
Boot assembly emits these fields; bootloaders and host tools read or patch them before transferring control to the kernel.

## State and Persistence Behavior
The header shapes persistent bytes in the kernel image, not runtime state.

## Dependencies and Integration Points
It integrates with `arch/sparc/boot` image creation, PROM/U-Boot boot paths, and early init assembly.

## Risks
Changing offsets or signatures can break bootloader/tool compatibility.

## Test Signals
Build SPARC32 boot images, inspect headers, run `piggyback`/U-Boot image creation, and boot under target firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h -->
