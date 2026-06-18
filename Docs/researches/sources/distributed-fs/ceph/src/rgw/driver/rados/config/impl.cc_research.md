# sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.cc

Purpose: Provides the low-level RADOS implementation used by `RadosConfigStore` for realm, period, zonegroup, zone, and period-config metadata. It centralizes pool selection, object read/write/remove, version tracking, and notification.

Important APIs/types/functions: `ConfigImpl::ConfigImpl()` resolves root pools from config with defaults to `rgw.root`. `read()` initializes an ioctx and reads the full object, preparing objv reads when supplied. `write()` applies `Create` semantics (`MustNotExist`, `MayExist`, `MustExist`), prepares object-version assertions, writes full content, and applies the write version. `remove()` does versioned delete. `notify()` sends RADOS notify payloads.

Control flow: Every operation opens an ioctx with `rgw_init_ioctx()`, builds a librados operation, optionally inserts version-tracker assertions, and delegates to `rgw_rados_operate()` or `rgw_rados_notify()`. Successful writes/removes call `objv->apply_write()` to advance local version state.

State/persistence: The class does not define object schemas; it persists already-encoded bufferlists or templated encoded objects into the configured root pools. Pool names are immutable members derived at construction.

Dependencies/integration: Depends on librados, RGW pool initialization helpers, `RGWObjVersionTracker`, `ConfigProxy`, and object encoding. Higher-level config files call it for all RADOS-backed SAL config-store operations.

Risks: Each call initializes a fresh ioctx, so failures in pool configuration surface on every operation. `Create::MayExist` overwrites full objects. Decode failures are handled in the templated header method, not here. Notification timeout handling is delegated to RADOS.

Test signals: Validate default and overridden pool names, create-mode error behavior (`-EEXIST`/`-ENOENT`), version conflict handling (`-ECANCELED`), full-object overwrite semantics, and notify delivery to realm watchers.
