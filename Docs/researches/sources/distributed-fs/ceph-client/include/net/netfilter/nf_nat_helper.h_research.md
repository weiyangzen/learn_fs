# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_helper.h

Purpose: Exposes helper routines for NAT-aware application protocol helpers that must rewrite payloads and coordinate expected related connections.

Important APIs/types/functions: `__nf_nat_mangle_tcp_packet` is the base TCP payload mangle primitive with optional sequence adjustment; `nf_nat_mangle_tcp_packet` wraps it with adjustment enabled. UDP payload rewriting is provided by `nf_nat_mangle_udp_packet`. Related-connection setup is handled by `nf_nat_follow_master`, and port selection for expectations by `nf_nat_exp_find_port`.

Control flow: A conntrack helper identifies protocol control payload offsets, invokes the TCP or UDP mangle routine with replacement bytes, and sequence/length adjustments are applied when needed. Expected conntracks inherit NAT from the master via `nf_nat_follow_master`.

State and persistence: State lives in conntrack, expectations, and sequence-adjust extension data. This header stores no state itself.

Dependencies/integration: Depends on skbuff mutability, conntrack, expectations, NAT extension state, and helper-specific parsers such as FTP, SIP, or PPTP.

Risks/test signals: Payload rewrites can fail on non-linear skbs, invalid offsets, insufficient tailroom, or sequence adjustment mistakes. Test helpers with TCP segmentation, UDP checksum changes, expectation port conflicts, NAT follow-master behavior, and malformed control payloads.
