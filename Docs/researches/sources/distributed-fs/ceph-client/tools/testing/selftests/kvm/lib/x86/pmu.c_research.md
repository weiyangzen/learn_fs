<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c

## Purpose
`pmu.c` centralizes x86 PMU event lists and host errata detection for KVM selftests. It supplies canonical Intel architectural event encodings, AMD Zen event encodings, and an errata mask for CPUs that overcount certain retired events.

## Important APIs, Types, and Functions
The file exports `intel_pmu_arch_events[]`, `amd_pmu_zen_events[]`, `pmu_errata_mask`, and `kvm_init_pmu_errata()`. Internal `get_pmu_errata()` checks vendor, family, and model to set `INSTRUCTIONS_RETIRED_OVERCOUNT` and `BRANCHES_RETIRED_OVERCOUNT` bits.

## Control Flow
Static assertions ensure event arrays match `NR_INTEL_ARCH_EVENTS` and `NR_AMD_ZEN_EVENTS`. Initialization runs once through architecture setup and records model-specific errata for later guest-visible synchronization.

## State and Persistence
`pmu_errata_mask` is global process state and is synchronized into guests by x86 VM setup. There is no external persistence.

## Dependencies and Integration Points
The file depends on `pmu.h`, `processor.h`, `linux/kernel.h`, and CPU vendor/model helpers. It integrates with PMU selftests that need to suppress or adjust expectations for known Intel Atom event-counting errata.

## Risks and Test Signals
Risks include incomplete model coverage, incorrect event-array ordering, or failing to sync errata state to guests. Test signals are compile-time array-size assertions and PMU tests that account for `pmu_errata_mask` when validating retired instruction or branch counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c -->
