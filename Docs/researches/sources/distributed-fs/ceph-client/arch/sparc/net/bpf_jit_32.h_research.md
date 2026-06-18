# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_32.h

Purpose: defines the SPARC32 classic BPF JIT register ABI and declares assembly skb load helpers.

Important APIs/types/functions: defines register numbers for C emission and register aliases for assembly. BPF `A`, `X`, skb pointer, saved `%o7`, skb head length, data pointer, temporaries, and offset registers map to `%o0`-`%o5` and `%g1`-`%g3`. Declares helper entry arrays such as `bpf_jit_load_word`, `bpf_jit_load_half`, `bpf_jit_load_byte`, `bpf_jit_load_byte_msh`, and positive/negative-offset variants.

Control flow: no executable flow; the C compiler and assembly stubs include the same header so emitted calls and stub register use agree.

State and persistence: no state. It defines an ABI contract for generated code.

Dependencies and integration points: included by `bpf_jit_comp_32.c` and `bpf_jit_asm_32.S`; integrates with `sk_buff`, classic BPF ancillary loads, and SPARC calling conventions.

Risks: changing register assignments breaks generated code and helper stubs together. The saved `%o7` convention is required because helper calls are made without a normal windowed function prologue.

Test signals: classic BPF filters with direct packet loads, negative ancillary offsets, helper calls, and return paths should pass on sparc32 with JIT enabled.
