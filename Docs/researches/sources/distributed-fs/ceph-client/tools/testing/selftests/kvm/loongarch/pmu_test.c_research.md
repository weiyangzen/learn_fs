<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c

## Purpose
`loongarch/pmu_test.c` validates LoongArch KVM PMU virtualization. It checks PMU availability, basic event counting for cycles/instructions/branches/branch misses, and delivery of a PMU overflow interrupt.

## Important APIs, Types, and Functions
Important functions are `has_pmu_support()`, `dump_pmu_caps()`, `guest_pmu_base_test()`, `guest_irq_handler()`, `guest_pmu_interrupt_test()`, `guest_code()`, and `main()`. The guest manipulates `LOONGARCH_CSR_PERFCNTR0-3` and `LOONGARCH_CSR_PERFCTRL0-3`, uses event constants from `pmu.h`, and handles `INT_PMI`.

## Control Flow
Host setup skips if CPUCFG6 says no PMU or no counters, dumps capabilities, creates a VM/vCPU, installs the interrupt handler, checks `KVM_LOONGARCH_VM_FEAT_PMU`, and runs the guest. Guest base test clears counters, configures four events, executes a relaxation loop, reads counters, and asserts ranges. The interrupt test preloads counter 0 near overflow, enables PMIE for cycles, spins, and expects one interrupt.

## State and Persistence
State includes guest PMU CSRs and global `pmu_irq_count`, which is synchronized into the guest. Host state is limited to VM feature discovery and ucall handling.

## Dependencies and Integration Points
The file depends on LoongArch processor helpers, `kvm_util.h`, `ucall_common.h`, PMU constants, `KVM_HAS_DEVICE_ATTR`, and exception table initialization. It integrates with KVM's LoongArch VM feature control ABI.

## Risks and Test Signals
Risks include hardware PMU absence, VM PMU feature disabled, counter-width mismatches, imprecise event ranges on different cores, and missing PMI delivery. Test signals include skip output for unsupported hosts, PMU capability prints, guest counter range assertions, `pmu_irq_count == 1`, and host handling of `UCALL_DONE` versus `UCALL_ABORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c -->
