<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h

## Purpose
`arm_pmu.h` defines ARM PMUv3 virtualization interfaces for KVM VCPUs and supplies no-op stubs when hardware perf events or KVM PMU support are disabled.

## Important APIs, types, and functions
With support enabled, it defines `KVM_ARMV8_PMU_MAX_COUNTERS`, `struct kvm_pmc`, `struct kvm_pmu_events`, `struct kvm_pmu`, and `struct arm_pmu_entry`. APIs cover support detection, counter read/write, implemented/access masks, PMCEID, VCPU init/destroy, counter reprogramming, hwstate flush/sync, run notification, software increment, PMCR handling, event type setup, PMU reload, KVM device attributes, PMUv3 enablement, host/guest PMU state restore, PMU version/counter limits, event type masking, default PMU selection, and nested transition.

## Control flow
VCPU PMU state is initialized during VCPU setup, programmed before guest entry, synced/flushed around runs, and restored between host and guest contexts. `kvm_pmu_update_vcpu_events()` copies per-CPU PMU event masks with interrupts disabled on non-VHE systems.

## State and persistence behavior
`struct kvm_pmu` stores perf-event-backed counters, overflow irq work, event masks, IRQ number/level, and created state. Counter values and device attributes are part of VCPU/VM migration-visible state.

## Dependencies and integration points
The header integrates KVM, Linux perf events, ARM PMUv3 definitions, IRQ work, VCPU feature bits, and KVM device attribute plumbing. Stub definitions return false, zero, `-ENXIO`, or `-ENODEV` so callers can compile unconditionally.

## Risks and test signals
Risks include host/guest PMU state leaks, incorrect counter accessibility masks, IRQ level mismatches, unsupported builds silently taking stubs, and nested virtualization transitions losing hyp counters. Test signals include KVM PMU selftests, perf event lifecycle tests, migration of PMU state, IRQ overflow tests, and builds with PMU support disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h -->
