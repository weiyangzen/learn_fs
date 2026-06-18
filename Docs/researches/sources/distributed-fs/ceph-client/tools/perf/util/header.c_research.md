<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/header.c

## Purpose
`header.c` implements perf.data header and feature-section serialization, deserialization, printing, and pipe-mode feature-event processing for perf. It is the compatibility layer between recorded perf files/streams and `perf_session`, `evlist`, `evsel`, `perf_env`, build-id, tracing, AUX trace, BPF, PMU, topology, cache, clock, compression, and scheduler-domain metadata.

## Important APIs, types, and functions
The public entry points are `perf_session__read_header`, `perf_session__write_header`, `perf_header__write_pipe`, `perf_session__inject_header`, `perf_session__data_offset`, `perf_header__process_sections`, `perf_header__fprintf_info`, `perf_event__process_feature`, `perf_event__process_attr`, `perf_event__process_event_update`, `perf_event__process_build_id`, `perf_file_header__read`, `is_perf_magic`, feature bit helpers, `do_write`, `write_padded`, `build_caches_for_cpu`, and weak architecture hooks `get_cpuid`, `get_cpuid_str`, and `strcmp_cpuid_str`. The central dispatch table is `feat_ops[HEADER_LAST_FEATURE]`, built with `FEAT_OPR`/`FEAT_OPN` entries mapping each `HEADER_*` feature to optional write, print, and process callbacks.

## Control flow
Write-side flow starts in `perf_session__write_header` or `perf_session__inject_header`, both entering `perf_session__do_write_header`. It lays out ID arrays, `perf_file_attr` records, data offsets, feature offsets, feature sections via `perf_header__adds_write`, then rewrites the fixed `perf_file_header` at offset zero. `do_write_feat` writes or copies a feature section and clears the feature bit if the write fails. Pipe mode writes a smaller `perf_pipe_file_header` and later processes feature records through `perf_event__process_feature`.

Read-side flow starts in `perf_session__read_header`. It first tries pipe format, then reads regular file headers with endian and ABI detection, constructs an `evlist`, reads every event attribute and ID, then calls `perf_header__process_sections` to visit feature sections in feature-bit order. Each feature process callback fills `header.env`, session auxtrace state, evlist event names/groups, tracing data, or build-id DSOs.

## State and persistence
Persistent on-disk state includes the fixed perf header, attribute table, ID arrays, data section, and variable feature sections. In-memory state is stored in `perf_header` (`needs_swap`, offsets, feature bitmap, `last_feat`, `perf_env`) and in owning `perf_session` structures. Many process callbacks allocate strings, topology arrays, PMU capability arrays, BPF metadata nodes, cache nodes, memory-node bitmaps, or CPU domain maps that become part of `perf_env`. Compatibility state includes legacy magic handling, legacy ABI size probing, feature-bit byte swapping, old build-id ABI quirks, old CPU topology layouts, and pipe-stream `last_feat` discovery.

## Dependencies and integration points
The file depends on perf core utilities (`evlist`, `evsel`, `session`, `data`, `tool`, `pmu`, `pmus`, `env`, `build-id`, `auxtrace`, `trace-event`, `bpf-event`, `clockid`, `cputopo`, `cacheline`) plus Linux/sysfs/procfs interfaces. It integrates with `/proc/cpuinfo`, `/proc/meminfo`, `/proc/schedstat`, `/sys/devices/system/*`, libtraceevent, libbpf, AUX trace indexing, build-id DSOs/machines, perf inject feature copying, and perf report header printing.

## Risks
This file parses untrusted perf.data input. Bounds checks exist for command line count, NUMA nodes, PMU mappings, group descriptions, cache entries, BPF payload sizes, PMU caps, scheduler domains, and feature section sizes, but regressions here can still become memory pressure, bad offsets, wrong byte swapping, leaks on partial parse, or corrupted `perf_env` state. Feature write failures silently clear feature bits, which preserves file creation but can hide metadata loss. Cross-endian BPF info/BTF is intentionally ignored. Several process paths return early after allocating nested structures without full cleanup on every failure path, so fuzz/error tests matter. Header layout and feature ordering are compatibility-sensitive and must remain stable.

## Test signals
Good test coverage includes perf record/report round trips, pipe-mode report, cross-endian perf.data files, legacy `PERFFILE`/ABI samples, perf inject with copied features, BPF/libbpf enabled and disabled builds, libtraceevent enabled and disabled builds, malformed feature-section fuzzing, huge-count rejection tests for every capped section, sysfs/procfs-missing tests, topology-heavy machines, hybrid/PMU capability cases, AUX trace sessions, and `perf report --header`/`--header-only` output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.c -->
