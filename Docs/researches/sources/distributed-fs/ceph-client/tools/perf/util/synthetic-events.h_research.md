<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h

## Purpose

`synthetic-events.h` declares the synthetic perf event API. It defines which synthetic event groups can be requested and exposes constructors for task, mmap, metadata, stat, sample, build-id, tracing, BPF, pipe, and schedstat records.

## Important APIs, Types, and Functions

`enum perf_record_synth` defines `PERF_SYNTH_TASK`, `PERF_SYNTH_MMAP`, `PERF_SYNTH_CGROUP`, and `PERF_SYNTH_ALL`. `perf_event__handler_t` is the callback signature used by almost every synthesizer. The header forward-declares the perf model types used by the API, including `perf_tool`, `machine`, `evlist`, `evsel`, `perf_sample`, `perf_session`, `perf_stat_config`, `target`, CPU/thread maps, and auxtrace/BPF support types.

The declarations include attribute/event-update synthesis, build-id and mmap2-build-id synthesis, CPU/thread map synthesis, kernel/module/task/mmap/namespace/cgroup synthesis, sample and id-sample synthesis, id-index synthesis, stat synthesis, tracing-data synthesis, feature/pipe synthesis, machine thread synthesis wrappers, BPF event synthesis, and schedstat synthesis. When libbpf support is unavailable, `perf_event__synthesize_bpf_events()` is an inline no-op.

## Control Flow and Data Flow

Callers pass a `perf_tool`, machine/session/evlist context, and a `perf_event__handler_t` callback. Each implementation fills one or more `union perf_event` records and hands them to the callback, optionally with a `perf_sample`. `parse_synth_opt()` converts user strings into `PERF_SYNTH_*` masks.

## State and Persistence Behavior

The header itself stores no state, but it exposes APIs that write synthetic records to a perf stream, mutate DSO build IDs, and read process/system state. The inline BPF fallback preserves behavior for builds without libbpf by making BPF metadata synthesis a successful no-op.

## Dependencies and Integration Points

It depends on Linux/perf types, `pid_t`, `bool`, and perf CPU map declarations. It is included by record, inject, report, stat, schedstat, BPF, auxtrace, and session code that needs self-describing perf data.

## Risks and Edge Cases

Callback semantics are central: some callers pass `NULL` tool or machine pointers for metadata records, so callbacks must handle the combinations used by each synthesizer. Feature availability varies by build flags, especially libbpf and libtraceevent. The enum mask must remain consistent with `parse_synth_opt()` and user-facing synth options.

## Test Signals

Compile tests should cover libbpf and non-libbpf builds. API tests should verify `parse_synth_opt()` masks, callback invocation contracts, and linkage for each declared synthesizer. Integration tests should compare generated records against perf data consumers for pipe, stat, and task/mmap workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h -->
