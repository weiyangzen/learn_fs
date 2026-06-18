<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c

## Purpose
Maintains and applies TCP sequence-number adjustments for conntrack helpers/NAT modules that change payload length. It rewrites sequence numbers, ACK numbers, and SACK blocks while updating TCP checksums.

## Important APIs, Types, and Functions
Exports `nf_ct_seqadj_init()`, `nf_ct_seqadj_set()`, `nf_ct_tcp_seqadj_set()`, `nf_ct_seq_adjust()`, and `nf_ct_seq_offset()`. Internal helpers are `nf_ct_sack_adjust()` and `nf_ct_sack_block_adjust()`. State lives in `struct nf_conn_seqadj` with per-direction `struct nf_ct_seqadj`.

## Control Flow
NAT/helper code calls init or set when payload length changes. `nf_ct_seqadj_set()` records a correction position and before/after offsets under `ct->lock`. `nf_ct_seq_adjust()` makes the TCP header writable, adjusts sequence by this direction's offset, adjusts ACK by the opposite direction's offset, and rewrites any SACK block sequence ranges. `nf_ct_seq_offset()` returns the offset relevant to a given sequence.

## State and Persistence
Per-direction offsets and correction positions persist in the conntrack extension for the connection lifetime. `IPS_SEQ_ADJUST_BIT` signals confirmation/helper paths to invoke adjustment. No global state is kept.

## Dependencies and Integration Points
Depends on conntrack extension storage, TCP header layout, checksum replacement helpers, TCP option parsing, and callers in helpers/NAT code plus `nf_confirm()` and `nf_ct_helper()`.

## Risks
Missing `nfct_seqadj_ext_add()` setup triggers a warning and skips updating, which can corrupt application data flows after NAT mangling. SACK parsing must reject partial options and keep checksum updates consistent. Locking spans packet mutation, so all callers must use writable skbs.

## Test Signals
Test FTP/SIP NAT payload expansion/shrink, sequence and ACK rewrite in both directions, SACK block rewrite, malformed TCP options, zero offset no-op, missing extension warning, and checksum validation after mangling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c -->
