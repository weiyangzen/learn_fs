<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h

## Purpose
Defines the Xtensa boot parameter tag format passed from boot loaders to the kernel.

## Important APIs, Types, And Functions
Key items are bootparam tag constants such as `BP_TAG_FIRST`, `BP_TAG_LAST`, `BP_TAG_COMMAND_LINE`, `BP_TAG_INITRD`, `BP_TAG_MEMORY`, `BP_TAG_SERIAL_BAUDRATE`, `BP_TAG_SERIAL_PORT`, `BP_TAG_FDT`, `BP_VERSION`, and structures for typed tag payloads.

## Control Flow
The header has no executable flow. Boot loaders and early kernel parsers use the tag IDs and struct layouts to walk a parameter list.

## State And Persistence
State is the boot-time parameter block in memory. It does not persist after early boot except through parsed kernel globals.

## Dependencies And Integration Points
Used by `boot-elf/bootstrap.S`, platform boot code, command-line/initrd/memory/FDT parsing, and user-provided boot loaders.

## Risks And Edge Cases
Tag size/alignment mismatches break parser traversal. Boot loaders must terminate with `BP_TAG_LAST`. Version drift can cause ignored or misread parameters.

## Test Signals
Boot with command line, initrd, memory, serial, and FDT tags; test malformed/short tag lists and no-bootparam configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h -->
