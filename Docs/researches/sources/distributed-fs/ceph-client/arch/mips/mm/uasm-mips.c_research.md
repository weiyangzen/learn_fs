<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c

### Purpose
`uasm-mips.c` provides the standard MIPS32/MIPS64 instruction encoding backend for the shared micro-assembler.

### Important APIs, Types, And Functions
It defines standard register/immediate field positions, `M()` and `M6()` encoding macros, `insn_table`, `build_bimm()`, `build_jimm()`, `build_insn()`, and `__resolve_relocs()`. It includes shared `uasm.c` to expose the instruction-emitter API.

### Control Flow
The shared emitter calls `build_insn()` with an opcode and operands. This backend rejects unsupported opcodes or the R4k DADDIU erratum case, builds fixed opcode bits plus requested fields, writes a 32-bit instruction, and advances the output pointer. PC16 relocations are later resolved as byte deltas from the branch delay-slot PC.

### State, Persistence, And Dependencies
No global mutable state is kept. Output instructions persist in generated handler buffers. Dependencies include MIPS opcode definitions, CPU errata helpers, ELF relocation constants, and shared uasm declarations.

### Integration Points
This is the normal backend used by `tlbex.c` and any other MIPS code that builds short instruction sequences at runtime.

### Risks
Opcode tables must match the CPU ISA revision, including MIPS R6 encodings for cache, LL/SC, JR, DIV/MOD, and multiplication variants. Immediate overflow only warns in field builders, while unsupported opcodes panic. Branch immediate range is limited and must be handled by callers.

### Test Signals
Boot generated TLB handlers on MIPS32, MIPS64, and MIPS R6 systems; run disassembly checks for emitted opcodes; force branch relocations near range limits; and test CPU errata builds such as DADDIU workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c -->
