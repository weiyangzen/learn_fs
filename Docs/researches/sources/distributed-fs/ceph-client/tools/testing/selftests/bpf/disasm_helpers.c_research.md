# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.c

Purpose: compact helper to disassemble one BPF instruction into a normalized string suitable for tests.

Important APIs and functions: `disasm_insn(insn, buf, buf_sz)` builds `bpf_insn_cbs`, calls `print_bpf_insn()`, strips the leading opcode prefix and trailing newline, simplifies call strings by removing `#id`, and advances over one or two instructions for ldimm64.

Control flow: callback `print_insn_cb()` writes into caller buffer; `print_call_cb()` prints pseudo-call offsets from `insn->off` because verifier subprog JIT rewrites `imm`.

State and persistence: only stack context and caller-provided buffer.

Dependencies and integration points: depends on `disasm.c` API and libbpf BPF definitions.

Risks: assumes disassembler prefix length of five characters; normalization can break if `print_bpf_insn()` formatting changes; buffer truncation is possible via `vsnprintf`.

Test signals: tests can iterate instructions by assigning returned pointer and compare short assembly strings.
