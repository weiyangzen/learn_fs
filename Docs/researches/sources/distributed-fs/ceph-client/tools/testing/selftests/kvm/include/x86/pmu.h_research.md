# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/pmu.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/pmu.h

Purpose: x86 PMU constants and helper declarations for KVM selftests. It encodes Intel/AMD event selectors, architectural PMU control bits, RDPMC flags, fixed counter controls, PMU capability bits, event indexes, and errata tracking.

Important APIs/types/functions: `KVM_PMU_EVENT_FILTER_MAX_EVENTS`, `RAW_EVENT`, `ARCH_PERFMON_EVENTSEL_*`, `INTEL_RDPMC_*`, `FIXED_PMC_*`, `PMU_CAP_*`, Intel and AMD event constants, `enum intel_pmu_architectural_events`, `enum amd_pmu_zen_events`, external event arrays, `enum pmu_errata`, `pmu_errata_mask`, `kvm_init_pmu_errata`, and `this_pmu_has_errata`.

Control flow and state: tests initialize errata state, query CPUID PMU features from `processor.h`, program event select MSRs/counters, run workloads, and validate counts or filter behavior. Persistent state includes vCPU PMU MSRs, global PMU errata mask, and host/KVM CPUID feature exposure.

Dependencies and integration: depends on Linux bit macros and x86 processor CPUID helpers. It integrates with PMU event-filter, RDPMC, fixed-counter, and migration tests.

Risks: PMU event behavior is CPU-vendor and model specific. The header explicitly tracks errata because exact counts can be unreliable. Event index ordering must stay aligned with CPUID architectural PMU enumeration.

Test signals: PMU selftests validate event encoding, supported-feature gating, counter increments, RDPMC paths, event filters, and errata handling.
