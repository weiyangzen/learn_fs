
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.h

## Purpose

`xe_oa.h` declares the public OA subsystem interface used by device init, query code, and observation ioctls.

## Important APIs, Types, and Functions

It exposes initialization/registration, stream open, add/remove config ioctls, timestamp frequency lookup, and engine-to-OA-unit id lookup. It includes `xe_oa_types.h` for shared data structures.

## Control Flow

Device probe calls `xe_oa_init()` and later `xe_oa_register()`. Observation ioctl dispatch calls stream/config functions. Query paths call `xe_oa_timestamp_frequency()` and `xe_oa_unit_id()`.

## State and Persistence Behavior

State is stored in device and GT OA structures defined in `xe_oa_types.h`; this header only declares access.

## Dependencies and Integration Points

It forward declares DRM and Xe types and is included by observation, query, and initialization code.

## Risks and Edge Cases

Callers must handle `-ENODEV` from OA ioctls when OA is unsupported or disabled by platform/SR-IOV conditions.

## Test Signals

Compile coverage plus query/observation integration tests catch API and lifecycle regressions.
