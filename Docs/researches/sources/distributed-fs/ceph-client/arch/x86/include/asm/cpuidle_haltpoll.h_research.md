
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuidle_haltpoll.h

Purpose: arch hooks for haltpoll cpuidle enable/disable on x86.

Important APIs and control flow: declares `arch_haltpoll_enable(unsigned int cpu)` and `arch_haltpoll_disable(unsigned int cpu)`. Actual policy and state transitions live in the haltpoll/cpuidle implementation.

State, dependencies, and risks: state is per-CPU haltpoll behavior outside the header. Dependencies include cpuidle/haltpoll drivers and CPU hotplug paths. Risks include enabling haltpoll on unsuitable CPUs or missing disable during hotplug. Test signals are haltpoll driver tests, virtualization latency measurements, and CPU online/offline coverage.
