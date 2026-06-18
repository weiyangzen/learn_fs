# sources/distributed-fs/ceph-client/include/linux/icmp.h

## Purpose
Defines in-kernel IPv4 ICMP helpers and RFC 4884/RFC 5837 extension constants. It bridges `sk_buff` transport-header access, UAPI ICMP definitions, and error-queue extension parsing.

## Important APIs, Types, And Functions
`icmp_hdr()` returns the ICMP header at `skb_transport_header()`. `icmp_is_err()` classifies destination unreachable, source quench, redirect, time exceeded, and parameter problem as ICMP error messages. `ip_icmp_error_rfc4884()` parses extended ICMP error data into `sock_ee_data_rfc4884`. Constants and `icmp_ext_iio_name_subobj` describe RFC 4884 extension versions and RFC 5837 interface information objects.

## Control Flow
Networking receive/error paths set the skb transport header, use `icmp_hdr()` to inspect the ICMP header, classify error types with `icmp_is_err()`, and optionally parse extension data for socket error queues or sysctl-enabled ICMP error extensions.

## State And Persistence
No persistent state is defined. State is packet-local in `sk_buff`, ICMP headers, and error queue metadata generated elsewhere.

## Dependencies And Integration Points
Includes `linux/skbuff.h`, UAPI ICMP constants, and UAPI error queue definitions. Integrates with IPv4 input, routing, socket error queues, PMTU/error reporting, and sysctls controlling ICMP error extensions.

## Risks
Callers must ensure transport headers and packet lengths are valid before dereferencing. Error classification influences whether packets are treated as network errors; incorrect classification can break error propagation or filtering. Extension parsing must defend against malformed lengths.

## Test Signals
IPv4 ICMP receive tests, error queue tests with RFC 4884 extensions, PMTU and redirect behavior, malformed/truncated ICMP packets, and sysctl-controlled interface-information extension reporting.
