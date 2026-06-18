# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/core.c

## Purpose
Implements central x86 FPU state management: register save/restore, lazy ownership tracking, kernel FPU sections, task clone/reset/drop, exception decoding, KVM guest fpstate swapping, dynamic XFD handling, and idle cleanup.

## Important APIs, Types, And Functions
Global configs are `fpu_kernel_cfg`, `fpu_user_cfg`, `guest_default_cfg`, and `init_fpstate`. Per-CPU state includes `kernel_fpu_allowed`, `fpu_fpregs_owner_ctx`, and x86_64 `xfd_state`. Key APIs include `save_fpregs_to_fpstate()`, `restore_fpregs_from_fpstate()`, `kernel_fpu_begin_mask()`, `kernel_fpu_end()`, `fpu_clone()`, `fpu__clear_user_states()`, `switch_fpu_return()`, `fpregs_mark_activate()`, and KVM exports such as `fpu_swap_kvm_fpstate()`.

## Control Flow
Save/restore chooses XSAVE, FXSAVE, or legacy FSAVE/FRSTOR based on CPU features. Kernel FPU begin locks fpregs, marks kernel FPU unavailable, saves current user state if loaded, invalidates ownership, and initializes MXCSR/x87 as requested; end re-enables use and unlocks. Fork resets destination FPU, optionally copies parent state, inherits permissions, clears caller-saved dynamic state, and updates shadow-stack state. KVM swaps current task fpstate with guest fpstate around VM entry/exit and keeps XFD synchronized.

## State, Persistence, And Dependencies
State spans task-embedded `struct fpu`, fpstate buffers, permission masks, XFD MSR state, AVX512 timestamps, PKRU, thread flags, and per-CPU ownership. It depends on xstate helpers, KVM, pkeys, CET shadow stack, IRQ/preemption locking, tracepoints, and CPU feature flags.

## Integration Points
Used by scheduler context switching, signal frames, ptrace/core dumps, KVM, kernel crypto/math users, fork/exec, exception handling, and cpuidle AMX cleanup.

## Risks
FPU state corruption is high impact. Risks include incorrect lazy restore invalidation, using FPU in NMI or nested hardirq contexts, mishandling supervisor xstates, XFD state mismatch causing #NM, and KVM guest/host ABI divergence.

## Test Signals
Stress context switches, signal delivery/return, ptrace writes, KVM save/restore, AMX/XFD allocation, kernel_fpu_begin nesting checks, AVX512 use tracking, and fork/exec should show no FPU leaks or invalid exceptions.
