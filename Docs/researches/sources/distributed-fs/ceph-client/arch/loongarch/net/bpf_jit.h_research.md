<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h -->
## sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h

### Purpose
`bpf_jit.h` defines the shared LoongArch BPF JIT context and instruction-emission helpers used by `bpf_jit.c`.

### Important APIs, Types, And Functions
Types are `struct jit_ctx` and `struct jit_data`. Emission helpers include `emit_insn`, `emit_nop()`, immediate-range macros, `bpf2la_offset()`, `epilogue_offset()`, zero/sign extension helpers, `emit_abi_ext()`, `move_addr()`, `move_imm()`, `move_reg()`, `invert_jmp_cond()`, `cond_jmp_offset()`, `emit_cond_jmp()`, `emit_uncond_jmp()`, `emit_tailcall_jmp()`, and `bpf_flush_icache()`.

### Control Flow
Most helpers are inline. During sizing passes `emit_insn` only increments `ctx->idx`; during emission it writes a LoongArch instruction word then increments. Branch helpers convert BPF relative offsets into LoongArch instruction offsets and use inverted conditional branch plus unconditional branch for 26-bit conditional jumps.

### State, Persistence, And Dependencies
State lives in `jit_ctx`: current program, instruction index, offsets, image/ro_image pointers, extable count, stack size, and BPF arena address bases. Dependencies include generic BPF headers, LoongArch instruction encoders, cache flushing, and bitfield helpers.

### Integration Points
`bpf_jit.c` includes this header for every emission path. Extable and arena fields connect instruction generation with runtime fault recovery and BPF arena addressing.

### Risks
Immediate-range checks and branch offset conversions must be exact; JIT passes rely on deterministic `ctx->idx` increments. `move_imm()` chooses variable-length sequences that affect branch offsets, so sizing and emission must remain identical.

### Test Signals
Build with JIT enabled, run BPF JIT selftests with long programs/branches, inspect emitted instruction sequences, and validate I-cache flushes after finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h -->
