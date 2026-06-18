# subset-b-005030 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-tphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-tphy.c

Purpose: Implements the generic MediaTek T-PHY provider for mixed USB2, USB3, PCIe, SATA, and SGMII PHY lanes. The driver instantiates one generic PHY per child node, maps each child register window into version-specific banks, and programs analog/digital lane registers for init, power, USB role mode, and SoC-specific tuning.

Important APIs, types, and flow: `struct mtk_tphy` holds parent state, SoC `mtk_phy_pdata`, per-lane instances, optional shared SIF base, and slew-rate calibration defaults. `struct mtk_phy_instance` tracks the child `struct phy`, port base, U2/U3 bank pointers, two optional clocks, DT-selected type, optional syscon type switch, software efuse fields, eye/disconnect/pre-emphasis tuning, BC1.2, and forced USB3 mode. Probe allocates children, maps resources, gets optional `ref`/`da_ref` clocks, and registers `mtk_phy_xlate()`. Translation validates the single phandle argument, stores the selected `PHY_TYPE_*`, initializes bank pointers by IP version, reads optional nvmem efuse values, parses DT tuning, updates the external type-switch syscon, and creates debugfs entries.

Control flow and state behavior: `mtk_phy_init()` enables clocks, applies software efuse overrides, then dispatches to USB2, USB3, PCIe, SATA, or SGMII setup. USB2 init clears UART/GPIO paths, enables USB PLL/interrupts, optionally applies MT8195 26 MHz PLL workaround, disables BC1.1 unless BC1.2 is explicitly enabled, and applies DT eye/tuning values. USB2 power-on/off controls VBUS/AVALID/SESSEND and runs high-speed slew-rate calibration using the frequency meter unless a fixed eye source is supplied. USB role mode writes IDDIG force bits for host/device/OTG. USB3 setup gates XTAL/XSQ paths, tunes RX/TX/lfps/rxdet values, and can force USB mode by resetting the IP through chip registers. PCIe setup is mostly V1-only analog PLL/clock tuning plus reset release/assert during power transitions. SATA setup applies fixed Gen1 CDR, lock, COMINIT/COMWAKE, and equalization tuning.

Dependencies and integration points: Depends on the Linux generic PHY framework, platform resources, DT phandle arguments from `<dt-bindings/phy/phy.h>`, optional `nvmem-cells`, optional syscon/regmap `mediatek,syscon-type`, optional debugfs, clocks, `readl_poll_timeout()`, and MediaTek register helper functions from `phy-mtk-io.h`. Compatible data selects V1, V2, V3, MT8173 degradation workaround, or MT8195 PLL/efuse behavior.

Risks and test signals: The instance `type` is established lazily by xlate, so clients with wrong phandle args can leave bank pointers unset or select incompatible paths. Software efuse override disables hardware auto-load and must only run on instances with valid nvmem values and valid misc/phyd banks. Slew calibration ignores poll timeout failure and falls back only when frequency output is zero, so USB electrical validation is important. Regression tests should cover each compatible, each PHY type, optional and missing SIF/syscon/nvmem/clocks, USB host/device/OTG mode changes, debugfs reads/writes, MT8173/MT8195-specific paths, and error unwinding for invalid child resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-tphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-ufs.c

Purpose: Provides a small MediaTek UFS MPHY generic PHY driver. It manages the UFS PHY MMIO block and two clocks, switching the PHY between active operation and deep hibernation by forcing or releasing PLL, CDR, isolation, squelch, and DIFZ controls.

Important APIs, types, and flow: `struct ufs_mtk_phy` contains the device, mapped MMIO base, and two `clk_bulk_data` entries named `unipro` and `mp`. `ufs_mtk_phy_probe()` allocates state, maps resource 0, obtains the clocks, creates one generic PHY with `ufs_mtk_phy_ops`, stores drvdata, and registers `of_phy_simple_xlate`. `ufs_mtk_phy_power_on()` enables clocks and calls `ufs_mtk_phy_set_active()`. `ufs_mtk_phy_power_off()` calls `ufs_mtk_phy_set_deep_hibern()` and disables clocks.

Control flow and state behavior: Active mode releases PLL power/isolation force bits, powers CDR, releases CDR isolation, enables RX squelch, waits 1 microsecond, then clears forced DIFZ. Deep hibernation applies the inverse sequence: force DIFZ, force RX squelch off, force CDR isolation and power off, force PLL isolation, and force PLL power off. Runtime state is entirely hardware-register state plus clock enable state; no persistent software state is maintained after probe.

Dependencies and integration points: Uses the generic PHY framework, platform resource mapping, bulk clock API, OF matching for `mediatek,mt8183-ufsphy`, and MediaTek bit helpers from `phy-mtk-io.h`. It is intended to be consumed by a UFS host controller node through a simple PHY phandle.

Risks and test signals: Register sequencing is the main correctness contract; reversed order can leave PLL/CDR isolated or powered unexpectedly. The driver has no `.init`/`.exit`, so consumers must rely on power-on/off transitions. Tests should verify clock names in DT, probe deferral on missing clocks, repeated power cycles, suspend/resume hibernation behavior, and UFS link bring-up after active transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xfi-tphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xfi-tphy.c

Purpose: Implements the MediaTek MT7988 XFI T-PHY used by Ethernet MAC/PCS blocks for SGMII, 1000BASE-X, 2500BASE-X, 5GBASE-R, 10GBASE-R, and USXGMII modes. It converts a generic PHY Ethernet mode request into a long SerDes register programming sequence.

Important APIs, types, and flow: `struct mtk_xfi_tphy` holds MMIO base, device, reset control, two clocks (`topxtal`, `xfipll`), and an optional 10GBase-R performance errata flag. Probe maps the register resource, gets clocks and reset, reads `mediatek,usxgmii-performance-errata`, creates one PHY, and registers `of_phy_simple_xlate`. `mtk_xfi_tphy_set_mode()` accepts only `PHY_MODE_ETHERNET`, validates the interface submode, and calls `mtk_xfi_tphy_setup()`. Power ops only gate clocks; reset uses the reset controller.

Control flow and state behavior: Setup classifies the requested interface into 1G, 2.5G, 5G, or 10G and selects LynxI PCS for 8b/10b 1G/2.5G or USXGMII PCS for 64b/66b 5G/10G. It programs PLL, RXFE, CDR, adaptation, TX defaults, PCS selection, AEQ, TX data force, RG defaults, RX EQ, optional 10G DA workaround, PHYA speed, PCS reset release, P0 transition, Gen2/Gen3 PCS mode, MAC clock enable, and TX data enable with microsecond delays between critical state changes.

Dependencies and integration points: Depends on generic PHY set-mode semantics, Ethernet `phy_interface_t` constants, reset controllers, clocks, OF compatible `mediatek,mt7988-xfi-tphy`, and `phy-mtk-io.h` read-modify-write helpers. It integrates with network drivers that call `phy_set_mode_ext()`, `phy_power_on()`, and reset during MAC/PCS configuration.

Risks and test signals: Many register writes remain vendor-derived magic constants, so mode coverage is essential. `set_mode()` returns success after programming but does not poll link/PLL status. The errata bit affects only 10GBase-R, not USXGMII. Tests should exercise every accepted interface mode, invalid modes, reset and clock failure paths, 10GBase-R with and without errata, repeated mode changes, and real link training with LynxI versus USXGMII PCS selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xfi-tphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xsphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xsphy.c

Purpose: Provides the MediaTek XS-PHY driver for USB3.1 Gen2-era PHY blocks supporting USB2, USB3, PCIe, and SGMII lane use. It is similar in shape to T-PHY but has a different bank layout and a narrower feature set.

Important APIs, types, and flow: `struct mtk_xsphy` stores the parent device, optional shared U3 global base, per-child `xsphy_instance` pointers, and USB2 slew calibration parameters. Each `xsphy_instance` stores the generic PHY, port base, per-lane ref clock, type selected by phandle argument, optional syscon type switch, efuse/tuning fields, and USB2 eye values. Probe maps optional global registers, creates a PHY for every child, maps child resources, obtains each `ref` clock, reads optional type switch info, and registers `mtk_phy_xlate()`.

Control flow and state behavior: Translation validates one phandle argument, supports USB2/USB3/PCIe/SGMII, parses type-specific DT tuning, and writes the optional syscon lane function. Init enables the lane ref clock, initializes USB2 registers or USB3 tuning, and leaves PCIe/SGMII to the type switch only. USB2 power-on enables OTG VBUS comparator, sets VBUSVALID/AVALID, and performs slew-rate calibration using the U2 frequency meter unless `eye-src` is fixed. Power-off clears VBUS comparator and sets SESSEND. USB2 set-mode toggles IDDIG force bits for host, device, or OTG.

Dependencies and integration points: Uses generic PHY, child-node resources, per-lane `ref` clocks, optional parent U3 global resource, optional `mediatek,syscon-type`, syscon/regmap, `readl_poll_timeout()`, and MediaTek IO helpers. Consumers distinguish lane purpose through the single `#phy-cells` argument.

Risks and test signals: USB3 tuning writes use `glb_base`; DTs with USB3 lanes but no global resource would be unsafe. Like T-PHY, lane type is stored at xlate time and may be reinterpreted if multiple consumers use one child differently. Slew calibration ignores timeout status and only falls back on zero frequency output. Tests should cover USB2/USB3/PCIe/SGMII xlate, missing optional global resource for non-USB3 cases, syscon switch offsets, ref-clock enable failure, USB role switching, and electrical tuning values from DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-xsphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/Kconfig

Purpose: Defines build-time configuration entries for the Microchip PHY drivers in this directory: Sparx5/LAN969x SerDes and LAN966x SerDes muxing.

Important APIs, types, and flow: `PHY_SPARX5_SERDES` is a tristate that selects `GENERIC_PHY`, depends on `ARCH_SPARX5 || ARCH_LAN969X || COMPILE_TEST`, `OF`, and `HAS_IOMEM`, and describes 10G/25G SerDes support for Microchip Sparx5. `PHY_LAN966X_SERDES` is a tristate that selects `GENERIC_PHY`, depends on `SOC_LAN966 || MCHP_LAN966X_PCI || COMPILE_TEST`, `OF`, and `MFD_SYSCON`, and describes LAN966X SerDes muxing support.

State, dependencies, and integration points: These symbols gate compilation through the local Makefile and determine whether platform devices matching the compatible strings can bind. The dependencies ensure DT probing and MMIO are available; LAN966x additionally requires syscon because the driver uses shared HSIO/config registers.

Risks and test signals: Build coverage should include built-in, module, and disabled variants, plus `COMPILE_TEST` on non-Microchip architectures. Dependency drift is the main risk: if driver code grows new APIs such as clocks or resets, Kconfig must gain matching dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/Makefile

Purpose: Connects Microchip PHY Kconfig symbols to their object files.

Important APIs, types, and flow: `obj-$(CONFIG_PHY_SPARX5_SERDES) := sparx5_serdes.o` builds the Sparx5/LAN969x SerDes driver when enabled. `obj-$(CONFIG_PHY_LAN966X_SERDES) := lan966x_serdes.o` builds the LAN966x SerDes driver when enabled.

State, dependencies, and integration points: There is no runtime state; this is a kernel build-system mapping consumed by Kbuild under `drivers/phy/microchip`. The object names match the platform-driver source files.

Risks and test signals: This file is simple, but using `:=` instead of accumulating with `+=` means each symbol maps to one object as intended. Build tests should verify both drivers compile when selected together and independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes.c -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes.c

Purpose: Implements the Microchip LAN966x SerDes generic PHY provider. It exposes CU, 6G SerDes, and RGMII PHY macros, maps Ethernet port/mode requests onto HSIO mux bits, and programs SD6G40 or RGMII timing/register state.

Important APIs, types, and flow: `struct serdes_ctrl` owns the HSIO register base, device, per-index PHY array, and detected 125 MHz reference flag. `struct serdes_macro` stores a PHY macro index, associated Ethernet port, speed, selected mode, and back-pointer. `lan966x_serdes_muxes[]` is the central mapping table from macro index, port, `PHY_MODE_ETHERNET`, and interface submode to HSIO mux mask/value. Probe maps HSIO registers plus a hardware-status resource, creates all PHYs, reads PLL configuration to determine the reference clock, and registers `serdes_simple_xlate()` which takes two cells: port and macro index.

Control flow and state behavior: `serdes_set_mode()` normalizes 1000BASE-X and 2500BASE-X to SGMII programming, maps QUSGMII to QSGMII, finds the mux table entry for the requested port and macro, writes HSIO hardware config, stores the mode, then dispatches by macro class. CU entries require only muxing. SD6G entries calculate QSGMII/SGMII lane setup from mode, speed, and reference clock, program SD_CFG/MPLL_CFG, deassert resets, enable MPLL/TX common-mode/RX PLL/TX, poll status bits, and enable TX/RX data. RGMII entries program clock speed selection and DLL delay enables according to RGMII delay submode. `serdes_set_speed()` reprograms only RGMII timing after link-speed changes.

Dependencies and integration points: Depends on generic PHY, OF platform probing, LAN966x DT binding macros from `phy-lan966x-serdes.h`, generated register macros from `lan966x_serdes_regs.h`, MMIO resources, and Ethernet `phy_interface_t` constants. Consumers are typically switch/MAC drivers that request a specific port/index pair and then call set-mode and set-speed.

Risks and test signals: The mux table is the policy boundary; missing or overlapping entries produce `-EINVAL` or wrong port routing. Status checks expect MPLL, TX common-mode, RX PLL, and TX state to become 1 after fixed sleeps; bring-up failures return `-EIO`. Tests should cover each legal port/macro combination, QSGMII group mappings, 1G versus 2.5G SGMII calculations, 25 MHz versus 125 MHz reference detection, every RGMII delay mode and speed, invalid phandle cells, and failure injection for lock/status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes_regs.h -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes_regs.h

Purpose: Provides generated-style LAN966x HSIO register address macros and bitfield helpers used by `lan966x_serdes.c`.

Important APIs, types, and flow: Defines `enum lan966x_target` with `TARGET_HSIO`, address tuple macros such as `HSIO_SD_CFG(g)`, `HSIO_MPLL_CFG(g)`, `HSIO_SD_STAT(g)`, `HSIO_HW_CFG`, `HSIO_RGMII_CFG(r)`, and `HSIO_DLL_CFG(r)`, and field `*_SET()`/`*_GET()` wrappers built from `FIELD_PREP()` and `FIELD_GET()`. Covered fields include SD lane resets/rates/inversion/data enables/loopback, MPLL enable/refclk/multiplier, status bits, HSIO mux config for RGMII/SD6G/GMII/QSGMII, RGMII clock/reset, and DLL delay enable/reset.

State, dependencies, and integration points: This header carries no state; it is the compile-time register contract for LAN966x SerDes programming. The tuple layout is consumed by `lan_offset()` in the C file to compute byte offsets.

Risks and test signals: Incorrect tuple dimensions or bit masks would silently write the wrong HSIO register or field. Compile-time users should remain limited to compatible address macros, and hardware tests should verify each field against the datasheet through known-good mode transitions and status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.c -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.c

Purpose: Implements the Microchip Sparx5 and LAN969x SerDes generic PHY provider. It supports multiple SerDes generations (6G, 10G, 25G), Ethernet interface modes from 100BASE-FX through 25G-oriented SFI presets, media-specific tuning, power save, reset, validation, and SoC-specific register maps.

Important APIs, types, and flow: The driver defines large preset tables for 25G and 10G media/mode combinations, parameter structures that flatten those presets into register fields, CMU maps for Sparx5 and LAN969x, and SoC descriptors with register offsets and type callbacks. `struct sparx5_serdes_private` stores device, mapped target bases, PHY array, core clock, and match data. Each `sparx5_serdes_macro` tracks logical index, target-local index, SerDes type, current mode, requested port interface, speed, and media. Probe gets match data, core clock, maps one large MMIO resource into target pointers using the descriptor iomap, creates all PHYs, powers them off by default, optionally powers down Sparx5 CMUs, and registers a one-cell xlate by SerDes index.

Control flow and state behavior: `set_speed()`, `set_media()`, and `set_mode()` store requested state and trigger `sparx5_serdes_config()` once enough state is present. Config maps `phy_interface_t` plus speed to an internal mode, handles 100BASE-FX core-clock setup, chooses 25G or 10G/6G programming, builds params from mode and media presets, resets the lane, applies many register fields, releases macro/CDR resets, waits for lock/reset completion, and returns errors on PLL loss-of-lock or PMA reset failure. Reset re-runs the relevant config with reset semantics. Power-on/off toggles TX driver power-down and quiet-mode registers rather than rebuilding full mode state. Validation enforces Ethernet mode, known speed, per-SoC lane speed ceilings, and compatible speed/interface combinations.

Dependencies and integration points: Depends on generated `sparx5_serdes_regs.h` through `sparx5_serdes.h`, generic PHY ops including media and speed callbacks, OF compatible data for `microchip,sparx5-serdes` and `microchip,lan9691-serdes`, platform MMIO, a core clock, Ethernet interface definitions, and target-size tables selected globally through `tsize`. Network drivers use the PHY to configure SerDes lanes before link operation.

Risks and test signals: The file is register-sequence heavy and relies on preset correctness, SoC iomap correctness, and CMU mapping tables. `set_mode()` ignores the return from `sparx5_serdes_config()` and returns 0 after attempting configuration, which can hide hardware programming failure from callers. The global `tsize` pointer is set at probe from match data and is shared across instances. Tests should cover Sparx5 and LAN969x descriptors, every lane-type boundary, 6G/10G/25G reset and power-save paths, invalid speed/interface combinations, media changes after mode set, PLL/PMA failure reporting, core-clock variants for 100BASE-FX, and xlate rejection for out-of-range indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.h -->
# sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.h

Purpose: Declares shared types, constants, SoC descriptor structures, and register access helpers for the Sparx5/LAN969x SerDes driver.

Important APIs, types, and flow: Defines `SPX5_SERDES_MAX`, SerDes type enum (`6G`, `10G`, `25G`), internal mode enum (`NONE`, `2G5`, `QSGMII`, `100FX`, `1000BASEX`, `SFI`), CMU selection enum, target enum (`SPARX5`, `LAN969X`), `struct sparx5_serdes_macro`, descriptor constants/ops/match data, and private driver state. Inline helpers `sdx5_addr()`, `sdx5_inst_baseaddr()`, `sdx5_rmw()`, `sdx5_inst_rmw()`, `sdx5_rmw_addr()`, `sdx5_inst_get()`, and `sdx5_inst_addr()` convert generated register macro tuples into MMIO addresses and read-modify-write operations, with `WARN_ON()` bounds checks for target/group/register instances.

State and dependencies: The header includes `sparx5_serdes_regs.h` and depends on its generated target IDs, `NUM_TARGETS`, target-size enums, and field macros. Runtime state is owned by the C file but shaped here: per-macro current requested link state and per-device target base arrays.

Risks and test signals: All register access goes through tuple arithmetic in these helpers, so target-size and index mistakes affect broad hardware programming. `WARN_ON()` detects some out-of-range tuple instances but does not prevent writes when base pointers are wrong. Build tests should catch descriptor/type mismatches, and hardware tests should exercise representative access paths for each target class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.h -->
