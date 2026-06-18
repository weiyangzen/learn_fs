# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.h

Purpose: declares JIT disassembly helper interface.

Important APIs and functions: `get_jited_program_text(int fd, char *text, size_t text_sz)`.

Control flow: header only.

State and persistence: no header state; implementation may initialize LLVM once.

Dependencies and integration points: includes stddef for `size_t`; used by tests that inspect native JIT output.

Risks: caller must provide adequate output buffer; function may be unsupported depending on build flags.

Test signals: compile-time declaration and runtime return code/text content.
