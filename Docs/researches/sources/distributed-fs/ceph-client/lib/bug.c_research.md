# sources/distributed-fs/ceph-client/lib/bug.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bug.c` provides generic BUG/WARN table handling for architectures that emit `__bug_table` entries. It finds bug metadata for trap addresses, reports warnings or fatal bugs, manages module bug tables, and resets one-shot warning state.

## Important APIs, Types, and Functions

Important functions include `module_bug_finalize`, `module_bug_cleanup`, `bug_get_file_line`, `find_bug`, `report_bug_entry`, `report_bug`, and `generic_bug_clear_once`. Internal helpers include `bug_addr`, `module_find_bug`, `bug_get_format`, `__warn_printf`, `__report_bug`, and `clear_once_table`. The file consumes linker symbols `__start___bug_table` and `__stop___bug_table` plus optional module `bug_table` metadata.

## Control Flow

Module load scans ELF section names for `__bug_table`, records the table in `struct module`, and links the module onto an RCU-protected list. Trap handling enters warning RCU context, resolves the `struct bug_entry` either directly or by address, validates arch bug addresses, decodes file/line and optional format strings, handles `BUGFLAG_ONCE` by setting `BUGFLAG_DONE`, emits the cut-here line and warning text when appropriate, then calls `__warn()` for warnings or prints a critical BUG location. Clear-once walks built-in and module tables to clear `BUGFLAG_DONE`.

## State and Persistence Behavior

Built-in bug entries live in the kernel image. Module bug tables live for the module lifetime and are tracked in `module_bug_list` under RCU. `BUGFLAG_DONE` mutates bug entries to suppress repeated one-shot warnings until `generic_bug_clear_once()`.

## Dependencies and Integration Points

The file integrates with architecture trap handlers through `report_bug()`, module loader finalization/cleanup, RCU list traversal, ftrace warning disabling, context tracking around warnings, and optional architecture format argument extraction. It depends on config-controlled `struct bug_entry` layout, relative pointer decoding, and arch `is_valid_bugaddr()`.

## Risks and Edge Cases

Relative pointer decoding, verbose/non-verbose layouts, and optional format argument extraction are ABI-sensitive. Reporting paths intentionally avoid normal locks because BUG handling can run in fragile contexts. Module unload races rely on RCU discipline. A stale or invalid trap address must return `BUG_TRAP_TYPE_NONE` rather than misreporting.

## Test Signals

Signals include arch trap tests for WARN, WARN_ON_ONCE, BUG, invalid bug addresses, verbose and non-verbose builds, module load/unload with `__bug_table`, `generic_bug_clear_once()` re-enabling one-shot warnings, and format-string WARN paths with and without arch argument extraction.

## Read Coverage

Source read size: 305 lines, 7498 bytes.
