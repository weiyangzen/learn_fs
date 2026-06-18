<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h

## Purpose
`icmp.h` defines the IPv4 ICMP wire-format constants and structures used by raw sockets, packet parsers, and kernel networking code.

## Important APIs, types, and functions
Constants define ICMP message types such as echo reply/request, destination unreachable, source quench, redirect, time exceeded, parameter problem, timestamp, info request/reply, address mask, and extended echo. Code constants cover unreachable reasons, redirect variants, time-exceeded reasons, extended echo reply codes/flags, c-types, and address family identifiers. `struct icmphdr` defines type, code, checksum, and a union for echo ID/sequence, gateway, fragment MTU, or reserved bytes. `ICMP_FILTER` and `struct icmp_filter` define the raw-socket filter option. RFC 4884 and RFC 8335 extension layouts include `struct icmp_ext_hdr`, `struct icmp_extobj_hdr`, `struct icmp_ext_echo_ctype3_hdr`, and `struct icmp_ext_echo_iio`.

## Control flow
ICMP packets are parsed by inspecting type and code, validating checksum, and interpreting the union based on type. Raw-socket users can install an ICMP type filter. Extended echo and RFC 4884 messages append extension headers and objects after the base ICMP payload.

## State and persistence behavior
ICMP state is packet-local, except that applications may correlate echo ID/sequence or extended echo identifiers. The header stores no state.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with IPv4 raw sockets, ping, traceroute, network diagnostics, firewall/NAT code, and packet analyzers.

## Risks and test signals
Risks include wrong union member for type, byte-order mistakes, accepting invalid type/code pairs, ICMP filter bit mistakes, extension object length errors, extended echo compatibility, and unchecked MTU or gateway fields. Test signals include ping/traceroute tests, checksum validation, unreachable/code parsing, socket filter behavior, extended echo cases, raw-socket send/receive, and packet-fuzzer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h -->
