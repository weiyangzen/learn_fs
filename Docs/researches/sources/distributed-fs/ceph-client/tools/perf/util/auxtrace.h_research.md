# sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.h

Purpose: defines perf's public AUX trace data structures, callback interfaces, option structures, enums, inline head/tail helpers, and declarations for the implementation in `auxtrace.c`.

Important APIs and types: `enum auxtrace_type` enumerates supported trace producers. `struct itrace_synth_opts` is the central decoded `--itrace` option state. `struct auxtrace` is the decoder callback vtable installed in `perf_session`. `struct auxtrace_buffer`, `auxtrace_queue`, `auxtrace_queues`, and `auxtrace_heap` describe queued trace storage and time ordering. `struct auxtrace_record` is the recording-side callback vtable. `struct addr_filter` and `addr_filters` model address filter specifications before/after resolution.

Control flow: inline `auxtrace_mmap__read_head()` and `auxtrace_mmap__write_tail()` enforce memory ordering around AUX ring buffer producer/consumer pointers. Other declarations route recording setup, sample/event queueing, decoder flushing, error synthesis, cache use, and filter parsing to `auxtrace.c`.

State and persistence: the header defines serialized `auxtrace_index_entry` format and in-memory buffer metadata that points either into perf.data, mmaped file regions, one-mmap memory, or copied pipe data. `itrace_synth_opts` persists user decode choices across the session.

Dependencies and integration points: includes Linux perf event ABI, barriers, cpumap, list and type conventions. It is included by hardware-specific decoders, perf record, perf report/script, and utility code that needs AUX data or instruction-trace options.

Risks: structure fields are heavily shared across perf subsystems; changing them has broad compile and behavior impact. The option struct has many booleans with overlapping meanings, so initialization defaults must be explicit. Head/tail memory barriers are correctness-critical for lockless communication with the kernel.

Test signals: build coverage across all auxtrace producers, static assertions or ABI review for serialized structures, and runtime tests for option parsing and mmap ring-buffer consumption.
