# sources/distributed-fs/ceph-client/lib/dynamic_debug.c

## Purpose
Implements Linux dynamic debug control for runtime-enabling `pr_debug()`, `dev_dbg()`, network-device debug, and InfiniBand-device debug callsites. It maintains global per-module tables of `_ddebug` descriptors, parses boot/module/control-file commands, applies flag changes to matching callsites, and exposes the configured callsites through `/proc/dynamic_debug/control` and debugfs `dynamic_debug/control`.

## Important APIs, Types, and Functions
Key internal types are `struct ddebug_table` for one module's descriptor range and class maps, `struct ddebug_query` for parsed match criteria, `struct ddebug_iter` for seq-file traversal, and `struct flag_settings` for parsed flag operations. Public/exported APIs include `__dynamic_pr_debug()`, `__dynamic_dev_dbg()`, `__dynamic_netdev_dbg()` under `CONFIG_NET`, `__dynamic_ibdev_dbg()` under InfiniBand, `param_set_dyndbg_classes()`, `param_get_dyndbg_classes()`, and `param_ops_dyndbg_classes`.

The query path is centered on `ddebug_exec_queries()`, `ddebug_exec_query()`, `ddebug_tokenize()`, `ddebug_parse_query()`, `ddebug_parse_flags()`, and `ddebug_change()`. `ddebug_change()` matches module, filename, function, format, line range, and optional class string, then mutates `dp->flags`; when jump labels are enabled it also toggles the descriptor's static branch for `_DPRINTK_FLAGS_PRINT`.

Module lifecycle support comes from `ddebug_add_module()`, `ddebug_attach_module_classes()`, `ddebug_remove_module()`, and `ddebug_module_notify()`. Boot/control setup is in `dynamic_debug_init()`, `dynamic_debug_init_control()`, `dyndbg_setup()`, `ddebug_dyndbg_boot_param_cb()`, and `ddebug_dyndbg_module_param_cb()`.

## Control Flow
At early init, `dynamic_debug_init()` registers the module notifier, walks linker-provided `__dyndbg` and `__dyndbg_classes` sections, groups descriptors by module name, adds a `ddebug_table` per module, and re-parses `saved_command_line` for `dyndbg` parameters after the tables exist. Later `dynamic_debug_init_control()` creates debugfs and procfs control files when initialization succeeded.

Writes to the control file are copied with `memdup_user_nul()`, split on semicolons/newlines, tokenized with simple whitespace/quote handling, parsed into query criteria plus a final flag operation, and applied across all registered tables under `ddebug_lock`. Reads use seq-file callbacks to hold `ddebug_lock`, iterate every descriptor in reverse index order per table, and format `filename:lineno [module]function =flags "format"` plus class metadata.

Class-param updates turn bitmaps or levels into synthesized `class <name> +/-<flags>` dynamic-debug commands. For named maps, comma-separated class names toggle bits or level thresholds; for numeric maps, input is parsed as a bitmask or level number.

## State and Persistence
Persistent runtime state is in static globals: `ddebug_tables`, `ddebug_lock`, `verbose`, and `ddebug_init_success`. Per-callsite state persists in the linker/module `_ddebug` descriptor array through its `flags` field and optional jump-label branch state. Per-class kernel parameters persist in caller-owned `ddebug_class_param` `bits` or `lvl` storage, while `ddebug_table` objects are allocated for built-in/module descriptor ranges and freed on module unload.

The control files are runtime views, not durable storage. Boot parameters and module parameters apply at initialization or load time but subsequent control-file changes live only until reboot/module unload.

## Dependencies and Integration Points
Depends on kernel module metadata, linker sections, debugfs, procfs, seq_file, sysctl/moduleparam parsing, `linux/dynamic_debug.h`, string matching helpers, optional jump labels, and device/net/InfiniBand logging APIs. Integration points include the dynamic-debug macros that emit `_ddebug` descriptors, module notifier hooks, kernel command line parsing, module parameter callbacks, and class maps declared by other modules.

## Risks
The parser is intentionally simple: it supports basic quoting but no escaping inside quotes, caps commands at one page, and accepts a fixed maximum word count. Query operations are global and can touch many descriptors under `ddebug_lock`, so expensive wildcard/format searches may hold the mutex for noticeable time on large systems. Class-map state can drift from direct control-file edits because `param_get_dyndbg_classes()` reports the last parameter state rather than re-deriving all callsite flags. Jump-label toggling must stay synchronized with `_DPRINTK_FLAGS_PRINT`; regressions would affect disabled-callsite fast paths. Module removal compares `dt->mod_name == mod_name`, relying on module-name pointer lifetime/identity described in the allocation comment.

## Test Signals
Useful signals include booting with `dyndbg=` and `$module.dyndbg=`, echoing valid/invalid queries into both debugfs and procfs control files, verifying seq-file output escaping and class display, loading/unloading modules with `_ddebug` descriptors, toggling class parameters for all map types, and checking jump-label/static-branch state changes under `CONFIG_JUMP_LABEL`. Negative tests should cover bad flags, duplicate match-specs, malformed line ranges, unknown class names, too-long writes, and no-match queries.
