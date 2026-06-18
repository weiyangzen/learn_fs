# sources/distributed-fs/ceph-client/tools/perf/util/perf_event_attr_fprintf.c

## Purpose
This file renders a `struct perf_event_attr` into human readable fields for perf diagnostics. It converts numeric `type`, `config`, `sample_type`, branch sample type, and read format values into symbolic names where possible, falling back to decimal or hex encodings for unknown values.

## Important APIs, Types, and Functions
The exported API is `perf_event_attr__fprintf(FILE *fp, struct perf_event_attr *attr, attr__fprintf_f attr__fprintf, void *priv)`. Internal helpers include `__p_bits`, `__p_sample_type`, `__p_branch_sample_type`, `__p_read_format`, and the `stringify_perf_*` family. `__p_config_id` dispatches config formatting by `attr->type`; it can use `tracepoint_id_to_name()` and `perf_pmu__name_from_config()`.

## Control Flow
`perf_event_attr__fprintf` first resolves the PMU by `attr->type`, with a second pass for hardware and cache events that encode an extended PMU type in `attr->config`. It then walks each attr field through `PRINT_ATTRn` and `PRINT_ATTRf` macros. Required fields such as `type` and `config` are always printed, while most booleans and optional values are emitted only when nonzero.

## State and Persistence
The file has no persistent state. It consults the global PMU registry through `perf_pmus__find_by_type()` and may allocate a transient tracepoint name that is freed immediately.

## Dependencies and Integration Points
It depends on Linux perf ABI constants, `evsel_fprintf` callback formatting, PMU lookup/name decoding, and trace-event lookup. It is integrated with verbose perf output paths that need deterministic attr dumps.

## Risks
Bit-name tables must track kernel ABI additions or newer fields print as empty numeric masks. `__p_bits` advances the output pointer but keeps the original size argument, so it depends on `scnprintf` behavior and bounded fixed buffers. PMU name resolution can trigger lazy PMU discovery and may produce different strings on heterogeneous systems.

## Test Signals
Useful tests compare attr dump output for hardware, software, tracepoint, cache, raw, and extended-type events. Regression signals include missing names for new sample bits, tracepoint config leaks, and invalid PMU fallback strings.
