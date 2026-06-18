# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ctx_rewrite.c

## Purpose
Validates verifier context access rewriting by loading tiny raw BPF programs that read/write specific context fields, disassembling translated instructions, and matching them against BTF-aware patterns.

## Important APIs, types, and functions
Defines `struct test_case` with program type, expected attach type, field offset/size, and read/write patterns. Uses raw `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_ST_MEM`, `bpf_prog_load()`, `get_xlated_program()`, `disasm_insn()`, `btf__load_vmlinux_btf()`, and POSIX regex. `match_pattern()` substitutes `$ctx/$src/$dst`, resolves `type::field` and grouped offsets through BTF, ignores whitespace/semicolons, and prints side-by-side mismatches.

## Control flow and state
`test_ctx_rewrite()` compiles regexes, loads vmlinux BTF, and runs every static case. `run_one_testcase()` builds up to three minimal programs per case (read, STX write, ST write), then `match_program()` loads, retrieves translated code, disassembles into memory, and matches the pattern. State is local regex objects, vmlinux BTF, generated instruction arrays, program FDs, translated instruction buffers, and disassembly text.

## Dependencies and integration points
Depends on vmlinux BTF, verifier rewrite logic, disassembly helpers, architecture-specific instruction output, and program types such as SCHED_CLS, CGROUP_SOCK, SOCK_OPS, CGROUP_SYSCTL, and CGROUP_SOCKOPT. Integrated as a detailed verifier regression test.

## Risks and test signals
Risks are architecture-specific disassembly differences, BTF field layout drift, and pattern brittleness. Passing signal is every generated program loading and its translated instructions matching BTF-resolved expected patterns.
