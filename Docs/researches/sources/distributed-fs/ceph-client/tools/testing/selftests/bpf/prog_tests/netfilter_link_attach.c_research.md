<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c

Purpose: verifies BPF netfilter program attachment through bpf links, including hook selection and link cleanup.

Important APIs and functions: the harness loads the netfilter skeleton, attaches programs to configured netfilter hooks through link APIs, generates local packet traffic, checks BSS counters or verdict effects, and destroys links.

Control flow: open/load, attach one or more hook programs, trigger traffic, assert hit counters/verdict behavior, close links/skeleton. Negative cases exercise invalid attach combinations where present.

State and persistence: BPF netfilter links are persistent kernel objects while fds are open and are destroyed with skeleton/link cleanup. Packet counters are transient.

Dependencies and integration: depends on kernel BPF netfilter link support, network helpers, and `netfilter_link_attach.skel.h`.

Risks and test signals: hook hit counters and successful link attach/detach are signals. Risks include kernel config differences, netfilter hook ordering, and privilege requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c -->
