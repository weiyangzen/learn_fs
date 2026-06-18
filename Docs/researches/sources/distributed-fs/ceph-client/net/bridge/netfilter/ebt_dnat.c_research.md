# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_dnat.c

## Purpose
Implements the legacy ebtables `dnat` target for destination MAC address rewriting in bridge nat and broute hooks.

## Important APIs, Types, And Functions
Key functions are `ebt_dnat_tg`, `ebt_dnat_tg_check`, and `xt_target ebt_dnat_tg_reg`, using `struct ebt_nat_info`.

## Control Flow
The target ensures the Ethernet header is writable, copies the configured MAC to `h_dest`, updates `skb->pkt_type` for broadcast, multicast, host, or otherhost semantics depending on hook and destination device, and returns the configured verdict. Checkentry validates allowed table/hook combinations (`nat` prerouting/local-out or `broute` brouting), target validity, and base-chain `RETURN` rules.

## State And Persistence Behavior
State mutation is limited to the current skb Ethernet destination and packet type. Rule data is immutable and there is no persistence.

## Dependencies And Integration Points
Depends on bridge private helpers for bridge-port lookup, netfilter bridge hook numbers, ebtables nat UAPI, and xtables target registration.

## Risks And Test Signals
Risks include writable-header failures, packet-type misclassification, and incorrect table/hook admission. Tests should cover unicast to bridge MAC, otherhost, multicast, broadcast, broute, local-out, invalid hooks, and malformed/cloned skb writability.
