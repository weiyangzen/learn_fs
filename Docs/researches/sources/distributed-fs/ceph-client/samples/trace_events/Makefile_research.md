# sources/distributed-fs/ceph-client/samples/trace_events/Makefile

## Purpose

This Kbuild file builds trace event sample modules and configures include paths so trace headers outside `include/trace/events` can be found.

## Important APIs, Types, and Functions

It sets `CFLAGS_trace-events-sample.o := -I$(src)` and `CFLAGS_trace_custom_sched.o := -I$(src)`, then maps `CONFIG_SAMPLE_TRACE_EVENTS` and `CONFIG_SAMPLE_TRACE_CUSTOM_EVENTS` to their objects.

## Control Flow

Kbuild applies object-specific CFLAGS before compiling the files that define tracepoints or custom events.

## State and Persistence Behavior

No runtime state; it controls build configuration.

## Dependencies and Integration Points

It integrates with the tracepoint code-generation mechanism that includes headers via `define_trace.h` and `define_custom_trace.h`.

## Risks and Edge Cases

Removing `-I$(src)` can make generated trace includes fail. Each trace header must have exactly one C file that creates the tracepoints.

## Test Signals

Enable both configs and verify both modules build.
