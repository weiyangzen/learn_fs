# subset-b-006755 research

Grouped research for perf annotation architecture helpers, data-type annotation, and Arm SPE packet decoding. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-csky.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-csky.c

## Purpose
Provides the C-SKY architecture adapter for perf annotate disassembly. It creates an `arch` descriptor named `csky`, sets objdump parsing conventions, and maps C-SKY branch, call, and return mnemonics to generic annotation instruction operations.

## Important APIs, Types, and Functions
`arch__new_csky()` allocates and initializes the architecture descriptor using `zalloc()`, copies the ELF machine/e_flags id, sets `objdump.comment_char` to `/`, and installs `csky__associate_ins_ops()`.
`csky__associate_ins_ops()` classifies mnemonics into `jump_ops`, `call_ops`, or `ret_ops`, then caches the association through `arch__associate_ins_ops()`.

## Control Flow
Perf annotation asks the architecture to associate an instruction name when a disassembly line is parsed. The function compares the mnemonic against fixed C-SKY branch forms (`bt`, `bf`, `bez`, `br`, `jmpi`, `jmp`, and related conditional forms), call forms (`bsr`, `jsri`, `jsr`), and return form (`rts`). Matching names are registered and reused by the common disassembly renderer.

## State and Persistence
State is limited to the allocated `struct arch` and the common instruction-operation cache populated by `arch__associate_ins_ops()`. There is no persistent file or cross-run state.

## Dependencies and Integration Points
Depends on `../disasm.h` for `struct arch`, `struct ins_ops`, and generic operation instances. Integrated by the perf architecture registry through `arch__new_csky()`, then consumed by generic annotate code for jump arrows, call markers, and return markers.

## Risks
The classifier uses exact string comparisons, so new assembler aliases or suffix forms are ignored until added. A missed branch/call primarily affects annotation presentation and jump-target accounting rather than sample accounting. The comment character is architecture-specific and must match objdump output.

## Test Signals
Useful tests include annotating C-SKY binaries containing each listed branch/call/return form, checking rendered call/return/jump arrows, and confirming comments beginning with `/` are parsed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-csky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-loongarch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-loongarch.c

## Purpose
Implements LoongArch-specific instruction classification and operand parsing for perf annotate. It improves generic jump and call rendering by resolving target addresses, symbol names, local offsets, and outside-function status from LoongArch objdump syntax.

## Important APIs, Types, and Functions
`arch__new_loongarch()` creates the `loongarch` descriptor and installs `loongarch__associate_ins_ops()`.
`loongarch_call__parse()` parses call operands containing `#addr <name>`, stores target address/name, maps objdump address to runtime memory address, and resolves a target symbol through thread maps.
`loongarch_jump__parse()` parses branch targets either after `#` or directly from the operand, records raw comment/function markers, computes whether the target is outside the current symbol, fills local offset availability, and resolves a symbol when possible.
`loongarch_call_ops` and `loongarch_jump_ops` bind those parsers to generic `call__scnprintf()` and `jump__scnprintf()`.

## Control Flow
During disassembly, `bl` is associated with LoongArch call parsing, `jirl` is treated as a return, and unconditional/conditional branch families (`b`, `beq*`, `bne*`, `blt*`, `bge*`, `bltu*`, `bgeu*`) use LoongArch jump parsing. Target resolution follows map conversion (`map__objdump_2mem()`), map lookup (`maps__find_ams()`), and verification by converting back to objdump address.

## State and Persistence
The code mutates `ins_operands` for each disassembly line by filling `ops->target`, `ops->jump`, and allocated target names. It temporarily gets map references and releases them with `addr_map_symbol__exit()`. No persistent state is stored beyond the per-line annotation structures and architecture operation cache.

## Dependencies and Integration Points
Depends on perf map/thread/symbol infrastructure (`map.h`, `maps.h`, `symbol.h`, `thread.h`) and common disassembly helpers. Feeds `annotate.c` jump validation, arrow rendering, and local target indexing by setting `target.offset`, `target.offset_avail`, and `target.outside`.

## Risks
Parsing assumes GNU objdump-style comments and symbol delimiters. `name = strchr(endptr, '<'); name++;` relies on the call operand containing `<`; malformed input before this point can risk invalid pointer use. Incorrect map conversion or symbol verification would show wrong target symbols or suppress local jump arrows.

## Test Signals
Annotate LoongArch samples with internal branches, external branches, calls with symbol names, and `jirl` returns. Include branch operands with comments and function annotations to verify `#` parsing and skip-function-character behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-loongarch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-mips.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-mips.c

## Purpose
Provides MIPS instruction classification for perf annotate. It maps branch-and-link forms to calls, `jr*` forms to returns, and remaining jump/branch mnemonics to generic jumps.

## Important APIs, Types, and Functions
`arch__new_mips()` allocates the `mips` architecture descriptor, sets `objdump.comment_char` to `#`, and installs `mips__associate_ins_ops()`.
`mips__associate_ins_ops()` classifies mnemonics with prefix checks for call-like branch-and-link instructions (`bal`, `bgezal`, `bltzal`, `jal`, `jialc`, and related likely forms), return-like `jr`, and generic `j*`/`b*` jumps.

## Control Flow
The common disassembly parser asks the architecture to classify a mnemonic. MIPS-specific prefix tests run in call-before-jump order so branch-and-link instructions are not downgraded to plain jumps. Matched operations are cached via `arch__associate_ins_ops()`.

## State and Persistence
State is limited to the allocated `struct arch` and instruction-operation associations. The file does not allocate per-instruction operand data or retain external resources.

## Dependencies and Integration Points
Depends on `../disasm.h` for `arch`, `ins_ops`, and generic operation instances. Its output affects annotate jump/call/return markers and any control-flow features that depend on `ins__is_call()`, `ins__is_jump()`, or `ins__is_ret()`.

## Risks
Prefix matching can over-classify synthetic or future mnemonics that share prefixes. Conversely, unlisted aliases can be missed. `jr` is treated as return even though some register jumps may represent indirect branches rather than function returns.

## Test Signals
Use MIPS disassembly with branch-and-link, plain branch, jump, and register-return forms; verify calls and returns render differently and that branch arrows still point to local targets through generic parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-powerpc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-powerpc.c

## Purpose
Implements PowerPC-specific annotate support. It classifies branch/call/return mnemonics, detects load/store and arithmetic instructions from raw instruction bits, configures operand metadata for type tracking, and provides a libdw-enabled register type-state updater for register moves.

## Important APIs, Types, and Functions
`arch__new_powerpc()` creates the architecture descriptor, sets `show_asm_raw = true`, installs `powerpc__associate_instruction_ops()`, and, with libdw, installs `update_insn_state_powerpc()`.
`powerpc__associate_instruction_ops()` maps `b*` mnemonics to jump/call/return operations, excluding non-branch prefixes such as `bcd`, `brinc`, and `bper`.
`check_ppc_insn()` inspects `dl->raw.raw_insn` to choose `load_store_ops` or `arithmetic_ops` for instructions that need operand location metadata.
`load_store__parse()` marks the source operand as a memory reference and sets `multi_regs` for X-form opcode 31 instructions.
`arithmetic__parse()` marks arithmetic source operands with multiple registers except for specific one-source extended forms.
`update_insn_state_powerpc()` propagates DWARF type-state across register moves, including special handling for `mr` encoded as OR X-form.

## Control Flow
Text mnemonics first classify branch-like instructions. Raw instruction classification then uses primary opcode and opcode-extension tables: opcodes 32 to 63 are memory instructions, opcode 31 is searched in sorted tables for memory or arithmetic X-form instructions, and selected two-operand arithmetic opcodes are recognized separately. With libdw type profiling, `annotate-data.c` calls the architecture updater as it walks basic blocks, allowing PowerPC register copies to keep data type attribution alive.

## State and Persistence
Static opcode tables provide read-only classification state. Per-line parsing writes `mem_ref` and `multi_regs` fields into `ins_operands`. Type-state updates mutate the transient `struct type_state` used during data-type lookup. `annotate_opts.show_asm_raw` is globally enabled for PowerPC because raw bits are required by the parser.

## Dependencies and Integration Points
Depends on `annotate-data.h`, `debug.h`, and `disasm.h`; `check_ppc_insn()` is consumed by common disassembly logic when raw PowerPC instructions need operation selection. `annotate_get_insn_location()` later uses `get_powerpc_regs()` with these metadata flags to fill operand locations.

## Risks
The opcode-extension tables must remain sorted for `bsearch()`. A missing or unsorted entry silently loses load/store or arithmetic type tracking. The `arithmetic__parse()` check compares the primary opcode variable against extension constants, which is fragile and depends on intended instruction encodings. Branch classification based on suffixes may misclassify uncommon branch aliases.

## Test Signals
Run annotate and data-type annotation on PowerPC binaries with X-form loads/stores, arithmetic register moves, `mr`, branch-and-link calls, `blr` returns, and conditional branches. Build with and without `HAVE_LIBDW_SUPPORT` to verify both classification-only and type-state paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-riscv64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-riscv64.c

## Purpose
Provides RISC-V 64-bit instruction classification for perf annotate. It maps common call, return, and branch/jump mnemonics to generic annotation operations.

## Important APIs, Types, and Functions
`arch__new_riscv64()` allocates the architecture descriptor, names it `riscv`, sets `objdump.comment_char` to `#`, and installs `riscv64__associate_ins_ops()`.
`riscv64__associate_ins_ops()` maps `jal`, `jr`, and `call` prefixes to `call_ops`, `ret` to `ret_ops`, and any `j*` or `b*` mnemonic to `jump_ops`.

## Control Flow
The function performs prefix checks in call/return/jump order, then caches matched operations via `arch__associate_ins_ops()`. The generic jump/call operand parsers are used; this file does not parse RISC-V operands itself.

## State and Persistence
Only the `struct arch` allocation and operation cache are persisted for the process lifetime. No per-line allocations are made here.

## Dependencies and Integration Points
Uses `../disasm.h` and the generic operation instances. Integrates with common annotate rendering and jump-target bookkeeping by assigning `ins_ops`.

## Risks
Classifying `jr` as a call is conservative for link-register idioms but can misrepresent plain indirect jumps. Prefix matching can catch aliases unintentionally and miss compressed or assembler-specific mnemonics not represented by these prefixes.

## Test Signals
Annotate RISC-V functions containing `jal`, `call`, `ret`, conditional branches, and indirect jumps; verify marker selection and local branch arrows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-riscv64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-s390.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-s390.c

## Purpose
Implements s390 architecture annotate support. It classifies jumps/calls/returns, parses s390 call targets, handles PC-relative load/store-like operands as move operations, and parses s390 CPU id strings for architecture metadata.

## Important APIs, Types, and Functions
`arch__new_s390()` allocates the `s390` descriptor, optionally parses `cpuid`, installs `s390__associate_ins_ops()`, and sets objdump comments to `#`.
`s390_call__parse()` parses call operands of the form `...,addr <name>`, records target address/name, and resolves the target symbol through thread maps.
`s390_mov__parse()` splits source and target around a comma, captures raw operands, parses target address and symbol name, and uses `mov__scnprintf()`.
`s390__associate_ins_ops()` classifies generic jump mnemonics containing `j`, `bct*`, or `br*`, overrides `bras`, `brasl`, and `basr` as calls, `br` as return, and relative load/store mnemonics as move operations.
`s390__cpuid_parse()` extracts the family from IBM-formatted cpuid strings.

## Control Flow
Mnemonic association starts broad for jumps, then applies overrides for calls, returns, and relative load/store instructions. Call parsing maps objdump addresses to memory addresses and validates symbol resolution round-trips. Move parsing prepares source/target fields so common move rendering can show address and symbol information.

## State and Persistence
The architecture descriptor records family/model metadata. Per-instruction parsing allocates strings for operand fields and symbol names; failure paths free partially allocated operands. No disk state is involved.

## Dependencies and Integration Points
Depends on common map, maps, thread, symbol, annotate, and annotate-data infrastructure. Integrated with common call/jump/move rendering and with architecture discovery via cpuid.

## Risks
The broad `strchr(name, 'j')` jump classification can catch non-control-flow mnemonics containing `j`. `s390_mov__parse()` requires symbol-delimited target text and will fail for address-only operands. `arch__new_s390()` returns `NULL` on bad cpuid after allocating `arch`, which risks a small leak on initialization failure.

## Test Signals
Use s390 disassembly with `brasl`, `basr`, `br`, `bct*`, `j*`, and `lgrl`/`strl` forms. Include valid and invalid cpuid strings and verify symbol target resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-sparc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-sparc.c

## Purpose
Provides SPARC instruction classification for perf annotate. It recognizes SPARC call, jump, return, move, integer branch, register branch, and floating-point branch mnemonics.

## Important APIs, Types, and Functions
`arch__new_sparc()` allocates the descriptor, names it `sparc`, sets `objdump.comment_char` to `#`, and installs `sparc__associate_instruction_ops()`.
`is_branch_cond()`, `is_branch_reg_cond()`, and `is_branch_float_cond()` validate condition-code suffixes for integer, register, and floating-point branch families.
`sparc__associate_instruction_ops()` maps `call`, `jmp`, and `jmpl` to calls, `ret`, `retl`, and `return` to returns, `mov` to moves, and validated branch forms to jumps.

## Control Flow
Classification handles exact call/return/move names first. For other names, it strips optional `cw`/`cx` prefixes before testing `b*` and `fb*` branch families. Valid condition suffixes are required before associating `jump_ops`, reducing accidental matches.

## State and Persistence
Only the process-local architecture descriptor and instruction-operation cache are modified. No per-instruction state is allocated in this file.

## Dependencies and Integration Points
Uses `../../util/disasm.h` and generic operation instances. The resulting `ins_ops` drive common annotate arrows, jump-source counts, and call/return markers.

## Risks
Condition recognition is hand-coded and must track assembler naming. Treating `jmp`/`jmpl` as calls can be display-oriented but may not always model indirect branch semantics. Prefix stripping changes the name pointer before caching, so cached aliases may use the stripped name rather than original spelling.

## Test Signals
Annotate SPARC functions containing integer conditional branches, register branches (`brz`, `brlz` forms), floating branches (`fb*`), `call`, `jmpl`, `retl`, and `mov`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-sparc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-x86.c

## Purpose
Implements x86 perf annotate support. It supplies a sorted mnemonic table, CPU-family dependent macro-fusion detection, cpuid parsing, x86 objdump syntax configuration, and libdw-backed type-state tracking for register, stack, global, per-CPU, and call-return data types.

## Important APIs, Types, and Functions
`arch__new_x86()` allocates and configures the `x86` descriptor, validates sorted instructions in debug builds, sets objdump chars (`%`, `(`, `$`, `#`), sets AT&T suffix stripping (`bwlq`), and installs `update_insn_state_x86()` with libdw.
`x86__instructions[]` maps many x86 mnemonics to generic `mov_ops`, `jump_ops`, `call_ops`, `ret_ops`, `lock_ops`, `nop_ops`, and `dec_ops`.
`x86__cpuid_parse()` extracts family/model/stepping and selects AMD or Intel fusion logic.
`amd__ins_is_fused()` and `intel__ins_is_fused()` decide when memory access attribution can fall back from a branch to the previous fused instruction.
`update_insn_state_x86()` updates `struct type_state` across calls, adds/subs, `lea`, moves, stack stores, PC-relative/global accesses, per-CPU accesses, stack canary accesses, and pointer-invalidating arithmetic.

## Control Flow
Architecture initialization parses cpuid and configures disassembly conventions. During disassembly, the common parser searches `x86__instructions` and handles suffixes. During data-type annotation, `annotate-data.c` walks basic blocks and calls `update_insn_state_x86()` for each instruction before checking the sampled memory operand. Calls invalidate caller-saved registers except preserved DWARF-lifetime registers and may seed the return register from DWARF function return type. Move and address-generation instructions propagate or derive type information through registers and stack slots.

## State and Persistence
Per-architecture state includes family/model and fusion callback. Per-analysis state is transient `type_state` in `annotate-data.c`. Register entries track kind, type DIE, offset, immediate value, lifetime, and copied-from relation. Stack variables are maintained in a linked list by offset. No persistent disk state is written.

## Dependencies and Integration Points
Depends on DWARF helpers, DSO/map/symbol facilities, `annotate-data.h`, and common disassembly operations. It is central to `hist_entry__get_data_type()` because x86 supports instruction tracking and PC-relative/per-CPU special cases. It also affects common annotate rendering through the instruction table and fusion detection.

## Risks
This is a high-complexity heuristic path. Operand parsing assumes AT&T objdump syntax. Per-CPU and stack-canary rules are kernel/x86-specific. Register invalidation and pointer arithmetic can produce false negatives or stale types if a mnemonic is missing from the invalidation list. Fusion logic depends on family/model thresholds and substring matching.

## Test Signals
Tests should cover annotate output for sorted table lookup, suffixed mnemonics, jumps/calls/returns, Intel and AMD cpuid fusion cases, `%gs` per-CPU accesses, stack canaries, `lea`, immediate moves, register copies, calls with return types, stack stores/loads, and pointer arithmetic invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.c

## Purpose
Converts sampled memory-access instructions into annotated data types using DWARF debug information. It resolves global, stack, register, pointer, per-CPU, and inferred instruction-tracked types, builds per-DSO type/member trees, records type histograms, and prints type-centric annotation reports.

## Important APIs, Types, and Functions
`find_data_type()` is the public lookup entry: it initializes default type offset, finds a DWARF type DIE via `find_data_type_die()`, then interns it in the DSO data-type tree with `dso__findnew_data_type()`.
`find_data_type_die()` maps sampled IP to DWARF PC, finds the CU, handles PC-relative globals, discovers frame base/CFA, searches lexical scopes for variable-by-address or variable-by-register matches, and falls back to instruction tracking.
`find_data_type_block()` and `find_data_type_insn()` build shortest-path basic blocks and update a `type_state` through instructions until the sampled instruction is reached.
`update_var_state()` seeds register and stack state from DWARF variable locations.
`check_matching_type()` checks the sampled operand against current register/stack/per-CPU/global state and returns detailed match status.
`get_global_var_type()`, `get_global_var_info()`, and `global_var__collect()` maintain a DSO RB-tree cache of global variable ranges.
`dso__findnew_data_type()`, `add_member_types()`, and `annotated_data_type__get_member_name()` intern type names/sizes and recursively record struct/union members.
`annotated_data_type__update_samples()` allocates and updates byte-level histograms per evsel.
`hist_entry__annotate_data_tty()` prints type annotation output.

## Control Flow
The high-level flow starts in `hist_entry__get_data_type()` in `annotate.c`, which extracts operand location and calls `find_data_type()`. This file converts runtime IP to objdump/DWARF PC, locates the CU, searches direct DWARF variables, tries alternate registers for multi-register operands, and, on x86/PowerPC, walks basic blocks to reconstruct type movement through registers and stack slots. Successful matches are interned by type name and size, optionally expanded with members, then sample counts are added to histograms for the accessed byte offset.

## State and Persistence
State is process-local. DSO RB-trees store interned `annotated_data_type` nodes and `global_var_entry` ranges. Type histograms are allocated lazily per event and per type size. `struct type_state` is transient per lookup and contains register and stack-variable state. Global counters in `ann_data_stat` and `ann_insn_stat` record debug statistics. No files are persisted.

## Dependencies and Integration Points
Requires libdw support for real functionality; the header provides stubs otherwise. Depends on perf debuginfo, DWARF register mapping, symbol/map/thread lookup, evsel/evlist data, and common annotate basic-block discovery. Architecture integration is through `arch->update_insn_state` and operand metadata produced by `annotate_get_insn_location()`.

## Risks
Accuracy depends on DWARF completeness, objdump/disassembly alignment, frame-base correctness, and architecture-specific instruction tracking. Global variable collection scans all CUs and can be expensive. Type histograms allocate one entry per byte of type size per event, which can be costly for huge types. The debuginfo cache used by `hist_entry__get_data_type()` is asserted single-threaded, so concurrent use would be unsafe.

## Test Signals
Exercise binaries with full and partial DWARF, globals, locals, inlined scopes, frame-base CFA, struct/union members, pointer dereferences, stack stores/loads, per-CPU variables, and x86/PowerPC instruction-tracked register moves. Validate `ann_data_stat` counters for failure modes and compare printed type histograms against expected member offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.h

## Purpose
Declares the data-type annotation model and public APIs used by perf annotate. It defines type-state kinds, annotated member/type structures, histograms, data-location inputs, debug statistics, and libdw-dependent lookup/update functions.

## Important APIs, Types, and Functions
`enum type_state_kind` identifies invalid, regular type, per-CPU base, constant, per-CPU pointer, pointer, and stack-canary states.
`struct annotated_member` models nested data members with names, offsets, sizes, and children.
`struct annotated_data_type` stores a DSO RB-tree node, root member metadata, histogram count, and per-event histograms.
`struct data_loc_info` is the lookup input/result carrier for architecture, thread, map-symbol, IP, global address, CPU mode, operand location, debuginfo, frame base, and final type offset.
`struct type_state_reg`, `struct type_state_stack`, and `struct type_state` define the instruction-tracking state table when libdw is enabled.
Public functions include `find_data_type()`, `annotated_data_type__update_samples()`, tree deletion helpers, TTY/TUI printers, member-name lookup, stack-state helpers, global-variable helpers, and debug type-name printing.

## Control Flow
Callers fill `data_loc_info` from an annotated instruction operand and call `find_data_type()`. Architecture update functions mutate `type_state` while `annotate-data.c` walks basic blocks. Successful types can be sampled with `annotated_data_type__update_samples()` and displayed through TTY/TUI functions.

## State and Persistence
The header describes process-local RB-trees, per-type histograms, debug counters, and transient instruction-tracking state. When libdw is unavailable, static inline stubs return failure or no-op values, preserving build compatibility without type annotation behavior.

## Dependencies and Integration Points
Includes `dwarf-regs.h` and `annotate.h`, with optional `debuginfo.h` under `HAVE_LIBDW_SUPPORT`. Used by `annotate.c`, `annotate-data.c`, and architecture files such as x86 and PowerPC.

## Risks
`TYPE_STATE_MAX_REGS` is fixed at 32 to cover supported architectures; future architectures with larger register numbering need changes. Stub behavior can silently disable feature paths in builds without libdw. Histogram sizing depends on type size and can be memory-heavy.

## Test Signals
Build with and without `HAVE_LIBDW_SUPPORT` and `HAVE_SLANG_SUPPORT`. Validate ABI expectations for `data_loc_info`, type-state register bounds, tree deletion, histogram updates, and member-name lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate.c

## Purpose
Provides the core perf annotate implementation: sample accounting by symbol offset, disassembly orchestration, percentage calculation, IPC/basic-block/branch-counter aggregation, TTY/file rendering, data-type lookup integration, annotation options/config, operand-location extraction, debuginfo caching, and basic-block path discovery.

## Important APIs, Types, and Functions
Global state includes `annotate_opts`, `ann_data_stat`, pseudo data types `stackop_type` and `canary_type`, and `ann_insn_stat`.
Sample accounting flows through `hist_entry__inc_addr_samples()`, `addr_map_symbol__inc_samples()`, and `__symbol__inc_addr_samples()`.
Cycle and branch-counter accounting flows through `addr_map_symbol__account_cycles()`, `symbol__account_cycles()`, `annotation__compute_ipc()`, and branch-counter formatting helpers.
Disassembly flows through `thread__get_arch()`, `symbol__annotate()`, and `symbol__annotate2()`.
Rendering uses `hist_entry__annotate_printf()`, `hist_entry__tty_annotate()`, `hist_entry__tty_annotate2()`, `map_symbol__annotation_dump()`, and `annotation_line__write()`.
Data-type integration uses `annotate_get_insn_location()`, `hist_entry__get_data_type()`, `__hist_entry__get_data_type()`, `annotate_calc_pcrel()`, and debuginfo cache helpers.
Control-flow discovery uses `annotate_get_basic_blocks()` and related BFS helpers.

## Control Flow
Samples increment per-symbol histograms keyed by `(offset << 16 | evsel index)`. When annotation is requested, `symbol__annotate()` discovers the thread architecture, prepares `annotated_source`, sets display base address, and calls `symbol__disassemble()`. `symbol__annotate2()` then calculates percentages, indexes lines, marks jump targets, computes IPC/cycles/branch counters, initializes column widths, and marks the symbol as annotate2-ready. Rendering walks `annotation_line` entries and prints percentages, source/disassembly, arrows, cycle data, branch counters, and optional data-type comments.

## State and Persistence
Each symbol has an adjacent `struct annotation` containing `annotated_source` and optional `annotated_branch`. `annotated_source` stores disassembly/source lines, per-event histograms, sparse sample entries in a hashmap, and column widths. `annotated_branch` stores cycle histograms and branch counter arrays sized by symbol size. A sharded mutex protects annotation state. The debuginfo cache stores one DSO/debug-info pair and is intended for single-threaded data-type lookup. Annotation dump writes a `<symbol>.annotation` file when requested.

## Dependencies and Integration Points
Integrates almost every perf profiling subsystem: disassembler backends, DSO/map/symbol/thread, evsel/evlist/hists, srcline, BPF, branch stacks, debuginfo/DWARF registers, UI browser, config, and architecture registry. Architecture files provide instruction operations, parser conventions, fusion callbacks, and type-state updaters.

## Risks
Memory scales with symbol size for cycle and branch-counter arrays. Basic-block discovery uses heuristic jump conditional detection (`strstr("jmp")`). Operand-location extraction assumes objdump syntax, especially AT&T x86 memory forms. Debuginfo cache asserts single-threaded use. Error handling around sparse sample hashmap insertion can leak an entry if adding fails after allocation.

## Test Signals
Run annotate in stdio and browser paths with grouped events, empty-event skipping, source-line summaries, full-address toggles, branch stacks with cycles, branch counters, data-type comments, BPF symbols, and multiple disassembler backends. Include tests for local/external jumps, PLT symbols, lock-prefixed instructions, PC-relative calculation at the last instruction, and basic-block path discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate.h

## Purpose
Defines the public data structures and APIs for perf annotation. It is the contract between sample accounting, disassembly, UI rendering, branch/cycle analysis, data-type attribution, and architecture-specific instruction parsing.

## Important APIs, Types, and Functions
`struct annotation_options` stores display/config behavior such as source visibility, offsets, jump arrows, line counts, disassembler preference, percent type, and type display.
`struct annotation_line` represents either a source line or disassembly line with offsets, rendered text, source path, cycles, branch counters, event data, indices, and jump-source counts.
`struct disasm_line` embeds `struct annotation_line` and adds instruction metadata, operands, and raw instruction bytes.
`struct annotated_source` stores all lines and histograms for a symbol.
`struct annotated_branch` stores cycle/IPC/coverage and branch-counter data.
`struct annotation` hangs annotation state off `struct symbol`.
The header declares lifecycle, locking, sample/cycle accounting, disassembly, printing, config, operand-location, data-type lookup, branch-counter formatting, basic-block discovery, and debuginfo cache APIs.

## Control Flow
Callers account samples into symbol histograms, request disassembly through `symbol__annotate()` or `symbol__annotate2()`, calculate/render line data through the declared UI functions, and optionally resolve data types through `hist_entry__get_data_type()`. Architecture-specific parsers fill `ins_operands`; `annotate_get_insn_location()` normalizes operands into register/offset fields for data typing.

## State and Persistence
All structures are process-local and generally attached to symbols for the duration of an annotate operation. Histograms, source lists, cycles, and branch counters are allocated dynamically and released by `annotation__exit()` or purged after TTY annotation. Options are global in `annotate_opts`.

## Dependencies and Integration Points
Includes symbol config, mutexes, sparkline support, hashmap, disassembly, branch, and evsel declarations. It is included by architecture adapters, `annotate.c`, `annotate-data.c`, UI code, and code that accounts perf samples.

## Risks
The flexible array `annotation_line.data[]` requires correct allocation sizing. Histogram keys reserve 16 bits for evsel index in implementation, which assumes event indices fit that packing. Public structs expose many fields, so changes can affect UI, disassembly, and data-type code simultaneously.

## Test Signals
Compile-time tests should cover builds with different optional UI/DWARF features. Runtime tests should validate lifecycle cleanup, locking, histogram indexing, branch counter formatting, offset/full-address rendering, and operand-location extraction across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.c

## Purpose
Implements the high-level Arm SPE decoder. It pulls raw trace buffers through a callback, decodes packets with the packet decoder, normalizes address payloads, and accumulates packets into one `arm_spe_record` per SPE sample record.

## Important APIs, Types, and Functions
`arm_spe_decoder_new()` validates `get_trace`, allocates `struct arm_spe_decoder`, and stores callback state.
`arm_spe_decoder_free()` releases the decoder.
`arm_spe_decode()` calls `arm_spe_read_record()`.
`arm_spe_get_data()` refills the current trace buffer from the callback.
`arm_spe_get_next_packet()` skips PAD packets and advances buffer pointers, returning `-EBADMSG` after bad packet decode.
`arm_spe_calc_ip()` strips/repairs address metadata for instruction, branch, data virtual, data physical, and previous-branch address packets.
`arm_spe_read_record()` loops over packets until timestamp, end, input exhaustion, or error and fills `arm_spe_record` fields.

## Control Flow
The decoder refills when its current buffer is empty, decodes one packet at a time, skips padding, and updates record fields based on packet type. Timestamp and end packets terminate the current record. Address packets populate from/to/data/previous-branch addresses. Counter packets currently use total latency. Context, operation type, event, and data-source packets update corresponding record fields.

## State and Persistence
`struct arm_spe_decoder` stores callback pointers, current buffer pointer/length, the last packet, and the current output record. Each record is zeroed before reading and `context_id` defaults to all-ones. No persistent storage is used.

## Dependencies and Integration Points
Depends on `arm-spe-pkt-decoder.h` for packet parsing and encoding macros, `auxtrace`-style buffer callbacks for trace input, and perf debug helpers. Downstream Arm SPE perf code consumes `arm_spe_record` to synthesize samples/events.

## Risks
Bad packets advance only one byte before returning an error, so callers must decide whether to retry/resynchronize. Unsupported address indices warn once per index and otherwise return raw payload. Operation decoding must track Arm SPE architectural extensions; missing subclass bits produce incomplete `record.op`.

## Test Signals
Feed synthetic SPE traces containing padding, timestamp-terminated records, end-terminated records, all address indices, total latency counters, context packets, load/store subclasses, SVE/SME/GCS branches, malformed packets, and buffer-boundary splits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.h

## Purpose
Defines the public Arm SPE decoded-record API, operation/event bit flags, vendor data-source enums, buffer callback contract, and decoder object layout.

## Important APIs, Types, and Functions
`struct arm_spe_record` is the decoded sample record containing event type bits, error, operation flags, latency, instruction/target/previous branch IPs, timestamp, virtual/physical data addresses, context id, and data source.
`struct arm_spe_buffer` carries raw trace buffer pointer, length, offset, and trace number.
`struct arm_spe_params` provides the `get_trace` callback and opaque data.
`struct arm_spe_decoder` stores callback state, current record, current buffer, and last packet.
`arm_spe_decoder_new()`, `arm_spe_decoder_free()`, and `arm_spe_decode()` are the public lifecycle/decode API.
Enums define first-level operation classes, second-level load/store and branch flags, common data-source values, and vendor-specific AmpereOne/Hisi HIP source encodings.

## Control Flow
Clients initialize `arm_spe_params`, allocate a decoder, repeatedly call `arm_spe_decode()`, and read `decoder->record` after successful decode. Event macros map packet event bits into named record flags.

## State and Persistence
The decoder is stateful across calls through current buffer pointer/length and callback data. Records are overwritten on each decode. No ownership of trace buffers is implied by the header; the provider controls buffer lifetime.

## Dependencies and Integration Points
Includes `arm-spe-pkt-decoder.h` for packet definitions and event bit positions. Used by Arm SPE auxtrace processing to turn byte streams into perf records.

## Risks
Operation flags share a 32-bit field with high bits up to bit 30; additions must avoid overflow and collisions. Callback buffer lifetime must outlive decode consumption. Vendor data-source enums require downstream interpretation to avoid mixing encodings.

## Test Signals
Compile API users against the header, verify bit masks match packet decoder event enum positions, and test callback-driven decode with multiple buffers and zero-length end-of-stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.c

## Purpose
Implements low-level Arm SPE packet decoding and human-readable packet descriptions. It recognizes SPE header encodings, extracts little-endian payloads, handles padding/alignment/end packets, and formats events, operation types, addresses, context, counters, timestamps, and data-source packets.

## Important APIs, Types, and Functions
`arm_spe_get_packet()` is the public parser. It calls `arm_spe_do_get_packet()` and coalesces consecutive zero PAD bytes up to 16 bytes.
`arm_spe_pkt_name()` returns a short packet type name.
`arm_spe_pkt_desc()` formats a packet into a caller-provided buffer.
`arm_spe_payload_len()` decodes the payload size from header bits.
`arm_spe_get_payload()` validates length and reads 1/2/4/8-byte little-endian payloads.
Specific packet helpers set type/index and consume payloads for timestamp, events, data source, context, op type, counter, address, alignment, pad, and end.
Formatting helpers include `arm_spe_pkt_desc_event()`, `arm_spe_pkt_desc_op_type()`, `arm_spe_pkt_desc_addr()`, and `arm_spe_pkt_desc_counter()`.

## Control Flow
Packet decode starts with byte 0. Special headers handle PAD, END, TIMESTAMP, events, source, context, and op type. Extended headers are detected through `SPE_HEADER0_EXTENDED`; alignment is a special extended header, otherwise byte 1 is reused for address/counter classification. Address and counter packets derive their index from short or extended header bits. Description formatting switches by packet type and falls back to raw `name payload (index)` formatting on unknown subtype errors.

## State and Persistence
Parser functions are stateless aside from static packet-name tables. Description output mutates only caller-provided buffers. No heap allocation or persistent state is used.

## Dependencies and Integration Points
Depends on Linux bit macros, unaligned little-endian reads, and packet constants from `arm-spe-pkt-decoder.h`. Integrated by `arm-spe-decoder.c` for record construction and by diagnostic tooling for packet dumps.

## Risks
`arm_spe_pkt_name()` indexes the name array directly and assumes a valid enum. Extended-header handling returns `ARM_SPE_BAD_PACKET` for a single byte extended header rather than `NEED_MORE_BYTES`, which affects callers at buffer boundaries. Formatting truncation is detected but represented as an internal error then falls back for packet subtype errors only.

## Test Signals
Use byte-level fixtures for every packet class, payload size, short and extended address/counter indices, alignment padding, consecutive PAD coalescing, malformed headers, truncated payloads, and descriptions for all event/op/address/counter variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.h

## Purpose
Defines Arm SPE packet types, parser return codes, maximum packet/description sizes, header masks, packet index encodings, payload bitfield helpers, event bit positions, operation subclass predicates, and public packet parser/formatter prototypes.

## Important APIs, Types, and Functions
`enum arm_spe_pkt_type` lists BAD, PAD, END, TIMESTAMP, ADDRESS, COUNTER, CONTEXT, OP_TYPE, EVENTS, and DATA_SOURCE packets.
`struct arm_spe_pkt` carries type, index, and payload.
Constants define short and extended header recognition, address indices (`INS`, `BRANCH`, `DATA_VIRT`, `DATA_PHYS`, `PREV_BRANCH`), counter indices, context index extraction, event bit positions, and operation class/subclass decoding.
Public APIs are `arm_spe_pkt_name()`, `arm_spe_get_packet()`, and `arm_spe_pkt_desc()`.

## Control Flow
The implementation uses these masks to classify headers, derive indices, sanitize address payloads, and interpret operation/event payloads. Higher-level decode uses the same event and operation flags to populate records.

## State and Persistence
The header declares no persistent state. All macros are compile-time constants or payload predicates.

## Dependencies and Integration Points
Includes `linux/bitfield.h` for `FIELD_GET`/GENMASK helpers. Included by both the low-level packet decoder and high-level Arm SPE decoder.

## Risks
Macro correctness is architecture-contract critical. New Arm SPE extensions require adding event bits and operation subclass predicates consistently in both the header and description/high-level decoding code. Some macros use similarly named `PKT`/`PKG` identifiers, so maintenance needs careful review.

## Test Signals
Compile-time and byte-fixture tests should validate header masks, index extraction, address metadata extraction, SVE/SME vector-length calculations, GCS subclass detection, event bit positions, and parser return-code handling for bad and incomplete packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.h -->
