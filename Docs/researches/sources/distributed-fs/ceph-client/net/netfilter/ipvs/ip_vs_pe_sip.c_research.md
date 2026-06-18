# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe_sip.c

## Purpose
Implements the SIP persistence engine for IPVS. It extracts the SIP Call-ID header from UDP SIP payloads and uses it as persistence data for connection templates, allowing all messages in a SIP dialog to map consistently.

## Important APIs, Types, and Functions
`ip_vs_sip_pe` registers PE name `sip`. `ip_vs_sip_fill_param()` parses a packet and fills `ip_vs_conn_param.pe_data`. `get_callid()` uses conntrack SIP parsing via `ct_sip_get_header()` to locate and validate the Call-ID. `ip_vs_sip_ct_match()` compares template connections against Call-ID data. `ip_vs_sip_hashkey_raw()` hashes Call-ID data for template lookup, `ip_vs_sip_show_pe_data()` exposes the data, and `ip_vs_sip_conn_out()` creates UDP outgoing connections through `ip_vs_new_conn_out()`.

## Control Flow
When persistence needs a SIP key, the fill function parses the IP header, rejects non-UDP traffic, linearizes the SKB, skips UDP header bytes, extracts Call-ID, validates maximum length and line termination, and copies the header value into `p->pe_data`. Template matching then checks address family, client address, virtual address and port, template flag, protocol, and exact persistence data. Module init registers the PE; module exit unregisters and waits for RCU readers.

## State and Persistence
The module has no mutable global state beyond registration. Per-connection persistence state is a copied Call-ID buffer stored in connection parameters and templates. The maximum data length is bounded by `IP_VS_PEDATA_MAXLEN`.

## Dependencies and Integration Points
Depends on IPVS PE registration, IPVS packet header parsing, SKB linearization, Jenkins hash, Netfilter SIP conntrack parser definitions, UDP header layout, and IPVS connection/template lookup. It works with the sync daemon because version 1 sync messages can carry PE name and PE data.

## Risks
Only UDP SIP is supported. `skb_linearize()` can fail and may be costly. Header parsing must handle folded or malformed SIP headers as implemented by conntrack SIP helpers; overly long or unterminated Call-ID values reject persistence and fall back to default behavior. `p->pe_data` allocation uses `GFP_ATOMIC`, so memory pressure can disable SIP persistence for a packet.

## Test Signals
Send SIP UDP requests with valid, missing, malformed, oversized, and differently cased Call-ID headers. Verify template reuse by Call-ID across client ports, fallback when parsing fails, sync of PE data to backup nodes, and no persistence for non-UDP SIP-like traffic.
