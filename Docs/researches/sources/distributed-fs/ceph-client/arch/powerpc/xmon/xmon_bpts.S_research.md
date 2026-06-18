<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S

## Purpose
Reserves the executable breakpoint trampoline table used by xmon software breakpoints.

## Important APIs, Types, And Functions
Exports global symbol `bpt_table`. The table is aligned to 64 bytes and reserves `NBPTS * BPT_SIZE` bytes from `xmon_bpts.h`.

## Control Flow
There is no runtime branch flow here. xmon.c patches saved original instructions and trap instructions into each reserved slot, then redirects execution through these slots when needed.

## State And Persistence
The table is persistent kernel text/storage for the lifetime of the kernel. Its contents are modified by xmon breakpoint insertion and removal paths.

## Dependencies And Integration Points
Depends on `NBPTS`/`BPT_SIZE`, PowerPC instruction width including prefixed instructions, and `patch_instruction()` users in xmon.c.

## Risks And Edge Cases
Alignment is important because prefixed PowerPC instructions cannot cross 64-byte boundaries. Size mismatches with xmon.c's indexing would corrupt adjacent breakpoint slots.

## Test Signals
Signals are successful builds, breakpoints that single-step through table slots, and absence of prefixed-instruction boundary failures.

Source read size: 11 lines, 269 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S -->
