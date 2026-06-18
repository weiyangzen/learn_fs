<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py
Purpose: Defines simple Python classes for grouping raw perf samples into generic and Intel PEBS event objects.

Important APIs/types/functions: Constants `EVTYPE_GENERIC`, `EVTYPE_PEBS`, `EVTYPE_PEBS_LL`, and `EVTYPE_IBS` identify event categories. `create_event()` selects `PebsEvent`, `PebsNHM`, or `PerfEvent` by raw buffer length. `PerfEvent` stores generic metadata. `PebsEvent` unpacks base PEBS register fields. `PebsNHM` unpacks Nehalem/Westmere load-latency fields.

Control flow: Consumers pass event metadata and `raw_buf`. The factory checks raw size, constructs the appropriate class, and constructors unpack fixed 64-bit fields with `struct.unpack` before calling base initialization.

State and persistence: Class counters track total created events by type. Each object stores raw buffer and decoded fields. No disk persistence.

Dependencies and integration points: Used by `event_analyzing_sample.py` to classify samples before SQLite insertion. Depends on Python `struct` and assumes x86 PEBS record layouts.

Risks: Raw-buffer-size detection is heuristic and architecture/layout-specific. Unexpected buffer lengths fall back to generic events. PEBS parsing assumes native data is little-endian 64-bit words in the expected order.

Test signals: Feeding known 144-byte and 176-byte raw buffers should produce `PebsEvent` and `PebsNHM` with decoded fields; `event_analyzing_sample.py` exercises this path during perf script replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py -->
