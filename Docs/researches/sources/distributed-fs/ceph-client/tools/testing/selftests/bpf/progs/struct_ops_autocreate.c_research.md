<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c

Purpose: Exercises libbpf auto-create and optional handling for module struct_ops maps with compatible and incompatible local type flavors.

Important APIs/types/functions: Defines `test_1`, `test_2`, v1/v2 local `bpf_testmod_ops` shapes, two required `.struct_ops.link` maps, and optional `?.struct_ops` maps.

Control flow: Callbacks are simple; the load path is the behavior under test, especially whether libbpf creates/link maps and skips optional ones correctly.

State and persistence: Global `test_1_result` records callback execution; map existence/link state is managed by libbpf.

Dependencies and integration: Depends on struct_ops section naming, BTF type compatibility, and optional section semantics.

Risks: Incompatible callback fields or optional map handling can cause unexpected load failures.

Test signals: Expected signals are successful skeleton open/load and callback setting `test_1_result=42` where invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c -->
