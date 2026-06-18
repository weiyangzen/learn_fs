# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_64.c

Purpose: implements the SPARC64 eBPF JIT compiler, translating verifier-accepted BPF instructions into SPARC V9 machine code.

Important APIs/types/functions: key types are `struct jit_ctx` and `struct sparc64_jit_data`. Public hooks are `bpf_int_jit_compile()` and `bpf_jit_needs_zext()`. Important helpers include instruction emitters, 64-bit constant synthesis (`emit_loadimm64()` and analysis helpers), `emit_compare_and_branch()`, `build_prologue()`, `build_epilogue()`, `emit_tail_call()`, `build_insn()`, `build_body()`, `jit_fill_hole()`, and `bpf_flush_icache()`.

Control flow: the compiler allocates or resumes per-program JIT data, iterates until instruction offsets converge, allocates a BPF binary image, emits a final pass, checks size convergence, flushes I-cache on Spitfire, marks the image read-only, records line info, and sets `prog->bpf_func`. `build_insn()` covers ALU32/ALU64 operations, endian swaps, jumps with optional CBCOND, helper calls, tail calls, loads/stores, stack frame use, and atomic add via CAS/CASX.

State and persistence: compile state tracks offsets, image pointer, temporary register usage, frame-pointer/call/tail-call observations, and epilogue offset. Program state is updated in `prog->bpf_func`, `jited`, `jited_len`, and temporary `prog->aux->jit_data` for subprogram extra passes.

Dependencies and integration points: depends on the eBPF verifier contract, BPF binary allocator/locking, helper-call base, BPF array tail-call layout, SPARC64 HWCAP `AV_SPARC_CBCOND`, cacheflush/TLB type, and register constants from `bpf_jit_64.h`.

Risks: constant materialization and branch displacement selection are complex. Tail-call prologue skip must match emitted prologue length. Atomic loops, stack offsets, zero-extension semantics, and helper ABI register preservation are security-sensitive.

Test signals: upstream BPF JIT selftests, verifier zext tests, tail-call chains and limit handling, subprogram JIT passes, atomics, endian conversions, helper calls, stack access, CBCOND-capable and non-CBCOND CPUs, and W^X image locking failures.
