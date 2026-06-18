# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf_types.h

## Purpose

`xe_guc_buf_types.h` defines opaque public structs for the GuC buffer cache and individual buffer references.

## Important APIs, Types, and Functions

- `struct xe_guc_buf_cache` contains the internal `struct xe_sa_manager *sam`.
- `struct xe_guc_buf` contains the internal `struct drm_suballoc *sa`.

## Control Flow

There is no executable flow. The types are manipulated only through `xe_guc_buf.h`/`.c` helpers.

## State and Persistence Behavior

The cache manager persists for the GuC lifetime or until device-managed cleanup. Buffer references are transient suballocations and must be released. The fields are marked private by comment but remain visible to C callers.

## Dependencies and Integration Points

It forward-declares DRM suballocation and Xe suballocation manager types, minimizing dependencies for headers that only need buffer handles.

## Risks and Edge Cases

External code can technically access private fields and bypass validation. A stale `struct xe_guc_buf` after release can become a use-after-free if reused.

## Test Signals

Tests should focus on API-level behavior rather than direct field access: valid/invalid checks, lifetime, and suballocation manager capacity.
