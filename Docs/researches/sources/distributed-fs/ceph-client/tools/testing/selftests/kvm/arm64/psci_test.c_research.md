# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/psci_test.c

Purpose: this arm64 KVM selftest validates PSCI emulation, including CPU_ON reset state races, SYSTEM_SUSPEND UAPI exits, and PSCI v1.3 SYSTEM_OFF2 hibernate shutdown events.

Important APIs and functions: SMCCC wrappers `psci_cpu_on()`, `psci_affinity_info()`, `psci_system_suspend()`, `psci_system_off2()`, and `psci_features()` issue PSCI calls. Host helpers `vcpu_power_off()`, `setup_vm()`, `enter_guest()`, and `assert_vcpu_reset()` manage two-vCPU VMs. Test pairs include `guest_test_cpu_on()` / `host_test_cpu_on()`, `guest_test_system_suspend()` / `host_test_system_suspend()`, and `guest_test_system_off2()` / `host_test_system_off2()`.

Control flow: `main()` requires `KVM_CAP_ARM_SYSTEM_SUSPEND`, then runs the three host tests. `setup_vm()` creates two PSCI 0.2-capable vCPUs. CPU_ON powers off the target, guest calls CPU_ON, polls affinity, and host verifies target PC/x0 reset values. SYSTEM_SUSPEND enables the VM cap and expects `KVM_EXIT_SYSTEM_EVENT` with suspend type. SYSTEM_OFF2 verifies PSCI 1.3, exercises invalid-cookie and valid-cookie calls, and expects two shutdown exits flagged as PSCI_OFF2 before guest done.

State and persistence: vCPU MP state and core registers carry the tested state. No persistent state is stored.

Dependencies and integration points: depends on ARM PSCI SMCCC ABI, KVM PSCI version register, `KVM_CAP_ARM_SYSTEM_SUSPEND`, `KVM_EXIT_SYSTEM_EVENT`, MP state UAPI, and libkvm vCPU initialization/finalization.

Risks: PSCI feature availability and version are host/KVM dependent. The SYSTEM_OFF2 test restarts the source vCPU after each shutdown exit, so MP state manipulation must be correct.

Test signals: failures include wrong target reset PC/x0, missing suspend system event, missing PSCI_OFF2 shutdown flag, wrong PSCI return values, or unexpected ucall.
