# sources/distributed-fs/ceph-client/scripts/generate_initcall_order.pl

## Purpose
Generates a linker script fragment that preserves deterministic kernel initcall ordering after LTO or archive aggregation by discovering `__initcall__...` symbols in object files and emitting ordered `SECTIONS` entries.

## APIs, Control Flow, and State
The script is a Perl host-build tool driven by `NM`, `objtree`, optional `PARALLELISM`, and command-line object paths. `process_files()` forks bounded child workers, each running `find_initcalls()` against `$objtree/$file`. Children parse `nm --defined-only` output, detect archive member boundaries, collect initcall records keyed by the compiler counter embedded in symbol names, and stream `<file-index> <level> <section-name>` lines to the parent. `wait_for_results()` uses `IO::Select` and `waitpid(WNOHANG)` to drain child pipes without deadlocking. `generate_initcall_lds()` reorders child results by input object index, groups by initcall level, and prints linker script sections such as `.initcall0.init` and `.con_initcall.init`.

## Dependencies and Integration
It integrates with kbuild linker-script generation and depends on GNU-compatible `nm`, Perl `IO::Handle`, `IO::Select`, and POSIX wait APIs. Its state is in-memory only: active child filehandles in `%$jobs` and collected records in `%$results`.

## Risks and Test Signals
The output is sensitive to exact symbol naming (`__initcall__module__counter_line_functionlevel`), input object ordering, archive formatting from `nm`, and child stdout protocol correctness. Test signals are a successful non-empty linker script, stable ordering for repeated object lists, failure on malformed child output, and failure on missing `NM` or empty initcall sets.
