# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_core.c

## Purpose
Shared PA-RISC eBPF JIT compilation driver. It runs sizing/convergence passes, allocates executable memory, invokes architecture-width-specific emitters, patches line info, locks the image read-only, and exposes 64-bit division helpers used by emitters.

## Important APIs, Types, And Control Flow
`build_body()` iterates BPF instructions, calls `bpf_jit_emit_insn()`, skips the second half of `BPF_LD | BPF_IMM | BPF_DW`, and records BPF-to-native offsets. `bpf_jit_needs_zext()` returns true. `bpf_int_jit_compile()` owns the compile lifecycle: honor `jit_requested`, allocate/reuse `prog->aux->jit_data`, seed rough offsets, iterate up to `NR_JIT_ITERATIONS`, compute prologue/body/epilogue sizes, allocate `bpf_jit_binary_alloc()` once size converges, emit final code, set extable storage, optionally dump/reboot for debug, lock RO, flush icache, set `prog->bpf_func`, and fill jited line info.

`hppa_div64()` and `hppa_div64_rem()` wrap generic kernel 64-bit divide helpers for generated code.

## State, Dependencies, Risks, And Tests
State is `prog->aux->jit_data` during compilation and final `prog->bpf_func`, `jited`, `jited_len`, `extable`, and jited line info after success. Dependencies include Linux BPF JIT allocation/locking APIs, verifier env, exception table sizing, and the arch-specific emitter functions. Risks include non-converging image sizes, freeing `jit_data` during subprogram extra passes, extable placement after code, incorrect prologue offset adjustment in line info, and failure cleanup for extra-pass functions. Test with BPF JIT selftests, subprogram calls requiring extra pass, exception-table programs, forced allocation failure, branch-heavy programs that stress convergence, and `bpf_jit_enable > 1` dumps.
