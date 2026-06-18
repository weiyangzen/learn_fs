# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/pmu.c

## Purpose
`pmu.c` implements AMD-specific KVM PMU operations for SVM. It maps AMD performance counter/control MSRs to KVM PMCs, handles RDPMC, programs event selectors and counters, derives guest-visible PMU capability from CPUID, and supports mediated PMU save/restore for AMD PerfMonV2 global control/status MSRs.

## Important APIs, types, and functions
- `enum pmu_type` distinguishes counter MSRs from event-select MSRs.
- `amd_pmu_get_pmc()`, `get_gp_pmc_amd()`, `amd_rdpmc_ecx_to_pmc()`, and `amd_msr_idx_to_pmc()` translate RDPMC indexes and AMD MSR numbers to `struct kvm_pmc`.
- `amd_is_valid_msr()` gates legacy K7, Family 15h core, and PerfMonV2 global PMU MSRs.
- `amd_pmu_get_msr()` and `amd_pmu_set_msr()` read/write PMC counters and event selectors, mask reserved bits, build `eventsel_hw` with guest-only behavior, and request counter reprogramming.
- `amd_pmu_refresh()` computes PMU version, number of counters, global reserved masks, counter bitmasks, reserved event bits, and fixed-counter absence from guest CPUID and host caps.
- `amd_pmu_init()` initializes the per-vCPU GP counter array.
- `amd_mediated_pmu_load()` and `amd_mediated_pmu_put()` switch AMD PerfMonV2 global status/control between host and guest.
- `amd_pmu_ops` exports the SVM PMU callbacks to KVM x86 core.

## Control flow
On vCPU PMU initialization, `amd_pmu_init()` seeds all possible AMD GP counters. After CPUID changes, `amd_pmu_refresh()` determines whether the guest has base PMU, `PERFCTR_CORE`, or `PERFMON_V2`, derives the counter count, and sets reserved masks. During MSR emulation, KVM calls `is_valid_msr`, then get/set callbacks. Counter MSRs call `pmc_read_counter()` or `pmc_write_counter()`; event selectors are masked and reprogrammed only when they actually change. RDPMC checks the index against the guest-visible counter count.

For mediated PMU, load clears any host global status, installs guest `global_status` and `global_ctrl`, and put disables global control, saves guest global status, and clears hardware status bits.

## State and persistence behavior
State is held in `struct kvm_pmu` and `struct kvm_pmc`: guest PMU version, GP counter count, counter bitmasks, reserved bit masks, raw event mask, per-counter `eventsel`, `eventsel_hw`, and counter values. Mediated PMU state persists `global_status` and `global_ctrl` across vCPU load/put. No file-local long-lived state exists beyond the `amd_pmu_ops` table.

## Dependencies and integration points
The file depends on KVM PMU core (`pmu.h`), CPUID helpers, perf event programming, MSR definitions, and SVM vCPU context switching. Nested SVM includes AMD PMU MSRs in its MSRPM merge list so PMU MSR interception is consistent for L2. PerfMonV2 depends on CPUID leaf `0x80000022`.

## Risks and edge cases
- MSR-to-counter mapping must handle overlapping K7 and Family 15h ranges and event/control parity correctly.
- Reserved bits in event selectors and global control/status must match AMD architecture and guest CPUID, or userspace-visible MSR behavior regresses.
- Mediated PMU global status clearing can perturb host PMU if load/put ordering is wrong.
- Counter counts are capped by host capability, so CPUID exposure and KVM PMU caps must remain synchronized.

## Test signals
Useful tests include PMU selftests for RDPMC bounds, K7 and F15h MSR aliases, PerfMonV2 global MSRs, event selector reserved-bit masking, CPUID counter count changes, mediated PMU vCPU switch behavior, and nested PMU MSR interception. Hardware perf counters and guest `perf` runs are practical integration checks.
