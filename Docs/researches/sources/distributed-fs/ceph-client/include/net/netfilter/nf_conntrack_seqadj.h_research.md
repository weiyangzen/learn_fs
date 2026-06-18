<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h

## Purpose
`nf_conntrack_seqadj.h` defines TCP sequence-number adjustment state and APIs used by NAT/helpers that modify payload length.

## Important APIs, types, and functions
It defines `struct nf_ct_seqadj`, `struct nf_conn_seqadj`, find/add helpers, `nf_ct_seqadj_init`, `nf_ct_seqadj_set`, `nf_ct_tcp_seqadj_set`, `nf_ct_seq_adjust`, and `nf_ct_seq_offset`.

## Control flow
When payload changes alter TCP sequence space, helpers initialize or update per-direction correction positions and offsets. Later packet paths adjust TCP sequence/ack numbers and checksums according to direction and sequence position.

## State and persistence
State is per-conntrack SEQADJ extension with two direction entries storing last correction position and before/after offsets.

## Dependencies and integration points
It depends on conntrack extensions and TCP skb manipulation in implementation. It integrates NAT helpers and synproxy with TCP stream correctness.

## Risks and test signals
Risks include off-by-one sequence position handling, signed offset overflow, missing extension allocation, checksum update mistakes, and retransmission interactions. Tests should cover payload expand/shrink, both directions, retransmits around correction point, checksum validation, and NAT helper flows.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h` completely for this pass (45 lines, 1400 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h -->
