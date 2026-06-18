<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc

Purpose: Implements RGW wrappers around RADOS cls object classes for OTP/MFA, time-indexed logs, and distributed locks.

Important APIs, types, and functions: `RGWSI_Cls::do_start()` starts the MFA subservice. `MFA::get_mfa_ref()`, `check_mfa()`, `create_mfa()`, `remove_mfa()`, `get_mfa()`, `list_mfa()`, `otp_get_current_time()`, `set_mfa()`, and the oid-based `list_mfa()` wrap `cls_otp_client`. `TimeLog::prepare_entry()`, `add()`, `list()`, `info()`, `info_async()`, and `trim()` wrap `cls_log_client`. `Lock::lock_exclusive()` and `unlock()` wrap `cls_lock_client` with a default `rgw_log_lock` name.

Control flow: MFA methods resolve the per-user OTP object in `zone_params.otp_pool`, prepare versioned writes when needed, run cls operations, and translate OTP check failure to `-EACCES`. TimeLog methods resolve log objects in `zone_params.log_pool`, build cls log read/write operations, and run them synchronously or with librados aio completions. Lock methods initialize an IoCtx for the target pool, configure lock duration, cookie, tag, and optional lock name, then call cls lock APIs.

State and persistence: MFA entries are stored in per-user objects named `user:<uid>` in the OTP pool with version tracker and mtime handling. Time logs persist as cls log entries in log pool objects. Locks persist in RADOS object class lock state and are tagged with zone and owner ids.

Dependencies and integration points: Depends on `RGWSI_Zone` for pool selection, `librados::Rados`, `rgw_rados_ref`, `RGWObjVersionTracker`, and Ceph cls clients for otp/log/lock. MDLog and other services use `TimeLog` and `Lock` for metadata log operations.

Risks and test signals: MFA writes depend on correct version tracker progression and object reset semantics in `set_mfa()`. TimeLog async calls depend on caller-owned `AioCompletion` lifetime. Lock renewal and unlock require consistent tag/cookie. Unit or integration tests should cover OTP CRUD/check failures, metadata log add/list/trim, async info completion, and lock contention/unlock errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc -->
