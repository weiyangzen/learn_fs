# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_printk.c

## Purpose
Tests `bpf_trace_printk()` output, including mutable rodata format text, UTF-8 format content, return values, and invalid format specifier failure.

## APIs, Types, and Functions
Entry point is `serial_test_trace_printk()`. Callback `trace_pipe_cb()` scans trace pipe lines for two expected messages. Uses lightweight skeleton `trace_printk.lskel.h`.

## Control Flow, State, and Persistence
The test opens the skeleton, checks and modifies the first byte of a rodata format string before load, loads and attaches, sleeps briefly for tracepoint execution, detaches, asserts BSS run counts and positive return values, asserts invalid specifier return is negative, and reads trace pipe to match printed message counts. State is transient in BSS counters and the kernel trace buffer.

## Dependencies and Integration
Depends on trace pipe helper `read_trace_pipe_iter`, tracepoint attachment in the lskel, and kernel trace buffer access.

## Risks and Test Signals
Risks include stale trace buffer data, tracefs access restrictions, timing around tracepoint trigger, and UTF-8 handling in terminals/logs. Signals are BSS counters, positive printk returns, negative invalid-spec return, and trace pipe matches equal to run counters.
