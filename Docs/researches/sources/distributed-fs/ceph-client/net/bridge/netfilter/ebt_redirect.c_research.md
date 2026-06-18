# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_redirect.c

## Purpose
Implements the legacy ebtables `redirect` target, rewriting destination MAC addresses so frames are delivered locally to either the bridge device or incoming port.

## Important APIs, Types, And Functions
Important functions are `ebt_redirect_tg`, `ebt_redirect_tg_check`, and `xt_target ebt_redirect_tg_reg`, using `struct ebt_redirect_info`.

## Control Flow
Runtime ensures the Ethernet header is writable, writes the destination MAC to the bridge device address in nat prerouting or to the incoming device address in brouting, sets `skb->pkt_type` to `PACKET_HOST`, and returns the configured verdict. Validation restricts use to nat prerouting or broute brouting hooks, validates verdicts, and forbids base-chain `RETURN`.

## State And Persistence Behavior
Only the current skb destination MAC and packet type are mutated. There is no stored state beyond rule data.

## Dependencies And Integration Points
Depends on bridge-port lookup under RCU, ebtables redirect UAPI, netfilter bridge hooks, and xtables registration. It interacts with broute and nat table traversal.

## Risks And Test Signals
Risks include wrong local MAC selection, writable-header failure, and table/hook validation gaps. Tests should cover nat prerouting redirect, brouting redirect, invalid hooks/tables, base-chain return rejection, and cloned/truncated skb behavior.
