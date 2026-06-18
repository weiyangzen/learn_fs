# Research: subset-b-004648

Grouped research report for the subset B work item. Each file section is wrapped with reconciliation markers so it can be split into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c

## Purpose
`dwmac-ipq806x.c` is the Qualcomm Atheros IPQ806x platform glue layer for the Synopsys stmmac Ethernet core. It translates IPQ806x device-tree resources into `plat_stmmacenet_data`, programs NSS common and QSGMII CSR registers for RGMII or SGMII operation, and adapts MAC clocks when link speed changes.

## Important APIs, Types, and Functions
- `struct ipq806x_gmac` stores the platform device, NSS common regmap, QSGMII regmap, GMAC id, core clock, and selected PHY mode.
- `ipq806x_gmac_of_parse()` reads `qcom,id`, `qcom,nss-common`, `qcom,qsgmii-csr`, and the `stmmaceth` clock.
- `ipq806x_gmac_set_speed()` chooses RGMII or SGMII dividers and temporarily gates RX/TX clocks while updating `NSS_COMMON_CLK_DIV0`.
- `ipq806x_gmac_configure_qsgmii_params()` and `ipq806x_gmac_configure_qsgmii_pcs_speed()` tune QSGMII PHY parameters and fixed-link speed forcing.
- `ipq806x_gmac_probe()` wires `set_clk_tx_rate`, FIFO sizes, `core_type`, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac MMIO/IRQ resources, parses common stmmac DT data, allocates private state, then parses IPQ806x-specific syscon and clock resources. It resets QSGMII calibration lock detect, writes per-GMAC NSS control bits for IFG, AXI low-power exit, interface selection, source clock selection, and clock gates, then performs SGMII-only QSGMII PHY/PCS setup. Runtime link speed changes enter through `plat_dat->set_clk_tx_rate`, which calls the divider programming path.

## State and Persistence
The driver keeps only per-device private state in `bsp_priv`. Persistent hardware state is in shared syscon/regmap registers for NSS clock gates/dividers/source selection, GMAC control, and QSGMII PCS/PHY tuning. There is no filesystem or firmware persistence.

## Dependencies and Integration Points
It depends on stmmac platform helpers, Linux clk, regmap/syscon, OF fixed-link parsing, and SoC revision matching. It integrates with `stmmac_pltfr_pm_ops`, `stmmac_dvr_probe()`, and stmmac speed callbacks. The OF binding is `qcom,ipq806x-gmac`.

## Risks and Edge Cases
- `qcom,id` must be 0..3; invalid IDs can shift clock bits into the wrong MAC lane.
- GMAC0 cannot use SGMII, and SGMII setup relies on a valid QSGMII CSR regmap.
- Unsupported speeds return `-EINVAL`; only 10/100/1000 are handled.
- Fixed-link nodes without a `speed` property make PCS speed forcing fail.
- Clock and syscon register writes are shared across NSS MACs, so mask precision matters.

## Test Signals
Useful tests include DT probe with each GMAC id, RGMII and SGMII mode bring-up, fixed-link 10/100/1000 operation, link-speed transitions checking `NSS_COMMON_CLK_DIV0`, suspend/resume through stmmac PM, and negative DT tests for missing syscon phandles, invalid id, unsupported PHY mode, and malformed fixed-link speed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c

## Purpose
`dwmac-loongson.c` is a PCI glue driver for Loongson GMAC/GNET controllers built around Synopsys GMAC cores with Loongson-specific DMA interrupt layout, reset behavior, PCI/OF/ACPI configuration, and optional multi-channel MSI routing.

## Important APIs, Types, and Functions
- `struct loongson_data` records the custom Loongson core ID, multi-channel capability, and device pointer.
- `loongson_default_data()`, `loongson_gmac_data()`, and `loongson_gnet_data()` initialize stmmac platform defaults for GMAC and integrated-GNET variants.
- `loongson_dwmac_dma_init_channel()` and `loongson_dwmac_dma_interrupt()` override DMA ops for Loongson multi-channel cores.
- `loongson_dwmac_setup()` patches `synopsys_id`, installs custom DMA ops, and fills `mac_device_info` link/MII capabilities.
- `loongson_dwmac_msi_config()` maps common, RX, and TX vectors for multi-MSI mode.
- `loongson_dwmac_dt_config()` and `loongson_dwmac_acpi_config()` choose IRQ, MDIO, bus id, and PHY mode depending on firmware interface.

## Control Flow
PCI probe allocates platform data, enables the PCI function, maps BAR0, records the Loongson core version from `GMAC_VERSION`, runs per-device setup from `driver_data`, computes FIFO sizes, then parses either DT or ACPI resources. Multi-channel devices try to allocate per-channel MSI vectors but continue with the common MAC IRQ if allocation fails. Finally `stmmac_dvr_probe()` owns the netdev. Remove reverses stmmac registration, DT MDIO node references, MSI allocation, and PCI enablement.

## State and Persistence
Driver state is per-PCI-device and held in devm allocations plus `plat->bsp_priv`. Hardware state includes DMA bus mode, interrupt masks/status, PCI MSI vectors, and PHY autonegotiation. No persistent storage is used.

## Dependencies and Integration Points
The file depends on PCI, OF IRQ, ACPI fallback through normal PCI IRQs, `stmmac_libpci`, `dwmac1000` DMA ops, GMAC register definitions, and phylib. It integrates with stmmac by providing custom `mac_setup`, `fix_soc_reset`, suspend/resume callbacks, and optional multi-MSI resource arrays.

## Risks and Edge Cases
- Loongson custom IDs `0x10` and `0x12` must be detected before stmmac core setup or the wrong DMA model is selected.
- Multi-channel V1 disables TX checksum offload on channels 1..7 because only channel 0 supports it.
- MSI allocation failures are tolerated but can reduce interrupt isolation and performance.
- The DMA reset can take up to two seconds; missing PHY clock is reported when reset is already stuck.
- GNET speed-up to 1000 Mbps restarts autonegotiation as a hardware workaround.

## Test Signals
Test coverage should include PCI probe/remove for GMAC1, GMAC2, and GNET IDs; DT and ACPI boot paths; multi-channel TX/RX interrupt accounting; MSI fallback; DMA soft reset timeout behavior; and GNET 10/100 to 1000 Mbps renegotiation. `ethtool -S` interrupt counters and traffic across all enabled queues are strong runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c

## Purpose
`dwmac-loongson1.c` provides OF platform glue for Loongson-1B GMAC and Loongson-1C EMAC instances. It programs Loongson syscon bits for MAC shutdown release, pin muxing, and PHY interface selection before handing the device to the generic stmmac platform driver.

## Important APIs, Types, and Functions
- `struct ls1x_dwmac` stores stmmac platform data, syscon regmap, and Loongson-1B MAC id.
- `struct ls1x_data` selects SoC-specific `setup` and `init` callbacks from OF match data.
- `ls1b_dwmac_setup()` infers GMAC0/GMAC1 from the MMIO base address.
- `ls1b_dwmac_syscon_init()` programs LS1B syscon bits for RGMII_ID or MII and releases GMAC shutdown.
- `ls1c_dwmac_syscon_init()` maps stmmac PHY interface selectors into the LS1C `PHY_INTF_SELI` field.
- `ls1x_dwmac_probe()` builds platform data and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe gathers stmmac resources, obtains the `loongson,ls1-syscon` regmap, loads match data, allocates private state, parses stmmac DT configuration, stores `bsp_priv`, and runs optional setup. The stmmac core later invokes the SoC-specific `init` callback to write syscon mode bits and deassert shutdown before normal MAC operation.

## State and Persistence
State is limited to devm private data and syscon register settings. The syscon writes persist until reset or later firmware/kernel changes. The driver has no dynamic runtime state beyond stmmac-owned netdev state.

## Dependencies and Integration Points
It uses syscon/regmap, platform resources, OF match data, stmmac DT parsing, and `stmmac_get_phy_intf_sel()`. Compatible strings are `loongson,ls1b-gmac` and `loongson,ls1c-emac`.

## Risks and Edge Cases
- LS1B id detection is hard-coded to two physical base addresses; unexpected address maps fail probe.
- LS1B supports only `RGMII_ID` and `MII`; LS1C accepts only GMII/MII and RMII selector results.
- GMAC1 shares pins with UART/PWM functions, so syscon mux writes can affect board-level pin use.
- Missing syscon phandle prevents all mode programming.

## Test Signals
Bring-up should verify both LS1B MAC base addresses, LS1C RMII/MII mode selection, syscon shutdown bit clearing, and negative tests for unsupported PHY modes. Network traffic at expected speeds plus scope or register inspection of pin mode bits are useful hardware signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c

## Purpose
`dwmac-lpc18xx.c` is the NXP LPC18xx/LPC43xx Ethernet glue layer. Its only platform-specific job is to program the CREG syscon Ethernet mode field for MII/GMII or RMII before delegating to stmmac.

## Important APIs, Types, and Functions
- `lpc18xx_set_phy_intf_sel()` validates stmmac's abstract PHY selector and writes `LPC18XX_CREG_CREG6_ETHMODE_MASK`.
- `lpc18xx_dwmac_probe()` parses stmmac DT resources, finds the `nxp,lpc1850-creg` syscon, sets `DWMAC_CORE_GMAC`, and installs `set_phy_intf_sel`.

## Control Flow
Probe gets stmmac resources and DT config, looks up the global CREG syscon by compatible string, stores the regmap as `bsp_priv`, and calls `stmmac_dvr_probe()`. The stmmac core calls back to `lpc18xx_set_phy_intf_sel()` when applying the selected PHY interface.

## State and Persistence
The only driver-owned state is a regmap pointer in `bsp_priv`. Hardware state is a small CREG mode field that survives until SoC reset or later syscon writes.

## Dependencies and Integration Points
The file depends on syscon/regmap, OF platform probing, stmmac platform helpers, and the generic stmmac PHY interface selector. Compatible string: `nxp,lpc1850-dwmac`.

## Risks and Edge Cases
- Syscon lookup is by compatible string, so boards must expose the CREG node correctly.
- Only GMII/MII and RMII selector values are accepted.
- Shared syscon access requires the field mask to stay accurate to avoid corrupting adjacent CREG settings.

## Test Signals
Probe tests should cover valid MII and RMII DT modes, missing CREG syscon, and unsupported interface rejection. Runtime signals are successful link-up in each mode and inspection of CREG6 mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c

## Purpose
`dwmac-mediatek.c` is the MediaTek MT2712/MT8195 stmmac glue layer. It handles per-SoC clock lists, PERICFG interface selection, RMII clock-source configuration, MAC-side TX/RX delay programming, safety feature defaults, WOL policy, and clock gating around the generic stmmac core.

## Important APIs, Types, and Functions
- `struct mediatek_dwmac_plat_data` carries variant data, delay settings, clocks, PERICFG regmap, PHY mode, RMII clock flags, and WOL policy.
- `struct mediatek_dwmac_variant` supplies `dwmac_set_phy_interface`, `dwmac_set_delay`, clock list, delay limits, and DMA address width.
- MT2712 and MT8195 have separate `*_set_interface()`, `*_delay_ps2stage()`, `*_delay_stage2ps()`, and `*_set_delay()` implementations.
- `mediatek_dwmac_config_dt()` reads `mediatek,pericfg`, delay properties, clock inversion flags, RMII clock-source flags, and `mediatek,mac-wol`.
- `mediatek_dwmac_clks_config()` gates bulk clocks plus optional `rmii_internal`.
- `mediatek_dwmac_common_data()` fills stmmac flags, queue TBS defaults, safety features, DMA width, and callbacks.

## Control Flow
Probe allocates private data, selects variant from OF match, parses MediaTek-specific DT properties before stmmac DT parsing, initializes clocks, gets stmmac resources, fills common stmmac data, writes interface/delay registers once, enables clocks, and calls `stmmac_dvr_probe()`. Remove unregisters stmmac and disables the same clocks. Resume re-runs interface and delay programming through `plat->resume`.

## State and Persistence
Per-device state lives in `bsp_priv`. Persistent hardware state is in PERICFG interface and delay registers plus enabled clock tree state. The delay fields are temporarily converted from picoseconds to register stages and converted back after programming, so the private structure remains in picoseconds after init.

## Dependencies and Integration Points
The driver depends on syscon/regmap, clk bulk APIs, stmmac DT helpers, stmmac safety feature structures, and OF properties. Compatible strings are `mediatek,mt2712-gmac` and `mediatek,mt8195-gmac`.

## Risks and Edge Cases
- Delay values must be below variant-specific maxima; equality with the max is rejected.
- `clk_prepare_enable(NULL)` for absent `rmii_internal_clk` relies on common clk API tolerance.
- `mediatek_dwmac_common_data()` returns `-ENOMEM`, but probe does not check that return value in the current code path.
- Interface/delay programming errors from the initial `mediatek_dwmac_init()` call are not checked in probe.
- RMII delay semantics differ depending on whether the MAC or PHY provides the reference clock.

## Test Signals
Tests should validate MT2712 and MT8195 RGMII/MII/RMII combinations, delay rounding and inversion bits, invalid delay rejection, RMII internal-clock and external RXC/TXC cases, MAC-vs-PHY WOL behavior, clock disable on probe failure/remove, and TBS enablement on queues above TXQ0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c

## Purpose
`dwmac-meson.c` is the older Amlogic Meson6/Meson8 stmmac glue layer. It programs a single auxiliary register bit to distinguish 10 Mbps from 100 Mbps operation.

## Important APIs, Types, and Functions
- `struct meson_dwmac` stores the device and a mapped control register.
- `meson6_dwmac_set_clk_tx_rate()` sets or clears `ETHMAC_SPEED_100` for SPEED_100 or SPEED_10.
- `meson6_dwmac_probe()` maps the second MMIO resource, installs the speed callback, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe parses standard stmmac resources and DT config, allocates private data, maps resource index 1 for the Meson control register, assigns `bsp_priv` and `set_clk_tx_rate`, then lets stmmac register the netdev. Link-speed changes call back into the register update path.

## State and Persistence
The only persistent hardware state is the speed bit in the auxiliary Meson register. The driver does not track the current speed separately and does not allocate runtime resources beyond devm memory and MMIO mapping.

## Dependencies and Integration Points
It uses stmmac platform probing, MMIO read/write helpers, and ethtool speed constants. Compatible string: `amlogic,meson6-dwmac`.

## Risks and Edge Cases
- SPEED_1000 is ignored rather than rejected, matching the register's 10/100 role but relying on platform capability constraints elsewhere.
- The second MMIO resource must be present.
- There is no locking around the read-modify-write, so it assumes no other agent mutates the same register concurrently.

## Test Signals
Run 10 and 100 Mbps link tests and confirm `ETHMAC_SPEED_100` transitions. Probe should fail cleanly when the second resource is absent. Regression coverage should verify stmmac still handles unsupported gigabit modes outside this glue callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c

## Purpose
`dwmac-meson8b.c` supports Amlogic Meson8b/Meson8m2/GXBB/AXG/G12A DWMAC variants. It creates a small clock tree for the RGMII TX clock, selects RGMII/RMII mode, programs TX/RX internal delays, and enables the PHY reference clock generator.

## Important APIs, Types, and Functions
- `struct meson8b_dwmac_data` selects mode programming and whether PRG_ETH1 has fine RGMII RX delay support.
- `struct meson8b_dwmac` stores MMIO registers, PHY mode, TX/RX delay values, RGMII TX clock, and optional timing-adjustment clock.
- `meson8b_init_rgmii_tx_clk()` registers mux, divider, fixed-factor, and gate clocks backed by PRG_ETH0 fields.
- `meson8b_set_phy_mode()` and `meson_axg_set_phy_mode()` program old and newer PHY mode fields.
- `meson8b_init_rgmii_delays()` validates and writes TX delay, optional RX retiming, and PRG_ETH1 RX clock delay.
- `meson8b_init_prg_eth()` enables RGMII clocking or RMII clock inversion and turns on the TX/PHY ref generator.

## Control Flow
Probe parses stmmac DT data, maps resource index 1, reads delay properties with legacy fallback, validates delay ranges based on variant, gets optional timing-adjustment clock, initializes delay registers, registers the synthetic RGMII TX clock, applies the PHY mode, initializes PRG_ETH clocking, stores `bsp_priv`, and calls `stmmac_dvr_probe()`.

## State and Persistence
State is per-device devm memory and registered clock hardware. Persistent hardware state is in PRG_ETH0/PRG_ETH1 mode, delay, clock mux/divider/gate, RMII inversion, and ref-clock enable bits. Devm actions disable prepared clocks on detach or probe failure.

## Dependencies and Integration Points
The driver depends on Linux common clock provider primitives, stmmac platform helpers, OF properties, and MMIO. Compatible strings include `amlogic,meson8b-dwmac`, `meson8m2`, `meson-gxbb`, `meson-axg`, and `meson-g12a`.

## Risks and Edge Cases
- G12A RX delay must be 0..3000 ps in 200 ps steps; older variants allow only 0 or 2000 ps.
- RX retiming on older variants requires the `timing-adjustment` clock.
- TX delay is encoded as `ns >> 1`, so odd nanosecond inputs are truncated.
- Clock registration uses device-name-derived names and depends on firmware clock parents.

## Test Signals
Test each compatible with RGMII, RGMII_ID/RXID/TXID, and RMII; validate delay property bounds; confirm generated clock rates and gate state; and run link-speed changes to ensure the RGMII TX clock remains functional. Probe-failure tests should cover missing timing-adjustment clock when RX retiming is requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c

## Purpose
`dwmac-motorcomm.c` is a PCI glue driver for Motorcomm YT6801-style DWMAC controllers. It initializes vendor management registers, resets the internal PHY/MDIO block, reads the MAC address from eFuse patch rows, configures MSI/MSI-X interrupts, and presents a GMAC4 stmmac platform device.

## Important APIs, Types, and Functions
- `struct dwmac_motorcomm_priv` stores the BAR0 base used for vendor and GMAC registers.
- eFuse helpers read byte rows, scan patch entries, and extract `MACA0LR/MACA0HR` into `res.mac`.
- `motorcomm_reset()` toggles `SYS_RESET_RESET` and deasserts internal MDIO/PHY reset.
- `motorcomm_init()` disables management interrupt routing, programs RX/TX interrupt moderation, and disables out-of-band WOL during normal operation.
- `motorcomm_default_plat_data()` creates stmmac defaults for DMA, AXI, checksumming, TSO, EEE/LPI, GMAC4, and PCI PM callbacks.
- `motorcomm_setup_irq()` prefers six MSI-X vectors and falls back to one MSI vector.

## Control Flow
PCI probe allocates private and platform data, enables and maps BAR0, disables PCIe L1 ASPM for interrupt reliability, resets the vendor block, waits for eFuse load, reads or randomizes the MAC address, sets up interrupts, initializes vendor registers, offsets stmmac MMIO by `GMAC_OFFSET`, and calls `stmmac_dvr_probe()`. Resume first runs generic PCI stmmac resume, then deasserts PHY reset and reinitializes vendor registers.

## State and Persistence
Runtime state is private BAR mapping plus stmmac platform data. Hardware state includes reset state, eFuse controller operation, interrupt moderation, OOB WOL disablement, PCI IRQ vectors, and MAC address resource data. eFuse is persistent hardware storage but the driver only reads it.

## Dependencies and Integration Points
The file depends on PCI, MSI/MSI-X APIs, iopoll, stmmac PCI helpers, GMAC4/DMA constants, and Ethernet address helpers. PCI IDs are vendor `0x1f0a`, device `0x6801`.

## Risks and Edge Cases
- eFuse reads need a post-reset delay; without it reads can return zeros.
- `motorcomm_efuse_read_byte()` writes `*byte` even if polling times out, so callers must respect the return code.
- No valid eFuse MAC falls back to a random MAC address.
- ASPM L1 is disabled unconditionally due to card-specific MSI delivery failures.
- MSI-X vector positions are assumed by the hardware mapping.

## Test Signals
PCI probe should be tested with valid eFuse MAC, empty eFuse, and eFuse timeout/error. Interrupt tests should exercise MSI-X and forced MSI fallback. Suspend/resume should verify DMA interrupts still arrive after D3hot. Traffic tests should check checksum/TSO, EEE/LPI behavior, and MAC address stability across reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c

## Purpose
`dwmac-nuvoton.c` is the Nuvoton MA35D1 DWMAC glue layer. It programs a syscon MISCR register for MAC0 or MAC1 to select RGMII/RMII mode and optional internal TX/RX delays.

## Important APIs, Types, and Functions
- `struct nvt_priv_data` stores device, syscon regmap, and MAC id.
- `nvt_gmac_get_delay()` reads delay properties in picoseconds and converts 0..2000 ps into a 4-bit register code.
- `nvt_set_phy_intf_sel()` writes RGMII delay fields or the RMII enable bit based on stmmac's PHY selector.
- `nvt_gmac_probe()` parses stmmac resources, resolves `nuvoton,sys` phandle arguments, validates MAC id, installs `set_phy_intf_sel`, and probes stmmac.

## Control Flow
Probe gets platform resources and stmmac DT data, allocates private state, looks up a syscon phandle with one argument for the MAC id, rejects ids above 1, stores the private state in `bsp_priv`, and calls `stmmac_pltfr_probe()`. The interface callback later programs `NVT_REG_SYS_GMAC0MISCR` or `NVT_REG_SYS_GMAC1MISCR`.

## State and Persistence
The driver persists mode and delay state only in Nuvoton syscon registers. Private data is devm-allocated per device. It has no runtime worker state or storage.

## Dependencies and Integration Points
It depends on syscon/regmap phandle arguments, stmmac platform probing, OF delay properties, and generic PHY interface selectors. Compatible string: `nuvoton,ma35d1-dwmac`.

## Risks and Edge Cases
- Delay inputs above 2000 ps are rejected; other values are rounded down by integer division except exactly 2000 ps mapping to 15.
- Only RGMII and RMII selector values are valid.
- Incorrect `nuvoton,sys` MAC id writes the wrong MISCR register.

## Test Signals
Validate MAC0 and MAC1 DT instances, RGMII delay codes for 0, intermediate, and 2000 ps, RMII mode bit setting, invalid delay rejection, invalid MAC id rejection, and successful traffic in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c

## Purpose
`dwmac-qcom-ethqos.c` is the Qualcomm ETHQOS glue driver for GMAC4-based SoCs. It configures RGMII IO macro registers, SGMII/2500BASE-X helper state, link clocks, optional SerDes PHY power, variant-specific register layouts, PTP clock rate, and queue features before binding the stmmac core.

## Important APIs, Types, and Functions
- `struct ethqos_emac_driver_data` describes reset defaults, loopback quirks, DMA width, link clock name, GMAC4 address layout, and SGMII loopback requirements.
- `struct qcom_ethqos` stores RGMII MMIO base, link clock, optional SerDes PHY, PHY mode, and selected variant flags.
- `ethqos_set_clk_tx_rate()` sets the link clock to twice the RGMII line clock.
- `ethqos_fix_mac_speed_rgmii()` restores POR values, initializes DLLs, waits for lock, and programs speed-specific RGMII macro fields.
- `ethqos_fix_mac_speed_sgmii()` handles SGMII clock divider and PCS in-band autonegotiation.
- `qcom_ethqos_serdes_powerup/powerdown()` and `ethqos_mac_finish_serdes()` integrate optional PHY framework SerDes control.
- `qcom_ethqos_probe()` assembles stmmac platform data and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe parses stmmac resources/DT, selects a speed-fix callback based on PHY mode, maps the named `rgmii` resource, loads variant data, obtains and enables the link clock, gets optional SerDes, pre-sets 1000 Mbps RGMII clocking and functional clock bits, then fills stmmac parameters such as CSR clock range, debug dump callback, PTP clock configuration, GMAC4 address offsets, PMT, TSO, DMA width, SerDes hooks, and per-queue TBS. Link changes invoke either the RGMII macro reinitialization path or the SGMII in-band path.

## State and Persistence
Per-device state is devm-managed. Hardware state includes RGMII IO macro registers, DLL configuration and lock state, SGMII loopback bit, link clock rate, SerDes power/mode, PCS autonegotiation, and optional PTP reference clock rate. No storage is persisted outside hardware registers.

## Dependencies and Integration Points
The driver depends on stmmac GMAC4 support, clk APIs, PHY framework, OF match data, phylink/PCS control through stmmac, and platform MMIO resources. Compatible strings include `qcom,qcs404-ethqos`, `qcom,sa8775p-ethqos`, `qcom,sc8280xp-ethqos`, and `qcom,sm8150-ethqos`.

## Risks and Edge Cases
- RGMII DLL lock polling logs errors but continues, so later link failures may be timing-related.
- `of_device_get_match_data()` is assumed non-NULL.
- SGMII loopback is conditionally required for some 2500BASE-X variants during clock enable.
- Different EMAC versions use different register defaults and address maps; wrong compatible can corrupt configuration.
- RGMII TX delay phase shift depends on whether PHY mode says the PHY supplies delay.

## Test Signals
Test RGMII 10/100/1000 on every compatible, SGMII and 2500BASE-X with SerDes mode setting, PTP clock rate update, suspend/resume clock re-enable, TSO/TBS queue behavior, and debug register dumps. Negative tests should cover unsupported PHY mode, missing `rgmii` resource, missing link clock, SerDes probe defer, and DLL timeout observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c

## Purpose
`dwmac-renesas-gbeth.c` is the Renesas GBETH/GMAC glue layer for RZ/V and RZ/G class SoCs. It supplies variant clock lists, optional reset ownership, TX clock rate callback, hardware timestamp flags, optional MIIC PCS creation, and stmmac init/exit hooks.

## Important APIs, Types, and Functions
- `struct renesas_gbeth_of_data` defines clock names, stmmac flags, reset handling, TX clock policy, and PCS presence.
- `struct renesas_gbeth` stores match data, platform data, reset control, and device pointer.
- `renesas_gmac_pcs_init/exit/select_pcs()` create and expose a MIIC phylink PCS from `pcs-handle`.
- `renesas_gbeth_init()` deasserts reset and enables bulk clocks.
- `renesas_gbeth_exit()` disables clocks and reasserts reset.
- `renesas_gbeth_probe()` allocates state, obtains clocks/reset, configures stmmac callbacks, and probes stmmac.

## Control Flow
Probe parses stmmac resources and DT data, allocates `renesas_gbeth`, builds the bulk clock array from match data, obtains the TX clock, optionally gets an exclusive reset, fills `bsp_priv`, optional `set_clk_tx_rate`, init/exit, low-power/TX LPI and timestamp flags, and optional PCS hooks. `devm_stmmac_pltfr_probe()` then invokes the stmmac lifecycle. Init deasserts reset before enabling clocks and asserts reset if clock enable fails.

## State and Persistence
State is devm-managed per device. Hardware state includes clock enable counts, reset line state, stmmac MAC registers, and optional MIIC PCS object lifetime. There is no persistent file-backed state.

## Dependencies and Integration Points
It depends on clk bulk APIs, reset controls, MIIC PCS helpers, OF phandles, and stmmac platform helpers. Compatible strings are `renesas,r9a08g046-gbeth`, `renesas,r9a09g077-gbeth`, and `renesas,rzv2h-gbeth`.

## Risks and Edge Cases
- Variant clock names differ: GBETH expects `tx`, `tx-180`, `rx`, `rx-180`; GMAC expects only `tx`.
- Reset handling is variant-specific; using the wrong compatible can leave reset ownership mismatched.
- Missing `tx` clock fails probe even when other clocks exist.
- PCS creation is optional and depends on `pcs-handle`.

## Test Signals
Run probe/remove and suspend/resume on each compatible, validate reset and clock sequencing, check TX clock rate changes where enabled, verify MIIC PCS attach/detach with SGMII-like links, and confirm hardware timestamp latency flags do not regress PTP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c

## Purpose
`dwmac-rk.c` is the Rockchip stmmac glue layer for a wide range of PX/RK/RV SoCs. It abstracts per-SoC GRF/PHP-GRF register layouts behind an ops table, handles RGMII/RMII interface selection, TX/RX delay programming, MAC clock routing and speed changes, PHY regulator/reset control, integrated PHY power sequencing, runtime PM, and stmmac lifecycle callbacks.

## Important APIs, Types, and Functions
- `struct rk_gmac_ops` contains SoC-specific init, RGMII/RMII programming, speed programming, integrated PHY power hooks, GRF register/mask metadata, supported interface flags, and optional MMIO base lists for instance id detection.
- `struct rk_priv_data` stores selected ops, interface, id, regulator, clocks, PHY reset, delays, GRF/PHP-GRF regmaps, and resolved register fields.
- `rk_encode_wm16()` builds Rockchip write-mask register values.
- `rk_gmac_setup()` parses `clock_in_out`, `tx_delay`, `rx_delay`, `rockchip,grf`, optional `rockchip,php-grf`, integrated PHY status, and runs ops init.
- `rk_gmac_powerup()` enables clocks, writes interface/mode bits, applies delay programming, enables PHY supply, runtime PM, and integrated PHY powerup.
- `rk_set_clk_tx_rate()` updates CRU clock rates and GRF speed selectors for RGMII/RMII.
- `rk_gmac_probe()` sets stmmac callbacks and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe selects `rk_gmac_ops` by compatible, parses stmmac DT data, normalizes core type/FIFO defaults, installs interface, clock, init/exit, suspend/resume callbacks, creates private Rockchip state, initializes clocks, and lets stmmac probe. The stmmac init path calls `rk_gmac_powerup()`. Suspend powers down unless wakeup is enabled; resume powers back up; exit powers down, releases optional PHY clock and reset handle. Link speed changes call the Rockchip clock-rate callback.

## State and Persistence
Private state is per-device. Hardware state spans GRF/PHP-GRF interface and clock registers, delay registers, RMII gates, CRU clocks, optional PHY clocks, regulators, reset controls, and runtime PM state. Delay defaults are stored in private memory and applied at each power-up.

## Dependencies and Integration Points
The driver depends on syscon/regmap, clk bulk APIs, regulators, reset controls, runtime PM, OF properties, stmmac platform helpers, and phylib interface helpers. It supports many compatible strings from `rockchip,px30-gmac` through `rockchip,rk3588-gmac` and `rockchip,rv1126-gmac`.

## Risks and Edge Cases
- SoC instance id detection relies on exact MMIO base addresses for variants with multiple MACs.
- Missing or misspelled `clock_in_out` defaults to input from PHY.
- Missing delay properties produce fallback hex delays and log errors, which can mask board-timing issues.
- `gmac_clk_enable()` does not unwind bulk clocks if enabling `clk_phy` fails.
- Some variants require PHP-GRF; missing phandle fails probe.
- Interface support is per-variant, and unsupported modes fail during init rather than early DT parse.

## Test Signals
Coverage should include each compatible's RGMII/RMII support matrix, multiple-instance id mapping, clock input/output routing, 10/100/1000 speed selector writes, integrated PHY reset/power sequencing, regulator failure handling, wake-on-LAN suspend behavior, and runtime PM balancing. Hardware tests should inspect GRF writes and run traffic after repeated suspend/resume and link-speed changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c

## Purpose
`dwmac-rzn1.c` is a small Renesas RZ/N1 glue layer that adds optional MIIC PCS support to a standard stmmac platform device.

## Important APIs, Types, and Functions
- `rzn1_dwmac_pcs_init()` parses `pcs-handle`, creates a MIIC PCS with `miic_create()`, and stores it in `priv->hw->phylink_pcs`.
- `rzn1_dwmac_pcs_exit()` destroys the MIIC PCS.
- `rzn1_dwmac_select_pcs()` returns the stored PCS to phylink.
- `rzn1_dwmac_probe()` installs PCS callbacks and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac resources and DT platform data, stores `plat_dat` as `bsp_priv`, assigns PCS init/exit/select callbacks, and registers stmmac. During stmmac MAC setup, the PCS init callback creates the MIIC PCS if the DT phandle exists.

## State and Persistence
The only extra runtime state is the phylink PCS pointer owned through the stmmac hardware structure. There are no persistent syscon settings or file-backed state.

## Dependencies and Integration Points
It depends on OF phandles, `pcs-rzn1-miic`, phylink PCS interfaces, and stmmac platform helpers. Compatible string: `renesas,rzn1-gmac`.

## Risks and Edge Cases
- PCS is optional; missing `pcs-handle` leaves stmmac without a PCS.
- PCS lifetime is tied to stmmac callbacks, so double-destroy or missing exit would affect phylink cleanup.
- Probe uses non-devm `stmmac_dvr_probe()` with `stmmac_pltfr_remove()`.

## Test Signals
Test probe with and without `pcs-handle`, PCS creation failure propagation, phylink mode selection, and traffic over interfaces requiring MIIC PCS. Remove/unbind should verify `miic_destroy()` is called once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c

## Purpose
`dwmac-s32.c` is the NXP S32G/R common chassis GMAC glue driver. It sets up TX/RX interface clocks, writes the SoC PHY interface selection register, enables GMAC4 platform features, configures FIFO sizes, and selects multi-IRQ mode when all per-queue IRQs are present.

## Important APIs, Types, and Functions
- `struct s32_priv_data` stores MAC/control MMIO, optional syscon regmap, clock handles, device pointer, and pointer to stmmac PHY mode.
- `s32_gmac_write_phy_intf_select()` writes the PHY select register or syscon offset.
- `s32_gmac_init()` enables TX/RX clocks, sets both to 125 MHz, and writes interface mode.
- `s32_gmac_exit()` disables both clocks.
- `s32_gmac_setup_multi_irq()` validates per-RX/TX queue IRQ arrays and sets `STMMAC_FLAG_MULTI_MSI_EN`.
- `s32_dwmac_probe()` parses resources, clocks, optional `nxp,phy-sel`, stmmac flags, FIFO sizes, and callbacks.

## Control Flow
Probe allocates private state, gathers resources and stmmac DT config, obtains PHY select access via syscon phandle or second MMIO resource, gets TX/RX clocks, configures GMAC4/PMT/SPH-disable platform data, selects multi-IRQ if all queue IRQs are valid, sets large FIFOs, installs init/exit and TX clock callback, and calls `stmmac_pltfr_probe()`. Init performs clock and PHY-select programming before MAC use.

## State and Persistence
State is per-device private data. Hardware state includes clock rates/enables, interface selection register, interrupt routing mode, and stmmac registers. No persistent storage is used.

## Dependencies and Integration Points
It uses clk APIs, syscon/regmap or MMIO resource fallback, stmmac GMAC4 platform helpers, queue IRQ resources, and `stmmac_set_clk_tx_rate()`. Compatible string: `nxp,s32g2-dwmac`.

## Risks and Edge Cases
- `s32_gmac_write_phy_intf_select()` currently always writes RGMII selector despite constants for other modes.
- All TX and RX queue IRQs must be present to enable multi-IRQ; one missing IRQ falls back to MAC IRQ mode.
- Clock enable error unwinding must keep TX/RX enable counts balanced.
- Missing `nxp,phy-sel` requires a valid second MMIO region.

## Test Signals
Tests should cover syscon and MMIO PHY-select access, missing queue IRQ fallback, all-queue multi-IRQ mode, clock set-rate failures, probe deferral for clocks/syscon, and traffic with per-queue interrupts enabled. Register inspection should confirm the 125 MHz clock setup and PHY select value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c

## Purpose
`dwmac-socfpga.c` is the Altera/Intel SoCFPGA stmmac glue layer. It programs system-manager PHY mode bits under reset, supports optional FPGA EMAC splitter and GMII-to-SGMII adapter blocks, creates a Lynx PCS over an MMIO-backed MDIO regmap, and adds Agilex5 XGMAC/PTP cross-timestamp support.

## Important APIs, Types, and Functions
- `struct socfpga_dwmac_ops` selects Gen5, Gen10, or Agilex5 PHY-mode and platform setup behavior.
- `struct socfpga_dwmac` stores sysmgr offset/shift, stmmac platform data, resets, optional splitter/TSE PCS/SGMII adapter mappings, F2H PTP clock flag, and ops.
- `socfpga_dwmac_parse_data()` reads `altr,sysmgr-syscon`, optional splitter and converter phandles, and maps auxiliary resources.
- `socfpga_gen5_set_phy_mode()` and `socfpga_gen10_set_phy_mode()` assert resets, update sysmgr PHY/PTP/F2H bits, then deassert resets.
- `socfpga_dwmac_fix_mac_speed()` updates splitter speed and toggles SGMII adapter enable around changes.
- `socfpga_dwmac_pcs_init()` creates a regmap MDIO bus and Lynx PCS when TSE PCS MMIO is present.
- `smtg_crosststamp()` implements Agilex5 hardware cross-timestamping using internal snapshot and SMTG MDIO time.

## Control Flow
Probe selects ops, gets stmmac resources and DT config, allocates private state, obtains optional OCP reset and deasserts it, parses sysmgr/auxiliary data, stores the stmmac reset handle for later mode changes, assigns stmmac fix-speed/init/PCS callbacks, applies variant platform setup, and calls `devm_stmmac_pltfr_probe()`. Stmmac init calls the selected PHY-mode writer; link changes update splitter/adapter state.

## State and Persistence
Private state is devm-managed. Persistent hardware state includes sysmgr PHY selection, FPGA interface enable bits, PTP reference clock selection, reset line state, splitter speed, SGMII adapter enable, PCS registers, and PTP auxiliary timestamp configuration. Cross-timestamping uses stmmac locks and MMIO/MDIO reads but no storage.

## Dependencies and Integration Points
The driver depends on Altera sysmgr regmap helpers, reset controls, stmmac GMAC/XGMAC/PTP internals, MDIO regmap, Lynx PCS, phylink, and ARM architectural counter IDs. Compatible strings are `altr,socfpga-stmmac`, `altr,socfpga-stmmac-a10-s10`, and `altr,socfpga-stmmac-agilex5`.

## Risks and Edge Cases
- The driver must own resets while changing PHY mode; reset sequencing errors can leave the MAC sampling stale mode bits.
- Splitter presence forces MAC-side GMII/MII selection even when the external PHY mode differs.
- SGMII adapter resources are optional and identified by `reg-names`; missing names silently skip related support.
- Cross-timestamping rejects concurrent external snapshot use and assumes SMTG MDIO reads succeed.
- Agilex5 enables TBS only on queues 6 and 7 for 7/8 queue configurations.

## Test Signals
Test Gen5 and Gen10 sysmgr writes for RGMII/RMII/SGMII/1000BASE-X, splitter speed changes at 10/100/1000, SGMII adapter toggling, PCS creation over TSE control port, reset assert/deassert ordering, Agilex5 XGMAC setup, TSO/TBS queue flags, and PTP cross-timestamp ioctl behavior including `-EBUSY` when external snapshots are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c

## Purpose
`dwmac-sophgo.c` is the Sophgo SG2042/SG2044 platform glue layer. It enables the TX clock, applies stmmac feature flags, configures TX clock rate handling, and accounts for SG2042 internal RX delay by adjusting the advertised PHY interface mode.

## Important APIs, Types, and Functions
- `struct sophgo_dwmac_data` records whether a compatible has internal RX delay.
- `sophgo_sg2044_dwmac_init()` gets the `tx` clock, disables SPH, installs generic `stmmac_set_clk_tx_rate`, and disables multicast hash bins.
- `sophgo_dwmac_probe()` parses resources/DT, runs common initialization, adjusts PHY mode with `phy_fix_phy_mode_for_mac_delays()` when needed, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac resources and DT data, initializes TX clock and platform flags, obtains match data, optionally rewrites the PHY interface to reflect MAC-provided RX delay, then registers stmmac. Remove uses the generic stmmac platform remove path.

## State and Persistence
The file holds no custom private state. Persistent hardware state is limited to enabled clock state and stmmac-programmed registers. PHY mode adjustment is stored in `plat_dat`.

## Dependencies and Integration Points
It depends on clk APIs, device properties, stmmac platform helpers, and PHY mode delay helpers. Compatible strings are `sophgo,sg2042-dwmac` and `sophgo,sg2044-dwmac`.

## Risks and Edge Cases
- `sophgo_sg2044_dwmac_init()` is used for both compatibles despite its name.
- `phy_fix_phy_mode_for_mac_delays()` can return `PHY_INTERFACE_MODE_NA`, causing probe failure for incompatible delay combinations.
- Multicast filter bins are forced to zero, affecting filtering behavior.

## Test Signals
Test SG2042 RGMII mode combinations with internal RX delay translation, SG2044 without translation, TX clock rate changes across link speeds, multicast filtering behavior, and probe failures for unsupported adjusted PHY modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c

## Purpose
`dwmac-spacemit.c` is the Spacemit K3 DWMAC glue layer. It uses an APMU syscon to configure MII/RMII/RGMII selection, RGMII TX/RX delay lines, and wake IRQ enablement, while exposing the supported PHY interfaces to stmmac.

## Important APIs, Types, and Functions
- `struct spacmit_dwmac` stores the APMU regmap and control/delay register offsets.
- `spacemit_dwmac_detected_delay_value()` converts requested picosecond delay into a K3 delay-line code.
- `spacemit_dwmac_set_delay()` writes TX/RX delay-line enable, step, and code fields.
- `spacemit_dwmac_update_irq_config()` enables wake IRQ routing when `stmmac_res.wol_irq` is valid.
- `spacemit_get_interfaces()` advertises MII, RMII, and all RGMII variants.
- `spacemit_set_phy_intf_sel()` writes APMU interface mode bits.
- `spacemit_dwmac_probe()` resolves clocks, syscon offsets, delays, callbacks, and registers stmmac.

## Control Flow
Probe gets stmmac resources, allocates private data, parses stmmac DT, enables the `tx` clock, looks up `spacemit,apmu` with two register offsets, programs wake IRQ enablement, reads optional internal delay properties, installs interface callbacks and private data, programs delay lines, and calls `stmmac_dvr_probe()`.

## State and Persistence
State is private regmap/offset data. Hardware state includes APMU control bits, wake IRQ enable, and RGMII delay-line codes. Clock enable is devm-managed through `devm_clk_get_enabled()`.

## Dependencies and Integration Points
The driver depends on syscon/regmap phandle arguments, clk APIs, stmmac platform helpers, OF delay properties, and generic interface selectors. Compatible string: `spacemit,k3-dwmac`.

## Risks and Edge Cases
- Delay values above 2800 ps are rejected; conversion uses a K3-specific 0.9 factor and rounding.
- There is no explicit check that computed codes fit the 8-bit delay fields, though the max delay is intended to keep them valid.
- Wake IRQ enablement depends on stmmac resource parsing setting `wol_irq >= 0`.
- The struct name is misspelled `spacmit_dwmac`, which is harmless but easy to propagate.

## Test Signals
Validate MII/RMII/RGMII selection writes, delay conversion for 0 and near-maximum values, invalid delay rejection, wake IRQ routing with and without WOL IRQ, TX clock enable probe deferral, and traffic across all advertised PHY modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c

## Purpose
`dwmac-starfive.c` is the StarFive JH7100/JH7110 DWMAC platform glue layer. It enables TX/GTX clocks, selects RGMII or RMII mode through a syscon phandle, optionally programs a JH7100 GTX clock delay chain, and configures stmmac DMA/cache and low-power flags.

## Important APIs, Types, and Functions
- `struct starfive_dwmac_data` stores optional GTX delay-chain value.
- `struct starfive_dwmac` stores device and match data.
- `starfive_dwmac_set_mode()` maps stmmac PHY mode to syscon field bits and writes optional `JH7100_SYSMAIN_REGISTER49_DLYCHAIN`.
- `starfive_dwmac_probe()` gets resources, parses stmmac DT, enables `tx` and `gtx` clocks, selects TX clock-rate callback policy, sets flags, and probes stmmac.

## Control Flow
Probe prepares stmmac data, allocates private state, enables required clocks, conditionally installs `stmmac_set_clk_tx_rate` unless `starfive,tx-use-rgmii-clk` says the external RGMII clock is used, sets low-power and DMA cache flags, programs syscon mode/delay, and calls `stmmac_dvr_probe()`.

## State and Persistence
Private state is devm-managed. Hardware state includes syscon interface selection, optional JH7100 delay-chain register, enabled clocks, and stmmac DMA/cache settings.

## Dependencies and Integration Points
It depends on syscon/regmap phandle arguments, clk APIs, stmmac platform helpers, and device properties. Compatible strings are `starfive,jh7100-dwmac` and `starfive,jh7110-dwmac`.

## Risks and Edge Cases
- Only RGMII and RMII selector values are accepted.
- `starfive,syscon` must provide offset and shift arguments.
- TX clock rate programming depends on the board-level `starfive,tx-use-rgmii-clk` property.
- JH7100 delay-chain programming is unconditional for that match data.

## Test Signals
Test JH7100 and JH7110 DTs, RGMII/RMII mode selection, external-vs-internal TX clock property behavior, GTX delay-chain write on JH7100, and traffic after speed transitions with and without `set_clk_tx_rate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c

## Purpose
`dwmac-sti.c` is the STMicroelectronics STiH407/STiH410 stmmac glue layer. It programs syscfg PHY interface bits, enables the GMAC glue block, selects MII enable polarity, and retimes TX clocks based on PHY mode, link speed, and clock-source DT properties.

## Important APIs, Types, and Functions
- `struct sti_dwmac` stores interface mode, external PHY clock flag, retime source, PHY clock, syscfg register offset, regmap, enable flag, current speed, and retime callback.
- `stih4xx_fix_retime_src()` chooses TXCLK, CLK_125, PHYCLK, or clock generator and may set `sti-ethclk` rate.
- `sti_set_phy_intf_sel()` writes GMAC enable, PHY selector, ENMII, and then retime source.
- `sti_dwmac_parse_data()` reads `st,syscon`, `st,gmac_en`, `st,ext-phyclk`, `st,tx-retime-src`, optional `sti-clkconf`, and `sti-ethclk`.
- `sti_dwmac_init/exit()` prepare and disable the PHY clock.
- `sti_dwmac_probe()` installs stmmac callbacks and probes.

## Control Flow
Probe selects match data, obtains stmmac resources and DT config, allocates private state, parses syscfg and clock settings, assigns the retime callback, installs `set_phy_intf_sel`, `fix_mac_speed`, init, and exit callbacks, then calls `devm_stmmac_pltfr_probe()`. Interface selection and link-speed changes both feed retime source programming.

## State and Persistence
Driver state is per-device. Hardware state is stored in syscfg control bits and the optional PHY clock rate/enable count. The private `speed` default is used for initial retiming before real link speed updates.

## Dependencies and Integration Points
It depends on syscon/regmap, clk APIs, stmmac platform probing, OF properties, and generic PHY selectors. Compatible string: `st,stih407-dwmac`.

## Risks and Edge Cases
- Unsupported selector values are silently coerced to GMII/MII in `sti_set_phy_intf_sel()`.
- Missing `sti-ethclk` only warns; clock-generator retiming may later call `clk_set_rate()` on NULL.
- Retiming choices are tightly coupled to board clock topology and `st,tx-retime-src`.
- The optional `sti-clkconf` resource is parsed but not otherwise used in this file.

## Test Signals
Test MII, GMII/RGMII, and RMII modes with external and internal clock sources; verify 10/100/1000 retime source transitions; inspect syscfg bits; exercise missing optional clock behavior; and run suspend/resume to confirm init/exit clock balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c

## Purpose
`dwmac-stm32.c` is the STM32 MCU/MP1/MP13/MP25 stmmac glue layer. It selects Ethernet PHY mode in SYSCFG, validates and enables clock sources, handles low-power stop clocks and wake IRQs, and provides suspend/resume clock sequencing for STM32 variants.

## Important APIs, Types, and Functions
- `struct stm32_dwmac` stores TX/RX/ETH/syscfg/stop clocks, PHY clock-source flags, wake IRQ, SYSCFG register/mask, speed, ops, and device.
- `struct stm32_ops` selects mode programming, suspend/resume hooks, extra parsing, and variant flags.
- `stm32_dwmac_clk_enable()` and `stm32_dwmac_clk_disable()` manage TX/RX/syscfg/ETH clocks.
- `stm32mp1_select_ethck_external()` and `stm32mp1_validate_ethck_rate()` decide and validate ETH_CK use.
- `stm32mp1_configure_pmcr()` and `stm32mp2_configure_syscfg()` write MP1/MP2 syscfg mode bits.
- `stm32mcu_set_mode()` programs MCU MII/RMII selection.
- `stm32mp1_parse_data()` reads clock-source properties, optional wake IRQ, and low-power clocks.
- `stm32_dwmac_probe/remove()` manage stmmac lifecycle and extra suspend RX clock enable.

## Control Flow
Probe obtains resources and stmmac DT data, selects variant ops, parses required TX/RX clocks and variant-specific data, stores private state, installs suspend/resume callbacks, runs initial mode selection and clock enable, optionally enables RX clock a second time for suspend retention, then registers stmmac. Remove unregisters stmmac, balances the extra RX clock, disables clocks, and clears wake IRQ setup. Suspend disables normal clocks then enables ETH stop clock for MP variants; resume disables stop clock and reruns init.

## State and Persistence
Private state is per-device. Hardware state includes SYSCFG mode registers, PMCCLRR clear writes on MP1, clock enable counts, optional wake IRQ registration, and device wakeup enablement. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on clk APIs, syscon/regmap phandle arguments, PM wake IRQ helpers, stmmac platform PM, OF properties, and generic PHY selectors. Compatible strings include `st,stm32-dwmac`, `st,stm32mp1-dwmac`, `st,stm32mp13-dwmac`, and `st,stm32mp25-dwmac`.

## Risks and Edge Cases
- ETH_CK frequency must match PHY mode when enabled; invalid board clocks fail init.
- MP13 requires a syscfg mask in DT; older MP1 can default it.
- Wake IRQ setup is conditional on no `eth-ck` clock and can leave wake disabled by default.
- Clock enable/disable order must balance the extra RX suspend reference.
- MP2 uses a different full-width ETHCR mask and always selects PTP clock from RCC.

## Test Signals
Test MCU MII/RMII and MP MII/GMII/RGMII/RMII modes, ETH_CK 25/50/125 MHz validation, syscfg clear/set writes, wake IRQ registration and wake enable toggling, suspend/resume in low-power stop, remove path clock balancing, and probe failure for missing required clocks or invalid syscfg masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c

## Purpose
`dwmac-sun55i.c` is the Allwinner sun55i A523 GMAC200 glue layer. It programs a syscon register for MII/RGMII/RMII mode and internal delay values, enables the MBUS clock and optional PHY regulator, sets GMAC200 platform flags, and delegates to stmmac.

## Important APIs, Types, and Functions
- `sun55i_gmac200_set_syscon()` reads delay properties, validates 100 ps granularity and field fit, sets interface bits, and writes `SYSCON_REG`.
- `sun55i_gmac200_probe()` parses stmmac data, disables SPH, constrains DMA width to 32 bits, programs syscon, enables `mbus`, enables optional `phy` supply, and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe obtains standard stmmac resources and DT config, mutates stmmac flags, runs syscon configuration before clocks/regulator are enabled, enables the bus clock and PHY supply through devm helpers, then registers the platform stmmac driver. Remove and failure cleanup are handled by devm and stmmac platform helpers.

## State and Persistence
The driver has no custom private structure. Hardware state is in the syscon mode/delay register, enabled MBUS clock, optional regulator state, and stmmac platform state.

## Dependencies and Integration Points
It depends on syscon/regmap, clk, regulator, stmmac platform helpers, OF delay properties, and phy mode helpers. Compatible string: `allwinner,sun55i-a523-gmac200`.

## Risks and Edge Cases
- Delay values must be multiples of 100 ps and fit the TX/RX field widths.
- RMII overrides the EPIT RGMII/MII bit, so mode bits must not conflict.
- Unsupported PHY modes fail probe.
- The syscon write replaces the full register value rather than using update-bits, so the register must be dedicated or fully described by this driver.

## Test Signals
Test MII, RGMII variants, and RMII mode programming; valid and invalid TX/RX delay properties; missing syscon, MBUS clock, and optional regulator paths; 32-bit DMA addressing; and traffic after repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c -->
