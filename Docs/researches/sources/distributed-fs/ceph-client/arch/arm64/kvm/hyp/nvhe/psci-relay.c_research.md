<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c

## Purpose
`psci-relay.c` intercepts host PSCI SMCs so CPU_ON and suspend resume through hyp entry points, preserving EL2 control while still forwarding firmware power-management calls. It validates target CPUs against the hyp CPU map and stores boot arguments until the target CPU reaches hyp.

## Important APIs, Types, and Functions
`kvm_host_psci_config` stores host-configured PSCI version and function IDs. `struct psci_boot_args` stores a lock, target PC, and x0. `psci_cpu_on()`, `psci_cpu_suspend()`, and `psci_system_suspend()` replace firmware entry addresses with `kvm_hyp_cpu_entry` or `kvm_hyp_cpu_resume`. `__kvm_host_psci_cpu_on_entry()` and `__kvm_host_psci_cpu_resume_entry()` restore saved host PC/x0 and enter the host through `__host_enter()`. `psci_0_1_handler()`, `psci_0_2_handler()`, `psci_1_0_handler()`, and `kvm_host_psci_handler()` select version-specific handling.

## Control Flow, State, and Persistence
CPU_ON finds the logical CPU by MPIDR, locks that CPU’s boot args, records host PC/x0, issues firmware SMC with the hyp entry physical address and that CPU’s init params, and leaves the lock held until the target CPU consumes it. CPU suspend/system suspend use per-current-CPU suspend args without a lock because only the current CPU can suspend itself. Entry functions restore EL1 SCTLR/PSTATE/ELR context and return to the host.

## Dependencies and Integration Points
It depends on `hyp-smp.c` CPU maps, `hyp-init.S` CPU entry/resume labels, `kvm_init_params`, SMCCC wrappers, tracing, and host SMC dispatch in `hyp-main.c`.

## Risks and Test Signals
Risks include rejecting valid CPUs not online at KVM init, boot-args lock leaks if firmware behavior is unexpected, PSCI 0.1 function-id configuration errors, and resume-state ordering. Test signals include CPU_ON success/failure, duplicate CPU_ON returning already-on, suspend/resume, system suspend, PSCI version variants, invalid MPIDR rejection, and tracing of PSCI enter/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c -->
