# sources/distributed-fs/ceph/src/osd/osd_tracer.cc

## Purpose

`osd_tracer.cc` defines the global OSD tracing object declared in `osd_tracer.h`. It provides storage for `tracing::osd::tracer`, giving OSD code a single namespace-scoped tracing hook.

## Important APIs and Functions

The only symbol defined is `tracing::Tracer tracer` inside namespace `tracing::osd`. There are no functions or methods in this file.

## Control Flow

There is no runtime control flow beyond static/global object construction and destruction according to C++ initialization rules. Any actual tracing behavior is implemented by `common/tracer.h` and call sites that use this global.

## State and Persistence Behavior

The tracer object is process-local runtime instrumentation state. This file does not persist trace data itself; exporters or sinks configured by the common tracer infrastructure determine whether trace spans are emitted externally.

## Dependencies and Integration Points

The implementation includes `osd_tracer.h`, which includes `common/tracer.h`. Its integration point is any OSD code that references `tracing::osd::tracer` for span creation or tracing context.

## Risks and Test Signals

Risks are mostly link-time and initialization related: missing the single definition would cause unresolved externals, while defining it in multiple places would violate the one-definition rule. Test signals include successful OSD linkage with tracing enabled and smoke tests that create OSD tracing spans.
