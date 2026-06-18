# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_irc.h

## Purpose
This header defines IRC conntrack helper NAT integration for DCC-style related connections.

## Important APIs, Types, and Functions
It defines `IRC_PORT` 6667, `nf_nat_irc_hook_fn`, and the RCU-published hook pointer `nf_nat_irc_hook`. The hook type receives skb, conntrack direction info, protocol offset, match offset/length, and an expectation.

## Control Flow
The IRC helper parses control traffic for embedded connection offers, creates an expectation, and calls the NAT hook when available to rewrite payload and expectation state for NAT traversal.

## State and Persistence
Only the global RCU hook pointer is declared here. Per-connection expectations and helper state live in conntrack structures elsewhere.

## Dependencies and Integration Points
It depends on netfilter, skb, and conntrack expectation APIs. It integrates the IRC helper with NAT rewriting.

## Risks
String parsing offsets must align with skb payload data; malformed or fragmented messages can cause missed expectations. NAT hook lifetime must be protected by RCU, and expectation ownership must match conntrack core rules.

## Test Signals
IRC DCC through NAT, fragmented control messages, malformed payloads, NAT disabled/enabled behavior, module unload under traffic, and checksum/sequence adjustment after payload rewrite.
