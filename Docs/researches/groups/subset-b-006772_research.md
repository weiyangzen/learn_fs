# subset-b-006772 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c

## Purpose

`svghelper.c` implements the low-level SVG writer used by perf timeline-style tools. It converts perf timestamps, CPU slots, scheduler states, frequency states, wakeups, interrupt points, and IO spans into SVG rectangles, lines, circles, text, titles, and descriptions. The file is not a general SVG library; it is a stateful renderer with fixed layout constants and perf-specific assumptions about nanosecond timestamps, CPU topology, and timeline rows.

## Important APIs, Types, and Functions

The public entry points are declared in `svghelper.h`. `open_svg()` opens the output file, initializes `first_time`, `last_time`, page width, total height, and CSS classes. `svg_close()` terminates and closes the SVG. Timeline drawing functions include `svg_box()`, `svg_ubox()`, `svg_lbox()`, `svg_fbox()`, `svg_blocked()`, `svg_running()`, `svg_waiting()`, `svg_process()`, `svg_cstate()`, `svg_pstate()`, `svg_wakeline()`, `svg_partial_wakeline()`, `svg_interrupt()`, `svg_text()`, `svg_time_grid()`, `svg_io_legenda()`, and `svg_legenda()`. `svg_build_topology_map()` builds an optional CPU display-order map from `struct perf_env`.

Important file-global state includes `svgfile`, `first_time`, `last_time`, `total_height`, `max_freq`, `turbo_frequency`, `topology_map`, and exported globals `svg_page_width`, `svg_highlight`, and `svg_highlight_name`. The internal `struct topology` stores parsed sibling-core and sibling-thread masks as local `cpumask_t` arrays.

## Control Flow and Data Flow

Callers first invoke `open_svg()` with CPU count, extra row count, and timestamp bounds. The renderer rounds `first_time` down to a 100 ms boundary, enlarges `svg_page_width` for long recordings, writes XML/SVG headers, and emits CSS classes for process, sample, IO, wait, CPU, p-state, and c-state elements. Subsequent drawing calls are no-ops if `svgfile` is not open.

Timestamp coordinates flow through `time2pixels()`, which scales nanoseconds between `first_time` and `last_time` into the current page width. CPU coordinates flow through `cpu2y()`, optionally remapped by `topology_map`, then scaled by `SLOT_MULT` and `SLOT_HEIGHT`. Duration labels are produced by `time_to_string()`. `svg_running()` and `svg_process()` select the highlighted sample class based on duration or process-name matching. `svg_pstate()` normalizes frequency against `max_freq`, while `svg_cstate()` maps idle state depth to CSS class `c1` through `c6`.

Topology construction parses NUL-separated sibling maps from `perf_env`, converts each CPU-list string with `perf_cpu_map__new()`, fills bitmaps, then scans core groups and thread groups to assign display slots.

## State and Persistence Behavior

The persistent output is the SVG file written to disk. Rendering state is process-global and supports only one active SVG at a time. `svg_page_width`, `svg_highlight`, and `svg_highlight_name` are exported mutable knobs, so caller configuration persists across rendering calls. `svg_build_topology_map()` allocates `topology_map` and does not free a previously allocated map in this file, making it effectively process-lifetime state. `cpu_model()` reads `/proc/cpuinfo` and cpufreq sysfs on demand and updates global `max_freq`.

## Dependencies and Integration Points

The code depends on Linux bitmap helpers, perf CPU map APIs, `struct perf_env`, `/proc/cpuinfo`, and `/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies`. It integrates with perf visualization code that has already interpreted scheduling or IO events and only needs an SVG emission backend. It also integrates with perf environment capture because topology ordering uses `env->sibling_cores`, `env->sibling_threads`, and `env->nr_cpus_online`.

## Risks and Edge Cases

`time2pixels()` divides by `last_time - first_time`, so equal start/end times would break scaling. Caller-provided strings are written into XML text, title, and desc nodes without escaping except for a few literal arrow labels, so process names or backtraces containing XML metacharacters can corrupt output. `normalize_height()` returns `0.100` for heights at or above `0.75`, which is surprising and should be tested before changing because it may be a bug or an intentional visual cap. Many drawing functions assume valid row and CPU indices; out-of-range CPU IDs can index `topology_map` unsafely. File-global state makes the API unsuitable for concurrent SVG writers.

## Test Signals

Useful tests include generating a small timeline with known timestamp bounds and checking SVG dimensions, CSS class presence, and expected coordinate scaling. Regression tests should cover highlight-by-duration, highlight-by-process-name, IO boxes, wake lines in both directions, c-state clamping above C6, p-state formatting including turbo frequency, and topology remapping from a synthetic `perf_env`. Negative tests should cover zero-duration recordings, failed output open, missing cpufreq sysfs, and process names/backtraces requiring XML escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/svghelper.h

## Purpose

`svghelper.h` is the public interface for perf's SVG timeline renderer. It exposes the procedural drawing API implemented by `svghelper.c`, along with global rendering knobs for page width and highlighting.

## Important APIs, Types, and Functions

The header forward-declares `struct perf_env` and includes `linux/types.h` for `u64`. Lifecycle functions are `open_svg()` and `svg_close()`. Drawing functions cover generic boxes, upper/lower/full IO boxes, scheduler states, process spans, CPU background boxes, c-states, p-states, legends, time grids, wake lines, partial wake lines, interrupts, and text. `svg_build_topology_map()` configures CPU display ordering from perf environment topology.

The exported globals are `svg_page_width`, `svg_highlight`, and `svg_highlight_name`. They let callers influence output width and highlighted tasks or spans without adding parameters to each draw call.

## Control Flow and Data Flow

Callers include this header, call `open_svg()` once, emit drawing primitives in timestamp order or any desired order, optionally call `svg_time_grid()` and legend helpers, then call `svg_close()`. All time arguments are nanosecond `u64` values in the same domain as the `open_svg()` start/end bounds. CPU arguments are logical CPU IDs that may be remapped after `svg_build_topology_map()`.

## State and Persistence Behavior

The header exposes a stateful singleton renderer. The globals persist across calls and can affect later SVGs unless reset by the caller. The final persistent artifact is the file path passed to `open_svg()`.

## Dependencies and Integration Points

The API is consumed by perf visualization code that already has scheduler, CPU-idle, frequency, wakeup, and IO intervals. It depends on `svghelper.c` for implementation and on `struct perf_env` data generated by perf environment collection.

## Risks and Edge Cases

The API does not return errors from most drawing functions, so callers cannot distinguish ignored drawing after a failed `open_svg()` from successful emission unless they check externally. The global knobs and singleton output file are not thread-safe. Callers must ensure timestamp bounds and row/CPU IDs are valid and must avoid passing unescaped text that could break SVG.

## Test Signals

Compile tests should verify all declarations match `svghelper.c`. Link tests should cover users that only include the header and call the lifecycle, drawing, and topology functions. Behavior tests should set `svg_page_width`, `svg_highlight`, and `svg_highlight_name` before rendering and confirm those globals alter output as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol.c

## Purpose

`symbol.c` is the generic symbol-management and symbol-loading orchestrator for perf. It owns symbol allocation, rb-tree insertion and lookup, duplicate and end-address fixups, name sorting, kallsyms parsing and splitting, module parsing, kcore map loading, DSO symbol-source search policy, vmlinux/kallsyms fallback policy, symbol filters, global symbol configuration, and demangling.

## Important APIs, Types, and Functions

Major public functions include `symbol__new()`, `symbol__delete()`, `symbols__delete()`, `symbols__insert()`, `__symbols__insert()`, `symbols__fixup_duplicate()`, `symbols__fixup_end()`, `dso__insert_symbol()`, `dso__delete_symbol()`, `dso__find_symbol()`, `dso__find_symbol_nocache()`, `dso__find_symbol_by_name()`, `dso__sort_by_name()`, `modules__parse()`, `compare_proc_modules()`, `dso__load()`, `dso__load_vmlinux()`, `dso__load_vmlinux_path()`, `__dso__load_kallsyms()`, `dso__load_kallsyms()`, `symbol__init()`, `symbol__exit()`, `symbol__config_symfs()`, `symbol__validate_sym_arguments()`, and `dso__demangle_sym()`.

The central global is `struct symbol_conf symbol_conf`, initialized with defaults for demangling, modules, vmlinux search, callchain behavior, field display, symfs layout, and addr2line timeout. The file also owns `vmlinux_path` and `vmlinux_path__nr_entries`.

## Control Flow and Data Flow

Symbol allocation reserves optional private space before `struct symbol`, initializes annotation state when configured, and stores a flexible-array name. Symbols are inserted into address-ordered rb-trees. Lookups use address ranges and a DSO last-find cache; name lookups require a sorted symbol-name array. Duplicate fixup chooses the best symbol at a shared start address using length, type, binding, underscore count, name length, and architecture hooks. End fixup fills zero-sized symbols using the next symbol, with special kallsyms behavior to avoid giant gaps between kernel, module, and BPF regions.

Kernel loading first honors explicit `kallsyms` or `vmlinux` paths, then build-id cache vmlinux, configured vmlinux paths, and finally kallsyms from `/proc` or build-id cache. Kallsyms symbols are loaded into a temporary kernel DSO tree, fixed up, and split into kernel/module maps or into kcore-derived maps. User and module DSO loading searches candidate binary types in priority order, checking compatibility, namespace/chroot paths, optional BFD loading, `symsrc__init()`, and then `dso__load_sym()` plus PLT synthesis. Perf JIT maps are handled through `/tmp/perf-<pid>.map`, including mount namespace lookup.

Initialization aligns private symbol storage, initializes the ELF backend, builds vmlinux search paths, validates field separators and parallelism filters, builds DSO/comm/pid/tid/symbol/backtrace-stop filters, normalizes symfs, and reads kernel pointer restrictions. Exit frees configured lists and vmlinux paths. Demangling tries Rust v0, C++/BFD, OCaml, then Java according to kernel/user demangle flags.

## State and Persistence Behavior

This file mutates long-lived perf model state: DSO loaded flags, binary types, build IDs, symbol rb-trees, sorted name arrays, last lookup caches, map boundaries, module maps, kcore maps, and global `symbol_conf`. It reads persistent system state from `/proc/modules`, `/proc/kallsyms`, `/proc/sys/kernel/kptr_restrict`, `/proc/kcore`, uname-derived vmlinux paths, build-id caches, and `/tmp/perf-<pid>.map`. It may persist a changed build-id cache directory when `symbol__config_symfs()` is used.

## Dependencies and Integration Points

The code depends on perf `dso`, `map`, `maps`, `machine`, namespace, build-id, kallsyms, annotation, demangler, cpumap, strlist, intlist, and header utilities. It integrates with `symbol-elf.c` or `symbol-minimal.c` through `symsrc__init()` and `dso__load_sym()`, with reporting and annotation through `symbol_conf.priv_size`, and with machine/kernel map creation through `maps__insert()`, `maps__merge_in()`, and trampoline mapping.

## Risks and Edge Cases

Symbol loading races against changing `/proc/modules`, `/proc/kallsyms`, `/proc/kcore`, exiting processes, and namespace changes. Kptr restrictions and perf paranoid settings can silently restrict kernel symbol access. Duplicate selection changes can alter reported call stacks. Map splitting must preserve BPF maps and handle relocated kernels, entry trampolines, guest kernels, modules without matching maps, and kcore maps whose PT_LOAD ranges overlap. `dso__load()` marks DSOs loaded even after some failures, so retry semantics are limited. Global `symbol_conf` must be initialized before code that needs annotation private space.

## Test Signals

Tests should cover symbol rb-tree insertion/lookup boundaries, zero-sized end fixups, duplicate resolution, name sorting with versioned symbols, module file parsing, perf-map loading, explicit bad vmlinux/kallsyms validation, symfs hierarchy and flat layouts, kptr restrictions, DSO candidate search order, deleted DSOs, guest kernel fallback, and demangling for Rust/C++/OCaml/Java. Integration tests should verify kernel symbolization from vmlinux, `/proc/kallsyms`, build-id cache, and kcore, plus user DSO symbolization from debuglink/debugdata/build-id paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h

## Purpose

`symbol_conf.h` defines the global configuration object controlling perf symbol loading, filtering, display, annotation, demangling, addr2line behavior, callchain behavior, guest symbol paths, symfs layout, and parallelism filters.

## Important APIs, Types, and Functions

The main type is `struct symbol_conf`, with many booleans for behavior flags such as `try_vmlinux_path`, `ignore_vmlinux`, `use_modules`, `demangle`, `demangle_kernel`, `hide_unresolved`, `lazy_load_kernel_maps`, `keep_exited_threads`, `annotate_data_member`, `enable_latency`, and `prefer_latency`. It stores path strings for vmlinux, kallsyms, guest files, source prefix, graph function, addr2line path, and symfs. It stores filter input strings and parsed `strlist`/`intlist` objects for DSOs, comms, pids, tids, symbols, address filters, column widths, and backtrace stops. It defines `enum a2l_style` and an array of preferred addr2line styles. It also declares the global `symbol_conf`.

## Control Flow and Data Flow

Command-line and config parsing populate raw strings and flags in `symbol_conf`. `symbol__init()` later converts those strings into parsed lists, initializes symbol-private allocation size, computes kernel pointer restriction state, configures vmlinux paths, and validates parallelism filters. Symbol loading, reporting, annotation, and demangling code read the resulting fields to decide which DSOs/symbols to load, display, annotate, or suppress.

## State and Persistence Behavior

`symbol_conf` is process-global mutable state. It persists across all DSO loads and reports in a perf process until `symbol__exit()` frees parsed lists and clears initialization state. Some fields own allocated strings, while others point to command-line storage or static defaults depending on the setup path. `symfs` changes also redirect build-id cache lookup through `symbol__config_symfs()`.

## Dependencies and Integration Points

The header depends on `stdbool.h`, Linux bitmap support, `perf.h`, and forward declarations for `strlist` and `intlist`. It integrates with `symbol.c`, annotate/report code, addr2line implementations, callchain rendering, latency reporting, and any option parser that writes symbol configuration.

## Risks and Edge Cases

Because this is global state, initialization order matters. `symbol__annotation_init()` must run before `symbol__init()` if callers need annotation private storage. Ownership of string fields is not uniform, so cleanup must only free fields that the owning functions allocate. The parallelism bitmap has `MAX_NR_CPUS + 1` bits and represents filtered-out levels by clearing requested bits, which can be easy to misread. Changing defaults can alter many perf commands.

## Test Signals

Tests should verify default values, conversion of DSO/comm/pid/tid/symbol filters, address extraction from symbol filters, symfs flat versus hierarchy behavior, invalid field separator rejection, invalid parallelism levels, addr2line style parsing by users of the enum, and cleanup/reinitialization without leaks or stale parsed lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c

## Purpose

`synthetic-events.c` creates perf events that did not come directly from the kernel ring buffer but are needed to make perf data self-describing. It synthesizes task, mmap, namespace, cgroup, module, kernel-map, thread-map, CPU-map, stat, sample, id-index, event-update, build-id, tracing-data, header-feature, pipe, and schedstat records.

## Important APIs, Types, and Functions

Core helpers include `perf_tool__process_synth_event()`, `perf_event__synthesize_comm()`, `perf_event__synthesize_namespaces()`, `perf_event__synthesize_mmap_events()`, `perf_event__synthesize_modules()`, `perf_event__synthesize_thread_map()`, `perf_event__synthesize_threads()`, `perf_event__synthesize_kernel_mmap()`, `perf_event__synthesize_thread_map2()`, `perf_event__synthesize_cpu_map()`, `perf_event__synthesize_stat_config()`, `perf_event__synthesize_stat()`, `perf_event__synthesize_stat_round()`, `perf_event__sample_event_size()`, `perf_event__synthesize_sample()`, `perf_event__synthesize_id_sample()`, `perf_event__synthesize_id_index()`, event update synthesizers for unit/scale/name/cpus, `perf_event__synthesize_attrs()`, `perf_event__synthesize_extra_attr()`, `perf_event__synthesize_attr()`, `perf_event__synthesize_build_id()`, `perf_event__synthesize_mmap2_build_id()`, `perf_event__synthesize_stat_events()`, `perf_event__synthesize_features()`, `perf_event__synthesize_for_pipe()`, `parse_synth_opt()`, and `perf_event__synthesize_schedstat()`.

Important internal flows parse `/proc/<pid>/status`, `/proc/<pid>/task/<tid>/maps`, namespace symlinks, cgroup trees, kernel module maps, `/proc`, perf evlists, sample layouts, header features, and `/proc/schedstat`.

## Control Flow and Data Flow

Task synthesis reads process/thread status to build COMM, FORK, NAMESPACES, and optional MMAP2 records. Full process scans iterate `/proc` and per-process task directories, optionally using worker pthreads. Mmap synthesis parses each maps line with `read_proc_maps_line()`, filters executable mappings unless data maps are requested, marks hugepage mappings as anonymous hugepage entries, optionally attaches build IDs, aligns variable filename data, and passes records through a caller-supplied handler.

Kernel and module synthesis walk `struct machine` maps to emit kernel or module MMAP/MMAP2 records. Metadata synthesis converts evsels into ATTR and EVENT_UPDATE records, evlists into ID_INDEX records, CPU maps into compact range/list/mask encodings, thread maps into THREAD_MAP records, and stat counts into STAT/STAT_ROUND/STAT_CONFIG records. Sample synthesis writes fields in the exact order required by `sample_type` and `read_format`, including cross-endian packing of pid/tid and cpu/reserved pairs. Feature and pipe synthesis serialize perf header feature blocks and optional trace data.

Schedstat synthesis reads version 15, 16, or 17 `/proc/schedstat`, creates CPU and domain records using included version field lists, filters requested CPUs, and emits records with a shared timestamp.

## State and Persistence Behavior

Most functions allocate temporary `union perf_event` buffers, fill them, invoke `process`, and free the buffers. The persistent effect is on the perf data stream or session state handled by the callback. The file-global `proc_map_timeout` controls maps parsing timeout. Some flows update DSO build IDs when mmap build-id synthesis discovers them. Thread synthesis can run concurrently across pthreads, so the callback and shared machine/session structures must tolerate that usage.

## Dependencies and Integration Points

The file depends on perf event record definitions, `perf_tool`, `machine`, `map`, `dso`, `evlist`, `evsel`, `session`, `stat`, `target`, `symbol_conf`, cgroup helpers, namespace helpers, build-id readers from `symbol.h`, `/proc`, sysfs, cgroupfs, trace-event support, and CPU/thread map libraries. It is used by `perf record`, `perf inject`, pipe output, stat recording, and report-side reconstruction.

## Risks and Edge Cases

The code races with process exit, thread exit, namespace changes, map changes, cgroup changes, and module changes; many failures are intentionally ignored or downgraded. Variable-length event sizes must stay 64-bit aligned and within header size limits. `perf_event__synthesize_stat_events()` overwrites `err` after extra attr synthesis, so failures from extra attrs may be lost before thread-map synthesis. `perf_event__synthesize_mmap2_build_id()` appears to assign `ev.build_id.size` instead of `ev.mmap2.build_id_size` when clamping oversized build IDs, which is worth regression testing. Sample synthesis assumes non-null optional structures when their sample bits are set. Parallel thread synthesis can interleave callback execution.

## Test Signals

Tests should cover COMM/FORK/MMAP generation for live and exiting tasks, namespace records, data mmap filtering, hugepage mapping rewriting, build-id attachment, proc map timeout marking, cgroup tree synthesis, module mmap records, kernel mmap records with and without build-id mmap2, thread scans with one and many worker threads, CPU map range/list/mask encodings, stat config and stat events, sample size versus synthesized sample bytes for every `PERF_SAMPLE_*` bit, id-index chunking over `UINT16_MAX` limits, pipe feature serialization, synth option parsing, and schedstat versions 15/16/17.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h

## Purpose

`synthetic-events.h` declares the synthetic perf event API. It defines which synthetic event groups can be requested and exposes constructors for task, mmap, metadata, stat, sample, build-id, tracing, BPF, pipe, and schedstat records.

## Important APIs, Types, and Functions

`enum perf_record_synth` defines `PERF_SYNTH_TASK`, `PERF_SYNTH_MMAP`, `PERF_SYNTH_CGROUP`, and `PERF_SYNTH_ALL`. `perf_event__handler_t` is the callback signature used by almost every synthesizer. The header forward-declares the perf model types used by the API, including `perf_tool`, `machine`, `evlist`, `evsel`, `perf_sample`, `perf_session`, `perf_stat_config`, `target`, CPU/thread maps, and auxtrace/BPF support types.

The declarations include attribute/event-update synthesis, build-id and mmap2-build-id synthesis, CPU/thread map synthesis, kernel/module/task/mmap/namespace/cgroup synthesis, sample and id-sample synthesis, id-index synthesis, stat synthesis, tracing-data synthesis, feature/pipe synthesis, machine thread synthesis wrappers, BPF event synthesis, and schedstat synthesis. When libbpf support is unavailable, `perf_event__synthesize_bpf_events()` is an inline no-op.

## Control Flow and Data Flow

Callers pass a `perf_tool`, machine/session/evlist context, and a `perf_event__handler_t` callback. Each implementation fills one or more `union perf_event` records and hands them to the callback, optionally with a `perf_sample`. `parse_synth_opt()` converts user strings into `PERF_SYNTH_*` masks.

## State and Persistence Behavior

The header itself stores no state, but it exposes APIs that write synthetic records to a perf stream, mutate DSO build IDs, and read process/system state. The inline BPF fallback preserves behavior for builds without libbpf by making BPF metadata synthesis a successful no-op.

## Dependencies and Integration Points

It depends on Linux/perf types, `pid_t`, `bool`, and perf CPU map declarations. It is included by record, inject, report, stat, schedstat, BPF, auxtrace, and session code that needs self-describing perf data.

## Risks and Edge Cases

Callback semantics are central: some callers pass `NULL` tool or machine pointers for metadata records, so callbacks must handle the combinations used by each synthesizer. Feature availability varies by build flags, especially libbpf and libtraceevent. The enum mask must remain consistent with `parse_synth_opt()` and user-facing synth options.

## Test Signals

Compile tests should cover libbpf and non-libbpf builds. API tests should verify `parse_synth_opt()` masks, callback invocation contracts, and linkage for each declared synthesizer. Integration tests should compare generated records against perf data consumers for pipe, stat, and task/mmap workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/synthetic-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c

## Purpose

`syscalltbl.c` maps architecture-specific syscall names and numbers for perf trace and related tools. It wraps generated syscall tables with lookup, reverse lookup, index iteration, and glob matching helpers.

## Important APIs, Types, and Functions

The public functions are `syscalltbl__name()`, `syscalltbl__id()`, `syscalltbl__num_idx()`, `syscalltbl__id_at_idx()`, `syscalltbl__strglobmatch_first()`, and `syscalltbl__strglobmatch_next()`. Internal `find_table()` selects a `struct syscalltbl` from `trace/beauty/generated/syscalltbl.c` and caches the last architecture. `syscallcmpname()` is the `bsearch()` comparator over sorted syscall-name indexes.

## Control Flow and Data Flow

Lookups start by finding the table for an ELF `e_machine` value. `EM_SPARCV9` aliases to `EM_SPARC`, and generated tables may include an `EM_NONE` fallback. Number-to-name lookup checks bounds in `num_to_name`; MIPS syscall numbers above 1000 are reduced modulo 1000 to mask ABI base values. Name-to-number lookup binary-searches `sorted_names` using the actual `num_to_name` strings. Glob iteration walks sorted names from a mutable index and returns matching syscall IDs.

## State and Persistence Behavior

The only mutable state is the static last-table cache in `find_table()`. The generated syscall table data is static read-only process data. Callers own the glob iteration index.

## Dependencies and Integration Points

The file depends on generated syscall table data, ELF machine constants, Linux kernel helper macros, `strglobmatch()`, and standard `bsearch()`. It integrates with perf trace syscall formatting, syscall filters, and beauty decoders that need stable syscall IDs and names.

## Risks and Edge Cases

Unknown architectures return null names, zero index count, or `-1` IDs. `syscalltbl__id_at_idx()` asserts index validity rather than returning an error for out-of-range input. The last-table cache is not synchronized, though races only affect redundant cache updates. MIPS modulo handling is specific to encoded ABI bases and should not be generalized to other architectures.

## Test Signals

Tests should verify known syscall name/id round trips for representative architectures, SPARCV9 aliasing, MIPS high-number masking, unknown architecture behavior, sorted index bounds, glob first/next iteration, and generated table ordering expected by `bsearch()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h

## Purpose

`syscalltbl.h` declares the syscall table lookup API used by perf tools to translate syscall IDs and names for a selected ELF machine architecture.

## Important APIs, Types, and Functions

The declarations provide number-to-name lookup (`syscalltbl__name()`), name-to-number lookup (`syscalltbl__id()`), sorted-table size (`syscalltbl__num_idx()`), index-to-id lookup (`syscalltbl__id_at_idx()`), and glob iteration (`syscalltbl__strglobmatch_first()` and `syscalltbl__strglobmatch_next()`).

## Control Flow and Data Flow

Callers supply an `e_machine` architecture value for every query. Glob iteration uses an integer cursor initialized by the `first` function and advanced by the `next` function.

## State and Persistence Behavior

The header exposes no state. The implementation uses static generated tables and an internal last-lookup cache.

## Dependencies and Integration Points

It integrates with perf trace filtering and syscall beautification code. Consumers must include ELF machine constants from elsewhere; this header deliberately stays small and only declares the lookup contract.

## Risks and Edge Cases

Callers must handle null names and `-1` IDs for unsupported architectures or missing syscalls. The index cursor for glob matching is mutable caller state and should not be shared across independent iterations.

## Test Signals

Compile tests should ensure users can include this header without pulling generated table internals. API tests should exercise all declared functions through `syscalltbl.c` for at least one supported and one unsupported architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/target.c

## Purpose

`target.c` validates and normalizes perf target selection options, parses user IDs, and formats target-related error messages. It resolves conflicts among pid/tid, CPU, system-wide, BPF, and per-thread modes.

## Important APIs, Types, and Functions

`target__validate()` mutates a `struct target` into a consistent mode and returns an `enum target_errno` describing the first override. `parse_uid()` converts a username or numeric UID string to `uid_t`, returning `UINT_MAX` on failure. `target__strerror()` formats either normal errno values or negative target-specific errors into a caller buffer. The local `target__error_str[]` must stay ordered with `enum target_errno`.

## Control Flow and Data Flow

Validation first maps `pid` to `tid` because perf treats pid targeting as thread-list targeting. If a tid is present, it clears `cpu_list` and `system_wide`. If BPF targeting is present, it clears CPU list, tid, and per-thread mode. If per-thread mode conflicts with system-wide or CPU targeting, it clears per-thread mode. Only the first conflict is reported, but all applicable normalizations still run.

`parse_uid()` tries `getpwnam_r()` first, then parses a decimal number and verifies it with `getpwuid_r()`. `target__strerror()` delegates nonnegative errors to `str_error_r()` and handles only the target-specific negative range.

## State and Persistence Behavior

The file does not own persistent global state beyond the static error string table. `target__validate()` intentionally persists normalization by modifying the caller's `struct target` in place. `parse_uid()` reads system passwd database state.

## Dependencies and Integration Points

The code depends on `target.h`, libc passwd APIs, Linux kernel/string helpers, and perf's target error enum. It integrates with perf command option validation before evlist/thread/cpu map creation and with user-facing warning/error formatting.

## Risks and Edge Cases

Because validation mutates the target, callers that need original user intent must preserve it before calling. Only the first override is returned, so multiple conflicts can be normalized with only one reported message. `parse_uid()` uses `strtol()` into `int`, which can mishandle very large numeric UIDs on systems where `uid_t` is wider. User/group database failures are collapsed to `UINT_MAX`.

## Test Signals

Tests should cover every target conflict and verify both mutation and returned first error. Additional tests should verify pid-to-tid normalization, no-op valid targets, username UID parsing, numeric UID parsing, invalid names, nonexistent numeric UIDs, large UID strings, normal errno formatting, target-specific formatting, and invalid target error ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.c -->
