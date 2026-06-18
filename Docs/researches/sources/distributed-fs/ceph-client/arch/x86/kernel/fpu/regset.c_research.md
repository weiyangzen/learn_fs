# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/regset.c

## Purpose
Implements FPU user-regset get/set operations for ptrace, core dumps, 32-bit compatibility, XSAVE state, FXSR state, and CET shadow-stack pointer exposure.

## Important APIs, Types, And Functions
Active predicates include `regset_fpregs_active()`, `regset_xregset_fpregs_active()`, and `ssp_active()`. Get/set APIs include `xfpregs_get/set()`, `xstateregs_get/set()`, `fpregs_get/set()`, and `ssp_get/set()`. Conversion helpers `convert_from_fxsr()` and `convert_to_fxsr()` translate between i387 and FXSR layouts.

## Control Flow
Get paths synchronize current fpstate if needed, then copy FXSR, XSAVE, shadow-stack, or legacy i387 data into a `membuf`. Set paths reject partial/oversized writes, copy input from kernel or user buffers, validate MXCSR and xstate constraints, invalidate cached register ownership, and update fpstate memory so the target reloads it on resume. Compatibility paths convert tag words and register environments between formats.

## State, Persistence, And Dependencies
State modifications are target task fpstate memory, xsave header feature bits, target PKRU, CET user SSP, and invalidated FPU ownership. It depends on user-regset core, ptrace stop semantics, xstate copy helpers, IA32 emulation, shadow stack features, and MXCSR masks.

## Integration Points
Used by ptrace, ELF core dump generation, 32-bit compat regsets, and debugger manipulation of FPU/CET state.

## Risks
Allowing stale cached registers after ptrace modification would discard debugger writes, so invalidation is critical. Bad MXCSR, invalid SSP, or unsupported xfeatures must be rejected. 32-bit callers must not expose xmm8-15.

## Test Signals
Ptrace get/set and coredumps should round-trip FP/FX/XSAVE state, reject invalid sizes/MXCSR/SSP, clear high XMM registers for ia32 callers, and force reload after writes.
