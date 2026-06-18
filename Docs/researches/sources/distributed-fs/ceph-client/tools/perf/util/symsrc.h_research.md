<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symsrc.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/symsrc.h

## Purpose

`symsrc.h` defines `struct symsrc`, the abstraction used by perf to represent an opened symbol source while loading DSO symbols. It lets the generic symbol layer work with either the full libelf backend or the minimal fallback backend.

## Important APIs, Types, and Functions

`struct symsrc` always contains `name`, `fd`, and `enum dso_binary_type type`. With `HAVE_LIBELF_SUPPORT`, it also stores an `Elf *`, ELF header, `.opd`, `.symtab`, and `.dynsym` section handles, section indexes and headers, plus `adjust_symbols` and `is_64_bit` flags. The header declares `symsrc__init()`, `symsrc__destroy()`, `symsrc__has_symtab()`, and `symsrc__possibly_runtime()`.

## Control Flow and Data Flow

`dso__load()` creates one or two `symsrc` instances while scanning candidate binary paths. One source may provide the desired symbol table, while another may represent the runtime image needed for program headers, dynsym, `.opd`, or address adjustment. `dso__load_sym()` receives those sources and consumes their fields. Cleanup returns ownership of file descriptors, names, and libelf handles to the backend.

## State and Persistence Behavior

A `symsrc` is temporary per load attempt. It owns its copied `name`, open file descriptor, and, in libelf builds, the libelf handle. It does not own the DSO, maps, or inserted symbols. Backends must destroy partially initialized sources on rejected candidates.

## Dependencies and Integration Points

The header depends on `dso.h`, ELF constants, and optionally libelf/gelf. It is the shared contract between `symbol.c`, `symbol-elf.c`, and `symbol-minimal.c`.

## Risks and Edge Cases

The struct layout changes materially depending on `HAVE_LIBELF_SUPPORT`, so users must not access libelf fields without the same guard. A runtime source without `.symtab` can still be important for dynsym or address adjustment. Minimal builds report no symtab and assume every source may be runtime, which changes generic loading behavior.

## Test Signals

Build matrix tests should compile with and without libelf. Runtime tests should cover separate debug and runtime sources, `.gnu_debugdata`, sources with only dynsym, missing symtab, and cleanup after failed source initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symsrc.h -->
