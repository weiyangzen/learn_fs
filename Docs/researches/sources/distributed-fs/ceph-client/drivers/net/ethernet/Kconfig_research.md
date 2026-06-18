# sources/distributed-fs/ceph-client/drivers/net/ethernet/Kconfig

Purpose: this top-level Ethernet Kconfig menu gates all Ethernet LAN drivers under `drivers/net/ethernet`. It defines the parent `ETHERNET` menu, a generic `MDIO` tristate helper symbol, sources vendor Kconfig files, and declares a few standalone drivers that live directly in the Ethernet directory.

Important APIs, types, and functions: this is declarative Kconfig rather than C code. `menuconfig ETHERNET` depends on `NET` and defaults to `y`. `config MDIO` is a bare tristate helper. The file uses many `source "drivers/net/ethernet/<vendor>/Kconfig"` directives, including the requested `actions`, `adaptec`, and `8390` subtrees. Direct symbols include `CX_ECAT`, `JME`, `KORINA`, `LANTIQ_ETOP`, `LANTIQ_XRX200`, `FEALNX`, `ETHOC`, and `OA_TC6`, each with dependency/select/help metadata.

Control flow: Kconfig evaluation enters this file from the networking driver configuration tree. If `ETHERNET` is disabled, all nested vendor choices are hidden. If enabled, each sourced vendor file contributes its own vendor gate and driver symbols. Direct driver symbols add dependencies such as `PCI`, `X86 || COMPILE_TEST`, `MIKROTIK_RB532 || COMPILE_TEST`, `SOC_TYPE_XWAY`, `HAS_IOMEM && HAS_DMA`, and `SPI`, and select supporting libraries such as `CRC32`, `MII`, `PHYLIB`, and `BITREVERSE`.

State and persistence: Kconfig state persists only in kernel configuration outputs such as `.config`. The file itself stores no runtime state, but the symbol graph determines which Makefile objects are built and which driver code is reachable.

Dependencies and integration points: the file depends on the wider Kconfig language and networking config hierarchy. It integrates with the top-level Ethernet Makefile through matching `CONFIG_*` symbols and with vendor Kconfig files through source order. Source ordering matters for menu presentation and for keeping vendor gates visible under `if ETHERNET`.

Risks: missing or misordered `source` lines can orphan an entire vendor directory. Incorrect dependencies can expose drivers on unsupported architectures or hide them from `COMPILE_TEST`. Missing `select` clauses can break builds by omitting library dependencies. Direct symbols mixed among vendor source lines make merge conflicts and alphabetical drift possible.

Test signals: run Kconfig parsing through `olddefconfig`, `allyesconfig`, `allmodconfig`, and relevant `COMPILE_TEST` builds. Confirm `CONFIG_NET_VENDOR_ACTIONS`, `CONFIG_OWL_EMAC`, `CONFIG_NET_VENDOR_ADAPTEC`, `CONFIG_ADAPTEC_STARFIRE`, and `CONFIG_NET_VENDOR_8390` appear only when expected, and that Makefile object selection follows the enabled symbols.
