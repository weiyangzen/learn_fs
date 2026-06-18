# sources/distributed-fs/ceph-client/samples/bpf/bpf_insn.h

Purpose: provides C macros for manually constructing `struct bpf_insn` instruction arrays.

Important APIs/types/functions: defines helpers for ALU64/ALU32 register and immediate ops, moves, 64-bit loads, map FD loads, absolute loads, memory loads/stores, atomic add, jumps, calls, exits, endian conversions, and raw instruction emission.

Control flow: preprocessor expands macros into compound literals used by loaders like `cookie_uid_helper_example.c` and `sock_example.c`.

State and persistence: no state; generated instruction arrays are compiled into userspace programs.

Dependencies and integration: depends on Linux BPF opcode/register definitions and `struct bpf_insn`. It supports old-style samples that do not compile C source to BPF bytecode.

Risks: manual instruction construction is easy to get wrong in offsets, register classes, and helper calling convention. Some macros encode assumptions about little fields in `struct bpf_insn`. Verifier diagnostics are the main safety net.

Test signals: successful `bpf_prog_load` of instruction arrays, verifier log checks, and exercising samples that use map FD rewrite macros.
