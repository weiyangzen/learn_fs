
# sources/distributed-fs/ceph-client/arch/powerpc/perf/generic-compat-pmu.c

## Purpose

This file provides a generic ISA v3-compatible Book3S PMU backend for systems that implement architected Power ISA PMU events but do not match a more specific IBM PMU driver.

## Important APIs, Types, And Functions

- The event enum defines architected ISA v3.0B raw event codes such as cycles, instructions completed, branch mispredicts, cache/TLB misses, and run events.
- `generic_event_alternatives` and `generic_get_alternatives()` provide alternate encodings via `isa207_get_alternatives()`.
- `GENERIC_EVENT_ATTR()` and `CACHE_EVENT_ATTR()` declarations create sysfs event aliases.
- Format attributes expose `event`, `pmcxsel`, and `pmc` bit fields.
- `compat_generic_events[]` and `generic_compat_cache_events[][][]` map standard perf hardware/cache events to raw ISA event codes.
- `generic_compute_mmcr()` delegates to `isa207_compute_mmcr()` and then sets `MMCR0_C56RUN` for counters 5 and 6.
- `generic_compat_pmu` is the `struct power_pmu` descriptor using ISA207 constraint, alternative, disable, and compute helpers.
- `init_generic_compat_pmu()` requires `CPU_FTR_ARCH_300`, registers the PMU, and advertises EBB to userspace.

## Control Flow

When model-specific Book3S PMU probes fail, `init_ppc64_pmu()` calls this initializer. If the CPU supports ISA 3.0, it registers the generic PMU. Later, `core-book3s.c` uses this descriptor to translate events, compute MMCR settings, expose sysfs aliases, and manage perf callbacks.

## State And Persistence

The file contains static maps and one static `struct power_pmu`. It mutates `cur_cpu_spec->cpu_user_features2` to advertise EBB after successful registration.

## Dependencies And Integration Points

It depends on `isa207-common.h` for constraints/MMCR computation and sysfs helper macros, Book3S core registration via `register_power_pmu()`, CPU feature flags, and perf sysfs attribute groups.

## Risks And Edge Cases

The fallback applies only to ISA 3.0+ because older ISA 2.07 lacks required events. Generic mappings may be less precise than model-specific drivers. Setting `MMCR0_C56RUN` is required for counters 5/6 on selected events. Advertising EBB assumes generic ISA support is sufficient.

## Test Signals

Test fallback registration on non-IBM ISA v3 systems, sysfs event aliases and format fields, generic/cache event counting, grouped events through ISA207 constraints, counters 5/6 behavior, and EBB visibility.
