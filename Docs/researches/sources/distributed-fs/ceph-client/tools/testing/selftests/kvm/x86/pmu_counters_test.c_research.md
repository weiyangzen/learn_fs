# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_counters_test.c

Purpose: Provides extensive Intel vPMU counter coverage. It tests architectural events, general-purpose counters, fixed counters, RDPMC behavior, event masks, PMU versions through v5, and `MSR_IA32_PERF_CAPABILITIES` fixed-counter write support.

Important APIs/types/functions: `struct kvm_intel_pmu_event` maps Intel architectural event indexes to selftest PMU features; `pmu_vm_create_with_one_vcpu()` configures PMU CPUID and perf capabilities; `guest_assert_event_count()` validates measured event counts; `GUEST_MEASURE_EVENT()` and `GUEST_TEST_EVENT()` produce tightly controlled assembly measurement windows; `guest_test_arch_event()`, `guest_test_gp_counters()`, and `guest_test_fixed_counters()` implement guest matrices; `test_intel_counters()` drives host-side PMU version/counter/mask/perf-cap permutations.

Control flow: `main()` requires PMU enabled, Intel host, and a positive PMU version. Host code records hardware-supported architectural events, then iterates PMU versions from 0 through at least 5, perf capability variants, event-mask lengths and unavailable masks, general-purpose counter counts, fixed counter counts, and fixed-counter bitmasks. Each configuration creates a VM, adjusts CPUID/MSRs, runs a guest test, and destroys the VM.

State and persistence behavior: PMU state is vCPU-local MSR and CPUID state. Guest tests write counter MSRs, event-select MSRs, fixed-control MSRs, and global control MSRs. No external state is persisted.

Dependencies and integration points: Depends on Intel PMU hardware, KVM vPMU support, `pmu.h` feature helpers, RDPMC safe wrappers, forced-emulation support for optional instruction-retirement checks, CLFLUSH/CLFLUSHOPT for LLC event stimulation, and `MSR_IA32_PERF_CAPABILITIES` when PDCM is present.

Risks and maintenance notes: Runtime can be large because the matrix is broad. Counts for instructions and branches account for known overcount errata. The test deliberately fails when hardware exposes new architectural events not represented in `NR_INTEL_ARCH_EVENTS`, forcing test updates. Timing-independent assembly minimizes compiler noise but is fragile.

Test signals: Passing means KVM's Intel vPMU exposes and virtualizes counters, event masks, RDPMC, fixed counters, global controls, and perf capabilities consistently across advertised PMU versions. Failures are strong signals for vPMU CPUID enumeration, MSR filtering, event counting, or counter access regressions.
