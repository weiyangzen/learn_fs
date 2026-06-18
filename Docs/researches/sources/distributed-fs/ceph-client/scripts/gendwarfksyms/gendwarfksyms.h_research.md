# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.h

## Purpose
`gendwarfksyms.h` defines shared state, diagnostics, type declarations, and cross-module APIs for the `gendwarfksyms` utility.

## Important APIs, Types, and Functions
It declares global flags, diagnostic macros, check macros, DWARF tag aliases, `SYMBOL_PTR_PREFIX`, symbol state/types, DIE state/fragments, the generic cache, expansion/kABI processing state, and public functions from `symbols.c`, `die.c`, `cache.c`, `dwarf.c`, `types.c`, and `kabi.c`.

## Control Flow
The header does not execute control flow, but its macros standardize error handling: `error()` exits, `warn()` reports, and `check()`/`checkp()` turn nonzero or negative results into fatal errors.

## State and Persistence Behavior
It defines the contracts for global process state: symbol maps, DIE maps, caches, expansion state, and kABI rule maps.

## Dependencies and Integration Points
It includes DWARF/libdwfl/libelf-facing headers and kernel host helpers (`hash.h`, `hashtable.h`, `xalloc.h`), making it the central interface for all C files in the directory.

## Risks and Test Signals
Macro names can shadow variables, especially `debug`. Enum bounds must match cleanup/stat loops. Test by compiling with warnings and running all example modes to exercise each declared API.
