# sources/distributed-fs/ceph/src/rgw/rgw_sal_filter.h

## Purpose
Declares the full filter/decorator layer for RGW SAL. It mirrors the generic SAL interface with wrapper classes that hold an underlying `next` object and forward calls. This provides a reusable base for filters that need to intercept, observe, or transform SAL behavior without implementing a storage backend.

## Important APIs, types, and functions
`FilterDriver` is the root wrapper and holds a raw `Driver* next` plus a cached `FilterZone`. It declares forwarding overrides for user, account, group, bucket, object, zone, lifecycle, restore, notification, topic, usage, metadata, sync, Lua, role, OIDC, writer, placement, admin, and context APIs.

Wrapper classes include `FilterPlacementTier`, `FilterZoneGroup`, `FilterZone`, `FilterUser`, `FilterBucket`, `FilterObject`, `FilterMultipartPart`, `FilterMultipartUpload`, `FilterMPSerializer`, `FilterLCSerializer`, `FilterRestoreSerializer`, `FilterLifecycle`, `FilterRestore`, `FilterNotification`, `FilterWriter`, and `FilterLuaManager`. Most store `std::unique_ptr<T> next` and expose `get_next()` for internal unwrapping.

`FilterObject` declares nested `FilterReadOp` and `FilterDeleteOp` to wrap object read and delete operations while preserving params and results. `FilterMultipartUpload` stores its own wrapper-level `parts` map so callers receive `FilterMultipartPart` objects even though the backend owns concrete parts.

## Control flow
The header's structure encodes a transparent decorator pattern. Factory methods in the driver and bucket layers return filtered versions of backend objects. Calls that return child objects allocate a wrapper around the backend child. Calls that accept objects or buckets are implemented in the `.cc` by unwrapping before forwarding.

## State and persistence behavior
The filter layer should not own persistence. It owns wrapper lifetimes with `unique_ptr` and maintains small amounts of adapter state: cached zone wrappers, a bucket pointer on `FilterObject`, and a copied/wrapped multipart parts map. All durable metadata, object content, usage, lifecycle, and sync state remains in the underlying driver.

## Dependencies and integration points
The header depends on `rgw_sal.h` and `rgw_role.h` and must track the evolving SAL virtual interface. It is used by `rgw_sal_filter.cc` and by any filter factory or derived custom filter that wants to extend the base forwarding behavior.

## Risks and test signals
Because this header mirrors many SAL methods, interface drift is the main maintenance risk. Missing an override can bypass filter behavior or fail compilation when SAL changes. The raw `Driver* next` is non-owning, so the wrapped driver must outlive the filter. Any derived filter must preserve wrapping/unwrapping rules or mixed backend/filter pointers can break. Build tests catch signature mismatches; runtime tests should instantiate a filter over a fake driver and assert that returned user/bucket/object/multipart/lifecycle/writer objects are wrapped and that forwarded method parameters are unchanged.
