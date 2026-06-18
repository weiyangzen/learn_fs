# Group Research: group_1143_lvm2_sources_block_storage_lvm2_tools_command_c_sources_block_stora_c6121459e756

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/lvm2`.

This grouped report covers LVM2 command metadata parsing, command registry headers, configuration dumping, small command handlers, LV type/property macro lists, and `lvchange` command execution logic.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/command.c -->
# File Research: sources/block-storage/lvm2/tools/command.c

## Purpose
`command.c` builds and parses LVM2 command definitions. It turns generated macro sources such as `args.h`, `vals.h`, `lv_props.h`, `lv_types.h`, `cmds.h`, `commands.h`, and `command-lines-input.h` into runtime `struct command` records, lookup tables, command help output, and man-page-oriented usage text.

## Main Flow
`define_commands()` is the central parser. It resets stale command data on reinitialization, sorts option/value lookup arrays, then walks `_command_input`, the generated `command-lines.in` content with comments stripped.

It recognizes command lines, reusable `OO_FOO:` optional-option groups, `OO:`, `IO:`, `OP:`, `DESC:`, `AUTOTYPE:`, `FLAGS:`, `RULE:`, and `ID:` lines, plus continuations. Parsed strings are converted into option enums, value enums, LV type bitsets, LV property bitsets, and positional/option argument definitions.

## Key Behavior
- `_opt_str_to_num()` maps long option strings to `foo_ARG`, including duplicate long-option handling.
- `_val_str_to_num()` maps command-definition value names to `foo_VAL`.
- `_set_pos_def()` and `_set_opt_def()` populate `struct arg_def`.
- `_add_rule()` parses command rules for option/LV type/LV property constraints.
- `factor_common_options()` computes options common to all variants of a command.
- `print_usage()` and related helpers generate compact command help/man usage.
- `configure_command_option_values()` adjusts accepted option value types for command-specific size/extents semantics.

## Integration Notes
The file bridges generated command metadata and the runtime command-line engine. It is used both in normal LVM builds and in `MAN_PAGE_GENERATOR` builds.

## Risks
Hard-coded capacity constants, generated-file ordering assumptions, and in-place parsing make this file sensitive to changes in `command-lines.in`, `args.h`, `vals.h`, `lv_props.h`, `lv_types.h`, and `commands.h`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/command.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/command.h -->
# File Research: sources/block-storage/lvm2/tools/command.h

## Purpose
`command.h` defines the core data model for LVM2 command definitions, command names, option/value descriptors, positional arguments, command rules, and command parsing/help state.

## Main Types
It defines command function pointers, `struct command_name`, `struct command_name_args`, `struct command`, `struct arg_def`, `struct opt_arg`, `struct pos_arg`, `struct cmd_rule`, `struct opt_name`, `struct val_name`, `struct lv_prop`, and `struct lv_type`.

## Key Contracts
The header sets fixed array limits for required/optional options, required/optional positional args, ignored options, and command rules. It also defines command-definition flags such as `CMD_FLAG_ANY_REQUIRED_OPT`, `CMD_FLAG_SECONDARY_SYNTAX`, `CMD_FLAG_PREVIOUS_SYNTAX`, and `CMD_FLAG_PARSE_ERROR`.

## Integration Notes
This is the shared ABI between generated command metadata parsing, command-line processing, help/man generation, and concrete command handlers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/command.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/command_enums.h -->
# File Research: sources/block-storage/lvm2/tools/command_enums.h

## Purpose
`command_enums.h` centralizes generated enums and command policy flags used by LVM2 command parsing and dispatch.

## Contents
It includes generated command-definition IDs, then expands macro lists into option enums, value enums, LV property enums, LV type enums, and top-level command enums.

It also defines command policy flags such as `PERMITTED_READ_ONLY`, `ALL_VGS_IS_DEFAULT`, `ENABLE_ALL_DEVS`, `LOCKD_VG_SH`, `NO_METADATA_PROCESSING`, `ALLOW_HINTS`, `ALLOW_EXPORTED`, `CHECK_DEVS_USED`, and `ALTERNATIVE_EXTENTS`.

## Integration Notes
Enum ordering and flag values are consumed by `command.c`, `command.h`, command dispatch, command validation, and `commands.h`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/command_enums.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/commands.h -->
# File Research: sources/block-storage/lvm2/tools/commands.h

## Purpose
`commands.h` is the top-level LVM command registry. It is a macro table using `xx(command, description, flags)` entries.

## Contents
The file lists user-facing commands such as `dumpconfig`, `formats`, `lvchange`, `lvconvert`, `lvcreate`, `lvdisplay`, `lvs`, PV/VG commands, reporting commands, and compatibility/removed commands.

Each entry provides a stable command name, short description, and command policy flags.

## Integration Notes
The file is included multiple times under different `xx` definitions to generate command-name tables, command enums, and command metadata. Changes affect command availability, help text, locking behavior, all-VG defaults, and metadata-processing policy.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/commands.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/dumpconfig.c -->
# File Research: sources/block-storage/lvm2/tools/dumpconfig.c

## Purpose
`dumpconfig.c` implements `dumpconfig`, `config`, and `lvmconfig`. These commands display, validate, or write LVM configuration trees.

## Main Flow
`dumpconfig()` validates option combinations, selects or merges the active config tree, optionally validates it, builds the requested config-definition tree, and writes it through `config_write()`.

## Key Behavior
- `_get_vsn()` parses `--atversion`, `--sinceversion`, or `LVM_VERSION`.
- `_do_def_check()` runs config-definition checks with mode-specific settings.
- `_merge_config_cascade()` recursively merges cascaded config trees.
- `_config_validate()` validates current configuration for `--validate`.

Supported output modes include `list`, `full`, `current`, `missing`, `default`, `diff`, `new`, `profilable`, `profilable-command`, and `profilable-metadata`.

## Integration Notes
The command uses config tree/profile APIs and returns standard LVM command return codes. `config()` and `lvmconfig()` are wrappers around `dumpconfig()`.

## Risks
The option matrix is dense. Future output modes or flags need careful validation against existing incompatibility checks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/dumpconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/errors.h -->
# File Research: sources/block-storage/lvm2/tools/errors.h

## Purpose
`errors.h` defines integer return codes used by LVM command handlers.

## Values
- `ECMD_PROCESSED`: command completed successfully.
- `ENO_SUCH_CMD`: command was not found.
- `EINVALID_CMD_LINE`: invalid command-line input.
- `EINIT_FAILED`: initialization failed.
- `ECMD_FAILED`: command execution failed.

## Integration Notes
These values are used across CLI command handlers and cmdlib-facing execution paths.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/formats.c -->
# File Research: sources/block-storage/lvm2/tools/formats.c

## Purpose
`formats.c` implements the `formats` command, which lists available LVM metadata formats.

## Behavior
`formats()` ignores positional arguments, calls `display_formats(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
The command is registered as read-only and metadata-free in `commands.h`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/formats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/license.inc -->
# File Research: sources/block-storage/lvm2/tools/license.inc

## Purpose
`license.inc` is an include fragment containing the standard LVM2 LGPL v2.1 copyright/license notice.

## Contents
It contains only the comment block and defines no symbols.

## Integration Notes
It is likely reused by generated or templated tool sources that need a shared license preamble.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/license.inc -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lv_props.h -->
# File Research: sources/block-storage/lvm2/tools/lv_props.h

## Purpose
`lv_props.h` is a macro list of LV property predicates used in command-definition rules.

## Contents
It lists LV state, visibility, sub-LV role, snapshot/origin, cache, COW, historical, RAID tracking, and RAID integrity properties.

## Integration Notes
Callers define `lvp(name)` to generate enums and lookup tables. The file notes that `toollib.c:_lv_is_prop()` must be updated when new properties are added.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lv_props.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lv_types.h -->
# File Research: sources/block-storage/lvm2/tools/lv_types.h

## Purpose
`lv_types.h` is a macro list of LV type names used by command definitions.

## Contents
It lists linear, striped, snapshot, cache, cachepool, integrity, mirror, RAID variants, thin/thinpool, VDO/vdopool, writecache, zero, and error types.

## Integration Notes
Callers define `lvt(name)` to generate enums and lookup tables. Type strings are used in command-definition suffixes such as `LV_type`. The file notes that `toollib.c:_lv_is_type()` must be updated when new types are added.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lv_types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvchange.c -->
# File Research: sources/block-storage/lvm2/tools/lvchange.c

## Purpose
`lvchange.c` implements the many `lvchange` command variants. It changes LV properties, activation state, monitoring/polling, refresh state, persistent device numbers, RAID resync/rebuild/sync actions, cache/writecache settings, VDO settings, integrity settings, tags, profiles, activation-skip, autoactivation, compression, and deduplication.

## Metadata Commit Model
The file uses internal bits `MR_COMMIT` and `MR_RELOAD` so helpers can request either metadata commit only or metadata commit plus table reload. `_commit_reload()` applies the requested operation.

## Major Operation Groups
Property helpers handle permissions, pool discard/zero settings, allocation, error-when-full, read-ahead, persistent major/minor numbers, tags, profiles, activation-skip, autoactivation, compression, and deduplication.

Cache/VDO/integrity helpers update writecache settings, cache mode/policy, VDO parameters, and dm-integrity settings with type-specific validation and active-LV restrictions.

RAID helpers implement resync, rebuild, writemostly/writebehind, recovery rates, and sync actions. Resync can deactivate active LVs, detach and wipe metadata/log devices, reattach them, commit metadata, reactivate, and back up.

Activation helpers handle foreign VG restrictions, activation-skip policy, snapshot-origin behavior, autoactivation filters, no-autoactivate flags, background polling, component LV activation prompts, and deactivation-friendly processing of component LVs.

## Command Entry Points
Exported handlers include `lvchange_properties_cmd()`, `lvchange_activate_cmd()`, `lvchange_refresh_cmd()`, `lvchange_resync_cmd()`, `lvchange_syncaction_cmd()`, `lvchange_rebuild_cmd()`, `lvchange_monitor_poll_cmd()`, `lvchange_persistent_cmd()`, and fallback `lvchange()` for missing command-definition function mappings.

## Integration Notes
Most command entry points call `process_each_lv()` with a check callback and a single-LV callback. They set command context flags for lockd, missing PV handling, activation mode, device-name mismatch tolerance, component LV processing, and foreign VG inclusion.

## Risks
The file has a large state space involving LV visibility, component LV exceptions, lockd state, active/inactive state, segment type, metadata commit grouping, and backward-compatible mixed activation/property behavior. New options must be classified correctly as group-commit or direct-commit operations.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvchange.c -->