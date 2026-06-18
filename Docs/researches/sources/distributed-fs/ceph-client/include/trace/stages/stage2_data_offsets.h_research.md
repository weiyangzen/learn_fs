# sources/distributed-fs/ceph-client/include/trace/stages/stage2_data_offsets.h

Purpose: Stage 2 of trace generation: builds offset metadata for dynamic fields in each event.

Important APIs/types/functions: Redefines field macros so only dynamic arrays, strings, bitmasks, cpumasks, sockaddrs, and relative variants generate `u32` offset members in `struct trace_event_data_offsets_<call>`.

Control flow: The generator expands each trace event under these definitions to compute which variable-length data offsets are needed. Static fields expand away.

State/persistence: Produces compile-time offset structs used by generated callbacks; no runtime storage is owned here.

Dependencies/integration: Consumed by stage 5 offset calculation and stage 6 event callback population.

Risks: Offset struct mismatches cause callback code to write variable data to wrong positions, corrupting trace records.

Test signals: Build events with multiple dynamic and relative fields and validate trace output lengths and payload strings/arrays.
