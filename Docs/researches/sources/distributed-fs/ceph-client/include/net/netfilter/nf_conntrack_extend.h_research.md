<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h

## Purpose
`nf_conntrack_extend.h` defines the optional extension area layout for conntrack entries and the extension IDs used by helpers, NAT, seqadj, acct, events, timestamps, timeouts, labels, synproxy, and TC act_ct.

## Important APIs, types, and functions
It defines `enum nf_ct_ext_id`, `struct nf_ct_ext`, existence/find helpers, `nf_ct_ext_add`, global `nf_conntrack_ext_genid`, and `nf_ct_ext_bump_genid`.

## Control flow
Code checks whether an extension offset is present, finds it directly when generation is current, or uses the slower finder if generation changed. New extensions are appended to the aligned data area; genid invalidation prevents unsafe use of stale unconfirmed extensions after extension layout changes.

## State and persistence
State is per-conntrack extension offsets/length/generation and global extension generation ID. Extension payloads persist for the conntrack lifetime.

## Dependencies and integration points
It depends on conntrack, slab allocation, and all CONFIG-dependent extension users. It integrates optional conntrack features without bloating base `struct nf_conn`.

## Risks and test signals
Risks include extension ID order/layout changes, alignment and length overflow, using extension pointers after reallocation/genid bump, and CONFIG matrix gaps. Tests should add multiple extensions, bump genid, use unconfirmed and confirmed entries, and build with feature combinations.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h` completely for this pass (79 lines, 1797 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h -->
