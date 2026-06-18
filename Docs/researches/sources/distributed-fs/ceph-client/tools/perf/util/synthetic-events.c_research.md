<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c

## Purpose

`synthetic-events.c` creates perf events that did not come directly from the kernel ring buffer but are needed to make perf data self-describing. It synthesizes task, mmap, namespace, cgroup, module, kernel-map, thread-map, CPU-map, stat, sample, id-index, event-update, build-id, tracing-data, header-feature, pipe, and schedstat records.

## Important APIs, Types, and Functions

Core helpers include `perf_tool__process_synth_event()`, `perf_event__synthesize_comm()`, `perf_event__synthesize_namespaces()`, `perf_event__synthesize_mmap_events()`, `perf_event__synthesize_modules()`, `perf_event__synthesize_thread_map()`, `perf_event__synthesize_threads()`, `perf_event__synthesize_kernel_mmap()`, `perf_event__synthesize_thread_map2()`, `perf_event__synthesize_cpu_map()`, `perf_event__synthesize_stat_config()`, `perf_event__synthesize_stat()`, `perf_event__synthesize_stat_round()`, `perf_event__sample_event_size()`, `perf_event__synthesize_sample()`, `perf_event__synthesize_id_sample()`, `perf_event__synthesize_id_index()`, event update synthesizers for unit/scale/name/cpus, `perf_event__synthesize_attrs()`, `perf_event__synthesize_extra_attr()`, `perf_event__synthesize_attr()`, `perf_event__synthesize_build_id()`, `perf_event__synthesize_mmap2_build_id()`, `perf_event__synthesize_stat_events()`, `perf_event__synthesize_features()`, `perf_event__synthesize_for_pipe()`, `parse_synth_opt()`, and `perf_event__synthesize_schedstat()`.

Important internal flows parse `/proc/<pid>/status`, `/proc/<pid>/task/<tid>/maps`, namespace symlinks, cgroup trees, kernel module maps, `/proc`, perf evlists, sample layouts, header features, and `/proc/schedstat`.

## Control Flow and Data Flow

Task synthesis reads process/thread status to build COMM, FORK, NAMESPACES, and optional MMAP2 records. Full process scans iterate `/proc` and per-process task directories, optionally using worker pthreads. Mmap synthesis parses each maps line with `read_proc_maps_line()`, filters executable mappings unless data maps are requested, marks hugepage mappings as anonymous hugepage entries, optionally attaches build IDs, aligns variable filename data, and passes records through a caller-supplied handler.

Kernel and module synthesis walk `struct machine` maps to emit kernel or module MMAP/MMAP2 records. Metadata synthesis converts evsels into ATTR and EVENT_UPDATE records, evlists into ID_INDEX records, CPU maps into compact range/list/mask encodings, thread maps into THREAD_MAP records, and stat counts into STAT/STAT_ROUND/STAT_CONFIG records. Sample synthesis writes fields in the exact order required by `sample_type` and `read_format`, including cross-endian packing of pid/tid and cpu/reserved pairs. Feature and pipe synthesis serialize perf header feature blocks and optional trace data.

Schedstat synthesis reads version 15, 16, or 17 `/proc/schedstat`, creates CPU and domain records using included version field lists, filters requested CPUs, and emits records with a shared timestamp.

## State and Persistence Behavior

Most functions allocate temporary `union perf_event` buffers, fill them, invoke `process`, and free the buffers. The persistent effect is on the perf data stream or session state handled by the callback. The file-global `proc_map_timeout` controls maps parsing timeout. Some flows update DSO build IDs when mmap build-id synthesis discovers them. Thread synthesis can run concurrently across pthreads, so the callback and shared machine/session structures must tolerate that usage.

## Dependencies and Integration Points

The file depends on perf event record definitions, `perf_tool`, `machine`, `map`, `dso`, `evlist`, `evsel`, `session`, `stat`, `target`, `symbol_conf`, cgroup helpers, namespace helpers, build-id readers from `symbol.h`, `/proc`, sysfs, cgroupfs, trace-event support, and CPU/thread map libraries. It is used by `perf record`, `perf inject`, pipe output, stat recording, and report-side reconstruction.

## Risks and Edge Cases

The code races with process exit, thread exit, namespace changes, map changes, cgroup changes, and module changes; many failures are intentionally ignored or downgraded. Variable-length event sizes must stay 64-bit aligned and within header size limits. `perf_event__synthesize_stat_events()` overwrites `err` after extra attr synthesis, so failures from extra attrs may be lost before thread-map synthesis. `perf_event__synthesize_mmap2_build_id()` appears to assign `ev.build_id.size` instead of `ev.mmap2.build_id_size` when clamping oversized build IDs, which is worth regression testing. Sample synthesis assumes non-null optional structures when their sample bits are set. Parallel thread synthesis can interleave callback execution.

## Test Signals

Tests should cover COMM/FORK/MMAP generation for live and exiting tasks, namespace records, data mmap filtering, hugepage mapping rewriting, build-id attachment, proc map timeout marking, cgroup tree synthesis, module mmap records, kernel mmap records with and without build-id mmap2, thread scans with one and many worker threads, CPU map range/list/mask encodings, stat config and stat events, sample size versus synthesized sample bytes for every `PERF_SAMPLE_*` bit, id-index chunking over `UINT16_MAX` limits, pipe feature serialization, synth option parsing, and schedstat versions 15/16/17.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c -->
