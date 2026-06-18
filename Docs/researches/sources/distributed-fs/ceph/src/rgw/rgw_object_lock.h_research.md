## sources/distributed-fs/ceph/src/rgw/rgw_object_lock.h

Purpose: declares serialized types for S3 Object Lock bucket configuration, default retention, object retention, and legal hold.

Important APIs/types: `DefaultRetention` stores mode/days/years; `ObjectLockRule` wraps it; `RGWObjectLock` stores enabled/rule state and exposes `retention_period_valid()`, `has_rule()`, getters, XML/JSON methods, and `get_lock_until_date()`. `RGWObjectRetention` stores mode and retain-until date. `RGWObjectLegalHold` stores status and `is_enabled()`.

Control flow: RGW APIs decode request XML/JSON into these types, validate retention fields, encode them to attrs, and dump them back to clients/admin tools.

State and persistence: all classes have `WRITE_CLASS_ENCODER`; `RGWObjectRetention` encode version 2 writes both normal and round-trip time encoding for precision compatibility.

Dependencies/integration: depends on Ceph encoding/time/ISO-8601 and RGW XML support.

Risks and test signals: `RGWObjectLock` defaults `enabled=true` with no rule, which callers must interpret carefully. Tests should cover binary encoding compatibility, retention period validity, and default construction semantics.
