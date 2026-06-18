<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c

### Purpose
`uasm-micromips.c` provides the microMIPS instruction encoding backend for the shared MIPS micro-assembler.

### Important APIs, Types, And Functions
It defines microMIPS field positions, the `M()` encoding macro, `insn_table_MM`, `build_bimm()`, `build_jimm()`, `build_insn()`, and `__resolve_relocs()`. It includes shared `uasm.c`, which generates the exported `uasm_i_*` and label/relocation helpers.

### Control Flow
Callers invoke shared `uasm_i_*` helpers. Those helpers call this file's `build_insn()`, which validates opcode support, maps variadic operands into microMIPS-specific fields, swaps halfwords for little-endian builds, writes the encoded word, and advances the buffer pointer. Relocation resolution patches PC16 branch immediates, also respecting endian halfword placement.

### State, Persistence, And Dependencies
There is no mutable global state. Persistent output is generated instruction words in caller-provided buffers. Dependencies include `asm/inst.h`, microMIPS opcode constants, `asm/uasm.h`, and shared `uasm.c`.

### Integration Points
`tlbex.c` uses the same public uasm API regardless of ISA mode; selecting this backend lets generated TLB handlers work for `CONFIG_CPU_MICROMIPS`.

### Risks
Many normal MIPS opcodes are intentionally unsupported in `insn_table_MM` and will panic if emitted in a microMIPS build. Operand order differs for some CP0/FPU control instructions. Branch and jump immediates use halfword scaling and optional ISA16 target low bit, so relocation mistakes misdirect exception handlers.

### Test Signals
Build and boot microMIPS kernels, trigger generated TLB handlers, validate unsupported instruction paths are not reached, and inspect generated handler disassembly for correct endian halfword order and branch targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c -->
