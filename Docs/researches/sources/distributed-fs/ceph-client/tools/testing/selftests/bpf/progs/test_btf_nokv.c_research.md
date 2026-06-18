<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c

Purpose: BTF map test intentionally lacking explicit key/value typing in the legacy/no-kv style.

Important APIs/types/functions: Defines `btf_map`, helper functions, and dummy tracepoint program.

Control flow: Program provides load coverage while userspace validates how missing key/value BTF is represented.

State and persistence: Persistent state is the map definition and BTF metadata.

Dependencies and integration: Depends on libbpf compatibility with no-kv map declarations.

Risks: Loader behavior for old map syntax can regress.

Test signals: Tests inspect map metadata and successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c -->
