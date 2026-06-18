# sources/distributed-fs/ceph-client/arch/mips/kernel/signal-common.h

## Purpose
Declares common MIPS signal-frame helpers and FPU/MSA context assembly hooks shared by signal implementation files.

## Important APIs, Types, and Functions
- `DEBUGP` macro optionally logs signal debugging.
- `get_sigframe()` selects/allocates a user signal frame.
- `fpcsr_pending()` checks and clears pending FP exceptions in saved FCSR.
- `lock_fpu_owner()` and `unlock_fpu_owner()` disable preemption and page faults while preserving FPU ownership.
- `_save_fp_context()`, `_restore_fp_context()`, `_save_msa_all_upper()`, and `_restore_msa_all_upper()` are assembly helpers.
- `setup_sigcontext()` and `restore_sigcontext()` convert between pt_regs/task state and user `sigcontext`.

## Control Flow
Signal delivery code includes this header to choose frame placement, protect FPU ownership while copying FP state, call assembly save/restore helpers, and build/restore sigcontext. The header itself contains declarations and small locking macros only.

## State and Persistence
No state. It defines access to transient user signal frames and CPU/task FP state.

## Dependencies and Integration Points
Integrates with `r2300_fpu.S` or `r4k_fpu.S`, MIPS signal C files, FPU ownership/page fault rules, and user `sigcontext` ABI.

## Risks
Lock macros disable both preemption and page faults; callers must always pair them. Assembly helper prototypes must match exact calling convention and user pointer semantics. Signal ABI changes must remain compatible with existing user-space frames.

## Test Signals
Signal delivery and `sigreturn` tests with FP/MSA-using programs should preserve context, detect pending FCSR exceptions, and handle invalid user signal frames without losing FPU ownership.
