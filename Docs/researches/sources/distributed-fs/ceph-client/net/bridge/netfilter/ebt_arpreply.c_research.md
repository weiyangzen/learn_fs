# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arpreply.c

## Purpose
Implements the legacy ebtables `arpreply` target, which sends synthetic ARP replies from bridge prerouting nat rules and returns a configured ebtables verdict.

## Important APIs, Types, And Functions
Core functions are `ebt_arpreply_tg`, `ebt_arpreply_tg_check`, and `xt_target ebt_arpreply_tg_reg`. It uses `arp_send` and `struct ebt_arpreply_info`.

## Control Flow
Runtime target evaluation validates the skb contains an Ethernet/IPv4 ARP request, extracts sender MAC, sender IP, and target IP, sends an ARP reply on the incoming device using the configured MAC address, and returns the configured target verdict. Checkentry restricts use to ARP ethproto, the nat table's bridge prerouting hook, non-invalid verdicts, and forbids `RETURN` from base chains.

## State And Persistence Behavior
No durable state exists. The target emits packets as side effects and uses immutable rule parameters.

## Dependencies And Integration Points
Depends on ARP helpers, bridge netfilter hook context, ebtables target validation, xtables registration, and the legacy nat table.

## Risks And Test Signals
Risks include replying to malformed ARP, using the wrong device/IP tuple, and rule verdict interactions after a reply is emitted. Tests should cover valid ARP request reply generation, non-request continuation, malformed header drop, invalid target rejection, and base-chain return rejection.
