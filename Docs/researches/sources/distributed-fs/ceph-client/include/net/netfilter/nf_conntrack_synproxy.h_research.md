<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h

## Purpose
`nf_conntrack_synproxy.h` defines the optional conntrack extension for SYNPROXY state and helper logic to copy synproxy/seqadj requirements from templates.

## Important APIs, types, and functions
It defines `struct nf_conn_synproxy`, find/add helpers, and `nf_ct_add_synproxy`.

## Control flow
When a template conntrack has SYNPROXY enabled, new conntracks allocate both SEQADJ and SYNPROXY extensions so SYN cookie sequence/timestamp offsets can be tracked.

## State and persistence
State is per-conntrack initial sequence number, initial timestamp, and timestamp offset. Disabled builds return NULL/true stubs.

## Dependencies and integration points
It depends on seqadj, conntrack extensions, netns generic, and CONFIG_NETFILTER_SYNPROXY. It integrates SYNPROXY rule handling with conntrack TCP adjustment.

## Risks and test signals
Risks include partial allocation where seqadj succeeds and synproxy fails, disabled-build assumptions, timestamp offset mistakes, and template detection. Tests should cover template-to-flow allocation, allocation failure, SYN/SYNACK/ACK proxy handshake, and CONFIG off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h` completely for this pass (48 lines, 1005 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h -->
