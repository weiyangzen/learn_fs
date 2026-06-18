# sources/distributed-fs/ceph-client/net/ipv6/ip6_checksum.c

Purpose: provides generic IPv6 pseudo-header checksum support when an architecture does not override it, plus a helper for setting UDP checksums on IPv6 UDP tunnel packets.

Important APIs, types, and functions: `csum_ipv6_magic()` folds source address, destination address, length, protocol, and an existing checksum into an IPv6 pseudo-header checksum. `udp6_set_csum()` sets `struct udphdr.check` for nocheck, GSO, CHECKSUM_PARTIAL, and software-prepared partial checksum cases.

Control flow: `csum_ipv6_magic()` accumulates each 32-bit address word and pseudo-header field with explicit carry handling, then folds the sum. `udp6_set_csum()` either writes zero for nocheck, writes the complemented pseudo-header checksum for GSO or newly partial skbs, or combines an existing LCO checksum for `CHECKSUM_PARTIAL`, converting zero to `CSUM_MANGLED_0`.

State and persistence: no persistent state. It mutates skb checksum metadata (`ip_summed`, `csum_start`, `csum_offset`) and UDP header checksum fields.

Dependencies and integration points: used by IPv6 UDP, tunnel, and checksum-offload paths. Depends on `udp_hdr()`, `udp_v6_check()`, `lco_csum()`, and architecture checksum primitives.

Risks: checksum mode transitions are subtle; callers must have transport headers set correctly. `nocheck` creates zero UDP checksums, which is only valid where upper-layer policy permits it. Incorrect length or address inputs silently produce bad checksums.

Test signals: checksum unit tests against known pseudo-header vectors, UDP tunnel packets with GSO and non-GSO skbs, CHECKSUM_PARTIAL paths with LCO, zero-checksum mangling, and architecture builds with and without `_HAVE_ARCH_IPV6_CSUM`.
