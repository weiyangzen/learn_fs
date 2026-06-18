# sources/distributed-fs/ceph-client/include/uapi/linux/ip.h

## Purpose
`ip.h` exports IPv4 packet header, option, TOS/precedence, IPsec transform header, BEET/IPTFS, and per-device IPv4 configuration constants to userspace.

## Important APIs, Types, and Functions
The main ABI type is `struct iphdr`, with endian-specific bitfields for `version` and `ihl`, network-order length, ID, fragment, checksum, and grouped source/destination addresses. Related protocol headers include `ip_auth_hdr`, `ip_esp_hdr`, `ip_comp_hdr`, `ip_beet_phdr`, `ip_iptfs_hdr`, and `ip_iptfs_cc_hdr`. Macros define IP options (`IPOPT_*`), TOS/precedence masks, TTL defaults, option offsets, and `IPV4_BEET_PHMAXLEN`. The `IPV4_DEVCONF_*` enum names per-interface IPv4 sysctl slots.

## Control Flow
Packet-producing userspace or tooling fills these structures, usually through raw sockets, packet captures, test fixtures, or tunnel/IPsec control paths. The kernel networking stack parses the same wire layouts while routing, fragmenting, applying options, and handling IPsec headers.

## State and Persistence
The header has no storage; persistence is in packet buffers, route/device configuration, and xfrm/IPsec state managed elsewhere. `IPV4_DEVCONF_*` values index mutable per-device configuration.

## Dependencies and Integration Points
It depends on `<linux/types.h>`, `<linux/stddef.h>`, and `<asm/byteorder.h>`. Integration points include raw sockets, netfilter, xfrm, tunnel drivers, `/proc`/sysctl IPv4 devconf, packet decoders, and network test suites.

## Risks and Test Signals
Endianness is the largest layout risk because bitfield order differs by byte order. Tests should inspect `sizeof(struct iphdr)`, option parsing up to `MAX_IPOPTLEN`, fragment flag handling, checksum field offsets, devconf enum stability, and variable-length transform headers.
