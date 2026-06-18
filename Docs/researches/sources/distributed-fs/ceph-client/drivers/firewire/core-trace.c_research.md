# sources/distributed-fs/ceph-client/drivers/firewire/core-trace.c

### Purpose
`core-trace.c` instantiates FireWire tracepoints. It defines `CREATE_TRACE_POINTS` before including `<trace/events/firewire.h>` so the trace event storage and metadata are emitted in the core module.

### Important APIs, Types, And Functions
The file includes packet and PHY header definition helpers used by trace event field decoders. When `TRACEPOINTS_ENABLED` is defined, it exports GPL tracepoint symbols for isochronous inbound single completions, inbound multiple completions, and outbound completions.

### Control Flow, State, And Persistence
There is no ordinary runtime control flow beyond tracepoint registration through the kernel tracing infrastructure at module load. The persistent effect is that all `trace_*` calls in the FireWire core resolve to concrete tracepoints.

### Dependencies, Integration Points, Risks, And Test Signals
This file must be built exactly once in `firewire-core-y`; otherwise tracepoints are either undefined or multiply defined. It integrates with tracing users, ISO completion providers, and packet serialization helpers. Risks are mostly build/linkage issues and trace event field drift when packet header definitions change. Test signals include successful core link, availability of FireWire trace events in tracefs, and external ISO drivers resolving exported tracepoint symbols when tracing is enabled.
