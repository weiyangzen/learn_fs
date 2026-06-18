# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hello_el2.c

Purpose: this basic arm64 KVM selftest verifies a VM can run at EL2 with E2H described as RES1 and with virtual-host-extension expectations satisfied.

Important APIs and functions: `guest_code()` reads `ID_AA64MMFR0_EL1`, `ID_AA64MMFR1_EL1`, `ID_AA64MMFR4_EL1`, checks `get_current_el()`, `HCR_EL2_E2H`, VH field support, E2H0 semantics, and FGT behavior. `main()` creates an EL2-capable vCPU by setting `KVM_ARM_VCPU_HAS_EL2`.

Control flow: host requires `KVM_CAP_ARM_EL2`, creates a one-vCPU VM without the convenience one-vCPU helper so it can modify `struct kvm_vcpu_init`, finalizes vCPUs, runs once, and handles `UCALL_DONE` or guest abort. The guest asserts it is executing at EL2 and validates the ID register story around E2H0/FGT.

State and persistence: no persistent state. The only runtime state is vCPU feature configuration and guest register values.

Dependencies and integration points: depends on arm64 nested/EL2 KVM support, sysreg helpers, `ucall`, and KVM vCPU target/finalization APIs.

Risks: ID register behavior around E2H0 and FGT is subtle; the test allows IMPDEF trap behavior by accepting all-zero reads in the appropriate case. Systems without EL2 KVM support skip.

Test signals: guest assertions for current EL, HCR.E2H, VH support, and E2H0/FGT fields are the main signal; any unexpected ucall fails.
