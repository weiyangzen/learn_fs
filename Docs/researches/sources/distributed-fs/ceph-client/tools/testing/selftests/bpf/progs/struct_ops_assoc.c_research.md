<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c

Purpose: Tests association between multiple `bpf_testmod_multi_st_ops` struct_ops maps and kfunc dispatch from syscall and tracepoint contexts.

Important APIs/types/functions: Defines two `.struct_ops.link` maps, `test_1_a`/`test_1_b`, syscall programs, tp_btf `sys_enter` programs, magic return globals, and error counters.

Control flow: Each struct_ops callback returns its map-specific magic. The syscall and tracepoint programs call `bpf_kfunc_multi_st_ops_test_1_assoc` and compare the result against the map they are associated with.

State and persistence: Persistent state is limited to global `test_pid`, `test_err_a`, and `test_err_b`; struct_ops maps are linked objects.

Dependencies and integration: Integrates with `bpf_testmod` multi struct_ops and its kfunc association machinery.

Risks: Wrong map-to-program association, pid filtering mistakes, or kfunc dispatch returning the other map magic would indicate regression.

Test signals: User tests load both maps, trigger syscall/tracepoint paths for `test_pid`, and expect zero error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c -->
