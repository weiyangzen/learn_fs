# sources/distributed-fs/ceph-client/tools/include/linux/ftrace.h

## Purpose

This is an empty compatibility header for kernel code that includes ftrace interfaces while being built in the tools environment.

## APIs, State, and Dependencies

Only an include guard is present. There are no tracing APIs or state.

## Risks and Test Signals

Code that actually needs ftrace instrumentation declarations will need a fuller shim. Compile tests validate that current tools users only require the header path.
