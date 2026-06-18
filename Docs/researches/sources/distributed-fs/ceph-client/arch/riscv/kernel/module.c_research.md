# sources/distributed-fs/ceph-client/arch/riscv/kernel/module.c

Purpose: Applies RISC-V ELF relocations for loadable kernel modules and finalizes module alternatives.

Important APIs/types/functions: Defines relocation apply handlers for absolute, branch, JAL, compressed branch/jump, PC-relative HI20/LO12, GOT, CALL/CALL_PLT, ADD/SUB/SET, ULEB128, unsupported dynamic/TLS relocations, relocation accumulation structures, `apply_relocate_add()`, and `module_finalize()`.

Control flow: `apply_relocate_add()` iterates relocation entries, resolves symbols and addends, finds matching HI20 relocations for LO12 entries, dispatches direct relocation handlers, or accumulates ADD/SUB/SET/ULEB128 chains by address before writing final values with overflow checks. Out-of-range calls may route through module PLT entries when module sections are enabled. Finalization applies module alternatives from the `.alternative` section.

State and persistence: Mutates loaded module text/data, module GOT/PLT sections, and temporary hash/list storage for accumulated relocations. Patched module alternatives persist until unload.

Dependencies and integration points: Depends on ELF psABI relocation constants, module loader, `module-sections.c`, alternative patching, endian helpers, and RISC-V instruction encoding.

Risks and test signals: Relocation math is high risk: range checks, PC-relative LO12 pairing, accumulation overflow, ULEB128 length, and GOT/PLT emission can break modules. Test module selftests, RISC-V module relocation test suite, far-call modules, weak unresolved symbols, compressed relocations, alternatives in modules, and error cleanup on allocation failures.
