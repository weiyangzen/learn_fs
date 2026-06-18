# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.h

## Purpose
`trace.h` defines the EBB trace buffer ABI used by `trace.c` and PMU EBB tests. It describes the entry types and the buffer/entry layouts consumed by trace logging and printing.

## Important APIs, Types, and Functions
It defines `TRACE_TYPE_REG`, `TRACE_TYPE_COUNTER`, `TRACE_TYPE_STRING`, `TRACE_TYPE_INDENT`, and `TRACE_TYPE_OUTDENT`, plus `struct trace_entry` and `struct trace_buffer`. It declares all trace allocation, logging, printing, and location-reporting functions.

## Control Flow and State
There is no control flow in the header. The persistent state contract is that a trace buffer has a byte size, an overflow flag, and a tail pointer, while each entry stores a type and payload size followed by variable payload bytes.

## Dependencies and Integration Points
It includes `utils.h` for `u64` and is included by EBB tracing code. Any producer or printer must agree on entry type values and payload packing.

## Risks and Test Signals
Risks are ABI drift between log producers and `trace_buffer_print()`, unaligned payload assumptions, and callers passing unallocated buffers. Test signals are successful compilation of EBB tracing clients and readable traces for register, counter, string, indent, and outdent entries.
