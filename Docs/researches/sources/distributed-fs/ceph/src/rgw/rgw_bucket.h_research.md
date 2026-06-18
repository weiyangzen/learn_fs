# sources/distributed-fs/ceph/src/rgw/rgw_bucket.h

Purpose: declares RGW bucket utility functions and object namespace constants used by bucket metadata, S3 URL parsing, and administrative ownership changes.

Important APIs/types/functions: `RGW_OBJ_NS_MULTIPART`, `RGW_OBJ_NS_SHADOW`, `init_bucket()`, `rgw_bucket_parse_bucket_key()`, `rgw_make_bucket_entry_name()`, `rgw_parse_url_bucket()`, and `rgw_chown_bucket_and_objects()`.

Control flow: this header is only declarations; behavior lives in `rgw_bucket.cc`.

State/persistence: constants define bucket-index namespaces for multipart and shadow objects. Declared functions operate on persisted bucket identifiers, metadata entry names, and SAL ownership state.

Dependencies/integration: includes `rgw_common.h` and `rgw_sal.h`, so it is RGW/SAL-specific unlike lower-level bucket types. Used by REST/admin code and bucket metadata utilities.

Risks: namespace constants and key parse contracts are compatibility surfaces; changing them breaks metadata lookup. The chown declaration exposes a broad operation whose callers must handle partial work and retries.

Test signals: compile users across RGW, namespace string expectations, and behavior tests in `rgw_bucket.cc`.
