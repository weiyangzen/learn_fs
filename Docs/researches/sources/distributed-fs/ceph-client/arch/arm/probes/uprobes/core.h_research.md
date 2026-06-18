## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.h

### Purpose
Declares the ARM uprobe decoder callbacks and shared decode-action table used between `core.c` and `actions-arm.c`.

### Important APIs, Types, And Functions
Exports prototypes for `uprobe_decode_ldmstm`, `decode_ldr`, `decode_rd12rn16rm0rs8_rwflags`, `decode_wb_pc`, `decode_pc_ro`, and `uprobes_probes_actions[]`.

### Control Flow
There is no runtime flow. The header allows the instruction analyzer to pass function pointers to the generic ARM probe decoder and lets action implementations remain in a separate translation unit.

### State, Persistence, And Dependencies
It declares no storage except the external action table. It depends on decode types such as `probes_opcode_t`, `struct arch_probes_insn`, and `struct decode_header` being visible through including C files.

### Integration Points
Acts as the private contract for ARM uprobe code under `arch/arm/probes/uprobes`.

### Risks
Prototype drift breaks build or, worse, mismatches decoder semantics. Since it is private, broad kernel users should not include it.

### Test Signals
Compile with `CONFIG_UPROBES=y` and run sparse/compiler checks to catch prototype or constness mismatches.
