# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/timer_test.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/timer_test.h

Purpose: cross-architecture timer selftest interface. It defines common timer-test parameters, guest/host synchronization points, and arch hooks so timer behavior can be validated consistently.

Important APIs/types/functions: timer-test constants, guest timer workload declarations, host setup helpers, and architecture hook declarations for enabling, programming, and checking virtual timer interrupts.

Control flow and state: host code creates vCPUs and shared timer test state, guest code programs an architecture timer, waits for interrupts or exits, and reports results. State includes per-vCPU timer configuration, interrupt counters, and synchronization flags.

Dependencies and integration: included by architecture timer implementations such as arm64, RISC-V, and LoongArch timer tests. Depends on `kvm_util.h`, guest interrupt helpers, and `test_util.h`.

Risks: timer tests are scheduling-sensitive and can be flaky if host load is high. Architecture timer frequency and interrupt controller setup must be correct before interpreting guest failures as KVM bugs.

Test signals: architecture timer selftests validate interrupt delivery timing, timer state migration or get/set behavior, and expected skips on unsupported hosts.
