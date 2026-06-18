<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c

This file supplies the 6LoWPAN-specific `ndisc_ops` hooks used by IPv6 neighbor discovery when the lower link is IEEE 802.15.4. Its purpose is to preserve and advertise 802.15.4 short-address information in ND source/target link-layer address options and to synthesize short-address-based autoconfigured IPv6 addresses from router advertisements.

Important entry points are the static hooks installed in `lowpan_ndisc_ops`: option parsing, neighbor update, option-space calculation, option filling, and prefix receive address addition. `lowpan_ndisc_parse_options()` accepts only IEEE802154 lowpan devices and handles source/target LL address options whose option length is the short-address form. `lowpan_ndisc_802154_update()` extracts short addresses from ND options and stores them in `struct lowpan_802154_neigh` under the neighbor lock. `lowpan_ndisc_opt_addr_space()` and `lowpan_ndisc_fill_addr_option()` decide whether outgoing RS/NS/NA/Redirect packets should carry the short address option.

Control flow is callback-driven from the IPv6 ndisc core. Incoming packets are parsed into `struct ndisc_options`, neighbor updates run only for override updates, and outgoing packet construction first asks for option space and then writes the option. State is in per-neighbor lowpan private data and the underlying `wpan_dev->short_addr`; there is no persistent storage. Dependencies include `net/ndisc.h`, `net/addrconf.h`, 6LoWPAN internals, IEEE802154 address helpers, and neighbor locking.

Integration risk is mainly around malformed option lengths, byte-order conversion between big-endian ND option data and little-endian IEEE802154 addresses, and races with neighbor updates. Test signals should include RA/RS/NS/NA/Redirect traffic on IEEE802154 6LoWPAN, duplicate option parsing, invalid short addresses, and non-IEEE802154 lowpan devices where hooks must be no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c -->
