# sources/distributed-fs/ceph-client/arch/x86/kernel/process_64.c

## Purpose
Implements 64-bit x86-specific register display, FS/GS base management, PKRU loading, context switching, personality transitions, VDSO mapping prctls, Linear Address Masking prctls, and 64-bit `arch_prctl` operations.

## APIs, Types, And Functions
Important functions include `__show_regs()`, `release_thread()`, inactive GS base helpers, `current_save_fsgs()`, `x86_fsgsbase_read_task()`, `x86_fsbase_read_task()`, `x86_gsbase_read_task()`, `x86_fsbase_write_task()`, `x86_gsbase_write_task()`, `start_thread()`, `compat_start_thread()`, `__switch_to()`, `set_personality_64bit()`, `set_personality_ia32()`, and `do_arch_prctl_64()`.

## Control Flow
Context switch saves FPU state, saves FS/GS selectors and bases before TLS changes, loads TLS, exits paravirt lazy mode, restores DS/ES and FS/GS using FSGSBASE or legacy MSR/selector paths, loads PKRU if needed, updates per-CPU current task/stack/TSS, runs extra switch work, applies SYSRET SS workaround, schedules resctrl state, and clears AMD workload history. `start_thread_common()` resets thread features and builds the user return frame, with FRED-specific NMI/single-step bits. `do_arch_prctl_64()` implements FS/GS base set/get, checkpoint-restore VDSO mapping, LAM/tagged-address operations, and shadow-stack prctls.

## State And Persistence
Per-task `thread_struct` stores FS/GS selectors/bases, DS/ES, PKRU, and personality flags. LAM state persists in `mm->context` masks and flags. FRED, Xen PV, FSGSBASE, and CPU erratum feature bits change which hardware registers are touched.

## Dependencies And Integration
Depends on scheduler, FPU, descriptors/TLS, FSGSBASE, FRED, Xen PV, PKRU, resctrl, syscall/personality ABI, VDSO images, address masking, shadow stacks, and KVM export of `current_save_fsgs()`.

## Risks And Test Signals
FS/GS handling is ABI-critical and security-sensitive; mistakes can corrupt TLS, percpu GS, or ptrace-visible bases. Other risks include PKRU leaks, SYSRET SS erratum regressions, LAM enabling while multithreaded, and VDSO remap misuse. Test signals include glibc TLS/thread tests, ptrace FS/GS tests, compat and x32 exec, PKU tests, LAM prctl selftests, shadow-stack tests, KVM use of `current_save_fsgs()`, and context-switch stress.
