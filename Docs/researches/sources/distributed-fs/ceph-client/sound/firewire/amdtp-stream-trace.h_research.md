# sources/distributed-fs/ceph-client/sound/firewire/amdtp-stream-trace.h

Purpose: defines the Linux tracepoint used to inspect AMDTP packet timing, CIP headers, payload sizes, data block counts, counters, packet indexes, and IRQ context.

Important APIs, types, and functions: `TRACE_EVENT(amdtp_packet, ...)` accepts an `amdtp_stream`, cycle count, optional CIP header, payload length, data block count, data block counter, packet index, descriptor index, and current cycle time. The trace entry records source/destination node IDs, channel, cycle time split into second/cycle, dynamic CIP header bytes, payload quadlets, and whether execution is in softirq.

Control flow: `amdtp-stream.c` defines `CREATE_TRACE_POINTS` and includes this header. Packet build/parse paths call `trace_amdtp_packet()` when tracing is enabled, providing either generated IT CIP headers or parsed IR headers. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point `define_trace.h` back to this local header.

State and persistence: trace data is transient in the kernel tracing subsystem. No driver state is changed by the tracepoint.

Dependencies and integration: depends on Linux tracepoint infrastructure and fields in `struct amdtp_stream`, including `context`, `direction`, and `unit`. The Makefile adds `-I$(src)` so `define_trace.h` can find the header.

Risks: tracepoint field extraction assumes `s->context` is valid and has a channel when called. Dynamic array length is zero when no CIP header is present, so print consumers must handle empty arrays. The assignment line for `data_block_counter` uses a comma expression style, which compiles but is visually easy to miss. Test signals include enabling/disabling the tracepoint, packets with and without CIP headers, in/out stream source/destination reversal, softirq flag correctness, and trace build under module and built-in configurations.
