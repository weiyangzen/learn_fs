# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kconfig.h

## Purpose

This header declares the NetIDMgr configuration provider API. It exposes a hierarchical, layered configuration model over user, machine, and schema stores, with typed values, shadow spaces, schema loading, enumeration, mutation, and removal.

## Important APIs, Types, and Functions

- `kconf_schema` describes schema entries: name, type, default value, and description.
- Value/schema types are `KC_NONE`, `KC_SPACE`, `KC_ENDSPACE`, `KC_INT32`, `KC_INT64`, `KC_STRING`, and `KC_BINARY`.
- Store/behavior flags include `KCONF_FLAG_ROOT`, `KCONF_FLAG_USER`, `KCONF_FLAG_MACHINE`, `KCONF_FLAG_SCHEMA`, `KCONF_FLAG_TRAILINGVALUE`, `KCONF_FLAG_WRITEIFMOD`, `KCONF_FLAG_IFMODCI`, and `KCONF_FLAG_NOPARSENAME`.
- Limits include `KCONF_MAXCCH_NAME`, `KCONF_MAX_DEPTH`, `KCONF_MAXCCH_PATH`, and `KCONF_MAXCCH_STRING`.
- Space lifecycle APIs: `khc_open_space`, `khc_shadow_space`, `khc_close_space`, `khc_get_config_space_name`, `khc_get_config_space_parent`, `khc_enum_subspaces`, and `khc_remove_space`.
- Read APIs: `khc_read_string`, `khc_read_multi_string`, `khc_read_int32`, `khc_read_int64`, and `khc_read_binary`.
- Write APIs: `khc_write_string`, `khc_write_multi_string`, `khc_write_int32`, `khc_write_int64`, and `khc_write_binary`.
- Metadata and schema APIs: `khc_get_type`, `khc_value_exists`, `khc_remove_value`, `khc_load_schema`, and `khc_unload_schema`.

## Control Flow

Clients open a configuration space relative to an optional parent, optionally creating it and choosing visible stores. Reads search visible stores by precedence, with user before machine before schema, and also consult shadow spaces for missing values. Writes target the top writable store visible through the handle. Schema loading uses a structured sequence of space-start, value, and space-end records. Enumeration returns subspace handles incrementally, freeing the previous handle as the next one is requested.

## State and Persistence Behavior

Configuration handles refer to persistent user and machine stores, plus read-only schema defaults. The comments indicate the Windows implementation maps spaces to registry keys, making name/path limits hard constraints. `KCONF_FLAG_WRITEIFMOD` avoids unnecessary writes by comparing with the effective read value. Shadowing is per-handle, not global, and does not transfer ownership of the lower handle.

## Dependencies and Integration Points

Depends on `<khdefs.h>` and `<mstring.h>`. It integrates NetIDMgr plugins and core code with Windows-backed application configuration, schema defaults, and identity/plugin settings. Identity configuration in `kcreddb.h` uses this provider through `kcdb_identity_get_config()`.

## Risks

- `KCONF_FLAG_WRITEIFMOD` and `KCONF_FLAG_NOPARSENAME` both use `0x00000040`; this overlap is surprising and requires implementation/context discipline to avoid ambiguous behavior.
- Binary values are unsupported by schema and are not affected by write-if-mod behavior.
- Handles can include layered stores and shadows; write behavior may differ from effective read behavior.
- Enumeration returns the union of stores and ignores shadowed spaces, which may surprise callers expecting only the restricted domain.
- Registry-backed persistence means permission and virtualization behavior can vary by process token and Windows version.

## Test Signals

Tests should use isolated registry/config roots where available. Cover open/create/close, path parsing and no-parse names, user/machine/schema precedence, shadow fallback, read/write for each type, buffer sizing with NULL buffers, schema load/unload, remove value/space, and enumeration handle lifetime.
