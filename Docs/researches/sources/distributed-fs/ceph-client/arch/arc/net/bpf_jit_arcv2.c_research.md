# sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_arcv2.c

Purpose: implements the ARCv2 backend for translating eBPF operations into ARC machine instructions.

Important APIs/functions: low-level `arc_*` emitters encode ARC moves, loads/stores, ALU, shifts, branches, calls, and returns. BPF-facing functions implement `zext()`, `mov_*`, `load_r()`, `store_*`, arithmetic/bitwise/shift operations, `gen_swap()`, register usage analysis through `mask_for_used_regs()`, frame prologue/epilogue, 32/64-bit jump check/generation, and `gen_func_call()`.

Control flow: emitters support dry-run length calculation and real emission through `buf` checks. Register mapping assigns BPF register pairs to ARC register pairs, preserving ABI argument/return constraints. Memory accesses use `adjust_mem_access()` to materialize large offsets in a temporary register. 64-bit ALU is composed from 32-bit operations with carry/borrow or temporary registers. Prologue saves used callee-saved registers, optional FP, and BLINK; epilogue restores them and moves BPF return value to ARC ABI return registers. Jump generation first validates displacement ranges, then emits 32-bit compare/tst plus branch or multi-branch 64-bit comparison templates.

State and persistence: no global mutable state. Translation state is implicit in emitted buffer position, returned lengths, register mapping, usage mask, and frame size provided by the caller.

Dependencies and integration: compiled only for ARCv2 BPF JIT. Depends on `bpf_jit.h`, Linux BPF instruction semantics, ARCv2 ABI, branch displacement encoding, endian configuration, and the generic BPF JIT core that sequences passes and final code allocation.

Risks: length stability is the core safety invariant; immediate moves for relocations and function calls use fixed-size forms to avoid pass divergence. Branch displacement checks must match emitted templates. 64-bit signed/unsigned comparisons and shifts are subtle because ARC is 32-bit. External calls must marshal BPF arg5 onto the stack and move return registers correctly. Division/modulo immediate zero returns no code and relies on higher-level BPF validation semantics.

Test signals: kernel BPF selftests, JIT versus interpreter result comparison for ALU64/ALU32, signed and unsigned jumps, far/near branch boundaries, memory offsets outside S9, endian swap operations, helper calls with five arguments, prologue/epilogue register preservation, and dry-run/emitted-size assertions.
