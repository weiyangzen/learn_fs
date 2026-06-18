<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_fprintf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol_fprintf.c

## Purpose

`symbol_fprintf.c` contains small formatting helpers for printing perf symbols and symbol names to `FILE` streams. It keeps textual symbol output separate from symbol loading and lookup logic.

## Important APIs, Types, and Functions

`symbol__fprintf()` prints a symbol range, binding character, and name. `__symbol__fprintf_symname_offs()` prints a symbol name, optional offset, unknown address, or `[unknown]`. `symbol__fprintf_symname_offs()`, `__symbol__fprintf_symname()`, and `symbol__fprintf_symname()` are convenience wrappers. `dso__fprintf_symbols_by_name()` prints the DSO's sorted symbol-name array.

## Control Flow and Data Flow

The formatters receive already-resolved `struct symbol`, optional `struct addr_location`, and a destination `FILE`. Offset calculation uses `al->addr - sym->start` when the address is inside the symbol, or falls back to map-relative calculation when the sampled address is beyond `sym->end`. Binding characters are rendered as `g`, `l`, or `w` for global, local, or other/weak.

## State and Persistence Behavior

The functions do not allocate persistent state. They read symbol fields, map start, DSO sorted symbol-name arrays, and write bytes to the provided stream. The return value is the number of bytes reported by `fprintf()` accumulation.

## Dependencies and Integration Points

The file depends on ELF binding constants, `dso.h`, `map.h`, and `symbol.h`. It is used by debugging, reporting, and tests that need stable textual representations of symbols or symbol-name tables.

## Risks and Edge Cases

Callers must ensure `dso__sort_by_name()` has run before using `dso__fprintf_symbols_by_name()` if sorted names are expected. Offset formatting assumes the `addr_location` map is valid when an address is outside the symbol range. The binding display collapses all non-global and non-local values to `w`, which may be imprecise for unusual ELF bindings.

## Test Signals

Tests should check exact output for global/local/weak symbols, null symbol with `unknown_as_addr` true and false, offset printing inside a symbol, offset printing through a map-relative address, and printing a DSO sorted-name table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_fprintf.c -->
