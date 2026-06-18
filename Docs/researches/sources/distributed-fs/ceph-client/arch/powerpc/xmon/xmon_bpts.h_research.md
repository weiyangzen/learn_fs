<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h

## Purpose
Defines the xmon breakpoint-table sizing contract shared by C and assembly.

## Important APIs, Types, And Functions
`NBPTS` is 256. For C, `BPT_SIZE` is two `ppc_inst_t` values, `BPT_WORDS` derives the word count, and `bpt_table` is declared as the backing storage.

## Control Flow
No executable flow. xmon.c uses the constants to index `bpts[]` and `bpt_table`; xmon_bpts.S uses them to reserve storage.

## State And Persistence
The constants fix the amount of persistent breakpoint storage available in the kernel image.

## Dependencies And Integration Points
Depends on `asm/inst.h` for `ppc_inst_t` and on assembly inclusion for `NBPTS` only.

## Risks And Edge Cases
Changing `NBPTS` or instruction slot sizing without updating C/assembly assumptions can break breakpoint restoration or table bounds.

## Test Signals
Signals are compile-time agreement between C and assembly and runtime ability to create up to 256 software breakpoints.

Source read size: 14 lines, 338 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h -->
