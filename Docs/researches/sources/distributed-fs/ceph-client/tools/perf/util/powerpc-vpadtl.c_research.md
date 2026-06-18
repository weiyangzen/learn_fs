# sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.c

## Purpose
This file decodes PowerPC VPA Dispatch Trace Log auxtrace data and turns it into synthesized perf samples that can be interleaved with normal ordered events.

## Important APIs, Types, and Functions
The exported entry point is `powerpc_vpadtl_process_auxtrace_info`. Internal state types are `struct powerpc_vpadtl` and `struct powerpc_vpadtl_queue`. Key helpers include `powerpc_vpadtl_decode`, `powerpc_vpadtl_decode_all`, `powerpc_vpadtl_timestamp`, `powerpc_vpadtl_sample`, `powerpc_vpadtl_process_queues`, queue setup/update functions, auxtrace callbacks, and `powerpc_vpadtl_synth_events`.

## Control Flow
Auxtrace info allocates decoder state, initializes queues, installs auxtrace callbacks, records PMU type, optionally prints dump info, synthesizes a `vpa-dtl` event attr, and processes indexed auxtrace queues. Queue setup reads the first buffer to capture boot timebase and frequency, computes queue timestamps, and inserts queues into an auxtrace heap. During ordered event processing, queues with timestamps earlier than the next perf sample are decoded and delivered as synthesized samples.

## State and Persistence
State is attached to `session->auxtrace`, with per-queue buffer pointers, timestamps, boot timebase, frequency, packet offsets, CPU numbers, and heap membership. No persistent files are written.

## Dependencies and Integration Points
It depends on perf session, auxtrace queues/heaps, perf data file access, evlist/evsel IDs, sample delivery, colorized dump output, and PowerPC DTL entry layout from included platform headers.

## Risks
Timestamp conversion uses floating-point division and assumes valid boot timebase/frequency records. Buffer sizes are rounded down to entry boundaries. Ordered-events mode is required. Raw sample sizing uses `sizeof(record)` where `record` is a pointer, which is a notable correctness risk if downstream expects the full entry size.

## Test Signals
Tests should feed synthetic auxtrace buffers containing boot records and DTL entries, verify timestamp ordering, heap interleaving, synthesized event IDs/names, dump mode output, malformed buffer handling, and cleanup paths.
