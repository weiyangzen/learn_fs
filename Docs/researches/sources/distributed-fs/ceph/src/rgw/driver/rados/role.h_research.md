# sources/distributed-fs/ceph/src/rgw/driver/rados/role.h

## Purpose
Declares the RADOS role metadata interface implemented by `role.cc`. It is the public boundary for reading, writing, removing, listing tenant roles, and constructing the metadata handler.

## Important APIs, types, and functions
- `read_by_id()` loads `RGWRoleInfo` by role id with optional mtime, version tracker, and cache info outputs.
- `read_by_name()` resolves tenant/account/name to role info.
- `write()` persists role info and updates name/path indexes, with `exclusive` controlling create-only behavior.
- `remove()` removes a role identified by tenant/account/name.
- `list_tenant()` returns paginated `RGWRoleInfo` entries for tenant roles filtered by path prefix.
- `create_metadata_handler()` returns an `RGWMetadataHandler` for role metadata sync.

## Control flow
The API separates id-based reads from name-based resolution and accepts all service dependencies explicitly: RADOS cluster handle, system object service, mdlog, and zone parameters. Callers provide `optional_yield` for coroutine-friendly RADOS operations.

## State and persistence behavior
The declarations expose optional version/mtime/cache outputs but hide object naming details. `write()` takes a mutable `RGWObjVersionTracker` and mtime, signaling optimistic write/version integration with metadata sync.

## Dependencies and integration points
Forward declares RADOS, metadata, mdlog, sysobj, zone, role info, cache, and account id types. It is used by RGW role administration, IAM-style account role code, and metadata replication.

## Risks and edge cases
Callers must pass the correct tenant/account pair for `read_by_name()` and `remove()`; the implementation stores account names differently from tenant names. `max_items` and path prefix behavior are implementation-defined and should be used consistently by admin list code.

## Test signals
Compile coverage should catch signature drift with `role.cc`; integration tests should exercise each declared operation under tenant and account contexts and verify version tracker propagation.
