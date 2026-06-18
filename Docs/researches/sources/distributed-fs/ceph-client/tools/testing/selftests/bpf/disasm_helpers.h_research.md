# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.h

Purpose: declares the single-instruction disassembly helper.

Important APIs and functions: forward-declares `struct bpf_insn` and declares `disasm_insn(struct bpf_insn *insn, char *buf, size_t buf_sz)`.

Control flow: header only.

State and persistence: none.

Dependencies and integration points: includes stdlib for `size_t`; pairs with `disasm_helpers.c`.

Risks: caller must provide a sufficiently sized writable buffer and valid instruction stream, including the second half of ldimm64.

Test signals: compile-time interface for tests comparing normalized disassembly.
