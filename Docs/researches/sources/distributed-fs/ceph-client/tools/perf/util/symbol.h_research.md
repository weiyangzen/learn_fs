<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol.h

## Purpose

`symbol.h` defines perf's core symbol data type and the public interface for DSO symbol loading, lookup, formatting, kernel/kcore support, symbol-source helpers, filters, architecture hooks, and SDT note handling.

## Important APIs, Types, and Functions

`struct symbol` is an rb-tree node with `[start, end)` address range, name length, ELF type and binding bitfields, flags for idle/ignore/inlined/annotate2/ifunc alias, an architecture-specific byte, and a flexible name. `symbol__size()` returns range size, and `symbol__priv()` retrieves caller-reserved private storage before the symbol.

The header declares DSO loaders (`dso__load()`, `dso__load_vmlinux()`, `dso__load_vmlinux_path()`, `dso__load_kallsyms()`), symbol insertion/lookup APIs, build-id/debuglink readers, module parsing, initialization/exit/configuration functions, ELF backend hooks, PLT synthesis, demangling, symbol fixups, file map reading, kcore extraction/copying, filter setup helpers, architecture name-comparison hooks, and SDT note APIs. It defines `struct ref_reloc_sym`, `struct kcore_extract`, `mapfn_t`, `enum symbol_tag_include`, `struct sdt_note`, SDT section constants, and SDT address indexes.

## Control Flow and Data Flow

Users include this header to allocate or load symbols into `struct dso`, then resolve instruction pointers through DSO lookup functions or print symbol names with optional offsets. Loader declarations bridge the generic symbol layer to binary-specific backends and kernel-specific kallsyms/kcore flows. Architecture hooks allow weak defaults in `symbol.c` to be overridden for name normalization, symbol comparison, and symbol update.

## State and Persistence Behavior

The header exposes mutable global `vmlinux_path` and `vmlinux_path__nr_entries`, plus all stateful APIs that mutate DSOs, maps, symbol trees, build IDs, kcore temporary files, and global `symbol_conf` from `symbol_conf.h`. `struct kcore_extract` tracks a temporary extract path and descriptor that must be cleaned with `kcore_extract__delete()`.

## Dependencies and Integration Points

It depends on Linux rb-tree/list/refcount/types, stdio, errno, ELF definitions, `addr_location`, `path`, `symbol_conf`, `spark`, and perf utility headers. It is included by symbol loaders, report/annotate code, event synthesis, map handling, and probe/SDT code.

## Risks and Edge Cases

`struct symbol` uses a flexible-array name and optional prefix private storage, so allocation and deletion must go through `symbol__new()` and `symbol__delete()`. Address semantics are half-open ranges except zero-sized symbols can match exactly at `start`. Callers must not assume full libelf functionality because the minimal backend provides many stubs. Weak architecture hooks can change behavior across builds.

## Test Signals

Compile tests should cover both libelf and minimal builds. ABI-oriented tests should verify symbol private storage alignment, rb-tree iteration macros, `symbol__size()` behavior, SDT note constants, and that users can call loader/formatter APIs with only forward declarations for DSO/map-related types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.h -->
