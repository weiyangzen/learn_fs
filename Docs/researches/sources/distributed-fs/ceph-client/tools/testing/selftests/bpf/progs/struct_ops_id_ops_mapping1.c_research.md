<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c

Purpose: One half of a pair testing stable id-to-ops mapping for `bpf_testmod_multi_st_ops`.

Important APIs/types/functions: Defines one struct_ops callback, a tp_btf `sys_enter` verifier, syscall verifier, a linked map, and an error counter.

Control flow: Verifier programs call the association kfunc and compare returned magic against the callback selected by the linked ops id.

State and persistence: Globals persist test pid and error count; map link holds ops identity.

Dependencies and integration: Depends on bpf_testmod multi ops ids and kfunc dispatch.

Risks: Ops-id mapping collisions or ordering changes can make the wrong callback run.

Test signals: Run with mapping2 to validate independent objects produce correct per-id behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c -->
