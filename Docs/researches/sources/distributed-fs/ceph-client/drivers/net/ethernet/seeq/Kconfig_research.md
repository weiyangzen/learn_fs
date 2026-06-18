# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Kconfig

Purpose: Defines Kconfig options for SEEQ-family Ethernet drivers.

Important APIs and flow: `NET_VENDOR_SEEQ` is the vendor menu gate, defaults to `y`, and depends on `HAS_IOMEM`. Within the vendor block, `ARM_ETHER3` builds Acorn/ANT Ether3 support for `ARM && ARCH_ACORN`, while `SGISEEQ` builds SGI Seeq controller support when `SGI_HAS_SEEQ` is available.

State and dependencies: This file controls whether `ether3.o` and `sgiseeq.o` are visible and selectable. It integrates with the parent Ethernet vendor menu and the `seeq/Makefile` object selections.

Risks and test signals: Dependency mistakes either expose drivers on unsupported architectures or hide them from valid legacy platforms. Build tests should cover vendor disabled, vendor enabled with unsupported arch, Acorn enabled, and SGI Seeq enabled.
