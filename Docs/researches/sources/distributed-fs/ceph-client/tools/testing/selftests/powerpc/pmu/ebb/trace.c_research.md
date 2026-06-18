# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.c

## Purpose
`trace.c` implements a small in-memory tracing facility for PMU EBB selftests. It records register/value pairs, counters, strings, indentation markers, and prints a decoded trace with source buffer locations for debugging event-based branch behavior.

## Important APIs, Types, and Functions
Public functions are `trace_buffer_allocate()`, `trace_log_reg()`, `trace_log_counter()`, `trace_log_string()`, `trace_log_indent()`, `trace_log_outdent()`, `trace_buffer_print()`, and `trace_print_location()`. Internal helpers perform bounds checks, linear allocation from the buffer tail, entry allocation, register-name decoding, and per-entry printing.

## Control Flow and State
Allocation creates a `struct trace_buffer` followed by an mmap-backed payload region and initializes `tb->tail` to the first entry slot. Each log call computes payload size, reserves a `struct trace_entry`, writes typed payload data, and advances the tail. Bounds failures set the buffer overflow flag and return errors. Printing walks entries from the beginning to the tail, adjusts indentation on indent/outdent entries, and prints decoded register or counter payloads.

## Dependencies and Integration Points
The code depends on `trace.h`, `utils.h` integer types, libc allocation/mmap APIs, and the EBB tests that call these trace helpers from instrumentation paths. It is a diagnostics layer rather than a kernel interface.

## Risks and Test Signals
Risks include payload-size mistakes, string length including the terminator, tail corruption, and silent truncation after overflow. Useful signals are deterministic trace dumps, clear overflow reporting, correct indentation nesting, and register names matching the PMU SPR values logged by EBB tests.
