# subset-b-006595 research

Grouped research for the objtool architecture adapters and shared objtool pipeline under `sources/distributed-fs/ceph-client/tools/objtool`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/decode.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/decode.c

Purpose: LoongArch implementation of the objtool architecture contract. It classifies fixed-width LoongArch instructions, extracts branch immediates, emits stack operations for CFI tracking, exposes relocation sizing, and provides generated NOP/RET bytes.

Important APIs/types/functions: `arch_reg_name` maps CFI register numbers to LoongArch names. `arch_ftrace_match()` recognizes `_mcount`. `arch_jump_destination()` computes branch targets as `offset + immediate * 4`. `arch_decode_instruction()` is the central decoder and delegates to helpers for `reg0i26`, `reg1i21`, `reg2i12`, `reg2i14`, `reg2i16`, and `reg3` encodings. `arch_initial_func_cfi_state()` initializes CFA at SP with all saved registers undefined. `arch_reloc_size()` and `arch_jump_table_sym_offset()` adapt generic jump table handling to LoongArch relocation types.

Control flow: the decoder rejects non-LoongArch ELF machines, requires `LOONGARCH_INSN_SIZE`, initializes the instruction as `INSN_OTHER`, reads a `union loongarch_instruction`, and tries encoding-specific decoders in priority order. Calls/jumps/returns/traps/bugs/nops are assigned objtool `enum insn_type` values. Stack effects are represented as allocated `struct stack_op` nodes so `check.c` can update CFA and saved-register state without knowing LoongArch opcodes.

State and persistence behavior: this file mutates only in-memory `struct instruction` fields and per-function `frame_pointer` state. It returns static buffers for generated NOP/RET instruction bytes and does not write ELF data directly; ELF writes occur later through shared objtool code.

Dependencies and integration points: depends on LoongArch kernel instruction definitions in `asm/inst.h`, ORC register constants in `asm/orc_types.h`, objtool CFI/ELF/check APIs, and `arch/elf.h` relocation aliases. Its stack operations feed `update_cfi_state()` in `check.c`; relocation sizing feeds jump table and metadata relocation generation.

Risks: the function names use `fomat` typos but are internal. The decoder is intentionally selective, so unsupported instructions become `INSN_OTHER`; missing stack-affecting opcodes can create false CFI warnings. Direct pointer casting from section data assumes alignment/endian behavior matches host build expectations. The special LoongArch `jirl` cases are narrow and could miss new ABI patterns.

Test signals: objtool tests should cover LoongArch prologues/epilogues with `addi.d`, `ld.d`, `st.d`, `ldptr.d`, `stptr.d`, direct and dynamic branches, `break` trap/bug cases, and ORC generation from compiled LoongArch objects. Regression signals include new "unsupported stack register modification" warnings or unresolved jump destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/cfi_regs.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/cfi_regs.h

Purpose: LoongArch CFI register numbering used by objtool's architecture-neutral CFI state.

Important APIs/types/functions: defines `CFI_RA`, `CFI_SP`, argument register `CFI_A0`, frame pointer `CFI_FP`, callee-saved `CFI_S0` through `CFI_S8`, `CFI_NUM_REGS`, and aliases `CFI_BP` to `CFI_FP`.

Control flow: no runtime control flow; this header is compiled into CFI structures and architecture decoder logic.

State and persistence behavior: determines array sizes for `struct cfi_init_state` and `struct cfi_state`. Incorrect numbering persists indirectly into ORC metadata because saved registers are serialized by architecture ORC code.

Dependencies and integration points: included by `include/objtool/cfi.h`; consumed by LoongArch decode and ORC files plus shared `check.c` stack validation.

Risks: register numbers must match LoongArch GPR numbering and `arch_reg_name`. A mismatch corrupts unwinder state silently.

Test signals: compile-time coverage for LoongArch objtool plus ORC dump inspection showing SP/FP/RA mappings for simple functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/cfi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/elf.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/elf.h

Purpose: declares LoongArch ELF machine and relocation constants for objtool, including fallback definitions when system headers lack them, and maps them to generic objtool relocation aliases.

Important APIs/types/functions: defines `R_LARCH_NONE`, `R_LARCH_32`, `R_LARCH_64`, `R_LARCH_32_PCREL`, `R_LARCH_64_PCREL`, `EM_LOONGARCH`, and generic aliases `R_NONE`, `R_ABS32`, `R_ABS64`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, `R_TEXT64`.

Control flow: no runtime control flow; constants are consumed by relocation classification and creation code.

State and persistence behavior: generic relocation aliases determine what relocation types objtool creates in generated sections and writes back to ELF files.

Dependencies and integration points: used by LoongArch `decode.c`, shared ELF relocation helpers, and metadata section writers in `check.c`/ORC code.

Risks: `R_DATA64` and `R_TEXT64` map to a 32-bit PC-relative relocation alias here; that must match the kernel's intended compact metadata encoding. Header drift against LoongArch ABI constants can break host builds or generated metadata.

Test signals: generated `.orc_unwind*`, call-site, and other objtool sections should have relocations accepted by LoongArch linker and kernel runtime consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/special.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/special.h

Purpose: LoongArch layout constants for special kernel metadata sections consumed by generic objtool special-section parsing.

Important APIs/types/functions: defines exception table entry size/offsets, jump label entry size/offsets, and alternative instruction entry size/offsets including original/new length fields.

Control flow: no executable control flow. Generic special parsing uses these constants to read binary entries.

State and persistence behavior: parsed special entries create in-memory `struct special_alt` records that later alter validation paths and alternative CFI propagation.

Dependencies and integration points: included by generic `objtool/special.h` implementation and LoongArch `special.c`; tied to LoongArch kernel structs in `extable.h`, `jump_label.h`, and `alternative.h`.

Risks: stale offsets produce mis-linked alternatives, bad exception targets, or invalid jump-label interpretation. These failures often surface as unresolved instructions or stack layout conflicts rather than obvious parse errors.

Test signals: objtool on LoongArch objects using exception tables, jump labels, and alternatives should produce correct alternative paths without "special: can't find" errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/special.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/orc.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/orc.c

Purpose: converts generic CFI states into LoongArch ORC unwind entries, writes ORC entries plus instruction-pointer relocations, and prints ORC dumps.

Important APIs/types/functions: `init_orc_entry()` maps `struct cfi_state` to `struct orc_entry`; `write_orc_entry()` stores entries and creates text relocations with `elf_init_reloc_text_sym()`; `orc_print_dump()` formats decoded entries.

Control flow: `init_orc_entry()` handles null CFI and undefined/end-of-stack hints early, then maps supported unwind hint types, CFA base (`CFI_SP`/`CFI_FP`), FP rule, RA rule, and signal flag. Unknown hint or base registers produce objtool errors.

State and persistence behavior: `write_orc_entry()` modifies the generated ORC section buffer and the paired IP relocation section. This persistent metadata is later written by `elf_write()`.

Dependencies and integration points: consumes LoongArch CFI register constants, `asm/orc_types.h`, and generic ORC creation. It must agree with kernel LoongArch ORC unwinder field semantics.

Risks: only SP and FP CFA bases are accepted, and only undefined/CFA/FP rules for FP and RA are serialized. New unwind forms need explicit mapping. Unlike x86 ORC writing, offsets are not byte-swapped here, so endian assumptions should be validated.

Test signals: `objtool --orc` followed by `--dump=orc` on LoongArch objects should show correct SP/FP/RA offsets for prologue, body, epilogue, undefined, and end-of-stack hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/orc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/special.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/special.c

Purpose: LoongArch special-section support for alternatives and switch/jump-table discovery.

Important APIs/types/functions: `arch_support_alt_relocation()` currently rejects PC-relative relocations in alternatives. `arch_find_switch_table()` locates switch tables via `.discard.tablejump_annotate` or the C jump table section. Helpers include `get_rodata_table_size_by_table_annotate()`, `find_reloc_by_table_annotate()`, and `find_reloc_of_rodata_c_jump_table()`. `arch_cpu_feature_name()` returns no names.

Control flow: annotated jump table relocations are scanned in pairs, grouped by text section, sorted by rodata offset to infer table size, then resolved to the first rodata relocation. C jump tables are found through relocations into `C_JUMP_TABLE_SECTION`.

State and persistence behavior: no ELF writes. It returns relocation pointers and table sizes used by shared `check.c` to mark jump-table heads and add alternative branch destinations.

Dependencies and integration points: depends on generic special parsing, relocation lookup, section rodata marking, and the common jump-table walker in `check.c`.

Risks: manual list allocation is not freed and `list_del_init(&table_list)` is suspicious for a list head; as a short-lived objtool process the leak is minor, but malformed annotations could confuse table sizing. The code increments `reloc` inside `for_each_reloc`, assuming paired entries. No CPU feature names means disassembly of alternatives shows feature numbers only.

Test signals: LoongArch switch statements and annotated C jump tables should not report "can't find switch jump table"; alternative sections with relocations should be rejected when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/special.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/decode.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/decode.c

Purpose: minimal PowerPC objtool architecture implementation, primarily enough to classify simple branch/call control flow and expose relocation sizing.

Important APIs/types/functions: `arch_reg_name` names 32 GPRs plus RA. `arch_ftrace_match()` recognizes `_mcount`. `arch_decode_instruction()` decodes PowerPC opcode 18 branch/call forms, sets instruction length to 4 or 8 for opcode 1, and stores immediate/AA flag. `arch_jump_destination()` handles absolute versus relative branch targets. `arch_initial_func_cfi_state()` initializes CFA at SP and RA at CFA+0.

Control flow: instructions are byte-swapped as needed, opcode is extracted from the high six bits, and only branch opcode 18 is classified. Branch with link becomes `INSN_CALL`, non-link branch becomes `INSN_JUMP_UNCONDITIONAL`; `bl .+4` is ignored as `INSN_OTHER`.

State and persistence behavior: mutates `struct instruction` fields only. Unsupported helpers such as hint decoding and NOP/RET generation call `exit(-1)`, signaling that corresponding objtool features are not implemented for PowerPC in this tree.

Dependencies and integration points: uses generic objtool headers and endian helpers. `arch_reloc_size()` recognizes PPC 32-bit relocation types for table walking and metadata generation.

Risks: no stack operation decoding, no dynamic branch classification, and several arch hooks abort. Enabling ORC, stack validation, or patching paths that need NOP/RET generation would fail hard.

Test signals: basic objtool runs for PowerPC should validate branch destination handling without invoking unsupported actions. Any test enabling `--orc`, unwind hints, or patch hacks should expose the `exit(-1)` limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/cfi_regs.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/cfi_regs.h

Purpose: PowerPC CFI register constants for objtool.

Important APIs/types/functions: aliases `CFI_BP` and `CFI_SP` to register 1, defines `CFI_RA` as 32, and sets `CFI_NUM_REGS` to 33.

Control flow: none; compile-time constants only.

State and persistence behavior: controls CFI array sizing and initial RA/SP register references. Because PowerPC stack validation support is limited, these mostly support basic initial state.

Dependencies and integration points: included by generic `cfi.h`, PowerPC decoder, and any shared CFI code compiled for PowerPC.

Risks: using `CFI_BP` as SP is a simplification; if full frame validation is added, more register semantics may be required.

Test signals: simple branch-only objtool operation should compile; future stack validation tests should verify register numbering against PPC ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/cfi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/elf.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/elf.h

Purpose: maps PowerPC ELF relocation types to objtool's generic relocation aliases.

Important APIs/types/functions: defines `R_NONE`, `R_ABS64`, `R_ABS32`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, and `R_TEXT64` using PPC/PPC64 relocation constants.

Control flow: none.

State and persistence behavior: determines relocation types in generated metadata sections if those features are used.

Dependencies and integration points: used by shared ELF writers and PowerPC decoder relocation sizing.

Risks: mixed PPC32/PPC64 relocation aliases must match object class and linker expectations. Some aliases use relative relocations, so consumers must interpret them consistently.

Test signals: generated metadata relocations in PPC objects should pass `relocs_check.sh` and linker validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/special.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/special.h

Purpose: PowerPC special-section binary layout constants for exception table, jump labels, and alternatives.

Important APIs/types/functions: defines sizes and offsets for exception entries, jump entries, and alternative entries.

Control flow: none; read by generic special-section code.

State and persistence behavior: affects how special-section bytes become in-memory alternative records, which in turn influence validation graph paths.

Dependencies and integration points: tied to PowerPC kernel metadata struct layouts.

Risks: stale offsets create false or missing alternatives. PowerPC `special.c` currently aborts for main hooks, so these constants are only useful if generic special parsing is enabled with a complete implementation.

Test signals: future PowerPC alternative/jump-label objtool tests should verify parsed original/new offsets and lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/special.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/special.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/special.c

Purpose: placeholder PowerPC special-section hooks.

Important APIs/types/functions: `arch_support_alt_relocation()` and `arch_find_switch_table()` call `exit(-1)`. `arch_cpu_feature_name()` returns `NULL`.

Control flow: any attempt to validate alternative relocation support or find switch tables through these hooks terminates the process.

State and persistence behavior: no persistent writes. It prevents unsupported paths from silently producing bad results.

Dependencies and integration points: compiled into the generic special/jump-table pipeline when building objtool for PowerPC.

Risks: hard exits are hostile for diagnostics and can surprise new objtool actions. Full PowerPC support requires real implementations before enabling alternatives or dynamic jump-table validation.

Test signals: tests should ensure current PowerPC workflows avoid these hooks, and future feature work should replace hard exits with deterministic support or graceful errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/special.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/decode.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/decode.c

Purpose: full x86 objtool decoder and architecture adapter. It uses kernel x86 instruction decoding to classify control flow, stack effects, ftrace calls, retpoline/rethunk symbols, relocation semantics, and generated patch bytes.

Important APIs/types/functions: `arch_decode_instruction()` is the main opcode decoder; `arch_adjusted_addend()` and `arch_insn_adjusted_addend()` normalize relocation addends; `arch_pc_relative_reloc()` and `arch_absolute_reloc()` classify relocations; `arch_nop_insn()`/`arch_ret_insn()` provide patch bytes; `arch_decode_hint_reg()` maps ORC hint registers; `arch_is_retpoline()`, `arch_is_rethunk()`, and `arch_is_embedded_insn()` identify x86 thunk symbols.

Control flow: after detecting 32-bit versus 64-bit ELF, the file decodes one instruction with `insn_decode()`, unpacks REX/ModRM/SIB fields, and switches on primary opcode. It emits stack ops for pushes, pops, calls, `leave`, RSP/RBP moves, stack arithmetic, and selected memory loads/stores. It classifies calls, returns, dynamic jumps, conditional jumps, syscalls/sysrets, STAC/CLAC, CLD/STD, traps, bugs, ENDBR, NOPs, and RIP-relative LEA.

State and persistence behavior: writes instruction metadata and allocated stack-op lists. It may add pv_ops targets through `objtool_pv_add()` when decoding special `.init.text` paravirt writes under noinstr mode. It does not write ELF bytes directly; generated NOP/RET bytes are used by shared patching code.

Dependencies and integration points: embeds kernel `inat.c`/`insn.c`, uses x86 nops, ORC types, objtool ELF/check/builtin APIs, and x86 relocation constants. Its output is central to `check.c` validation, metadata generation, disassembly, and patch-hack paths.

Risks: x86 instruction coverage is intentionally focused on control-flow and stack-relevant behavior; new compiler patterns can evade stack-op modeling. Complex SIB addressing is skipped unless simple enough. Notrack prefixes on indirect branches warn. Addend adjustment around PC-relative relocations and `__pa_symbol()` is subtle and high risk.

Test signals: objtool x86 tests should cover prologues, DRAP, stack swizzles, alternatives, retpoline/rethunk, IBT ENDBR, noinstr paravirt, relocation addends, NOP/RET patching lengths, and disassembly of RIP-relative references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/cfi_regs.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/cfi_regs.h

Purpose: x86 CFI register numbering for objtool stack validation and ORC output.

Important APIs/types/functions: defines CFI IDs for `AX`, `CX`, `DX`, `BX`, `SP`, `BP`, `SI`, `DI`, `R8` through `R15`, `RA`, and `CFI_NUM_REGS`.

Control flow: none; constants only.

State and persistence behavior: these constants index saved register state and are serialized indirectly into ORC metadata through x86 ORC mapping.

Dependencies and integration points: consumed by generic `cfi.h`, x86 decoder, x86 ORC writer, and stack validation in `check.c`.

Risks: ordering must match `arch_reg_name`, decoder ModRM register numbering, and ORC mappings. Any mismatch corrupts validation and unwind output.

Test signals: stack validation and ORC dumps for x86 should report expected SP/BP/RA behavior across standard prologues and epilogues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/cfi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/elf.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/elf.h

Purpose: x86 generic relocation aliases for objtool metadata and instruction analysis.

Important APIs/types/functions: maps `R_NONE`, `R_ABS64`, `R_ABS32`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, and `R_TEXT64` to x86-64 relocation types.

Control flow: none.

State and persistence behavior: controls relocation types for generated objtool sections and architecture-specific relocation classification.

Dependencies and integration points: used by x86 decoder, shared ELF helpers, and metadata writers in `check.c`/ORC code.

Risks: objtool mostly targets x86-64 here; using these aliases with 32-bit objects requires care. Incorrect aliasing can break linker relocation application or runtime metadata interpretation.

Test signals: generated `.orc_unwind_ip`, call-site, retpoline, return, static-call, and mcount sections should contain expected x86 relocation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/special.h -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/special.h

Purpose: x86 special-section layout constants for exception tables, jump labels, static calls, and alternatives.

Important APIs/types/functions: defines `EX_*`, `JUMP_*`, and `ALT_*` entry sizes and offsets used by generic special parsing.

Control flow: none.

State and persistence behavior: parsed entries create alternative paths and jump-label transformations that affect validation and generated diagnostics.

Dependencies and integration points: consumed by generic `special.c`, x86 `special.c`, disassembly alternative naming, and `check.c` alternative graph construction.

Risks: offsets are ABI-coupled to kernel x86 metadata. Mismatch yields wrong branch targets, alternative lengths, or feature flags.

Test signals: x86 objects using `ALTERNATIVE`, exception tables, and jump labels should parse without "weirdly overlapping alternative" or missing instruction errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/special.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/orc.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/orc.c

Purpose: x86 ORC metadata conversion, writing, and dump formatting.

Important APIs/types/functions: `init_orc_entry()` maps generic CFI to x86 `struct orc_entry`; `write_orc_entry()` stores entries, byte-swaps offsets when needed, and emits IP relocations; `orc_print_dump()` formats ORC rows.

Control flow: handles null/undefined/end-of-stack CFI early, maps call/regs hint types, maps many CFA bases (`AX`, `DX`, `SP`, `BP`, `DI`, `R10`, `R13`, indirect SP/BP), maps BP recovery state, then writes offsets.

State and persistence behavior: modifies generated ORC section data and relocation section entries. Persistent changes are committed by shared ELF writing.

Dependencies and integration points: tied to x86 ORC kernel ABI, generic ORC creation, CFI state from `check.c`, and endian helpers.

Risks: only BP is tracked as a saved frame register in the ORC entry; unsupported CFA bases produce hard errors. Offset byte-swapping must stay consistent with target endianness.

Test signals: `objtool --orc --dump=orc` should show correct CFA/BP mapping for standard frames, DRAP cases, interrupt/reg hints, indirect SP/BP hints, and undefined/end entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/orc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/special.c -->
# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/special.c

Purpose: x86 architecture hooks for alternatives, jump-table discovery, and CPU feature naming.

Important APIs/types/functions: `arch_handle_alternative()` normalizes nested alternative original lengths. `arch_support_alt_relocation()` allows alternative relocations. `arch_find_switch_table()` detects x86 switch tables from text relocations into rodata and returns the first table relocation. `arch_cpu_feature_name()` maps feature numbers through generated `cpu-feature-names.c`.

Control flow: switch-table discovery checks an instruction's relocations for rodata section symbols, adjusts PC-relative offsets, rejects named data except C jump-table sections, resolves table entry relocations, and marks rare RIP-relative table patterns by enabling `file->ignore_unreachables`.

State and persistence behavior: mutates in-memory alternative records and `objtool_file.ignore_unreachables`; no direct ELF writes.

Dependencies and integration points: used by generic special parsing, jump-table analysis in `check.c`, alternative disassembly naming, and x86 cpufeature definitions.

Risks: static state in `arch_handle_alternative()` assumes ordered parsing. Switch-table heuristics intentionally trade precision for kernel compiler patterns and can miss or overaccept unusual generated code.

Test signals: x86 switch-heavy objects, C jump-table sections, nested alternatives, and disassembly of feature-named alternatives should produce stable alternative graphs and no false unreachable warnings for known RIP-relative quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/arch/x86/special.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/builtin-check.c -->
# sources/distributed-fs/ceph-client/tools/objtool/builtin-check.c

Purpose: command-line entry for `objtool <actions> [options] file.o`, option parsing, validation, backup handling, output-copy handling, and orchestration of the `check()` pipeline.

Important APIs/types/functions: global `opts`, `objname`, `orig_argc`; `cmd_parse_options()` handles environment and CLI options; `opts_valid()` enforces option combinations; `copy_file()` and `make_backup()` preserve object files; `objtool_run()` opens the object, runs `check()`, writes changes, and closes ELF state.

Control flow: parses `OBJTOOL_ARGS` first, then `OBJTOOL_VERBOSE`, then CLI args. It validates actions, supports `--dump=orc` fast path, copies to `--output` when needed, opens the ELF, rejects linked objects without `--link`, runs `check(file)`, and writes only when not dry-run and ELF changed.

State and persistence behavior: `opts` is global process state. `copy_file()` persists output or `.orig` backup files. `objtool_run()` persists modified ELF data through `elf_write()`.

Dependencies and integration points: depends on `subcmd/parse-options`, `objtool_open_read()`, `check()`, `orc_dump()`, warning infrastructure, and the ELF writer.

Risks: `OBJTOOL_ARGS` parsing splits only on spaces and mutates the environment string. Some file descriptors in error paths may leak in `copy_file()`, though process lifetime is short. Option validation must stay aligned with feature dependencies.

Test signals: CLI tests should cover required-action errors, invalid combinations, env options, dry-run/output behavior, backup command reconstruction, `--dump=orc`, and `--werror` warning promotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/builtin-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/builtin-klp.c -->
# sources/distributed-fs/ceph-client/tools/objtool/builtin-klp.c

Purpose: small subcommand dispatcher for objtool livepatch (`klp`) operations.

Important APIs/types/functions: `struct subcmd`, `subcmds[]` mapping `diff` to `cmd_klp_diff` and `post-link` to `cmd_klp_post_link`, `cmd_klp_usage()`, and `cmd_klp()`.

Control flow: strips the `klp` word from argv, requires a subcommand, scans the static table for a name match, and dispatches to the matched function. Unknown or missing subcommands print usage and exit.

State and persistence behavior: this file itself has no persistent state. The dispatched KLP commands may create or mutate ELF artifacts elsewhere.

Dependencies and integration points: includes parse-options, objtool core, and `objtool/klp.h`; integrated by the top-level objtool command dispatcher.

Risks: usage exits the process, so embedding would need care. Adding new KLP operations requires table updates and matching command implementation.

Test signals: invoking `objtool klp`, `objtool klp diff`, `objtool klp post-link`, and an unknown subcommand should exercise dispatch and usage behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/builtin-klp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/check.c -->
# sources/distributed-fs/ceph-client/tools/objtool/check.c

Purpose: central objtool analysis and mutation engine. It decodes instructions, builds control-flow graphs, reads annotations and special sections, validates stack/CFI/uaccess/noinstr/retpoline/IBT/SLS rules, and emits generated metadata sections.

Important APIs/types/functions: `check()` orchestrates the full pass. Early helpers include `decode_sections()`, `decode_instructions()`, `classify_symbols()`, `add_jump_destinations()`, `add_call_destinations()`, `add_special_section_alts()`, and `add_jump_table_alts()`. Validation centers on `validate_branch()`, `validate_insn()`, `update_cfi_state()`, `validate_retpoline()`, `validate_ibt()`, `validate_sls()`, and `validate_reachable_instructions()`. Metadata writers include `create_static_call_sections()`, `create_retpoline_sites_sections()`, `create_return_sites_sections()`, `create_ibt_endbr_seal_sections()`, `create_cfi_sections()`, `create_mcount_loc_sections()`, `create_direct_call_sections()`, and `orc_create()`.

Control flow: `check()` initializes architecture CFI, CFI hash tables, optional disassembly, then decodes sections and symbols. `decode_sections()` marks rodata/noinstr/init text, initializes pv_ops, classifies symbols, decodes instructions, reads ignores/annotations, wires alternatives, jumps, calls, jump tables, unwind hints, holes, and late annotations. Validation recursively walks function branches and alternatives while tracking `struct insn_state` and `struct cfi_state`.

State and persistence behavior: most state is in-memory per instruction, symbol, section, CFI hash, and objtool file lists. Persistent outputs are new or modified ELF sections and relocations for static calls, retpolines, returns, IBT sealing, CFI, mcount, direct calls, prefix symbols, checksums, ORC, and optional NOP/RET patch hacks.

Dependencies and integration points: consumes architecture hooks from `arch.h`, ELF/symbol/reloc helpers, special-section parsing, ORC writer, disassembler, checksum support, warning/trace infrastructure, and Linux list/hash utilities. Architecture decoders provide instruction types and stack ops; ELF code persists section changes.

Risks: this is high-complexity recursive analysis with many compiler- and architecture-specific heuristics. False positives can come from missing decoder stack ops, unusual alternatives, unmodeled jump tables, or symbol size issues. Memory is intentionally leaked at process exit, and `free_insns()` only reduces peak RSS before ELF writes.

Test signals: strong coverage includes representative kernel objects for each action: stack validation, ORC, noinstr/uaccess, retpoline/rethunk/unret, IBT, SLS, static calls, mcount, prefix symbols, checksum, jump labels, alternatives, exception tables, switch tables, cold functions, weak symbol holes, and dry-run/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/disas.c -->
# sources/distributed-fs/ceph-client/tools/objtool/disas.c

Purpose: BFD-backed disassembly and diagnostic formatting for objtool warnings, tracing, explicit `--disas`, and alternative visualization.

Important APIs/types/functions: `disas_context_create()` initializes libopcodes/BFD state through `arch_disas_info_init()`. `disas_insn()` disassembles one instruction. `disas_print_insn()` and `disas_print_info()` format output. `disas_alt_type_name()`, `disas_alt_name()`, and `disas_alt()` format alternatives. `disas_warned_funcs()` and `disas_funcs()` drive function-level output.

Control flow: creates a context with custom memory and address printers, resolves printed addresses through instruction destinations, relocations, symbols, and alternative remapping, then prints either normal instruction streams or compact/wide alternative tables. Alternative printers collect default and replacement instruction strings, trim trailing NOPs, and align output.

State and persistence behavior: owns transient `struct disas_context` and allocated alternative strings. It writes only to stdout/stderr and does not mutate ELF files.

Dependencies and integration points: depends on BFD/dis-asm compatibility, architecture-specific disassembly setup, objtool instruction graph state, relocation lookup, special alternative data, and global `opts`.

Risks: hard limits `DISAS_ALT_MAX` and `DISAS_ALT_INSN_MAX` can truncate unusual alternative sets. Symbol resolution is heuristic around `_THIS_IP_`, section symbols, and alternative-applied addresses. Missing BFD support disables disassembly-related diagnostics.

Test signals: verify disassembly for warned functions, wildcard/function-pattern `--disas`, compact and `--wide` alternatives, exception/jump-table alternatives, RIP-relative relocations, and big/little-endian architecture setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/disas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/elf.c -->
# sources/distributed-fs/ceph-client/tools/objtool/elf.c

Purpose: objtool ELF access and mutation layer. It reads sections, symbols, relocations, builds lookup indexes, creates new symbols/sections/relocations, patches instruction bytes, writes changed ELF files, and supports temporary ELF creation.

Important APIs/types/functions: lookup APIs include `find_section_by_name()`, `find_symbol_by_offset()`, `find_func_by_offset()`, `find_symbol_containing()`, `find_symbol_by_name()`, and `find_reloc_by_dest_range()`. Readers include `read_sections()`, `read_symbols()`, `mark_group_syms()`, and `read_relocs()`. Mutation APIs include `elf_create_symbol()`, `elf_create_section()`, `elf_create_rela_section()`, `elf_create_reloc()`, `elf_create_section_pair()`, `elf_write_insn()`, `elf_write()`, and `elf_close()`.

Control flow: `elf_open_read()` initializes libelf, opens the file in the requested mode, reads headers, sections, symbols, group links, and relocations. Hash tables and interval trees accelerate lookups. Symbol ingestion demangles local suffixes, tracks aliases, cold subfunctions, prefix symbols, KLP symbols, and section symbols. Relocation creation manages libelf data buffers and internal relocation arrays.

State and persistence behavior: maintains in-memory `struct elf`, section lists, symbol lists, hash tables, symbol trees, relocation arrays, changed flags, and optional temp-file names. Persistent writes happen through `elf_write()` and `elf_close()` rename of temp files. `elf_write_insn()` directly modifies section data buffers before writeback.

Dependencies and integration points: used by nearly every objtool pass. It wraps libelf/GELF, Linux interval trees/hash helpers, architecture relocation aliases from `arch/elf.h`, and warning infrastructure.

Risks: symbol aliasing and cold-function parent/child adjustment are subtle. Libelf over-allocation requires manual truncation. Relocation array reallocation updates symbol-linked relocation lists and hash nodes, which is error-prone. Many allocations are intentionally leaked because objtool exits after one run.

Test signals: tests should cover empty objects, missing `.symtab`, extended section indexes, local/global symbol insertion, section-symbol relocation creation, duplicate reloc detection, changed section writeback, temp-file rename, cold function handling, and generated metadata sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/arch.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/arch.h

Purpose: architecture abstraction contract for objtool instruction classification, stack operations, relocation behavior, patch bytes, special thunk recognition, and disassembly setup.

Important APIs/types/functions: defines `enum insn_type`, stack operation source/destination enums and structs, `struct stack_op`, and arch hook prototypes such as `arch_decode_instruction()`, `arch_initial_func_cfi_state()`, `arch_jump_destination()`, `arch_insn_adjusted_addend()`, `arch_nop_insn()`, `arch_ret_insn()`, `arch_decode_hint_reg()`, `arch_pc_relative_reloc()`, `arch_reloc_size()`, and optional disassembly init.

Control flow: none directly; it defines the interface used by shared objtool code to call into selected architecture implementation.

State and persistence behavior: stack-op and instruction type definitions determine how decoded state flows into CFI validation and metadata generation. No persistence by itself.

Dependencies and integration points: includes objtool file and CFI declarations, and BFD types under `DISAS`. Implemented by x86, LoongArch, and PowerPC files in this work item.

Risks: adding a new `INSN_*` or stack op requires updates in decoders, validators, disassembler, and possibly ORC writers. Weak default hooks in shared code hide unsupported architecture behavior unless tested.

Test signals: architecture implementations should compile against this header and common validation tests should exercise every instruction type and stack-op variant used by decoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/builtin.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/builtin.h

Purpose: shared declaration of objtool command options and top-level command entry points.

Important APIs/types/functions: `struct opts` groups action flags and option flags, including ORC, CFI, IBT, retpoline, rethunk, noinstr, uaccess, disassembly, dry-run, output, stats, trace, verbose, werror, and wide output. Declares global `opts`, `cmd_parse_options()`, `objtool_run()`, `make_backup()`, and `cmd_klp()`.

Control flow: none; consumers branch heavily on the global flags declared here.

State and persistence behavior: `opts` is global mutable process state set by `builtin-check.c` and read by analysis, ELF, disassembly, trace, and architecture code. Some flags cause persistent ELF changes.

Dependencies and integration points: includes `subcmd/parse-options.h` and is included across objtool modules.

Risks: global options make feature interactions implicit. Adding a flag requires updates to parser, validation, and all consumers.

Test signals: CLI option parsing tests should verify each field affects the expected downstream behavior and rejects invalid combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/builtin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/cfi.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/cfi.h

Purpose: architecture-neutral CFI data model used by objtool stack validation and ORC generation.

Important APIs/types/functions: defines sentinel bases `CFI_UNDEFINED`, `CFI_CFA`, `CFI_SP_INDIRECT`, `CFI_BP_INDIRECT`; `struct cfi_reg`; `struct cfi_init_state`; and `struct cfi_state` with register rules, value tracking, CFA, stack size, DRAP metadata, hint type, scratch flags, signal/end/force flags, and hash node.

Control flow: none; it provides the state structure transformed by validation code.

State and persistence behavior: `struct cfi_state` instances are hashed and shared during validation. Their contents are later serialized into ORC entries by architecture ORC code.

Dependencies and integration points: includes architecture register constants from `arch/cfi_regs.h` and Linux list/hash support. Used by `check.c`, architecture decoders, ORC writers, and unwind hint readers.

Risks: `hash` must remain first for `cficmp()` assumptions in `check.c`. Any field added to `struct cfi_state` changes hash/equality behavior and can affect CFI reuse/conflict detection.

Test signals: stack validation tests should exercise CFA base changes, saved/restored registers, indirect stack bases, DRAP, forced undefined hints, signal frames, and alternative CFI conflict detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/cfi.h -->
