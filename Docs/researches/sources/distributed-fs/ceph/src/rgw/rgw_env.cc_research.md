# sources/distributed-fs/ceph/src/rgw/rgw_env.cc

## Purpose
Implements RGW request environment/config map helpers used by frontends to access CGI/HTTP environment values and RGW logging options.

## Important APIs, types, and functions
`RGWEnv::init()` loads `char** envp` into a case-insensitive map and initializes `RGWConf`. `set()`, `get()`, `get_optional()`, `get_int()`, `get_bool()`, `get_size()`, `exists()`, `exists_prefix()`, and `remove()` provide typed access. Free helpers `rgw_conf_get*()` operate on generic config maps. `RGWConf::init()` snapshots ops/usage log enablement and bucket-ACL defer mode.

## Control flow
Frontend request setup populates `RGWEnv`, then request/auth/operation code reads headers and flags by name. `exists_prefix()` uses map lower_bound to efficiently detect prefixed variables.

## State and persistence
State is request-local environment map plus copied config booleans/mode. No durable storage.

## Dependencies and integration points
Uses `rgw_common.h`, `rgw_log.h`, Ceph config, case-insensitive comparator, and boolean parsing. It includes crypt sanitization because environment logging may redact keys elsewhere.

## Risks and test signals
Risks include `atoi()` accepting malformed ints, size parse fallback, case-insensitive ordering assumptions for prefix detection, and stale config snapshots after runtime config changes. Tests should cover malformed env entries, duplicate/case-variant keys, prefix lookups, bool parsing, size overflow, and ACL defer modes.
