# sources/distributed-fs/ceph/src/rgw/driver/rados/groups.cc

Purpose: Implements account-scoped group listing helpers using the `cls_user_account_resource` object-class API.

Important APIs/types/functions: `add()` encodes `resource_metadata{group_id}` into a cls resource named by group name with path from `RGWGroupInfo`. `remove()` removes a resource by name. `list()` pages resource entries by marker/path prefix and returns decoded group ids. `resource_metadata::dump()` and `generate_test_instances()` support JSON/encoding tests.

Control flow: Each operation resolves the supplied `rgw_raw_obj` to `rgw_rados_ref`, builds a cls_user account-resource op, and operates on the object. Listing treats missing objects as empty, decodes metadata for each returned entry, and clears `next_marker` when not truncated.

State/persistence: Group references are stored as cls_user account resources on an account's groups object, usually from `account::get_groups_obj()`. The resource name is the group name; encoded metadata carries the stable group id.

Dependencies/integration: Depends on librados, `cls/user/cls_user_client.h`, `RGWGroupInfo`, SAL forward types, and Ceph encoding/JSON helpers. `group.cc` calls these helpers when linking groups to accounts.

Risks: Since removal is by name, stale resources can remain if old names are not removed during rename. Decode failure in metadata aborts listing with `-EIO`. The `exclusive` and `limit` parameters are delegated to cls_user and need caller-chosen semantics.

Test signals: Add/remove/list pagination, path-prefix filtering, limit enforcement, missing object as empty list, corrupt resource metadata, and rename cleanup through `group.cc`.
