# sources/distributed-fs/ceph/src/rgw/driver/rados/role.cc

## Purpose
Implements v2 IAM role metadata storage on RADOS. It stores role records by globally unique id, maintains name and path/account indexes for lookup/listing, integrates with account resource lists, and exposes an RGW metadata handler for multisite metadata sync.

## Important APIs, types, and functions
- `read_by_id()` reads `RGWRoleInfo` from `roles.{id}` objects and optional tags from the raw `tagging` attr.
- `read_by_name()` resolves a name index object to a role id, then reads by id.
- `write()` writes or overwrites role info, updates name/path/account indexes, rolls back newly written indexes on failure, and records mdlog entries.
- `remove()` resolves by tenant/account/name and removes role info plus indexes.
- `list_tenant()` lists tenant path-index objects and reads each role by id.
- Internal `IndexObj`, `AccountIndex`, `NameIndex`, and `PathIndex` model system-object indexes and cls-user account resource indexes.
- `MetadataHandler` implements `get`, `put`, `remove`, and list operations for metadata type `roles`.

## Control flow
Writes first read existing role info when not exclusive, compare old/new name and path, gather old indexes that should be removed, write a new name object if needed, write a new path/account index, then write the main `roles.{id}` object. If the path or main write fails, it removes newly created indexes. After main write succeeds, old indexes are removed best-effort and mdlog completion is recorded. Removal performs the inverse: read by id, delete the main object with version tracking, delete name and path/account indexes best-effort, then mdlog.

## State and persistence behavior
Persistent objects live in `zone.roles_pool`: `roles.{id}` contains encoded `RGWRoleInfo`, tenant name indexes use `{tenant}role_names.{name}`, account name indexes use `{account}role_names.{lowercase_name}`, and tenant path indexes use `{tenant}role_paths.{path}roles.{id}`. Account roles are also indexed with `rgwrados::roles` in the account roles object. Tags are persisted as a system object attr named `tagging`. Version trackers guard main role objects and index writes generate write versions.

## Dependencies and integration points
Uses `RGWSI_SysObj`, `RGWSI_MDLog`, `RGWMetadataLister`, `RGWMetadataHandler`, `RGWRoleInfo`, `RGWNameToId`, `account::get_roles_obj()`, `rgwrados::roles` account-resource helpers, `librados::Rados`, and string utilities. It integrates with metadata sync via `create_metadata_handler()`.

## Risks and edge cases
Name handling differs for tenant and account roles: account names are lowercased for case-insensitive lookup, tenant names are not. Multi-object writes can leave stale name/path indexes if cleanup fails, though lookup reads the main object afterward. `write()` forbids role id mutation. `list_tenant()` may skip races where path index exists but main object is already deleted. Account path index removal is best-effort and uses role name, so stale account lists may survive partial failures.

## Test signals
Tests should cover exclusive create conflicts, overwrite rename/path changes, rollback when path or main write fails, account-role case-insensitive name lookup, tenant path-prefix listing, tag attr encode/decode, metadata handler put/remove/list, and deletion races during listing.
