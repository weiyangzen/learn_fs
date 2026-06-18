# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_64.h

Purpose: provides SPARC64 register-number constants used by the eBPF JIT emitter.

Important APIs/types/functions: defines general, out, local, in, stack, frame, and link register numbers (`G0`-`G7`, `O0`-`O7`, `L0`-`L7`, `I0`-`I7`, `SP`, `FP`) for non-assembly code.

Control flow: no executable logic. `bpf_jit_comp_64.c` uses these constants to encode SPARC64 instructions and map BPF virtual registers.

State and persistence: no runtime state.

Dependencies and integration points: included by the 64-bit BPF JIT compiler. It is tied to the SPARC V9 register file and instruction encoding macros in the compiler.

Risks: incorrect numeric register constants corrupt emitted instructions. Since the compiler uses callee-saved locals for BPF registers, ABI mistakes can leak values across helper calls or break tail calls.

Test signals: eBPF verifier/JIT selftests covering helper calls, stack access, tail calls, and register preservation on sparc64.
