# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.h

## Purpose
This header declares the opaque display snapshot diagnostic API.

## Important APIs, Types, and Functions
It forward-declares `struct intel_display_snapshot`, `struct intel_display`, and `struct drm_printer`, then declares `intel_display_snapshot_capture()`, `intel_display_snapshot_print()`, and `intel_display_snapshot_free()`.

## Control Flow
The header has no logic. The API lifecycle is capture, optional print, then free. All functions are expected to tolerate null where implemented for print/free.

## State and Persistence Behavior
The snapshot type is opaque to callers, preserving ownership and layout in the C file. Callers own the returned pointer and must free it.

## Dependencies and Integration Points
The header is consumed by diagnostic and error capture code that should not depend on the detailed snapshot layout.

## Risks
Because the object is opaque, misuse is mainly lifecycle related: leaking snapshots, printing after display teardown, or failing to handle capture returning null.

## Test Signals
Build coverage, error-state dump tests, and memory leak checking around capture/free are the primary signals.
