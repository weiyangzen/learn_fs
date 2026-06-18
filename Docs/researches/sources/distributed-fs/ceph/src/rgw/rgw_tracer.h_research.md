# sources/distributed-fs/ceph/src/rgw/rgw_tracer.h

## Purpose
`rgw_tracer.h` declares RGW tracing tag constants, the global tracer, and a helper to recover span context from object attributes.

## Important APIs, Types, and Functions
Constants name common span attributes such as bucket, user, object, operation result, upload id, transaction id, and host id. `extern tracing::Tracer tracer` is the RGW tracer handle. `extract_span_context()` looks for `RGW_ATTR_TRACE` in an attrs map and decodes a `jspan_context`.

## Control Flow
Callers pass object attrs into `extract_span_context()`, which silently ignores missing or malformed trace attrs.

## State and Persistence Behavior
Trace context can be persisted as `RGW_ATTR_TRACE` in object metadata. The helper only decodes it into request-local state.

## Dependencies and Integration Points
Depends on Ceph `common/tracer.h`, RGW attrs, and tracing decode support. Used by object operations that continue distributed traces across stored metadata.

## Risks
Decode failures are swallowed, which keeps request paths robust but hides corrupt trace attrs. Constants are untyped string pointers.

## Test Signals
Cover valid trace attr decode, missing attr, corrupt bufferlist, and span tags appearing in traced RGW operations.
