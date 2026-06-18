# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.c

## Purpose

`cs-etm.c` is perf's CoreSight ETM/ETE auxtrace decoder integration. It reads CoreSight metadata and AUX trace records from `perf.data`, constructs OpenCSD decoder instances, resolves trace IDs to CPU metadata, tracks thread/exception-level context, and synthesizes perf instruction and branch samples from decoded ETM packets.

## Important APIs, Types, and Functions

The central state types are `struct cs_etm_auxtrace`, `struct cs_etm_queue`, and `struct cs_etm_traceid_queue`. `cs_etm__process_auxtrace_info_full()` installs perf auxtrace callbacks and prepares metadata, queues, synthesized event attributes, timestamp conversion, trace ID mapping, and decoders. Queue and trace-id helpers include `cs_etm__setup_queue()`, `cs_etm__insert_trace_id_node()`, `cs_etm__process_aux_output_hw_id()`, `cs_etm__create_queue_decoders()`, and `cs_etm__map_trace_ids_metadata()`. Decode and synthesis functions include `cs_etm__process_timestamped_queues()`, `cs_etm__process_timeless_queues()`, `cs_etm__decode_data_block()`, `cs_etm__process_traceid_queue()`, `cs_etm__synth_instruction_sample()`, and `cs_etm__synth_branch_sample()`.

## Control Flow

Perf enters through the auxtrace-info record, builds per-CPU/per-thread queues, peeks existing AUX and AUX_OUTPUT_HW_ID records, maps trace IDs, then creates one decoder per populated queue. During event processing, AUX records are queued or dumped; ITRACE_START and SWITCH records seed thread lookup state; AUX timestamps update fallback sample time. Flush dispatches either timestamped decoding, which orders queue/channel work through `auxtrace_heap`, or timeless decoding, which drains each queue directly. Decoded packets are classified as ranges, discontinuities, exceptions, or exception returns, then converted into branch/instruction samples with appropriate flags.

## State and Persistence Behavior

Persistent input state is `perf.data` metadata, AUX trace bytes, AUX_OUTPUT_HW_ID records, event attributes, and time conversion fields. Runtime state is held in trace-id maps, packet ring buffers, branch stacks, current/previous packets, current thread references, latest kernel timestamp, and decoder offsets. The file mutates in-memory metadata trace ID fields when hardware ID records override legacy IDs, but it does not write persistent data except by optionally injecting synthesized events through the perf session pipeline.

## Dependencies and Integration Points

This file depends on OpenCSD via `cs-etm-decoder`, perf auxtrace queues/heaps, ordered events, perf sessions, maps/DSOs/symbols, thread-stack and branch sample infrastructure, CoreSight PMU metadata from Linux headers, and time conversion helpers. It integrates with `perf report`, `perf inject`, `perf script`, synthesized branch/instruction events, CoreSight raw dump mode, and DSO memory reads for instruction bytes.

## Risks and Edge Cases

Trace ID mapping is fragile when hardware IDs overlap, sink IDs change, or old metadata-only files are decoded. Timestamp handling has multiple modes: virtual timestamps, kernel timestamp fallback, user-forced timestamp use, and timeless decoding. Per-thread mode collapses trace IDs to `CS_ETM_PER_THREAD_TRACEID` and cannot support overlapping IDs. Missing DSO or kernel image data prevents instruction fetches and degrades decoding. Mixed formatted/unformatted trace in one queue is rejected. Guest/host EL mapping is intentionally approximate and supports only limited guest distinction.

## Test Signals

Useful tests include decoding old metadata-only files and newer AUX_OUTPUT_HW_ID files, per-CPU and per-thread trace captures, formatted and raw CoreSight buffers, timestamped and timeless traces, branch-only and instruction-period synthesis, missing DSO/kcore warning paths, snapshot overwrite AUX fragments, SVC/interrupt exception flag classification, and `dump_trace` raw packet output. Regression signals are stable synthesized sample counts, correct CPU/TID assignment, no trace ID mismatch errors, and ordered-event processing without stale packet samples.
