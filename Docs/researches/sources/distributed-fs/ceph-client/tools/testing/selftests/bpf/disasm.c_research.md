# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.c

Purpose: BPF instruction disassembler shared with selftests, formatting eBPF bytecode into human-readable strings.

Important APIs and functions: `func_id_name()` maps helper ids; `print_bpf_insn()` formats one instruction using `struct bpf_insn_cbs` callbacks. Static tables map classes, ALU ops, signed div/mod, movsx, atomic ops, load/store widths, signed loads, and jumps. Special handling covers helper/pseudo/kfunc calls, ldimm64, address-space casts, percpu address moves, atomics, may_goto, gotox, and endian/bswap.

Control flow: `print_bpf_insn()` switches by BPF instruction class and submode, formats the corresponding syntax, invokes callbacks for helper names and immediate names, and masks pointer immediates unless allowed.

State and persistence: static string tables only.

Dependencies and integration points: uses Linux BPF UAPI, kernel-style stringify/build macros, and callback definitions from `disasm.h`. Kept close to kernel verifier/JIT disassembler behavior.

Risks: instruction set additions require updates; malformed/unknown encodings print `BUG_*`; pointer leak masking must be used correctly by callers; formatting changes can break string-comparison tests.

Test signals: tests can compare expected instruction strings for generated BPF programs, including new opcodes and pseudo-call handling.
