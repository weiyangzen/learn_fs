# sources/distributed-fs/ceph-client/tools/perf/util/data-convert-bt.c

## Purpose

`data-convert-bt.c` implements `perf data convert --to-ctf` using Babeltrace CTF writer APIs. It opens a perf session, maps perf sample and selected non-sample records into CTF event classes and streams, writes environment and clock metadata, and flushes per-CPU streams.

## Important APIs, Types, and Functions

Key types are `struct ctf_writer`, `struct ctf_stream`, `struct convert`, and `struct evsel_priv`. Public entry `bt_convert__perf2ctf()` configures the perf tool callbacks and drives conversion. Field creation and population are handled by `value_set*()`, `string_set_value()`, `add_generic_types()`, `add_generic_values()`, `add_tracepoint_types()`, `add_tracepoint_values()`, `add_bpf_output_types()`, and `add_callchain_output_values()`. Writer setup/teardown lives in `ctf_writer__init()`, `ctf_writer__setup_clock()`, `ctf_writer__setup_env()`, `setup_streams()`, and `ctf_writer__cleanup()`.

## Control Flow

Conversion initializes a `perf_data` reader, creates a `perf_session`, parses optional time ranges, initializes the CTF writer and common integer/string field types, registers event classes from the session's evsels, optionally registers comm/fork/exit/mmap non-sample classes, then processes ordered events. Sample callbacks skip samples outside requested time ranges, create a CTF event from the evsel-private class, add generic sample fields, tracepoint fields, callchain data, and BPF raw output, append to a CPU stream, and flush streams every `STREAM_FLUSH_COUNT` events or at the end.

## State and Persistence Behavior

Persistent output is a CTF trace directory at the requested path. Runtime state includes event counters, skipped counts, stream objects indexed by CPU, CTF field type objects, event-class pointers attached to `evsel->priv`, and optional time-range filters. Input state is read-only `perf.data`; the converter does not mutate captured records.

## Dependencies and Integration Points

The file depends on Babeltrace CTF writer/IR APIs, perf sessions/tools/evlists, libtraceevent for tracepoint metadata, perf time utilities, clock metadata, and perf config for `convert.queue-size`. It integrates with perf's ordered event processing, tracepoint format parsing, BPF output events, callchain resolution, and non-sample event processors.

## Risks and Edge Cases

Identifier collisions and CTF reserved words are handled by aliases, but duplicate names only allow `_dupl_1` through `_dupl_9`. Unsupported sample fields are explicitly omitted, including read, branch stack, user regs, and user stack. Dynamic tracepoint fields require correct offset/length interpretation. CPU values beyond stream capacity are forced to stream 0 after an error. Pipe-mode feature ordering requires delayed event class setup. Error paths must release Babeltrace references to avoid leaks.

## Test Signals

Tests should cover normal samples, tracepoint samples with common and dynamic fields, BPF output, callchains, `--all` non-sample export, pipe-mode feature events, time filtering, TOD clock conversion requiring clock metadata, queue-size config, high CPU ids, unprintable strings, and CTF readability by Babeltrace tools.
