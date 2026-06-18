<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c

## Purpose
`xt_physdev.c` implements bridge physical-device matching for packets traversing the bridge/netfilter path. It matches bridged status and physical input/output device names.

## Important APIs, Types, and Functions
`physdev_mt()` reads bridge netfilter skb metadata through `nf_bridge_info_get()` and compares `physindev`/`physoutdev` names from `struct xt_physdev_info`. `physdev_mt_check()` validates flags and warns or rejects impossible hook usage.

## Control Flow, State, and Persistence
The match first determines whether bridge metadata exists. It can match `--physdev-is-in`, `--physdev-is-out`, `--physdev-is-bridged`, and name/mask predicates for physical input and output devices. Device-name comparisons use masks to support wildcards. No state is persisted.

## Dependencies and Integration Points
It depends on bridge netfilter metadata and x_tables hook information. It is meaningful only when bridge netfilter support attaches physical-device context to skbs.

## Risks and Test Signals
Risks include behavior when bridge netfilter is disabled, local versus forwarded bridge packets, wildcard mask mistakes, stale device names, and hooks where physout is unavailable. Tests should cover bridged and non-bridged packets, physin/physout names and masks, is-in/is-out/is-bridged flags, inversion, invalid flag combinations, and bridge netfilter off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c -->
