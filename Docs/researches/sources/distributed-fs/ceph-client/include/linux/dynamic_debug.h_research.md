# sources/distributed-fs/ceph-client/include/linux/dynamic_debug.h

## Purpose
This header implements the compile-time and runtime callsite metadata interface for dynamic debug. It places descriptors and class maps in special ELF sections, then wraps debug print calls in runtime flags or jump-label branches.

## Important APIs, types, and functions
`struct _ddebug` describes a callsite with module, function, file, format, line, class ID, flags, and optional static key. Flag bits control printing and whether module/function/line/TID/source/stack are included. `enum class_map_type`, `struct ddebug_class_map`, `DECLARE_DYNDBG_CLASSMAP()`, `struct _ddebug_info`, and `struct ddebug_class_param` support class-based debug controls.

When dynamic debug is enabled, exported functions include `__dynamic_pr_debug()`, `__dynamic_dev_dbg()`, `__dynamic_netdev_dbg()`, and `__dynamic_ibdev_dbg()`. Macros such as `DEFINE_DYNAMIC_DEBUG_METADATA_CLS()`, `dynamic_pr_debug_cls()`, `dynamic_pr_debug()`, `dynamic_dev_dbg()`, `dynamic_netdev_dbg()`, `dynamic_ibdev_dbg()`, and `dynamic_hex_dump()` create metadata and conditionally call print functions. Module parameter hooks are `ddebug_dyndbg_module_param_cb()`, `param_set_dyndbg_classes()`, `param_get_dyndbg_classes()`, and `param_ops_dyndbg_classes`.

## Control flow, state, and persistence
Each debug macro creates a static `_ddebug` descriptor in `__dyndbg`; class maps go into `__dyndbg_classes`. Runtime control changes descriptor flags and optional static keys through debugfs/module parameters. The branch path is static-key backed when jump labels are available, or flag-checked otherwise. If dynamic debug is disabled, macros compile to `no_printk()` or dead code while retaining format checking.

## Dependencies and integration points
It depends on jump labels when enabled, build bug checks, module metadata, debugfs control infrastructure, printk/device/netdev/ibdev debug routines, and kernel parameter ops. It integrates with `pr_debug()`, device debug wrappers, and subsystem-specific class controls.

## Risks and test signals
Risks include format string duplication in macros, class ID overflow, static-key state desynchronization, stack dump overhead when enabled, and control file parsing errors. Tests should cover compile-time format checking in disabled builds, enabling/disabling callsites through dynamic_debug/control, class-map parameter parsing, jump-label branch toggling, and no-op behavior when only core support is absent.
