# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323.h

## Purpose
This header defines H.323 conntrack helper state and the NAT callback table used to rewrite H.225/H.245 transport addresses and install related expectations.

## Important APIs, Types, and Functions
It defines `RAS_PORT` 1719, `Q931_PORT` 1720, and `H323_RTP_CHANNEL_MAX` 4. `struct nf_ct_h323_master` stores original/NATed signaling ports, RTP ports for media channels, and either RAS timeout or per-direction TPKT lengths. `get_h225_addr()` extracts a transport address from decoded data. `struct nfct_h323_nat_hooks` contains callbacks for setting H.245/H.225/signaling/RAS addresses and NATing RTP/RTCP, T.120, H.245, call forwarding, and Q.931. `nfct_h323_nat_hook` is RCU-published.

## Control Flow
The helper decodes H.323 control payloads using ASN.1 structures, extracts embedded transport addresses, creates expectations for related channels, and calls NAT hooks to rewrite embedded addresses/ports when NAT is active. Master state tracks negotiated ports and split TPKT handling.

## State and Persistence
Per-master H.323 helper state lives with conntrack entries. NAT hooks are global RCU state. No durable persistence is defined.

## Dependencies and Integration Points
It depends on netfilter, skb, ASN.1 H.323 type definitions, conntrack expectations, and tuple direction uapi. It integrates H.225/Q.931/RAS/H.245 parsing with NAT rewriting and RTP/RTCP expectation management.

## Risks
H.323 embeds addresses deeply in ASN.1; decoder limits, offsets, and NAT rewrite lengths must be exact. IPv4-only decoder limitations affect address support. Split TPKT handling and multiple media channels can create stale or missing expectations. RCU NAT hook lifetime must be observed.

## Test Signals
H.323 call setup through NAT, RAS registration/admission, Q.931 signaling, H.245 tunneled and separate control, fast-start RTP/RTCP channels, T.120, call forwarding, fragmented/split TPKT packets, and NAT hook unload/reload.
