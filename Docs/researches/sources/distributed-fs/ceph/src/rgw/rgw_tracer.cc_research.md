# sources/distributed-fs/ceph/src/rgw/rgw_tracer.cc

## Purpose
`rgw_tracer.cc` defines the global RGW tracing object declared in the header.

## Important APIs, Types, and Functions
It instantiates `tracing::rgw::tracer`.

## Control Flow
There is no runtime control flow beyond static/global initialization.

## State and Persistence Behavior
The global tracer is process state used by tracing instrumentation; no direct persistence occurs.

## Dependencies and Integration Points
Depends on `rgw_tracer.h` and Ceph tracing infrastructure. RGW request paths import the global tracer to create spans.

## Risks
Global initialization order can matter if tracing code uses the object before normal startup. The file is intentionally minimal.

## Test Signals
Link tests should ensure exactly one tracer definition exists and tracing-enabled builds resolve it.
