
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpumask.h

Purpose: x86-special cpumask helpers for early/instrumentation-sensitive online CPU checks.

Important APIs and control flow: declares `setup_cpu_local_masks()`. For SMP builds, `arch_cpu_online()` tests `cpu_online_mask` with `arch_test_bit()` and `arch_cpumask_clear_cpu()` clears with `arch_clear_bit()` after `cpumask_check()`. UP builds return CPU 0 online and no-op clear. `arch_cpu_is_offline()` wraps the negated online check.

State, dependencies, and risks: state is global and per-CPU cpumasks. Dependencies include generic cpumask and x86 bitops. Risks include using instrumented generic checks in NMI/MCE paths, stale online masks during hotplug, and invalid CPU indexes. Test signals are CPU hotplug, NMI/MCE paths on offlined CPUs, and cpumask selftests.
