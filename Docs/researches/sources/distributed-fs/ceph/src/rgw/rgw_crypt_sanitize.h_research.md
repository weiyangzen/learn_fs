# sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.h

## Purpose
Declares lightweight wrapper types for redacting encryption customer keys from RGW logs.

## Important APIs, types, and functions
`rgw::crypt_sanitize::env`, `x_meta_map`, `s3_policy`, `auth`, and `log_content` each capture the context needed to decide whether an output value may contain an SSE-C key. The header declares insertion operators for each wrapper.

## Control flow
Callers construct wrappers inline in log statements. The implementation decides whether to write the sensitive value or a suppression marker.

## State and persistence
Wrappers hold string views or request pointers only for the duration of the log expression. Nothing is persisted.

## Dependencies and integration points
Includes `rgw_common.h` for `req_state`. This is a small interface consumed by RGW request parsing and logging code that handles environment variables, metadata maps, S3 policy variables, auth strings, and raw logs.

## Risks and test signals
Because values are mostly `string_view`, caller lifetime must outlive streaming. Tests should ensure wrappers do not outlive temporaries, all sensitive field names are handled, non-sensitive values still print, and the config flag gates behavior.
