# sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.h

Purpose: declares perf's userspace hwmon PMU interface. It models Linux hwmon sysfs files named like `<type><num>_<item>` as perf PMU events, so sensors can be discovered, parsed, exposed as event aliases, opened, and read through perf's PMU/evsel paths.

Important APIs and types: `enum hwmon_type` lists supported sysfs type prefixes such as `temp`, `fan`, `power`, `energy`, and `cpu`; `enum hwmon_item` lists suffix items such as `input`, `max`, `crit`, `alarm`, and `label`; `union hwmon_pmu_event_key` packs a 16-bit number and 8-bit type into a `long` key for event grouping. Public functions include `parse_hwmon_filename()`, `hwmon_pmu__new()`, `hwmon_pmu__exit()`, event iteration/count/existence helpers, parse-events term validation/configuration helpers, `perf_pmus__read_hwmon_pmus()`, and evsel open/read hooks.

Control flow: discovery starts from `perf_pmus__read_hwmon_pmus()`, which populates a PMU list using `hwmon_pmu__new()`. Parser and alias callbacks translate user event names into `perf_event_attr`/terms. Runtime evsels are identified by `perf_pmu__is_hwmon()` and `evsel__is_hwmon()`, opened with `evsel__hwmon_pmu_open()`, and sampled/read with `evsel__hwmon_pmu_read()`.

State and persistence: the header defines no storage directly, but the event-key union implies an internal event map keyed by type/number, with item metadata maintained by the corresponding implementation. No persistent disk writes are declared; persistent input is hwmon sysfs.

Dependencies and integration: depends on perf core PMU types, parse-events structures, evsel, `list_head`, and thread maps. It integrates the kernel hwmon sysfs ABI into perf PMU enumeration and event parsing.

Risks: filename parsing must match the hwmon ABI precisely, including alarms and labels. The bitfield union is endian-sensitive and explicitly exposed for testing. Sensor files are not perf events in the kernel sense, so open/read behavior must avoid assumptions made for hardware counters.

Test signals: focused tests should cover parse cases for all supported type/item names, alarm detection, big-endian key layout, alias validation errors, event iteration counts, and read/open behavior against temporary sysfs-like fixtures.
