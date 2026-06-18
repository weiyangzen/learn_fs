# subset-b-006596 Research

Grouped research for `subset-b-006596`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/check.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/check.h

Purpose: Defines objtool instruction-analysis data structures shared by the checker, ORC generator, disassembler, tracing, and warning paths.

Important APIs/types/functions: `is_static_jump`, `is_dynamic_jump`, `is_jump`, `pv_ops_idx_off`, `_CHECK_H`, `INSN_CHUNK_BITS`, `INSN_CHUNK_SIZE`, `INSN_CHUNK_MAX`, `VISITED_BRANCH`, `VISITED_BRANCH_UACCESS`, `VISITED_BRANCH_MASK`, `VISITED_UNRET`.

Control flow: The checker populates `struct instruction` records, links alternatives/jump sources/call targets, tracks `struct insn_state` CFI and uaccess/noinstr flags, and exposes lookup/iteration helpers consumed by validation and ORC emission.

State and persistence behavior: Per-object in-memory analysis state lives in instruction records and alternative groups; no disk persistence except downstream ELF updates.

Dependencies and integration points: Depends on CFI, ELF sections/symbols/relocs, arch instruction types, Linux list/hlist helpers, and the optional disassembly context.

Risks: Bitfield limits (`INSN_CHUNK_BITS`), alternative-group CFI arrays, and unioned call/jump-table fields must stay consistent with checker allocation and traversal code.

Test signals: Objtool check tests should cover direct and dynamic jumps, alternatives, exception tables, static calls, uaccess/noinstr paths, and ORC output.

Source coverage: researched from the complete local file (165 lines, 3678 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum.h

Purpose: Provides objtool symbol checksum declarations or inline helpers used by livepatch diffing to decide whether functions changed.

Important APIs/types/functions: `checksum_init`, `checksum_update`, `checksum_finish`, `_OBJTOOL_CHECKSUM_H`.

Control flow: When `BUILD_CHECKSUM` is enabled, helpers initialize per-symbol checksum state, feed instruction bytes/data, and finish into `.discard.sym_checksum`; otherwise they compile away.

State and persistence behavior: Stores per-symbol checksum fields in `struct checksum`/`struct sym_checksum`; emitted discard sections are temporary build artifacts.

Dependencies and integration points: Uses `struct symbol`, `struct instruction`, Linux objtool checksum types, and the livepatch diff consumer.

Risks: Disabled builds silently omit checksum data, which makes `klp diff` reject inputs; architecture instruction normalization must remain stable to avoid false changes.

Test signals: Build with and without `BUILD_CHECKSUM`; verify `.discard.sym_checksum` size and livepatch diff changed/unchanged function detection.

Source coverage: researched from the complete local file (44 lines, 1088 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum_types.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum_types.h

Purpose: Provides objtool symbol checksum declarations or inline helpers used by livepatch diffing to decide whether functions changed.

Important APIs/types/functions: `_OBJTOOL_CHECKSUM_TYPES_H`, `sym_checksum`, `checksum`.

Control flow: When `BUILD_CHECKSUM` is enabled, helpers initialize per-symbol checksum state, feed instruction bytes/data, and finish into `.discard.sym_checksum`; otherwise they compile away.

State and persistence behavior: Stores per-symbol checksum fields in `struct checksum`/`struct sym_checksum`; emitted discard sections are temporary build artifacts.

Dependencies and integration points: Uses `struct symbol`, `struct instruction`, Linux objtool checksum types, and the livepatch diff consumer.

Risks: Disabled builds silently omit checksum data, which makes `klp diff` reject inputs; architecture instruction normalization must remain stable to avoid false changes.

Test signals: Build with and without `BUILD_CHECKSUM`; verify `.discard.sym_checksum` size and livepatch diff changed/unchanged function detection.

Source coverage: researched from the complete local file (26 lines, 376 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/disas.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/disas.h

Purpose: Declares the optional objtool disassembly formatting interface used for diagnostics, tracing, and readable instruction dumps.

Important APIs/types/functions: `disas_context_destroy`, `disas_warned_funcs`, `disas_funcs`, `disas_info_init`, `disas_insn`, `disas_print_info`, `disas_print_insn`, `_DISAS_H`, `alternative`, `disas_context`, `disassemble_info`.

Control flow: When disassembly support is compiled in, callers create a context, disassemble functions/instructions, and print annotated output; stub inlines make calls no-ops otherwise.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Integrates with binutils disassembler types, `struct objtool_file`, `struct instruction`, alternatives, and trace/warn macros.

Risks: Stub behavior can hide missing disassembly during diagnostics; context lifetime must bracket all formatted instruction use.

Test signals: Run objtool with disassembly-enabled warnings/tracing and with a build lacking disassembler support.

Source coverage: researched from the complete local file (82 lines, 2292 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/disas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/elf.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/elf.h

Purpose: Defines objtool ELF object model and APIs for reading, creating, mutating, hashing, and writing sections, symbols, and relocations.

Important APIs/types/functions: `elf_write_insn`, `elf_write`, `elf_close`, `iterate_global_symbol_by_demangled_name`, `find_symbol_hole_containing`, `has_multiple_files`, `elf_addr_size`, `elf_rela_size`, `is_undef_sym`, `is_null_sym`, `is_sec_sym`, `is_object_sym`.

Control flow: Clients open an ELF, iterate sections/symbols/relocs through cached lists and hash tables, create or update data/relocations, mark changed sections, then write and close the file.

State and persistence behavior: Owns process-local `struct elf` caches plus modified libelf data buffers; persistence occurs only through `elf_write()`.

Dependencies and integration points: Wraps libelf/GElf, Linux rbtree/list helpers, endianness utilities, checksum types, and architecture relocation helpers.

Risks: Relocation accessors must preserve 32/64-bit layout and byte order; section change flags and symbol aliases/twins/clones drive livepatch correctness.

Test signals: ELF mutation tests for 32/64-bit, endian-swapped objects, RELA creation, symbol lookup by range/name, and idempotent write/close.

Source coverage: researched from the complete local file (534 lines, 13872 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/endianness.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/endianness.h

Purpose: Centralizes objtool byte-swap decisions for host versus target ELF endianness.

Important APIs/types/functions: `need_bswap`, `_OBJTOOL_ENDIANNESS_H`, `__bswap_if_needed`.

Control flow: `need_bswap()` compares ELF data encoding to host byte order; `__bswap_if_needed` conditionally swaps scalar fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses GElf headers and libc byte-swap support through objtool ELF code.

Risks: Wrong encoding detection corrupts relocation fields and section metadata for cross-endian analysis.

Test signals: Read and mutate big-endian and little-endian test ELFs on the host.

Source coverage: researched from the complete local file (38 lines, 1086 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/endianness.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/klp.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/klp.h

Purpose: Implements or declares objtool livepatch support for diffing original/patched objects and post-link relocation conversion.

Important APIs/types/functions: `cmd_klp_diff`, `cmd_klp_post_link`, `_OBJTOOL_KLP_H`, `SHF_RELA_LIVEPATCH`, `SHN_LIVEPATCH`, `KLP_OBJECTS_SEC`, `KLP_FUNCS_SEC`, `KLP_RELOCS_SEC`, `KLP_STRINGS_SEC`, `klp_reloc`.

Control flow: `klp-diff.c` reads symbol checksums and Module.symvers, correlates original and patched symbols, marks changed/new functions, clones included code/data/relocs, emits `.klp.sym.*` symbols and intermediate `__klp_relocs`; `klp-post-link.c` later converts those into livepatch rela sections with `SHN_LIVEPATCH` after final module link.

State and persistence behavior: Maintains in-memory twin/clone/included/changed flags and emits persistent output object sections/symbols/relocations.

Dependencies and integration points: Depends on objtool ELF mutation APIs, checksum sections, Linux livepatch external symbol naming, architecture relocation adjustment, Module.symvers, and linker behavior.

Risks: Symbol correlation by FILE order/demangled names can fail or become ambiguous; KLP relocation conversion is sensitive to addends, duplicate local `sympos`, module names, and linker rewriting.

Test signals: Livepatch builds with changed, added, static, exported-module, unexported, string/rodata, weak, and duplicate local symbols; run post-link and inspect `.klp.rela.*` plus disabled original relocs.

Source coverage: researched from the complete local file (36 lines, 1060 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/klp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/objtool.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/objtool.h

Purpose: Provides objtool top-level object state and command dispatch shared by check, ORC, livepatch, and architecture hooks.

Important APIs/types/functions: `init_signal_handler`, `objtool_pv_add`, `check`, `orc_dump`, `orc_create`, `_OBJTOOL_H`, `__weak`, `pv_state`, `objtool_file`.

Control flow: `objtool_open_read()` opens one mutable ELF and initializes analysis lists/hash tables; `main()` initializes signal/subcmd/pager support, dispatches `objtool klp`, or runs the normal builtin path.

State and persistence behavior: Process-global `debug`, `indent`, and static `objtool_file file` hold transient run state; output persistence is delegated to ELF writers.

Dependencies and integration points: Uses libsubcmd, builtin option state, ELF helpers, Linux list/hash utilities, and signal handling.

Risks: The static single-file object prevents multi-file processing in one process; paravirt tracking is gated by `opts.noinstr` and assumes pv state allocation elsewhere.

Test signals: CLI dispatch for normal and `klp` subcommands, repeated open rejection, paravirt add edge cases, and top-level directory discovery from installed binary layout.

Source coverage: researched from the complete local file (55 lines, 1196 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/objtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/orc.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/orc.h

Purpose: Declares or implements ORC unwind table creation and dumping for objtool-generated stack unwind metadata.

Important APIs/types/functions: `init_orc_entry`, `orc_print_dump`, `write_orc_entry`, `_OBJTOOL_ORC_H`.

Control flow: `orc_gen.c` walks analyzed text instructions, deduplicates ORC entries, handles alternative-group byte CFI, appends section terminators, creates `.orc_unwind`/`.orc_unwind_ip` sections, and writes relocatable IP entries. `orc_dump.c` reads those sections and prints resolved symbol/section offsets or absolute IP deltas.

State and persistence behavior: Builds transient ORC list entries, then persists generated unwind sections in the target ELF.

Dependencies and integration points: Depends on checker CFI state, `asm/orc_types.h`, objtool ELF section creation, relocation lookup, and libelf for dumping.

Risks: Alternative flattening, deduplication, and terminator entries must align with unwinder expectations; malformed ORC section sizes or missing rela entries break dumps.

Test signals: Objtool ORC generation on normal text, alternatives, empty text, duplicate states, and `orc_dump` on relocatable and non-relocatable files.

Source coverage: researched from the complete local file (15 lines, 512 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/orc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/special.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/special.h

Purpose: Defines and parses objtool special sections describing alternatives, jump labels, exception tables, and switch/jump-table metadata.

Important APIs/types/functions: `special_get_alts`, `arch_handle_alternative`, `arch_support_alt_relocation`, `_SPECIAL_H`, `C_JUMP_TABLE_SECTION`, `special_alt`, `reloc`.

Control flow: `special_get_alts()` scans known special sections, validates entry sizes, resolves orig/new/key relocations into `struct special_alt`, applies arch adjustment, and returns a list for checker control-flow modeling.

State and persistence behavior: Allocates a per-run list of `special_alt` records; no direct persistence.

Dependencies and integration points: Uses architecture special-section offsets, objtool ELF relocation helpers, arch alternative handlers, and Linux list utilities.

Risks: Section layout constants must match assembler macros; missing relocations or x86 extable offset hacks can mis-model runtime control flow.

Test signals: Objects with `.altinstructions`, `__jump_table`, `__ex_table`, empty sections, bad sizes, missing relocs, and arch-specific alternative handling.

Source coverage: researched from the complete local file (44 lines, 1008 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/special.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/trace.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/trace.h

Purpose: Provides optional objtool tracing macros and CFI/alternative trace printers for debugging checker state transitions.

Important APIs/types/functions: `trace_enable`, `trace_disable`, `trace_depth_inc`, `trace_depth_dec`, `trace_insn_state`, `trace_alt_begin`, `trace_alt_end`, `_TRACE_H`, `TRACE`, `TRACE_ADDR`, `TRACE_INSN`, `TRACE_INSN_STATE`.

Control flow: Trace macros gate output on global `trace`, adjust indentation through `trace_depth`, print instruction state deltas, and annotate alternative traversal begin/end.

State and persistence behavior: Global `trace` and `trace_depth` hold process-local diagnostic state only.

Dependencies and integration points: Depends on checker instruction/CFI structures, disassembly printers, arch register names, and stderr diagnostics.

Risks: Only compiled when trace support is enabled; static register-name buffer requires duplication before nested formatting; trace depth must balance on alternative paths.

Test signals: Enable trace for functions with register-state changes, exception alternatives, jump labels, and nested alternatives.

Source coverage: researched from the complete local file (142 lines, 3391 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/util.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/util.h

Purpose: Provides a checked `snprintf` wrapper macro used when constructing bounded ELF section and symbol names.

Important APIs/types/functions: `_UTIL_H`, `snprintf_check`.

Control flow: The macro calls `snprintf`, reports truncation through `ERROR`, and returns `-1` from the caller on overflow.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on objtool warning macros and standard snprintf semantics.

Risks: It assumes use inside functions returning integer status; misuse in other return contexts will be wrong.

Test signals: Boundary-length KLP symbol/section names and normal short names.

Source coverage: researched from the complete local file (20 lines, 448 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/warn.h -->
# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/warn.h

Purpose: Defines objtool diagnostic macros that format object, ELF, glibc, function, instruction, and backtrace messages.

Important APIs/types/functions: `unindent`, `_WARN_H`, `___WARN`, `__WARN`, `__WARN_LINE`, `__WARN_ELF`, `__WARN_GLIBC`, `__WARN_FUNC`, `WARN_STR`, `WARN`, `WARN_FUNC`, `WARN_INSN`.

Control flow: Macros build location strings with section/symbol offsets, optionally include disassembly, honor `opts.werror`, and increment warning counters through shared builtin state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses ELF symbol lookup, checker instruction formatting, libelf/libc error APIs, and objtool option globals.

Risks: Location formatting allocates memory in warning paths; missing symbols degrade diagnostics; `werror` changes severity strings without changing call sites.

Test signals: Warnings for raw messages, ELF errors, function offsets, instructions with/without disassembly, and `--werror` behavior.

Source coverage: researched from the complete local file (162 lines, 4735 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/include/objtool/warn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/klp-diff.c -->
# sources/distributed-fs/ceph-client/tools/objtool/klp-diff.c

Purpose: Implements or declares objtool livepatch support for diffing original/patched objects and post-link relocation conversion.

Important APIs/types/functions: `str_hash`, `read_exports`, `read_sym_checksums`, `is_uncorrelated_static_local`, `is_clang_tmp_label`, `is_special_section`, `is_special_section_aux`, `dont_correlate`, `process_demangled_name`, `find_global_symbol_by_demangled_name`, `correlate_symbols`, `clone_sym_relocs`.

Control flow: `klp-diff.c` reads symbol checksums and Module.symvers, correlates original and patched symbols, marks changed/new functions, clones included code/data/relocs, emits `.klp.sym.*` symbols and intermediate `__klp_relocs`; `klp-post-link.c` later converts those into livepatch rela sections with `SHN_LIVEPATCH` after final module link.

State and persistence behavior: Maintains in-memory twin/clone/included/changed flags and emits persistent output object sections/symbols/relocations.

Dependencies and integration points: Depends on objtool ELF mutation APIs, checksum sections, Linux livepatch external symbol naming, architecture relocation adjustment, Module.symvers, and linker behavior.

Risks: Symbol correlation by FILE order/demangled names can fail or become ambiguous; KLP relocation conversion is sensitive to addends, duplicate local `sympos`, module names, and linker rewriting.

Test signals: Livepatch builds with changed, added, static, exported-module, unexported, string/rodata, weak, and duplicate local symbols; run post-link and inspect `.klp.rela.*` plus disabled original relocs.

Source coverage: researched from the complete local file (1862 lines, 45504 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/klp-diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/klp-post-link.c -->
# sources/distributed-fs/ceph-client/tools/objtool/klp-post-link.c

Purpose: Implements or declares objtool livepatch support for diffing original/patched objects and post-link relocation conversion.

Important APIs/types/functions: `fix_klp_relocs`, `cmd_klp_post_link`.

Control flow: `klp-diff.c` reads symbol checksums and Module.symvers, correlates original and patched symbols, marks changed/new functions, clones included code/data/relocs, emits `.klp.sym.*` symbols and intermediate `__klp_relocs`; `klp-post-link.c` later converts those into livepatch rela sections with `SHN_LIVEPATCH` after final module link.

State and persistence behavior: Maintains in-memory twin/clone/included/changed flags and emits persistent output object sections/symbols/relocations.

Dependencies and integration points: Depends on objtool ELF mutation APIs, checksum sections, Linux livepatch external symbol naming, architecture relocation adjustment, Module.symvers, and linker behavior.

Risks: Symbol correlation by FILE order/demangled names can fail or become ambiguous; KLP relocation conversion is sensitive to addends, duplicate local `sympos`, module names, and linker rewriting.

Test signals: Livepatch builds with changed, added, static, exported-module, unexported, string/rodata, weak, and duplicate local symbols; run post-link and inspect `.klp.rela.*` plus disabled original relocs.

Source coverage: researched from the complete local file (169 lines, 4323 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/klp-post-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/noreturns.h -->
# sources/distributed-fs/ceph-client/tools/objtool/noreturns.h

Purpose: Lists functions objtool treats as non-returning for control-flow validation.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The checker includes this generated/static list when annotating calls that terminate execution instead of returning to the next instruction.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Integrates with objtool call graph and kernel symbol naming.

Risks: Missing entries create false unreachable/return warnings; stale entries can hide real fallthrough.

Test signals: Control-flow validation around panic/BUG/exit-style calls and sync with kernel annotations.

Source coverage: researched from the complete local file (56 lines, 1633 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/noreturns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/objtool.c -->
# sources/distributed-fs/ceph-client/tools/objtool/objtool.c

Purpose: Provides objtool top-level object state and command dispatch shared by check, ORC, livepatch, and architecture hooks.

Important APIs/types/functions: `objtool_pv_add`, `main`, `objtool_file`.

Control flow: `objtool_open_read()` opens one mutable ELF and initializes analysis lists/hash tables; `main()` initializes signal/subcmd/pager support, dispatches `objtool klp`, or runs the normal builtin path.

State and persistence behavior: Process-global `debug`, `indent`, and static `objtool_file file` hold transient run state; output persistence is delegated to ELF writers.

Dependencies and integration points: Uses libsubcmd, builtin option state, ELF helpers, Linux list/hash utilities, and signal handling.

Risks: The static single-file object prevents multi-file processing in one process; paravirt tracking is gated by `opts.noinstr` and assumes pv state allocation elsewhere.

Test signals: CLI dispatch for normal and `klp` subcommands, repeated open rejection, paravirt add edge cases, and top-level directory discovery from installed binary layout.

Source coverage: researched from the complete local file (126 lines, 2487 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/objtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/orc_dump.c -->
# sources/distributed-fs/ceph-client/tools/objtool/orc_dump.c

Purpose: Declares or implements ORC unwind table creation and dumping for objtool-generated stack unwind metadata.

Important APIs/types/functions: `orc_dump`.

Control flow: `orc_gen.c` walks analyzed text instructions, deduplicates ORC entries, handles alternative-group byte CFI, appends section terminators, creates `.orc_unwind`/`.orc_unwind_ip` sections, and writes relocatable IP entries. `orc_dump.c` reads those sections and prints resolved symbol/section offsets or absolute IP deltas.

State and persistence behavior: Builds transient ORC list entries, then persists generated unwind sections in the target ELF.

Dependencies and integration points: Depends on checker CFI state, `asm/orc_types.h`, objtool ELF section creation, relocation lookup, and libelf for dumping.

Risks: Alternative flattening, deduplication, and terminator entries must align with unwinder expectations; malformed ORC section sizes or missing rela entries break dumps.

Test signals: Objtool ORC generation on normal text, alternatives, empty text, duplicate states, and `orc_dump` on relocatable and non-relocatable files.

Source coverage: researched from the complete local file (157 lines, 3201 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/orc_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/orc_gen.c -->
# sources/distributed-fs/ceph-client/tools/objtool/orc_gen.c

Purpose: Declares or implements ORC unwind table creation and dumping for objtool-generated stack unwind metadata.

Important APIs/types/functions: `orc_list_add`, `orc_create`, `orc_list_entry`.

Control flow: `orc_gen.c` walks analyzed text instructions, deduplicates ORC entries, handles alternative-group byte CFI, appends section terminators, creates `.orc_unwind`/`.orc_unwind_ip` sections, and writes relocatable IP entries. `orc_dump.c` reads those sections and prints resolved symbol/section offsets or absolute IP deltas.

State and persistence behavior: Builds transient ORC list entries, then persists generated unwind sections in the target ELF.

Dependencies and integration points: Depends on checker CFI state, `asm/orc_types.h`, objtool ELF section creation, relocation lookup, and libelf for dumping.

Risks: Alternative flattening, deduplication, and terminator entries must align with unwinder expectations; malformed ORC section sizes or missing rela entries break dumps.

Test signals: Objtool ORC generation on normal text, alternatives, empty text, duplicate states, and `orc_dump` on relocatable and non-relocatable files.

Source coverage: researched from the complete local file (151 lines, 3496 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/orc_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/signal.c -->
# sources/distributed-fs/ceph-client/tools/objtool/signal.c

Purpose: Installs objtool signal handling so interrupted runs can clean up or report consistently.

Important APIs/types/functions: `is_stack_overflow`, `signal_handler`, `read_stack_limit`, `init_signal_handler`.

Control flow: Initialization registers handlers for fatal/interruption signals used by the command-line tool.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses POSIX signal APIs and objtool process state.

Risks: Handlers must remain async-signal-safe and not corrupt partially written ELF output.

Test signals: Interrupt objtool during long analysis and verify exit status/temp-file cleanup.

Source coverage: researched from the complete local file (136 lines, 2865 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/special.c -->
# sources/distributed-fs/ceph-client/tools/objtool/special.c

Purpose: Defines and parses objtool special sections describing alternatives, jump labels, exception tables, and switch/jump-table metadata.

Important APIs/types/functions: `reloc_to_sec_off`, `get_alt_entry`, `special_get_alts`, `special_entry`.

Control flow: `special_get_alts()` scans known special sections, validates entry sizes, resolves orig/new/key relocations into `struct special_alt`, applies arch adjustment, and returns a list for checker control-flow modeling.

State and persistence behavior: Allocates a per-run list of `special_alt` records; no direct persistence.

Dependencies and integration points: Uses architecture special-section offsets, objtool ELF relocation helpers, arch alternative handlers, and Linux list utilities.

Risks: Section layout constants must match assembler macros; missing relocations or x86 extable offset hacks can mis-model runtime control flow.

Test signals: Objects with `.altinstructions`, `__jump_table`, `__ex_table`, empty sections, bad sizes, missing relocs, and arch-specific alternative handling.

Source coverage: researched from the complete local file (170 lines, 3953 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/special.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/sync-check.sh -->
# sources/distributed-fs/ceph-client/tools/objtool/sync-check.sh

Purpose: Shell helper that checks objtool source synchronization between kernel copies or generated lists.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Runs command-line comparisons and exits nonzero when checked files diverge.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on POSIX shell tools and the kernel tree layout.

Risks: Path assumptions can produce false failures outside the expected build tree.

Test signals: Run from the kernel tree with synced and intentionally modified files.

Source coverage: researched from the complete local file (78 lines, 1376 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/sync-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/trace.c -->
# sources/distributed-fs/ceph-client/tools/objtool/trace.c

Purpose: Provides optional objtool tracing macros and CFI/alternative trace printers for debugging checker state transitions.

Important APIs/types/functions: `trace_cfi_reg`, `trace_cfi_reg_val`, `trace_cfi_reg_ref`, `trace_insn_state`, `trace_alt_begin`, `trace_alt_end`, `TRACE_CFI_ATTR`, `TRACE_CFI_ATTR_BOOL`, `TRACE_CFI_ATTR_NUM`, `CFI_REG_NAME_MAXLEN`, `TRACE_CFI_REG_VAL`, `TRACE_CFI_REG_REF`.

Control flow: Trace macros gate output on global `trace`, adjust indentation through `trace_depth`, print instruction state deltas, and annotate alternative traversal begin/end.

State and persistence behavior: Global `trace` and `trace_depth` hold process-local diagnostic state only.

Dependencies and integration points: Depends on checker instruction/CFI structures, disassembly printers, arch register names, and stderr diagnostics.

Risks: Only compiled when trace support is enabled; static register-name buffer requires duplication before nested formatting; trace depth must balance on alternative paths.

Test signals: Enable trace for functions with register-state changes, exception alternatives, jump labels, and nested alternatives.

Source coverage: researched from the complete local file (204 lines, 5424 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/weak.c -->
# sources/distributed-fs/ceph-client/tools/objtool/weak.c

Purpose: Provides weak fallback definitions for architecture hooks so generic objtool can link when an arch does not override them.

Important APIs/types/functions: `UNSUPPORTED`.

Control flow: Weak symbols return default/no-op behavior until replaced by architecture-specific implementations at link time.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on objtool arch hook declarations and compiler weak-symbol support.

Risks: A missing arch override may silently use conservative fallback behavior.

Test signals: Link generic objtool and architecture builds; verify expected hooks are overridden.

Source coverage: researched from the complete local file (34 lines, 687 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/weak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/pcmcia/Makefile -->
# sources/distributed-fs/ceph-client/tools/pcmcia/Makefile

Purpose: Builds or implements the small PCMCIA CRC32 hash utility used to generate module alias hash values.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The Makefile builds `crc32hash`; the C utility accepts strings, computes Linux CRC32-derived hashes, and prints results for build-time use.

State and persistence behavior: No persistent runtime state; output is printed for build scripts.

Dependencies and integration points: Uses host C library, kernel tools build rules, and CRC32 helper logic.

Risks: Host/target integer-size or CRC polynomial mismatches would generate aliases that do not match kernel expectations.

Test signals: Build the tool and compare known input hashes against kernel/module alias fixtures.

Source coverage: researched from the complete local file (11 lines, 151 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/pcmcia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/pcmcia/crc32hash.c -->
# sources/distributed-fs/ceph-client/tools/pcmcia/crc32hash.c

Purpose: Builds or implements the small PCMCIA CRC32 hash utility used to generate module alias hash values.

Important APIs/types/functions: `main`.

Control flow: The Makefile builds `crc32hash`; the C utility accepts strings, computes Linux CRC32-derived hashes, and prints results for build-time use.

State and persistence behavior: No persistent runtime state; output is printed for build scripts.

Dependencies and integration points: Uses host C library, kernel tools build rules, and CRC32 helper logic.

Risks: Host/target integer-size or CRC polynomial mismatches would generate aliases that do not match kernel expectations.

Test signals: Build the tool and compare known input hashes against kernel/module alias fixtures.

Source coverage: researched from the complete local file (34 lines, 702 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/pcmcia/crc32hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/Documentation/Makefile

Purpose: Supports building perf manual pages and HTML documentation from asciidoc/asciidoctor sources.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The Makefile selects asciidoc/asciidoctor/xmlto/docbook pipelines, while config/extension files translate perf link macros and manpage references.

State and persistence behavior: Persists generated docs only through make targets; configs are declarative.

Dependencies and integration points: Depends on make, asciidoc or asciidoctor, ruby extensions, xmlto/docbook toolchain, and perf documentation sources.

Risks: Toolchain version differences can break manpage links, macro expansion, or generated filenames.

Test signals: Build man/html targets with asciidoc and asciidoctor paths and inspect cross-reference output.

Source coverage: researched from the complete local file (316 lines, 8784 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoc.conf -->
# sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoc.conf

Purpose: Supports building perf manual pages and HTML documentation from asciidoc/asciidoctor sources.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The Makefile selects asciidoc/asciidoctor/xmlto/docbook pipelines, while config/extension files translate perf link macros and manpage references.

State and persistence behavior: Persists generated docs only through make targets; configs are declarative.

Dependencies and integration points: Depends on make, asciidoc or asciidoctor, ruby extensions, xmlto/docbook toolchain, and perf documentation sources.

Risks: Toolchain version differences can break manpage links, macro expansion, or generated filenames.

Test signals: Build man/html targets with asciidoc and asciidoctor paths and inspect cross-reference output.

Source coverage: researched from the complete local file (95 lines, 2330 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoc.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoctor-extensions.rb -->
# sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoctor-extensions.rb

Purpose: Supports building perf manual pages and HTML documentation from asciidoc/asciidoctor sources.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The Makefile selects asciidoc/asciidoctor/xmlto/docbook pipelines, while config/extension files translate perf link macros and manpage references.

State and persistence behavior: Persists generated docs only through make targets; configs are declarative.

Dependencies and integration points: Depends on make, asciidoc or asciidoctor, ruby extensions, xmlto/docbook toolchain, and perf documentation sources.

Risks: Toolchain version differences can break manpage links, macro expansion, or generated filenames.

Test signals: Build man/html targets with asciidoc and asciidoctor paths and inspect cross-reference output.

Source coverage: researched from the complete local file (30 lines, 816 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoctor-extensions.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/Makefile

Purpose: Top-level perf make entry that forwards user targets into `tools/build/Makefile.build` and perf-specific makefiles.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Normalizes output directories, includes scripts, forwards goals to `Makefile.perf`, and provides clean/install/help style targets.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel tools build infrastructure, make variables such as `O`, `OUTPUT`, `DESTDIR`, and perf sub-make files.

Risks: Output-directory normalization and recursive make variable forwarding are easy to break for out-of-tree builds.

Test signals: Build, clean, install, and help targets with in-tree and `O=` output directories.

Source coverage: researched from the complete local file (122 lines, 2830 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/Makefile

Purpose: Perf architecture make fragment for `arm` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 63 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/arch-tests.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/arch-tests.h

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `ARCH_TESTS_H`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (8 lines, 130 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/arch-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (11 lines, 295 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/perf_regs.h

Purpose: Defines arm perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `perf_regs_load`, `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build arm perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (16 lines, 409 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/arch-tests.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/arch-tests.c

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (13 lines, 238 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/arch-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/dwarf-unwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/dwarf-unwind.c

Purpose: Creates architecture-specific synthetic unwind samples for perf tests.

Important APIs/types/functions: `sample_ustack`, `test__arch_unwind_sample`, `STACK_SIZE`.

Control flow: Populates sampled user registers and stack bytes from `perf_regs_load()`/assembly helpers, maps the test function, and invokes common unwind validation.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind support, perf sample structures, map/thread helpers, and architecture register layout.

Risks: Stack pointer/register index mismatches produce fragile test-only failures or mask real unwinder regressions.

Test signals: Run the architecture DWARF unwind perf test under frame-pointer and DWARF unwind configurations.

Source coverage: researched from the complete local file (64 lines, 1371 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/dwarf-unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/regs_load.S -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/regs_load.S

Purpose: Assembly helper that stores live architecture registers into the array expected by perf unwind tests.

Important APIs/types/functions: `R0`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R8`, `R9`, `SL`, `FP`.

Control flow: Defines register offsets and emits stores for general-purpose registers plus PC/LR/SP-style state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on assembler syntax, calling convention, and `perf_regs.h` ordering.

Risks: Offset drift corrupts synthetic unwind samples.

Test signals: Perf architecture unwind test and objdump review of stored registers.

Source coverage: researched from the complete local file (60 lines, 1556 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/regs_load.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/vectors-page.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/vectors-page.c

Purpose: ARM perf test for kernel vectors page symbolization/mapping behavior.

Important APIs/types/functions: `test__vectors_page`, `VECTORS__MAP_NAME`.

Control flow: Exercises perf machine/map logic for ARM exception vector addresses.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on ARM-specific maps and perf test infrastructure.

Risks: Kernel mapping layout changes can make hard-coded expectations stale.

Test signals: Run ARM perf test suite on kernels with and without vectors page mappings.

Source coverage: researched from the complete local file (26 lines, 564 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/vectors-page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/auxtrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/auxtrace.c

Purpose: Architecture auxtrace recorder setup for perf, selecting PMU trace events and filling AUXTRACE metadata.

Important APIs/types/functions: `compat_auxtrace_mmap__read_head`, `compat_auxtrace_mmap__write_tail`, `auxtrace_record`.

Control flow: Scans evlist events for architecture trace PMUs, sets full auxtrace mode, chooses mmap defaults, configures tracking events, and fills private metadata for perf.data.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace/record/session APIs, PMU sysfs capabilities, event parser, and architecture trace drivers.

Risks: Mmap size defaults, privilege checks, event ordering, and metadata type/size must match decoder expectations.

Test signals: Record/report with architecture trace PMUs, invalid mmap sizes, missing PMUs, and snapshot/full-trace modes where supported.

Source coverage: researched from the complete local file (221 lines, 4942 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/auxtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.c

Purpose: ARM CoreSight ETM perf recording support and metadata declarations.

Important APIs/types/functions: `cs_etm_is_ete`, `cs_etm_get_ro`, `cs_etm_pmu_path_exists`, `cs_etm_validate_context_id`, `cs_etm_validate_timestamp`, `cs_etm_validate_config`, `cs_etm_parse_snapshot_options`, `cs_etm_set_sink_attr`, `cs_etm_recording_options`, `cs_etm_synth_etmcr`, `cs_etmv4_synth_trcconfigr`, `cs_etm_info_priv_size`.

Control flow: Validates ETMv3/ETMv4/ETE capabilities per CPU, checks context ID/timestamp options, configures AUX buffers/snapshot mode, and records metadata paths needed by decoders.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on CoreSight PMU sysfs files, perf auxtrace APIs, CPU maps, event config terms, and page-size/privilege helpers.

Risks: Heterogeneous CPUs with missing metadata, unsupported context/timestamp options, and AUX size rounding can fail late or produce undecodable traces.

Test signals: Perf record with ETMv3, ETMv4, ETE, per-thread/per-cpu modes, snapshot mode, and invalid option combinations.

Source coverage: researched from the complete local file (925 lines, 28272 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.h

Purpose: ARM CoreSight ETM perf recording support and metadata declarations.

Important APIs/types/functions: `INCLUDE__PERF_CS_ETM_H__`, `auxtrace_record`.

Control flow: Validates ETMv3/ETMv4/ETE capabilities per CPU, checks context ID/timestamp options, configures AUX buffers/snapshot mode, and records metadata paths needed by decoders.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on CoreSight PMU sysfs files, perf auxtrace APIs, CPU maps, event config terms, and page-size/privilege helpers.

Risks: Heterogeneous CPUs with missing metadata, unsupported context/timestamp options, and AUX size rounding can fail late or produce undecodable traces.

Test signals: Perf record with ETMv3, ETMv4, ETE, per-thread/per-cpu modes, snapshot mode, and invalid option combinations.

Source coverage: researched from the complete local file (13 lines, 290 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/pmu.c

Purpose: Architecture PMU customization for perf, such as slots-per-cycle lookup or PMU capability initialization.

Important APIs/types/functions: `perf_pmu__arch_init`.

Control flow: Reads PMU sysfs capability files or sets architecture flags during PMU initialization.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU registry and architecture PMU sysfs ABI.

Risks: Missing capability files must fall back cleanly; wrong defaults distort metrics.

Test signals: Metric calculations and PMU initialization on hardware with and without optional caps.

Source coverage: researched from the complete local file (47 lines, 1416 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `libunwind__arch_reg_id`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (51 lines, 1041 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/Makefile

Purpose: Perf architecture make fragment for `arm64` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/arch-tests.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/arch-tests.h

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test__cpuid_match`, `ARCH_TESTS_H`, `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (11 lines, 211 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/arch-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (15 lines, 434 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/perf_regs.h

Purpose: Defines arm64 perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `perf_regs_load`, `ARCH_PERF_REGS_H`, `perf_event_arm_regs`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build arm64 perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (18 lines, 492 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/arch-tests.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/arch-tests.c

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (16 lines, 290 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/arch-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/cpuid-match.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/cpuid-match.c

Purpose: ARM64 perf test for CPU ID matching logic used by PMU event maps.

Important APIs/types/functions: `test__cpuid_match`.

Control flow: Feeds MIDR strings into comparison helpers to verify wildcarding of variant/revision fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on arm64 header cpuid parsing helpers and perf test framework.

Risks: Incorrect masking rejects valid event-map matches or accepts wrong CPU models.

Test signals: Perf `cpuid match` test with variant/revision and base MIDR cases.

Source coverage: researched from the complete local file (38 lines, 1130 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/cpuid-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/dwarf-unwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/dwarf-unwind.c

Purpose: Creates architecture-specific synthetic unwind samples for perf tests.

Important APIs/types/functions: `sample_ustack`, `test__arch_unwind_sample`, `STACK_SIZE`.

Control flow: Populates sampled user registers and stack bytes from `perf_regs_load()`/assembly helpers, maps the test function, and invokes common unwind validation.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind support, perf sample structures, map/thread helpers, and architecture register layout.

Risks: Stack pointer/register index mismatches produce fragile test-only failures or mask real unwinder regressions.

Test signals: Run the architecture DWARF unwind perf test under frame-pointer and DWARF unwind configurations.

Source coverage: researched from the complete local file (64 lines, 1365 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/dwarf-unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/regs_load.S -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/regs_load.S

Purpose: Assembly helper that stores live architecture registers into the array expected by perf unwind tests.

Important APIs/types/functions: `STR_REG`, `LDR_REG`, `SP`, `PC`.

Control flow: Defines register offsets and emits stores for general-purpose registers plus PC/LR/SP-style state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on assembler syntax, calling convention, and `perf_regs.h` ordering.

Risks: Offset drift corrupts synthetic unwind samples.

Test signals: Perf architecture unwind test and objdump review of stored registers.

Source coverage: researched from the complete local file (48 lines, 747 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/regs_load.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/arm-spe.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/arm-spe.c

Purpose: ARM64 SPE perf recording support, including PMU defaults, AUX buffer sizing, CPU metadata, snapshot handling, and tracking events.

Important APIs/types/functions: `arm_spe_is_set_freq`, `arm_spe_info_priv_size`, `arm_spe_save_cpu_header`, `arm_spe_info_fill`, `arm_spe_snapshot_resolve_auxtrace_defaults`, `arm_spe_setup_evsel`, `arm_spe_setup_aux_buffer`, `arm_spe_setup_tracking_event`, `arm_spe_recording_options`, `arm_spe_parse_snapshot_options`, `arm_spe_snapshot_start`, `arm_spe_snapshot_finish`.

Control flow: Detects SPE aux events, rejects frequency mode, sets sample period and DATA_SRC/PHYS_ADDR bits, calculates AUX mmap/snapshot sizes, records per-CPU MIDR/caps, tracks wrap state for snapshots, and emits auxtrace metadata.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU sysfs caps, CPU maps, record options, auxtrace callbacks, cpuid helpers, and page-size/privilege checks.

Risks: Snapshot wrap detection relies on zeroed buffers; min interval/capability reads may be absent; discard mode skips tracking setup.

Test signals: SPE record/report in full, discard, per-cpu, snapshot, privileged/unprivileged, and invalid frequency/mmap-size modes.

Source coverage: researched from the complete local file (695 lines, 18521 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/arm-spe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `_get_cpuid`, `get_cpuid`, `strcmp_cpuid_str`, `MIDR`, `MIDR_SIZE`, `MIDR_REVISION_MASK`, `MIDR_VARIANT_MASK`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (126 lines, 2970 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/hisi-ptt.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/hisi-ptt.c

Purpose: HiSilicon PTT perf auxtrace recorder for PCIe trace data.

Important APIs/types/functions: `hisi_ptt_info_priv_size`, `hisi_ptt_info_fill`, `hisi_ptt_set_auxtrace_mmap_page`, `hisi_ptt_recording_options`, `hisi_ptt_reference`, `hisi_ptt_recording_free`, `KiB`, `MiB`, `hisi_ptt_recording`, `auxtrace_record`.

Control flow: Finds a single PTT PMU event, forces period sampling, configures AUX mmap defaults, moves the event to the front, adds a dummy tracking event, and fills auxtrace info.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace, HiSilicon PTT PMU definitions, TSC reference, page-size and paranoid checks.

Risks: Code assumes a matching event before `evlist__to_front`; multiple PTT events are rejected; AUX size must be power-of-two.

Test signals: PTT record with one event, duplicate events, missing PMU, invalid mmap sizes, and report decoder metadata.

Source coverage: researched from the complete local file (189 lines, 4743 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/hisi-ptt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/machine.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/machine.c

Purpose: Architecture perf machine customization for callchain or module text handling.

Important APIs/types/functions: `arch__add_leaf_frame_record_opts`, `SMPL_REG_MASK`.

Control flow: Adjusts record options or module text start/size based on architecture-specific kernel mapping rules.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf machine/module APIs and architecture proc/sysfs module layout.

Risks: Wrong text start correction mis-symbolizes samples.

Test signals: Perf report on kernel modules and leaf-frame callchains for the target architecture.

Source coverage: researched from the complete local file (13 lines, 322 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.c

Purpose: Defines architecture memory event aliases for `perf mem`.

Important APIs/types/functions: `E`, `perf_mem_event`.

Control flow: Populates `perf_mem_event` entries with tag, display name, PMU event string, default load latency, and auxiliary-event flag.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PMU event names exposed by the architecture and common perf mem code.

Risks: Stale event names fail at record time or silently omit expected memory operations.

Test signals: Run `perf mem record/list` on supported systems and verify alias expansion.

Source coverage: researched from the complete local file (13 lines, 563 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.h

Purpose: Defines architecture memory event aliases for `perf mem`.

Important APIs/types/functions: `_ARM64_MEM_EVENTS_H`.

Control flow: Populates `perf_mem_event` entries with tag, display name, PMU event string, default load latency, and auxiliary-event flag.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PMU event names exposed by the architecture and common perf mem code.

Risks: Stale event names fail at record time or silently omit expected memory operations.

Test signals: Run `perf mem record/list` on supported systems and verify alias expansion.

Source coverage: researched from the complete local file (8 lines, 202 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/pmu.c

Purpose: Architecture PMU customization for perf, such as slots-per-cycle lookup or PMU capability initialization.

Important APIs/types/functions: `tool_pmu__cpu_slots_per_cycle`.

Control flow: Reads PMU sysfs capability files or sets architecture flags during PMU initialization.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU registry and architecture PMU sysfs ABI.

Risks: Missing capability files must fall back cleanly; wrong defaults distort metrics.

Test signals: Metric calculations and PMU initialization on hardware with and without optional caps.

Source coverage: researched from the complete local file (27 lines, 629 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/tsc.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/tsc.c

Purpose: ARM64 timestamp-counter helper used as a perf auxtrace reference clock.

Important APIs/types/functions: `rdtsc`.

Control flow: Reads the architectural virtual counter with inline assembly and returns it as `rdtsc()` equivalent.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on ARM64 counter availability and perf util TSC abstraction.

Risks: Counter frequency/availability assumptions affect trace correlation.

Test signals: Build on arm64 and compare monotonic behavior during auxtrace recording.

Source coverage: researched from the complete local file (22 lines, 498 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `LIBUNWIND__ARCH_REG_ID`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (18 lines, 345 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/common.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/common.c

Purpose: Common perf architecture helpers for locating cross-architecture binutils and identifying address-space behavior.

Important APIs/types/functions: `lookup_path`, `lookup_triplets`, `perf_env__lookup_binutils_path`, `perf_env__lookup_objdump`, `perf_env__single_address_space`.

Control flow: Maps perf environment architecture names to objdump triplet candidates, honors cross-compile environment variables, searches PATH, and reports whether an env has a single address space.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf env metadata, libc PATH handling, and installed binutils naming conventions.

Risks: Triplet lists can become stale and path lookup allocates/parses environment strings.

Test signals: Lookup objdump for native and cross perf.data environments; test missing PATH and unsupported arch names.

Source coverage: researched from the complete local file (242 lines, 5128 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/common.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/common.h

Purpose: Common perf architecture helpers for locating cross-architecture binutils and identifying address-space behavior.

Important APIs/types/functions: `perf_env__lookup_objdump`, `perf_env__single_address_space`, `ARCH_PERF_COMMON_H`, `perf_env`.

Control flow: Maps perf environment architecture names to objdump triplet candidates, honors cross-compile environment variables, searches PATH, and reports whether an env has a single address space.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf env metadata, libc PATH handling, and installed binutils naming conventions.

Risks: Triplet lists can become stale and path lookup allocates/parses environment strings.

Test signals: Lookup objdump for native and cross perf.data environments; test missing PATH and unsupported arch names.

Source coverage: researched from the complete local file (13 lines, 291 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/csky/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/csky/include/perf_regs.h

Purpose: Defines csky perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build csky perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (16 lines, 439 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/csky/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/Makefile

Purpose: Perf architecture make fragment for `loongarch` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (17 lines, 551 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/perf_regs.h

Purpose: Defines loongarch perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `ARCH_PERF_REGS_H`, `PERF_REGS_MAX`, `PERF_REGS_MASK`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build loongarch perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (14 lines, 342 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `get_cpuid`, `CPUINFO_MODEL`, `CPUINFO`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (97 lines, 1744 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `libunwind__arch_reg_id`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (83 lines, 2218 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/loongarch/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: `REG_DWARFNUM_NAME`.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (32 lines, 1123 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/perf_regs.h

Purpose: Defines mips perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `ARCH_PERF_REGS_H`, `PERF_REGS_MAX`, `PERF_REGS_MASK`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build mips perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (14 lines, 327 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/mips/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `libunwind__arch_reg_id`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (23 lines, 521 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/mips/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/Makefile

Purpose: Perf architecture make fragment for `powerpc` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/arch-tests.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/arch-tests.h

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `ARCH_TESTS_H`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (8 lines, 130 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/arch-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: `REG_DWARFNUM_NAME`.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (29 lines, 898 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/perf_regs.h

Purpose: Defines powerpc perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `perf_regs_load`, `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build powerpc perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (20 lines, 513 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/arch-tests.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/arch-tests.c

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (13 lines, 216 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/arch-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/dwarf-unwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/dwarf-unwind.c

Purpose: Creates architecture-specific synthetic unwind samples for perf tests.

Important APIs/types/functions: `sample_ustack`, `test__arch_unwind_sample`, `STACK_SIZE`.

Control flow: Populates sampled user registers and stack bytes from `perf_regs_load()`/assembly helpers, maps the test function, and invokes common unwind validation.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind support, perf sample structures, map/thread helpers, and architecture register layout.

Risks: Stack pointer/register index mismatches produce fragile test-only failures or mask real unwinder regressions.

Test signals: Run the architecture DWARF unwind perf test under frame-pointer and DWARF unwind configurations.

Source coverage: researched from the complete local file (64 lines, 1375 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/dwarf-unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/regs_load.S -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/regs_load.S

Purpose: Assembly helper that stores live architecture registers into the array expected by perf unwind tests.

Important APIs/types/functions: `R0`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R8`, `R9`, `R10`, `R11`.

Control flow: Defines register offsets and emits stores for general-purpose registers plus PC/LR/SP-style state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on assembler syntax, calling convention, and `perf_regs.h` ordering.

Risks: Offset drift corrupts synthetic unwind samples.

Test signals: Perf architecture unwind test and objdump review of stored registers.

Source coverage: researched from the complete local file (96 lines, 1560 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/tests/regs_load.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/auxtrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/auxtrace.c

Purpose: Architecture auxtrace recorder setup for perf, selecting PMU trace events and filling AUXTRACE metadata.

Important APIs/types/functions: `powerpc_vpadtl_recording_options`, `powerpc_vpadtl_info_priv_size`, `powerpc_vpadtl_info_fill`, `powerpc_vpadtl_free`, `powerpc_vpadtl_reference`, `KiB`, `auxtrace_record`.

Control flow: Scans evlist events for architecture trace PMUs, sets full auxtrace mode, chooses mmap defaults, configures tracking events, and fills private metadata for perf.data.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace/record/session APIs, PMU sysfs capabilities, event parser, and architecture trace drivers.

Risks: Mmap size defaults, privilege checks, event ordering, and metadata type/size must match decoder expectations.

Test signals: Record/report with architecture trace PMUs, invalid mmap sizes, missing PMUs, and snapshot/full-trace modes where supported.

Source coverage: researched from the complete local file (105 lines, 2313 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/auxtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/evsel.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/evsel.c

Purpose: PowerPC evsel hook that maps architecture sample weight fields.

Important APIs/types/functions: `arch_evsel__set_sample_weight`.

Control flow: Sets sample weight interpretation for PowerPC events before reporting.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on common evsel weight helpers.

Risks: Incorrect weight source skews reported memory/latency metrics.

Test signals: Perf report on weighted PowerPC samples.

Source coverage: researched from the complete local file (9 lines, 186 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/evsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `is_compat_mode`, `get_cpuid`, `get_cpuid_str`, `arch_get_runtimeparam`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (81 lines, 1926 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.c

Purpose: Defines architecture memory event aliases for `perf mem`.

Important APIs/types/functions: `E`, `perf_mem_event`.

Control flow: Populates `perf_mem_event` entries with tag, display name, PMU event string, default load latency, and auxiliary-event flag.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PMU event names exposed by the architecture and common perf mem code.

Risks: Stale event names fail at record time or silently omit expected memory operations.

Test signals: Run `perf mem record/list` on supported systems and verify alias expansion.

Source coverage: researched from the complete local file (13 lines, 445 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.h

Purpose: Defines architecture memory event aliases for `perf mem`.

Important APIs/types/functions: `_POWER_MEM_EVENTS_H`.

Control flow: Populates `perf_mem_event` entries with tag, display name, PMU event string, default load latency, and auxiliary-event flag.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PMU event names exposed by the architecture and common perf mem code.

Risks: Stale event names fail at record time or silently omit expected memory operations.

Test signals: Run `perf mem record/list` on supported systems and verify alias expansion.

Source coverage: researched from the complete local file (8 lines, 204 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/mem-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/pmu.c

Purpose: Architecture PMU customization for perf, such as slots-per-cycle lookup or PMU capability initialization.

Important APIs/types/functions: `perf_pmu__arch_init`.

Control flow: Reads PMU sysfs capability files or sets architecture flags during PMU initialization.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU registry and architecture PMU sysfs ABI.

Risks: Missing capability files must fall back cleanly; wrong defaults distort metrics.

Test signals: Metric calculations and PMU initialization on hardware with and without optional caps.

Source coverage: researched from the complete local file (13 lines, 227 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/skip-callchain-idx.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/skip-callchain-idx.c

Purpose: PowerPC callchain cleanup helper that uses DWARF CFI to skip unnecessary LR-derived callchain slots.

Important APIs/types/functions: `check_return_reg`, `check_return_addr`, `arch_skip_callchain_idx`.

Control flow: Finds the DSO/module for a sampled PC, queries `.eh_frame`/`.debug_frame`, determines whether return address is still in LR or on stack, then returns the callchain index to suppress.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libdwfl/libdw, perf thread/map/DSO/callchain structures, and PowerPC ABI register behavior.

Risks: Missing debug info falls back to no skip; incorrect CFI interpretation creates duplicate or missing callgraph arcs.

Test signals: PowerPC perf callgraph tests with leaf, non-leaf, split-debug, and missing-CFI binaries.

Source coverage: researched from the complete local file (258 lines, 6332 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/skip-callchain-idx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/sym-handling.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/sym-handling.c

Purpose: PowerPC symbol normalization and probe post-processing for ELFv2 local/global entry point semantics.

Important APIs/types/functions: `arch__choose_best_symbol`, `arch__compare_symbol_names`, `arch__compare_symbol_names_n`, `arch__sym_update`, `arch__fix_tev_from_maps`, `arch__post_process_probe_trace_events`, `PPC64LE_LEP_OFFSET`.

Control flow: Chooses best symbols, compares normalized names, updates symbol entry values, and adjusts probe trace events by local entry point offsets.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf symbols, probe-event structures, maps, GElf symbols, and PowerPC ABI conventions.

Risks: LEP/GEP handling errors place probes at wrong instruction addresses or merge distinct symbols.

Test signals: Probe placement and symbol resolution on PPC64 ELFv1/ELFv2 binaries.

Source coverage: researched from the complete local file (144 lines, 3283 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/sym-handling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `libunwind__arch_reg_id`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (93 lines, 2245 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/utils_header.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/utils_header.h

Purpose: PowerPC utility macros for reading and decoding the processor version register.

Important APIs/types/functions: `__PERF_UTIL_HEADER_H`, `mfspr`, `SPRN_PVR`, `PVR_VER`, `PVR_REV`.

Control flow: `mfspr` emits inline assembly, and PVR macros split version/revision fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PowerPC SPR assembly support.

Risks: Including on non-PowerPC would fail; callers must guard architecture.

Test signals: Build and CPU header reporting on PowerPC.

Source coverage: researched from the complete local file (16 lines, 493 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/utils_header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/riscv/Makefile

Purpose: Perf architecture make fragment for `riscv` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: `REG_DWARFNUM_NAME`.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (43 lines, 1222 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/perf_regs.h

Purpose: Defines riscv perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build riscv perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (25 lines, 625 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/riscv/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `get_cpuid`, `get_cpuid_str`, `CPUINFO_MVEN`, `CPUINFO_MARCH`, `CPUINFO_MIMP`, `CPUINFO`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (105 lines, 1921 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/riscv/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/Makefile

Purpose: Perf architecture make fragment for `s390` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 63 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: `S390_DWARF_REGS_TABLE_H`, `REG_DWARFNUM_NAME`, `s390_regstr_tbl`.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (73 lines, 2086 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/perf_regs.h

Purpose: Defines s390 perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `perf_regs_load`, `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build s390 perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (15 lines, 373 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/auxtrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/auxtrace.c

Purpose: Architecture auxtrace recorder setup for perf, selecting PMU trace events and filling AUXTRACE metadata.

Important APIs/types/functions: `cpumsf_free`, `cpumsf_info_priv_size`, `cpumsf_info_fill`, `cpumsf_recording_options`, `cpumsf_parse_snapshot_options`, `PERF_EVENT_CPUM_SF`, `PERF_EVENT_CPUM_SF_DIAG`, `DEFAULT_AUX_PAGES`, `DEFAULT_FREQ`, `auxtrace_record`.

Control flow: Scans evlist events for architecture trace PMUs, sets full auxtrace mode, chooses mmap defaults, configures tracking events, and fills private metadata for perf.data.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace/record/session APIs, PMU sysfs capabilities, event parser, and architecture trace drivers.

Risks: Mmap size defaults, privilege checks, event ordering, and metadata type/size must match decoder expectations.

Test signals: Record/report with architecture trace PMUs, invalid mmap sizes, missing PMUs, and snapshot/full-trace modes where supported.

Source coverage: researched from the complete local file (126 lines, 3087 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/auxtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `get_cpuid`, `SYSINFO_MANU`, `SYSINFO_TYPE`, `SYSINFO_MODEL`, `SRVLVL_CPUMF`, `SRVLVL_VERSION`, `SRVLVL_AUTHORIZATION`, `SYSINFO`, `SRVLVL`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (148 lines, 4042 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/machine.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/machine.c

Purpose: Architecture perf machine customization for callchain or module text handling.

Important APIs/types/functions: `arch__fix_module_text_start`.

Control flow: Adjusts record options or module text start/size based on architecture-specific kernel mapping rules.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf machine/module APIs and architecture proc/sysfs module layout.

Risks: Wrong text start correction mis-symbolizes samples.

Test signals: Perf report on kernel modules and leaf-frame callchains for the target architecture.

Source coverage: researched from the complete local file (38 lines, 1104 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/pmu.c

Purpose: Architecture PMU customization for perf, such as slots-per-cycle lookup or PMU capability initialization.

Important APIs/types/functions: `perf_pmu__arch_init`, `S390_PMUPAI_CRYPTO`, `S390_PMUPAI_EXT`, `S390_PMUCPUM_CF`.

Control flow: Reads PMU sysfs capability files or sets architecture flags during PMU initialization.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU registry and architecture PMU sysfs ABI.

Risks: Missing capability files must fall back cleanly; wrong defaults distort metrics.

Test signals: Metric calculations and PMU initialization on hardware with and without optional caps.

Source coverage: researched from the complete local file (23 lines, 500 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sh/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/sh/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (27 lines, 311 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sh/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sparc/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/sparc/Makefile

Purpose: Perf architecture make fragment for `sparc` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 63 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sparc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sparc/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/sparc/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (20 lines, 919 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/sparc/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/Makefile

Purpose: Perf architecture make fragment for `x86` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/arch-tests.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/arch-tests.h

Purpose: Declares or registers architecture-specific perf test suites.

Important APIs/types/functions: `test__rdpmc`, `test__insn_x86`, `test__intel_pt_pkt_decoder`, `test__intel_pt_hybrid_compat`, `test__bp_modify`, `test__amd_ibs_via_core_pmu`, `test__amd_ibs_period`, `test__hybrid`, `ARCH_TESTS_H`, `test_suite`.

Control flow: The global perf test runner includes `arch_tests` so arch-only tests are appended to common tests.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf test framework and architecture test implementations.

Risks: Missing null termination or stale declarations can hide tests or break the test binary.

Test signals: Run `perf test` on the target architecture and verify listed suites appear.

Source coverage: researched from the complete local file (26 lines, 753 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/arch-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/dwarf-regs-table.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (16 lines, 452 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/perf_regs.h

Purpose: Defines x86 perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `perf_regs_load`, `ARCH_PERF_REGS_H`, `PERF_REGS_MAX`, `PERF_REGS_MASK`, `PERF_SAMPLE_REGS_ABI`, `REG_NOSUPPORT`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build x86 perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (25 lines, 760 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/include/perf_regs.h -->
