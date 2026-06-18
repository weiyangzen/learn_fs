<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c

## Purpose
`xt_esp.c` implements the `esp` match for IPsec ESP packets. It matches the ESP Security Parameters Index against a configured range.

## Important APIs, Types, and Functions
`esp_mt()` reads `struct ip_esp_hdr` at `par->thoff` and calls `spi_match()` for range and inversion logic. `esp_mt_check()` validates inversion flags. `esp_mt_reg[]` registers IPv4 and IPv6 matches with `.proto = IPPROTO_ESP`.

## Control Flow, State, and Persistence
The matcher rejects non-initial fragments, reads the ESP header through `skb_header_pointer()`, hotdrops truncated headers, converts SPI to host order, then checks `spis[0] <= spi <= spis[1]` with `XT_ESP_INV_SPI`. It persists no state.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 registration, and the IPsec ESP header definitions. It is a parser-only match; actual IPsec policy and state are handled elsewhere by xfrm.

## Risks and Test Signals
Risks include truncated ESP headers, fragment handling, endian errors on SPI, and rule confusion between ESP SPI and xfrm policy. Tests should cover SPI range boundaries, inverted ranges, fragments, tiny packets with hotdrop, IPv4/IPv6 rules, and invalid inversion flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c -->
