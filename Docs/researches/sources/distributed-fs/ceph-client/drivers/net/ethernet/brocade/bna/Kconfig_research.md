# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Kconfig

Purpose: driver-specific Kconfig option for the QLogic BR-series 1010/1020/1860 10Gb CEE-capable Ethernet driver.

Important APIs/types/functions: defines `config BNA` as a tristate option with prompt text and `depends on PCI`. The help text says module builds produce a module named `bna`.

Control flow: once the parent vendor menu is active, the user or defconfig may select `BNA=y` or `BNA=m`, subject to PCI availability. That symbol drives the top-level and child Makefiles.

State and persistence behavior: no runtime state. Persistent state is the generated `CONFIG_BNA` selection that controls whether the BNA code is omitted, built in, or built as a module.

Dependencies and integration points: integrates with kernel Kconfig, the parent Brocade Kconfig, and the kbuild Makefiles. The runtime driver itself also depends on PCI APIs, firmware/message infrastructure, netdev, ethtool, and debugfs through source files listed in the Makefile.

Risks: missing dependency constraints can expose compile failures on unsupported architectures; over-constraining hides valid builds. The support URL is informational and may not reflect current vendor branding.

Test signals: Kconfig should accept `CONFIG_BNA=m` on PCI-capable builds, and `modinfo bna` should exist after module compilation.
