# sources/distributed-fs/orangefs/src/common/misc/server-config.h

## Purpose

`server-config.h` declares the public data structures and accessors for parsed OrangeFS server configuration. It is the contract shared by the config parser, server config manager, server startup code, storage setup, security code, and callers that need filesystem, alias, handle-range, module, timeout, and storage hint settings.

## Important APIs, types, and fields

- Context bit constants `CTX_GLOBAL`, `CTX_DEFAULTS`, `CTX_ALIASES`, `CTX_FILESYSTEM`, `CTX_METAHANDLERANGES`, `CTX_DATAHANDLERANGES`, `CTX_STORAGEHINTS`, `CTX_DISTRIBUTION`, `CTX_SECURITY`, `CTX_EXPORT`, `CTX_SERVER_OPTIONS`, and `CTX_LDAP` define dotconf legality masks and parser state values.
- `phys_server_desc_s` stores a resolved BMI address, address string, and server type.
- `host_alias_s` maps a human server alias to one BMI URL-like address string.
- `host_handle_mapping_s` binds an alias to a textual handle range and its `PVFS_handle_extent_array` representation for wire-level create/mkdir and local range checks.
- `filesystem_configuration_s` stores per-filesystem identity, root handle, metadata and data handle ranges, flow/encoding defaults, storage hints, export policy lists/netmasks, anonymous uid/gid, file stuffing, Direct I/O settings, and LMDB sizing.
- `distribution_param_configuration` and `distribution_configuration` represent configured default distribution name and integer parameters.
- `server_configuration_s` is the top-level parsed configuration: selected server alias and host id, storage paths, cached config file, request/job/retry/perf settings, precreate thresholds, logging, BMI/flow modules, TCP settings, trusted connection settings when enabled, parser context, alias and filesystem lists, distribution defaults, DB/Trove settings, security key/cert/LDAP/timeouts, private parser data, and distributed directory tuning.

The declared functions include `PINT_parse_config`, `PINT_config_release`, optional trusted-port/network accessors, alias lookups, handle range and extent queries, configuration validation, filesystem lookup and trimming helpers, filesystem secret key retrieval, and optional Trove storage setup/removal and sync-mode helpers.

## Control flow and ownership contract

Callers allocate `server_configuration_s`, pass it to `PINT_parse_config()`, use getters and direct struct fields while the object is live, and eventually call `PINT_config_release()`. Most returned strings from getters are borrowed pointers into the config object. The exception called out by the implementation is merged handle ranges, which allocate a new string. `PINT_config_get_meta_handle_extent_array()` allocates an extent array for the caller to free.

`server_configuration_s.private_data` is available to the parser implementation. `configuration_context`, `prev_context`, and `my_server_options` are parser execution state and should not be treated as stable user configuration.

## State and persistence behavior

The header describes in-memory state only. Persistent behavior is exposed indirectly under `__PVFS2_TROVE_SUPPORT__` through `PINT_config_pvfs2_mkspace()` and `PINT_config_pvfs2_rmspace()`, which use parsed paths and filesystem definitions to create or remove Trove storage spaces.

## Dependencies and integration points

The header depends on PVFS core types, `PINT_llist`, gossip logging, and optionally Trove. It is included by `server-config.c`, config manager code, state-machine helper macros through `server-config-mgr.h`, and components that need parsed configuration for networking, storage, security, flow, and filesystem lookup.

## Risks and edge cases

- The structs expose many mutable pointers directly, so callers can accidentally break parser-owned invariants if they modify fields instead of using parser helpers.
- `host_handle_mapping_s.alias_mapping` is a borrowed pointer into `server_configuration_s.host_aliases`; copying or freeing these objects independently requires care.
- Arrays such as export host lists, netmasks, precreate values, and extent arrays depend on companion count fields. Tests and callers must keep counts synchronized.
- Conditional fields under `USE_TRUSTED` and APIs under `__PVFS2_TROVE_SUPPORT__` change struct layout and available functions by build configuration.

## Test signals

Compile coverage should include trusted and non-trusted builds, Trove and non-Trove builds, and security-key/cert combinations. ABI-sensitive tests should verify that parsed configs can be released after partial and full initialization, copied or trimmed through the implementation helpers, and used by callers without taking ownership of borrowed pointers.
