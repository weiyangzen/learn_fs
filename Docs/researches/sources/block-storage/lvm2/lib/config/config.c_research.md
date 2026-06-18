# File Research: sources/block-storage/lvm2/lib/config/config.c

## Purpose

`config.c` is the implementation of LVM2's configuration subsystem. It turns the declarative configuration catalog from `config_settings.h` into runtime structures, reads configuration from files/devices/strings/profiles, validates user-provided config trees against known definitions, resolves typed values with defaults and profile overrides, merges config trees, emits generated configuration output, and supplies runtime-computed defaults for selected settings.

## Main Structures and State

- `_cfg_def_items[]`: generated static table of every configuration section/setting. It is built by including `config_settings.h` with macro definitions for `cfg_section`, `cfg`, `cfg_runtime`, `cfg_array`, and `cfg_array_runtime`.
- `struct config_source`: custom metadata attached to each `dm_config_tree`, recording source type, timestamp, file/profile backing object, and cached validation handle.
- `struct config_file`: stores file metadata including size, filename, existence status, and an active `struct device` wrapper while reading.
- `struct cft_check_handle`: declared in `config.h`, used here to track validation options and per-setting status flags (`CFG_USED`, `CFG_VALID`, `CFG_DIFF`).

## Configuration Sources

The code distinguishes:
- file-like sources: regular config files, special files, and profile files;
- profile-based sources: command profiles and metadata profiles;
- string overrides from command-line `--config`;
- merged config trees.

`config_open()` allocates a `dm_config_tree`, attaches source metadata, and prepares file metadata when the source is file-based. `config_get_source_type()` retrieves the attached source type.

## File Reading and Change Detection

`config_file_check()` validates that a config file exists and is a regular file, records ctime and size, and treats empty files as valid but with no filename returned for reading.

`config_file_changed()` checks whether a config file should be reloaded by comparing stored timestamp and size against current `stat()` data. Deleted files are treated as reload-worthy only if the file previously existed.

`config_file_open_and_read()` opens a config tree and reads a config file if it exists. Missing non-profile config files are tolerated; missing profile files are errors.

`config_file_read_from_file()` wraps a regular file descriptor in a temporary `struct device`, then calls `config_file_read_fd()`.

`config_file_read_fd()` is the lower-level metadata/config reader. It can read from regular files or block devices, supports split/circular metadata buffers, validates metadata text names for non-regular devices, verifies checksums when provided, and parses the buffer through libdevmapper config parsers. It also supports checksum-only mode and partial parsing of the `physical_volumes` section.

## Cascaded Overrides and Profiles

LVM config precedence is represented as a cascade:

`CONFIG_STRING -> CONFIG_PROFILE_COMMAND -> CONFIG_PROFILE_METADATA -> CONFIG_FILE/CONFIG_MERGED_FILES`

`override_config_tree_from_string()` parses a command-line config string, validates it in interactive mode, attaches source metadata, and inserts it at the head of the cascade.

`override_config_tree_from_profile()` loads a profile if needed and inserts command or metadata profiles at the correct cascade position. Helper functions handle command-profile and metadata-profile insertion.

`_apply_local_profile()` temporarily applies a VG/LV-local profile for a lookup unless a global metadata profile overrides it.

`add_profile()`, `load_profile()`, and `load_pending_profiles()` manage profile registration, validation, loading from `<profile_dir>/<name>.profile`, and migration from pending to loaded lists. Profile validation is always forced because invalid profile settings could otherwise alter behavior nondeterministically.

## Typed Lookup API

The file implements public accessors declared in `config.h`:

- `find_config_tree_node()`
- `find_config_tree_str()`
- `find_config_tree_str_allow_empty()`
- `find_config_tree_int()`
- `find_config_tree_int64()`
- `find_config_tree_float()`
- `find_config_tree_bool()`
- `find_config_tree_array()`
- `find_config_node()` and `find_config_bool()` for explicit config trees without normal override lookup

Each accessor:
1. resolves the definition item by ID;
2. builds the slash-separated config path;
3. optionally applies a local profile;
4. starts from the static or runtime default;
5. consults the cascaded `dm_config_tree`;
6. removes any temporarily applied profile.

`_config_disabled()` enforces `CFG_DISABLED` by warning when a disabled setting is explicitly present and returning the default value.

Array defaults are decoded from the compact `#S...#I...#B...#F...` representation by `_get_def_array_values()`.

## Validation

`config_def_check()` validates a config tree against `_cfg_def_items[]`.

Important behavior:
- Builds a hash from full config paths to definition items, using `#` for variable path components.
- Rejects unknown settings and unknown sections unless variable-name matching succeeds.
- Rejects top-level scalar settings outside sections.
- Checks value type compatibility, including arrays, booleans represented as strings, empty value rules, and scalar-vs-array misuse.
- Enforces profile eligibility through `CFG_PROFILABLE` and `CFG_PROFILABLE_METADATA`.
- Enforces context-specific disallowed flags such as `CFG_DISALLOW_INTERACTIVE`.
- Marks each definition ID as used, valid, and optionally different from default.

`config_force_check()` creates a temporary validation handle, forces checks even if `config/checks` is disabled, suppresses messages when normal checks are disabled, and adds interactive restrictions for shell mode.

## Difference Tracking

When `handle->check_diff` is set, `_check_value_differs_from_default()` compares configured values with static or runtime defaults and marks the node and ancestors with `CFG_DIFF`. This powers generated `CFG_DEF_TREE_DIFF` output.

## Tree Merging

`merge_config_tree()` destructively merges one config tree into another.

Raw merge replaces old values with new values.

Tag merge has special behavior:
- skips top-level `tags`;
- honors host tag matching;
- strips `tags` subsections from newly inserted nodes;
- merges selected value lists instead of replacing them, specifically `activation/volume_list`, `devices/filter`, and `devices/types`.

It also carries forward the newest config-source timestamp, which matters for persistent filter cache freshness.

## Generated Config Output

`config_def_create_tree()` constructs generated trees for modes such as current, missing, full, default, new, profilable, diff, and list.

`_should_skip_def_node()` controls inclusion by parent, version, advanced/unsupported/deprecated filters, profile eligibility, missing/current state, local-section filtering, and tree mode.

`_add_def_node()` creates nodes with default values, runtime defaults, unconfigured placeholder defaults, array defaults, octal formatting, and output spacing flags.

`config_write()` writes a config tree to stdout or a file. Output callbacks add comments, summaries, version metadata, deprecation notices, advanced/unsupported markers, variable-name notices, default-commenting behavior, list mode, value-only mode, and diff filtering.

## Runtime Default Helpers

Runtime defaults implemented here include:
- cache directory and cache file path defaults based on `cmd->system_dir`;
- backup, archive, and profile directory defaults;
- mirror image fault policy derived from mirror device fault policy;
- thin pool chunk size via `get_default_allocation_thin_pool_chunk_size()`;
- cache pool chunk size and maximum chunks;
- VDO metadata hints default, which changes for kernels newer than 6.8;
- PV metadata size via `get_default_pvmetadatasize_sectors()`.

## Dependencies

This file relies heavily on:
- libdevmapper config APIs (`dm_config_*`);
- LVM command context (`struct cmd_context`);
- device abstraction (`struct device`, `dev_read_bytes`, `dev_fd`);
- metadata/device helpers such as `validate_name()` and `get_default_pvmetadatasize_sectors()`;
- logging helpers (`log_error`, `log_warn_suppress`, etc.);
- memory pools (`dm_pool_*`);
- config definitions from `config_settings.h`.

## Risk and Maintenance Notes

- The config catalog is generated through repeated inclusion of `config_settings.h`; changing macro signatures or field ordering affects IDs, defaults, validation, and output.
- Profile validation is intentionally stricter than normal config validation.
- Config cascade ordering is a core invariant; inserting trees incorrectly changes precedence semantics.
- Runtime defaults may call other config lookups, so cyclic or unexpectedly expensive dependencies should be avoided.
- `CFG_PATH_MAX_LEN` bounds generated path buffers; deeper config paths or longer variable names would need care.
- Array default encoding is compact but fragile: malformed `#X` tokens are internal errors.
