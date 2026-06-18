<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c

Purpose: TC ingress test for syncookie helpers and BTF socket tuple handling.

Important APIs/types/functions: Defines local sockaddr structs, helpers `test_syncookie_helper`, `handle_ip_tcp`, and tc `cls_ingress`.

Control flow: Program parses IPv4/IPv6 TCP packets, fills socket addresses, and calls syncookie/check helpers.

State and persistence: No persistent maps; return codes and helper results are observed by packet tests.

Dependencies and integration: Depends on tc direct packet access, TCP/IP header parsing, and syncookie BPF helpers.

Risks: Malformed packet bounds and address-family handling are risks.

Test signals: Tests send crafted packets and check tc verdict/helper outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c -->
