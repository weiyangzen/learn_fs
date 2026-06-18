# sources/distributed-fs/ceph-client/net/mpls/Kconfig

Purpose: defines configuration options for MPLS core support, GSO helper, routing, and IP-over-MPLS tunnel support.

Important symbols: `MPLS` is the top-level bool. `NET_MPLS_GSO` enables segmentation support for MPLS-stacked GSO packets. `MPLS_ROUTING` depends on `PROC_SYSCTL` and compatible IP tunnel configuration. `MPLS_IPTUNNEL` depends on `LWTUNNEL` and `MPLS_ROUTING`.

Control flow and state: options gate compilation of MPLS data-plane and sysctl/netlink components in the Makefile.

Dependencies and integration: pairs with `net/mpls/Makefile`, routing implementation, GSO helper, and lightweight tunnel integration.

Risks and test signals: dependency expressions control valid build matrices; test modular and built-in combinations for routing/tunnel/GSO.
