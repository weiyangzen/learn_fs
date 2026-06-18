# sources/distributed-fs/ceph-client/tools/perf/scripts/python/powerpc-hcalls.py

Purpose: `powerpc-hcalls.py` reports PowerPC hypervisor call latency statistics from `powerpc:hcall_entry` and `powerpc:hcall_exit` tracepoints.

Important APIs and state: `hcall_table` maps opcodes to names, `d_enter` tracks in-flight entry timestamps by CPU and opcode, and `output` stores total time, count, min, and max per opcode. Perf callbacks are `powerpc__hcall_entry`, `powerpc__hcall_exit`, and `trace_end`.

Control flow: entry events store `nsecs(sec, nsec)` under the event CPU and opcode. Exit events look for a matching entry on the same CPU/opcode, compute elapsed nanoseconds, update aggregate counters, and delete the in-flight entry. `trace_end` prints a fixed-width table with count, min, max, and average nanoseconds.

State and persistence: state is in memory only and is keyed by CPU, so nested or overlapping calls with the same opcode on one CPU would overwrite the prior entry. There is no file persistence.

Dependencies, integration, risks, and tests: it depends on perf Python `Core`/`Util`, PowerPC tracepoint availability, and stable opcode values. Risks include unmatched exits after dropped events, overwritten nested entries, unordered output, and integer opcode printing for unknown hcalls. Test signals are paired hcall traces producing nonzero aggregate rows with plausible latency ranges.
