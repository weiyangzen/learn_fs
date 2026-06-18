<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c

Purpose: table-driven cgroup/sysctl BPF verifier and runtime suite covering attach-type validation, read/write allow/deny, context field access, helper behavior, file-position changes, value reads/writes, and object-file based programs.

Important APIs/types/functions: `struct sysctl_test` describes inline instructions or `prog_file`, attach type, `/proc/sys` target, open mode, expected operation result, and optional fixup. `probe_prog_length()`, `fixup_sysctl_value()`, `load_sysctl_prog_insns()`, `load_sysctl_prog_file()`, `access_sysctl()`, `run_test_case()`, and `run_tests()` implement execution. It uses `bpf_prog_load()`, `bpf_prog_test_load()`, `bpf_prog_attach()`, `bpf_prog_detach()`, and cgroup helpers.

Control flow: `test_sysctl()` creates and joins cgroup `/foo`, then iterates the large static `tests[]` array. Each case builds `/proc/sys/<sysctl>`, loads either raw BPF instructions or a BPF object, optionally patches a `BPF_LD_IMM64` with the live sysctl value, attaches to the cgroup, reads or writes the sysctl, and compares the observed result with `LOAD_REJECT`, `ATTACH_REJECT`, `OP_EPERM`, or `SUCCESS`.

State and persistence: creates a cgroup test environment, attaches one program at a time, opens and may write selected sysctls such as `kernel/domainname`, closes BPF objects and fds per case, and cleans the cgroup environment at end. Some tests rely on default or current sysctl values.

Dependencies and integration: depends on `test_progs.h`, `cgroup_helpers.h`, raw BPF instruction macros, cgroup sysctl program type, procfs sysctls, and object files referenced by `prog_file` cases. Integrated as `test_sysctl`.

Risks: large inline instruction table is brittle to helper ABI/verifier changes. Some sysctls may be absent, read-only, or policy-restricted in unusual environments. `FIXUP_SYSCTL_VALUE` cases depend on live procfs contents and BPF instruction position. Cleanup detaches best-effort without checking detach return.

Test signals: per-case `[PASS]/[FAIL]` printing, detailed verifier log on unexpected load failure, expected errno `EPERM` for operation denial, old-value string comparisons, and final summary requiring zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c -->
