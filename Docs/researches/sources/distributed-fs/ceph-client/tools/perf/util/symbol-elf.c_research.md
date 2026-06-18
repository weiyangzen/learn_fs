<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol-elf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol-elf.c

## Purpose

`symbol-elf.c` is perf's full libelf-backed symbol source implementation. It reads ELF files, compressed kernel modules, mini debug data, build IDs, debug links, symbol tables, dynamic symbol tables, PLT entries, program headers, kcore images, and SystemTap SDT notes. It is the high-capability backend behind symbol loading when perf is built with libelf support.

## Important APIs, Types, and Functions

Important exported functions include `elf_section_by_name()`, `filename__has_section()`, `filename__read_build_id()`, `sysfs__read_build_id()`, `filename__read_debuglink()`, `symsrc__init()`, `symsrc__destroy()`, `symsrc__has_symtab()`, `symsrc__possibly_runtime()`, `dso__load_sym()`, `dso__synthesize_plt_symbols()`, `file__read_maps()`, `dso__type_fd()`, `kcore_copy()`, `kcore_extract__create()`, `kcore_extract__delete()`, `get_sdt_note_list()`, `cleanup_sdt_note_list()`, `sdt_notes__get_count()`, and `symbol__elf_init()`.

Key internal structures are `struct rel_info` for `.rel.plt` or `.rela.plt`, `struct rela_dyn_info` for x86 `.plt.got`, `struct kcore` and `struct kcore_copy_info` for creating smaller kcore files, and `struct sdt_note` from `symbol.h` for parsed SDT probes. `struct symsrc` from `symsrc.h` is populated with libelf handles, section handles, section headers, ELF header, symbol table metadata, and adjustment flags.

## Control Flow and Data Flow

`symsrc__init()` opens or decompresses a file, begins libelf reading, optionally expands `.gnu_debugdata`, validates build IDs when the DSO already has one, records ELF class and relevant sections, and decides whether symbols need address adjustment. `dso__load_sym()` then loads `.symtab`, `.dynsym`, and in the `.gnu_debugdata` case runtime dynsym entries. The internal loader filters functions, objects, and selected labels; rejects ARM/AArch64/RISC-V mapping symbols; handles PPC64 `.opd`; resolves section names; adjusts kernel, module, VDSO, ET_EXEC, ET_REL, and ET_DYN symbol addresses; demangles names; inserts symbols into DSO rb-trees; and finally fixes zero-sized symbols and duplicates.

PLT synthesis starts with `.plt`, finds relocation and symbol-string sections, handles architecture-specific PLT header and entry sizes, optionally names x86 `.plt.got` and `.plt.sec` entries, recognizes IFUNC relocations, demangles target names, and inserts synthetic `@plt` function symbols.

Build-id and debuglink flows read ELF note sections or sysfs note streams, with libbfd helpers tried first when available. `file__read_maps()` iterates PT_LOAD program headers and calls a caller-provided `mapfn_t`. Kcore flows parse copied `kallsyms` and `modules`, calculate executable kernel/module ranges, write a compact ELF kcore with selected PT_LOAD segments, and verify kallsyms stability. SDT flows parse `.note.stapsdt`, translate note addresses, adjust prelink/base/refctr offsets, and return an allocated note list.

## State and Persistence Behavior

The primary state mutations are on `struct dso`, `struct map`, and `struct maps`: symbol rb-trees are populated, build IDs and binary types are set, map starts/ends/pgoffs can be rewritten, kernel maps can be split, and DSO long names can point to kcore paths. Temporary state includes open file descriptors, libelf handles, decompressed module files, temporary `.gnu_debugdata` files, and temporary extracted kcore files under `/tmp/perf-kcore-XXXXXX`. `kcore_copy()` persists copied `kallsyms`, `modules`, and a reduced `kcore` under the destination directory. Callers own cleanup of SDT lists and kcore extracts.

## Dependencies and Integration Points

This file depends on libelf/gelf, optional libbfd, compression helpers, Linux ELF constants, perf `dso`, `map`, `maps`, `machine`, `vdso`, `build-id`, kallsyms parsing, namespace-aware path handling in higher layers, and internal copy/decompression utilities. It integrates with `symbol.c` through the `symsrc` and `dso__load_sym()` interfaces and with perf probe/trace tooling through SDT note discovery.

## Risks and Edge Cases

ELF files may be truncated, stripped, compressed, cross-endian, prelinked, relocated, or have missing section-string data. Kernel and module symbol adjustment is architecture-sensitive and can corrupt map layout if reference relocation symbols or section offsets are wrong. PLT synthesis relies on relocation ordering, entry sizes, and x86 instruction decoding for `.plt.got`; IFUNC handling is especially subtle. Kcore copying races with module load/unload and requires readable `/proc/kcore`, which may require `CAP_SYS_RAWIO`. Temporary files under `/tmp` must be unlinked on error paths. SDT note parsing must reject malformed notes without leaking partially allocated strings.

## Test Signals

Tests should load symbols from ordinary ET_DYN shared libraries, ET_EXEC binaries, stripped files with dynsym only, files with `.gnu_debuglink`, `.gnu_debugdata`, compressed kernel modules, VDSO, and vmlinux. PLT tests should verify generated `.plt`, `.plt.got`, `.plt.sec`, and IFUNC `@plt` names on x86 and basic entry sizing on ARM/AArch64/RISC-V/LoongArch/Sparc. Kcore tests need copied module/kallsyms stability checks and permission-denied behavior for `/proc/kcore`. SDT tests should parse known `.note.stapsdt` notes and confirm cleanup count. Build-id tests should cover ELF notes, sysfs notes, compressed modules, mismatches, and missing notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol-elf.c -->
