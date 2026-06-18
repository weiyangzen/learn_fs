# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/legacy.h

## Purpose
Defines low-level legacy x87/FXSR instruction wrappers used for save/restore, signal frames, and MXCSR programming.

## Important APIs, Types, And Functions
`ldmxcsr()` loads MXCSR. `user_insn()` wraps user-memory FPU instructions with STAC/CLAC and exception tables. `kernel_insn()` and `kernel_insn_err()` wrap kernel-memory restore/save fault handling. Inline helpers include `fnsave_to_user_sigframe()`, `fxsave_to_user_sigframe()`, `fxrstor()`, `fxrstor_safe()`, `fxrstor_from_user_sigframe()`, `frstor()`, `frstor_safe()`, `frstor_from_user_sigframe()`, and `fxsave()`.

## Control Flow
Each helper selects 32-bit or 64-bit instruction variants where needed and returns either success or a trap/error code for safe restore paths. User helpers use exception table entries suitable for page fault and machine-check-safe handling.

## State, Persistence, And Dependencies
No persistent state is owned here. It depends on assembly exception table types, SMAP access toggling, FPU type definitions, and `mxcsr_feature_mask`.

## Integration Points
Used by FPU core and signal handling for non-XSAVE or FXSR-compatible paths and for direct user signal-frame save/restore.

## Risks
Exception table annotations must match the instruction fault semantics. User-memory instructions need correct access checks and fault handling to avoid corrupting FPU state or leaking kernel access.

## Test Signals
Signal frame save/restore, ptrace legacy paths, and fallback non-XSAVE CPUs should handle valid and faulting user buffers without kernel oopses.
