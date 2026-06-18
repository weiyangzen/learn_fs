<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c

Purpose: end-to-end IPv6 Segment Routing local action test using End.BPF programs to manipulate SRH TLVs, flags, tags, and table lookup behavior across six namespaces.

Important APIs and functions: `setup()` creates six netns, five veth pairs, link-scope/global IPv6 addresses, SRv6 routes, `encap bpf in` route in NS2, three `seg6local action End.BPF` routes from `test_lwt_seg6local.bpf.o`, forwarding sysctls, and seg6 enablement in NS6. `cleanup()` deletes all namespaces. `test_lwt_seg6local()` starts a UDP server in NS6 and client in NS1 and sends `foobar`.

Control flow: setup topology, open NS6 for server, open NS1 for client, send UDP from `fb00::1` to `fb00::6`, read from server, compare payload, close fds/namespaces, cleanup.

State and persistence: six network namespaces, veth devices, routes, SRv6 local actions, sockets, and sysctls are temporary. Cleanup removes namespaces even after partial failure.

Dependencies and integration: depends on SRv6 kernel support, `iproute2` seg6local BPF support, network helpers, UDP helpers, and the companion BPF object.

Risks and test signals: successful receipt of exact `foobar` payload proves the SRH chain and BPF actions worked. Risks are missing SRv6 support, route setup mistakes, namespace cleanup issues, and timing/environment differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c -->
