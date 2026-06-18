# sources/distributed-fs/ceph-client/kernel/debug/kdb/Makefile

## Purpose
This Makefile builds the KDB frontend objects and generates `gen-kdb_cmds.c` from the textual `kdb_cmds` file. It is used when the parent debugger Makefile descends into `kernel/debug/kdb/`.

## Important APIs, types, and functions
There are no runtime APIs. Build objects are `kdb_io.o`, `kdb_main.o`, `kdb_support.o`, `kdb_bt.o`, `gen-kdb_cmds.o`, `kdb_bp.o`, and `kdb_debugger.o`, with optional `kdb_keyboard.o` under `CONFIG_KDB_KEYBOARD`. `clean-files := gen-kdb_cmds.c` marks the generated source for cleanup.

The `cmd_gen-kdb` AWK rule emits C strings from non-comment, non-empty `kdb_cmds` lines and builds an `__initdata` `kdb_cmds[]` array.

## Control flow
Kbuild compiles the listed KDB objects. When `gen-kdb_cmds.c` is needed, the rule reads `$(src)/kdb_cmds` and the Makefile, escapes quotes, emits one static string per command line, and emits a NULL-terminated `kdb_cmds` pointer array.

## State and persistence behavior
The only persistent artifact is generated build output `gen-kdb_cmds.c`, which is cleaned by Kbuild. The Makefile has no runtime state.

## Dependencies and integration points
It depends on Kbuild, AWK, `kdb_cmds`, KDB source files, and `CONFIG_KDB_KEYBOARD`. The generated command table is consumed by KDB initialization.

## Risks and edge cases
The AWK generator skips comments and blank lines and escapes quotes; malformed command lines in `kdb_cmds` become embedded strings and may fail later at KDB parse time. Missing AWK or stale generated output would break KDB builds. The dependency includes the Makefile itself so generator changes rebuild the source.

## Test signals
Build KDB with and without keyboard support, inspect regenerated `gen-kdb_cmds.c`, run clean targets, and boot KDB to verify built-in commands from `kdb_cmds` are registered.
