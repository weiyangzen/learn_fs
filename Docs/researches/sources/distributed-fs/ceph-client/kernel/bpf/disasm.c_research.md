# sources/distributed-fs/ceph-client/kernel/bpf/disasm.c

## Purpose
`disasm.c` prints human-readable eBPF instructions for verifier logs, debugging, and userspace/shared disassembly contexts. It maps BPF opcode classes, ALU/jump operations, load/store sizes, helper ids, pseudo calls, kfunc calls, atomic operations, and newer special instruction encodings into stable textual output.

## Important APIs, types, and functions
The public entry points are `func_id_name()` and `print_bpf_insn()`. Static helpers include `__func_get_name()` for helper, pseudo-call, and kfunc call names; `__func_imm_name()` for ldimm64 rendering; `print_bpf_end_insn()` and `print_bpf_bswap_insn()` for endian/byteswap operations; and recognizers for signed div/mod, movsx, address-space casts, and per-CPU address moves. The file exports `bpf_class_string` and `bpf_alu_string` tables declared in `disasm.h`.

## Control flow
`print_bpf_insn()` computes the instruction class and dispatches by class. ALU/ALU64 handles endian conversion, negation, address-space cast, per-CPU address pseudo-move, register-source operations, immediate operations, signed division/modulo spelling, and sign-extending moves. `BPF_STX` handles plain stores and all supported atomic forms, including fetch variants, cmpxchg, xchg, acquire load, and release store. `BPF_ST` handles immediate stores and internal nospec. `BPF_LDX` validates normal or sign-extending memory loads. `BPF_LD` prints ABS/IND packet loads and ldimm64, masking map pointers when pointer leaks are not allowed. Jump classes print helper/kfunc/pseudo calls, gotos, gotox, may_goto, exit, and conditional jumps with 32-bit or 64-bit register names.

## State and persistence behavior
The file is stateless apart from constant string tables. It never mutates BPF programs or global state; all output goes through the callback supplied in `struct bpf_insn_cbs`. Pointer secrecy is controlled per call by the `allow_ptr_leaks` argument.

## Dependencies and integration points
The disassembler depends on UAPI/internal BPF opcode definitions, `__BPF_FUNC_MAPPER`, stringification, and callback hooks from `disasm.h`. It is used by verifier/logging paths and other components that need a formatted instruction without embedding formatting logic.

## Risks and test signals
Risks are stale opcode coverage, unsafe immediate formatting, pointer leaks for map ldimm64 instructions, and misleading output for internal pseudo encodings. Tests should format representative instructions for every class, signed div/mod, movsx widths, addr-space cast, per-CPU move, all atomics, ldabs/ldind, ldimm64 with and without pointer leak permission, helper call name fallback, pseudo call offsets, kfunc calls, may_goto, gotox, and invalid class/mode fallbacks.
