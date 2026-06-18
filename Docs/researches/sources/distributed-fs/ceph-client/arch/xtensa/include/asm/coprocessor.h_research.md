<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h

## Purpose
Defines Xtensa optional register and coprocessor save-area types plus assembly macros for saving/restoring configured TIE/coprocessor state.

## Important APIs, Types, And Functions
Important macros include `XTENSA_HAVE_COPROCESSOR`, `XTENSA_HAVE_COPROCESSORS`, `XTENSA_HAVE_IO_PORT`, `save_xtregs_opt`, `load_xtregs_opt`, `save_xtregs_user`, and `load_xtregs_user`. Types include `xtregs_opt_t`, `xtregs_user_t`, `xtregs_cp0_t` through `xtregs_cp7_t`. Functions include `coprocessor_flush`, `coprocessor_release_all`, `coprocessor_flush_all`, `coprocessor_flush_release_all`, and `local_coprocessors_flush_release_all`.

## Control Flow
The header expands variant-provided `XCHAL_*_SA_LIST` macros into aligned C structs and assembly save/load sequences. Coprocessor management code uses the declared functions to lazily save, flush, or release per-thread coprocessor state.

## State And Persistence
State is per-thread optional/coprocessor register save areas. Hardware CPENABLE and coprocessor registers are managed elsewhere.

## Dependencies And Integration Points
Depends on variant `tie.h` and `tie-asm.h`, Xtensa core definitions, thread-info code, ptrace/ELF core dumps, and context-switch code.

## Risks And Edge Cases
Variant save-area metadata must be exact; wrong sizes/alignments corrupt task state or core dumps. Assembly and C struct generation must stay consistent.

## Test Signals
Run context-switch, signal, ptrace, and core-dump tests on variants with optional registers and coprocessors; verify lazy coprocessor flush/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h -->
