# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm.cc

Purpose: Implements RADOS storage for realm metadata, default realm id, realm name lookup, realm writer operations, notification control objects, and realm listing.

Important APIs/types/functions: Realm objects use `realms.<id>`, name indexes use `realms_names.<name>`, control objects use `realms.<id>.control`, and default id uses configured/default `default.realm`. `RadosRealmWriter` implements write/rename/remove with objv. `create_realm()`, `read_realm_by_id()`, `read_realm_by_name()`, `read_default_realm()`, `read_realm_id()`, `realm_notify_new_period()`, and `list_realm_names()` implement the SAL API.

Control flow: Create validates nonempty id/name, writes info, writes name->id, then creates the control object, rolling back prior objects on failure. Rename first creates the new name index exclusively, updates the info object with `MustExist`, removes the new name on failure, then best-effort removes the old name. Remove deletes info with versioning, then best-effort deletes name and control. Notifications encode `ZonesNeedPeriod`, the period, then `Reload`, and notify the realm control object.

State/persistence: Realm state spans info, name index, optional default-id object, and control object in the realm pool. Writer objects capture the objv from read/create to protect later mutations.

Dependencies/integration: Uses `RGWRealm`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, `RGWRealmNotify`, `ConfigImpl`, SAL writer interfaces, and `RadosRealmWatcher` consumers.

Risks: Multi-object create/rename/remove rollback is best effort; stale name indexes or control objects may remain. Rename mutates the caller's `RGWRealm& info` before the final old-name cleanup. Notification payload ordering must match watcher decoding expectations.

Test signals: Validate create rollback at each failure point, rename conflict and rollback, writer id/name immutability checks, default realm read/write/delete, realm notification decode by watcher, and list prefix filtering.
