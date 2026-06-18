# Group Research: group_1145_lvm2_sources_block_storage_lvm2_tools_lvm_c_sources_block_storage_l_2608d2e8ddd5

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm.c -->
# File Research: sources/block-storage/lvm2/tools/lvm.c

## Purpose
`lvm.c` is the main executable entry point for the `lvm` binary and, when readline/editline support is compiled in, implements the interactive `lvm>` shell.

## Main Behavior
- `main()` delegates directly to `lvm2_main(argc, argv)`.
- Shell completion is compiled under `READLINE_SUPPORT` or `EDITLINE_SUPPORT`.
- `_list_cmds()` completes command names from `struct cmdline_context`.
- `_list_args()` completes valid short and long options for the detected command.
- `_completion()` chooses command completion for the first word and option completion for words beginning with `-`.
- Shell history is stored in `$HOME/.lvm_history`, capped by `shell_history_size`, read at startup, and written after command execution.

## Shell Flow
`lvm_shell()` initializes report formatting and command-log state, then loops over `readline("lvm> ")`. It handles EOF, empty lines, optional leading `lvm`, `quit`/`exit`, argument splitting with `lvm_split()`, command execution through `lvm_run_command()`, and user-facing errors for `ENO_SUCH_CMD`.

## Important Details
- `cmd->is_interactive` prevents use of options marked noninteractive.
- `lastlog` is special because it preserves command log rows and temporarily changes report selection.
- Normal commands discard prior command-log rows before execution.
- Report-group output is flushed with `dm_report_group_output_and_pop_all()`.
- Cleanup restores log report state, frees input/history/report objects, and clears interactive mode.

## Dependencies
- `lvm2cmdline.h` for `lvm2_main`, `lvm_run_command`, `lvm_split`, and command metadata.
- Readline/editline APIs.
- LVM report and command-log APIs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd-static.c -->
# File Research: sources/block-storage/lvm2/tools/lvm2cmd-static.c

## Purpose
Provides `liblvm2cmd` initialization functions for static builds.

## Main Behavior
- `lvm2_init()` calls `cmdlib_lvm2_init(1, 0)`.
- `lvm2_init_threaded()` calls `cmdlib_lvm2_init(1, 1)`.

## Important Details
The first initializer argument marks static compilation. All real setup is delegated to `cmdlib_lvm2_init()` in `lvmcmdlib.c`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd-static.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd.c -->
# File Research: sources/block-storage/lvm2/tools/lvm2cmd.c

## Purpose
Provides `liblvm2cmd` initialization functions for normal dynamic builds and a stub shell implementation for library contexts.

## Main Behavior
- `lvm2_init()` calls `cmdlib_lvm2_init(0, 0)`.
- `lvm2_init_threaded()` calls `cmdlib_lvm2_init(0, 1)`.
- `lvm_shell()` is a no-op returning `0`.

## Important Details
The stub `lvm_shell()` satisfies linkage where command-library APIs are present without the interactive executable shell from `lvm.c`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd.h -->
# File Research: sources/block-storage/lvm2/tools/lvm2cmd.h

## Purpose
Public C API header for embedding or running LVM2 commands through `liblvm2cmd`.

## API Surface
- Defines `lvm2_log_fn_t` for line-oriented logging callbacks.
- Defines log levels from `LVM2_LOG_SUPPRESS` through `LVM2_LOG_DEBUG`.
- Defines public command result constants mapped to internal `ECMD_*` style values.
- Declares:
  - `lvm2_log_fn()`
  - `lvm2_init()`
  - `lvm2_init_threaded()`
  - `lvm2_disable_dmeventd_monitoring()`
  - `lvm2_log_level()`
  - `lvm2_run()`
  - `lvm2_exit()`

## Important Details
Supports C++ callers with `extern "C"`. `lvm2_run()` accepts a nullable handle for one-off execution. The default built-in log level is documented as `LVM2_LOG_PRINT`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmdline.h -->
# File Research: sources/block-storage/lvm2/tools/lvm2cmdline.h

## Purpose
Internal command-line subsystem header shared by the executable, shell, and command-library wrapper.

## Key Types
`struct cmdline_context` holds option metadata, generated command definitions, command-name metadata, and valid argument tables.

## Declared Functions
- `lvm2_main()`
- `cmdlib_lvm2_init()`
- `lvm_fin()`
- `init_lvm()`
- `lvm_register_commands()`
- `lvm_split()`
- `lvm_run_command()`
- `lvm_return_code()`
- `lvm_shell()`

## Important Details
This header is the bridge between standalone CLI startup, interactive shell execution, and `liblvm2cmd` embedding.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm2cmdline.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvmcmdlib.c -->
# File Research: sources/block-storage/lvm2/tools/lvmcmdlib.c

## Purpose
Implements the public `liblvm2cmd` API declared in `lvm2cmd.h`.

## Main Behavior
- `cmdlib_lvm2_init(static_compile, threaded)` sets static-build state, initializes an LVM command context, registers commands, and returns the context as an opaque handle.
- `lvm2_run(handle, cmdline)` creates a one-off handle if needed, duplicates and splits the command line, rejects empty or oversized commands, and delegates to `lvm_run_command()`.
- Internal command strings handle daemon-specific operations:
  - `_memlock_inc`
  - `_memlock_dec`
  - `_dmeventd_thin_command`
  - `_dmeventd_vdo_command`
- `lvm2_disable_dmeventd_monitoring()` marks the context as dmeventd-run.
- `lvm2_log_level()` changes built-in verbosity.
- `lvm2_log_fn()` installs the external log callback.
- `lvm2_exit()` finalizes the command context.

## Important Details
One-off execution owns and releases its temporary handle. Return values are internal command status codes matching the public constants.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvmcmdlib.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvmcmdline.c -->
# File Research: sources/block-storage/lvm2/tools/lvmcmdline.c

## Purpose
Central LVM2 command-line engine. It registers generated command definitions, parses options and positionals, chooses the matching command variant, applies configuration/profile/runtime settings, initializes subsystems, dispatches command functions, and performs cleanup.

## Command Metadata
- Global `commands[COMMAND_COUNT]` stores generated command definitions.
- `_cmdline` stores command and option tables used by parsing, usage, shell completion, and dispatch.
- `_command_functions[]` maps newer command enums to variant-specific implementations; unmapped commands fall back to the command-name function table.
- `lvm_register_commands()` calls `define_commands()`, assigns command indexes, computes valid options per command name, and populates `_cmdline`.

## Argument Helpers
Exports shared helpers used by tool implementations:
- Presence and count helpers: `arg_count()`, `arg_is_set()`, grouped variants.
- Value helpers for strings, signed/unsigned integers, sizes, percentages, signs, and force levels.
- List checks for mutually allowed/disallowed options and negative/zero values.
- Synonym merging for legacy option names such as `--resizable`, `--allocation`, raid aliases, and metadata-copy aliases.

## Value Parsing
Implements validators/parsers for yes/no, activation modes, cache mode, discards, mirror logs, metadata type, allocation, lock type, segment type, readahead, regionsize, metadata copies, polling operations, report formats, config types, repair/dump types, headings, integer values, size values, and extent/percentage forms. Size parsing stores sectors, handles locale decimal separators, validates 512-byte alignment for byte input, supports IEC suffixes, and rejects overflow.

## Command Matching
`_find_command()` selects the best generated command variant by matching:
- command name,
- required options,
- any-required option groups,
- required positionals,
- `--type` special cases and autotypes,
- accepted optional/ignored options,
- unused options and extra positionals,
- command rules for invalid or required option combinations.

It prints nearest syntax hints when no variant matches and rejects unused options/arguments for the selected variant.

## Runtime Setup
`lvm_run_command()`:
- normalizes long-option hyphens,
- records the command line,
- finds the command name,
- parses options with generated getopt tables,
- applies immediate output settings,
- finds the command variant,
- handles ignored options,
- applies `--config` and profile overrides,
- refreshes tool context if config changed,
- initializes connections, filters, locking, lvmlockd, multipath checks, hints, and md-component checks,
- dispatches the selected command function,
- sends dbus notifications when configured,
- drops caches, labels, hints, devices-file state, temporary config/profile trees, and per-command memory.

## Startup And Scripts
`lvm2_main()` validates file descriptors, handles custom log FDs, may exec the dynamic `lvm` from a static binary, detects aliases, translates help shortcuts, initializes the tool context, registers commands, and chooses shell, script, or single-command execution. `_run_script()` executes shebang-marked LVM command scripts line by line using `lvm_split()` and `lvm_run_command()`.

## Important Details
- `lvm_split()` is simple shell-like splitting with single/double quote support and comment handling.
- `_check_standard_fds()` ensures stdin/stdout/stderr are usable.
- `init_lvm()` creates the tool context and installs option metadata.
- `lvm_fin()` unregisters commands, destroys the tool context, and finalizes udev library context.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvmcmdline.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvmdevices.c -->
# File Research: sources/block-storage/lvm2/tools/lvmdevices.c

## Purpose
Implements the `lvmdevices` command for inspecting, checking, updating, and editing the LVM devices file.

## Main Modes
- `--listids`: scans a device and prints available system device IDs, optionally filtered by `--deviceidtype`.
- no modifying option: reads and prints current devices-file entries.
- `--check`: validates the devices file and exits with failure if updates are needed.
- `--update`: validates and writes required devices-file updates.
- `--adddev`: adds a specific device path.
- `--addpvid`: searches all eligible devices for a PVID and adds matching devices.
- `--addid`: adds by explicit device ID and ID type.
- `--deldev`: removes by device name, or legacy ID-name behavior with `--deviceidtype`.
- `--delid`: removes by ID name/type.
- `--delpvid`: removes by PVID.

## Device Search
`_search_devs_for_pvids()` builds an unfiltered device list, skips devices already matched to devices-file entries, applies non-data filters, reads LVM labels for candidate PVIDs, records found devices, invalidates unmatched labels, and then reapplies data-reading filters to warn about excluded matches.

## Check/Update Reporting
`_print_check()` compares old devices-file entries against newly resolved entries. It reports no-change, update, add/remove, device-not-found, indeterminate, and system identifier changes. It handles:
- stable ID-type/ID-name matches,
- `DEVNAME` entries matched by PVID,
- refreshed entries with changed ID type,
- entries that cannot be conclusively correlated.

## Devices File Handling
`lvmdevices()` sets up and locks the devices file. Mutating operations use exclusive locking and create the file for add operations when needed. Read/check operations use shared locking and require the file to exist. The command reads IDs, scans the device cache, matches devices, prepares open-file limits, and writes updates through `device_ids_write()`.

## Safety Details
- Device removal prompts if the target is used by an active LV unless `--yes` is set.
- `--adddev` can add filtered devices but warns when filters exclude them.
- `--addpvid` only adds devices found through the filtered search path.
- `--check` treats entry updates as failure, while hash-only mismatch is reported separately.
- Multipath component entries can be removed and replaced with multipath devices during update.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvmdevices.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvmdiskscan.c -->
# File Research: sources/block-storage/lvm2/tools/lvmdiskscan.c

## Purpose
Implements `lvmdiskscan`, which lists block devices visible to LVM and reports which are LVM physical volumes.

## Main Behavior
- Initializes counters on each invocation to support interactive shell reuse.
- Warns when `--lvmpartition` limits output to LVM devices.
- Runs `label_scan()` before filtered device iteration.
- Computes maximum device-name width for aligned output.
- Iterates devices with filters applied.
- Uses `lvmcache_has_dev_info()` to identify LVM PVs.
- Prints device path, size, and optional “LVM physical volume” label.
- Counts whole disks versus partitions using the last character of the device name.
- Prints disk, partition, PV whole-disk, and PV partition totals.

## Important Details
If size lookup fails for a normal device, the command warns and prints size zero. If size lookup fails for a known PV, it logs an error and skips that device.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvmdiskscan.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvpoll.c -->
# File Research: sources/block-storage/lvm2/tools/lvpoll.c

## Purpose
Implements `lvpoll`, which waits for or aborts asynchronous LV operations such as pvmove, conversion, and merge operations.

## Main Behavior
- Defines poll function tables for pvmove, mirror conversion, snapshot merge, and thin merge.
- `_set_daemon_parms()` maps `--polloperation` to progress title, LV type flags, and poll callbacks.
- Reads `--interval`, `--abort`, signed interval behavior, and `--handlemissingpvs`.
- `_poll_lv()` validates the LV name and calls `wait_for_single_lv()`.
- `lvpoll()` requires `--polloperation`, rejects negative intervals, requires an LV name, and dispatches polling.

## Important Details
Accepted poll operations are `pvmove`, `convert`, `merge`, and `merge_thin`. The command returns invalid-command-line status for missing or unknown operation parameters.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvpoll.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvreduce.c -->
# File Research: sources/block-storage/lvm2/tools/lvreduce.c

## Purpose
Thin wrapper implementing the old command-name entry point for `lvreduce`.

## Main Behavior
`lvreduce()` delegates directly to `lvresize_cmd(cmd, argc, argv)`.

## Important Details
Actual reduce parsing and execution are handled by the shared resize implementation in `lvresize.c`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvreduce.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvremove.c -->
# File Research: sources/block-storage/lvm2/tools/lvremove.c

## Purpose
Implements `lvremove`, removing one or more logical volumes or selected LVs.

## Main Behavior
- Requires at least one LV path unless `--select` is used.
- Enables handling missing PVs and includes historical LVs.
- Initializes a processing handle with `struct lvremove_params`.
- Calls `process_each_lv()` with `READ_FOR_UPDATE` and `lvremove_single`.
- If LV scanning and devices-file support are enabled, updates device IDs for removed LV UUIDs.
- Destroys the processing handle and returns the per-LV processing result.

## Important Details
The file is a command wrapper around shared LV removal logic, with devices-file cleanup triggered after successful processing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvremove.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvrename.c -->
# File Research: sources/block-storage/lvm2/tools/lvrename.c

## Purpose
Implements `lvrename`, including support for renaming historical LVs.

## Main Behavior
- Accepts either `VG old_lv new_lv` or `old_lv new_lv`.
- Validates consistent VG names when paths include `VG/LV`.
- Strips path prefixes from LV names.
- Detects `HISTORICAL_LV_PREFIX` on old and new names.
- Validates new LV name length, non-empty value, local restrictions, syntax, and difference from old name.
- Stores names in command memory and processes the target VG with `READ_FOR_UPDATE`.

## Rename Execution
`_lvrename_single()`:
- Finds the live LV or historical GLV.
- Rejects direct renames of RAID image/metadata LVs and RAID LVs tracking split images.
- Creates a dummy `logical_volume` for historical LVs.
- Acquires a transient exclusive lvmlockd LV lock to ensure the LV is not active elsewhere.
- Calls `lv_rename()`.
- Prints a success message with historical prefixes when applicable.

## Important Details
Historical LV support is implemented by `_historical_lv`, a static dummy logical-volume object populated before rename.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvrename.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvresize.c -->
# File Research: sources/block-storage/lvm2/tools/lvresize.c

## Purpose
Implements shared resize behavior for `lvextend`, `lvreduce`, and `lvresize` command variants.

## Parameter Setup
`_lvresize_params()` initializes `struct lvresize_params` based on the selected generated command enum. It handles:
- extend by policy,
- pool metadata extension/resizing,
- PV-based extension/resizing,
- size/extents based extend/reduce/resize,
- filesystem options from `--fs`, `--resizefs`, `--fsmode`, and `--nofsck`,
- size versus extents exclusivity,
- allocation policy, yes/force/nosync,
- segment type, mirrors, stripes, and stripesize validation.

## Filesystem Handling
With blkid filesystem info support, default behavior is `checksize`; `--resizefs` maps to `--fs resize`. Without that support, filesystem handling is restricted to `resize_fsadm`, and unsupported modes are warned or rejected.

## Policy Extension
`_lv_extend_policy()` supports snapshot COW, thin pool, and VDO pool policy extension. It requires the LV to be active, calculates data/metadata extension percentages from policy settings, skips when no extension is needed, and calls `lv_resize()`.

## Execution
- `_lvextend_policy_single()` builds optional PV lists and runs policy extension for one LV.
- `_lvresize_single()` builds optional PV lists and runs `lv_resize()`.
- `lvextend_policy_cmd()` processes exactly the target LV for policy extension.
- `lvresize_cmd()` processes the target LV, retries once if the VG changed during filesystem resize, refreshes lvmlockd state if needed, and returns the command status.
- `lvresize()` itself is an internal-error fallback because generated command definitions should dispatch to specific functions.

## Important Details
Reduce operations ignore allocation-shaping arguments because they do not allocate new space. `--type linear` is internally treated as striped with a flag requiring only one stripe.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvresize.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvscan.c -->
# File Research: sources/block-storage/lvm2/tools/lvscan.c

## Purpose
Implements `lvscan`, printing a compact listing of logical volumes.

## Main Behavior
- `lvscan()` ignores obsolete `--cache` with a warning because lvmetad is no longer used.
- Calls `process_each_lv()` with `_lvscan_single()`.
- `_lvscan_single()` skips invisible LVs unless `--all` is set.
- Checks whether the LV exists in kernel with `lv_info()`.
- For COW snapshots, checks snapshot percent and treats invalid percent as inactive.
- Prints active/inactive status, origin/snapshot label, device path, size, and allocation policy.

## Important Details
Snapshot activity is stricter than kernel presence alone because invalid snapshot usage marks the snapshot inactive for display.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvscan.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/man-generator.c -->
# File Research: sources/block-storage/lvm2/tools/man-generator.c

## Purpose
Standalone generator for LVM man pages, indexes, categories, argument reference pages, and command-definition overlap checks.

## Structure
The file defines minimal local replacements for LVM allocation/logging helpers, includes `command.h` and `command.c` under `MAN_PAGE_GENERATOR`, and operates on the generated command/option/value metadata without requiring the full LVM runtime.

## Man Page Generation
- `_print_header()` emits roff headers and helper macros.
- `_print_val_man()` renders value syntax with man-page markup.
- `_print_def_man()` renders argument definitions, constants, positional values, repeat markers, and LV-type constraints.
- `_print_man_usage()` renders each command syntax variant, including required options, any-required option groups, positionals, optional options, common options, implied autotypes, and alternate `--extents`.
- `_print_man_all_options_list_string()`, `_print_man_all_options_list()`, and `_print_man_all_options_desc()` emit option macro definitions, option summaries, and descriptions.
- `_print_man_all_positions_desc()` emits shared variable/positional documentation.
- `_print_man()` generates primary command man pages; `_print_man_secondary()` emits advanced/secondary syntax.

## Description And Metadata Handling
- `_include_description_file()` includes external description text with a 1 MiB limit.
- `_print_desc_man()` strips internal `DESC:` markers into printable description text.
- Option descriptions can contain command-specific `#cmdname` sections.
- Index metadata is read from `_meta` files with `_read_meta_field()`.

## Index Generation
- `_get_des_index_cname()` extracts dynamic command names from `*_des` filenames and command metadata.
- `_get_main_index_cname()` parses static man-page `_main` files from the `.SH NAME` section.
- `_get_index_cname()` combines meta category/conditional information with `_des`, `_main`, or built-in command metadata.
- `_print_alphabetical_index()` emits `lvm-index(7)`.
- `_print_category_index()` emits `lvm-categories(7)`.
- Optional condition markers wrap conditional index entries.

## Validation And Args Reference
- `_check_overlap()` compares command definitions for repeated or ambiguous syntax.
- `_compare_cmds()` checks required positionals and required/optional option combinations, including `--type` distinctions.
- `_print_args_man()` emits `lvm-args(7)`, listing each used option, generic description text, and commands that accept it.

## Program Modes
`main()` supports exactly one mode group:
- `--primary <command> [description-file]`
- `--secondary <command>`
- `--check`
- `--index [--with-condition-markers] files...`
- `--categories [--with-condition-markers] files...`
- `--args`

It calls `define_commands()`, factors common options, dispatches the selected mode, buffers stdout for large output, and exits success only when generation/checking succeeds.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/man-generator.c -->