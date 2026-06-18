# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Kconfig

Purpose: declares Broadcom B53 DSA common support and transport/SerDes options.

Important APIs/types/functions: `B53` depends on `NET_DSA` and selects supported DSA tag protocols. Transport symbols are `B53_SPI_DRIVER`, `B53_MDIO_DRIVER`, `B53_MMAP_DRIVER`, `B53_SRAB_DRIVER`, and optional `B53_SERDES`.

Control flow: enabling `B53` exposes transport choices; each selected transport maps to a Makefile object. SRAB can use SerDes when enabled.

State and persistence behavior: Build-time `.config` state only.

Dependencies and integration points: DSA, SPI, MMIO, architecture defaults, Broadcom tag protocols, and the local B53 Makefile.

Risks: selected tag protocol dependencies must remain valid; SRAB/SerDes optional linking must match guards; defaults can change platform build contents.

Test signals: B53 common only, each transport as built-in/module, SRAB with `B53_SERDES` enabled/disabled, and architecture default configs.
