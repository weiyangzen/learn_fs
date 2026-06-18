# sources/distributed-fs/ceph-client/include/linux/fs_parser.h

Purpose: declares the generic filesystem parameter parser used by `fs_context`-based mount implementations. It lets filesystems describe accepted parameter names, expected value types, flags, and enum tables in a compact table-driven format.

Important APIs and types: `struct constant_table` maps strings to integer values. `fs_param_type` is the validation/conversion function type used by built-in validators such as `fs_param_is_bool`, integer parsers, enum parser, string parser, block-device lookup, fd parser, uid/gid parser, and file-or-string parser. `struct fs_parameter_spec` describes one option name, parser, returned option id, flags such as `fs_param_neg_with_no`, `fs_param_can_be_empty`, and `fs_param_deprecated`, plus type-specific data. `struct fs_parse_result` returns negation and parsed scalar/id values. `fs_parse()`, `__fs_parse()`, `fs_lookup_param()`, `lookup_constant()`, and optional `fs_validate_description()` are the public functions. Constructor macros `fsparam_flag()`, `fsparam_bool()`, `fsparam_u32()`, `fsparam_enum()`, `fsparam_string_empty()`, and related helpers populate spec tables.

Control flow: filesystem `parse_param` callbacks pass their spec table and incoming `struct fs_parameter` to `fs_parse()`. The parser matches by name, handles `no` negation where allowed, invokes the expected type converter, and returns the option id for a switch statement. Block-device/file/path parameters may be looked up with `fs_lookup_param()`.

State and persistence: no persistent state is owned here. Parsed values affect transient mount contexts and ultimately superblock state if accepted. Deprecated flags and validation support are build-time/runtime diagnostics for parser table quality.

Dependencies and integration points: tightly integrated with `fs_context.h`, mount API UAPI value types, id mapping for uid/gid parsing, path lookup, block device opening, and filesystem-specific option enums.

Risks and test signals: risks include accepting malformed values, incorrect negation semantics, enum table drift, leaking filename/file references, and parser tables that forget terminators or duplicate names. Tests should cover every parameter type, `nofoo` handling, empty strings, deprecated options, monolithic mount strings, validation-enabled builds, and filesystem-specific option switch coverage.
