# sources/distributed-fs/ceph-client/arch/sparc/net/Makefile

Purpose: wires SPARC architecture-specific BPF JIT objects into kbuild.

Important APIs/targets: builds `bpf_jit_comp_$(BITS).o` when `CONFIG_BPF_JIT` is enabled. On 32-bit builds it additionally builds `bpf_jit_asm_32.o`.

Control flow: kbuild expands `$(BITS)` to choose `bpf_jit_comp_32.o` or `bpf_jit_comp_64.o`. The 32-bit helper assembly is required only for classic BPF skb load stubs.

State and persistence: no runtime state; it affects build graph composition.

Dependencies and integration points: integrates with the kernel networking/filter subsystem and architecture build variables. It assumes the 64-bit compiler is self-contained and the 32-bit compiler depends on external assembly stubs.

Risks: wrong `BITS` selection or missing 32-bit stub object breaks BPF JIT linkage. Accidentally building assembly on 64-bit would duplicate nonexistent symbols.

Test signals: build sparc32 and sparc64 with `CONFIG_BPF_JIT=y`, and verify generated objects export the expected BPF JIT entry points without unresolved helper symbols.
