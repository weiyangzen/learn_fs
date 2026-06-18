<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c

## Purpose
`sysreg-sr.c` provides the non-VHE save/restore wrappers for CPU system-register state. In nVHE, host and guest both need complete EL1/common/user/return-state save and restore around guest execution.

## Important APIs, Types, and Functions
`__sysreg_save_state_nvhe()` calls `__sysreg_save_el1_state()`, `__sysreg_save_common_state()`, `__sysreg_save_user_state()`, and `__sysreg_save_el2_return_state()`. `__sysreg_restore_state_nvhe()` restores EL1 state using saved MIDR/MPIDR, then common, user, and EL2 return state.

## Control Flow, State, and Persistence
The file has linear save/restore flow and persists state only in the caller-provided `struct kvm_cpu_context`. It is invoked for both host and guest contexts during `__kvm_vcpu_run()`.

## Dependencies and Integration Points
It depends on generic hyp sysreg save/restore primitives and `struct kvm_cpu_context` layout. It integrates directly with `switch.c` guest entry/exit and indirectly with pKVM vCPU synchronization in `hyp-main.c`.

## Risks and Test Signals
Risks include omissions when new sysregs are added to common helpers, MIDR/MPIDR restore assumptions, and ordering issues with stage-2/trap activation. Test signals are guest/host sysreg preservation across exits, migration of vCPUs between CPUs with compatible MIDR handling, and architecture feature additions that expand generic save/restore helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c -->
