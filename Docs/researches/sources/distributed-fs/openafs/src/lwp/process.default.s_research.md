# sources/distributed-fs/openafs/src/lwp/process.default.s

Purpose: legacy multi-architecture assembly context-switch implementation for LWP. It contains conditional implementations for ARM, RIOS/AIX, m68k, SPARC, IBM032, VAX, MIPS, HPUX, Alpha, and PowerPC.

Important APIs/types/functions: each architecture exports variants of `savecontext` and `returnto`, with platform-specific symbol names and register save areas. The common contract is storing a top-of-stack pointer in the save area, optionally switching to `newsp`, calling the supplied function, and later restoring saved registers/stack. Several blocks also set or clear global `PRE_Block`.

Control flow: all architecture blocks follow the same scheduler handoff: save callee/global registers and special registers as needed, store current stack pointer, switch stack if requested, branch to the target function, and restore on `returnto`. SPARC additionally flushes register windows; MIPS/Alpha save floating-point registers; HPUX delegates to `process.s.hpux`.

State and persistence: CPU register state and `PRE_Block` are the only persistent runtime effects. No heap or file persistence.

Dependencies/integration: selected by build macros from `afs/param.h`. It integrates with `lwp.h`'s `struct lwp_context` layout; for SPARC it relies on the larger `globals` area in the context structure.

Risks and test signals: high maintenance risk because many target ABIs are obsolete and hard to test. Register save completeness, stack-frame sizing, and symbol naming are the critical failure modes. The most useful signal is successful per-architecture build plus LWP runtime tests on that architecture.
