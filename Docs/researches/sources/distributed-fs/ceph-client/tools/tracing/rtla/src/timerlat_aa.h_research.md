# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.h

## Purpose
`timerlat_aa.h` declares the timerlat auto-analysis interface.

## Important APIs, Types, and Functions
It exposes `timerlat_aa_init(struct osnoise_tool *tool, int dump_task, enum stack_format stack_format)`, `timerlat_aa_destroy()`, and `timerlat_auto_analysis(int irq_thresh, int thread_thresh)`.

## Control Flow and Integration
`timerlat.c` calls init while enabling timerlat, destroy during cleanup, and auto-analysis after a threshold stop. The implementation uses the passed `osnoise_tool` trace instance to register events and inspect collected trace data.

## State and Persistence
The header itself owns no state; the implementation creates a singleton context and per-CPU analysis data.

## Dependencies and Integration Points
It relies on `struct osnoise_tool` and `enum stack_format` being available through including translation units, normally via `timerlat.h`/`common.h`.

## Risks and Edge Cases
Because this header does not include the defining headers directly, include order matters. API users must pass thresholds in microseconds as expected by `timerlat_auto_analysis()`, which scales them internally.

## Test Signals
Compile consumers with strict include ordering and run timerlat with AA enabled/disabled and multiple stack formats.
