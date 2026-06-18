<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c

## Purpose
`hwmon_pmu.c` exposes Linux hwmon sysfs sensors as synthetic perf PMUs/events. It discovers `/sys/class/hwmon/hwmon*`, parses sensor files such as `temp1_input`, lists events with labels/descriptions, configures perf attrs from event terms, opens sensor input files, and reads counts.

## Important APIs, types, and functions
Public functions are `perf_pmu__is_hwmon`, `evsel__is_hwmon`, `parse_hwmon_filename`, `hwmon_pmu__new`, `hwmon_pmu__exit`, `hwmon_pmu__for_each_event`, `hwmon_pmu__num_events`, `hwmon_pmu__have_event`, `hwmon_pmu__config_terms`, `hwmon_pmu__check_alias`, `perf_pmus__read_hwmon_pmus`, `evsel__hwmon_pmu_open`, and `evsel__hwmon_pmu_read`. Internal `struct hwmon_pmu` embeds `perf_pmu`; `struct hwmon_pmu_event_value` tracks present item/alarm bitmaps, label, and generated name.

## Control flow
Discovery scans sysfs class hwmon symlinks, opens each device name, creates PMUs named `hwmon_<fixed-name>`, and assigns synthetic PMU types in the hwmon reserved range. Event loading opens the hwmon directory, parses regular filenames into type/number/item/alarm, groups files by type+number in a hashmap, reads labels, derives friendly names, and removes events lacking an `_input` file. Listing walks the hashmap and emits `pmu_event_info` with aliases, scale units, descriptions, extra item values, and config encodings. Config parsing resolves either direct `<type><num>` names or label-derived `<type>_<label>` names. Open creates fd entries for every requested cpu/thread slot; read `pread`s the input file and updates perf counts.

## State and persistence
State is per `struct hwmon_pmu`: sysfs directory path, perf PMU metadata, and a lazily populated hashmap of available sensor events. `pmu.sysfs_aliases_loaded` prevents repeated directory scans. Runtime event fds are stored in the evsel fd xyarray. Counts accumulate in `evsel->counts`; if `prev_raw_counts` exists, reads add the current raw sysfs value to previous values and increment enabled/running counts.

## Dependencies and integration points
The module depends on perf PMU/event parsing, hashmap, counts, evsel fd arrays, thread maps, sysfs helpers, low-level `io_dir`, and hwmon naming conventions documented by the kernel. It integrates with perf PMU discovery, `perf list`, parse-events alias checking, event opening, and stat/read paths.

## Risks
`parse_hwmon_filename` assumes sorted type/item string tables for `bsearch`; table changes must preserve lexical order. `evsel__hwmon_pmu_read` reads into `char buf[32]` then writes `buf[len] = '\0'`; if `pread` returns exactly 32, this is out of bounds. `hwmon_pmu__describe_items` appends with `snprintf(out_buf + len, out_buf_len - len, ...)` without guarding `len >= out_buf_len`, so long descriptions can underflow the remaining size. In `hwmon_pmu__new`, failure after `zalloc` calls `perf_pmu__delete(&hwm->pmu)` and may rely on initialization state. Event fds are duplicated per cpu/thread even though sensors are not CPU-specific. Sysfs labels and names are normalized but collisions are possible.

## Test signals
Tests should use fake sysfs hwmon trees for filename parsing, PMU discovery, label-derived names, events without input removal, alarm/item descriptions, direct and label alias config, scale/unit selection, fd open cleanup on partial failure, read count accumulation, and boundary cases for 32-byte sensor values and long descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c -->
