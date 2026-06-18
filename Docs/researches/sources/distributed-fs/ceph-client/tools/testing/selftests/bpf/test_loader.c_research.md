# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_loader.c

## Research

`test_loader.c` is the generic annotation-driven BPF object test runner used by many selftests. It opens generated skeleton ELF bytes, reads BTF declaration tags on each BPF program, derives expected load/runtime behavior, and runs privileged and optional unprivileged subtests.

Important types are `struct test_spec` and `struct test_subspec`, which hold program names, expected verifier messages, translated/JIT disassembly patterns, stdout/stderr stream patterns, return values, capability requirements, custom BTF path, log level, program flags, architecture/load-mode masks, and execution controls. `compile_regex()`, `__push_msg()`, `collect_decl_tags()`, and `parse_test_spec()` turn `bpf_misc.h` decl-tag comments into structured expectations. `validate_msgs()` checks ordered positive patterns, negative patterns scoped between positives, and next-line expectations.

Control flow begins in `test_loader__run_subtests()`, which calls `process_subtest()`. The loader opens the object from memory, parses specs for each program, skips auxiliary programs as top-level cases, and calls `run_subtest()` for privileged and unprivileged variants. `run_subtest()` reopens the object, autoloads only the target plus needed auxiliary programs, configures logs/flags/maps, optionally drops capabilities, loads the object, validates verifier logs, restores capabilities for info reads, optionally validates xlated/JIT text, attaches struct_ops maps for executable tests, runs `bpf_prog_test_run_opts()`, and validates BPF stdout/stderr streams.

State is process-local log buffers, compiled regex arrays, temporary libbpf objects, BPF FDs, links, capability masks, and cached unprivileged sysctl state. Dependencies include libbpf, BTF, selftest assertion helpers, capability helpers, unprivileged sysctl helpers, disassembly helpers, and JIT availability for JIT text checks.

Risks include strict coupling to decl-tag syntax, regex length limits, arch-specific disassembly differences, capability restoration bugs, and environment-dependent unprivileged/JIT support. Test signals are named subtests with clear failures for unexpected load result, missing verifier/disassembly/stdout/stderr patterns, wrong retval, unsupported JIT disassembly, or failed struct_ops attachment.
