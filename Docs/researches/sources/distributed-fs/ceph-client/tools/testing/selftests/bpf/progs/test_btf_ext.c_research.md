<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c

Purpose: Minimal BTF.ext function/line info test for XDP with a global function.

Important APIs/types/functions: Defines `f0` XDP program and `global_func`.

Control flow: XDP program calls the global function or exposes it for BTF.ext metadata validation.

State and persistence: No maps; state is emitted BTF.ext records.

Dependencies and integration: Depends on compiler BTF.ext generation and libbpf load.

Risks: Missing line/function info can break introspection tests.

Test signals: Tests load object and inspect BTF.ext records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c -->
