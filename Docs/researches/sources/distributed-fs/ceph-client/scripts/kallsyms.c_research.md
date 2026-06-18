# sources/distributed-fs/ceph-client/scripts/kallsyms.c

## Purpose
Converts a linker map into assembly data tables used by the kernel `kallsyms` runtime for compressed symbol lookup.

## APIs, Control Flow, and State
`main()` parses `--all-symbols` and `--pc-relative`, reads the map with `read_map()`, prunes invalid symbols with `shrink_table()`, sorts by address, optimizes the token table, and writes assembly. `read_symbol()` parses `addr type name`, ignores undefined/debug/most absolute symbols, tracks text/inittext ranges, and stores type plus name in `struct sym_entry`. `symbol_valid()` filters to text ranges unless all symbols are requested, preserving `__start_`/`__stop_`. Compression counts two-byte token profit, inserts real byte codes, repeatedly selects profitable tokens, rewrites symbols, and emits compressed names, markers, token tables, offsets, and name-order sequence tables.

## Dependencies and Integration
It depends on libc, `xalloc.h`, linker map format, kernel symbol range conventions, and assembly syntax expected by the kernel build. Persistent output is generated assembly on stdout.

## Risks and Test Signals
Risks include map format drift, symbol length limit mismatches with the kernel, address truncation when not PC-relative, relative offset overflow, and compression table regressions. Test signals are successful boot/runtime symbol lookup, stable table generation across kallsyms passes, and explicit failure on overlong symbols or out-of-range relative addresses.
