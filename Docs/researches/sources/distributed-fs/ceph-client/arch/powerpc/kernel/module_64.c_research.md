
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_64.c

Purpose: 64-bit PowerPC module loader backend for ABI validation, TOC/GOT/stub sizing, symbol name normalization, relocation application, ftrace stub setup, and trampoline target discovery.

Important APIs/types/functions: `module_elf_check_arch`; `module_frob_arch_sections`; `module_init_section`; `apply_relocate_add`; `stub_for_addr`; `create_stub`; `create_ftrace_stub`; `got_for_addr`; `restore_r2`; `module_trampoline_target`; `module_finalize_ftrace`; helper types `ppc64_stub_entry`, `ppc64_got_entry`, `func_desc_t`.

Control flow: ELF flags are checked against configured ABI. Section preparation finds `.stubs`, `.toc` or PCREL `.mygot`, `.data..percpu`, symtab, and version sections; ABI v1/v2 non-PCREL builds remove leading dots from undefined symbols and version names and synthesize `.TOC.`. Stub size is computed from unique REL24/REL24_NOTOC relocations plus ftrace and out-of-line ftrace needs; PCREL builds also size GOT entries for `R_PPC64_GOT_PCREL34` and moved percpu references. Relocation then handles absolute, TOC, REL24, REL64/REL32, PCREL34, GOT_PCREL34, ENTRY, REL16, and TOCSAVE cases. External or livepatch REL24 calls route through stubs that load target/TOC data; non-external calls may use ELFv2 local-entry offsets. Non-PCREL link calls get a following `ld r2,...` restore if the ABI requires it.

State and persistence: mutates loaded module relocation targets, stub section, GOT section, ftrace fields, `.TOC.` symbol value, arch stub counters, OPD-aware function descriptors, and optional out-of-line ftrace storage. Effects persist until module unload.

Dependencies and integration: heavily coupled to PPC64 ELF ABI v1/v2, PC-relative kernel mode, ftrace/mprofile, livepatch symbol states, PowerPC prefixed instruction patching, module memory layout, and `paca_struct` kernel TOC/base fields.

Risks: relocation range checks are architecture-critical; stub alignment must be 8 bytes for prefixed instructions; dedotifying symbols can break if string tables are malformed; PCREL percpu conversion changes instruction form from `pla` to `pld`; `restore_r2` expects a nop after link branches; duplicate stub matching by function address can conflate names with same address.

Test signals: load modules for ABI v1, ABI v2, and PCREL builds; exercise external calls beyond REL24 range, percpu references, ftrace/mprofile and out-of-line ftrace, livepatch relocations, function descriptor dereference, and bad relocation/range failure paths.
