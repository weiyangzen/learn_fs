# sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.c

## Purpose
Implements the eBPF JIT compiler for 32-bit ARM. It translates verifier-approved eBPF instructions into ARM A32 instructions, manages 64-bit BPF registers on a 32-bit register file, emits prologue/epilogue and helper-call ABI glue, allocates executable JIT images, flushes I-cache, and installs `prog->bpf_func`.

## Important APIs, Types, And Functions
Public integration points are `bpf_int_jit_compile(struct bpf_verifier_env *, struct bpf_prog *)` and `bpf_jit_needs_zext()`. Key internals include `struct jit_ctx`, `bpf2a32` register mapping, `_emit`, `emit_mov_i`, literal-pool handling for pre-v7, `arm_bpf_get_reg*`/`put_reg*`, ALU/shift/mul/div emitters, memory load/store emitters, branch comparison emitters, `emit_bpf_tail_call`, `build_prologue`, `build_epilogue`, `build_insn`, `build_body`, and `validate_code`.

## Control Flow
Compilation runs a fake pass to count generated instructions and fill BPF instruction offsets, appends prologue/epilogue sizing, allocates a `bpf_binary_header` initialized with UDF instructions, then performs a real pass that emits the prologue, body, and epilogue. The body switch handles ALU32/ALU64, loads/stores, endian conversions, branches, helper calls, tail calls, and exits. Unsupported pseudo calls, pseudo func immediates, and atomic operations return errors so execution falls back to the interpreter. Final validation rejects any remaining UDF holes, then icache is flushed and the image is locked read-only.

## State, Dependencies, And Integration
Persistent result state is `prog->bpf_func`, `prog->jited`, and `prog->jited_len`. Temporary state includes `ctx->offsets`, optional pre-v7 literal pool `imms`, `ctx->idx`, prologue/epilogue offsets, stack size, CPU architecture, and overflow flags. Dependencies are the BPF core, verifier metadata, `bpf_jit_binary_alloc/free/lock_ro`, `bpf_jit_dump`, ARM opcode helpers, `elf_hwcap`, `cpu_architecture()`, `flush_icache_range`, and math helpers for 64-bit division.

## Risks And Test Signals
Risks are incorrect 64-bit emulation over 32-bit register pairs, stack-frame or ABI misalignment, helper-call register preservation bugs, branch offset miscalculation, literal-pool overflow, unsupported opcode fallback regressions, tail-call count mishandling, and security issues if UDF validation or RO locking fails. Test signals include upstream BPF selftests on ARM, JIT on/off comparison, verifier zext tests, tail-call chains, helper calls with stack arguments, ALU64 division/modulo, big/little endian load/store coverage, pre-v7 literal-pool builds, and `bpf_jit_enable > 1` dumps.
