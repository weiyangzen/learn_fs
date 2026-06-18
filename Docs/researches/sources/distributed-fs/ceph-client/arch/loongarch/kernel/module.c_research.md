## sources/distributed-fs/ceph-client/arch/loongarch/kernel/module.c

### Purpose
`module.c` applies LoongArch ELF RELA relocations to loaded modules and finalizes architecture-specific module features. It implements the stack-operation relocation language, direct absolute/PC-relative relocations, long-branch PLT generation, GOT references, alternatives, ORC unwind metadata, and ftrace trampoline initialization.

### Important APIs, Types, And Functions
The main exported loader hook is `apply_relocate_add`, with `module_finalize` for post-relocation setup. Relocation handlers cover `R_LARCH_32`, `R_LARCH_64`, SOP push/pop/arithmetic relocations, add/sub relocations, `R_LARCH_B26`, PCADD/PCALA, GOT_PC/GOT_PCADD, and 32/64-bit PC-relative data relocations. Helpers use `union loongarch_instruction`, `signed_imm_check`, `unsigned_imm_check`, `module_emit_plt_entry`, `module_emit_got_entry`, `apply_alternatives`, and `unwind_module_init`.

### Control Flow
For each relocation entry, the loader computes `location`, symbol value plus addend, resolves weak unresolved symbols, chooses a handler, and applies instruction-field or data updates. SOP relocations push operands onto a bounded per-module stack, perform arithmetic/logic/select operations, and pop into encoded instruction fields with alignment/range checks. `B26` and PLT PC-relative relocations use PLT entries when the target is outside the signed 128 MiB branch reach. PCADD/GOT PCADD LO12 relocation handling scans for the corresponding HI20 relocation to compute the correct low residual.

### State, Persistence, And Dependencies
Relocation effects persist in module text/data, GOT, PLT, and unwind/ftrace sections. Temporary relocation stack state is local to one relocation section. The code depends on module section addresses, relocation order enough to find HI20 partners, LoongArch instruction bitfield definitions, and helper sections sized by `module-sections.c`.

### Integration Points
The generic module loader calls `apply_relocate_add` and `module_finalize`. Alternatives integrate with CPU feature patching, ORC metadata integrates with stack unwinding, and dynamic ftrace consumes initialized ftrace PLTs. GOT/PLT emission is shared with `module-sections.c`.

### Risks
Relocation range and alignment errors can create silent bad code if not caught; this file explicitly rejects overflow and unaligned branch/immediate values. The HI20/LO12 pairing scan is subtle and can fail on unexpected relocation sequences. Stack-operation relocations are vulnerable to malformed modules exhausting or underflowing `RELA_STACK_DEPTH`. Long-branch PLT decisions use strict `>= SZ_128M` and `< -SZ_128M` checks that must match ISA reach.

### Test Signals
Build and load modules with all supported relocation families, external calls beyond branch range, GOT references, alternatives, ORC unwinding, and dynamic ftrace. Run module load/unload under `CONFIG_32BIT` and `CONFIG_64BIT` where available. Malformed relocation tests should verify `-ENOEXEC`, `-EINVAL`, and unresolved non-weak symbol failures.
