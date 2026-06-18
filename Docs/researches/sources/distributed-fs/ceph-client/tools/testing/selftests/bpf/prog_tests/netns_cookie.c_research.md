<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c

Purpose: tests BPF netns cookie retrieval and consistency across sockets/network namespaces.

Important APIs and functions: the harness loads the `netns_cookie` fixture, creates or enters network namespaces, triggers socket operations, and compares BPF-observed cookies against expected userspace/kernel values.

Control flow: setup netns and skeleton, run traffic or socket operations in default and test namespaces, read BSS/map cookie fields, assert identity/difference rules, cleanup namespaces and fds.

State and persistence: netns objects, sockets, and BPF map/BSS cookie records are temporary.

Dependencies and integration: depends on network namespace support, network helpers, generated skeleton, and `bpf_get_netns_cookie()` semantics.

Risks and test signals: stable equal cookies within the same namespace and different cookies across namespaces are signals. Risks include namespace cleanup failures and helper availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c -->
