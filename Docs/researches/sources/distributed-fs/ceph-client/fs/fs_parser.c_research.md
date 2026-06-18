# sources/distributed-fs/ceph-client/fs/fs_parser.c

## Purpose
`fs_parser.c` is the VFS helper library for parsing filesystem mount/reconfigure parameters described by `struct fs_parameter_spec`. It matches incoming `struct fs_parameter` keys, handles negated flag forms such as `nofoo`, converts simple string/file/path values into typed `struct fs_parse_result` fields, and validates duplicate parameter descriptions under `CONFIG_VALIDATE_FS_PARSER`.

## Important APIs, Types, and Functions
- `lookup_constant()` searches a `constant_table` and is exported for filesystems with enum-like options.
- `__fs_parse()` is the central matcher/converter used by `fs_parse()` wrappers. It returns the matched option id, `-ENOPARAM`, or conversion errors.
- `fs_lookup_param()` turns a string/filename parameter into a `struct path`, optionally requiring a block device.
- `fs_param_is_bool/u32/s32/u64/enum/string/fd/file_or_string/uid/gid/blockdev()` are reusable conversion callbacks for parameter specs.
- `fs_validate_description()` checks duplicate parameter names with matching flag/value shape in validation builds.

## Control Flow
Parsing begins in `__fs_parse()`, which calls `fs_lookup_key()` to find an exact spec whose flag-ness matches the incoming value. For flag parameters, `fs_lookup_key()` also supports `no` prefixes when `fs_param_neg_with_no` is set and reports the result through `result->negated`. `__fs_parse()` warns on deprecated specs, then either sets `result->boolean` for flags or invokes the spec-provided conversion callback. The conversion helpers uniformly reject mismatched value types, honor `fs_param_can_be_empty` for empty strings, and populate a typed field in `struct fs_parse_result`.

## State and Persistence
The file has no persistent storage. It mutates only caller-owned `fs_parse_result`, `fs_parameter`, and output `struct path` objects. `fs_lookup_param()` temporarily converts kernel strings to `struct filename`, performs `filename_lookup()`, and returns a refcounted path that callers must release. UID/GID conversion is relative to `current_user_ns()`.

## Dependencies and Integration Points
This code integrates with `fs_context`, the new mount API, `namei` pathname lookup, user namespace ID conversion, and filesystem-specific parameter tables throughout `fs/`. It is directly exercised by `fsconfig()` paths in `fsopen.c` via `vfs_parse_fs_param()` and by many filesystem `->parse_param` implementations.

## Risks
The main risks are option table ambiguity, accidentally accepting an unexpected value shape, namespace-sensitive UID/GID rejection, and lifetime mistakes around returned paths. `fs_param_is_blockdev()` is a placeholder that returns success without conversion, so block-device users need `fs_lookup_param()` or higher-level validation. Negated flags are only supported for pure flag parameters, so specs that define both flag and value forms must be tested for intended precedence.

## Test Signals
Useful signals include fsconfig/mount tests for flags, `no`-prefixed flags, deprecated options, empty values, enum tables, invalid UID/GID mappings, path lookup failures, and block-device rejection. Validation builds should catch duplicate spec entries through `CONFIG_VALIDATE_FS_PARSER`.
