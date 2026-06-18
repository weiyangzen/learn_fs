<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c

## Purpose
This file provides helpers for entering and leaving kernel Altivec/VMX regions used by optimized usercopy and memory operations.

## Important APIs, types, and functions
Exported usercopy APIs are `enter_vmx_usercopy` and `exit_vmx_usercopy`. Non-exported operation helpers are `enter_vmx_ops` and `exit_vmx_ops`. They call `enable_kernel_altivec`, `disable_kernel_altivec`, `pagefault_disable`, `pagefault_enable`, and preemption helpers.

## Control flow
Enter helpers return zero in interrupt context, otherwise disable preemption and enable kernel Altivec. The usercopy variant also disables page faults so faults fall back to non-VMX copying. Exit helpers disable Altivec and restore pagefault/preemption state; `exit_vmx_usercopy` schedules a near decrementer interrupt if preemption is needed.

## State and persistence behavior
The helpers temporarily change preemption state, page-fault handling, VMX ownership, and possibly the decrementer. They do not persist data.

## Dependencies and integration points
They integrate with PowerPC optimized copy routines, KUAP-sensitive usercopy, kexec copy paths with MMU off, and scheduler/preemption logic.

## Risks and edge cases
Calling schedule while KUAP is unlocked is unsafe, so `exit_vmx_usercopy` uses `preempt_enable_no_resched` and a decrementer nudge. Missing enter/exit pairing would leave VMX or fault/preempt state inconsistent.

## Test signals
Signals come from usercopy/memcpy correctness under VMX-enabled builds, fault fallback behavior, and absence of scheduler/KUAP assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c -->
