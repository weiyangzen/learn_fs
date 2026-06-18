# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xfi-tphy.c

Purpose: Implements the MediaTek MT7988 XFI T-PHY used by Ethernet MAC/PCS blocks for SGMII, 1000BASE-X, 2500BASE-X, 5GBASE-R, 10GBASE-R, and USXGMII modes. It converts a generic PHY Ethernet mode request into a long SerDes register programming sequence.

Important APIs, types, and flow: `struct mtk_xfi_tphy` holds MMIO base, device, reset control, two clocks (`topxtal`, `xfipll`), and an optional 10GBase-R performance errata flag. Probe maps the register resource, gets clocks and reset, reads `mediatek,usxgmii-performance-errata`, creates one PHY, and registers `of_phy_simple_xlate`. `mtk_xfi_tphy_set_mode()` accepts only `PHY_MODE_ETHERNET`, validates the interface submode, and calls `mtk_xfi_tphy_setup()`. Power ops only gate clocks; reset uses the reset controller.

Control flow and state behavior: Setup classifies the requested interface into 1G, 2.5G, 5G, or 10G and selects LynxI PCS for 8b/10b 1G/2.5G or USXGMII PCS for 64b/66b 5G/10G. It programs PLL, RXFE, CDR, adaptation, TX defaults, PCS selection, AEQ, TX data force, RG defaults, RX EQ, optional 10G DA workaround, PHYA speed, PCS reset release, P0 transition, Gen2/Gen3 PCS mode, MAC clock enable, and TX data enable with microsecond delays between critical state changes.

Dependencies and integration points: Depends on generic PHY set-mode semantics, Ethernet `phy_interface_t` constants, reset controllers, clocks, OF compatible `mediatek,mt7988-xfi-tphy`, and `phy-mtk-io.h` read-modify-write helpers. It integrates with network drivers that call `phy_set_mode_ext()`, `phy_power_on()`, and reset during MAC/PCS configuration.

Risks and test signals: Many register writes remain vendor-derived magic constants, so mode coverage is essential. `set_mode()` returns success after programming but does not poll link/PLL status. The errata bit affects only 10GBase-R, not USXGMII. Tests should exercise every accepted interface mode, invalid modes, reset and clock failure paths, 10GBase-R with and without errata, repeated mode changes, and real link training with LynxI versus USXGMII PCS selection.
