# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_32.c

Purpose: compiles classic socket BPF filters into SPARC32 machine code.

Important APIs/functions: main entry points are `bpf_jit_compile()` and `bpf_jit_free()`. The file defines SPARC instruction encoders, branch helpers, load/store macros, ALU emitters, skb field loaders, and flags `SEEN_DATAREF`, `SEEN_XREG`, and `SEEN_MEM` that drive prologue/epilogue generation.

Control flow: compilation is multi-pass. An initial rough address table estimates every BPF instruction, then up to 10 passes emit code into a temporary buffer, update instruction end offsets, and converge on a stable length. Once stable, executable memory is allocated and the final pass copies instructions into it. The generated prologue allocates stack memory for BPF scratch, clears X/A when needed to avoid leaks, preloads skb head length/data, and saves `%o7`. Each classic BPF opcode emits SPARC ALU, branch, memory, ancillary load, or helper-call sequences. Returns jump to a cleanup epilogue when needed.

State and persistence: per-compile state includes `addrs`, emitted image, seen flags, cleanup address, and `pc_ret0` optimization. A successful compile stores `fp->bpf_func` and `fp->jited`; free releases execmem.

Dependencies and integration points: depends on classic BPF filter encoding, `bpf_anc_helper()`, skb layout, `execmem_alloc/free`, `bpf_jit_dump()`, `bpf_needs_clear_a()`, SPARC32 helper stubs, and network filter JIT hooks.

Risks: branch offset convergence, delay slots, `%y` register latency for division, and helper-call link handling are all subtle. The code must avoid kernel data leakage by clearing registers and returning zero on invalid loads.

Test signals: classic BPF JIT selftests, tcpdump/socket filters with ALU/jump/memory/ancillary loads, division by zero, out-of-range packet access, JIT dump validation, and execmem free on program teardown.
