# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/no-vgic.c

Purpose: this arm64 KVM selftest verifies that when a VM is created without a VGIC, GICv3 and GICv5 system register/instruction interfaces are hidden from the guest and accesses trap as UNDEF.

Important APIs and functions: guest macros issue sysreg reads/writes and GICv5 operations while checking a volatile `handled` flag. `guest_code_gicv3()` validates `ID_AA64PFR0_EL1.GIC == 0` and probes many ICC registers. `guest_code_gicv5()` validates `ID_AA64PFR2_EL1.GCIE == 0`, probes GICv5 ops and registers. `guest_undef_handler()` marks success and advances PC. Host `test_guest_no_vgic()` creates the no-GIC VM and installs the unknown-exception handler.

Control flow: `main()` calls `test_disable_default_vgic()`, probes whether the host supports GICv3/GICv5 in a temporary VM, requires at least one, and runs the corresponding guest tests. Each guest access is expected to trap to `ESR_ELx_EC_UNKNOWN`, except `ICC_SRE_EL1` may legally be untrappable if SRE is RAO/WI.

State and persistence: guest global `handled` records whether the last access trapped. No durable state is stored.

Dependencies and integration points: depends on arm64 GIC system register encodings, optional GICv5 helper macros, KVM no-default-VGIC mode, and descriptor-table handlers.

Risks: GIC register trap semantics have legal exceptions, which the test handles for `ICC_SRE_EL1`. New GIC registers or GICv5 features may require expanding the probe list.

Test signals: a failure indicates feature ID bits are exposed without VGIC, an access did not UNDEF, or an unexpected ucall occurred. Informational prints show skipped v3/v5 subtests.
