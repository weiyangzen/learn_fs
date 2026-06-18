# sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.cc

## Purpose
Implements stream insertion wrappers that suppress SSE-C customer keys in logs when `rgw_crypt_suppress_logs` is enabled.

## Important APIs, types, and functions
Overloaded `operator<<` functions handle `env`, `x_meta_map`, `s3_policy`, `auth`, and `log_content`. They compare environment/header/policy field names against SSE-C key and copy-source-key names and print a fixed suppression message instead of the original value.

## Control flow
Logging code wraps potentially sensitive values in the appropriate type. The operator checks the global config flag and either writes `=suppressed due to key presence=` or forwards the raw value.

## State and persistence
No state is persisted. The only state read is global config and request environment contents.

## Dependencies and integration points
Depends on `rgw_common.h`, request state, global Ceph context, and Boost case-insensitive/eager substring predicates. It integrates with request logging, environment dumps, S3 POST policy logs, and civetweb-originated content logs.

## Risks and test signals
Risks include missing a header variant, suppressing only when exact wrappers are used, global-context access during early logging, and query-string substring false positives/negatives. Tests should cover every wrapper, case-insensitive names, copy-source key names, disabled suppression, query-string detection, and auth logs when key env vars exist.
