# sources/distributed-fs/ceph/src/rgw/driver/rados/account.h

Purpose: Declares the account RADOS persistence API used by RGW services and metadata sync. The header exposes account metadata CRUD, name/email lookup, resource-index object lookup, account resource count reading, and the account metadata handler factory.

Important APIs/types/functions: `create_metadata_handler()` creates the `"account"` RGW metadata handler. `get_buckets_obj()`, `get_users_obj()`, `get_groups_obj()`, `get_roles_obj()`, `get_topics_obj()`, and `get_oidcs_obj()` return `rgw_raw_obj` locations for account-scoped cls_user resource indexes. `read()`, `read_by_name()`, `read_by_email()`, `write()`, `remove()`, and `resource_count()` are the public entry points.

Control flow: Callers supply `DoutPrefixProvider`, `optional_yield`, `RGWSI_SysObj`, zone pools, and version trackers. The interface makes old account info explicit on writes so implementations can update secondary indexes safely relative to previous state.

State/persistence: The API is explicitly pool/object oriented through `rgw_raw_obj` and zone parameters. `write()` includes attrs, mtime, exclusivity, and objv so metadata sync and admin operations can preserve object metadata and concurrency semantics.

Dependencies/integration: Forward declarations keep compile dependencies low while coupling to RGW account info, bucket info, storage stats, metadata handler, sysobj, zone params, and librados. The resource-object helpers are integration points for bucket, group, role, topic, and OIDC listing modules.

Risks: The contract assumes callers pass an accurate `old_info` when updating mutable secondary-indexed fields. Passing null or stale old state can leave redirects or account-resource indexes inconsistent. The header does not document ownership/atomicity limits of multi-object writes, so users must know implementation behavior.

Test signals: Compile/link consumers against the declared API; exercise callers that use each `get_*_obj()` with cls_user helpers; verify metadata sync passes attrs/mtime/objv through `write()`.
