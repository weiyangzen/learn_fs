# sources/distributed-fs/ceph-client/tools/perf/util/mem-events.c

## Purpose

`mem-events.c` implements perf memory-event selection and memory data-source formatting/statistics. It builds `perf record -e` arguments for load/store memory sampling PMUs, lists and parses memory event tags, formats `perf_mem_data_src` fields for scripts, and decodes c2c and histogram memory statistics.

## Important APIs, Types, and Functions

Global defaults are `perf_mem_events__loads_ldlat = 30`, `perf_mem_events[]`, and `perf_mem_record[]`. PMU/event APIs include `perf_pmu__mem_events_ptr()`, `perf_mem_events_find_pmu()`, `perf_pmu__mem_events_num_mem_pmus()`, `perf_pmu__mem_events_parse()`, `perf_pmu__mem_events_init()`, `perf_pmu__mem_events_list()`, `perf_mem_events__record_args()`, and `is_mem_loads_aux_event()`. Formatting APIs include `perf_mem__tlb_scnprintf()`, `perf_mem__lvl_scnprintf()`, `perf_mem__snp_scnprintf()`, `perf_mem__lck_scnprintf()`, `perf_mem__blk_scnprintf()`, and `perf_script__meminfo_scnprintf()`. Stats APIs include `c2c_decode_stats()`, `c2c_add_stats()`, `mem_stat_index()`, and `mem_stat_name()`.

## Control Flow

PMU scanning walks all PMUs with `perf_pmus__scan()` and selects those with `mem_events`. Parsing duplicates the user's comma-separated string, marks matching `perf_mem_record` slots by tag substring, and reports an error if none match. Initialization checks sysfs for each PMU event file and marks supported entries. Record-arg generation allocates one storage buffer sized by PMU count and event count, emits `-e <event>` pairs for requested supported events, handles load-latency and auxiliary event name templates, and warns when memory PMUs cover only a CPU subset. Formatting functions decode bitfields into fixed strings for TLB, level, snoop, lock, and block dimensions. `c2c_decode_stats()` classifies one sample into load/store, cache/DRAM/HITM/peer/blocking/no-map counters and returns errors for missing addresses or unparsable data. `mem_stat_index()` maps `perf_mem_data_src` fields into compact histogram bucket indexes.

## State and Persistence Behavior

Global `perf_mem_record[]` persists selected memory event kinds for command construction. Each PMU's `mem_events[j].supported` bit is updated from sysfs. `perf_mem_events__record_args()` returns heap storage through `event_name_storage_out`; argv entries point inside that buffer and require caller lifetime management. Stats functions mutate caller-owned `c2c_stats`.

## Dependencies and Integration Points

This file depends on sysfs mount discovery, PMU and PMU list handling, CPU maps, evsel, debug output, `mem_info`, map-symbol data, Linux perf memory data-source bitfields, and c2c/hist consumers. It integrates with `perf mem`, `perf c2c`, `perf script`, and memory-focused reporting.

## Risks and Edge Cases

Tag parsing uses `strstr(e->tag, tok)`, so partial tokens can match more than expected. `perf_pmu__mem_events_init()` returns `-ENOENT` if any scanned memory PMU fails initialization, which can be strict on heterogeneous systems. Event-name storage sizing assumes 128 bytes per event. Several formatters subtract one from `sz` and then use `strcat()`, so callers must pass nonzero buffers. `perf_script__meminfo_scnprintf()` passes `sz` rather than `sz - i` to the level formatter, which deserves attention in boundary tests. c2c classification relies on architecture-populated data-source bits and can mark samples as no-address or no-map.

## Test Signals

Tests should cover PMU scans with zero, one, and multiple memory PMUs; load, store, and load-store event templates; Intel auxiliary load events; unsupported sysfs events; CPU subset warnings; parsing exact and partial tags; formatting every memory data-source category; small output buffers; c2c load/store/HITM/peer/remote/blocked/no-address/no-map cases; and histogram bucket mappings for op, cache, memory, snoop, and DTLB.
