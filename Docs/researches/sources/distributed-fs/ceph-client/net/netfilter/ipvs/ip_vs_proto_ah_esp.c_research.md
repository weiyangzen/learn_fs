# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_ah_esp.c

## Purpose
Provides IPVS protocol handlers for IPsec AH and ESP related traffic. Since AH/ESP do not expose transport ports, the handlers associate them with existing ISAKMP UDP/500 connections rather than scheduling new services directly.

## Important APIs, Types, and Functions
`ah_esp_conn_fill_param_proto()` creates a UDP/500 connection parameter from the IP header, respecting inverse direction. `ah_esp_conn_in_get()` and `ah_esp_conn_out_get()` look up matching IPVS connections. `ah_esp_conn_schedule()` always accepts the packet without scheduling. `ip_vs_protocol_ah` and `ip_vs_protocol_esp` are compiled conditionally and provide the `struct ip_vs_protocol` entries.

## Control Flow
For inbound or outbound AH/ESP packets, the handler fills an ISAKMP-style parameter and searches the IPVS connection table. If no connection exists, debug logging records an unknown related packet and the packet is allowed to pass. The scheduling hook sets verdict `NF_ACCEPT` because AH/ESP is handled only as related traffic.

## State and Persistence
No local state or timeout table is owned by this file. AH/ESP association depends on existing IPVS UDP/500 connection entries and their lifetimes.

## Dependencies and Integration Points
Depends on IPVS protocol registration, connection lookup helpers, IP header direction helpers, Netfilter verdicts, and UDP/ISAKMP port conventions. It integrates with IPsec VPN load balancing where IKE creates the controlling connection and AH/ESP follows it.

## Risks
Mapping all AH/ESP to UDP/500 control state is coarse and cannot distinguish multiple security associations beyond addresses and direction. The code does not NAT AH/ESP payloads and provides no state transition handler. Unknown related traffic is accepted, so policy enforcement must be elsewhere.

## Test Signals
Create IPVS services for IKE and verify AH/ESP packets find the expected connection in both directions. Test absence of an ISAKMP connection, inverse header handling, AH-only and ESP-only builds, and debug logs for unknown related packets.
