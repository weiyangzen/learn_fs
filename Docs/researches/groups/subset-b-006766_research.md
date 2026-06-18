# subset-b-006766 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm.c

## Purpose

`llvm.c` is perf's optional LLVM-backed address-to-source and disassembly adapter. When `HAVE_LIBLLVM_SUPPORT` is enabled it resolves source lines and inline frames through helper APIs and disassembles symbol bytes without spawning objdump. When LLVM support is absent the public entry points return failure so existing objdump or non-inline paths can be used.

## Important APIs, Types, and Functions

The exported APIs are `llvm__addr2line()` and `symbol__disassemble_llvm()`. `llvm__addr2line()` wraps `llvm_addr2line()`, optionally converts returned `llvm_a2l_frame` records into perf inline symbols with `new_inline_sym()`, `srcline_from_fileline()`, and `inline_list__append()`, and frees frame strings with `free_llvm_inline_frames()`. `symbol__disassemble_llvm()` reads symbol bytes via `dso__read_symbol()`, initializes all LLVM targets once in `init_llvm()`, creates a disassembler for x86 or a generic `<arch>-linux-gnu` triplet, and emits `struct disasm_line` records into `symbol__annotation(sym)->src->source`. `symbol_lookup_storage` is callback scratch state used by `symbol_lookup_callback()` to remember branch and PC-relative data references observed by LLVM.

## Control Flow

Address-to-line flow is straight-line: call LLVM helper, return on no inline frames, otherwise append each inline frame to the caller-provided `inline_node`. Disassembly first rejects explicit `objdump_path`, reads the symbol from the DSO/map, creates and configures the LLVM context, emits a function header line, then loops over instruction bytes with `LLVMDisasmInstruction()`. For each instruction it uses callback-collected addresses to append code or data symbol annotations from `llvm_name_for_code()` and `llvm_name_for_data()`, expands tabs, asks LLVM for a file/line for the current PC, and adds a disassembly line. All error exits dispose the LLVM context and free temporary buffers.

## State and Persistence Behavior

State is transient except for annotation lines appended to the symbol annotation tree and inline nodes cached by callers. LLVM target initialization is protected by a static boolean and persists process-wide. The function owns `code_buf`, `line_storage`, `args->fileloc`, and returned inline-frame strings. It sets fields in `annotate_args` while constructing each output line, so callers must treat that object as mutable during disassembly.

## Dependencies and Integration Points

This file depends on perf annotation, DSO, map, srcline, namespace, and symbol helpers, plus LLVM C disassembler APIs under `HAVE_LIBLLVM_SUPPORT`. It integrates with perf annotate/disassembly output, inline callchain presentation, source-line reporting, and architecture selection through `args->arch`. The x86 path handles 32-bit versus 64-bit code using the DSO read result; aarch64 requests `+all` CPU features.

## Risks and Edge Cases

LLVM callbacks deliberately return `NULL` and suppress LLVM's own symbol text because LLVM adds quotes around returned names. Incorrect callback state would lose branch/data annotations. `LLVMSetDisasmOptions()` order matters because the asm-printer variant can reset `PrintImmHex`. `llvm_addr2line()` is called with `filename` during disassembly but with `dso_name` in the public addr2line API; path and namespace mismatches can affect source lookup. A zero instruction length aborts the whole disassembly. Without LLVM support both public paths fail cleanly.

## Test Signals

Useful tests include building with and without `HAVE_LIBLLVM_SUPPORT`, `perf annotate --disassembler=llvm` on x86 and aarch64 binaries, branch and PC-relative load annotations, inline frame expansion, Intel syntax selection, and fallback behavior when `objdump_path` is set. Leak checks should cover early failures after partial inline-frame or disassembly-line creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm.h

## Purpose

`llvm.h` declares perf's optional LLVM integration surface for source-line lookup and disassembly. It keeps LLVM details out of callers by exposing only perf-native types and two entry points.

## Important APIs, Types, and Functions

The header forward-declares `struct annotate_args`, `struct dso`, `struct inline_node`, and `struct symbol`. `llvm__addr2line()` resolves a DSO-relative address to file/line information and, when requested, populates inline frame data. `symbol__disassemble_llvm()` disassembles one symbol into perf's annotation structures.

## Control Flow

There is no local control flow. Callers include this header and call the functions; runtime behavior is selected inside `llvm.c` based on compile-time LLVM support and runtime annotate options.

## State and Persistence Behavior

The header defines no state. Ownership contracts are implicit in the implementation: `file` may receive allocated storage, `node` may receive inline entries, and `annotate_args` is mutated during disassembly.

## Dependencies and Integration Points

It depends on `<stdbool.h>` and `<linux/types.h>` for `bool` and `u64`. It is consumed by annotation, symbol, and srcline users that want LLVM support without including LLVM C headers directly.

## Risks and Edge Cases

The API is compiled in regardless of whether LLVM is linked, so callers must handle negative or zero returns. The header's forward declarations mean type contract changes in annotation, symbol, or DSO code must stay synchronized with the implementation.

## Test Signals

Compile tests should cover builds with and without LLVM development headers. Functional tests should verify callers degrade when `llvm__addr2line()` or `symbol__disassemble_llvm()` returns failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.c

## Purpose

`lock-contention.c` provides shared helpers for perf lock contention aggregation. It parses call-stack filters, stores lock statistics in a hash table keyed by lock address, and tests whether sampled call stacks match requested kernel-symbol filters.

## Important APIs, Types, and Functions

`parse_call_stack()` consumes comma/space separated filter names into a private `callstack_filters` list. `needs_callstack()` reports whether call stacks must be collected. `lock_stat_find()` and `lock_stat_findnew()` search or create `struct lock_stat` entries in the global `lockhash_table` using `LOCKHASH_BITS`. `match_callstack_filter()` resolves stack IPs to kernel symbols with `machine__find_kernel_symbol()` and checks substring matches against filter names.

## Control Flow

Filter parsing duplicates the input string, tokenizes it with `strtok_r()`, allocates a variable-size `callstack_filter` for each token, and appends it to a list. Lock-stat lookup computes a bucket with `hash_long()` and linearly scans the bucket hlist. `lock_stat_findnew()` initializes new entries with address, duplicated name, flags, and `wait_time_min = ULLONG_MAX`. Call-stack matching exits early when no filters exist, walks up to `max_stack_depth`, handles powerpc zero entries in early LR/NIP positions specially, resolves kernel symbols, and returns true on the first substring match.

## State and Persistence Behavior

`callstack_filters` and `lockhash_table` are process-global state. The file allocates filter strings and lock names but does not provide a local teardown path; owning perf lock code is responsible for lifetime around one command invocation. `struct lock_stat` persists accumulated counts and timing across processed events until the command reports or frees it.

## Dependencies and Integration Points

The code depends on perf debug, env, machine, and symbol helpers plus Linux list, hlist, hash, and zalloc utilities. It integrates with perf lock's event/BPF readers through the shared structures in `lock-contention.h`, and with machine kernel symbol resolution for call-stack filters.

## Risks and Edge Cases

`lockhash_table` must be allocated before lookup or insertion. Filter matching uses substring comparison, so broad tokens can match unexpected lock functions. Powerpc zero-frame handling intentionally differs from other architectures. Allocation failures during parsing or lock creation are reported but can leave previously parsed filters installed. No synchronization is used here; callers must avoid concurrent mutation or provide external serialization.

## Test Signals

Tests should cover parsing comma and space separated filters, empty filter behavior, duplicate lock-address lookup, allocation failure handling where possible, powerpc call-stack zero handling, and symbol-name substring matches. Integration tests should compare perf lock results with and without call-stack filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.h

## Purpose

`lock-contention.h` defines the data model and helper interface for perf's lock contention reporting, including classic trace-event state tracking and optional BPF-backed collection hooks.

## Important APIs, Types, and Functions

Core types are `struct lock_filter`, `struct lock_delay`, `struct lock_stat`, `struct lock_seq_stat`, `struct thread_stat`, `struct lock_contention_fails`, and `struct lock_contention`. `lock_stat` stores address, name, optional call stack, counts, flags, timing aggregates, and sorting/combine metadata. Sequence states define acquire/acquired/contended/released transitions. Public helpers include `parse_call_stack()`, `needs_callstack()`, `lock_stat_find()`, `lock_stat_findnew()`, and `match_callstack_filter()`. With `HAVE_BPF_SKEL`, BPF lifecycle functions are declared; without it, inline stubs return success or NULL.

## Control Flow

The header itself has no runtime flow. It defines the state machine values consumed by perf lock event handlers and provides compile-time selection between real BPF hooks and no-op fallbacks.

## State and Persistence Behavior

`lockhash_table` is declared as shared global storage. `lock_contention` carries command-level state: evlist, target, machine, filters, delays, fail counters, cgroup tree, BTF handle, stack settings, aggregation mode, owner mode, and saved call-stack behavior. `lock_seq_stat` instances persist per-thread in `thread_stat.seq_list` while matching event sequences.

## Dependencies and Integration Points

It depends on Linux list/rbtree infrastructure and perf `evlist`, `machine`, and `target` abstractions. It integrates with tracepoints such as `lock:contention_begin`, kernel lock type flags, cgroup filters, BPF skeleton code, and perf lock reporting/sorting code.

## Risks and Edge Cases

The imported constants (`MAX_LOCK_DEPTH`, contention stack skip/depth, and `LCB_F_*`) must remain compatible with kernel trace-event definitions. Sequence tracking must tolerate missing first events because perf records can begin mid-sequence or lose events. The no-op BPF stubs mean feature availability must be checked by build configuration and command behavior, not just successful function calls.

## Test Signals

Validation should exercise trace-event and BPF builds, lock sequence transitions, read and trylock flags, owner-stack extraction, filters by type/address/symbol/cgroup/slab, and aggregation modes. Header compile tests should cover `HAVE_BPF_SKEL` on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lzma.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/lzma.c

## Purpose

`lzma.c` implements XZ/LZMA decompression helpers used by perf's compressed data paths. It can detect `.xz` magic and stream-decompress input into an output file descriptor.

## Important APIs, Types, and Functions

The public functions are `lzma_decompress_stream_to_file()`, `lzma_decompress_to_file()`, and `lzma_is_compressed()`. `lzma_strerror()` maps selected `lzma_ret` codes to debug strings. Decompression uses an `lzma_stream`, 8 KiB input/output buffers, `lzma_stream_decoder(..., LZMA_CONCATENATED)`, and perf's `writen()` helper.

## Control Flow

`lzma_decompress_to_file()` opens a named file and delegates to the stream helper. The stream helper initializes the decoder, fills input from `fread()` when needed, switches to `LZMA_FINISH` on EOF, repeatedly calls `lzma_code()`, writes full or final output buffers, and exits successfully only on `LZMA_STREAM_END`. `lzma_is_compressed()` opens the file, reads six bytes, and compares them with the XZ magic.

## State and Persistence Behavior

All decompressor state is local to the call and released with `lzma_end()`. Output is persistent only because bytes are written to the caller-provided file descriptor; this file does not own truncation, fsync, or close behavior. Debug messages are emitted on read, write, decoder, and format errors.

## Dependencies and Integration Points

The file depends on liblzma, stdio/fcntl/unistd, perf debug, internal `writen()`, and `compress.h` declarations. It integrates with DSO and data-file readers that need to unpack compressed kernel modules or perf artifacts.

## Risks and Edge Cases

Partial writes are treated as errors through `writen()` size comparison. Truncated, corrupt, unsupported, or non-XZ input all fail with debug output. `LZMA_CONCATENATED` accepts concatenated streams, which is intentional for `.xz` but should be understood by callers. `lzma_is_compressed()` returns false for unreadable or shorter-than-magic files, so callers must distinguish detection from open errors if that matters.

## Test Signals

Tests should decompress valid single and concatenated `.xz` files, reject corrupt/truncated/non-XZ inputs, simulate read and write errors, and verify magic detection on valid, short, missing, and uncompressed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/lzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/machine.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/machine.c

## Purpose

`machine.c` is the central perf model for a profiled address space. It owns host and guest machines, thread tables, DSO registries, kernel maps, event-driven mmap/task state, memory and branch sample resolution, callchain construction, current CPU-to-thread tracking, and kernel symbol helpers.

## Important APIs, Types, and Functions

Machine lifecycle APIs include `machine__init()`, `machine__new_host()`, `machine__new_live()`, `machine__new_kallsyms()`, `machine__exit()`, and `machine__delete()`. Multi-machine APIs include `machines__init()`, `machines__add()`, `machines__findnew()`, guest lookup, and guest processing. Thread APIs include `machine__findnew_thread()`, `machine__find_thread()`, `machine__idle_thread()`, `machine__remove_thread()`, and `machine__thread_list()`. Event processors cover COMM, NAMESPACES, CGROUP, MMAP/MMAP2, FORK, EXIT, LOST, AUX, SWITCH, KSYMBOL, BPF, TEXT_POKE, and AUX_OUTPUT_HW_ID. Kernel-map APIs include `machine__create_kernel_maps()`, `machine__destroy_kernel_maps()`, `machine__load_kallsyms()`, `machine__load_vmlinux_path()`, module creation, extra kernel maps, and x86_64 entry trampoline mapping. Resolution APIs include `sample__resolve_mem()`, `sample__resolve_bstack()`, `__thread__resolve_callchain()`, `machine__resolve_kernel_addr()`, and `machine__is_lock_function()`.

## Control Flow

Initialization creates `kmaps`, DSO/thread containers, root and mmap names, and guest placeholder threads. `machines__findnew()` resolves guest roots from `symbol_conf.guestmount` and inserts machines into a cached rb-tree. Perf event dispatch in `machine__process_event()` routes by event type. MMAP/MMAP2 events either update kernel/module maps for kernel cpumodes or create user maps and insert them into the target thread. FORK clones or initializes thread maps unless the synthesized fork-exec marker says not to; EXIT removes or marks threads. KSYMBOL and TEXT_POKE events update dynamic kernel/JIT symbol maps and DSO data caches. Kernel-map creation builds the kernel DSO, module maps, kallsyms relocation reference, extra maps, trampoline maps, and final map end fixups.

Callchain resolution first handles LBR call-stack mode when requested, then raw callchain and/or DWARF unwind depending on callchain order. It interprets context markers, resolves IPs to maps/symbols, handles parent and ignore-callee regexes, optional inline expansion, source-line caching, branch flags, loop removal, and LBR stitching across samples. Memory and branch-stack resolution use thread address-location helpers to populate `addr_map_symbol` records.

## State and Persistence Behavior

`struct machine` persists rb-tree linkage, pid, id-header size, comm behavior, root paths, `threads`, `dsos`, `kmaps`, `vmlinux_map`, kernel start cache, section ranges used for lock-function detection, current parallelism, per-CPU current TID array, private tool data, and trampoline mapping status. Event processing mutates thread comms, namespaces, maps, cgroups, kernel DSOs, dynamic symbols, and parallelism. `machine__is_lock_function()` lazily caches kernel section boundaries. Callchain processing may cache source lines and inline nodes in DSO trees and LBR stitch state in threads.

## Dependencies and Integration Points

This file is integrated with nearly every perf utility layer: callchain, branch, DSO, maps, threads, event decoding, env, evsel, hist, mem-events, mem-info, path, srcline, symbol, synthetic events, target, unwind, BPF events, cgroups, vdso, kallsyms, modules, libdw/libunwind hooks, architecture helpers, and kernel procfs/sysfs data. It is the bridge between raw perf events and higher-level report, script, annotate, mem, c2c, sched, and lock views.

## Risks and Edge Cases

Event streams may be out of order or incomplete, so thread PID repair, fork parent replacement, missing first lock events, missing maps, and zero kernel addresses are tolerated. Kernel mapping has many special cases: kcore disables later mmap processing, guest-injected mmap names may look like host names, module paths can be compressed, x86_64 PTI trampolines may lack symbols, and `kptr_restrict` may hide relocation addresses. `machine__init()` currently returns `0` even on the error path after cleanup, which is a risk if callers rely on nonzero failure. LBR stitching stores references that must be released when recycled. `sample__resolve_bstack()` assumes a branch stack exists and allocates by `bs->nr`.

## Test Signals

Good coverage includes host, live, kallsyms, and guest machine creation; synthesized MMAP/FORK streams; out-of-order fork/exit handling; kernel/module mmap with and without build IDs; ksymbol register/unregister; text poke updates; x86_64 trampoline mapping; cgroup and namespace events; current TID resizing; branch stack and memory resolution; callchains in caller/callee order with LBR, branch callstack, inline expansion, DWARF unwind, parent regex, hide-unresolved, and ignore-callee settings; and lock-function section detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/machine.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/machine.h

## Purpose

`machine.h` declares perf's machine and machines abstractions: the top-level state used to resolve events, threads, DSOs, maps, callchains, kernel symbols, host/guest machines, and per-CPU current thread information.

## Important APIs, Types, and Functions

`struct machine` contains guest rb linkage, pid, id header size, flags, root and mmap names, thread/DSO containers, perf environment, kernel maps, vmlinux map, cached kernel start, lock/sched/trace section ranges, parallelism, current TID array, private tool storage, parent `machines`, and trampoline status. `struct machines` contains the host machine and cached guest rb-root. The header declares lifecycle, event processing, thread lookup, sample resolution, callchain resolution, kernel map creation/destruction/loading, DSO iteration, kernel-map iteration, lock-function detection, current TID access, and kernel address resolver APIs.

## Control Flow

There is no implementation flow here, but the declarations define the normal caller flow: initialize machines, create kernel maps, process perf events through `machine__process_event()`, resolve samples/callchains, iterate threads or DSOs for reporting, then destroy maps and machines.

## State and Persistence Behavior

The struct layout defines long-lived mutable analysis state. Inline helpers expose the kernel map, kernel maps, host/default guest checks, lazy kernel-start lookup, kernel-IP classification, and kernel symbol lookup wrappers. Current TID state persists per CPU until updated by switch or tracking code.

## Dependencies and Integration Points

The header depends on rbtrees, maps, DSOs, rwsems, and threads. It is included by event readers, report/script/annotate/mem/lock tools, branch and callchain code, kernel symbol resolvers, and guest handling code.

## Risks and Edge Cases

Because many fields are public to perf internals, invariants depend on disciplined callers: maps and threads are refcounted, kernel maps must be created before kernel symbol lookup, and `machine->env` must be populated before architecture or CPU queries. The host kernel id is `-1` and default guest id is `0`, so callers must not treat pid values as ordinary process ids in machine trees.

## Test Signals

Compile coverage should include all major perf tools that include this header. Runtime tests should confirm host/default guest checks, kernel symbol wrappers, current TID helpers, event processor declarations, and callchain prototypes remain compatible with their implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/map.c

## Purpose

`map.c` implements perf's refcounted mapping object, which connects an address range to a DSO and translates between runtime IPs, DSO-relative addresses, and objdump addresses. It handles user maps, kernel maps, anonymous maps, Android library remapping, vdso namespace handling, symbol loading, and formatted map output.

## Important APIs, Types, and Functions

Constructors are `map__new()` for mmap events and `map__new2()` for known DSOs such as kernel/modules. Lifetime APIs are `map__clone()`, `map__put()`, `map__delete()`, and internal `map__exit()`. Symbol APIs include `map__load()`, `map__find_symbol()`, `map__find_symbol_by_name_idx()`, `map__find_symbol_by_name()`, `map__fixup_start()`, and `map__fixup_end()`. Address conversion APIs are `map__rip_2objdump()`, `map__objdump_2mem()`, and `map__objdump_2rip()`. Classification helpers identify kernel maps, extra kernel maps, BPF programs/images, out-of-line code, modules, anonymous/no-DSO memory, vdso, and entry trampolines.

## Control Flow

`map__new()` allocates a refcounted map, classifies the filename, obtains namespace info from the thread, rewrites executable anonymous/no-DSO maps to `/tmp/perf-<pid>.map`, rewrites Android library paths from environment variables, handles vdso maps by clearing namespace setns requirements and using `machine__findnew_vdso()`, otherwise finds or creates a DSO by id. It initializes map bounds, pgoff, DSO reference, protection, flags, and mapping type; anonymous/no-DSO maps become identity mappings and non-exec DSOs are marked loaded. Build IDs may be copied from a header DSO with the same name. Symbol lookup loads the DSO lazily and then searches by address or name. Address conversion branches on `dso__adjust_symbols()`, ET_REL, user/kernel DSO space, pgoff, text offset, relocation, and entry trampoline remapping.

## State and Persistence Behavior

Each map stores start, end, pgoff, reloc, DSO reference, refcount, prot, flags, mapping type, and warning/private/hit bits. Kernel DSOs allocate trailing `struct kmap` storage. Maps own a DSO reference until final put. Loading a map mutates DSO loaded/symbol state. `map__srcline()` and `map__fprintf_srcline()` depend on DSO source-line caches.

## Dependencies and Integration Points

The implementation depends on DSO, namespace, srcline, symbol, thread, vdso, machine, Linux mman flags, and perf debug/config globals. It is used by `maps.c`, `machine.c`, annotation/disassembly code, callchain resolution, perf report/script output, and any code that needs reliable address translation.

## Risks and Edge Cases

Android remapping depends on `APP_ABI`, `APK_PATH`, `NDK_ROOT`, and `APP_PLATFORM`. Executable anonymous maps are redirected to JIT map files only when namespace info is available. VDSO maps must not use container setns. The DSO deleted-name check is fragile around `(deleted)` suffix handling. Address conversion is easy to break because ET_EXEC, ET_DYN, ET_REL, kernel, kcore, and trampoline paths differ. `map__contains_symbol()` compares unmapped symbol start against runtime range and depends on correct mapping type.

## Test Signals

Tests should cover user shared libraries, ET_EXEC, ET_DYN, ET_REL, kernel maps, modules, vdso, anonymous executable JIT maps, Android path rewrites, BPF image/program classification, symbol load failures, map clone/refcount behavior, source-line formatting, and round trips through `rip_2objdump`, `objdump_2mem`, and `objdump_2rip`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/map.h

## Purpose

`map.h` defines the public structure and inline helpers for perf address maps. It is the contract for translating between process/kernel IPs and DSO offsets and for managing map lifetime.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(map)` stores start, end, pgoff, reloc, DSO pointer, refcount, protection, flags, mapping type, and status bits. `enum mapping_type` selects DSO-relative or identity address translation. Inline accessors expose fields and implement `map__dso_map_ip()`, `map__dso_unmap_ip()`, `map__map_ip()`, and `map__unmap_ip()`. Declared APIs cover constructors, get/put/zput, printing, source lines, loading, symbol lookup, fixups, kernel/BPF/OOL classification, address conversions, kmap access, and mutators.

## Control Flow

Most local flow is inline address conversion: DSO mappings subtract start and add pgoff for map IPs, while identity mappings return the input unchanged. The symbol-by-name iteration macros repeatedly call indexed lookup and advance through DSO name-sorted symbols until the default symbol-name match fails.

## State and Persistence Behavior

The header exposes mutable map state through setters. Refcounting is explicit with `map__get()`, `map__put()`, and `map__zput()`. Kernel map metadata is represented by trailing `struct kmap` storage accessed through functions declared here.

## Dependencies and Integration Points

The header depends on Linux refcount/list/rbtree/compiler/types, internal rc checking, DSO declarations, and symbol/thread/machine declarations. It is included by machine, maps, thread, annotation, mem, branch, and symbol code.

## Risks and Edge Cases

Inline access through `RC_CHK_ACCESS()` means callers must pass valid map objects. Incorrect mapping type silently changes all address resolution. The `map__for_each_symbol_by_name()` macro assumes DSO symbols are loaded and sorted by name. Anonymous/no-DSO detection is string based and must stay aligned with event filename conventions.

## Test Signals

Compile and unit tests should cover inline address translations for DSO and identity maps, refcount get/zput, setter/getter consistency, symbol iteration macros, anonymous/no-DSO classification strings, BPF image name recognition, and kernel map access error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.c

## Purpose

`map_symbol.c` implements small ownership helpers for bundled thread/map/symbol address-resolution results. These helpers keep reference counts correct when map-symbol records are copied or destroyed.

## Important APIs, Types, and Functions

`map_symbol__exit()` drops the contained thread and map references. `addr_map_symbol__exit()` delegates for the embedded `map_symbol`. `map_symbol__copy()` takes new references to source thread and map and copies the raw symbol pointer. `addr_map_symbol__copy()` copies the embedded map-symbol plus raw, resolved, physical, level, and page-size address fields.

## Control Flow

All functions are straight-line. Exit functions call `thread__zput()` and `map__zput()`. Copy functions use `thread__get()` and `map__get()` so the destination owns independent references to the same thread/map objects.

## State and Persistence Behavior

The functions mutate only the destination or target structures. Symbols are not refcounted here; their lifetime is expected to be tied to the referenced DSO/map. Address fields are plain value copies.

## Dependencies and Integration Points

The file depends on `map_symbol.h`, `maps.h`, `map.h`, and `thread.h`. It is used by memory info, branch info, callchain/LBR stitching, and address-location code that stores resolved IP/data addresses beyond a stack frame.

## Risks and Edge Cases

Copying into a destination that already owns references without first exiting it would leak those references. Raw symbol pointers can become stale if DSO symbols are deleted while records persist. Null thread/map inputs rely on `thread__get()`/`map__get()` tolerating null.

## Test Signals

Tests should check copy/exit refcount changes, null-safe behavior, repeated clone/free cycles through `mem_info__clone()`, and LBR stitch cleanup paths that use `map_symbol__exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.h

## Purpose

`map_symbol.h` defines compact containers for resolved perf addresses. It pairs a thread, map, and symbol with optional address metadata used by branch, memory, and callchain code.

## Important APIs, Types, and Functions

`struct map_symbol` contains `thread`, `map`, and `sym`. `struct addr_map_symbol` embeds `map_symbol` and adds original address, resolved address (`al_addr`), address level, physical address, and data page size. The header declares exit and copy helpers for both structures.

## Control Flow

No local runtime flow exists. Callers populate these records from address-location lookups, copy them when storing longer-lived sample data, and exit them to release references.

## State and Persistence Behavior

The structs are value containers. Thread and map fields are refcount-owned according to the helper functions; symbol is a borrowed pointer. Physical address and page size persist with memory sample data when supplied by the kernel.

## Dependencies and Integration Points

It depends on Linux integer types and forward declarations for thread, maps, map, and symbol. It is integrated with `mem_info`, branch stacks, callchain cursors, hist entries, and map/symbol resolution.

## Risks and Edge Cases

Borrowed `sym` lifetime depends on map/DSO stability. Callers must not mix shallow assignment with helper-managed ownership unless they understand refcounts. `al_level` is a char and should only store expected address-location level values.

## Test Signals

Compile coverage and ownership tests through `map_symbol__copy()`/`addr_map_symbol__copy()` are the main signals. Memory and branch sample tests should confirm copied records survive after temporary address locations are exited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/maps.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/maps.c

## Purpose

`maps.c` implements a refcounted, lock-protected collection of `struct map` objects for a machine or thread. It supports insertion, removal, lazy sorting, address and name lookup, overlap repair, map copying, kernel-map merging, unwinder state, and debug printing.

## Important APIs, Types, and Functions

The private `DECLARE_RC_STRUCT(maps)` stores an rwsem, arrays sorted by address and optionally by DSO name, parent machine pointer, unwind/libdw state, refcount, allocation counts, last name-search index, sorted flags, and `ends_broken`. Public APIs include `maps__new()`, `maps__get()`, `maps__put()`, `maps__insert()`, `maps__remove()`, `maps__remove_maps()`, `maps__for_each_map()`, `maps__find()`, `maps__find_by_name()`, `maps__find_symbol()`, `maps__find_symbol_by_name()`, `maps__find_ams()`, `maps__fixup_overlap_and_insert()`, `maps__copy_from()`, `maps__merge_in()`, `maps__fixup_end()`, and `maps__load_first()`.

## Control Flow

Insertions append maps, grow arrays geometrically, take references, and update sorted flags. Sorting by address or name happens lazily under a write lock; readers loop until sorted state is available. Address lookup uses binary search against sorted ranges; name lookup first checks the last-hit index, then binary-searches the name array, and falls back to linear scan if allocation for the name array fails. Overlap repair sorts by address, finds the first map ending after the new map starts, then removes, replaces, shortens, or splits existing maps so the new range fits. `maps__merge_in()` rebuilds the array when merging a map into overlapping kernel maps.

## State and Persistence Behavior

The collection owns references to maps in `maps_by_address` and, when allocated, additional references in `maps_by_name`. Removal and teardown put both references. Libunwind and libdw address-space state is stored in the maps object and invalidated on removal. `ends_broken` permits temporary construction states where map ends are missing or unordered until `maps__fixup_end()` repairs them.

## Dependencies and Integration Points

It depends on map, DSO, machine, thread, rwsem, unwind, libdw, debug, and UI globals. Thread maps, machine kernel maps, fork map cloning, mmap event handling, callchain/unwind access, and symbol resolution all depend on this file.

## Risks and Edge Cases

The locking note documents a race between sorting and later inserts; code retries but assumes inserts are rare. Callback iteration can be unsafe if callbacks insert maps, so the loop reloads array pointers each time and may skip or repeat entries. Name-array reallocation failure disables and rebuilds the index later. Overlap repair must preserve pgoff when splitting trailing ranges. Refcount balance is subtle because maps may live in two arrays.

## Test Signals

Tests should cover sorted and unsorted insertions, address/name lookup, last-name cache hits, name-array allocation failure fallback, removal from both arrays, overlap cases where a new map covers, splits, trims before, or trims after an existing map, map copying from parent threads, `maps__merge_in()` with overlapping kernel maps, `maps__fixup_end()` for missing ends, and libdw invalidation on removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/maps.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/maps.h

## Purpose

`maps.h` declares the map-collection interface and kernel-map metadata used by perf machines and threads.

## Important APIs, Types, and Functions

`struct kmap` stores an optional relocation reference symbol, owning `maps`, and a fixed-size name for extra kernel maps. Public functions cover lifecycle, emptiness/equality, copying, iteration, removal by callback, parent machine access, refcount access for tests, libunwind/libdw accessors, printing, insert/remove, address and symbol lookup, `addr_map_symbol` lookup, overlap insertion, lookup by DSO name, next-entry lookup, merging, end fixup, and first-map loading.

## Control Flow

There is no implementation flow in the header. It defines the operations that callers use to mutate maps under implementation-managed locking and lookup symbols from address collections.

## State and Persistence Behavior

`struct maps` is opaque, so state is owned by `maps.c`. `struct kmap` is embedded behind kernel maps and persists with the map. Refcounting is exposed through `maps__get()`, `maps__put()`, and `maps__zput()`.

## Dependencies and Integration Points

The header depends on Linux refcount/types and perf machine/map declarations. It is used by `machine.c`, `map.c`, thread map handling, unwind code, and symbol resolution code.

## Risks and Edge Cases

Because `struct maps` is opaque, callers must not assume storage shape and must use accessors. `maps__nr_maps()` and `maps__refcnt()` are marked test-only. Kernel map names are capped by `KMAP_NAME_LEN`, so copying must use bounded string helpers.

## Test Signals

Header-level tests are compile and ABI-style tests through all map users. Functional tests should verify every declared operation is implemented and keeps refcount and locking behavior consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/maps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem-events.c

## Purpose

`mem-events.c` implements perf memory-event selection and memory data-source formatting/statistics. It builds `perf record -e` arguments for load/store memory sampling PMUs, lists and parses memory event tags, formats `perf_mem_data_src` fields for scripts, and decodes c2c and histogram memory statistics.

## Important APIs, Types, and Functions

Global defaults are `perf_mem_events__loads_ldlat = 30`, `perf_mem_events[]`, and `perf_mem_record[]`. PMU/event APIs include `perf_pmu__mem_events_ptr()`, `perf_mem_events_find_pmu()`, `perf_pmu__mem_events_num_mem_pmus()`, `perf_pmu__mem_events_parse()`, `perf_pmu__mem_events_init()`, `perf_pmu__mem_events_list()`, `perf_mem_events__record_args()`, and `is_mem_loads_aux_event()`. Formatting APIs include `perf_mem__tlb_scnprintf()`, `perf_mem__lvl_scnprintf()`, `perf_mem__snp_scnprintf()`, `perf_mem__lck_scnprintf()`, `perf_mem__blk_scnprintf()`, and `perf_script__meminfo_scnprintf()`. Stats APIs include `c2c_decode_stats()`, `c2c_add_stats()`, `mem_stat_index()`, and `mem_stat_name()`.

## Control Flow

PMU scanning walks all PMUs with `perf_pmus__scan()` and selects those with `mem_events`. Parsing duplicates the user's comma-separated string, marks matching `perf_mem_record` slots by tag substring, and reports an error if none match. Initialization checks sysfs for each PMU event file and marks supported entries. Record-arg generation allocates one storage buffer sized by PMU count and event count, emits `-e <event>` pairs for requested supported events, handles load-latency and auxiliary event name templates, and warns when memory PMUs cover only a CPU subset. Formatting functions decode bitfields into fixed strings for TLB, level, snoop, lock, and block dimensions. `c2c_decode_stats()` classifies one sample into load/store, cache/DRAM/HITM/peer/blocking/no-map counters and returns errors for missing addresses or unparsable data. `mem_stat_index()` maps `perf_mem_data_src` fields into compact histogram bucket indexes.

## State and Persistence Behavior

Global `perf_mem_record[]` persists selected memory event kinds for command construction. Each PMU's `mem_events[j].supported` bit is updated from sysfs. `perf_mem_events__record_args()` returns heap storage through `event_name_storage_out`; argv entries point inside that buffer and require caller lifetime management. Stats functions mutate caller-owned `c2c_stats`.

## Dependencies and Integration Points

This file depends on sysfs mount discovery, PMU and PMU list handling, CPU maps, evsel, debug output, `mem_info`, map-symbol data, Linux perf memory data-source bitfields, and c2c/hist consumers. It integrates with `perf mem`, `perf c2c`, `perf script`, and memory-focused reporting.

## Risks and Edge Cases

Tag parsing uses `strstr(e->tag, tok)`, so partial tokens can match more than expected. `perf_pmu__mem_events_init()` returns `-ENOENT` if any scanned memory PMU fails initialization, which can be strict on heterogeneous systems. Event-name storage sizing assumes 128 bytes per event. Several formatters subtract one from `sz` and then use `strcat()`, so callers must pass nonzero buffers. `perf_script__meminfo_scnprintf()` passes `sz` rather than `sz - i` to the level formatter, which deserves attention in boundary tests. c2c classification relies on architecture-populated data-source bits and can mark samples as no-address or no-map.

## Test Signals

Tests should cover PMU scans with zero, one, and multiple memory PMUs; load, store, and load-store event templates; Intel auxiliary load events; unsupported sysfs events; CPU subset warnings; parsing exact and partial tags; formatting every memory data-source category; small output buffers; c2c load/store/HITM/peer/remote/blocked/no-address/no-map cases; and histogram bucket mappings for op, cache, memory, snoop, and DTLB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem-events.h

## Purpose

`mem-events.h` declares perf memory-event selection, formatting, cache-to-cache statistics, and memory-stat bucket APIs.

## Important APIs, Types, and Functions

`struct perf_mem_event` describes one PMU memory event template with support, load-latency, optional auxiliary config, tag, event-name format, and sysfs event name. Enums define load/store/load-store slots and memory stat types/buckets. `struct c2c_stats` stores counters for locks, stores, loads, cache hits, HITM, peer hits, DRAM locality, blocking, missing maps, and parse failures. The header declares PMU initialization/list/parse/record APIs, data-source formatting APIs, c2c decode/add APIs, and stat index/name APIs.

## Control Flow

No local runtime flow exists. Callers typically initialize PMU memory events, parse user selections, generate record arguments, then format and aggregate memory samples during reporting.

## State and Persistence Behavior

The header exposes global `perf_mem_events__loads_ldlat`, `perf_mem_events[]`, and `perf_mem_record[]`. Those globals are command-level state and affect later record-argument generation.

## Dependencies and Integration Points

It depends on Linux types and perf `evsel`, `mem_info`, and `perf_pmu` declarations. It is used by perf mem, perf c2c, perf script, hist sorting, and memory sample resolution code.

## Risks and Edge Cases

Bucket enums and `MEM_STAT_PRINT_LEN` must stay aligned with display code. Adding a new memory level or data-source field requires updates in both index and name functions. Global selection state means independent command phases must reset or initialize it intentionally.

## Test Signals

Compile tests should cover users of every declared API. Functional tests should validate each enum bucket maps to a display name and that c2c counters remain large enough for expected workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-info.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem-info.c

## Purpose

`mem-info.c` implements refcounted ownership for `struct mem_info`, the perf object that stores resolved instruction and data addresses plus memory data-source metadata for a sample.

## Important APIs, Types, and Functions

`mem_info__new()` allocates and initializes a refcounted `mem_info`. `mem_info__get()` increments the refcount. `mem_info__put()` decrements, exits embedded instruction/data `addr_map_symbol` fields, and frees on the final put. `mem_info__clone()` allocates a new object, deep-copies address map-symbol references with `addr_map_symbol__copy()`, and copies the data-source value.

## Control Flow

Creation uses `zalloc()` and `ADD_RC_CHK()`, then sets refcount to one. Put either frees on final reference or records an rc-check put. Clone is allocate-then-copy and returns NULL on allocation failure.

## State and Persistence Behavior

The object owns references embedded in its instruction and data address records. `data_src.val` is copied by value and persists with the object. Final destruction releases map/thread references through `addr_map_symbol__exit()`.

## Dependencies and Integration Points

It depends on `mem-info.h`, `map_symbol` ownership helpers, Linux zalloc, refcounting, and rc-check infrastructure. It is used by `sample__resolve_mem()`, hist entries, perf mem, perf c2c, and script formatting.

## Risks and Edge Cases

`mem_info__clone()` assumes the source is valid and does not copy any future fields unless updated. Borrowed symbol pointers inside the copied `addr_map_symbol` remain tied to DSO lifetime. Callers must not double-put or shallow-copy without ownership awareness.

## Test Signals

Tests should cover new/get/put finalization, clone independence of map/thread references, NULL put handling, and integration with memory sample resolution and c2c stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-info.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem-info.h

## Purpose

`mem-info.h` defines the refcounted memory sample metadata object used across perf memory analysis.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(mem_info)` contains instruction address `iaddr`, data address `daddr`, `union perf_mem_data_src data_src`, and `refcount_t refcnt`. The header declares new/clone/get/put and defines zput plus inline accessors for instruction address, data address, data source, const data source, and refcount.

## Control Flow

There is no implementation flow. Inline accessors return addresses of fields through rc-check access.

## State and Persistence Behavior

`mem_info` persists resolved address metadata and kernel-provided memory data-source bits. Refcounting controls lifetime; embedded map-symbol fields own thread/map references according to implementation helpers.

## Dependencies and Integration Points

It depends on Linux refcount, perf event memory data-source definitions, rc-check infrastructure, and `map_symbol.h`. It is consumed by machine sample resolution, mem-events formatting, c2c, hist entries, and scripts.

## Risks and Edge Cases

All accessors assume a valid `mem_info` pointer. The object contains borrowed symbol pointers through `addr_map_symbol`, so map/DSO lifetime must be managed by the owned map references. Any new field must be added to clone and free paths.

## Test Signals

Compile tests should cover accessors in const and mutable contexts. Runtime tests should verify zput nulls pointers and final put releases embedded address references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem2node.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem2node.c

## Purpose

`mem2node.c` builds a physical-address-to-NUMA-node lookup table from `perf_env` memory node bitmaps. It lets memory analysis map sampled physical addresses to NUMA nodes.

## Important APIs, Types, and Functions

The private `struct phys_entry` stores rb-node linkage, start, end, and node id. `mem2node__init()` builds and inserts merged physical ranges. `mem2node__exit()` frees the entries array. `mem2node__node()` searches the rb-tree and returns the node or `-1`.

## Control Flow

Initialization clears the map, counts all set memory-block bits across environment nodes, allocates that many entries, walks node bitmaps in order, converts each set bit to `start = bit * memory_bsize`, merges adjacent blocks from the same node, shrinks the array with `realloc()`, logs ranges, inserts each range into an rb-tree ordered by start, and stores the entry array. Lookup descends the rb-tree by comparing the address with entry start/end.

## State and Persistence Behavior

The map owns one contiguous `entries` allocation and rb-tree nodes embedded in that allocation. It persists until `mem2node__exit()`. The `cnt` field in the header is not populated by this implementation.

## Dependencies and Integration Points

The file depends on `perf_env` memory node data, Linux bitmaps, rbtrees, kernel macros, zalloc, debug output, and warnings. It integrates with perf mem/c2c NUMA locality reporting where physical addresses are available.

## Risks and Edge Cases

If no memory nodes are present, a warning mentions `CONFIG_MEMORY_HOTPLUG`; the `realloc(entries, 0)` path can set `entries` to NULL and still continue safely only because insertion count is zero. Ranges are sorted by iteration order within each node, but nodes themselves may produce interleaved ranges; the rb-tree handles lookup but merge only occurs for adjacent blocks encountered consecutively. The unused `cnt` field may mislead callers if they expect a count.

## Test Signals

Tests should build maps from empty, single-node, multi-node, adjacent, and interleaved bitmaps; verify merged ranges and lookup boundaries; query holes and end addresses; and check cleanup under allocation and zero-node cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem2node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem2node.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/mem2node.h

## Purpose

`mem2node.h` declares the physical memory to NUMA node mapping helper.

## Important APIs, Types, and Functions

`struct mem2node` contains an rb-tree root, an owned array of physical entries, and a `cnt` field. Public APIs are `mem2node__init()`, `mem2node__exit()`, and `mem2node__node()`.

## Control Flow

There is no implementation flow. Callers initialize from a `perf_env`, query addresses, then exit to release storage.

## State and Persistence Behavior

The struct stores lookup state derived from environment memory-node snapshots. It is caller-owned and must be initialized before lookup.

## Dependencies and Integration Points

It depends on Linux rbtrees and integer types plus `struct perf_env`. It is used by memory analysis code that has physical addresses and wants NUMA attribution.

## Risks and Edge Cases

The `struct phys_entry` type is opaque to callers. The `cnt` field is declared but not set by the current implementation, so callers should not rely on it unless the implementation changes.

## Test Signals

Compile tests should verify callers can allocate the struct on stack or heap. Runtime tests should verify init/query/exit sequencing and unknown address behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mem2node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/memswap.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/memswap.c

## Purpose

`memswap.c` provides in-place byte-swap helpers for 32-bit and 64-bit words. It supports perf data handling where endianness conversion is needed for arrays of fixed-width values.

## Important APIs, Types, and Functions

`mem_bswap_32(void *src, int byte_size)` treats the buffer as `u32` words and applies `bswap_32()` while decrementing by four bytes. `mem_bswap_64(void *src, int byte_size)` does the same for `u64` words with `bswap_64()`.

## Control Flow

Both functions are simple loops: cast the pointer, swap the current word, decrement `byte_size` by the word width, and advance to the next word until `byte_size <= 0`.

## State and Persistence Behavior

The functions mutate the caller-provided memory in place and allocate no state. Converted bytes persist in the supplied buffer.

## Dependencies and Integration Points

The file depends on `<byteswap.h>`, Linux integer types, and `memswap.h`. It integrates with perf file/event readers that need endian conversion of numeric arrays.

## Risks and Edge Cases

The functions assume `byte_size` is a multiple of the word size and that `src` is suitably aligned for `u32` or `u64` access on the target architecture. Negative or non-multiple sizes are not validated; a non-multiple positive size still swaps a full final word. Callers are responsible for choosing the correct width.

## Test Signals

Tests should cover known 32-bit and 64-bit patterns, zero sizes, multiple elements, non-host-endian perf data fixtures, and sanitizer/alignment checks on strict-alignment architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/memswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/memswap.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/memswap.h

## Purpose

`memswap.h` declares fixed-width memory byte-swap helpers and a small union useful for viewing a 64-bit value as two 32-bit words.

## Important APIs, Types, and Functions

`union u64_swap` exposes `val64` and `val32[2]`. The declared functions are `mem_bswap_64()` and `mem_bswap_32()`.

## Control Flow

There is no local flow. Callers include this header and invoke the implementation on mutable buffers.

## State and Persistence Behavior

The header defines no global state. The union is a value type; swap functions mutate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux integer types. It is used by perf data parsing or conversion code that handles cross-endian data.

## Risks and Edge Cases

The API accepts byte counts rather than element counts, so callers must pass correctly sized buffers. The union can expose endian-sensitive word order and should be used carefully.

## Test Signals

Compile tests should cover both function declarations and union usage. Runtime tests should validate byte-order conversion with representative perf data values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/memswap.h -->
