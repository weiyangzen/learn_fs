<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c

Purpose: Exercises `bpf_check_mtu` helper from XDP and TC contexts with normal, exceeding, negative-delta, input-length, and segmented-SKB cases.

Important APIs/types/functions: Defines global user MTU/ifindex inputs, BPF-observed MTU globals, six XDP programs and seven TC programs.

Control flow: Each program calls `bpf_check_mtu` with a different delta/input/flag setup and maps helper errno to XDP/TC verdicts.

State and persistence: Persistent state is global MTU result variables set for userspace.

Dependencies and integration: Depends on XDP/TC contexts, ETH header length assumptions, and `BPF_MTU_CHK_RET_FRAG_NEEDED`.

Risks: Data length calculation, direct-access SKB length, negative delta, and segmentation flags are risks.

Test signals: Tests set MTU/ifindex, run packets through each program, and compare verdicts plus stored MTU values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c -->
