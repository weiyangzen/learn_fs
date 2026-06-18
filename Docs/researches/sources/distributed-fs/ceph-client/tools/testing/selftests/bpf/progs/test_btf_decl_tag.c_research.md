<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c

Purpose: Tests BTF declaration tag emission and map/value typing.

Important APIs/types/functions: Defines tagged key/value types, `hashmap1`, helper `foo`, and `fentry/bpf_fentry_test1` program.

Control flow: Program and helper exercise tagged declarations so BTF.ext can be inspected by userspace.

State and persistence: Persistent state is the hash map and emitted BTF metadata.

Dependencies and integration: Depends on compiler BTF decl_tag support and fentry attachment.

Risks: Tags can be dropped by compiler/libbpf changes or misassociated with fields.

Test signals: Tests inspect BTF tags and load the fentry program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c -->
