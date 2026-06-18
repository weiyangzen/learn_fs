# sources/distributed-fs/ceph-client/tools/objtool/check.c

Purpose: central objtool analysis and mutation engine. It decodes instructions, builds control-flow graphs, reads annotations and special sections, validates stack/CFI/uaccess/noinstr/retpoline/IBT/SLS rules, and emits generated metadata sections.

Important APIs/types/functions: `check()` orchestrates the full pass. Early helpers include `decode_sections()`, `decode_instructions()`, `classify_symbols()`, `add_jump_destinations()`, `add_call_destinations()`, `add_special_section_alts()`, and `add_jump_table_alts()`. Validation centers on `validate_branch()`, `validate_insn()`, `update_cfi_state()`, `validate_retpoline()`, `validate_ibt()`, `validate_sls()`, and `validate_reachable_instructions()`. Metadata writers include `create_static_call_sections()`, `create_retpoline_sites_sections()`, `create_return_sites_sections()`, `create_ibt_endbr_seal_sections()`, `create_cfi_sections()`, `create_mcount_loc_sections()`, `create_direct_call_sections()`, and `orc_create()`.

Control flow: `check()` initializes architecture CFI, CFI hash tables, optional disassembly, then decodes sections and symbols. `decode_sections()` marks rodata/noinstr/init text, initializes pv_ops, classifies symbols, decodes instructions, reads ignores/annotations, wires alternatives, jumps, calls, jump tables, unwind hints, holes, and late annotations. Validation recursively walks function branches and alternatives while tracking `struct insn_state` and `struct cfi_state`.

State and persistence behavior: most state is in-memory per instruction, symbol, section, CFI hash, and objtool file lists. Persistent outputs are new or modified ELF sections and relocations for static calls, retpolines, returns, IBT sealing, CFI, mcount, direct calls, prefix symbols, checksums, ORC, and optional NOP/RET patch hacks.

Dependencies and integration points: consumes architecture hooks from `arch.h`, ELF/symbol/reloc helpers, special-section parsing, ORC writer, disassembler, checksum support, warning/trace infrastructure, and Linux list/hash utilities. Architecture decoders provide instruction types and stack ops; ELF code persists section changes.

Risks: this is high-complexity recursive analysis with many compiler- and architecture-specific heuristics. False positives can come from missing decoder stack ops, unusual alternatives, unmodeled jump tables, or symbol size issues. Memory is intentionally leaked at process exit, and `free_insns()` only reduces peak RSS before ELF writes.

Test signals: strong coverage includes representative kernel objects for each action: stack validation, ORC, noinstr/uaccess, retpoline/rethunk/unret, IBT, SLS, static calls, mcount, prefix symbols, checksum, jump labels, alternatives, exception tables, switch tables, cold functions, weak symbol holes, and dry-run/write paths.
