## `sources/distributed-fs/ceph-client/arch/x86/events/probe.h`

Purpose: declares the perf MSR probing descriptor and helper macros for simple PMU event sysfs groups.

Important APIs and types: `struct perf_msr` contains the MSR number, optional attribute group, optional predicate, `no_check` bypass, and value mask. `perf_msr_probe()` is declared for users such as RAPL. `PMU_EVENT_GROUP()` builds a one-attribute sysfs event group around an existing `attr_*` symbol.

Control flow: no runtime logic in the header; it provides the data contract consumed by `probe.c`.

State and persistence: descriptor arrays are normally static model tables. The pointed `attribute_group` objects may be mutated by `perf_msr_probe()` to hide or reveal events.

Dependencies and integration points: depends on `<linux/sysfs.h>` and x86 perf-event users. RAPL uses this contract to map hardware domain MSRs to perf event groups.

Risks: descriptor arrays with missing groups or wrong masks can hide valid events or expose unsupported ones. The `PMU_EVENT_GROUP` macro assumes naming conventions (`attr_<name>`) and should be used only where that generated symbol exists.

Test signals: compile coverage of descriptor arrays; sysfs event files appear only for present MSRs; probing returns correct bitmasks on platforms with known domain support.
