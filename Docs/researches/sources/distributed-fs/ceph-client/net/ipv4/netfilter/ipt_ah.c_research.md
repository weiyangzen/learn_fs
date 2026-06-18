# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ah.c

## Purpose
`ipt_ah.c` implements the IPv4 `ah` match, matching IPsec Authentication Header packets by SPI range.

## Important APIs, Types, And Functions
The match object is `ah_mt_reg`. `spi_match()` applies inclusive SPI range and inversion. `ah_mt()` extracts the AH header and evaluates the SPI. `ah_mt_check()` validates inversion flags.

## Control Flow
The match refuses non-first fragments, safely reads the AH header at `par->thoff`, hotdrops tiny packets when the header cannot be read, and compares the network-order SPI against the configured host-order range.

## State And Persistence
No global state. Rule state is `struct ipt_ah` in the xtables match data.

## Dependencies And Integration Points
It is registered for `NFPROTO_IPV4` with protocol `IPPROTO_AH`, and is called from `ip_tables.c` match traversal.

## Risks
Risks include fragment handling surprises, incorrect hotdrop behavior for tiny packets, endianness mistakes in SPI comparison, and invalid inversion flag acceptance.

## Test Signals
Test SPI range match, inverted match, boundary values, non-first fragments, truncated AH headers, non-AH rule rejection via xtables protocol gate, and invalid invflags.
