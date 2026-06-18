<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c

Purpose: BTF map test using new-style key/value declarations.

Important APIs/types/functions: Defines `ipv_counts`, BTF map `btf_map`, long-named helper functions, and dummy tracepoint program.

Control flow: Tracepoint calls helpers so symbols/BTF are preserved while map key/value BTF is checked.

State and persistence: Persistent state is `btf_map` and BTF metadata.

Dependencies and integration: Depends on BTF map key/value inference.

Risks: Long function names and map BTF layout must remain stable.

Test signals: Tests load and inspect BTF map metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c -->
