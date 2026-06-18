# sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/dmesg.c

## Purpose

implements an Amiga diagnostic dmesg extractor that scans chip memory for saved kernel message
records

## Important APIs, Types, and Functions

Source read size: 69 lines, 1656 bytes. Includes: `stdio.h`, `stdlib.h`, `unistd.h`. Defined
functions: `main`. Declared functions: `return`. Key macros/defines: `CHIPMEM_START`, `CHIPMEM_END`,
`SAVEKMSG_MAGIC1`, `SAVEKMSG_MAGIC2`. Types visible in this file: `savekmsg`.

## Control Flow and Behavior

main() parses an optional memory limit, scans for SAVE/KMSG magic, validates lengths, and prints the
saved kernel log payload

## State and Persistence

persistent state is only process-local scan buffers and stdout output; it does not modify the memory
image

## Dependencies and Integration Points

depends on Amiga saved-kmsg layout constants, stdio/unistd, and host access to a memory dump or
mapped chip memory

## Risks and Test Signals

bad bounds checks can read outside the supplied image; tests should cover missing magic, truncated
records, and valid saved logs
