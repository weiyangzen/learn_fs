# sources/distributed-fs/ceph-client/include/linux/dsa/ocelot.h

## Purpose
This header defines Ocelot/Felix DSA tagger metadata, injection/extraction header layout helpers, PTP rewrite operation selection, deferred transmit work, and VLAN-tag handling for CPU-injected frames.

## Important APIs, types, and functions
Important constants define tag lengths, prefix lengths, tag types, and rewrite op codes. `struct ocelot_skb_cb` stores clone, PTP class, TX time, low timestamp bits, PTP command, and timestamp ID in the skb control block. `struct felix_deferred_xmit_work` and `struct ocelot_8021q_tagger_data` support deferred TX. Accessors and mutators such as `ocelot_xfh_get_rew_val()`, `ocelot_xfh_get_len()`, `ocelot_xfh_get_src_port()`, `ocelot_xfh_get_qos_class()`, `ocelot_xfh_get_tag_type()`, `ocelot_xfh_get_vlan_tci()`, and `ocelot_ifh_set_*()` pack/unpack bit ranges via `packing()`.

`ocelot_ptp_rew_op()` selects two-step or origin PTP rewrite operations based on skb control-block state. `ocelot_xmit_get_vlan_info()` decides which VLAN TCI and tag type to place in the injection header, removing an skb VLAN header when the bridge is VLAN-aware and otherwise using VID 0 with C-tag type.

## Control flow, state, and persistence
Per-packet state is in `skb->cb` and tag headers. Deferred transmission persists as kthread work. The extraction header parser computes frame length from LLEN/WLEN fields and extracts source/QoS/VLAN metadata. VLAN handling mutates the skb by removing VLAN tags for VLAN-aware bridges.

## Dependencies and integration points
It depends on bridge VLAN helpers, VLAN headers, kthread work, packing bitfield helpers, skbuffs, and DSA. It integrates with Ocelot and Felix switch taggers, PTP timestamping, and VLAN-aware bridge forwarding.

## Risks and test signals
Risks include bit-range packing mistakes, skb control-block collisions, incorrect length calculation (`60 * wlen + llen - 80`), VLAN tag removal side effects, and `BUG_ON()` if tagger protocol is unexpected. Tests should cover extraction/injection bit round trips, PTP two-step clone handling, VLAN-aware and VLAN-unaware bridge injection, short/long/no-prefix frames, and Seville destination-width differences.
