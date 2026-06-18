<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h

Purpose: this header provides simple guest-side busy-wait delay helpers for arm64 KVM selftests.

Important APIs, types, and functions: `__delay(u64 cycles)` reads the virtual timer counter with `timer_get_cntct(VIRTUAL)` and spins with `cpu_relax()` until the requested cycle delta elapses. `udelay(unsigned long usec)` converts microseconds to cycles with `usec_to_cycles()` from `arch_timer.h`.

Control flow: both helpers are inline and synchronous; they never yield to the host except through normal vCPU scheduling.

State, persistence, and dependencies: no persistent state. Dependencies are the virtual generic timer helpers in `arch_timer.h` and `cpu_relax()` from processor helpers.

Risks and edge cases: this is a busy wait, so long delays consume guest CPU time. Timing precision depends on the virtual counter frequency and scheduling latency.

Test signals: downstream tests use these helpers when they need approximate guest-side delay without host coordination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h -->
