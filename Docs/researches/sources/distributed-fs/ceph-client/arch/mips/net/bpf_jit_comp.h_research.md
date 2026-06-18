<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h -->
## sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h

### Purpose
`bpf_jit_comp.h` declares shared MIPS eBPF JIT register constants, internal descriptor flags, the JIT context structure, emission macros, errata workarounds, and common/backend function interfaces.

### Important APIs, Types, And Functions
It defines MIPS register numbers, `MIPS_JMP_MASK`, `JIT_MAX_ITERATIONS`, `JIT_JNSET`, `JIT_JNOP`, `JIT_DESC_CONVERT`, `struct jit_context`, `emit()`/`__emit()`, LL/SC and JALR workaround macros, `access_reg()`, `clobber_reg()`, all common emitter prototypes, and backend hooks `build_prologue()`, `build_epilogue()`, and `build_insn()`.

### Control Flow
The header itself has no runtime control flow beyond inline helpers. The `emit` macro either writes an instruction through `uasm_i_*` when the target buffer exists or just increments `jit_index` during dry runs. Access/clobber helpers update bitmasks used by prologue/epilogue generation.

### State, Persistence, And Dependencies
Persistent state is caller-owned `struct jit_context`. Dependencies include Linux BPF types, MIPS register/ISA conventions, uasm emitters, and CPU errata config symbols.

### Integration Points
Common JIT code and 32-bit/64-bit backends include this header to share ABI, register, and helper contracts.

### Risks
Register aliases differ between o32 and n64 argument registers. The emit macro must keep dry-run and real-run instruction counts identical. Errata macros change branch offsets and loop sizes, so code using fixed offsets must include `LLSC_offset`.

### Test Signals
Compile both width backends, inspect prologue save masks and stack sizes, run atomic BPF programs on errata-enabled builds, and compare dry-run instruction counts against emitted code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h -->
