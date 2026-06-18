<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c

Purpose: this arm64 vPMU selftest verifies that userspace-selected PMU event counter count (`PMCR_EL0.N`) is reflected to the guest, that implemented counters are accessible through both direct and indirect sysregs, that unimplemented counters trap or read-as-zero as required, and that userspace register accesses honor the configured counter count.

Important APIs, types, and functions: `struct vpmu_vm` holds the active VM and vCPU. `struct pmc_accessor` abstracts direct `PMEV{CNTR,TYPER}<n>_EL0` access and indirect `PMXEV{CNTR,TYPER}_EL0` access through `PMSELR_EL0`. `get_pmcr_n()`, `get_counters_mask()`, `pmu_disable_reset()`, `test_bitmap_pmu_regs()`, `test_access_pmc_regs()`, and `test_access_invalid_pmc_regs()` implement guest-side checks. `guest_sync_handler()` validates expected exception classes and skips trapping instructions. Host-side `create_vpmu_vm()`, `test_create_vpmu_vm_with_nr_counters()`, `run_access_test()`, `run_pmregs_validity_test()`, and `run_error_test()` exercise device attributes including `KVM_ARM_VCPU_PMU_V3_SET_NR_COUNTERS` and `KVM_ARM_VCPU_PMU_V3_INIT`.

Control flow: `main()` requires `KVM_CAP_ARM_PMU_V3`, VGICv3, and the set-number-of-counters attribute. It discovers the host/guest PMCR.N limit, runs access and host-register-validity tests for every count from zero through the limit, and then verifies larger counts fail with `EINVAL`. Each access test runs the guest twice: before and after vCPU reset/reinitialization, restoring SP and PC to ensure PMCR.N persistence.

State, persistence, and dependencies: state is VM/vCPU PMU register state and guest exception-handler state (`expected_ec`). Dependencies include arm PMUv3 register definitions from `<perf/arm_pmuv3.h>`, VGIC support for the PMU interrupt, descriptor-table setup, PMEVN register-switch macros, and arm64 exception decoding.

Risks and edge cases: counter count zero is valid and leaves only the cycle counter valid. Unimplemented event counter direct/indirect accesses must raise `ESR_ELx_EC_UNKNOWN`; bitmap registers must mask unimplemented counters. Host register set/clear aliases must not retain invalid bits. The test intentionally uses all accessor combinations to catch inconsistencies between direct and selected register paths.

Test signals: guest assertions validate PMCR.N, bitmap masks, read/write round-trips, undefined exceptions for invalid counters, and reset persistence. Host assertions validate PMUVer exposure, device attr success/failure, and masking in `PMCNTEN`, `PMINTEN`, and `PMOVS` set/clear registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c -->
