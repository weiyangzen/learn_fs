# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf_events.c

Purpose: defines the s390 CPU-Measurement Counter Facility perf event sysfs inventory. It maps CPUMF hardware counter numbers to named perf PMU events, grouped by counter facility version, crypto counter version, and IBM Z machine generation.

Important APIs/types/functions: the file is almost entirely generated-style `CPUMF_EVENT_ATTR()` declarations and `CPUMF_EVENT_PTR()` arrays. It exports `cpumf_cf_event_group()`, which returns the `attribute_group` set used by the counter-facility PMU. The helper `merge_attr()` allocates one NULL-terminated attribute array from the selected generic CFVN set, CSVN crypto set, and model-specific set. The static groups are `cpumcf_pmu_events_group`, `cpumcf_pmu_format_group`, and `cpumcf_pmu_attr_groups`.

Control flow: initialization-time callers invoke `cpumf_cf_event_group()`. It queries counter metadata with `qctri()`, selects generic counters for `cfvn` 1 or 3, selects crypto counters for `csvn` 1-5 or 6+, then calls `get_cpu_id()` and dispatches on machine IDs for z10, z196, zEC12, z13, z14, z15, z16, and z17. The chosen arrays are concatenated and assigned to `cpumcf_pmu_events_group.attrs`; the format group exposes `event` as `config:0-63`.

State and persistence: state is static attribute data plus one allocated merged attribute pointer table retained after init. No runtime counter values are stored here and no persistent storage is touched.

Dependencies and integration points: depends on `linux/perf_event.h`, `asm/cpu_mf.h`, `qctri()`, `get_cpu_id()`, and `cpumf_events_sysfs_show()` from `perf_event.c`. It integrates with the counter-facility PMU registration path by supplying sysfs `events/` and `format/` groups.

Risks: the table is a hardware ABI surface; wrong event numbers or wrong model gating exposes misleading perf events. `merge_attr()` returns NULL on allocation failure, in which case callers get the groups but without newly populated event attrs. Adding machine generations must preserve unique CPUMF event identifiers across CF, sampling, and PAI spaces.

Test signals: boot on each supported IBM Z generation should show the expected `/sys/bus/event_source/devices/cpum_cf/events/*` names, `perf list` should contain model-appropriate counters, raw event encodings should match architecture manuals, and unsupported models should still expose valid generic/crypto sets when `qctri()` reports them.
