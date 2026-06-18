# sources/distributed-fs/ceph-client/kernel/bpf/disasm.h

## Purpose
`disasm.h` defines the callback interface and exported declarations for the BPF instruction disassembler implemented in `disasm.c`. It is deliberately small so both kernel and non-kernel builds can share the same formatting API.

## Important APIs, types, and functions
The header declares the exported opcode string tables `bpf_alu_string` and `bpf_class_string`, `func_id_name(int id)`, and `print_bpf_insn()`. It defines `bpf_insn_print_t` as a printf-style output callback, `bpf_insn_revmap_call_t` as an optional callback for resolving call instructions, and `bpf_insn_print_imm_t` as an optional callback for formatting 64-bit immediates. `struct bpf_insn_cbs` bundles those callbacks with caller-owned `private_data`.

## Control flow
There is no executable control flow in the header. Its contract is that callers provide at least a print callback and optionally provide call/immediate resolvers. `print_bpf_insn()` consumes this callback bundle, one `struct bpf_insn`, and an `allow_ptr_leaks` policy bit.

## State and persistence behavior
The header owns no state. The only persistent values are external const string tables defined in `disasm.c`. Callback private data lifetime remains the caller's responsibility.

## Dependencies and integration points
The header includes `linux/bpf.h`, `linux/kernel.h`, and `linux/stringify.h`; for non-kernel builds it also includes stdio/string headers. It is the integration point for verifier log printers, debugging code, and any userspace-compatible build that reuses the kernel disassembler source.

## Risks and test signals
The main risk is callback contract misuse: `cb_print` must match the printf annotation, optional callbacks must tolerate the instruction forms they are asked to resolve, and private data must outlive the print call. Compile tests should cover kernel and non-kernel include paths. API tests should verify custom call and immediate callbacks are honored and that callers can pass null optional callbacks without crashing.
