# sources/distributed-fs/ceph-client/net/nsh/nsh.c

## Purpose

This file implements Linux Network Service Header packet manipulation and GSO support. It exports `nsh_push()` and `nsh_pop()` for consumers such as Open vSwitch, and registers a packet offload handler for `ETH_P_NSH` segmentation.

## Important APIs, Types, and Functions

`nsh_push()` prepends an NSH header to an skb, derives the old payload protocol as a tunnel protocol (`TUN_P_ETHERNET` or `tun_p_from_eth_p()`), copies the requested header, fills `nh->np`, updates checksum, resets skb protocol and headers to `ETH_P_NSH`, and clears MAC length. `nsh_pop()` validates and pulls an NSH header, maps `nh->np` back to an Ethernet protocol with `tun_p_to_eth_p()`, updates checksum/header offsets, and restores `skb->protocol`.

`nsh_gso_segment()` temporarily removes the NSH header, segments the inner packet with `skb_mac_gso_segment()`, then pushes outer headers back onto each segment. Module init/exit register and unregister `nsh_packet_offload`.

## Control Flow

Push/pop are synchronous skb transforms used by callers in packet action paths. GSO flow starts when the stack segments an `ETH_P_NSH` skb. The code validates base and full NSH length, maps the next protocol, pulls the NSH header, sets inner MAC/protocol state for segmentation, and either unwinds on error or restores outer NSH framing on each generated segment.

## State and Persistence

Runtime state is limited to the registered `packet_offload` descriptor. Packet state changes are carried in skb headers, protocol fields, checksum state, and header offsets. No durable storage exists.

## Dependencies and Integration Points

The file depends on `net/nsh.h`, skb GSO helpers, tunnel protocol mapping helpers, and packet offload registration. Open vSwitch action execution uses the exported push/pop helpers for `OVS_ACTION_ATTR_PUSH_NSH` and `OVS_ACTION_ATTR_POP_NSH`.

## Risks and Edge Cases

Header length validation is essential: a header shorter than `NSH_BASE_HDR_LEN` returns `-EINVAL`, while insufficient linear data returns `-ENOMEM`. Unsupported inner protocol returns `-EAFNOSUPPORT`. GSO unwind must restore protocol, header offsets, and MAC length correctly to avoid corrupting the original skb after segmentation failure.

## Test Signals

Tests should cover push/pop of Ethernet and L3 payloads, unsupported protocols, malformed length, non-linear skb pull failures, checksum correctness, GSO success for inner IPv4/IPv6/TCP traffic, and GSO error unwind.
