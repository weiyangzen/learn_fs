<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c -->
## sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c

### Purpose
`bpf_jit_comp.c` implements common MIPS eBPF JIT logic shared by 32-bit and 64-bit backends. It manages register save/restore helpers, ALU and jump emission, atomic 32-bit sequences, branch relaxation, multi-pass offset convergence, executable image allocation, and the public JIT compile entry.

### Important APIs, Types, And Functions
Public/common helpers include `push_regs()`, `pop_regs()`, `get_target()`, `get_offset()`, `emit_mov_i()`, `emit_mov_r()`, `valid_alu_i()`, `rewrite_alu_i()`, `emit_alu_i()`, `emit_alu_r()`, `emit_atomic_r()`, `emit_cmpxchg_r()`, `emit_bswap_r()`, `valid_jmp_i()`, `setup_jmp_i()`, `setup_jmp_r()`, `finish_jmp()`, `emit_jmp_i()`, `emit_jmp_r()`, `emit_ja()`, `emit_exit()`, `bpf_jit_needs_zext()`, and `bpf_int_jit_compile()`.

### Control Flow
Compilation first dry-runs the body to discover register/stack use. A second phase builds the prologue and repeatedly dry-runs the body to compute instruction offsets, converting out-of-range PC-relative branches into inverted-branch plus absolute-jump sequences until descriptors converge. It then emits the epilogue, allocates JIT memory filled with trap instructions, performs the real code generation pass, fills line info, locks the image read-only executable, flushes icache, optionally dumps code, and marks the program jited.

### State, Persistence, And Dependencies
State lives in `struct jit_context`: BPF program, descriptor table, target buffer, indices, branch conversion count, accessed/clobbered masks, and stack sizes. Persistent output is the executable BPF image and updated `struct bpf_prog`. Dependencies include Linux BPF verifier/JIT APIs, MIPS uasm, CPU feature/ISA flags, cache flush, JIT binary allocator, and backend-specific prologue/epilogue/instruction builders.

### Integration Points
The Linux BPF core calls `bpf_int_jit_compile()`. `bpf_jit_comp32.c` or `bpf_jit_comp64.c` supply width-specific instruction translation. The verifier is told zero-extension is needed through `bpf_jit_needs_zext()`.

### Risks
Branch offset convergence is subtle; failure falls back to interpreter after warning. Absolute jumps require target and PC to share upper address bits. Atomic LL/SC loops include R10000 and Loongson workarounds. MIPS 32-bit ALU sign extension means verifier-inserted zext is required. Any wrong descriptor index corrupts jump targets or line info.

### Test Signals
Run BPF selftests on 32-bit and 64-bit MIPS, especially long programs with far branches, atomics, cmpxchg, byte swaps, signed/unsigned JMP32, JIT line info, zext insertion, `bpf_jit_enable > 1` dumps, and allocation failure fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c -->
