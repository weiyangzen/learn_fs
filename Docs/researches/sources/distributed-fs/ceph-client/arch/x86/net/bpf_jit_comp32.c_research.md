# sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp32.c

## Purpose
Implements the IA32 x86 eBPF JIT backend. Because 32-bit x86 lacks enough 64-bit general registers, it maps most BPF registers to scratch stack slots and emits paired 32-bit operations for 64-bit BPF semantics. It supports normal calls, kfunc calls, direct memory operations, tail calls, and core ALU/branch operations, but explicitly rejects several newer or complex operations such as BPF-to-BPF pseudo calls, 64-bit div/mod, and atomic RMW instructions.

## Important APIs, types, and functions
- `bpf2ia32` maps each BPF register to two IA32 registers or scratch offsets. `BPF_REG_AX` is backed by `esi:edi`; most other BPF registers live in stack scratch space.
- `emit_ia32_*()` helpers generate 32-bit moves, ALU ops, 64-bit add/sub/carry sequences, byte-order conversion, shifts, multiply, division/modulo, and stack argument pushes.
- `emit_prologue()` and `emit_epilogue()` establish the IA32 BPF frame, save/restore `ebp`, `edi`, `esi`, and `ebx`, reserve `SCRATCH_SIZE`, initialize BPF FP and tail-call count, and return `edx:eax`.
- `emit_bpf_tail_call()` implements the 32-bit tail-call helper path and jumps through `edx` to `prog->bpf_func + PROLOGUE_SIZE`.
- `emit_kfunc_call()` adapts BPF register arguments to the i386 `-mregparm=3` calling convention using `btf_func_model`.
- `do_jit()` translates BPF instructions and validates output length against the convergence pass.
- `bpf_int_jit_compile()` drives up to 20 convergence passes, allocates executable memory with `bpf_jit_binary_alloc()`, locks it read-only, and publishes `prog->bpf_func`.
- `bpf_jit_needs_zext()` returns true, telling the verifier/JIT contract that explicit zero extension is required.

## Control flow
The top-level compile path exits immediately unless JIT is requested. It allocates an `addrs[]` array for every BPF instruction and seeds it with a 64-byte estimate. `do_jit()` first emits the fixed-size prologue, then iterates instruction by instruction, emitting into a temporary buffer and recording cumulative offsets. On stable length, executable memory is allocated and a final pass copies bytes into the image. If the image pass changes length or an unsupported opcode is encountered, compilation falls back by leaving the program not JITed.

Instruction translation is stack-register heavy. BPF 64-bit registers are split into low/high halves. 64-bit arithmetic emits carry/borrow logic over the low/high halves; shifts handle `<32`, `>=32`, and `>=64` cases; loads/stores perform low/high memory transfers for `BPF_DW`; branches compare high halves before low halves for 64-bit semantics. Calls marshal BPF arguments to IA32 ABI registers/stack, call either helper base or kfunc target, and store return values back into BPF R0 scratch slots.

## State and persistence
State is limited compared with x86-64: `addrs[]`, `jit_context.cleanup_addr`, `prog->bpf_func`, `prog->jited`, and `prog->jited_len`. Tail-call count is stored in the JIT scratch stack area as a synthetic BPF register. There is no packed RW/executable alias state, trampoline state, exception-table population, or private stack persistence in this file.

## Dependencies and integration points
The backend depends on BPF core program metadata, BTF kfunc models, i386 calling convention behavior, x86 direct machine-code encoding, retpoline thunk `__x86_indirect_thunk_edx` when configured, and generic BPF JIT allocation/RO locking. It includes x86 mitigation and cacheflush headers but is far less integrated with modern x86-64 CFI/trampoline machinery.

## Risks and edge cases
Main risks are split-register semantic bugs, missing high-half zeroing when verifier zext expectations are wrong, branch offset instability, unsupported opcode fallback, and ABI mistakes in helper/kfunc call marshalling. Tail calls depend on `PROLOGUE_SIZE` staying exactly 35 bytes. Memory operations ignore high address halves because IA32 addresses are 32-bit, which is expected but must align with verifier constraints. Unsupported atomics and 64-bit div/mod should be covered by verifier or fallback behavior.

## Test signals
Run BPF selftests on 32-bit x86 configurations with JIT enabled, especially ALU32/ALU64, zext, endian conversion, shifts around 31/32/63/64, helper calls, kfunc calls, branches, memory loads/stores, and tail calls. Logs with `*** NOT YET: opcode`, `bpf_jit: fatal error`, `unsupported BPF func`, or `cond_jmp gen bug` indicate either verifier/JIT contract drift or encoder defects.
