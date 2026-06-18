# sources/distributed-fs/ceph-client/tools/objtool/klp-diff.c

Purpose: Implements or declares objtool livepatch support for diffing original/patched objects and post-link relocation conversion.

Important APIs/types/functions: `str_hash`, `read_exports`, `read_sym_checksums`, `is_uncorrelated_static_local`, `is_clang_tmp_label`, `is_special_section`, `is_special_section_aux`, `dont_correlate`, `process_demangled_name`, `find_global_symbol_by_demangled_name`, `correlate_symbols`, `clone_sym_relocs`.

Control flow: `klp-diff.c` reads symbol checksums and Module.symvers, correlates original and patched symbols, marks changed/new functions, clones included code/data/relocs, emits `.klp.sym.*` symbols and intermediate `__klp_relocs`; `klp-post-link.c` later converts those into livepatch rela sections with `SHN_LIVEPATCH` after final module link.

State and persistence behavior: Maintains in-memory twin/clone/included/changed flags and emits persistent output object sections/symbols/relocations.

Dependencies and integration points: Depends on objtool ELF mutation APIs, checksum sections, Linux livepatch external symbol naming, architecture relocation adjustment, Module.symvers, and linker behavior.

Risks: Symbol correlation by FILE order/demangled names can fail or become ambiguous; KLP relocation conversion is sensitive to addends, duplicate local `sympos`, module names, and linker rewriting.

Test signals: Livepatch builds with changed, added, static, exported-module, unexported, string/rodata, weak, and duplicate local symbols; run post-link and inspect `.klp.rela.*` plus disabled original relocs.

Source coverage: researched from the complete local file (1862 lines, 45504 bytes).
