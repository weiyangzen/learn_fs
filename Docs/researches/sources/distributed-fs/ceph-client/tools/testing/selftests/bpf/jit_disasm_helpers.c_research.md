# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.c

Purpose: obtains and disassembles JITed native code for loaded BPF programs when built with LLVM disassembler support.

Important APIs and functions: `get_jited_program_text(fd, text, text_sz)` fetches JITed bytes and per-function lengths with `bpf_prog_get_info_by_fd`, then disassembles each function. LLVM-backed helpers initialize targets, discover local branch labels, assign `L#` labels, and print addresses, bytes, labels, and instructions. Without LLVM support, the function returns `-EOPNOTSUPP`.

Control flow: first info query gets total JIT length and function count, buffers are allocated, second query fills bytes/lens, then each function is disassembled in two passes: label discovery and formatted output.

State and persistence: static `llvm_initialized` avoids repeated LLVM initialization. All buffers are freed per call.

Dependencies and integration points: depends on libbpf, `test_progs.h` assertions/env, LLVM C disassembler APIs under `HAVE_LLVM_SUPPORT`, and kernel JIT info exposure.

Risks: native disassembly target uses default host triple; JIT bytes may be unavailable without privileges/sysctls; local label capacity is capped at 32; output is architecture-specific.

Test signals: tests can compare or print JITed native text; missing LLVM support emits a verbose skip-style message and returns `-EOPNOTSUPP`.
