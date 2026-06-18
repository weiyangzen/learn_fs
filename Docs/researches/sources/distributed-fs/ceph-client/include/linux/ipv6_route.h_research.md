# sources/distributed-fs/ceph-client/include/linux/ipv6_route.h

## Purpose
`ipv6_route.h` provides small kernel helpers around UAPI IPv6 route flags, mainly for extracting and decoding RFC router-preference bits.

## Important APIs, types, and functions
It defines `IPV6_EXTRACT_PREF(flag)` and `IPV6_DECODE_PREF(pref)`, using `RTF_PREF_MASK` from `uapi/linux/ipv6_route.h`.

## Control flow
Routing code masks route flags, shifts preference bits into a compact value, then XOR-decodes it into the kernel preference ordering where low, medium, and high become ordered values.

## State and persistence
The header has no state and does not persist anything.

## Dependencies and integration points
It integrates with IPv6 route table entries, router advertisements, route preference display, and UAPI route flag definitions.

## Risks and test signals
Risks are bit-position drift with UAPI flags and callers confusing encoded versus decoded preference. Tests should cover low/medium/high route preference flags and zero/default routes.
