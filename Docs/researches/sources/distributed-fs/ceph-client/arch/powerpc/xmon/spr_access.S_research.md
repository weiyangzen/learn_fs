<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S

## Purpose
Provides xmon's generic runtime accessors for all 1024 PowerPC special purpose registers.

## Important APIs, Types, And Functions
`xmon_mfspr(sprn, default_value)` and `xmon_mtspr(sprn, new_value)` are exported assembly entry points. The shared `xmon_mxspr` masks the SPR number to 10 bits, scales it by eight bytes, and branches through generated mfspr/mtspr tables.

## Control Flow
Callers pass the SPR number in r3 and a default or new value in r4. The wrapper selects either `.Lmfspr_table` or `.Lmtspr_table`, computes the branch target, and executes the generated two-instruction slot for that SPR.

## State And Persistence
No persistent state is held. Fault behavior is handled by xmon.c with `catch_spr_faults` and longjmp recovery around these calls.

## Dependencies And Integration Points
Used by `read_spr()` and `write_spr()` in xmon.c. Depends on PowerPC assembler macros, the 1024-entry SPR namespace, and exception handling that can recover from illegal SPR access.

## Risks And Edge Cases
Invalid or privileged SPR accesses may fault. The table assumes each generated slot is the expected size; changing instruction sequence length would break indexing. Writes are especially hazardous and are gated by xmon read-only mode in C.

## Test Signals
Signals are `S`, `Sr`, `Sw`, and `Sa` xmon commands reading implemented SPRs, reporting faults for inaccessible SPRs, and preserving monitor control after a fault.

Source read size: 47 lines, 814 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S -->
