<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c

Purpose: Checks reusing the same struct_ops program in more than one linked map while preserving each map association.

Important APIs/types/functions: Defines callbacks and syscall programs for map A and B, with two `.struct_ops.link` instances using associated test callbacks.

Control flow: Syscall programs invoke the association kfunc and verify map-specific magic values, similar to `struct_ops_assoc.c` but focused on reuse behavior.

State and persistence: Globals hold error counters; linked struct_ops maps persist attachment identity.

Dependencies and integration: Uses bpf_testmod multi struct_ops and association kfunc support.

Risks: A reused program must not inherit stale association metadata from another map.

Test signals: Tests load both links and verify no map-specific error counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c -->
