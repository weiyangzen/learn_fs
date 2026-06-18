## sources/distributed-fs/ceph-client/arch/loongarch/kernel/module-sections.c

### Purpose
`module-sections.c` sizes and emits LoongArch module GOT, PLT, PLT index, and ftrace trampoline sections. It scans relocation records before final layout to reserve enough architecture-specific entries for long branches, GOT references, and dynamic ftrace trampolines.

### Important APIs, Types, And Functions
Public helpers are `module_emit_got_entry`, `module_emit_plt_entry`, and `module_frob_arch_sections`. Internal helpers include `compare_rela` and `count_max_entries`. The code manipulates `struct mod_section`, `struct got_entry`, `struct plt_entry`, `struct plt_idx_entry`, and relocation types such as `R_LARCH_SOP_PUSH_PLT_PCREL`, `R_LARCH_B26`, `R_LARCH_GOT_PC_HI20`, and `R_LARCH_GOT_PCADD_HI20`.

### Control Flow
`module_frob_arch_sections` finds `.got`, `.plt`, `.plt.idx`, and optional `.ftrace_trampoline` sections, rejects modules missing required sections, scans executable relocation sections, sorts relocations by info/addend to count unique PLT/GOT needs, then converts the empty sections to allocated `SHT_NOBITS` with cache-line alignment and computed size. Emission helpers reuse an existing matching entry when possible or append a new one and advance counters.

### State, Persistence, And Dependencies
The module's architecture section counters persist in `mod->arch` for relocation application. Generated GOT and PLT contents persist in loaded module memory and are executed/read by relocated code. Dependencies include module loader section mutation, LoongArch relocation definitions, ftrace trampoline constants, and section names produced by module linking.

### Integration Points
`module.c` calls `module_emit_got_entry` and `module_emit_plt_entry` while applying relocations. `module_finalize` initializes `.ftrace_trampoline` contents. Dynamic ftrace uses module trampoline slots for callsites outside direct branch range.

### Risks
Counting must match relocation application exactly; undercounting causes BUGs or rejection, while overcounting wastes module memory. Sorting relocation records mutates the in-memory module image before relocation and must be acceptable to the loader. Missing paired GOT relocations are detected late in `module_emit_got_entry`.

### Test Signals
Load modules with many external calls, far branch targets, GOT references, duplicate relocations, and dynamic ftrace enabled. Negative tests should include malformed modules missing `.got`/`.plt`/`.plt.idx` and bad unpaired GOT relocations.
