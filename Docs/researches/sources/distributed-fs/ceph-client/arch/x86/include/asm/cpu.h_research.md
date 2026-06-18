
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu.h

Purpose: shared x86 CPU initialization, hotplug, split-lock, microcode, and architecture capability declarations.

Important APIs and control flow: declares CPU restart/hotplug hooks, APERF/MPERF init, `mwait_usable()`, signature extraction helpers, optional split-lock/bus-lock handling, IA32 feature-control init, CET disable, Intel microcode helpers, architecture capability MSR reader, and `cpus_stop_mask`. Unsupported feature blocks provide no-op or false-returning stubs.

State, dependencies, and risks: state includes CPU feature state, microcode metadata, split-lock policy, and stop masks. Dependencies include topology, cpumasks, IBT/CET, and vendor-specific code. Risks include config-gated stubs masking missing behavior, split-lock exception handling in user/guest paths, and microcode signature mismatches. Test signals are CPU hotplug, microcode loading, split-lock selftests, and capability MSR tests.
