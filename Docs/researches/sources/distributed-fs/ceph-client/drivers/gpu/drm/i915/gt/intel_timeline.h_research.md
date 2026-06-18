# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.h

## Purpose
`intel_timeline.h` declares the timeline API and inline sync/ref helpers for i915 request ordering.

## Important APIs, Types, And Functions
It declares creation, get/put, pin/unpin, enter/exit, seqno allocation, HWSP read, reset, GT init/fini, and timeline dump functions. Inline helpers wrap krefs and `i915_syncmap` operations and test whether a request is last in a timeline.

## Control Flow
Callers create or acquire timelines, pin before request construction, enter while adding requests, allocate seqnos, exit when construction/activity is done, and unpin when no longer needed. Sync helpers record and compare latest waited fence seqnos by context.

## State, Persistence, And Dependencies
The header has no state itself; it exposes `struct intel_timeline` from `intel_timeline_types.h`. Dependencies include lockdep, active tracking, list utilities, syncmaps, and request/GT forward declarations.

## Integration Points
Context code, engine submission, request dependency emission, debug/error reporting, and selftests include this API.

## Risks
The API assumes callers hold the right timeline mutex around enter/exit and request-list operations. `intel_timeline_get()`/`put()` and pin/unpin lifetimes are independent and easy to confuse.

## Test Signals
Compile-time selftest declarations, lockdep, request ordering tests, syncmap dependency tests, and timeline refcount tests are key signals.
