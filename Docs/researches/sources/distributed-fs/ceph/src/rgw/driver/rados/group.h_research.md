# sources/distributed-fs/ceph/src/rgw/driver/rados/group.h

Purpose: Declares the RADOS-backed group metadata API and metadata-handler factory.

Important APIs/types/functions: `create_metadata_handler()` creates the group metadata handler. `get_users_obj()` returns the per-group user-list object. `read()`, `read_by_name()`, `write()`, and `remove()` expose group CRUD with attrs, mtime, version tracking, sysobj, rados, and zone parameters.

Control flow: The API requires both `RGWSI_SysObj` and `librados::Rados` for writes/removes because group updates touch system objects and cls_user account-resource indexes.

State/persistence: The contract covers primary group info, name lookup, and per-group user tracking in `zone.group_pool`, plus account group listing through implementation dependencies.

Dependencies/integration: Forward declares RGW group info, metadata handler, objv, sysobj, zone params, and librados. Includes buffer and time types for attrs/mtime.

Risks: Callers must pass correct old group state for update operations and the correct Rados client for cls_user linkage; mistakes can leave indexes stale.

Test signals: Compile consumers, verify metadata-handler registration, and run integration tests for account group listings after group create/update/remove.
