# sources/distributed-fs/ceph-client/arch/parisc/net/Makefile

Purpose: selects PA-RISC BPF JIT objects for the kernel build.

Important build rules: `obj-$(CONFIG_BPF_JIT) += bpf_jit_core.o` includes shared PA-RISC JIT support when BPF JIT is enabled. A `CONFIG_64BIT` conditional adds `bpf_jit_comp64.o` for 64-bit kernels and `bpf_jit_comp32.o` otherwise.

Control flow: build-system only. Kbuild evaluates the config symbols and appends the architecture-specific JIT compiler object matching word size.

State and persistence: no runtime state in the Makefile. Its lasting effect is which JIT implementation is linked into the kernel image.

Dependencies and integration: integrates with the generic BPF JIT framework and PA-RISC architecture build. The selected compiler object must match the ABI, instruction encoding, register width, and calling convention for the target kernel bitness.

Risks: selecting the wrong compiler object would produce invalid code generation or link failures. Building compiler objects without `bpf_jit_core.o` would omit shared support. Missing `CONFIG_BPF_JIT` gating could include unused code in kernels that disable JIT.

Test signals: build PA-RISC with `CONFIG_BPF_JIT` on and off, for both 32-bit and 64-bit configurations; run BPF JIT selftests or verifier/JIT smoke tests; inspect linked objects to ensure only the matching compiler is included.
