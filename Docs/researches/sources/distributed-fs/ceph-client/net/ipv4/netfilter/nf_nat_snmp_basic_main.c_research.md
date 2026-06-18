# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_snmp_basic_main.c

## Purpose
Basic SNMP NAT application-layer gateway. It scans SNMPv1/SNMPv2 UDP payloads at ASN.1/BER level and rewrites embedded IPv4 address values so SNMP management traffic remains coherent across static NAT boundaries.

## Important APIs, types, and functions
`struct snmp_ctx` carries payload base, UDP checksum pointer, old address, and new address. `snmp_version()` validates supported versions. `snmp_helper()` is called by the generated ASN.1 decoder for IP address values. `fast_csum()` adjusts UDP checksum after rewriting. `snmp_translate()` computes direction-dependent address mapping and invokes `asn1_ber_decoder()`. `help()` is the conntrack helper callback. `snmp_trap_helper` registers the UDP trap helper.

## Control flow
`help()` receives candidate UDP packets, only mangles SNMP replies and originating traps in expected directions, exits when there is no NAT, verifies UDP length, makes the skb writable, and serializes parser/mangle work under `snmp_lock`. `snmp_translate()` selects old/new addresses from conntrack tuples and runs the BER decoder. When `snmp_helper()` sees a four-byte value equal to `ctx.from`, it fixes checksum if nonzero and writes `ctx.to`.

## State and persistence
No durable per-flow state beyond conntrack/NAT state. `snmp_lock` globally serializes decoder and payload mutation. The helper policy creates no expectations. `nf_nat_snmp_hook` is RCU-published on init and cleared on exit.

## Dependencies and integration points
Depends on IPv4/UDP headers, NAT and conntrack helper APIs, generated `nf_nat_snmp_basic.asn1.h`, checksum helpers, and helper aliases for `snmp_trap` / `ip_nat_snmp_basic`.

## Risks
Malformed or unsupported BER drops packets. Only SNMPv1/v2 are supported. Checksum delta handling depends on payload offset parity. Because the decoder scans tagged IP address values, it can rewrite matching generic address fields rather than MIB-aware fields.

## Test signals
Cover replies from port 161, traps to port 162, NATed/non-NATed flows, bad UDP length, unsupported versions, malformed BER, zero/nonzero UDP checksum, odd/even offset rewrites, and no-match payloads.
