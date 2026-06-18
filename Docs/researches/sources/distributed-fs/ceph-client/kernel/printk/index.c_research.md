# sources/distributed-fs/ceph-client/kernel/printk/index.c

## Purpose

`index.c` implements the userspace-visible printk format index under debugfs. It exposes compile-time collected `struct pi_entry` records for vmlinux and loaded modules so tools can inspect printk callsite metadata and format strings without scanning binary text.

## Important APIs and functions

- `pi_get_entry(const struct module *mod, loff_t pos)` selects either module `printk_index_start/size` metadata or vmlinux linker symbols `__start_printk_index` and `__stop_printk_index`.
- `pi_start()`, `pi_next()`, `pi_show()`, and `pi_stop()` implement a `seq_file` iterator.
- `pi_show()` prints a header, parses embedded log-level prefixes with `printk_parse_prefix()`, emits continuation markers, and escapes format strings with `seq_escape_str()`.
- `pi_create_file()` creates one debugfs file per module name, with `vmlinux` used for built-in entries.
- `pi_module_notify()` adds a file at `MODULE_STATE_COMING` and removes it at `MODULE_STATE_GOING`.
- `pi_init()` creates `debugfs/printk/index`, registers the module notifier, and creates the vmlinux file via `postcore_initcall()`.

## Control flow and state

At postcore init, the file creates a debugfs root directory named `printk`, an `index` child, then exposes the built-in index. When modules are enabled, the notifier mirrors module lifetime by adding and removing per-module debugfs files. Reads are lazy: seq_file uses the file inode private pointer as the module key and indexes entries by file position. The only owned persistent state is `dfs_index`, the debugfs dentry for the index directory, and the module notifier object. Actual printk index entries live in linker sections or module metadata.

## Dependencies and integration points

This file depends on debugfs, seq_file helper macros, module notifier infrastructure, `struct pi_entry`, linker section symbols, and `printk_parse_prefix()` from `printk.c`. The output format is `# <level/flags> filename:line function "format"` followed by one row per indexed callsite. It understands separate `entry->level`, inline printk prefixes in `entry->fmt`, `LOG_CONT`, and optional `entry->subsys_fmt_prefix`.

## Risks and test signals

Debugfs creation failures are not checked. Module file lifetime relies on notifier ordering and debugfs lookup/removal by module name. Format escaping must stay correct for quotes and backslashes. Enable `CONFIG_PRINTK_INDEX`, inspect `/sys/kernel/debug/printk/index/vmlinux`, load and unload a module containing printk calls, and include callsites with continuation markers, explicit log levels, subsystem prefixes, quotes, and backslashes.
