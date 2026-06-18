# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_arm.c

Purpose: supplies the ARM architecture backend for the KVM virtual PTP clock. The common `ptp_kvm_common.c` module owns PHC registration; this file only verifies that the KVM hypervisor service is available and routes simple clock reads through the architecture crosstimestamp implementation.

Important APIs/types/functions: `kvm_arch_ptp_init()` checks `kvm_arm_hyp_service_available(ARM_SMCCC_KVM_FUNC_PTP)` and returns `-EOPNOTSUPP` when unavailable. `kvm_arch_ptp_exit()` is a no-op. `kvm_arch_ptp_get_clock()` calls `kvm_arch_ptp_get_crosststamp(NULL, ts, NULL)`, relying on the ARM implementation declared in `linux/ptp_kvm.h` and architecture support.

Control flow: module initialization in the common file invokes `kvm_arch_ptp_init()`. If the SMCCC KVM PTP function is present, common registration continues; otherwise the module exits quietly for unsupported guests. Runtime `gettime64` requests call `kvm_arch_ptp_get_clock()`, which delegates to crosstimestamp acquisition.

State and persistence: no local state, no allocations, no hardware programming, and no persistent data. Availability is probed each load.

Dependencies and integration: depends on ARM SMCCC, ARM arch timer support, hypervisor detection, and the common KVM PTP module. It is intentionally tiny because ARM-specific crosstimestamp mechanics live outside this file.

Risks and test signals: the main risk is availability mismatch between advertised SMCCC support and working crosstimestamp calls. Build tests need ARM configurations with `CONFIG_PTP_1588_CLOCK_KVM`; runtime tests need KVM guests with and without `ARM_SMCCC_KVM_FUNC_PTP`, plus `phc2sys` or `testptp` reads confirming `-EOPNOTSUPP` on unsupported hosts and stable timestamps on supported hosts.
