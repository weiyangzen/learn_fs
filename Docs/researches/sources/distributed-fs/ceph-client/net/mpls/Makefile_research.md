# sources/distributed-fs/ceph-client/net/mpls/Makefile

Purpose: maps MPLS Kconfig symbols to build objects.

Important entries: `obj-$(CONFIG_NET_MPLS_GSO) += mpls_gso.o`, `obj-$(CONFIG_MPLS_ROUTING) += mpls_router.o`, `obj-$(CONFIG_MPLS_IPTUNNEL) += mpls_iptunnel.o`, and `mpls_router-y := af_mpls.o`.

Control flow and state: when routing is enabled, `af_mpls.o` is linked as `mpls_router`. Optional tunnel and GSO helpers build independently according to their symbols.

Dependencies and integration: driven by `Kconfig`; integrates with kernel net build system and module naming.

Risks and test signals: object naming affects module load names and symbol ownership. Build tests should cover each Kconfig symbol combination.
