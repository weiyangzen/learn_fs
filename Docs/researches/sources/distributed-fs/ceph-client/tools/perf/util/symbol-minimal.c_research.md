<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol-minimal.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol-minimal.c

## Purpose

`symbol-minimal.c` is the fallback symbol backend used when perf lacks full libelf support. It provides enough ELF parsing to identify build IDs and ELF class, but it does not load real symbol tables, debug links, maps, kcore, PLT symbols, or sections.

## Important APIs, Types, and Functions

The file implements the same external entry points expected by the generic symbol layer: `filename__read_debuglink()`, `filename__read_build_id()`, `sysfs__read_build_id()`, `symsrc__init()`, `symsrc__destroy()`, `symsrc__possibly_runtime()`, `symsrc__has_symtab()`, `dso__synthesize_plt_symbols()`, `dso__type_fd()`, `dso__load_sym()`, `file__read_maps()`, `kcore_extract__create()`, `kcore_extract__delete()`, `kcore_copy()`, `symbol__elf_init()`, and `filename__has_section()`. Internal helpers include `check_need_swap()`, `read_build_id()`, and `fd__is_64_bit()`.

## Control Flow and Data Flow

`filename__read_build_id()` opens a regular ELF file, reads `e_ident`, determines class and byte order, reads the ELF header and program headers manually, scans PT_NOTE segments, and extracts an `NT_GNU_BUILD_ID` note. `sysfs__read_build_id()` reads the whole sysfs note file and reuses the note parser without byte swapping. `symsrc__init()` merely opens the file, stores a copied name, file descriptor, and DSO binary type. `dso__load_sym()` records whether the source is 64-bit and sets the DSO build ID if one is present, then returns success with zero loaded symbols.

Unsupported capabilities return conservative failures: debuglink reading returns `-1`, `symsrc__has_symtab()` returns false, PLT synthesis returns zero, `file__read_maps()` and kcore helpers return `-1`, and `filename__has_section()` returns false.

## State and Persistence Behavior

The fallback stores only `symsrc->name`, `symsrc->fd`, and `symsrc->type`, and may persist a build ID plus `is_64_bit` on the DSO. It does not persist symbols into DSO rb-trees. `symsrc__destroy()` frees the copied name and closes the descriptor.

## Dependencies and Integration Points

It depends only on standard file IO, ELF headers, byte-swap helpers, `is_regular_file()`, `readn()`, and DSO accessors. It integrates with `symbol.c` by satisfying link-time symbols when libelf support is absent, allowing perf to keep build-id and binary-class behavior even though symbolization is degraded.

## Risks and Edge Cases

Manual ELF parsing is intentionally limited. Cross-endian handling mutates note header words in the input buffer, so callers should not reuse that buffer as raw data. The 32-bit program-header swap path assigns `p_filesz` from the swapped `p_offset`, which looks suspicious and should be regression-tested on cross-endian 32-bit files. Since `symsrc__has_symtab()` is always false, generic symbol loading may mark DSOs loaded with no usable symbols. Missing debuglink, kcore, section, and map support are expected limitations rather than runtime errors.

## Test Signals

Build tests should exercise perf with libelf disabled. Unit tests should feed 32-bit and 64-bit ELF files with PT_NOTE build IDs, no build ID, invalid magic, short headers, non-regular files, and sysfs-style note data. Integration tests should verify `dso__load()` does not crash but yields no symbols, while build IDs and 32/64-bit DSO type still propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol-minimal.c -->
