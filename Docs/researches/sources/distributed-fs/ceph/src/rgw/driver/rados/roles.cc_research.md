# sources/distributed-fs/ceph/src/rgw/driver/rados/roles.cc

## Purpose
Implements account role list/index operations using the `cls_user_account_resource` object class. It stores role names/paths in account resource objects and encodes role ids as per-resource metadata.

## Important APIs, types, and functions
- `add()` builds a `cls_user_account_resource` from `RGWRoleInfo::name` and `path`, encodes `resource_metadata{role_id}`, and calls `cls_user_account_resource_add()`.
- `get()` reads a resource by name and decodes the role id from metadata.
- `remove()` removes a resource by name.
- `list()` lists resources by marker/path prefix and decodes each role id.
- `resource_metadata` supports Ceph encode/decode, JSON dump, and test instances.

## Control flow
Each operation resolves `rgw_raw_obj` to a `rgw_rados_ref`, prepares a librados read or write operation with cls_user helpers, executes through `ref.operate()`, then handles both transport errors and cls return codes.

## State and persistence behavior
State is stored inside a RADOS object using the user/account resource cls schema. The visible resource key is the role name, the sortable/listable path is the role path, and encoded metadata carries the actual role id. Missing list objects are treated as empty lists.

## Dependencies and integration points
Depends on `librados`, `cls/user/cls_user_client.h`, `rgw_sal.h`, `RGWRoleInfo`, and `rgw_get_rados_ref()`. Called from `role.cc` for account role path indexes and from account role listing code.

## Risks and edge cases
Metadata decode failures return `-EIO`, so corrupt account-resource metadata can break get/list. `add()` honors an exclusive flag and limit but leaves conflict/limit semantics to the cls method. List pagination depends on cls-provided `next_marker` and `truncated`.

## Test signals
Tests should cover add/get/remove/list round trips, exclusive duplicate behavior, path-prefix list filtering, missing object list behavior, limit enforcement, and corrupt metadata decode.
