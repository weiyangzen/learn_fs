# sources/distributed-fs/ceph-client/include/trace/stages/stage3_trace_output.h

Purpose: Stage 3 defines macros used while generating human-readable trace output functions.

Important APIs/types/functions: Defines `__entry`, `TP_printk`, dynamic-data accessors (`__get_str`, `__get_dynamic_array`, relative variants, bitmask/cpumask/sockaddr accessors), symbolic printers (`__print_flags`, `__print_symbolic`, u64 variants), hex/array dump helpers, namespace time printers, and IRQ-context helpers.

Control flow: `trace_events.h` expands event `TP_printk` blocks under these definitions so each event class gets a generated print function.

State/persistence: No state is owned. It defines how raw event payloads are interpreted for text output.

Dependencies/integration: Relies on trace sequence APIs, trace print flag structs, raw event layout, and helper functions for arrays/time/buffers.

Risks: Accessor arithmetic must match dynamic data layout. Formatting helper changes are user-visible in tracefs output.

Test signals: Inspect trace text for events using dynamic strings, flags, arrays, cpumasks, sockaddrs, and namespace time values.
