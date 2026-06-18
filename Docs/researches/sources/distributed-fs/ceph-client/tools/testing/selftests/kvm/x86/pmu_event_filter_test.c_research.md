<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c

## Purpose
This selftest validates the x86 `KVM_SET_PMU_EVENT_FILTER` ABI. It checks PMU event allow and deny lists, masked event matching, fixed-counter bitmap semantics, invalid ioctl inputs, and PMU disablement through `KVM_CAP_PMU_CAPABILITY`. It runs on Intel architectural PMUs and AMD Zen/Hygon PMUs and skips when the host PMU or required KVM capabilities are unavailable.

## Important APIs, Types, and Functions
The central data type is the local ABI mirror `struct __kvm_pmu_event_filter`, which is cast to `struct kvm_pmu_event_filter` for `KVM_SET_PMU_EVENT_FILTER`. Important helpers are `intel_guest_code()`, `amd_guest_code()`, `sanity_check_pmu()`, `test_with_filter()`, `run_vcpu_and_sync_pmc_results()`, `test_masked_events()`, `test_filter_ioctl()`, `test_fixed_counter_bitmap()`, and `test_pmu_config_disable()`. The code uses PMU constants from `pmu.h`, MSR helpers from `processor.h`, KVM VM/vCPU helpers from `kvm_util.h`, and PMU feature probes such as `kvm_pmu_has()` and `kvm_cpu_property()`.

## Control Flow, State, and Persistence
`main()` requires PMU filtering and masked-event support, selects Intel or AMD guest PMU code, performs a guest MSR sanity check, then runs no-filter, member/non-member allow-list, and member/non-member deny-list cases. A second vCPU is created for masked-event tests when suitable counters exist. The guest repeatedly configures two or three PMCs, executes small instruction or load/store sequences, and copies deltas through the global `pmc_results`. Later tests validate ioctl rejection paths and fixed-counter filtering over every fixed-counter bitmap combination. State is transient in KVM VM/vCPU objects, PMU MSRs, the global result struct mirrored into guest memory, and KVM capability state; nothing is persisted.

## Dependencies and Integration Points
The test integrates with KVM's PMU virtualization, PMU event-filter ioctl, masked-event encoding, fixed performance counters, host CPUID PMU enumeration, AMD K7/Zen PMU aliases, and Intel architectural/event-specific encodings. It also exercises selftests infrastructure for guest exception handlers, `GUEST_SYNC`, and VM capabilities.

## Risks and Test Signals
Risks include host model-specific event availability, PMU errata such as branch-retired overcounting, nested virtualization or disabled vPMU making PMU MSRs unusable, and ABI drift in event-filter flags or fixed-counter masks. Strong signals are zero counts for filtered events, non-zero counts for allowed events, expected ioctl failures for invalid action/flags/nevents/masked entries, and fixed-counter count/no-count behavior matching allow/deny bitmap policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c -->
