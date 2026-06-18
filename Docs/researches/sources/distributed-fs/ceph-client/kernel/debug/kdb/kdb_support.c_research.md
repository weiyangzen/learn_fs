# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_support.c

## Purpose
This file provides KDB's shared support routines for symbol lookup/printing, symbol completion, debugger-safe memory access, physical memory reads, string duplication, and task-state formatting.

## Important APIs, Types, And Functions
`kdbgetsymval()` resolves exact symbols through kallsyms. `kdbnearsym()` resolves nearest symbols and fills `kdb_symtab_t`. `kallsyms_symbol_complete()` and `kallsyms_symbol_next()` support tab completion. `kdb_symbol_print()` formats addresses with optional symbol/module/offset metadata. `kdb_strdup()` and `kdb_strdup_dequote()` allocate KDB-owned strings. `kdb_getarea_size()`, `kdb_putarea_size()`, `kdb_getphysword()`, `kdb_getword()`, and `kdb_putword()` implement safe memory access. `kdb_task_state_char()` and `kdb_task_state()` format/filter tasks for `ps`/backtrace commands.

## Control Flow
Symbol lookup zeroes the result, queries kallsyms, and suppresses absurd nearest-symbol offsets. Completion walks kallsyms to count matches and extend the prefix to the longest common prefix. Memory reads and writes use `copy_from_kernel_nofault()` and `copy_to_kernel_nofault()`, setting `KDB_STATE(SUPPRESS)` after the first bad-address message. Physical reads validate PFNs and temporarily map pages with `kmap_local_page()`. Task state maps idle tasks to `-` when appropriate and sleeping kernel daemons to lowercase state characters.

## State, Persistence, And Dependencies
State is limited to static kallsyms completion buffers and KDB suppress/debug flags. No persistent storage exists. Dependencies include kallsyms walking, nofault copy helpers, highmem mapping, page/PFN helpers, scheduler state, `kgdb_info`, and private KDB formatting constants.

## Integration Points
`kdb_main.c` uses these helpers for address parsing, memory display/modify, process listing, per-CPU display, and diagnostics. `kdb_io.c` uses completion helpers. Other KDB commands can use the exported symbol and memory helpers.

## Risks
`kdbnearsym()` uses a static name buffer and relies on KDB's single-master execution model. Physical reads assume the requested width does not cross problematic boundaries. Bad-address suppression avoids log spam but may hide repeated faults after the first message until a successful access clears it. `kdb_putword()` can write arbitrary kernel memory when permissions allow it.

## Test Signals
Test exact and nearest symbol lookup, tab completion with no/one/many matches, bad virtual and physical addresses, 1/2/4/8-byte reads and writes, highmem physical reads, task filters with idle/system-daemon states, and `md`/`mm` callers under `KDB_STATE(SUPPRESS)`.
