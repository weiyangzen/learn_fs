<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module.h -->
# sources/distributed-fs/ceph-client/include/linux/module.h

## Purpose
`module.h` is the main public kernel header for loadable module metadata, lifecycle entry points, module state, module memory layout, symbol access, reference management, sysfs/kallsyms integration, taint/signature state, and feature sections.

## Important APIs, Types, and Functions
It defines `MODULE_NAME_LEN`, `struct modversion_info`, `struct module_kobject`, `struct module_attribute`, `struct module_version_attribute`, `module_init()`, `module_exit()`, initcall aliases for modules, `MODULE_ALIAS`, `MODULE_SOFTDEP`, `MODULE_WEAKDEP`, `MODULE_FILE`, `MODULE_LICENSE`, `MODULE_AUTHOR`, `MODULE_DESCRIPTION`, `MODULE_DEVICE_TABLE`, `MODULE_VERSION`, `MODULE_FIRMWARE`, and `MODULE_IMPORT_NS`.

Core state types include `enum module_state`, `struct mod_tree_node`, `enum mod_mem_type`, `struct module_memory`, `struct mod_kallsyms`, optional `struct klp_modinfo`, and the large `struct module`. `struct module` tracks state, list membership, name, build ID, sysfs objects, exported symbols, parameter arrays, signature status, init function, memory regions, arch data, taints, exception tables, kallsyms, per-CPU storage, trace/BPF/debug/livepatch/KUnit/static-call/FTRACE data, unload dependency lists, exit callback, refcount, constructors, error injection, and dynamic debug data.

Runtime APIs include `__symbol_get()`, `__symbol_get_gpl()`, `symbol_get()`, `kallsyms_symbol_value()`, `module_is_live()`, `module_is_coming()`, `__module_text_address()`, `__module_address()`, `is_module_address()`, `is_module_percpu_address()`, `within_module_mem_type()`, `within_module_core()`, `within_module_init()`, `within_module()`, `find_module()`, `try_module_get()`, `module_put()`, `__module_get()`, `module_name()`, `module_buildid()`, `dereference_module_function_descriptor()`, module notifiers, `print_modules()`, `module_requested_async_probing()`, `is_livepatch_module()`, and kallsyms lookup functions.

## Control Flow and State
For built-ins, `module_init()` maps to initcall sections and `module_exit()` maps to an exitcall that is discarded for non-modular use. For modules, `module_init()` and `module_exit()` alias driver functions to `init_module` and `cleanup_module`. Loading moves `struct module` through `UNFORMED`, `COMING`, and `LIVE`; unloading moves it toward `GOING`, checks reference counts, runs exit callbacks, removes sysfs/kallsyms/trace state, and frees memory.

Symbol access flows through exported symbol metadata and optional GPL-only enforcement. Address lookup flows through module memory regions and optional tree lookup. Config-disabled paths provide stubs so code compiles when modules or kallsyms are absent.

## State and Persistence Behavior
Module state is runtime kernel state, surfaced through sysfs, kallsyms, proc/debug interfaces, taint flags, and module lists. Module metadata persists in the `.ko` ELF and `.modinfo` sections; runtime `struct module` data persists while the module is loaded.

## Dependencies and Integration Points
The header integrates with kobjects/sysfs, module parameters, ELF, export symbols, kallsyms, exception tables, livepatch, tracepoints, SRCU, BPF events, BTF, jump labels, ftrace, kprobes, static calls, KUnit, printk indexing, constructors, module signatures, retpoline checks, and architecture-specific module layout.

## Risks
Module lifetime is sensitive: missing `module_put()` leaks or blocks unload, while using module memory after `GOING` risks UAF. Metadata macros affect build output and autoloading. `struct module` layout is highly config-dependent. GPL-only symbol enforcement and signature state are policy-critical. Address lookup must handle init memory that can be freed after initialization.

## Test Signals
Load/unload modules repeatedly, exercise dependency/refcount paths, verify sysfs attributes and parameters, inspect kallsyms/address lookup, test signature enforcement configs, build without `CONFIG_MODULES`, run livepatch and tracing module tests, and compile representative drivers using `MODULE_DEVICE_TABLE()` and metadata macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module.h -->
