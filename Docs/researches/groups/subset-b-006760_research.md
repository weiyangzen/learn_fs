# subset-b-006760 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.c

## Purpose
This file is a C translation of Rust `rustc-demangle` support used by perf to recognize and display Rust legacy `_ZN...E` and v0 `_R...` symbol names. It keeps close upstream parity, exposes only the public functions declared in `demangle-rust-v0.h`, and otherwise implements a private parser/printer pipeline for paths, types, constants, lifetimes, backreferences, punycode identifiers, and suffix handling.

## Important APIs, Types, And Functions
The public entry points are `rust_demangle_demangle()`, `rust_demangle_display_demangle()`, and `rust_demangle_is_known()`. Internal state is split between `struct parser` for symbol traversal and recursion depth, `struct printer` for formatted output and overflow tracking, `struct demangle_v0`, `struct demangle_legacy`, and `struct ident`. Core helpers include `rust_demangle_v0_demangle()`, `rust_demangle_v0_display_demangle()`, `rust_demangle_legacy_demangle()`, `rust_demangle_legacy_display_demangle()`, `printer_print_path()`, `printer_print_type()`, `printer_print_const()`, `parser_backref()`, and `display_ident()`.

## Control Flow
`rust_demangle_demangle()` first strips ThinLTO `.llvm.<hex>` suffixes, tries legacy parsing, then v0 parsing, and otherwise marks the symbol unknown. Both parsers validate ASCII, prefixes, length encodings, and terminal structure before saving references into the original input. Display dispatches by style: unknown symbols are copied raw, legacy elements are decoded and joined with `::`, and v0 symbols are recursively printed through path/type/const grammar functions. After the main symbol is printed, valid symbol-like suffixes are appended.

## State, Dependencies, And Integration
The demangle result stores borrowed pointers into the caller's symbol string; callers must keep the input stable until display completes. Output is caller-owned and guarded by `OVERFLOW_MARGIN`, while parser recursion is bounded by `MAX_DEPTH`. Dependencies are intentionally small: libc string/stdio/stdint helpers plus the public header. Integration is via perf symbol display paths that need Rust demangling without pulling Rust code into perf.

## Risks And Test Signals
Key risks are divergence from upstream `rustc-demangle`, accidental use-after-free of borrowed string slices, output explosion from recursive/backreference-heavy v0 names, and edge cases in UTF-8, punycode, or const-string escaping. Tests should cover legacy and v0 valid symbols, unknown symbols, LLVM suffix stripping, alternate formatting without hashes/types, too-small output buffers returning `OverflowOverflow`, non-ASCII rejection for mangled payloads, recursion-limit handling, and malformed lengths/backrefs/hex nibbles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.h

## Purpose
This header defines perf's public C interface for Rust symbol demangling. It documents the borrowed-data contract for `struct demangle`, the supported demangling styles, and the bounded-output behavior expected by callers.

## Important APIs And Types
`enum demangle_style` distinguishes unknown, legacy, and v0 Rust formats. `struct demangle` contains the selected style, the mangled slice, original string slice, suffix slice, and legacy element count. `overflow_status` reports whether display fit the caller's buffer. `OVERFLOW_MARGIN` intentionally forces a few spare bytes so display can safely terminate and detect near-overflow. `DEMANGLE_NODISCARD` marks the display API's return value as important on GCC/Clang.

## Control Flow And Integration
Callers use `rust_demangle_demangle(const char *s, struct demangle *res)` to classify a NUL-terminated symbol, optionally check `rust_demangle_is_known(res)`, and then call `rust_demangle_display_demangle(res, out, len, alternate)`. The `alternate` flag maps to Rust's less verbose `{:#}` formatting style, omitting symbol hashes and some constant integer type suffixes.

## State, Dependencies, And Persistence
The header depends only on `<stddef.h>` and C/C++ linkage guards, but it uses `bool` in prototypes and therefore relies on consumers including or otherwise providing `<stdbool.h>` in C builds, as the implementation does. `struct demangle` contains borrowed pointers into the input symbol and does not own memory or persist beyond that input's lifetime.

## Risks And Test Signals
The highest integration risk is misuse of `struct demangle` after freeing or mutating the original symbol. Callers must also honor `OverflowOverflow` and retry with a larger buffer rather than assuming truncation. Compile tests should include C and C++ consumers, and behavioral tests should assert unknown-style passthrough, legacy/v0 classification, suffix preservation, and alternate formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/disasm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/disasm.c

## Purpose
This file turns binary code for a perf `struct symbol` into annotation lines. It selects architecture metadata, parses disassembler output, classifies instructions into semantic operation families, maps branch/call targets back to perf symbols, and coordinates objdump, LLVM, Capstone, raw PowerPC, BPF, compressed module, and kcore paths.

## Important APIs, Types, And Functions
Exported APIs include `arch__find()`, `arch__associate_ins_ops()`, `ins__find()`, `ins__is_call()`, `ins__is_jump()`, `ins__is_fused()`, `disasm_line__new()`, `disasm_line__free()`, `disasm_line__scnprintf()`, `expand_tabs()`, `symbol__strerror_disassemble()`, and `symbol__disassemble()`. Important operation tables are `call_ops`, `jump_ops`, `mov_ops`, `dec_ops`, `lock_ops`, `nop_ops`, and `ret_ops`. Internal control centers are `symbol__parse_objdump_line()`, `symbol__disassemble_objdump()`, `symbol__disassemble_raw()`, `dso__disassemble_filename()`, and instruction parsers such as `call__parse()`, `jump__parse()`, `mov__parse()`, and `lock__parse()`.

## Control Flow
`symbol__disassemble()` resolves the best file path for the DSO, optionally extracts kcore or decompresses kernel modules, then tries disassembly strategies in configured order. Source annotation requests prefer objdump because LLVM/Capstone paths do not support source emission here. Objdump output is read line by line, tabs are expanded, source `file:line` markers update line state, and address-prefixed lines become `struct disasm_line` entries with offsets relative to the target symbol. Each instruction name is looked up in the architecture instruction table, parsed into operands, and later rendered in normalized form.

## State, Dependencies, And Integration
Static state includes the compiled `file_lineno` regex and a lazily grown/sorted array of architecture descriptors. Each disassembly line owns duplicated line text, file-location text, instruction name, operand strings, and per-event annotation data. Integration points are broad: `dso` file resolution/cache APIs, `map` address translation, `maps__find_ams()` symbol lookup, `annotation_line__add()`, `thread` maps, `symbol` metadata, kcore extraction, BPF disassembly, libbfd, LLVM, Capstone, objdump child processes, and perf annotation options.

## Risks And Test Signals
Risks include fragile objdump text parsing, command-line quoting issues around filenames/options, architecture-specific suffix/opcode matching mistakes, wrong objdump-to-memory address translation, races with DSO metadata changes, missing BPF/kcore capabilities, and partial disassembly leaving stale lines. Tests should exercise call/jump/mov parsing, PowerPC raw parsing, source line preservation, kcore nop deletion, compressed module cleanup, failure messages from `symbol__strerror_disassemble()`, backend fallback ordering, tab expansion, and branch/call target resolution across maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/disasm.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/disasm.h

## Purpose
This header declares perf's disassembly and instruction-classification contract for annotation code and architecture-specific backends. It defines the architecture descriptor, instruction descriptor, parsed operand layout, operation callbacks, and the arguments passed into disassembly-line construction.

## Important APIs And Types
`struct arch` carries ELF identity, objdump syntax characters, instruction tables, optional instruction-fusion and DWARF state hooks, and architecture-specific dynamic association. `struct ins` binds a mnemonic to `struct ins_ops`. `struct ins_operands` stores raw operands, source/target details, lock-prefixed nested instructions, and jump comment metadata. `struct annotate_args` supplies the architecture, map/symbol, annotation options, current offset, source line, and file location. Exported APIs include architecture constructors, `arch__find()`, instruction predicates, `ins__find()`, `disasm_line__new/free/scnprintf()`, `symbol__disassemble()`, and render helpers for call/jump/mov/raw instructions.

## Control Flow And Integration
Architecture-specific code constructs `struct arch` instances and can associate unknown instruction names on demand. Generic disassembly code consumes these definitions to parse lines, normalize operands, update annotation state, and render output for perf annotate/report views. Optional `HAVE_LIBDW_SUPPORT` adds data-location/type-state updates tied to DWARF DIEs.

## State And Persistence
The header's structures describe ownership boundaries: operation parsers may allocate operand strings and must pair them with `free` callbacks when custom cleanup is required. `struct arch` instruction arrays may be static initially and later copied/grown dynamically by `arch__associate_ins_ops()`.

## Risks And Test Signals
The main risks are ABI drift between generic disassembly and arch-specific constructors, missing cleanup for operands added by new parsers, and incorrect objdump syntax characters for a target architecture. Build tests should cover all enabled architecture constructors and optional libdw paths; behavior tests should verify instruction lookup, suffix stripping, call/jump predicates, and cleanup of nested lock operands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/disasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.c

## Purpose
This file implements `perf script --dlfilter` loading and callback mediation. It loads user-provided shared objects, exposes a stable `perf_dlfilter_fns` helper table, converts perf internal sample/address structures into public dlfilter structs, and invokes early or normal filter callbacks with a temporarily valid context.

## Important APIs, Types, And Functions
Public functions are `dlfilter__new()`, `dlfilter__start()`, `dlfilter__do_filter_event()`, `dlfilter__cleanup()`, `get_filter_desc()`, and `list_available_dlfilters()`. Internal helpers include `find_dlfilter()`, `dlfilter__open()`, `dlfilter__close()`, `al_to_d_al()`, `dlfilter__resolve_ip()`, `dlfilter__resolve_addr()`, `dlfilter__resolve_address()`, `dlfilter__al_cleanup()`, `dlfilter__insn()`, `dlfilter__srcline()`, `dlfilter__attr()`, and `dlfilter__object_code()`.

## Control Flow
Creation resolves the filter path from an explicit path, current directory, or perf's `dlfilters` directory, then uses `dlopen()` and `dlsym()` to discover `start`, `stop`, `filter_event`, `filter_event_early`, and `perf_dlfilter_fns`. On start/stop, flags allow the filter to query arguments outside sample processing. For each event, `dlfilter__do_filter_event()` fills a public sample object, installs transient pointers to event/sample/evsel/machine/address locations, marks `ctx_valid`, calls the selected filter, and clears context validity before returning.

## State, Dependencies, And Integration
`struct dlfilter` owns the shared-object handle, resolved file path, plugin data pointer, argument vector, session pointer, callback pointers, and transient event context. Address helpers integrate with `machine__resolve()`, `thread__resolve()`, `thread__find_symbol_fb()`, `get_srcline_split()`, `perf_sample__fetch_insn()`, and `dso__data_read_offset()`. `CHECK_FLAG()` build assertions keep public dlfilter branch flags synchronized with `PERF_IP_FLAG_*`.

## Risks And Test Signals
Risks include untrusted shared-object execution, leaks if v2 `priv` address-location results are not cleaned with `al_cleanup`, use of helper callbacks outside valid context, stale instruction/source allocations owned by lower layers, and `get_filter_desc()` returning without `dlclose()` when validation fails. Tests should load filters with only early or normal callbacks, validate callback table population, exercise args in start/stop and event contexts, resolve IP/address/srcline/object code, confirm v0/v2 address cleanup compatibility, and list filters from both current and install directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.h

## Purpose
This header defines the internal perf object used to manage a dlfilter plugin and declares the wrapper APIs used by perf script. It separates fast inline no-op checks from the heavier callback invocation implemented in `dlfilter.c`.

## Important APIs And Types
`struct dlfilter` stores the plugin file path, `dlopen` handle, plugin-private `data`, session pointer, context-validity flags, dlfilter arguments, transient event/sample/evsel/machine/address-location pointers, public converted sample/address objects, and function pointers for `start`, `stop`, `filter_event`, and `filter_event_early`. API declarations cover construction, start, event dispatch, cleanup, filter listing, and description lookup.

## Control Flow And Integration
Callers construct a filter with `dlfilter__new()`, optionally start it with a session, and then call `dlfilter__filter_event()` or `dlfilter__filter_event_early()`. The inline wrappers return pass-through success when no filter or no matching callback exists; otherwise they delegate to `dlfilter__do_filter_event()`.

## State And Persistence
Persistent state is the plugin handle, file path, callback table, plugin data returned from `start`, and command-line arguments. Event context fields are transient and valid only during `dlfilter__do_filter_event()`. This is important because helper callbacks in the public dlfilter API guard on `ctx_valid`.

## Risks And Test Signals
The main risks are callers bypassing the inline guards with a partially initialized object, plugins assuming context persists after callbacks, and lifetime mistakes around `dlargv` ownership, which is borrowed. Tests should cover null filters, missing early/normal callbacks, start/stop data lifetime, cleanup after failed start, and event filtering with both resolved and unresolved address locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.c

## Purpose
This file implements a perf pseudo-PMU for Linux DRM usage statistics exposed through `/proc/<pid>/fdinfo`. It discovers DRM drivers/events from live file descriptors, exposes those events through perf's PMU listing/parsing interfaces, and reads counters by summing fdinfo values for a selected pid or system-wide view.

## Important APIs, Types, And Functions
Public APIs include `perf_pmu__is_drm()`, `evsel__is_drm()`, `perf_pmus__read_drm_pmus()`, `drm_pmu__exit()`, `drm_pmu__have_event()`, `drm_pmu__for_each_event()`, `drm_pmu__num_events()`, `drm_pmu__config_terms()`, `drm_pmu__check_alias()`, `evsel__drm_pmu_open()`, and `evsel__drm_pmu_read()`. Internal structures are `struct drm_pmu`, `struct drm_pmu_event`, `enum drm_pmu_unit`, `struct minor_info`, and callback argument structs for discovery/read passes.

## Control Flow
Discovery walks numeric `/proc` directories, opens `fd` and lazily `fdinfo`, filters character devices with major 226, deduplicates DRM minors, and parses `drm-driver:` plus recognized `drm-*` statistic lines. Each new driver becomes a pseudo-PMU with a synthetic type in the DRM range, and each statistic name becomes an event indexed by array position. Event parsing sets `attr->config` to that index. Reads either scan a single pid or all pids, match the configured event name in fdinfo, convert units, sum values, and update perf counts.

## State, Dependencies, And Integration
Each `struct drm_pmu` embeds `struct perf_pmu`, owns a dynamic event array, and uses synthetic CPU map `0`. The implementation depends on procfs helpers, `api/io` line reading, `perf_counts`, thread maps, parse-events errors, PMU metadata callbacks, and Linux DRM fdinfo conventions. No kernel perf_event fd is opened; `evsel__drm_pmu_open()` is a no-op because reads are procfs scans.

## Risks And Test Signals
Risks include races while processes exit or close fds, fdinfo format drift, a probable unit typo where `drm-total-cycles-` is registered as bytes instead of cycles, duplicate-minor suppression changing totals, unchecked growth failures in the minor array causing possible out-of-bounds writes, and synthetic PMU type exhaustion. Tests should mock procfs fd/fdinfo trees, verify event discovery/deduplication, parse all unit conversions, validate parse-event errors, compare per-pid and system-wide sums, and exercise disappearing processes/fds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.h

## Purpose
This header declares the DRM pseudo-PMU interface used by perf PMU discovery, event parsing, opening, and reading paths. It documents that DRM metrics come from Linux DRM usage stats rather than hardware perf events.

## Important APIs And Types
The header exposes PMU lifecycle/query functions (`drm_pmu__exit()`, `drm_pmu__have_event()`, `drm_pmu__for_each_event()`, `drm_pmu__num_events()`), parse integration (`drm_pmu__config_terms()`, `drm_pmu__check_alias()`), classification helpers (`perf_pmu__is_drm()`, `evsel__is_drm()`), discovery (`perf_pmus__read_drm_pmus()`), and evsel operations (`evsel__drm_pmu_open()`, `evsel__drm_pmu_read()`).

## Control Flow And Integration
Perf PMU enumeration calls `perf_pmus__read_drm_pmus()` to append DRM pseudo-PMUs. Parse-event code checks event names and configures `perf_event_attr.config` through the DRM helpers. Runtime count collection uses the evsel helpers; open is intentionally a no-op and read performs procfs-backed accumulation.

## State And Persistence
Opaque state is stored behind `struct perf_pmu` in the implementation's container type. Consumers should treat DRM PMUs as synthetic PMUs identified by type range and should not expect kernel file descriptors or normal perf_event mmap/read behavior.

## Risks And Test Signals
Risks are mostly contract mismatches with generic PMU code that assumes kernel-backed events. Tests should ensure DRM PMUs are recognized by type, event iteration supplies unit/scale metadata, parse aliases reject invalid terms, and read paths update `perf_counts_values` consistently with other software PMU readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dso.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dso.c

## Purpose
This file implements perf's DSO object lifecycle, identity, binary-path resolution, file descriptor cache, data cache, module compression handling, build-id helpers, ELF-machine detection, and symbol-byte reading. It is the central backing store for maps, symbols, annotation, build-id processing, namespace-aware file access, BPF JIT code, and kernel module handling.

## Important APIs, Types, And Functions
Key lifecycle APIs are `dso__new_id()`, `dso__new()`, `dso__get()`, `dso__put()`, and `dso__delete()`. Identity/name APIs include `dso_id__cmp()`, `__dso__improve_id()`, `dso__set_short_name()`, `dso__set_long_name()`, and build-id helpers. File/data APIs include `dso__read_binary_type_filename()`, `dso__data_get_fd()`, `dso__data_put_fd()`, `dso__data_close()`, `dso__data_size()`, `dso__data_read_offset()`, `dso__data_read_addr()`, cache-write helpers, `dso__e_machine()`, `dso__read_symbol()`, and `dso__debuginfo()`. Module helpers include `is_kernel_module()`, `__kmod_path__parse()`, `dso__set_module_info()`, and decompression APIs.

## Control Flow
New DSOs initialize refcounted state, rb-trees, lock, names, default binary/symtab type, file data state, and architecture assumptions. File opening resolves a path from the current binary type, optional symfs/root namespace, debuglink/build-id/debug-info locations, guest roots, kcore, or module paths; compressed modules are decompressed to a temporary file and unlinked after opening/using. Data reads first ensure file size, then use 4 KiB rb-tree cache chunks populated from file, BPF program info, or synthetic OOL data. File descriptors are globally LRU-managed under `_dso__data_open_lock`, capped at half `RLIMIT_NOFILE`.

## State, Dependencies, And Integration
`struct dso` owns symbol/source/type rb-trees, name strings, namespace info, auxtrace/libdw/a2l handles, `struct dso_data`, build identity, BPF metadata, load error state, and many one-bit flags. Global state includes the open-DSO list, open count, lazily initialized open lock, and cached fd limit. Dependencies include namespace switching, symfs path helpers, compression backends, build-id/debuglink readers, map address translation, libbpf/perf env, auxtrace, libdw, srcline, symbol trees, and machine root metadata.

## Risks And Test Signals
Risks include lock-order mistakes between DSO locks and the global open lock, stale `errno` leading to wrong load errors, temporary decompression cleanup failures, DSO renames invalidating sorted `dsos` arrays, partial ID comparison treating missing IDs as equal, cache writes changing only memory not backing files, and build option differences for zlib/lzma/libbpf/libdw. Tests should cover fd LRU under low `RLIMIT_NOFILE`, namespace path fallback, all binary-type path constructors, compressed and uncompressed module handling, DSO id improvement/sorting, cache read/write across chunk boundaries, ELF endianness/e_machine parsing, BPF program reads, refcount deletion cleanup, and `dso__strerror_load()` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dso.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/dso.h

## Purpose
This header defines the DSO object model used throughout perf. It exposes binary type classification, namespace-aware symbol/data access, build identity, data caching APIs, refcounted lifetime helpers, and a large set of inline accessors for `struct dso`.

## Important APIs And Types
Major enums include `dso_binary_type`, `dso_space_type`, `dso_swap_type`, `dso_data_status`, `dso_type`, and `dso_load_errno`. Core data structures include `struct dso_id`, `struct dso_cache`, `struct dso_data`, `struct dso_bpf_prog`, `struct kmod_path`, and the refcount-checked `struct dso`. The header declares construction/lifetime functions, name/id mutation, build-id APIs, module parsing/decompression, DSO data fd/read/cache APIs, ELF machine helpers, map/kernel helpers, symbol/source dump helpers, debuginfo access, and symbol-byte reading.

## Control Flow And Integration
Consumers create or find DSOs through machine/dsos code, mutate identity as more mmap2/build-id data appears, read data through `dso__data_*`, and release references with `dso__put()` or `dso__zput()`. Inline accessors use `RC_CHK_ACCESS()` to support reference-count checking builds. Generic mapping, annotation, symbol loading, auxtrace, BPF, libdw, and srcline code all depend on this contract.

## State And Persistence
The DSO carries persistent in-memory state for symbol trees, source-line trees, inlined nodes, global/data type trees, names, file-descriptor cache metadata, BPF ids, build id, namespace info, binary/symtab type, and warning flags. The backing binary/debug file is not owned; only temporary decompressed module files are created and removed by implementation code.

## Risks And Test Signals
Risks include direct field access bypassing inline/refcount checks, callers forgetting to pair `dso__data_get_fd()` with `dso__data_put_fd()`, ownership confusion for allocated versus borrowed names, and misclassifying binary types. Tests should compile with refcount checking and optional feature combinations, verify `DSO__SWAP` behavior, exercise inline flag setters/getters, pair fd-lock annotations, and validate kmod parsing and data cache APIs through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dsos.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dsos.c

## Purpose
This file manages a thread-safe collection of `struct dso *` objects. It stores DSOs in a dynamically sized array optimized for iteration and sorted binary lookup by long name, DSO id, and short name; it also supports module lookup/creation, build-id scanning, hit marking, and kernel DSO discovery.

## Important APIs, Types, And Functions
Public APIs are `dsos__init()`, `dsos__exit()`, `__dsos__add()`, `dsos__add()`, `dsos__find()`, `dsos__findnew_id()`, `dsos__read_build_ids()`, `dsos__fprintf_buildid()`, `dsos__fprintf()`, `dsos__hit_all()`, `dsos__findnew_module_dso()`, `dsos__find_kernel_dso()`, and `dsos__for_each_dso()`. Important internals include `__dsos__find_by_longname_id()`, `__dsos__find_id()`, `__dsos__addnew_id()`, `dso__set_basename()`, comparison helpers, and callback wrappers.

## Control Flow
Initialization sets an empty sorted array with an rwsem. Adds grow the array and either insert in sorted order or append if sorting is already invalid. Long-name lookups use bsearch, sorting under write lock if required; short-name lookups scan linearly. `findnew` holds the write lock, returns an existing DSO while improving its id if new metadata is available, or creates/inserts a new DSO. Module creation looks up by short module name, initializes module metadata, long name, kernel space, and inserts under lock.

## State, Dependencies, And Integration
`struct dsos` owns references to each DSO and clears `dso->dsos` during purge. It integrates with namespace-aware build-id reading, vdso hit exceptions, basename/JIT naming from perf map filenames, module parsing from `dso.c`, machine host/guest state, and kernel module classification. Read/write semaphores protect the array and sorted flag, but callbacks run under the read lock.

## Risks And Test Signals
Risks include callback code performing operations that need the write lock, stale sorted flags after DSO renames, incomplete identity causing false matches because empty IDs compare equal, memory leaks if `strdup(filename)` fails in module creation, and races if external users mutate DSO names outside provided setters. Tests should cover add/find ordering, findnew id improvement, short-name JIT basename generation, build-id reads with namespace fallback, module DSO creation for host/guest compressed modules, purge refcount behavior, and kernel DSO selection excluding modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dsos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dsos.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/dsos.h

## Purpose
This header defines the `struct dsos` collection contract for perf machine/map code. It provides a lock-protected dynamic array of DSO references plus APIs for insertion, lookup, iteration, build-id reporting, and module/kernel-specific discovery.

## Important APIs And Types
`struct dsos` contains an `rw_semaphore`, `struct dso **dsos`, count, allocation size, and sorted flag. Public functions cover lifecycle, raw and locked add, lookup by name/id, find-or-create by id, build-id scanning/printing, marking all DSOs as hit, module DSO find/create, kernel DSO lookup, and read-locked iteration callbacks.

## Control Flow And Integration
Machine code initializes a `dsos` collection, adds DSOs as maps/build-id events are processed, finds existing DSOs during mmap synthesis or sample resolution, and tears the collection down with `dsos__exit()`. The implementation owns DSO references while entries remain in the collection.

## State And Persistence
The collection keeps process-local in-memory DSO references only; it does not persist to disk. The sorted flag is part of the lookup invariant and is invalidated by name/id mutations through DSO setters.

## Risks And Test Signals
Risks are around lock discipline and callback behavior under read locks. Tests should verify add/find semantics, cleanup releases references, sorted flag restoration after mutation, and safe behavior when iteration callbacks stop early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dsos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dump-insn.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/dump-insn.h

## Purpose
This header declares a small architecture-aware instruction dumping interface used by perf code that needs a textual representation of instruction bytes and branch classification without going through full annotation disassembly.

## Important APIs And Types
`MAXINSN` is set to 15, matching the maximum x86 instruction length. `struct perf_insn` carries caller-initialized context: thread, machine, cpumode, 64-bit mode, CPU, and a fixed 256-byte output buffer. The declared APIs are `dump_insn(struct perf_insn *x, u64 ip, u8 *inbuf, int inlen, int *lenp)` and `arch_is_uncond_branch(const unsigned char *buf, size_t len, int x86_64)`.

## Control Flow And Integration
Callers populate `perf_insn` with sample/thread/machine context and pass instruction bytes plus the IP. The implementation, outside this header, is expected to decode or format the instruction into `x->out`, report the consumed length via `lenp`, and classify unconditional branches for the current architecture/mode.

## State And Persistence
The API is stack-friendly and caller-owned. It persists no global state in the header contract; `out` is embedded in the caller-provided object and valid until that object changes.

## Risks And Test Signals
Risks include buffer-size assumptions, incomplete architecture support, and wrong length reporting when fewer than `MAXINSN` bytes are available. Tests should cover short buffers, maximum-length x86 instructions, 32-bit versus 64-bit x86 unconditional branches, non-branch bytes, and integration with sample context where thread or machine is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dump-insn.h -->
