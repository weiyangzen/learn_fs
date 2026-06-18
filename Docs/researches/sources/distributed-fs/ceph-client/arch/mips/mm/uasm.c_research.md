<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c

### Purpose
`uasm.c` is the shared source for a compact MIPS micro-assembler used by runtime code generators. It defines opcode IDs, field builders, public instruction-emitter wrappers, label/relocation management, address materialization helpers, and labeled-branch convenience functions.

### Important APIs, Types, And Functions
Core pieces include `enum opcode`, `struct insn`, `build_rs/rt/rd/re/simm/uimm/scimm/func/set()`, the `I_*` wrapper macros that export `uasm_i_*`, `uasm_build_label()`, `uasm_r_mips_pc16()`, `uasm_resolve_relocs()`, `uasm_move_relocs()`, `uasm_move_labels()`, `uasm_copy_handler()`, `uasm_insn_has_bdelay()`, `UASM_i_LA_mostly()`, `UASM_i_LA()`, and the `uasm_il_*` labeled branch helpers.

### Control Flow
Architecture backends include this file after defining instruction tables and `build_insn()`. Public emitters append encoded instructions to caller buffers. Label helpers record target addresses, relocation helpers record branch sites, copy/move helpers adjust metadata when generated handlers are folded, and `uasm_resolve_relocs()` patches pending branches once all labels are known.

### State, Persistence, And Dependencies
There is no shared mutable state. Callers own instruction buffers, label arrays, and relocation arrays. Dependencies are supplied by the including backend and by `asm/uasm.h`; Octeon builds also apply a prefetch erratum substitution.

### Integration Points
`tlbex.c` is the main consumer, using uasm to build exception handlers and move/copy handler fragments safely. The API is exported for other MIPS runtime code-generation users.

### Risks
The assembler intentionally does not hide branch delay slots or pipeline hazards, so callers must emit correct nops and hazard instructions. Label arrays require `UASM_LABEL_INVALID` termination. Address materialization must match 32-bit compatibility and 64-bit sign-extension rules. Copying handler fragments requires relocation and label moves to stay in sync.

### Test Signals
Validate generated handler disassembly, branch relocation at positive and negative offsets, handler folding across delay slots, 32-bit and 64-bit address loads, Octeon prefetch substitution, and exported helper use under module or built-in code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c -->
