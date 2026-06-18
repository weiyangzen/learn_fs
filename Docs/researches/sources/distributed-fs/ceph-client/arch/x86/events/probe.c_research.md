## `sources/distributed-fs/ceph-client/arch/x86/events/probe.c`

Purpose: probes arrays of perf MSR descriptors and controls sysfs visibility for event groups whose backing MSRs are unavailable or zero.

Important APIs and functions: `perf_msr_probe(struct perf_msr *msr, int cnt, bool zero, void *data)` iterates a descriptor array, applies optional per-entry `test()` filtering, safely reads the MSR with `rdmsrq_safe()`, optionally rejects zero-valued counters, and returns an availability bitmask. `not_visible()` is assigned to an attribute group to hide unsupported sysfs entries.

Control flow: the probe rejects overly large arrays (`cnt >= BITS_PER_LONG`), hides each checked group by default, skips empty descriptors, applies the descriptor-specific predicate, verifies MSR readability, checks the masked value when zero counters are disallowed, and restores default visibility for entries that pass.

State and persistence: mutates `struct attribute_group.is_visible` for the groups referenced by descriptors; returns transient bit state to the caller. It does not retain private state.

Dependencies and integration points: exported GPL symbol used by RAPL and similar PMU drivers. Depends on `struct perf_msr` from `probe.h`, x86 MSR helpers, sysfs attribute groups, and descriptor masks.

Risks: changing group visibility has global sysfs consequences. A descriptor with `no_check` bypasses all validation and always sets availability, so callers must only use it when the MSR is known present. Virtualization may make read-only MSR presence ambiguous; the code deliberately treats read failures as absence.

Test signals: RAPL PMU sysfs event visibility on systems with partial domains, virtualized boots without RAPL MSRs, and build/load tests for modules using `perf_msr_probe()`.
