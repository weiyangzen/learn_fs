<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c

Purpose: Tests build-id stack collection from normal and sleepable uprobe.multi attachments.

Important APIs/types/functions: Defines local `bpf_stack_build_id` structs and `uprobe_nofault`/`uprobe_sleepable`.

Control flow: Uprobe handlers collect or validate build-id stack data in different faulting/sleepable modes.

State and persistence: State is result globals/stack buffers in BSS.

Dependencies and integration: Depends on uprobe.multi section syntax and build-id stack helper behavior.

Risks: Sleepable versus nofault user memory behavior can diverge.

Test signals: Tests attach to `./uprobe_multi:uprobe` and inspect build-id results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c -->
