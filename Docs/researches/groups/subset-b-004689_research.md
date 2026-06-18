<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83867.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83867.c

## Purpose
`dp83867.c` is the Linux PHYLIB driver for the Texas Instruments DP83867 gigabit Ethernet PHY. It binds the MDIO PHY ID `0x2000a231` and supplies board-specific initialization for copper, RGMII, and SGMII deployments. The file is responsible for translating devicetree/nvmem configuration into register writes, exposing ethtool tunables and wake-on-LAN, managing PHY interrupts, correcting link status from TI status registers, supporting LED class hardware control, and applying reset/link workarounds that generic PHY code cannot know.

## Important APIs, Types, And Functions
The core private state is `struct dp83867_private`, which stores RX/TX internal delay taps, FIFO depths, IO impedance, port mirroring mode, RX_CTRL strap quirk state, clock output selection, and SGMII reference clock output selection. The driver callbacks are registered in `dp83867_driver[]` through `module_phy_driver()`.

Important callback functions include `dp83867_probe()`, `dp83867_config_init()`, `dp83867_phy_reset()`, `dp83867_read_status()`, `dp83867_config_intr()`, `dp83867_handle_interrupt()`, `dp83867_set_wol()`, `dp83867_get_wol()`, `dp83867_get_tunable()`, `dp83867_set_tunable()`, `dp83867_link_change_notify()`, LED callbacks, and the SGMII in-band callbacks `dp83867_inband_caps()` and `dp83867_config_inband()`.

## Control Flow
Probe allocates `phydev->priv` and calls `dp83867_of_init()`. With OF enabled, that parses `ti,clk-output-sel`, nvmem cell `io_impedance_ctrl`, impedance booleans, `ti,dp83867-rxctrl-strap-quirk`, `ti,sgmii-ref-clock-output-enable`, RGMII delay properties, lane swap properties, and FIFO depth properties. Without OF, it reads existing delay register values and seeds conservative defaults.

`dp83867_phy_reset()` performs a global software reset, clears force-link-good, writes a DSP FFE workaround for short cables, then restarts the PHY. `dp83867_config_init()` forces downshift optimization, applies RX_CTRL strap workarounds, repairs FLD threshold if straps enabled FLD, disables EEE because the hardware advertises unsupported EEE capability, programs FIFO depth, selects RGMII or SGMII behavior, configures RGMII delay registers, sets IO impedance, handles SGMII 10 Mbps rate-adapt and autoneg timer quirks, enables interrupt output, applies port mirroring, and optionally configures CLK_OUT.

Runtime status calls `genphy_read_status()` and then overwrites speed/duplex from `MII_DP83867_PHYSTS`. Interrupt enable reads/acks status before programming MICR masks. Link changes in SGMII toggle `DP83867_SGMII_AUTONEG_EN` to retrigger in-band SGMII autonegotiation.

## State And Persistence
Persistent driver state is limited to devm-allocated `phydev->priv`; hardware state lives in standard and vendor MDIO/MMD registers. WOL programming persists in PHY RX filter registers until reset or reconfiguration. LED hardware modes are kept in LEDCR registers. Suspend disables PHY interrupts before `genphy_suspend()`; resume re-enables interrupts and resumes the generic PHY.

## Dependencies And Integration Points
The driver depends on PHYLIB, MDIO Clause 22 and vendor MMD access helpers, ethtool WOL/tunable APIs, LED trigger mappings, devicetree properties from `dt-bindings/net/ti-dp83867.h`, and optionally nvmem. It integrates with MAC drivers through `phy_device` interface mode selection, interrupt lines, in-band SGMII configuration, and LED classdev PHY hooks.

## Risks
Risk is concentrated in board configuration and hardware errata handling: wrong RGMII delay or FIFO depth values can break timing; invalid MAC addresses reject WOL programming; the RX_CTRL strap workaround affects SGMII reliability; advertised EEE is intentionally disabled despite register claims; and SGMII autoneg retriggering depends on preserving the in-band configuration bit. Several `phy_write_mmd()` calls in init are not checked in older-style paths, so failures may be latent in some board bring-up failures.

## Test Signals
Useful signals are successful MDIO probe with the DP83867 ID, correct RGMII/SGMII link at 10/100/1000, ethtool downshift get/set behavior for counts 1/2/4/8 and disable, WOL magic/secure/unicast/broadcast wake tests, interrupt-driven link changes, suspend/resume with interrupts, LED hardware trigger and brightness tests, `ti,clk-output-sel` and impedance DT/nvmem validation, and link recovery across SGMII MAC restart events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83867.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83869.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83869.c

## Purpose
`dp83869.c` is the PHYLIB driver for TI DP83869 and DP83561-SP PHYs. It covers copper Ethernet, RGMII-to-SGMII bridge mode, SGMII copper, 100/1000 Mbps media-converter modes, and fibre modes. Its job is to parse the selected operating mode from devicetree or straps, program the corresponding TI initialization sequence, expose WOL and downshift tunables, and adapt status/autoneg handling for copper versus fibre/Clause 37 operation.

## Important APIs, Types, And Functions
`struct dp83869_private` stores FIFO depths, RX/TX internal delay indexes, impedance selection, port mirroring, RX_CTRL strap quirk flag, clock output selection, and selected `mode`. Driver instances are generated with `DP83869_PHY_DRIVER()` for `DP83869_PHY_ID` and `DP83561_PHY_ID`.

Key functions are `dp83869_probe()`, `dp83869_of_init()`, `dp83869_set_strapped_mode()`, `dp83869_configure_mode()`, `dp83869_configure_rgmii()`, `dp83869_configure_fiber()`, `dp83869_config_init()`, `dp83869_phy_reset()`, `dp83869_config_aneg()`, `dp83869_read_status()`, interrupt handlers, WOL handlers, and downshift tunable helpers.

## Control Flow
Probe allocates private state, initializes it from OF or strap registers, marks fibre ports for 100/1000BASE-X modes, and invokes `dp83869_config_init()`. OF parsing reads `ti,clk-output-sel`, `ti,op-mode`, impedance booleans, lane swap or strap mirror state, FIFO depths, and internal delay values through `phy_get_internal_delay()`.

`dp83869_config_init()` enables downshift optimization, delegates mode-specific programming to `dp83869_configure_mode()`, optionally enables interrupt output, applies port mirroring, updates clock output muxing after the required PLL register write, and programs RGMII delay controls. Mode configuration writes `DP83869_OP_MODE`, BMCR defaults, FIFO bits, gigabit advertisement defaults, fibre capability masks, FX control registers, and media-converter bridge bits according to `ti,op-mode`.

Autoneg uses Clause 37 helpers only for `DP83869_RGMII_1000_BASE`; other modes use generic copper autoneg. Status similarly uses Clause 37 status for 1000BASE-X, generic PHY status otherwise, and forces 100 Mbps when in `DP83869_RGMII_100_BASE` with link.

## State And Persistence
State is held in `phydev->priv` and hardware registers. WOL MAC/SOPASS values are stored in vendor MMD RX filter registers; interrupt masks live in MICR; mode and delay settings are restored by `config_init()` after global reset. `dp83869_phy_reset()` writes software reset and then reruns initialization because reset returns registers to defaults.

## Dependencies And Integration Points
The driver depends on PHYLIB, ethtool WOL/tunables, MMD helpers, `dt-bindings/net/ti-dp83869.h`, and linkmode helpers for fibre capability shaping. It integrates with MAC drivers through RGMII/MII interface mode and with board descriptions through `ti,op-mode`, FIFO depth, delay, impedance, lane swap, and clock output properties.

## Risks
The main risks are mismatched `ti,op-mode` versus MAC interface, invalid use of MII with unsupported modes, fibre autoneg differences, and broad register init sequences that can regress one mode while fixing another. Clock output programming requires a magic PLL write before mux changes. WOL setup validates MAC addresses and returns early on MMD errors, which is good, but board wake behavior still depends on interrupt routing and PHY power retention.

## Test Signals
Test each supported mode: RGMII copper, MII-compatible modes, RGMII-SGMII bridge, SGMII copper, 100M/1000M media conversion, and fibre. Verify Clause 37 autoneg and link reporting, RGMII delay DT values, port mirroring from DT and straps, clock output selection, WOL modes, downshift tunables, interrupt link events, and reset reinitialization. Negative DT tests should cover out-of-range `ti,op-mode` and interface/mode mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83869.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83tc811.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83tc811.c

## Purpose
`dp83tc811.c` supports the TI DP83TC811 automotive PHY. It provides SGMII enable/autoneg control, WOL support for magic and secure-on packets, three interrupt status/mask registers, reset handling, and basic suspend/resume behavior for a single PHY ID family.

## Important APIs, Types, And Functions
The driver has no private state. It registers one `phy_driver` entry for `DP83TC811_PHY_ID`. Important functions are `dp83811_config_init()`, `dp83811_config_aneg()`, `dp83811_phy_reset()`, `dp83811_ack_interrupt()`, `dp83811_config_intr()`, `dp83811_handle_interrupt()`, `dp83811_set_wol()`, `dp83811_get_wol()`, `dp83811_suspend()`, and `dp83811_resume()`.

## Control Flow
Initialization reads `MII_DP83811_SGMII_CTRL` and sets or clears `DP83811_SGMII_EN` based on `phydev->interface`. It then clears all WOL enable bits so a fresh driver start does not inherit stale wake state. Autoneg configuration toggles `DP83811_SGMII_AUTO_NEG_EN` when the MAC-facing interface is SGMII and then delegates copper negotiation to `genphy_config_aneg()`.

WOL setup validates the attached netdev MAC address, writes destination address registers, optionally writes secure-on password registers, clears pending WOL interrupt state, and enables WOL indication bits. Interrupt enable first reads all three INT_STAT registers to acknowledge stale events, then writes enable masks into INT_STAT1/2/3. The IRQ handler reads each INT_STAT register and detects an active interrupt by comparing upper status bits with lower enabled bits before triggering the PHY state machine.

## State And Persistence
There is no allocated driver-private state. Hardware state includes SGMII control, WOL filters, and interrupt enable/status bits. `dp83811_suspend()` avoids generic suspend when WOL is enabled, preserving wake functionality; resume clears the WOL indication bit after generic resume.

## Dependencies And Integration Points
The driver depends on PHYLIB, generic Clause 45 PMA feature reading through `.get_features = genphy_c45_pma_read_ext_abilities`, ethtool WOL APIs, and the attached netdev MAC address. It integrates with MAC drivers through the `PHY_INTERFACE_MODE_SGMII` interface mode and with platform IRQ wiring through PHYLIB interrupt callbacks.

## Risks
The INT_STAT registers combine enable bits and status bits, making interrupt handling easy to break if the upper/lower-half convention is changed. WOL register writes are not consistently error-checked in the middle of `set_wol()`. `dp83811_config_init()` contains a stray blank line after `if (err < 0)`, but semantically returns `err`. SGMII autoneg changes must preserve unrelated bits read from the control register.

## Test Signals
Useful tests include SGMII and non-SGMII initialization, autoneg enable/disable in SGMII mode, magic and secure WOL programming with valid and invalid MAC addresses, suspend with WOL enabled versus disabled, interrupt handling for all three status registers, and hardware reset followed by clean link establishment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83tc811.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83td510.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83td510.c

## Purpose
`dp83td510.c` is the PHYLIB driver for the TI DP83TD510E 10BASE-T1L PHY. It handles a single-pair long-reach automotive/industrial Ethernet PHY with 10 Mbps full-duplex link mode, master/slave management, SQI and MSE diagnostics, LED hardware control, PHY packet statistics, interrupt link handling, and ethtool cable testing using either TDR or ALCD depending on current link state.

## Important APIs, Types, And Functions
`struct dp83td510_priv` stores whether an ALCD cable test is active and accumulated `struct dp83td510_stats`. The main callbacks are `dp83td510_probe()`, `dp83td510_get_features()`, `dp83td510_config_aneg()`, `dp83td510_read_status()`, `dp83td510_config_intr()`, `dp83td510_handle_interrupt()`, `dp83td510_get_sqi()`, cable test callbacks, `dp83td510_update_stats()`, PHY stats/MSE callbacks, and LED callbacks.

## Control Flow
Probe allocates private state. `get_features()` manually advertises autoneg, pause, asym pause, and `10baseT1L_Full` because the PHY can be inaccessible without an RMII clock. Autoneg config programs master/slave settings through Clause 45 BASE-T1 helpers, disables AN when requested, or configures/restarts Clause 45 AN.

Status resets speed/duplex/pause, reads the vendor PHY status bit for link, assigns 10 Mbps full duplex when link is up, reads LPA and resolves linkmode when autoneg is enabled, then reads BASE-T1 status and detects master/slave resolution failure. Interrupt configuration enables only link interrupts and global interrupt output/polarity bits.

Cable testing chooses ALCD if link is currently up, because an active partner prevents useful TDR silence. If link is down, the TDR path performs hardware reset, disables AN, forces master mode, writes TDR timing/fault registers and an undocumented recommended register, starts TDR, then later reports OK/open/short/unspecified and reinitializes hardware. ALCD reads cable length after completion and reports source-specific ethtool results.

## State And Persistence
Driver-private state persists accumulated counters and cable-test mode across callbacks. Packet counters are read in strict register order because each TX/RX group freezes and clears only after a plain sequence. Hardware stores LED modes, interrupt masks, master/slave state, TDR configuration, ALCD results, and MSE/SQI registers.

## Dependencies And Integration Points
The file depends on PHYLIB Clause 45 BASE-T1 helpers, ethtool netlink cable-test reporting, MSE APIs, LED trigger APIs, and vendor MMD registers. It integrates with ethtool for SQI, MSE, PHY stats, and cable diagnostics, and with MACs through the advertised single 10BASE-T1L mode.

## Risks
The cable diagnostics path relies on undocumented or application-note register values, forced master mode, timing assumptions, and `phy_init_hw()` after TDR completion. Incorrect read ordering of packet counters would lose statistics. `dp83td510_read_status()` reads `DP83TD510E_PHY_STS` via `phy_read()` although many registers are vendor MMD-defined, so register addressing assumptions matter. MSE capability refresh rates are inferred rather than documented.

## Test Signals
Exercise autoneg and forced master/slave modes, link-up/down status, master/slave resolution failure reporting, SQI mapping at several MSE thresholds, MSE snapshots for LINK and channel A, stats accumulation over multiple reads, LED brightness/hardware trigger/polarity behavior, IRQ link events, TDR cable test on open/short/OK/noisy lines, ALCD cable length on active links, and recovery after `phy_init_hw()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83td510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83tg720.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83tg720.c

## Purpose
`dp83tg720.c` supports the TI DP83TG720S 1000BASE-T1 PHY. It is more than a basic PHY driver: it implements vendor workarounds for unreliable link detection, adaptive polling, asymmetric reset delays to avoid two-ended reset deadlock, RGMII delay configuration, SQI, cable testing, and accumulated link/packet statistics.

## Important APIs, Types, And Functions
`struct dp83tg720_priv` stores accumulated stats and `last_link_down_jiffies` for polling policy. Important callbacks are `dp83tg720_probe()`, `dp83tg720_soft_reset()`, `dp83tg720_config_init()`, `dp83tg720_config_aneg()`, `dp83tg720_read_status()`, `dp83tg720_get_next_update_time()`, `dp83tg720_get_sqi()`, cable test callbacks, and stats callbacks.

## Control Flow
Initialization performs a hardware reset through `dp83tg720_soft_reset()`, waits a master/slave-dependent delay, configures RGMII internal delay bits if the interface mode requires them, wakes the PHY from managed mode, and reads master/slave role for ethtool visibility. Autoneg is not supported for speed selection; `config_aneg()` only programs and rereads BASE-T1 master/slave configuration.

`read_status()` reads a vendor link bit rather than generic Clause 45 status. If link is down, it snapshots stats, resets and reinitializes hardware, restores master/slave configuration, and reports unknown speed/duplex. If link is up, it reads master/slave state and reports 1000 Mbps full duplex. `get_next_update_time()` chooses faster polling soon after link loss and slower polling after a prolonged down state; this is required because link-up interrupts are not reliable.

Cable test setup writes a sequence of documented and guessed vendor registers, then starts TDR. Completion reads Open Alliance-compatible TDR fault status using `open_alliance_helpers.h`, reports fault length if available, snapshots stats before reset, and calls `phy_init_hw()`.

## State And Persistence
Persistent software state is private stats and polling history. Hardware state includes master/slave role, RGMII delay, managed-mode power setting, TDR configuration, SQI register contents, link-loss counter, and packet counters. Stats counters are accumulated before resets because reset is part of normal link-down recovery.

## Dependencies And Integration Points
The driver depends on PHYLIB Clause 45 BASE-T1 helpers, jiffies/time helpers, ethtool cable-test reporting, Open Alliance TDR helper functions, and RGMII interface mode from the MAC. It uses `PHY_POLL_CABLE_TEST` and the PHYLIB adaptive polling callback.

## Risks
The largest risk is reset policy: link-down status triggers hardware reset and can disrupt diagnostics or obscure short link flaps if not paired with stats capture. Delay values and polling intervals are empirical. Interrupt support is absent by design, so platforms expecting IRQ-driven link-up will behave poorly. Cable-test registers include undocumented values inferred from application notes and comparison with DP83TD510E.

## Test Signals
Test stable link-up at 1000BASE-T1, link-loss recovery, asymmetric master/slave reset timing, adaptive polling intervals, RGMII/RGMII_ID/RGMII_RXID/RGMII_TXID delay bits, master/slave ethtool changes while administratively down, SQI reads, link-loss and packet stat accumulation across resets, cable-test open/short/OK paths, and long down-time transition to slow polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83tg720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/et1011c.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/et1011c.c

## Purpose
`et1011c.c` is a small PHYLIB driver for LSI ET1011C gigabit PHYs. It primarily resets the PHY before autonegotiation and applies a gigabit-speed FIFO/interface configuration when speed changes to 1000 Mbps.

## Important APIs, Types, And Functions
The driver registers one PHY ID, `0x0282f014`, with `et1011c_config_aneg()` and `et1011c_read_status()`. It relies on generic PHY features and no private data structure.

## Control Flow
`et1011c_config_aneg()` reads BMCR, clears duplex/speed/autoneg bits, writes BMCR reset, and then calls `genphy_config_aneg()`. `et1011c_read_status()` delegates to `genphy_read_status()`, compares a file-static `speed` value with `phydev->speed`, and when it detects a change to gigabit according to `ET1011C_STATUS_REG`, it updates `ET1011C_CONFIG_REG` to select GMII, enable system clock, and use 16-depth TX FIFO.

## State And Persistence
There is no per-device private state. The only software state is a `static int speed` shared across all devices using this module, which is a legacy shortcut and not per-PHY. Hardware state persists in BMCR and ET1011C vendor config/status registers.

## Dependencies And Integration Points
The file depends on PHYLIB generic autoneg/status helpers and standard MII register definitions. It integrates with MACs through GMII configuration and PHYLIB speed/duplex reporting.

## Risks
The file-static `speed` can cause cross-device interference if multiple ET1011C PHYs are present. Error handling in `read_status()` does not guard all vendor register reads/writes after `genphy_read_status()`. The gigabit FIFO workaround only runs when speed changes and status register reports gigabit, so missed transitions can leave stale FIFO settings.

## Test Signals
Validate reset before autoneg, link at 10/100/1000, transition into and out of 1000 Mbps, TX FIFO depth programming, multi-PHY behavior if more than one ET1011C is present, and error injection on vendor register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/et1011c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c

## Purpose
`fixed_phy.c` implements the fixed MDIO bus: a software-emulated MDIO bus that exposes fixed-link PHY devices to PHYLIB. It lets MAC and DSA drivers use normal `phy_device` flows even when the link is not backed by a real MDIO PHY.

## Important APIs, Types, And Functions
`struct fixed_phy` binds a `phy_device`, `fixed_phy_status`, and optional `link_update` callback. Exported APIs are `fixed_phy_register()`, `fixed_phy_register_100fd()`, `fixed_phy_unregister()`, `fixed_phy_change_carrier()`, and `fixed_phy_set_link_update()`. Internal helpers include `fixed_mdio_read()`, `fixed_mdio_write()`, `fixed_phy_find()`, `fixed_phy_get_free_addr()`, and module init/exit for the fixed MDIO bus.

## Control Flow
Module init allocates and registers an MDIO bus named `fixed-0` with read/write callbacks. `fixed_phy_register()` validates the requested fixed state with `swphy_validate_state()`, defers if the bus is not registered, allocates one of eight bitmap-backed pseudo addresses, stores status with link forced true, creates a PHY device through `get_phy_device()`, attaches an OF node if provided, marks it `is_pseudo_fixed_link`, and registers it with PHYLIB.

`fixed_mdio_read()` finds the pseudo PHY, invokes its optional `link_update()` against the attached netdev, and returns a synthetic register value from `swphy_read_reg()`. Writes are ignored. Carrier changes mutate the stored fixed link state directly.

## State And Persistence
State is global to the module: `fixed_phy_ids`, `fmb_fixed_phys[]`, and `fmb_mii_bus`. A registered fixed PHY owns a bitmap slot until `fixed_phy_unregister()` removes the PHY device, releases the OF node, clears the slot, and frees the device. No persistent storage exists outside memory.

## Dependencies And Integration Points
The file depends on PHYLIB, MDIO bus registration, `linux/phy_fixed.h`, OF node refcounting, and `swphy` synthetic register helpers. It integrates with MAC drivers that use fixed-link devicetree nodes and with DSA loop or switch setups that need pseudo PHYs.

## Risks
Only eight fixed PHY slots are available. The global static storage requires correct unregister ordering to avoid stale slots. `fixed_phy_change_carrier()` and link update callbacks mutate shared state without explicit locking in this file, relying on higher-level PHY/RTNL context. Reads for missing pseudo PHYs return `0xffff`, mimicking absent MDIO devices.

## Test Signals
Test fixed-link registration and unregister, slot exhaustion, OF node lifetime, `fixed_phy_register_100fd()`, synthetic BMCR/BMSR/LPA reads through `swphy_read_reg()`, carrier changes reflected in MAC link state, DSA loop allocation, and deferred registration before the fixed bus is initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c

## Purpose
`icplus.c` supports ICPlus IP175C, IP1001, IP101A, and IP101G PHYs. It covers an embedded switch-style IP175C path, IP1001 gigabit RGMII delay and power saving setup, IP101A/G interrupt and MDIX handling, IP101G hardware counters, and package-specific pin mux selection for IP101GR.

## Important APIs, Types, And Functions
Private state is `struct ip101a_g_phy_priv`, containing the selected RXER/INTR32 mode and accumulated IP101G stats. `struct ip101g_hw_stat` maps stat names to pages. Important functions include `ip175c_config_init()`, `ip1001_config_init()`, `ip101a_g_probe()`, `ip101a_g_config_intr_pin()`, `ip101a_g_read_status()`, `ip101a_g_config_mdix()`, interrupt callbacks, IP101A/G page helpers and match functions, and IP101G stats callbacks.

## Control Flow
IP175C initialization performs a one-time module-static full reset sequence across MDIO addresses 29/30 and switch ports 0-4, then treats non-WAN ports as always-running 100 Mbps full-duplex links. IP1001 enables auto power saving and sets RX/TX clock phase bits according to RGMII interface mode.

IP101A/G probe parses `icplus,select-rx-error` and `icplus,select-interrupt`, rejecting the conflicting combination. Init enables APS for IP101A or enables/clear-on-read counters for IP101G, then applies the optional INTR32 pin mux through paged register access. Status calls `genphy_read_status()`, reads MDIX control/status from the default page, and updates `phydev->mdix_ctrl`/`mdix`. Autoneg first programs forced/auto MDIX and then delegates to generic autoneg.

IP101A and IP101G share a PHY ID. Matching distinguishes them by probing whether the page select register behaves like IP101G. IP101A fakes page operations to let shared paged helper code work.

## State And Persistence
IP175C has a file-static `full_reset_performed` flag shared across all devices. IP101A/G private state persists pin selection and accumulated stats. Hardware state includes page registers, interrupt masks, MDIX control, APS mode, counters, and RGMII delay bits.

## Dependencies And Integration Points
The file depends on PHYLIB, device property APIs, ethtool stats helpers, paged PHY register helpers, and netdev carrier operations for IP175C switch ports. It integrates with board properties for IP101GR pin selection and with MACs via RGMII delay modes and MDIX controls.

## Risks
One-time IP175C reset state is module-wide and assumes one shared switch reset is sufficient. IP101A/G ID disambiguation writes `0xffff` to the page register and restores it, which is necessary but risky on unexpected silicon. Paged register restore paths must always run to avoid leaving the wrong page selected. Hardware stats return `U64_MAX` on read errors, which callers must treat as invalid.

## Test Signals
Test IP175C WAN versus switch-port behavior, one-time reset across multiple ports, IP1001 RGMII delay modes, IP101A versus IP101G matching, conflicting pinmux DT properties, interrupt enable/disable and link/speed/duplex IRQs, forced MDI/MDIX/auto modes, IP101G stats accumulation and clear-on-read behavior, and page restore after injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c

## Purpose
`intel-xway.c` is the PHYLIB driver for multiple Intel/Lantiq XWAY PHY11G and PHY22F revisions. It handles interrupt masking/status, RGMII internal delay programming and warnings, default LED setup, LED class hardware control, and an autonegotiation workaround for older gigabit revisions.

## Important APIs, Types, And Functions
The file is mostly stateless and registers many `phy_driver` entries in `xway_gphy[]`. Important helpers are `xway_gphy_config_init()`, `xway_gphy_rgmii_init()`, `xway_gphy_init_leds()`, `xway_gphy14_config_aneg()`, interrupt callbacks, and LED callbacks `xway_gphy_led_brightness_set()`, `xway_gphy_led_hw_is_supported()`, `xway_gphy_led_hw_control_get()`, `xway_gphy_led_hw_control_set()`, and `xway_gphy_led_polarity_set()`.

## Control Flow
`config_init()` masks all interrupts, applies a default LED configuration when no devicetree `leds` child exists, clears pending interrupts, and configures RGMII skew. For plain `rgmii`, the driver preserves strapped delays but warns if nonzero skew is detected because `rgmii` should mean no internal delay. For `rgmii-id`, `rgmii-rxid`, and `rgmii-txid`, it reads optional internal delay properties and defaults missing delays to 2 ns before writing MII control skew fields.

Revision 1.3/1.4 `config_aneg()` sets the multi-port-device bit in `MII_CTRL1000` as an erratum workaround, then calls generic autoneg. Interrupt enable acks pending status and writes a mask for link state change and auto-downspeed detection. LED control maps netdev link speed and activity triggers to XWAY MMD LED registers.

## State And Persistence
There is no private software state. Persistent hardware state includes interrupt masks, MIICTRL skew bits, LED direct/integrated control bits, MMD LED blink/constant/pulse registers, polarity inversion bits, and autoneg advertisement workaround bits.

## Dependencies And Integration Points
The driver depends on PHYLIB, OF child-node lookup for `leds`, `phy_get_internal_delay()`, MMD register access, and LED trigger APIs. It integrates with devicetree RGMII delay properties and optional PHY LED descriptions; absent LED nodes trigger legacy default LED programming.

## Risks
RGMII delay semantics are compatibility-sensitive: the driver deliberately warns but preserves strapped delays for `rgmii`. LED hardware trigger reconstruction in `get()` assumes caller-provided `rules` storage is cleared before ORing bits. Activity-only LED triggers are rejected because hardware requires link context. Older revision autoneg workaround applies only to driver entries that set `xway_gphy14_config_aneg()`.

## Test Signals
Test all registered PHY IDs, interrupt mask/status handling, RGMII mode warnings with strapped delays, DT RX/TX delay properties, default LED programming when no `leds` node exists, LED brightness/manual mode, hardware trigger combinations and unsupported activity-only triggers, polarity active-low/high, and rev 1.3/1.4 gigabit autoneg with MPD bit set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c

## Purpose
`linkmode.c` provides common helpers for pause-frame advertisement and resolution using ethtool linkmode bitmaps. It is a small shared utility used by PHY and MAC code that needs IEEE 802.3 pause/asymmetric pause negotiation behavior.

## Important APIs, Types, And Functions
The exported APIs are `linkmode_resolve_pause()` and `linkmode_set_pause()`, both exported GPL. They operate on ethtool link mode masks and standard bits `ETHTOOL_LINK_MODE_Pause_BIT` and `ETHTOOL_LINK_MODE_Asym_Pause_BIT`.

## Control Flow
`linkmode_resolve_pause()` computes the intersection of local and partner advertisements. If both advertise symmetric pause, it enables TX and RX pause. If only asymmetric pause intersects, it enables TX pause when the partner advertises Pause and RX pause when the local side advertises Pause. Otherwise, it disables both directions.

`linkmode_set_pause()` translates ethtool `tx`/`rx` pause booleans into advertised Pause and Asym_Pause bits: Pause follows RX capability, and Asym_Pause is set when TX and RX differ. The comments document why this mapping is imperfect but conventional.

## State And Persistence
The file has no persistent state. All behavior is pure bitmap transformation through caller-provided masks and output booleans.

## Dependencies And Integration Points
It depends on `linux/linkmode.h` and ethtool link mode bit definitions. It integrates with PHYLIB pause resolution, MAC pause configuration, and autonegotiation advertisement setup.

## Risks
The main risk is semantic confusion between local TX/RX pause capability and IEEE Pause/AsymDir advertisement rules. `linkmode_resolve_pause()` assumes the provided bitmaps are already valid negotiated advertisements. `linkmode_set_pause()` intentionally cannot guarantee all requested unidirectional outcomes with every partner advertisement.

## Test Signals
Unit-style tests should enumerate all combinations of local/partner Pause and Asym_Pause bits and compare output with the documented table. Advertisement tests should verify the four `tx`/`rx` inputs map to expected Pause/Asym_Pause bit states and that unrelated linkmode bits are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c

## Purpose
`lxt.c` supports Intel/Level One LXT970, LXT971, and LXT973 PHYs. It supplies interrupt handling for LXT970/971, reset/config setup for LXT970, an LXT973 fibre-mode probe path, and a special read-status implementation for the LXT973-A2 erratum where odd register reads can return stale even-register contents.

## Important APIs, Types, And Functions
Important functions are `lxt970_ack_interrupt()`, `lxt970_config_intr()`, `lxt970_handle_interrupt()`, `lxt970_config_init()`, `lxt971_ack_interrupt()`, `lxt971_config_intr()`, `lxt971_handle_interrupt()`, `lxt973a2_update_link()`, `lxt973a2_read_status()`, `lxt973_probe()`, and `lxt973_config_aneg()`. The registered `phy_driver` table has separate entries for LXT970, LXT971, LXT973-A2, and generic LXT973.

## Control Flow
LXT970 interrupt ack reads BMSR then ISR because status clears in that order. Interrupt enable acks before writing IER and acks after disabling. The handler repeats the BMSR/ISR read sequence and triggers the PHY state machine if the MINT bit is set. LXT971 uses its own ISR/IER registers and status mask.

LXT973-A2 status uses `lxt973a2_update_link()` to fake-read BMSR, read BMCR, and retry BMSR reads when the returned status equals the control value, avoiding the documented stale-read erratum. Autoneg status then reads advertisement and LPA, retries once if they are suspiciously equal, resolves 10/100 speed/duplex and pause, or uses fixed-status generic helpers when autoneg is disabled.

`lxt973_probe()` checks the port configuration register for fibre mode. Fibre mode forces 100 Mbps full duplex, disables autoneg, stores a non-NULL sentinel in `phydev->priv`, and sets `phydev->port = PORT_FIBRE`. `lxt973_config_aneg()` is a no-op for fibre mode.

## State And Persistence
The only software state is the `phydev->priv` sentinel used to remember LXT973 fibre mode. Hardware state includes interrupt masks/status, LXT970 config register, LXT973 PCR, and BMCR fibre forced mode.

## Dependencies And Integration Points
The file depends on PHYLIB generic suspend/resume, generic fixed status helper, MII conversion helpers, and PHY interrupt machinery. It integrates with MACs through normal PHYLIB speed/duplex/link reporting and through `phydev->port` for fibre mode.

## Risks
The LXT973 fibre sentinel uses a function pointer value in `phydev->priv`, which is opaque and easy to misuse if future code expects allocated private data. The A2 erratum workaround uses equality heuristics and limited retries; unusual valid register equality could still confuse status. LXT970 interrupt clearing depends on strict read ordering.

## Test Signals
Test LXT970/LXT971 IRQ enable/disable and handler paths, LXT970 config register zeroing, LXT973 copper autoneg, LXT973 fibre forced mode and autoneg no-op, LXT973-A2 stale-read retry behavior, fixed-speed status, pause resolution, and suspend/resume on supported entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c

## Purpose
`marvell-88q2xxx.c` is the PHYLIB driver for Marvell 88Q2110 and 88Q2220 automotive 100/1000BASE-T1 PHYs. It implements silicon-revision initialization sequences, vendor-specific link and speed status, BASE-T1 feature discovery, autoneg reset sequencing, SQI, interrupts, suspend/resume, 88Q2220 cable testing, optional hwmon temperature reporting, and PHY LED hardware control.

## Important APIs, Types, And Functions
`struct mv88q2xxx_priv` stores whether LED0 should be used as an LED instead of TX enable. `struct mmd_val` represents ordered MMD initialization writes. Important functions include `mv88q2xxx_probe()`, `mv88q2xxx_config_init()`, revision-specific config init functions, `mv88q2xxx_soft_reset()`, `mv88q2xxx_get_features()`, `mv88q2xxx_config_aneg()`, `mv88q2xxx_read_status()`, link helpers for 100M/1000M, interrupt callbacks, SQI callbacks, hwmon callbacks, LED callbacks, and 88Q2220 cable-test callbacks.

## Control Flow
Probe allocates private state, parses optional DT `leds` children to decide LED0/TX_ENABLE behavior, and registers hwmon if enabled. Config init forces `phydev->pma_extable = MDIO_PMA_EXTABLE_BT1`, configures interrupt GPIO drive when IRQs exist, clears TX-disable if LED0 is configured as an LED, and re-enables temperature sensing. 88Q2110 and 88Q2220 revisions run ordered vendor MMD write sequences with required sleeps before common config.

Autoneg delegates to generic Clause 45 config then performs a soft reset. Status reads negotiated speed before link because vendor link registers differ by speed. 1000BASE-T1 link uses Marvell AN receiver status and PCS link bits; 100BASE-T1 link uses vendor 100BT1 status and receiver-good bits. Autoneg status also reads LPA, BASE-T1 status, master/slave state, and resolves linkmode. Forced mode reads vendor link and generic PMA status.

## State And Persistence
Software state is minimal. Hardware state is extensive: revision init registers, PMA extended ability override, interrupt masks/status, TDR calibration/status registers, temperature sensor registers, LED function control, low-power bit, and SQI vendor registers. Cable test sleeps 500 ms, then status read resets TDR and reports results.

## Dependencies And Integration Points
The driver depends on PHYLIB Clause 45 and BASE-T1 helpers, Marvell PHY IDs, ethtool netlink cable-test APIs, hwmon when configured, OF LED child parsing, and PHY LED trigger APIs. It integrates with IRQ-capable boards, hwmon userspace, ethtool SQI/cable test, and automotive single-pair MAC setups.

## Risks
Long vendor initialization sequences are silicon-revision-sensitive. Link status uses different latched/realtime behavior depending on polling mode, so IRQ versus polling behavior must remain intentional. Temperature conversion assumes register value offset of 75 degrees C. LED0 shares TX_ENABLE behavior, making DT LED selection hardware-sensitive. TDR status returns `-ETIMEDOUT` if hardware has not returned to OFF after the fixed wait.

## Test Signals
Test 88Q2110 and each 88Q2220 revision init path, 100BASE-T1 and 1000BASE-T1 autoneg and forced modes, master/slave state, polling versus IRQ link transitions, soft reset after autoneg changes, SQI for both speeds, suspend/resume low-power and interrupt masks, hwmon input/max/alarm and threshold writes, DT LED0/GPIO LED modes, and cable-test open/short/OK/timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c

## Purpose
`marvell-88x2222.c` is the PHYLIB driver for the Marvell 88X2222 dual-port multi-speed Ethernet transceiver. It bridges an XAUI host-side interface to line-side 10GBASE-R, 1000BASE-X, or SGMII, supports SFP/PHY port integration, dynamically swaps line type based on advertised capabilities and link progress, and controls PMA transmitter power on suspend/resume.

## Important APIs, Types, And Functions
`struct mv2222_data` stores current line interface, a filtered supported-linkmode mask, and SFP link state. Important functions are `mv2222_probe()`, `mv2222_config_init()`, `mv2222_configure_serdes()`, `mv2222_attach_mii_port()`, `mv2222_config_aneg()`, `mv2222_setup_forced()`, `mv2222_swap_line_type()`, `mv2222_read_status()`, `mv2222_read_status_10g()`, `mv2222_read_status_1g()`, `mv2222_aneg_done()`, `mv2222_soft_reset()`, and TX enable/disable helpers.

## Control Flow
Probe seeds `phydev->supported` with fibre, twisted-pair, 10/100/1000, 1000BASE-X, 10G, pause, and autoneg modes, then allocates private state with no active line interface. Config init rejects any host interface except XAUI. When a PHY port configures MII/SerDes, `mv2222_configure_serdes()` stores the requested line interface, intersects PHY and port supported masks, writes the PCS host/line configuration, and tries to run autoneg under `phydev->lock`.

`config_aneg()` does nothing until a line interface is attached. Forced mode or 10GBASE-R uses `mv2222_setup_forced()`, which may swap from 10G to 1G/SGMII for lower forced speeds and programs SGMII speed bits before disabling AN. For 1G autoneg, it writes 1000BASE-X advertisement bits and enables AN. Status first requires PMA signal detect and, when an SFP bus exists, SFP link-up notification. Then it uses 10G PCS status or 1G/SGMII status. If autoneg/link does not complete within `AUTONEG_TIMEOUT` polls, it swaps between 10G and 1G-capable line types and restarts configuration.

## State And Persistence
Private state persists line interface, SFP link state, and the port-filtered capability mask. The 10G and 1G status functions each use a file-static `timeout`, shared across devices. Hardware state includes PCS configuration, port reset bits, PMA TX disable, 1GBX control/advertisement/status, and signal-detect status.

## Dependencies And Integration Points
The driver depends on PHYLIB, Marvell PHY IDs, Clause 45 MMD helpers, `phy_port` operations, SFP link notifications, and ethtool linkmode conversion helpers. It integrates with MACs that expose XAUI host connectivity and with pluggable/line-side ports that can request 10GBASE-R, 1000BASE-X, or SGMII.

## Risks
The static timeout counters are not per device and can cross-contaminate multiple transceivers. Dynamic line-type swapping can surprise users if supported masks are too broad or SFP link reporting is delayed. `mutex_trylock()` in SerDes configuration means autoneg may be skipped if the PHY lock is busy. SGMII forced speed selection depends on the filtered `priv->supported` mask and returns `-EINVAL` when no matching mode remains.

## Test Signals
Test XAUI-only host validation, SerDes enable/disable for 10GBASE-R/1000BASE-X/SGMII, SFP link-up/down gating, 10G forced link, 1G autoneg advertisement, SGMII forced 10/100/1000 speeds, line-type fallback after timeout, PMA TX disable/enable during suspend/resume, multi-device timeout behavior, and port capability filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c -->
