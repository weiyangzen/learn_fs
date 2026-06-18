# subset-b-006756 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.c

Purpose: implements perf's Arm Statistical Profiling Extension AUX trace decoder glue. It consumes `PERF_RECORD_AUXTRACE_INFO` metadata and queued AUX buffers, drives the low-level Arm SPE packet decoder, and synthesizes normal perf samples for memory hierarchy, TLB, branch, remote-access, memory, and instruction views.

Important APIs and functions: `arm_spe_process_auxtrace_info()` is the public entry point registered from generic auxtrace dispatch. It parses v1/v2 metadata, initializes `struct arm_spe`, installs auxtrace callbacks on the session, chooses timeless versus timestamped decoding, creates synthetic event attributes through `arm_spe_synth_events()`, and processes any auxtrace index. Runtime callbacks are `arm_spe_process_event()`, `arm_spe_process_auxtrace_event()`, `arm_spe_flush()`, `arm_spe_free_events()`, `arm_spe_free()`, and `arm_spe_evsel_is_auxtrace()`. Queue-local state lives in `struct arm_spe_queue`; session state lives in `struct arm_spe`.

Control flow: AUX trace events are queued with `auxtrace_queues__add_event()`. `arm_spe__setup_queue()` allocates a queue decoder and, for timestamped sessions, decodes the first record to seed the auxtrace heap. `arm_spe_process_queues()` repeatedly pops the earliest queue, updates pid/tid from context-switch state unless SPE context packets are being used, runs `arm_spe_run_decoder()`, and re-adds the queue if more records remain before the next perf event timestamp. Timeless decoding instead drains matching queues on exit or flush. `arm_spe_run_decoder()` intentionally synthesizes the previous decoded record before decoding the next one so records can be deferred for global time ordering.

State and persistence: SPE metadata is copied from the auxtrace info record into per-CPU `u64` arrays and freed at session shutdown. Per-queue buffers are lazily mmaped or loaded through auxtrace helpers, with old buffer data dropped after the next non-empty buffer is accepted. Synthetic event ids are deterministic offsets from the original SPE evsel id range. The code persists no files itself; it mutates the perf session, evlist names, machine current tid state, and DSO/thread references.

Dependencies and integration points: depends on `auxtrace.*`, `arm-spe-decoder`, perf session/machine/thread APIs, tsc conversion, synthetic event delivery, and Arm MIDR ranges from arm64 CPU type headers. It integrates with `perf report/script/inject` through synthesized sample events and with perf's ordered-events requirement for timestamped trace.

Risks: correctness depends on complete metadata, especially on heterogeneous systems where per-thread queues have CPU `-1`. Old v1 metadata falls back to global `cpuid`, reducing data-source accuracy. Context attribution can be inaccurate when SPE CONTEXT packets are absent and context-switch events are incomplete. Branch stack synthesis only supports up to two entries. Memory data-source decoding encodes CPU-family-specific assumptions and may need updates for new cores or cache topologies. Error handling skips malformed decoder records, which is useful for robustness but can hide trace quality problems unless debug output is inspected.

Test signals: useful checks include decoding real Arm SPE perf.data with timestamped and timeless modes, `--itrace` combinations for `f/m/t/a/M/b/i/l`, perf inject output validation, heterogeneous metadata fixtures, no-CONTEXT-packet warning paths, data-source expectations on known MIDR values, and leak/error tests around queued buffers and decoder allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.h

Purpose: declares the Arm SPE perf integration contract and metadata layout used in AUXTRACE_INFO private data. It provides the shared constants needed by recording-side setup and decoding-side processing.

Important APIs and types: `ARM_SPE_PMU_NAME` identifies SPE PMUs by prefix. The first enum describes legacy v1 private fields, including PMU type and per-CPU mmap mode. The second enum describes v2 header fields: version, header size, shared PMU type, and CPU count. The third enum describes per-CPU metadata slots: magic, CPU logical id, parameter count, MIDR, PMU type, minimal interval, and event filter capability. Public functions are `arm_spe_recording_init()`, `arm_spe_process_auxtrace_info()`, and `arm_spe_pmu_default_config()`.

Control flow: this header does not implement control flow. It binds the recording side, which fills auxtrace info and default PMU config, to the decoding side in `arm-spe.c`, which validates and interprets the metadata.

State and persistence: the metadata enums define the stable serialized format stored inside perf.data AUXTRACE_INFO records. `ARM_SPE_HEADER_CURRENT_VERSION` is the current writer version and must remain compatible with the parser's legacy v1 detection.

Dependencies and integration points: forward declares perf event, session, and PMU types so Arm SPE can be conditionally integrated into perf record and report without exposing implementation internals.

Risks: enum order is ABI-like for perf.data files. Reordering or changing sizes would break older/newer perf interop. Additions need coordinated writer and reader changes, especially when heterogeneous CPU support needs new per-CPU parameters.

Test signals: perf.data compatibility tests should cover old v1 metadata, current v2 metadata with multiple CPUs, absent optional capability fields, and cross-version decode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.c

Purpose: provides an AArch64-specific helper to recover the caller of the leaf frame when frame-pointer callchain recording has captured LR but not enough unwind context.

Important APIs and functions: `get_leaf_frame_caller_aarch64()` is the exported helper. `get_leaf_frame_caller_enabled()` gates the logic to `CALLCHAIN_FP` mode and requires a recorded `PERF_REG_ARM64_LR`. `add_entry()` collects up to two unwind IP entries from `unwind__get_entries()`.

Control flow: the helper first checks that frame-pointer mode and LR are available. It snapshots the sample's user regs, then temporarily fills cached PC and SP values if the sample did not record them. PC is taken from the user callchain entry after `usr_idx`, and SP is set to zero because the unwind path requires it even though it is not used by this recovery. It then asks generic unwind code for two entries and restores the original regs. The return value depends on callchain order: caller-first returns the first collected IP, callee-first returns the second.

State and persistence: state is strictly temporary in the provided `perf_sample`. The function saves and restores `struct regs_dump`, so no persistent mutation should remain after the call.

Dependencies and integration points: uses perf callchain globals, `perf_sample__user_regs()`, generic unwind support, and AArch64 perf register definitions. It is integrated where perf needs to fix or augment frame-pointer callchains for arm64 leaf frames.

Risks: the function returns `ret` when unwinding fails, even though the function type is `u64`; negative errors become large unsigned values unless callers treat non-canonical IPs carefully. It assumes `sample->callchain` and `usr_idx + 1` are valid when PC is missing. Cache register masks are set rather than normal masks, so behavior depends on unwind code honoring cache fields.

Test signals: arm64 frame-pointer callchain tests should cover missing PC, missing SP, missing LR, both callchain orders, unwind failure, short callchains, and verification that regs are restored after the helper returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.h

Purpose: declares the AArch64 frame-pointer leaf caller recovery helper.

Important APIs and types: forward declares `struct perf_sample` and `struct thread`, includes Linux integer types, and exports `u64 get_leaf_frame_caller_aarch64(struct perf_sample *sample, struct thread *thread, int user_idx)`.

Control flow: no executable control flow; the header gives architecture-specific callchain code a narrow entry point without exposing register or unwind internals.

State and persistence: no state is defined here.

Dependencies and integration points: consumed by callchain or unwind paths that need arm64-specific frame-pointer support. The implementation includes AArch64 UAPI perf register names.

Risks: the signature exposes only `user_idx`; callers must ensure that index is valid for the sample callchain. Include guard naming differs slightly from the file name but is conventional enough.

Test signals: compile coverage on arm64 and non-arm64 build combinations is the main signal; runtime behavior is covered through the `.c` helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.c

Purpose: provides perf's generic AUX area tracing infrastructure. It manages AUX mmap setup, ring-buffer reads, AUX buffer queues and indexes, auxtrace record callbacks, instruction-trace option parsing, synthetic auxtrace info/error events, cache helpers, address filters, and dispatch to hardware-specific decoders such as Intel PT, Intel BTS, CoreSight ETM, Arm SPE, s390 CPU-MF, Hisilicon PTT, and PowerPC VPA DTL.

Important APIs and functions: mmap helpers include `auxtrace_mmap__mmap()`, `auxtrace_mmap__read()`, and `auxtrace_mmap__read_snapshot()`. Queue helpers include `auxtrace_queues__init()`, `auxtrace_queues__add_event()`, `auxtrace_queues__add_sample()`, `auxtrace_queues__process_index()`, `auxtrace_buffer__get_data_rw()`, and `auxtrace_buffer__drop_data()`. Heap helpers provide timestamp ordering. Recording wrappers call `struct auxtrace_record` methods. Session dispatchers include `perf_event__process_auxtrace_info()`, `perf_event__process_auxtrace()`, `auxtrace__process_event()`, and `auxtrace__flush_events()`. Option parsing is handled by `itrace_do_parse_synth_opts()`.

Control flow: recording maps AUX areas, reads producer head/tail, packages new bytes into `PERF_RECORD_AUXTRACE`, and writes padding/alignment. Reporting reads AUXTRACE_INFO, delegates to a type-specific processor that installs session callbacks, queues AUX buffers either from the auxtrace index or from streamed events, then lets the decoder consume buffers in event order. Address-filter control flow parses textual filters, resolves symbols through kallsyms or DSO symbol tables, and replaces user-facing filters with concrete address ranges.

State and persistence: AUX trace index entries are stored as lists of fixed-size chunks and written to perf.data. `auxtrace_queues` own buffer lists with file offsets, mmap pointers, copied pipe data, and monotonically assigned buffer numbers. The auxtrace cache is an in-memory hash table with a count limit that drops all entries when exceeded. Parsed `itrace_synth_opts` live in the session. Address filters mutate evsel filter strings after symbol resolution.

Dependencies and integration points: integrates tightly with perf session/data/event parsing, mmap code, evlist/evsel, record options, PMU capabilities, kallsyms, DSO maps, synthetic events, and type-specific auxtrace implementations. It also contains 32-bit compatibility helpers for reading/writing 64-bit AUX head/tail when the kernel is 64-bit.

Risks: AUX ring-buffer arithmetic must handle wraparound, non-power-of-two sizes, snapshots, and alignment correctly. Queue growth currently leaks the old queue array after copying to a new array because it assigns `queues->queue_array = queue_array` without freeing the old array; this should be checked against surrounding ownership assumptions. `auxtrace_cache__remove()` calls `auxtrace_cache__free_entry()` even when lookup returns NULL; `free(NULL)` is safe, but custom overrides would need care. Address-filter symbol resolution depends on available kallsyms/DSO symbols and may fail under `kptr_restrict`. Option parsing packs many flags into compact syntax, making regression tests important.

Test signals: test with pipe and regular perf.data inputs, indexed and non-indexed AUX records, AUX samples, 32-bit compat head/tail paths, snapshots, overwrite and non-overwrite mmaps, `--itrace` syntax including bad inputs, `--aux-sample` grouping rules, address filters using kernel symbols, DSO symbols, duplicates, and permission-restricted kallsyms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.h

Purpose: defines perf's public AUX trace data structures, callback interfaces, option structures, enums, inline head/tail helpers, and declarations for the implementation in `auxtrace.c`.

Important APIs and types: `enum auxtrace_type` enumerates supported trace producers. `struct itrace_synth_opts` is the central decoded `--itrace` option state. `struct auxtrace` is the decoder callback vtable installed in `perf_session`. `struct auxtrace_buffer`, `auxtrace_queue`, `auxtrace_queues`, and `auxtrace_heap` describe queued trace storage and time ordering. `struct auxtrace_record` is the recording-side callback vtable. `struct addr_filter` and `addr_filters` model address filter specifications before/after resolution.

Control flow: inline `auxtrace_mmap__read_head()` and `auxtrace_mmap__write_tail()` enforce memory ordering around AUX ring buffer producer/consumer pointers. Other declarations route recording setup, sample/event queueing, decoder flushing, error synthesis, cache use, and filter parsing to `auxtrace.c`.

State and persistence: the header defines serialized `auxtrace_index_entry` format and in-memory buffer metadata that points either into perf.data, mmaped file regions, one-mmap memory, or copied pipe data. `itrace_synth_opts` persists user decode choices across the session.

Dependencies and integration points: includes Linux perf event ABI, barriers, cpumap, list and type conventions. It is included by hardware-specific decoders, perf record, perf report/script, and utility code that needs AUX data or instruction-trace options.

Risks: structure fields are heavily shared across perf subsystems; changing them has broad compile and behavior impact. The option struct has many booleans with overlapping meanings, so initialization defaults must be explicit. Head/tail memory barriers are correctness-critical for lockless communication with the kernel.

Test signals: build coverage across all auxtrace producers, static assertions or ABI review for serialized structures, and runtime tests for option parsing and mmap ring-buffer consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/auxtrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/blake2s.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/blake2s.c

Purpose: implements the BLAKE2s compression, update, and finalization routines used by perf utilities that need a small keyed or unkeyed hash/PRF implementation.

Important APIs and functions: public functions are `blake2s_update()` and `blake2s_final()`. Internal helpers include `ror32()`, endian conversion helpers, `blake2s_increment_counter()`, `blake2s_compress()`, and `blake2s_set_lastblock()`. The compression function uses the standard 10-round BLAKE2s sigma schedule and IV constants from the header.

Control flow: callers initialize a `blake2s_ctx` via inline header helpers, feed arbitrary input through `blake2s_update()`, and call `blake2s_final()` to pad the final block, mark it final, compress it with the real byte count, output little-endian digest bytes, and zero the context. `blake2s_update()` fills a partial buffer, compresses full blocks while leaving the final block buffered, and appends remaining bytes.

State and persistence: all state is held in `struct blake2s_ctx`: chaining state, byte counter, finalization flags, partial block, buffer length, and output length. Finalization wipes the context after copying the digest. There is no file or global state.

Dependencies and integration points: uses Linux kernel-style endian helpers, `ARRAY_SIZE`, `DIV_ROUND_UP`, `unlikely`, and standard `memcpy`/`memset`. It is self-contained and licensed GPL-2.0 OR MIT.

Risks: callers must provide valid `outlen`, key length, and output buffers; the code does not perform runtime bounds checks against BLAKE2s maximum digest/key sizes. Counter increments assume the `inc` value selected by update/final logic. Cryptographic regressions are subtle and require known-answer tests.

Test signals: BLAKE2s known-answer vectors for empty input, single block, multi-block, keyed mode, all digest lengths in supported range, incremental updates with varied chunk boundaries, and context wipe checks after finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/blake2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/blake2s.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/blake2s.h

Purpose: declares the BLAKE2s context, IV constants, inline initialization helpers, and streaming API.

Important APIs and types: `struct blake2s_ctx` stores hash state, counters, finalization flags, buffer, buffer length, and output length. `enum blake2s_iv` provides the eight 32-bit IV constants. `blake2s_init()` initializes unkeyed hashing, `blake2s_init_key()` initializes keyed hashing, and `blake2s_update()`/`blake2s_final()` complete the streaming API.

Control flow: initialization sets the parameter block into `h[0]`, clears counters and flags, sets output length, and, for keyed hashing, preloads a full padded key block so the first update/final path processes it correctly.

State and persistence: context state is caller-owned. The header does not allocate or persist anything globally.

Dependencies and integration points: depends on Linux integer types and string routines. Consumers include code that needs a compact in-tree hash without linking external crypto libraries.

Risks: no explicit validation enforces maximum BLAKE2s digest or key sizes; misuse can overrun `ctx->buf` during keyed init if caller passes an invalid key length. The inline init is part of each translation unit and must stay in sync with the compression implementation.

Test signals: compile with all consumers, run known-answer vectors through both keyed and unkeyed init paths, and test invalid or boundary sizes where callers constrain inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/blake2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-info.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/block-info.c

Purpose: builds and renders perf block-level reports from annotated branch/cycle histograms. It converts per-symbol cycle histogram entries into `hist_entry` rows representing program block ranges and registers report columns for text or TUI browsing.

Important APIs and functions: `block_info__process_sym()` extracts block records from a symbol's `annotation->branch->cycles_hist`. `block_info__create_report()` creates one block report per evsel. `block_info__free_report()` releases reports. `report__browse_block_hists()` displays block hists through stdio or TUI. Column callbacks include total cycles percent, sampled cycles, average cycles percent, average cycles, block range, DSO, and branch counter formatting.

Control flow: for each evsel's hists, `process_block_report()` initializes a dedicated `block_hist`, registers requested columns, walks existing histogram entries, and calls `block_info__process_sym()` for entries with symbols and maps. Each populated cycle histogram offset creates a `block_info`, copies cycle and branch-counter data, adds a block hist entry, accumulates aggregate cycles, then resorts output.

State and persistence: `block_info` instances are heap allocated and owned by hist entries. `block_report` arrays are heap allocated per evlist and must be freed with `block_info__free_report()`. The code mutates `symbol_conf.report_individual_block` while browsing. It persists no files.

Dependencies and integration points: depends on annotation data, symbols, maps, DSOs, srcline lookup, perf hpp formatting, hists, evlist/evsel, and optional slang browser support. It consumes branch counter metadata from annotations and evlist.

Risks: `block_avg_cycles_entry()` divides by `bi->num_aggr`; construction only creates entries when `num_aggr` is nonzero, but future callers must preserve that invariant. Srcline lookups can be expensive and unavailable. Branch counter arrays require correct `br_cntr_nr` sizing. Sorting and formatting assume `he->block_info` is populated.

Test signals: report generation with and without symbols, with unknown srclines, with branch counters, text and TUI browser modes, multiple evsels, zero total cycles, and memory cleanup under allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-info.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/block-info.h

Purpose: declares data structures and APIs for block-level perf reports.

Important APIs and types: `struct block_info` captures symbol, start/end offsets, sampled and aggregate cycles, sparkline buckets, total cycles, hit counts, branch counters, and owning evsel. `struct block_fmt` wraps `perf_hpp_fmt` with block-specific widths and totals. The enum lists supported block report columns. `struct block_report` contains a `block_hist`, cycle total, registered formatters, and formatter count.

Control flow: no implementation flow; callers create reports, browse block hists, free reports, compare entries, and compute total cycle percentages through declarations here.

State and persistence: structures are in-memory report state owned by callers and hist entries.

Dependencies and integration points: includes hist, symbol, sort, and UI headers so block reports integrate with perf's existing hists/hpp output path.

Risks: embedding `perf_hpp_fmt` means lifetime of `block_fmt` must outlive hpp list use. `block_info` ownership is split through hist entries, so free paths must know whether `block_info__delete()` is registered/used by hist cleanup.

Test signals: compile and runtime coverage for every enum column, report creation/free cycles, and percentage calculations with zero and nonzero totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-range.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/block-range.c

Purpose: maintains a global red-black tree of non-overlapping basic-block address ranges for annotation. It splits, fills, and marks ranges so branch targets and branch instructions can be represented precisely even when observed blocks overlap.

Important APIs and functions: `block_range__find()` finds the range containing an address. `block_range__create()` creates or splits ranges covering an inclusive start/end block and returns an iterator over the affected ranges. `block_range__coverage()` normalizes a range's coverage by its symbol's maximum coverage. Internal helpers link new nodes to the left/right edge of existing nodes and `block_range__debug()` asserts ordering invariants in debug builds.

Control flow: `block_range__create()` searches for the range containing `start`; if none exists it either inserts a whole new range or a head before the next overlapping range. If an existing range starts before `start`, it splits a head. It then walks forward until `end` is covered, splitting tails, adding tails, or filling holes between adjacent ranges. The resulting first range is marked target and final range is marked branch.

State and persistence: `block_ranges` is a static global tree and block counter. Allocated `block_range` nodes persist for process lifetime unless cleaned elsewhere, and coverage/taken/pred counters are stored in nodes as annotation state.

Dependencies and integration points: uses Linux rbtree and annotation symbols. `block_range__coverage()` reaches into `symbol__annotation(sym)->branch->max_coverage`.

Risks: the global tree is not keyed per symbol or DSO in this file; callers must ensure address spaces do not collide or that lifecycle is reset appropriately. Allocation failure can return a partially useful iterator with missing tail work. The range math is inclusive and sensitive to underflow around zero, though comments note NULL is not executable. No locking is present.

Test signals: unit-style tests for non-overlapping insert, overlapping insert, split at start, split at end, holes, adjacent ranges, single-instruction blocks, allocation failure injection, and coverage with missing symbols/annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-range.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/block-range.h

Purpose: declares the block-range rbtree node, iterator helpers, and public lookup/create/coverage APIs.

Important APIs and types: `struct block_range` contains rb node, symbol pointer, inclusive start/end, target/branch flags, coverage, entry, taken, and prediction counters. `struct block_range_iter` identifies a start and end range over newly created or affected block ranges. Inline helpers advance and validate iterators.

Control flow: inline `block_range__next()` uses `rb_next()`. `block_range_iter__next()` advances until the iterator reaches its end. Creation and lookup are implemented in the `.c` file.

State and persistence: the structure defines mutable per-range annotation state; storage is allocated and held by the global implementation tree.

Dependencies and integration points: includes Linux rbtree/types and forward declares `struct symbol`. Used by annotation paths that map branch observations to source/assembly block coverage.

Risks: callers must respect inclusive range semantics and iterator validity. Because the implementation uses a global tree, API consumers need a clear lifecycle/reset model outside this header.

Test signals: compile coverage in annotation code and iterator traversal tests over ranges created from overlapping branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/block-range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.c

Purpose: synthesizes and processes perf records that describe BPF programs, BPF ksymbols, BTF data, and optional BPF metadata. This lets perf annotate and symbolize BPF JIT code in recorded sessions and sideband streams.

Important APIs and functions: `machine__process_bpf()` handles runtime `PERF_RECORD_BPF_EVENT` records and marks kernel maps as BPF program DSOs. `perf_event__synthesize_bpf_events()` enumerates kernel BPF programs, creates `PERF_RECORD_KSYMBOL` and `PERF_RECORD_BPF_EVENT` records, and synthesizes BPF trampoline/dispatcher images from kallsyms. `evlist__add_bpf_sb_event()` installs a dummy sideband event with `bpf_event` enabled. `__bpf_event__print_bpf_prog_info()` prints stored BPF program details. Metadata helpers read `.rodata` BPF maps with BTF and emit `PERF_RECORD_BPF_METADATA` when supported.

Control flow: synthesis obtains program ids with `bpf_prog_get_next_id()`, opens each program fd, linearizes selected `bpf_prog_info` arrays through `get_bpf_prog_info_linear()`, optionally loads BTF, emits a ksymbol per JITed subprogram, inserts program info into `perf_env`, emits BPF load events, and emits metadata records. Sideband events call `perf_env__add_bpf_info()` when load records arrive. Processing BPF load records later finds stored info and associates matching kernel maps with BPF metadata.

State and persistence: BPF program info and BTF blobs are stored in `perf_env` as `bpf_prog_info_node` and `btf_node`, making them available for later report/annotation. Metadata allocation owns per-subprogram names and event payload until synthesized or freed. Unload events intentionally do not free program info because annotation can still need it later.

Dependencies and integration points: uses libbpf, kernel BPF syscalls, perf env/session/machine/map/DSO APIs, kallsyms, synthetic event delivery, `bpf-utils` linearization, and optional libbpf string formatting support.

Risks: kernel support is feature-dependent; old kernels can lack program info fields, BTF, BPF event sideband, or permissions. Subprogram counts must match across ksyms, lengths, tags, and function info. Metadata path assumes `.rodata` array maps with BTF datasec layout and may silently skip unsupported maps. Error handling often downgrades old-kernel/permission failures to nonfatal behavior, so missing BPF symbolization can be quiet.

Test signals: record/report tests with single and multi-subprogram BPF programs, with and without BTF, with metadata variables, old-kernel field truncation, permission failures, sideband load/unload, BPF trampolines in kallsyms, and annotation lookup after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.h

Purpose: declares BPF event processing and BPF program metadata structures for perf.

Important APIs and types: `struct bpf_metadata` owns a metadata perf event plus synthesized program names. `struct bpf_prog_info_node` stores a linearized `bpf_prog_info`, optional metadata, and an rbtree node for `perf_env`. `struct btf_node` stores raw BTF by id. Public APIs under libbpf support include `machine__process_bpf()`, `evlist__add_bpf_sb_event()`, `__bpf_event__print_bpf_prog_info()`, and `bpf_metadata_free()`. Stub implementations no-op when libbpf support is absent.

Control flow: no implementation flow in the header; conditional compilation selects real APIs or no-op stubs based on `HAVE_LIBBPF_SUPPORT`.

State and persistence: structures are stored in perf environment rbtrees and persist for the session lifetime.

Dependencies and integration points: includes rbtree, fd array API, and forward declares perf session/machine/sample/env types. It bridges BPF event synthesis, sideband event collection, and report-time symbolization.

Risks: users built without libbpf support get silent no-op BPF processing, so feature availability must be surfaced elsewhere. Ownership of `perf_bpil` and metadata is explicit but easy to leak if insertion into env fails.

Test signals: build with and without libbpf, env insertion/free tests, and BPF annotation tests that retrieve `bpf_prog_info_node` and `btf_node` from the environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.c

Purpose: implements perf's generic BPF sample filter support. It converts parsed filter expressions into BPF map entries, attaches a fixed sample-filter BPF program to perf events, supports a root-pinned shared filter setup for non-root users, and reports dropped samples.

Important APIs and functions: `perf_bpf_filter__parse()` checks capability/pinned setup and invokes the flex/bison parser. `perf_bpf_filter__prepare()` builds filter entries, validates sample flags, loads or reuses the BPF skeleton, updates maps, and attaches programs with `bpf_program__attach_perf_event_opts()` or `PERF_EVENT_IOC_SET_BPF`. `perf_bpf_filter__destroy()` frees expressions and removes pinned map entries. `perf_bpf_filter__lost_count()` reads the dropped count. `perf_bpf_filter__pin()` and `perf_bpf_filter__unpin()` manage pinned BPF objects under `/sys/fs/bpf/perf_filter`.

Control flow: parsed expressions live on `evsel->bpf_filters`. `get_filter_entries()` flattens normal expressions and one-level OR groups into `perf_bpf_filter_entry` arrays terminated by `PBF_OP_DONE`. In per-task non-root mode, `create_idx_hash()` reserves a slot in the shared `filters` map, creates event-id aliases in `event_hash`, maps `(tgid,event-id)` to the filter slot in `idx_hash`, resets dropped count, and attaches the pinned program. Root/system-wide mode loads a private skeleton and uses filter index zero.

State and persistence: `pinned_filters` tracks shared map slots to clean up later. Pinned mode persists BPF programs and maps in bpffs with relaxed permissions so non-root users can attach preloaded filters. Per-evsel private mode stores the skeleton pointer on `evsel->bpf_skel`. Filter expressions are heap allocated and freed at destroy.

Dependencies and integration points: depends on libbpf skeleton `sample_filter.skel.h`, perf evsel fd arrays, target/thread maps, capability checks, procfs for Tgid lookup, bpffs/sysfs helpers, and parser headers generated from `bpf-filter.l/.y`.

Risks: shared pinned maps have finite sizes and require cleanup; stale entries can exhaust slots or cause wrong dropped counts. `create_idx_hash()` assumes thread map pids can be converted to TGIDs via `/proc`, but threads can exit during setup. Sample flag validation must match BPF program expectations. Attaching to many event fds can partially succeed before a later failure, so cleanup paths are important. Permission and libbpf-version behavior differs between root, CAP_BPF, and non-root pinned workflows.

Test signals: parse and attach filters for system-wide and per-task targets, non-root pinned workflow, map slot exhaustion, event fd id failures, dead task pids, missing sample flags with hint output, dropped count reporting, pin/unpin permissions, and cleanup after partial attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.h

Purpose: declares BPF sample-filter expression structures and public filter lifecycle APIs.

Important APIs and types: `struct perf_bpf_filter_expr` stores list membership, optional OR-group list, operation, sample term part, term, and comparison value. `PERF_BPF_FILTER_PIN_PATH` names the bpffs pin directory. Real APIs are exposed when `HAVE_BPF_SKEL` is set: expression allocation, parse, prepare, destroy, lost-count, pin, and unpin. Stub APIs return `-EOPNOTSUPP` or zero when BPF skeleton support is absent.

Control flow: the header supports parser construction of expression lists and evsel preparation/cleanup in the implementation. Conditional compilation determines whether callers get working filtering or a clear build-time unsupported path.

State and persistence: expression nodes are in-memory list elements owned by evsels. Pinned path names persistent bpffs objects used across perf invocations.

Dependencies and integration points: includes generated sample-filter BPF definitions, debug output, Linux lists, and forward declarations for evsel/target.

Risks: stubs mean code can compile without BPF support but runtime requests fail. Expression ownership is manual; parser errors and destroy paths must free nested group entries correctly.

Test signals: build with and without BPF skeleton support, expression parse/free tests, and unsupported-mode error message tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.l -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.l

Purpose: flex lexer for perf BPF sample-filter expressions. It tokenizes sample terms, operators, numeric literals, cgroup paths, and symbolic constants used by the parser.

Important APIs and tokens: lexer prefix is `perf_bpf_filter_`. It emits `BFT_SAMPLE`, `BFT_SAMPLE_PATH`, `BFT_OP`, `BFT_NUM`, `BFT_PATH`, `BFT_LOGICAL_OR`, and punctuation tokens. Helpers set `perf_bpf_filter_lval` with sample term/part, operation, numeric value, or path. Recognized sample terms include `ip`, `id`, `tid`, `pid`, `cpu`, `time`, `addr`, `period`, `txn`, `weight*`, page sizes, data-source subfields, `uid`, `gid`, and `cgroup`.

Control flow: numeric patterns parse decimal or hex. Sample keywords reset or set `perf_bpf_filter_needs_path`; only `cgroup` expects a following path token. Operators map to BPF filter ops. Many textual constants map to perf memory data-source bit values, such as load/store, cache levels, snoop states, remote, locked, TLB states, block reasons, and hop counts. Unexpected path-like text is an error unless the parser is waiting for a path.

State and persistence: lexer state is transient, but it mutates the global parser semantic value and the `perf_bpf_filter_needs_path` flag. No persistent storage is allocated here except returning `yytext` for paths during parse.

Dependencies and integration points: includes perf event ABI constants and parser header `bpf-filter-bison.h`. It feeds `bpf-filter.y` and ultimately `perf_bpf_filter__parse()`.

Risks: keyword order matters because `{path}` catches broad text. Constants must remain aligned with kernel/perf memory data-source encodings and BPF program interpretation. Path semantic values point to lexer text, so parser actions must consume them immediately.

Test signals: lexer/parser tests for every sample term, aliases, decimal/hex values, all comparison operators, `||`, comma separation, cgroup path acceptance, and unexpected token errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.y -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.y

Purpose: bison grammar for BPF sample-filter expressions. It builds `perf_bpf_filter_expr` lists consumed by `bpf-filter.c`.

Important APIs and grammar: the parse parameter is `struct list_head *expr_head`. `filter` accepts comma-separated terms. `filter_term` supports `filter_expr || filter_expr` by creating a `PBF_OP_GROUP_BEGIN` expression and adding member expressions to its `groups` list. `filter_expr` accepts numeric comparisons for sample terms and path comparisons for cgroup terms. Cgroup comparisons are limited to `==` and `!=`.

Control flow: each parsed top-level expression is appended to `expr_head`. OR groups are flattened one level by storing a group begin node whose `val` counts members, then later `bpf-filter.c` emits member entries followed by `PBF_OP_GROUP_END`. For cgroup paths, the parser creates a cgroup object, reads its cgroup id, and stores that id as the comparison value.

State and persistence: expression nodes are heap allocated through `perf_bpf_filter_expr__new()` and owned by the evsel filter list after parsing. The parser uses the global `perf_bpf_filter_needs_path` flag coordinated with the lexer.

Dependencies and integration points: includes Linux list helpers, cgroup utilities, and `bpf-filter.h`. It is invoked by `perf_bpf_filter__parse()`.

Risks: nested OR groups are not supported. If cgroup lookup fails, the expression value remains zero, which could match an unintended id unless callers treat zero carefully. Error reporting uses `printf` rather than perf's usual `pr_err`.

Test signals: parser tests for comma lists, OR groups of more than two expressions, numeric comparisons, cgroup equality/inequality, invalid cgroup operators, bad paths, and parser cleanup on syntax errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-trace-summary.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-trace-summary.c

Purpose: provides syscall latency summary support for perf trace using a BPF skeleton. It aggregates syscall counts, errors, total/min/avg/max latency, and relative standard deviation by CPU/global, thread, or cgroup.

Important APIs and functions: `trace_prepare_bpf_summary()` opens, configures, loads, and attaches the syscall summary skeleton. `trace_start_bpf_summary()` and `trace_end_bpf_summary()` toggle collection. `trace_print_bpf_summary()` reads the BPF map, aggregates entries in userspace hashmaps, sorts by total time, and prints formatted tables. `trace_cleanup_bpf_summary()` destroys the skeleton and releases cached cgroups.

Control flow: preparation sets aggregation mode in rodata and detects cgroup v2. During printing, the code iterates `syscall_stats_map` keys, looks up stats, dispatches to `update_thread_stats()`, `update_total_stats()`, or `update_cgroup_stats()`, copies hashmap values into an array, sorts groups by total time, sorts per-group syscall nodes by total time, and prints common columns.

State and persistence: global `skel` owns the loaded BPF object and maps. Global `cgroups` caches cgroup names for cgroup aggregation. Userspace aggregation state is temporary during print and freed before return. No report is persisted beyond the output stream.

Dependencies and integration points: depends on libbpf generated skeleton `syscall_summary.skel.h`, BPF map APIs, syscall table lookup, cgroup helpers, perf hashmaps, Linux time constants, and math for standard deviation.

Risks: `rel_stddev()` divides by average when count is at least two; zero total time could still produce zero average. `print_total_stats()` calls `print_common_stats(data[i], max_summary, fp)` for each single-node total item; the inner `max_summary` is harmless because each node count is one, but the naming can confuse review. Skeleton load/attach failures return `-1` without cleanup of already-opened skeleton in some paths. Cgroup names can disappear after collection.

Test signals: BPF summary tests for CPU/global, thread, and cgroup modes; zero/one/many syscall entries; unknown syscall numbers; error counts; cgroup v1/v2; sorting by total time; max-summary truncation; and cleanup after load/attach failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-trace-summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.c

Purpose: provides helper functions for retrieving `struct bpf_prog_info` plus selected variable-length arrays into one contiguous allocation, and for converting embedded array pointers to file-storable offsets and back.

Important APIs and functions: `get_bpf_prog_info_linear()` is the main API. It uses descriptors for arrays such as JITed instructions, translated instructions, map ids, JITed ksyms, function lengths, function info, line info, JITed line info, and program tags. `bpil_addr_to_offs()` rewrites array pointers as offsets from `info_linear->data`; `bpil_offs_to_addr()` restores them.

Control flow: the function first calls `bpf_obj_get_info_by_fd()` with an empty info struct to discover counts and record sizes. It filters requested arrays not supported by the returned info length, computes a rounded contiguous data size, allocates `struct perf_bpil + data`, points requested arrays into the data area, calls the BPF syscall again to fill data, validates that counts, sizes, and pointers match expectations, records info/data lengths, and returns the allocation.

State and persistence: returned `perf_bpil` is heap allocated and caller-owned. Pointer-to-offset conversion makes the blob suitable for storage in perf environment data or files; offset-to-pointer conversion must be done before dereferencing arrays.

Dependencies and integration points: uses libbpf/BPF syscall APIs, `struct bpf_prog_info`, perf debug logging, and header definitions from `bpf-utils.h`. BPF event synthesis stores these blobs in `perf_env`.

Risks: array sizing can race with program changes between the two info syscalls; validation catches mismatches and returns `-ERANGE`. Requested array bitmasks beyond `PERF_BPIL_LAST_ARRAY` are rejected. Old kernels with shorter `bpf_prog_info` silently drop unsupported arrays. Pointer arithmetic assumes all array pointers are inside the contiguous data block.

Test signals: tests against BPF programs with each supported array present/absent, old-kernel simulated short info lengths, mismatched counts via fault injection, pointer-offset round trips, invalid array bitmasks, and memory leak checks on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.h

Purpose: declares BPF utility helpers and the linearized `bpf_prog_info` storage format used by perf.

Important APIs and types: `ptr_to_u64()` converts pointers for kernel ABI fields. `LIBBPF_CURRENT_VERSION_GEQ()` and `HAVE_LIBBPF_STRINGS_SUPPORT` gate libbpf feature use. `enum perf_bpil_array_types` names retrievable `bpf_prog_info` arrays. `struct perf_bpil` records compiled info length, data length, included array bitmask, a `bpf_prog_info`, and a flexible data area. Public functions fetch linear info and convert addresses to offsets or offsets to addresses.

Control flow: no implementation flow; the declarations support BPF event code that needs to serialize/deserialize BPF program information.

State and persistence: `perf_bpil` is explicitly designed as a contiguous, persistable blob after pointer fields are converted to offsets.

Dependencies and integration points: only active under `HAVE_LIBBPF_SUPPORT`, includes libbpf headers and version macros. Used by `bpf-event.c` and any report path that reads stored BPF program info.

Risks: compile-time libbpf feature checks must match actual APIs. The blob format depends on the tool's compiled `struct bpf_prog_info` size, recorded in `info_len`, so readers must handle version skew.

Test signals: build with multiple libbpf versions, save/load `perf_bpil` blobs across pointer conversion, and verify every enum array type maps to the correct kernel info fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.h -->
