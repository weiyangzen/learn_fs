# sources/distributed-fs/ceph/src/rgw/driver/rados/users.cc

## Purpose
Implements account user list/index operations using the `cls_user_account_resource` object class. It maps display names and paths to encoded user ids for account-scoped user listing and lookup.

## Important APIs, types, and functions
- `add()` builds a resource from `RGWUserInfo::display_name` and `path`, encodes `resource_metadata{user_id}`, and inserts it with optional exclusivity/limit.
- `get()` reads a resource by display name and decodes the stored user id.
- `remove()` removes a resource by name.
- `list()` lists resources by marker/path prefix and decodes user ids.
- `resource_metadata` encodes/decodes a single `user_id` string and supports formatter dump/test instances.

## Control flow
The functions mirror `roles.cc`: resolve RADOS ref, prepare cls read/write operation, execute, check both operation and cls ret code, then decode metadata for get/list.

## State and persistence behavior
Account user resources are stored in a caller-provided raw object. The resource name is display name, path is user path, and metadata stores canonical user id. Missing list objects are treated as empty lists.

## Dependencies and integration points
Depends on `librados`, `cls/user/cls_user_client.h`, `RGWUserInfo`, `rgw_common.h`, and `rgw_sal.h`. It integrates with account IAM-style user management and any code that lists users under an account.

## Risks and edge cases
Display name is used as the resource name, so rename/display-name changes must update this index elsewhere. Decode corruption returns `-EIO`. Listing by path prefix depends on the path stored during add. A typo leaves a double semicolon in test instance construction but has no behavior impact.

## Test signals
Tests should cover add/get/remove/list, path-prefix filtering, display-name duplicate conflicts, missing object listing, corrupt metadata decode, and user id encoding compatibility.
