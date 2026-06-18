# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/monitor_mwait_test.c

Purpose: Tests KVM handling of `MONITOR` and `MWAIT` under different CPUID and emulation configurations, ensuring the instructions either execute or fault as expected.

Important APIs/types/functions: `CPUID_MWAIT` names the CPUID feature bit; `enum monitor_mwait_testcases` identifies scenarios; `GUEST_ASSERT_MONITOR_MWAIT()` emits an instruction and validates the fault vector; `guest_monitor_wait()` runs the guest cases. Host setup toggles CPUID exposure and KVM capability/quirk behavior.

Control flow: The host creates a vCPU with selected MONITOR/MWAIT exposure, runs the guest, and the guest executes monitor/mwait instruction sequences for each testcase. Expected vectors are compared to actual exception results.

State and persistence behavior: CPUID feature exposure is vCPU state. No persistent data is used.

Dependencies and integration points: Depends on x86 instruction emulation, CPUID filtering, KVM monitor/mwait capability behavior, and exception reporting.

Risks and maintenance notes: Hardware support, KVM policy, and userspace CPUID choices all affect expected results. The test must track KVM's intended virtualization policy for these power-management instructions.

Test signals: Passing means KVM consistently allows or rejects MONITOR/MWAIT according to CPUID/capability state. Failures indicate instruction-emulation or CPUID gating regressions.
