# Research: subset-b-006761

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.c

Purpose: Implements perf's libdw helper layer for source lookup, DIE tree traversal, type resolution, line walking, variable location matching, CFA extraction, prologue skipping, and member/pointer type dereference. It is used by probe and annotation code that needs DWARF information in a form closer to perf's symbols, registers, variables, and source lines.

Important APIs and types: CU helpers include `cu_find_realpath`, `cu_get_comp_dir`, `cu_find_lineinfo`, and `cu_walk_functions_at`. DIE helpers include name matching, linkage lookup, `die_entrypc`, function definition/instance tests, data-member offsets, function/inline search, return-type lookup, line walking, variable/member lookup, type-name formatting, variable range formatting, variable-by-register/address lookup, variable collection, `die_get_cfa`, optimized-target detection, `die_skip_prologue`, `die_get_scopes`, `die_get_member_type`, and `die_deref_ptr_type`. Internal callbacks use the `DIE_FIND_CB_*` protocol from the header.

Control flow: Most routines query elfutils libdw attributes, normalize the result, and return either a borrowed libdw pointer/string or a negative errno. `die_find_child` is the generic recursive walker: callbacks decide whether to stop, descend, move to siblings, or continue both. Function lookup uses `dwarf_getfuncs` for non-inlined subprograms and recursive child searches for inlined subroutines. Line walking first streams the CU line table, then augments it with declaration and inline call-site records that line tables omit. Variable location matching parses simple DWARF expressions and rejects complex operations that would make register/offset matching ambiguous.

State and persistence: The file owns no durable state. It allocates temporary scope arrays from elfutils and linked `die_var_type` nodes for callers to free. It writes to caller-provided `strbuf`s, DIE buffers, offsets, and type buffers. Returned filenames and DIE-derived strings are libdw-owned. Some recursive paths such as `die_is_optimized_target` walk DIE children/siblings without memoization.

Dependencies and integration: Depends heavily on elfutils libdw/libdwfl, DWARF constants, perf `debug`, `dwarf-regs`, `strbuf`, and string helpers. It bridges debug information to perf probe, annotated data-type recovery, source-line display, and variable access decoding. Register matching uses perf's DWARF register abstraction, including `DWARF_REG_FB`.

Risks: DWARF producer differences are explicitly handled but remain risky: missing `DW_AT_comp_dir`, Clang DWARF5 file index quirks, GCC declaration bugs, range-only functions, location-list forms, and optimized-out variables. Location matching intentionally supports only simple op sequences, so valid but complex DWARF expressions can be ignored. `cu_getsrc_die` has delicate binary-search/backtracking logic and relies on sorted line records. Type/member offset logic has limited union handling and only one array level is resolved.

Test signals: Useful tests compile small C/C++ fixtures with gcc and clang, with and without optimization, inline functions, typedef/qualifier chains, anonymous structs/unions, arrays, global variables, frame-base locals, and tail calls. Integration tests should verify probe variable names, source lines, and type recovery on x86 and at least one non-x86 architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.h

Purpose: Declares perf's DWARF auxiliary API exported by `dwarf-aux.c`. It exposes CU, DIE, type, variable, line, scope, CFA, and member/pointer helpers to probe and annotation code.

Important APIs and types: Includes elfutils `Dwarf`, `Dwarf_Die`, and `Dwarf_Addr` types. Defines the `DIE_FIND_CB_*` callback protocol, `line_walk_callback_t`, and `struct die_var_type`, which records type DIE offset, address/range, register, offset, and whether a register stores the variable address. Public functions cover source/line lookup, function and inline search, type resolution, name matching, variable and member lookup, variable collection, prologue skipping, scope discovery, CFA decoding, and pointer/member type resolution.

Control flow and state: The header has no executable flow, but it establishes ownership contracts: callers provide DIE buffers and `strbuf`s, receive borrowed libdw strings, and must free linked lists from variable collection. The callback enum controls recursive traversal behavior used by `die_find_child`.

Dependencies and integration: Pulls in `<dwarf.h>`, elfutils libdw/libdwfl, and elfutils version headers. Forward-declares `struct strbuf` to avoid pulling in perf's string buffer implementation. It is a central contract between DWARF consumers in perf and the libdw implementation.

Risks: ABI/API risk is mostly semantic: many functions return negative errno values or NULL depending on operation, so callers must distinguish absent debug info from unsupported expressions. `struct die_var_type` stores DIE offsets rather than references, requiring consumers to resolve them against the same DWARF object.

Test signals: Header-level test signals come from successful builds with and without libdw users and from compile coverage of callers that exercise all prototypes, especially variable-location and member-type APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm.c

Purpose: Provides ARM-specific conversion from perf register numbers to DWARF register numbers.

Important API: `__get_dwarf_regnum_for_perf_regnum_arm(int perf_regnum)` validates the input against `PERF_REG_ARM_MAX` from the ARM uapi perf register header and returns the same number for valid registers, or `-ENOENT` for invalid inputs.

Control flow and state: Stateless, single bounds check then identity mapping. No allocation or persistence.

Dependencies and integration: Included by the generic DWARF register dispatcher through declarations in `dwarf-regs.h`; used by `get_dwarf_regnum_for_perf_regnum` when `e_machine` is `EM_ARM`.

Risks: Assumes ARM perf register numbering matches DWARF numbering. If kernel uapi adds non-DWARF or reordered registers, this identity mapping must be revisited.

Test signals: Validate negative, `PERF_REG_ARM_MAX`, and common ARM GPR inputs; integration tests should verify perf sample register decoding on ARM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm64.c

Purpose: Provides AArch64-specific conversion from perf register numbers to DWARF register numbers.

Important API: `__get_dwarf_regnum_for_perf_regnum_arm64(int perf_regnum)` checks `0 <= perf_regnum < PERF_REG_ARM64_MAX` and returns the input as the DWARF number when valid.

Control flow and state: Stateless identity mapping with `-ENOENT` for invalid registers.

Dependencies and integration: Depends on `arch/arm64/include/uapi/asm/perf_regs.h` and `dwarf-regs.h`. The generic dispatcher calls it for `EM_AARCH64`.

Risks: Same-number assumption must remain aligned with kernel perf register definitions and libdw AArch64 frame numbering. Register additions beyond libdw support are filtered later by `only_libdw_supported`.

Test signals: Unit coverage for bounds and common x/sp/pc register mappings; end-to-end callchain/register-variable resolution on AArch64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-csky.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-csky.c

Purpose: Implements C-SKY DWARF register name and perf-register mapping for both ABI v1 and ABI v2.

Important APIs: `__get_csky_regstr(n, flags)` returns a `%reg` name from ABI-specific tables. `__get_csky_regnum(name, flags)` performs reverse name lookup. `__get_dwarf_regnum_for_perf_regnum_csky(perf_regnum, flags)` maps perf register enum values to ABI-specific DWARF numbers.

Control flow and state: Stateless table lookups. `EF_CSKY_ABIV2` selects the ABI v2 table/column; otherwise ABI v1 is used. Missing entries are encoded as NULL or `-ENOENT`.

Dependencies and integration: Forces `__CSKYABIV2__` before including C-SKY perf register uapi definitions. Integrated by `dwarf-regs.c` for `EM_CSKY`, which passes ELF flags through to preserve ABI selection.

Risks: Sparse tables and TODO entries mean several perf registers intentionally cannot be translated. The bounds check uses `perf_regnum > ARRAY_SIZE(...)`; an index exactly equal to `ARRAY_SIZE` is risky and should be scrutinized because valid C arrays require `< ARRAY_SIZE`.

Test signals: ABI v1/v2 lookup tests for stack, link, argument, extended, PC/EPC, and unsupported registers; reverse lookup tests for NULL holes; ELF-flag integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-csky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-loongarch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-loongarch.c

Purpose: Provides LoongArch perf-register to DWARF-register conversion.

Important API: `__get_dwarf_regnum_for_perf_regnum_loongarch(int perf_regnum)` bounds-checks against `PERF_REG_LOONGARCH_MAX` and returns an identity mapping for valid values.

Control flow and state: Stateless validation-only wrapper; invalid inputs return `-ENOENT`.

Dependencies and integration: Uses LoongArch uapi perf register definitions and is selected by `dwarf-regs.c` for `EM_LOONGARCH`.

Risks: Assumes LoongArch perf and DWARF numbering match. Future uapi additions or libdw frame register limits need coordinated updates.

Test signals: Bounds tests plus representative GPR/PC register mappings on LoongArch perf data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-loongarch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-mips.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-mips.c

Purpose: Provides MIPS perf-register to DWARF-register conversion with special handling for PC.

Important API: `__get_dwarf_regnum_for_perf_regnum_mips(int perf_regnum)` maps `PERF_REG_MIPS_PC` to DWARF register 37, validates other values against `PERF_REG_MIPS_MAX`, and otherwise uses identity mapping.

Control flow and state: Stateless branch for PC followed by bounds check.

Dependencies and integration: Uses MIPS uapi perf register definitions and is called by the generic dispatcher for `EM_MIPS`.

Risks: The explicit PC mapping must stay aligned with MIPS DWARF conventions. Other registers rely on identity numbering, so uapi reordering or additions are potential integration risks.

Test signals: Tests for PC, negative/out-of-range values, and several GPR/FPR mappings; regression tests on MIPS perf samples with instruction pointer register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-powerpc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-powerpc.c

Purpose: Provides PowerPC DWARF register mapping and a helper to decode register operands from raw PowerPC instructions for annotation.

Important APIs: `get_powerpc_regs(raw_insn, is_source, op_loc)` fills an `annotated_op_loc` with source/target register, optional second register, and memory offset for D/DS-form instructions. `__get_dwarf_regnum_for_perf_regnum_powerpc(perf_regnum)` maps perf register enums to DWARF numbers for GPRs and selected special registers.

Control flow and state: Stateless bitfield extraction macros decode opcode and operand fields. Register mapping uses a sparse static table where unsupported entries remain zero, with a special case preserving valid register zero.

Dependencies and integration: Depends on PowerPC perf uapi, `dwarf-regs.h`, and `annotated_op_loc`. The generic dispatcher selects it for `EM_PPC` and `EM_PPC64`.

Risks: The sparse table uses zero as unsupported sentinel, requiring special handling for register 0; this pattern is easy to break on future valid zero-like entries. X-form offset handling is still TODO. Several perf registers are intentionally unmapped.

Test signals: Instruction decode tests for D, DS, and X forms; mapping tests for R0/R31, MSR, CTR, LINK, XER, unsupported NIP/CCR; annotation tests for PowerPC load/store operands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-riscv.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-riscv.c

Purpose: Provides RISC-V perf-register to DWARF-register conversion.

Important API: `__get_dwarf_regnum_for_perf_regnum_riscv(int perf_regnum)` returns the same number for registers in `[0, PERF_REG_RISCV_MAX)`, otherwise `-ENOENT`.

Control flow and state: Stateless bounds-checked identity mapping.

Dependencies and integration: Depends on RISC-V uapi perf register definitions and the generic `dwarf-regs.h` contract. Used for `EM_RISCV`.

Risks: Assumes kernel perf register numbering matches DWARF numbering. Libdw support filtering in the generic layer should catch registers beyond known frame ranges.

Test signals: Bounds tests and representative integer/floating register translation on RISC-V data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-s390.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-s390.c

Purpose: Converts s390 perf register numbers to DWARF register numbers, including the non-linear floating-point register order.

Important API: `__get_dwarf_regnum_for_perf_regnum_s390(int perf_regnum)` maps GPRs, FPRs, mask, and PC using a sparse table. Perf register zero is specially accepted because zero is otherwise the unsupported sentinel.

Control flow and state: Stateless table lookup with bounds checking and `-ENOENT` for unsupported entries.

Dependencies and integration: Uses s390 uapi perf register definitions and is selected by the generic dispatcher for `EM_S390`.

Risks: Sparse-table sentinel handling can misclassify future valid zero mappings unless special-cased. Floating-point numbering is non-contiguous and easy to regress.

Test signals: Mapping tests for R0/R15, FP0-FP15 reordered numbers, mask, PC, and unsupported/out-of-range registers; callchain/register tests on s390 samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-x86.c

Purpose: Provides x86/i386 register-name to DWARF-number conversion and perf-register to DWARF-register mapping.

Important APIs: `__get_dwarf_regnum_i386` and `__get_dwarf_regnum_x86_64` parse names with a required leading `%` and accept aliases such as full, partial, stack, flags, segment, SIMD, PC, and base registers. `__get_dwarf_regnum_for_perf_regnum_i386` and `_x86_64` translate perf register enum values to architecture-specific DWARF numbers.

Control flow and state: Stateless lookup through alias tables and sparse mapping arrays. Mapping functions special-case valid perf register zero because unsupported entries also default to zero.

Dependencies and integration: Depends on x86 perf register uapi, Linux `ARRAY_SIZE`, and `dwarf-regs.h`. `dwarf-regs.c` dispatches to these functions for `EM_386` and `EM_X86_64`.

Risks: Alias table correctness directly affects probe argument parsing. A visible table typo maps x86-64 `"edx"` to DWARF register 3 in the RBX row, which should be reviewed because `"edx"` already appears in the RDX row. Sparse zero sentinel handling has the usual future-maintenance risk.

Test signals: Reverse lookup tests for `%rax/%eax/%al`, `%rip/%eip/%ip`, `%fs.base`, i386 `%esp/%stack`, invalid names without `%`, and perf enum mappings for GPRs, IP, flags, segments, and XMM registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs.c

Purpose: Central architecture dispatcher for translating DWARF register numbers to perf probe register strings, register strings back to DWARF numbers, and perf sample register enums to DWARF frame numbers.

Important APIs: `get_dwarf_regstr(n, machine, flags)` selects an architecture table or C-SKY ABI helper. `get_dwarf_regnum(name, machine, flags)` normalizes a register token and dispatches to arch reverse lookups. `get_dwarf_regnum_for_perf_regnum(perf_regnum, machine, flags, only_libdw_supported)` converts perf enum registers and optionally filters out registers beyond libdw frame support. `get_libdw_frame_nregs` encodes per-architecture libdw frame limits.

Control flow and state: Stateless switch on ELF machine, defaulting `EM_NONE` to `EM_HOST`. Register-string tables are compiled by defining `DEFINE_DWARF_REGSTR_TABLE` before including architecture table headers. Unsupported machines log an error and return NULL or `-ENOENT`.

Dependencies and integration: Includes many arch DWARF register table headers plus arch-specific helpers from `dwarf-regs-arch`. Used by probe argument parsing, DWARF variable decoding, and sample register interpretation.

Risks: `get_dwarf_regnum` duplicates `name` into `regname` and strips trailing delimiters, but dispatches `name` rather than `regname`; this means delimiter stripping is ineffective for current calls and should be reviewed. Architecture switch coverage and libdw register counts must track new ELF machines and libdw support.

Test signals: Cross-architecture table tests for valid/invalid names, delimiter-stripped tokens, `EM_NONE` host fallback, unsupported machine errors, and `only_libdw_supported` filtering for high-number registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/env.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/env.c

Purpose: Implements lifecycle, lazy discovery, cleanup, and query helpers for `struct perf_env`, which stores host/session environment metadata used by perf record/report/stat.

Important APIs: Initialization and teardown use `perf_env__init` and `perf_env__exit`. Discovery helpers read CPU topology, PMU mappings, CPUID, core PMU capabilities, architecture, CPU count, NUMA maps, branch counter info, and x86 vendor identity. With libbpf, BPF program info and BTF records are stored in locked rbtrees through insert/find/iterate helpers.

Control flow: Most public getters lazily populate missing fields for local operation, then return cached values. PMU capability collection handles single-core-PMU and hybrid multi-PMU systems differently. `perf_env__numa_node` builds a fast CPU-to-node array from recorded node maps. BPF insert/find paths use read/write semaphores around rbtrees and reject duplicate IDs.

State and persistence: Owns many heap fields in `perf_env`; `perf_env__exit` frees strings, arrays, cache levels, NUMA maps, memory node sets, hybrid nodes, PMU caps, cgroups, BPF trees, and CPU domain maps. Static caches in x86 vendor helpers memoize AMD/Intel answers process-wide.

Dependencies and integration: Depends on cpumap, PMU/PMUs, cgroup cleanup, rwsem, strbuf, utsname, BPF/libbpf optional code, trace beauty errno lookup, and sysfs/proc helpers behind CPU/PMU calls. It integrates with perf headers, session metadata, event reporting, stat, and architecture-specific formatting.

Risks: Lazy getters assume `env` is initialized and can allocate during read paths. `perf_env__find_br_cntr_info` chooses either legacy `cpu_pmu_caps` or first hybrid `pmu_caps`; callers need valid cap data. Static x86 vendor caches ignore different env objects after first call. BPF returned nodes remain owned by the env tree, so lifetime must outlive consumers.

Test signals: Tests should cover init/exit under valgrind/asan, duplicate BPF/BTF insertion, PMU capability parsing for single and hybrid PMUs, NUMA lookup with missing CPUs, arch normalization strings, x86 vendor caching, and behavior without libbpf/libtraceevent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/env.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/env.h

Purpose: Defines `struct perf_env` and related topology, NUMA, memory, hybrid PMU, PMU capability, sched-domain, compression, and BPF metadata contracts.

Important APIs and types: Key structs include `cpu_topology_map`, `cpu_cache_level`, `numa_node`, `memory_node`, `hybrid_node`, `pmu_caps`, `domain_info`, `cpu_domain_map`, and `perf_env`. Function prototypes expose env lifecycle, CPUID/PMU/topology readers, arch formatting, BPF metadata accessors, NUMA lookup, PMU cap lookup, branch counter info, and x86 vendor helpers. `perf_env` also embeds clock conversion metadata and optional BPF rbtrees protected by rwsems.

Control flow and state: The header defines the persistent in-memory shape that is serialized in perf data headers and consumed by report/stat paths. Counters describe how many elements are valid in associated dynamic arrays.

Dependencies and integration: Includes Linux types/rbtree, cpumap, and rwsem. It is shared across perf record, report, stat, BPF event, cgroup, topology, and header code.

Risks: Many fields are raw pointers with paired count fields, so allocation/free and serialization must stay synchronized. Optional libbpf fields alter layout under build configuration. Callers must not assume fields are populated unless they invoked the corresponding reader or loaded them from a perf data file.

Test signals: Build matrix with/without libbpf, header serialization round trips for env fields, and teardown tests for every dynamically allocated substructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/event.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/event.c

Purpose: Implements perf event record names, event printing, machine-processing adapters, kallsyms symbol lookup helpers, stat config import, address-to-map/symbol resolution, and sample address correlation predicates.

Important APIs: `perf_event__name`, many `perf_event__fprintf_*` functions, `perf_event__fprintf`, `perf_event__process_*` adapters, `kallsyms__get_function_start`, `kallsyms__get_symbol_start`, `machine__resolve`, `thread__find_map`, `thread__find_map_fb`, `thread__find_symbol`, `thread__resolve`, `is_bts_event`, and `sample_addr_correlates_sym`.

Control flow: Processing functions mostly delegate typed records to `machine__process_*`. Printers switch on record type and format typed payloads, including mmap build IDs, namespaces, cgroups, aux flags, text poke bytes, BPF metadata, and schedstat version-specific fields. `machine__resolve` finds or creates the relevant thread, locates maps based on host/guest cpumode, applies thread/dso/symbol/parallelism filters, computes latency, and resolves symbols.

State and persistence: No persistent state is owned here. It mutates machine/thread/map state via delegated processing and fills caller-owned `addr_location` structures. Kallsyms helpers stream symbol files and return a found address.

Dependencies and integration: Bridges raw perf records to `machine`, `thread`, `map`, `dso`, `symbol`, BPF, namespace, hist, stat, and session code. Uses global symbol configuration such as host/guest filters, dso/symbol lists, lazy kernel map loading, and parallelism filters.

Risks: Record printers assume event payload layout matches header type and size. Address resolution can filter incorrectly if cpumode is missing or branch/sample address mode differs; fallback logic mitigates this. Text poke symbol lookup may load kernel maps. Schedstat printing depends on version-specific include files.

Test signals: Synthetic perf event fixtures for every printed record type, kallsyms parsing tests for function and alias symbols, host/guest cpumode resolution tests, dso/symbol filter tests, branch/page-fault address-correlation tests, and schedstat v15/v16/v17 print tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/event.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/event.h

Purpose: Declares perf record utility APIs, sample constants, synthesized event formats, branch flag masks, stat round constants, guest helpers, and formatting/processing prototypes.

Important APIs and types: Defines `PERF_SAMPLE_MASK`, `PERF_SAMPLE_MAX_SIZE`, `struct ip_callchain`, branch flag bits and masks, `PERF_TYPE_SYNTH`, `enum perf_synth_id`, Intel PT synthesized raw payload structs, PowerPC VPA DTL struct, raw-data helpers, event processing/printing prototypes, kallsyms lookup prototypes, paranoid/sysctl helpers, page-size naming, and guest cpumode inline helpers.

Control flow and state: Header-only inline logic includes raw-data offset helpers and guest cpumode checks. The synthesized raw structs intentionally include 4 bytes of padding so raw data lines up with `PERF_SAMPLE_RAW` expectations.

Dependencies and integration: Includes kernel/perf event ABI headers, libperf event definitions, Linux types, and forward declarations for perf core structs. Used by event processing, auxtrace, Intel PT, PowerPC DTL, stat, report, and record code.

Risks: Struct packing and padding are ABI-sensitive; changing synthesized event layouts can break decoding. Format macros differ by LP64 to satisfy printf type checking. Branch flag character order must remain aligned with bit definitions.

Test signals: Compile-time size/layout checks for synth structs, raw-size helper tests, sample-size guard tests, guest cpumode helper tests, and decoder tests for Intel PT/PowerPC synthesized records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/events_stats.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/events_stats.h

Purpose: Defines aggregate counters for perf event stream health and histogram sample accounting.

Important types/APIs: `struct events_stats` tracks lost events, lost samples, BPF-dropped samples, aux lost/partial/collision counts, invalid callchains, counts per perf record type, unknown/unprocessable samples, auxtrace errors, and proc-map timeouts. `struct hists_stats` tracks total/non-filtered periods, latency, sample counts, lost samples, and dropped samples. Declares `events_stats__inc` and `events_stats__fprintf`.

Control flow and state: Header is declarative. State is accumulated by event processing and reporting code; arrays are indexed by perf record and auxtrace error enums.

Dependencies and integration: Includes libperf event ABI, Linux types, stdio, and auxtrace definitions. Embedded in `struct evlist` for stream-wide accounting.

Risks: Array sizes must remain compatible with `PERF_RECORD_HEADER_MAX` and `PERF_AUXTRACE_ERROR_MAX`. Counters distinguish kernel-lost samples from BPF-dropped samples via record misc flags, so processing code must update the correct field.

Test signals: Counter increment/printing tests, lost/lost-samples/BPF-dropped sample classification, auxtrace error indexing, and report summary regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/events_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/evlist.c

Purpose: Implements perf's high-level event-list orchestration: evsel list lifecycle, default/dummy event creation, tracepoint handlers and filters, CPU iteration with affinity, enable/disable, polling, sample ID lookup, mmap setup/teardown, target map creation, workload fork/exec control, sample parsing, control-fd commands, timed enable windows, tracking events, weak group reset, branch counter indexing, and name uniquification.

Important APIs: Lifecycle functions include `evlist__new`, `evlist__init`, `evlist__delete`, `evlist__add`, `evlist__remove`, `evlist__open`, `evlist__close`, `evlist__mmap_ex`, and `evlist__munmap`. Runtime controls include `evlist__enable/disable`, non-dummy and per-event variants, `evlist__poll`, `evlist__parse_sample`, `evlist__prepare_workload`, `evlist__start_workload`, control-fd initialization/processing, and event-enable timer functions. Helper APIs handle maps, filters, tracking events, branch counters, sample type validation, and user CPU warnings.

Control flow: Construction wraps libperf `perf_evlist` and attaches perf-specific state. Opening ensures maps exist, updates sample ID positions, and opens each evsel. CPU iteration may temporarily pin affinity when multiple PMU syscalls on shared CPUs benefit. Mmap setup delegates to libperf callbacks that allocate `struct mmap` arrays and configure auxtrace maps. Workload preparation forks a child, waits on pipes, and releases exec only when recording is ready. Control-fd processing reads one command, toggles/list events, and acknowledges supported commands.

State and persistence: Owns selected evsels, mmap arrays, event stats, workload pid/cork fd, control fd positions, backward mmap state, event-enable timer, metric events, and deferred samples. Cleanup closes fds, unmaps buffers, frees ids/fds/stats, exits timers and metric lists, and deletes evsels. Backward overwrite mmap uses a small state machine to pause/resume output around snapshot consumption.

Dependencies and integration: Integrates libperf evlist/evsel/mmap, perf PMU parsing, BPF filters, auxtrace, record options, thread/cpu maps, target handling, sideband events, metric groups, timerfd, poll, fork/exec, and sysctls. It is central to `perf record`, `stat`, `top`, and report-side event list handling.

Risks: Lifecycle ordering is critical: fds, mmap refs, id hashes, and evsel ownership must be released in the right order. Control FIFO parsing opens FIFOs read/write nonblocking to avoid repeated HUPs. Event-enable time parsing requires sorted non-overlapping ranges. `event_enable_timer__exit` frees the struct without closing `timerfd`, so ownership expectations around pollfd/fd cleanup deserve review. Backward mmap transitions silently ignore invalid transitions after `goto state_err`.

Test signals: Unit tests for mmap page parsing/rounding, sample ID lookup, sample type/read format validation, enable/disable per event, control fd commands, timer range parsing and transitions, workload cancellation/start, weak group reset, tracking dummy event selection, and BPF output/sideband decisions. Integration tests should record with multiple PMUs, hybrid CPUs, auxtrace overwrite snapshots, control FIFOs, and delayed enable windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evlist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/evlist.h

Purpose: Defines perf's `struct evlist`, backward mmap state machine, CPU iterator, control command protocol, and the public event-list API implemented across `evlist.c` and related files.

Important APIs and types: `struct evlist` embeds `struct perf_evlist` plus enabled state, ID positions, branch counter count, mmap state, workload, mmap arrays, selected evsel, stats, session, sideband thread, control fds, timer pointer, metric events, and deferred samples. The header declares lifecycle, event creation, tracepoint filter, poll, ID lookup, mmap, enable/disable, maps, sample parsing, validation, tracking, control-fd, timer, formatting, warning, uniquification, and BPF sideband APIs. Macros implement evsel list iteration and `evlist__for_each_cpu`.

Control flow and state: The backward mmap enum documents valid transitions from not-ready to running, data-pending, empty, and back to running. The CPU iterator tracks evlist CPU index, evsel CPU index, current CPU, and optional saved affinity. Control command strings define the external text protocol.

Dependencies and integration: Includes libperf internal evlist/evsel, fdarray, affinity, events stats, evsel, rblist, pthread/signal/unistd, and perf record/stat forward declarations. Shared by record, stat, top, report, sideband, and auxtrace code.

Risks: Because `struct evlist` embeds many subsystems, ownership is distributed; users must pair init/open/mmap/timer/control setup with close/munmap/exit/delete. Iteration macros expose list internals, so removing evsels during iteration requires safe variants. Control command max length is fixed at 64 bytes.

Test signals: Compile coverage for iterator macros, state-machine transitions, control command parsing, lifecycle pairing, and users that embed or stack-allocate `struct evlist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evlist.h -->
