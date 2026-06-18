# sources/distributed-fs/ceph-client/arch/s390/lib/expoline.S

## Purpose
Generates external branch thunks for expoline/nospec mitigation on s390 when external thunks are configured.

## Important APIs, Types, And Functions
The assembly macro `GEN_ALL_BR_THUNK_EXTERN` iterates registers 1 through 15 and emits `GEN_BR_THUNK_EXTERN %rN` from `asm/nospec-insn.h`.

## Control Flow And State
No runtime state is stored here. The file contributes mitigation thunk symbols at build time so indirect branch sequences can target hardened external thunks.

## Dependencies And Integration
Depends on s390 nospec instruction macros and the build rule gated by `CONFIG_EXPOLINE_EXTERN`. It integrates with compiler/kernel branch mitigation code generation.

## Risks And Test Signals
Risks include missing thunk symbols for a register, mismatch with nospec macro definitions, and build/link failures under expoline configurations. Signals include successful builds with `CONFIG_EXPOLINE_EXTERN`, objdump inspection of thunk symbols, and boot under branch-mitigation settings.
