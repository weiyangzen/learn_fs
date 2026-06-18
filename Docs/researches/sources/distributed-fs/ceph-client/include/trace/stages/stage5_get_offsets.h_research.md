# sources/distributed-fs/ceph-client/include/trace/stages/stage5_get_offsets.h

Purpose: Stage 5 computes runtime offsets and total payload size for variable-length trace event data.

Important APIs/types/functions: Defines `__data_offsets`, validates static field macros with dummy structs, and implements dynamic sizing for `__dynamic_array`, `__string`, `__string_len`, `__vstring`, relative dynamic arrays/strings, bitmasks, cpumasks, and sockaddrs. It also defines bitmask sizing helpers.

Control flow: Generated `trace_event_get_offsets_<call>()` functions expand event field macros to increment `__data_size` and fill `__data_offsets` members before event reservation.

State/persistence: It computes per-event-call transient offsets; no persistent state beyond generated code.

Dependencies/integration: Used by stage 6 callbacks before writing dynamic payloads into `trace_event_buffer`.

Risks: Off-by-one string lengths, alignment mistakes, or relative-location calculations corrupt trace records and readers.

Test signals: Trace events with multiple variable fields and verify payload lengths, string termination, and relative offsets under ftrace/perf.
