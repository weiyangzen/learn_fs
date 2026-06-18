<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c

Purpose: Tests detach behavior when a linked struct_ops map references a callback/subprogram that should become dangling after detach.

Important APIs/types/functions: Defines `dangling_subprog` and a `.struct_ops.link` map for `bpf_testmod_ops`.

Control flow: There is no active BPF program flow in the file; loader/link detach operations exercise lifetime handling.

State and persistence: Struct_ops link lifetime is the persistent state under test.

Dependencies and integration: Depends on bpf_testmod ops and libbpf struct_ops link detach handling.

Risks: Dangling callback references after detach can cause use-after-free or verifier/link cleanup bugs.

Test signals: A passing test detaches without kernel warnings and rejects or cleans dangling references correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c -->
