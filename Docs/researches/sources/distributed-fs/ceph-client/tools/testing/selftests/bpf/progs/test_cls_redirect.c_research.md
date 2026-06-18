<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c

Purpose: Large Cloudflare TC classifier implementing packet classification and GRE/GUE redirect logic for selftests.

Important APIs/types/functions: Defines metrics map, packet buffer abstraction, IPv4/IPv6/ICMP/TCP/UDP parsers, checksum helpers, classification functions, forwarding helpers, and `cls_redirect`.

Control flow: `cls_redirect` parses L3/L4, rejects malformed/fragmented/unwanted traffic, accepts local SYN/established/ICMP cases, or encapsulates and redirects to the next hop while updating metrics.

State and persistence: Persistent state is `metrics_map`; packet data is modified in-place for encapsulation/redirect.

Dependencies and integration: Depends on tc skb helpers, direct packet access, checksum helpers, endian helpers, and `test_cls_redirect.h` GRE/GUE headers.

Risks: Verifier-sensitive pointer alignment, non-linear SKB reads, checksum correctness, MTU/encap buffer limits, and redirect-loop detection are risks.

Test signals: Packet-driven tests validate metrics increments, verdicts, encapsulated headers, and malformed-packet drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c -->
