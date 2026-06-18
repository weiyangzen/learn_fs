# Research Report: subset-b-004694

Scope: Linux PHY and MACsec sources under `sources/distributed-fs/ceph-client/drivers/net/phy`. Each section is source-tree aligned and intended to be split into the corresponding `Docs/researches/<source>_research.md` file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mxl-gpy.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mxl-gpy.c

## Purpose
This file is the Linux phylib driver for MaxLinear GPY2xx, GPY11x/21x/24x, and MxL862xx Ethernet PHYs. It handles Clause 45 capability discovery, copper link negotiation, SGMII/2500Base-X in-band signaling, MDIX, Wake-on-LAN, LED controls, optional hwmon temperature reporting, loopback, interrupts, and ethtool PHY statistics.

## Important APIs, Types, and Functions
The main state type is `struct gpy_priv`, stored in `phydev->priv`. It contains a mailbox mutex, firmware major/minor values, WoL options, accumulated RX error count, and loopback disable timeout. Driver callbacks are registered through the large `gpy_drivers[]` table and exported with `module_phy_driver()`.

Key callbacks include `gpy_probe()`, `gpy_config_init()`, `gpy21x_config_init()`, `gpy_config_aneg()`, `gpy_read_status()`, `gpy_config_intr()`, `gpy_handle_interrupt()`, `gpy_set_wol()`, `gpy_get_wol()`, `gpy_loopback()`, `gpy115_loopback()`, LED callbacks, `gpy_update_stats()`, and `gpy_get_phy_stats()`. Optional hwmon paths are guarded by `CONFIG_HWMON`; `gpy_hwmon_read()` uses a polynomial conversion while MxL862x2 uses a signed-register linear conversion.

## Control Flow
Probe allocates `gpy_priv`, ensures Clause 45 IDs are populated for Clause 22 access, disables IRQ use unless the device property `maxlinear,use-broken-interrupts` is present, reads firmware version, registers hwmon, and logs firmware details. Init selects the RX error counter. GPY21x variants also mark `2500BASEX` and `SGMII` as possible interfaces.

Autonegotiation first handles forced mode, using Clause 22 forced setup for half duplex and Clause 45 PMA setup for full duplex. In autoneg mode it programs MDIX, Clause 45 advertisements, 1000BASE-T advertisements, restarts negotiation if needed, and may trigger a firmware-specific SGMII renegotiation workaround after polling link for up to four seconds. Status reading refreshes link, LPA, speed, duplex, dynamic SERDES interface, master/slave state, and MDIX.

Interrupt setup acknowledges pending status, enables link/speed/duplex/autoneg/downspeed events, and folds in WoL masks. The interrupt handler ignores unrelated status and uses a mailbox read workaround when link-state or speed changes can leave the interrupt line asserted. WoL writes the attached netdev MAC address into vendor registers and enables magic packet or link-change wake. LED callbacks translate netdev LED triggers to vendor LED registers and allow active high/low polarity control.

## State and Persistence
State is runtime-only in `phydev->priv` and hardware registers. `wolopts` mirrors ethtool WoL state, `rx_errors` accumulates an 8-bit read-clear hardware counter, firmware fields drive workarounds, and `lb_dis_to` prevents rapid loopback re-entry. Hardware state persists across callbacks until reset or reconfiguration.

## Dependencies and Integration Points
The file integrates with phylib, Clause 45 generic helpers, ethtool WoL/stats/LED APIs, Linux hwmon, device properties, netdev address storage, MMD register helpers, and optional firmware-specific behavior. It depends on PHY register definitions and kernel helpers such as `phy_modify_mmd()`, `genphy_c45_*()`, `linkmode_*()`, and `devm_hwmon_device_register_with_info()`.

## Risks
Important risks are hardware-specific timing and interrupt workarounds, read-clear error counter races, incorrect dynamic interface selection on MACs that cannot tolerate SGMII/2500Base-X changes, WoL programming without an attached netdev MAC, firmware-version workaround coverage, and LED trigger mappings that may not match every board design.

## Test Signals
Useful tests include probing every listed PHY ID, forced and autoneg link at 10/100/1000/2500, interface switching between SGMII and 2500Base-X, WoL magic/link-change wake, IRQ storm regression under link flaps, LED trigger/polarity ethtool tests, hwmon temperature reads, loopback timing, and RX error counter accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mxl-gpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/national.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/national.c

## Purpose
This is a compact phylib driver for the National Semiconductor DP83865 Gigabit PHY. It provides device-specific initialization for gigabit speed fallback and 10BASE-T half-duplex loopback behavior, plus interrupt masking and acknowledgement.

## Important APIs, Types, and Functions
The single driver table entry `dp83865_driver[]` binds `DP83865_PHY_ID` with mask `0xfffffff0`. Main functions are `ns_exp_read()`, `ns_exp_write()`, `ns_ack_interrupt()`, `ns_handle_interrupt()`, `ns_config_intr()`, `ns_giga_speed_fallback()`, `ns_10_base_t_hdx_loopack()`, and `ns_config_init()`. `enum hdx_loopback` supplies readable on/off constants for the loopback helper.

## Control Flow
Initialization calls `ns_giga_speed_fallback()` to power down the PHY, configure expanded memory access, write an internal expanded-memory value, restore BMCR power state, and enable all fallback modes through the LED control register. It then disables 10 Mbps half-duplex loopback by modifying expanded memory register `0x1c0` and acknowledges interrupts.

Interrupt configuration either acknowledges and enables default remote fault, autoneg-complete, and link-change interrupt masks, or disables the mask and acknowledges any pending status. The interrupt handler reads `DP83865_INT_STATUS`, ignores unmasked/uninteresting interrupts, clears asserted bits through `DP83865_INT_CLEAR`, and triggers the phylib state machine.

## State and Persistence
No private software state is allocated. State is held in hardware registers: interrupt mask/status/clear registers, BMCR power-down state, expanded memory register `0x1c0`, and LED/fallback control. Register writes persist until reset or subsequent driver/firmware changes.

## Dependencies and Integration Points
The driver depends on Linux phylib Clause 22 helpers, MII/BMCR definitions, module PHY registration, and netdevice/ethtool headers. It does not expose ethtool stats or custom link status callbacks, relying on generic phylib behavior outside its init and interrupt callbacks.

## Risks
`ns_exp_read()` returns `u8` while `phy_read()` returns negative errors, so MDIO read failures in expanded memory access are truncated rather than propagated. Init helpers do not check every write result, so partial configuration can go unnoticed. The fallback programming sequence is tightly hardware-specific and may be sensitive to power-down timing.

## Test Signals
Tests should verify DP83865 probe, init register writes, link-change/remote-fault interrupt delivery, interrupt disable behavior, and regression coverage for 10BASE-T half-duplex loopback disablement and gigabit fallback interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/national.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ncn26000.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/ncn26000.c

## Purpose
This is the onsemi NCN26000 10BASE-T1S PHY driver. The device is point-to-multipoint and does not support normal Ethernet autonegotiation; the driver maps the hardware link-control/status behavior into phylib and exposes Open Alliance PLCA operations through generic Clause 45 helpers.

## Important APIs, Types, and Functions
The driver table `ncn26000_driver[]` registers one PHY model using `PHY_ID_MATCH_MODEL(PHY_ID_NCN26000)`. Core callbacks are `ncn26000_config_init()`, `ncn26000_config_aneg()`, `ncn26000_read_status()`, `ncn26000_config_intr()`, and `ncn26000_handle_interrupt()`. It attaches `genphy_c45_plca_get_cfg()`, `genphy_c45_plca_set_cfg()`, and `genphy_c45_plca_get_status()` for PLCA management.

## Control Flow
Init applies a hardware workaround by forcing Open Alliance TC14 PLCA `TO_TIMER` to 32 through `MDIO_OATC14_PLCA_TOTMR`. Config-aneg is used as a link bring-up callback: it sets MDI auto defaults and writes `BMCR_ANENABLE`, which this PHY repurposes as link control. Status reads handle the latched-low behavior of BMSR by avoiding unnecessary double reads in polling mode unless the link was already down, then maps the NCN26000 status bit to `phydev->link`, half-duplex 10 Mbps speed, and no pause.

Interrupt handling reads the IRQ status register, treats asserted link status as the meaningful event, and triggers the phylib state machine. Interrupt configuration acknowledges pending status before enabling only link-status notifications, or disables all IRQs.

## State and Persistence
The driver has no private allocation. Runtime state is in `phydev` fields and in hardware registers for BMCR/BMSR, IRQ control/status, and PLCA MMD registers. The TO_TIMER workaround is persistent until reset or explicit PLCA reconfiguration.

## Dependencies and Integration Points
Dependencies are phylib, standard MII definitions, `mdio-open-alliance.h`, and generic Clause 45 PLCA helpers. The feature mask is `PHY_BASIC_T1S_P2MP_FEATURES`, aligning it with 10BASE-T1S point-to-multipoint behavior.

## Risks
The interrupt handler condition appears suspicious because it checks `(ret & NCN26000_REG_IRQ_STATUS) == 0` rather than the link-status bit mask, which can miss or misclassify interrupts. The no-autoneg mapping to BMCR/BMSR is device-specific and easy to break if generic phylib expectations change. Status is fixed to half-duplex 10 Mbps and must stay aligned with T1S semantics.

## Test Signals
Test with NCN26000 link up/down transitions in polling and IRQ mode, PLCA get/set/status via ethtool netlink, TO_TIMER default after reset, no-autoneg link bring-up, and interrupt masking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ncn26000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx-macsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx-macsec.c

## Purpose
This file implements MACsec offload support for NXP Clause 45 TJA11xx PHYs that expose an embedded MACsec engine. It bridges Linux `macsec_ops` to vendor MMD registers for SecY, TX/RX SC, TX/RX SA, keys, packet number handling, statistics, PN wrap interrupts, and the adapter TLV tag insertion required by the hardware.

## Important APIs, Types, and Functions
Private MACsec state is represented by `struct nxp_c45_macsec`, which owns a SecY list and bitmaps for active SecYs and allocated TX SC slots. `struct nxp_c45_secy` tracks the kernel `macsec_secy`, optional RX SC, SA list, hardware SecY id, and RX SC0 point-to-point implementation flag. `struct nxp_c45_sa` tracks a TX or RX SA, AN, hardware key bank A/B, and register layout.

Register helpers `nxp_c45_macsec_read()` and `nxp_c45_macsec_write()` map 32-bit MACsec registers onto 16-bit MDIO VEND2 accesses. The exported entry points used by the C45 core are `nxp_c45_macsec_probe()`, `nxp_c45_macsec_config_init()`, `nxp_c45_macsec_remove()`, and `nxp_c45_handle_macsec_interrupt()`. The kernel-facing `nxp_c45_macsec_ops` table implements the full add/update/delete lifecycle for SecY, RXSC, RXSA, TXSA, stats, open/stop, and TX tag insertion.

## Control Flow
Probe allocates the MACsec state, initializes the SecY list, and installs `phydev->macsec_ops`. Config-init enables MACsec and adapter functions, configures the adapter, sets the PN wrap threshold, and installs an MKA pass-through filter for PAE EtherType. Adding a SecY validates MAC address uniqueness, slot availability, and hardware point-to-point constraints, then selects the SecY slot, writes TX SCI and TX filters, updates TX SC config, enables PN wrap IRQs if valid, and links the object into software state.

Opening a SecY enables its TX filter, optional RX SC, RX SC0 mode, and global MACsec bypass when the first SecY becomes active. Stopping reverses that and disables global MACsec when no SecYs remain active. RXSC and RXSA callbacks program SCI, replay windows, validation mode, PN thresholds, keys, salt/SSCI for XPN, and active bits. TXSA callbacks program PN/key material and update the currently encoded SA when applicable. Deletion disables hardware entries, clears stats, frees list nodes, clears bitmaps, and clears global stats when all SecYs are gone.

Stats callbacks read 32-bit or split 64-bit counters into Linux MACsec stats structures. The interrupt handler reads `MACSEC_EVR`, maps the bit position to a SecY id, finds the active encoding SA, calls `macsec_pn_wrapped()`, acknowledges the event, and marks the parent IRQ handled.

## State and Persistence
Software state persists in `struct nxp_c45_phy::macsec` for the PHY lifetime. Hardware state persists in selected MACsec register banks and is selected by writing SecY id to RX/TX selector registers. SA allocation alternates key bank A/B and enforces at most two SAs per direction. Packet number state, replay lower PN, XPN salt/SSCI, and counters live in hardware and are synchronized by ops callbacks.

## Dependencies and Integration Points
The file depends on `<net/macsec.h>`, phylib MDIO helpers, `nxp-c45-tja11xx.h`, netdev MAC addresses, sk_buff headroom handling, ethtool netlink stats/cable constants, and the parent NXP C45 driver for ability detection and interrupt dispatch. It is compiled only when `CONFIG_MACSEC` enables the non-stub declarations from the header.

## Risks
Key and salt programming uses casts to `u32 *`, so alignment and endianness assumptions are important. SecY validity is constrained by hardware point-to-point and port-1 SCI rules; unsupported topologies return `-EINVAL` or `-EBUSY`. Bitmap/list state must remain synchronized with hardware selection registers. PN wrap interrupt handling depends on correct bit-to-SecY mapping and active SA lookup. Some read helpers ignore return values for stats, so MDIO failures can surface as stale or zeroed data rather than hard errors.

## Test Signals
Test MACsec offload add/update/delete for SecY, RXSC, RXSA, and TXSA; XPN and non-XPN keys; 128-bit and 256-bit keys; replay protection windows; port-1/end-station constraints; multiple SecY slot exhaustion; MKA pass-through; PN wrap notification; stats reads; TX TLV insertion headroom; module removal cleanup; and interrupt coexistence with link/PTP events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx-macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.c

## Purpose
This is the main NXP Clause 45 TJA1103/TJA1104/TJA1120/TJA1121 PHY driver. It handles PHY configuration, interface mode selection, RGMII delay setup, link interrupts, cable tests, SQI, ethtool stats, PTP hardware timestamping, PHC registration, external timestamp/perout GPIO functions, and optional MACsec integration.

## Important APIs, Types, and Functions
The central private type is `struct nxp_c45_phy` from the companion header, allocated in `nxp_c45_probe()` and stored in `phydev->priv`. Internal data tables use `struct nxp_c45_regmap`, `struct nxp_c45_phy_data`, `struct nxp_c45_reg_field`, `struct nxp_c45_hwts`, and `struct nxp_c45_phy_stats` to abstract register differences between TJA1103 and TJA1120 families.

Major functions include register-field helpers, PTP clock methods (`nxp_c45_ptp_gettimex64()`, `settime64`, `adjfine`, `adjtime`, `enable`), timestamp queue handling (`nxp_c45_txtstamp()`, `nxp_c45_rxtstamp()`, `nxp_c45_do_aux_work()`), PHY configuration (`nxp_c45_config_enable()`, `nxp_c45_set_phy_mode()`, `nxp_c45_config_init()`), interrupts (`nxp_c45_handle_interrupt()` plus TJA-specific NMI handlers), cable tests, SQI, stats, and probe/remove.

## Control Flow
Probe allocates and initializes private state, skb queues, mutexes, device-tree flags, PTP support when the hardware and kernel config allow it, and MACsec support when advertised by the PHY. Config-init enables global/port/PHY configuration, applies PMAPMD write-access and TJA1120 engineering-sample errata, enables automatic PHY config, validates and programs the selected host interface, disables autoneg, enables counters, initializes PTP, initializes MACsec, and starts operation.

PTP TX timestamping queues SKBs after parsing PTP headers and either waits for IRQs or schedules worker polling. Egress timestamp retrieval differs by family; TJA1120 has FIFO workarounds for engineering samples. RX timestamping queues incoming SKBs, reconstructs seconds from the current PHC time plus embedded timestamp bits, clears reserved header storage, and reinjects via `netif_rx()`. The auxiliary worker drains TX timestamps, RX timestamps, and optional external timestamp events.

Interrupt handling reads PHY link IRQ status, acknowledges link events and triggers phylib, drains egress timestamp IRQs, invokes TJA-specific NMI handlers, and delegates MACsec IRQ handling to the companion file. Cable tests enable test mode, start a vendor cable test, report ethtool pair-A result when valid, disable test mode, and restart operation.

## State and Persistence
State includes the PHC pointer, timestamp queues, PTP configuration, RGMII delays, external timestamp last value/index, hardware timestamp enable flags, and optional MACsec state. It persists for the driver lifetime and is cleaned up in `nxp_c45_remove()` by unregistering the PHC, purging queues, and removing MACsec state. Hardware registers store PTP time, event filters, GPIO pin mux, counters, interface mode, delays, and cable-test state.

## Dependencies and Integration Points
The driver integrates with phylib, `mii_timestamper`, PTP clock kernel APIs, network hardware timestamping APIs, ethtool stats/cable/SQI, device tree properties, generic Clause 45 helpers, and the MACsec companion through `nxp-c45-tja11xx.h`. PHY variants are split by matching MACsec ability so the same PHY IDs register separate no-MACsec and MACsec-capable driver entries.

## Risks
PTP timestamp reconstruction uses truncated hardware seconds and current PHC time, so long delays or queue stalls can misassociate seconds. SKB queue lifetime must be correct across remove and timestamp configuration changes. Errata sequences use magic registers and must be constrained to the right silicon. Interface mode validation depends on hardware ability bits. PTP/MACsec/link interrupt sharing increases risk of missed acknowledgements. RGMII delay range enforcement can reject boards with invalid DT values.

## Test Signals
Test probe for TJA1103/TJA1104/TJA1120/TJA1121 with and without MACsec, all supported host interface modes, RGMII delay DT properties, PHC registration and time adjustments, TX/RX hardware timestamping under IRQ and polling, external timestamp and PPS GPIO functions, cable test results, SQI reads, stats reads, link IRQs, suspend/resume, TJA1120 link-recovery workaround, and MACsec interrupt coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.h

## Purpose
This header shares private state and MACsec integration declarations between the NXP Clause 45 TJA11xx core driver and its MACsec companion. It also provides no-op MACsec stubs when `CONFIG_MACSEC` is disabled.

## Important APIs, Types, and Functions
The key type is `struct nxp_c45_phy`, which stores variant data, `phy_device`, `mii_timestamper`, PTP clock and clock info, TX/RX timestamp skb queues, PTP mutex, timestamping mode flags, RGMII delays, external timestamp state, optional `struct nxp_c45_macsec *`, and flags. The shared register define is `VEND1_PORT_FUNC_ENABLES`.

The header declares or stubs `nxp_c45_macsec_config_init()`, `nxp_c45_macsec_probe()`, `nxp_c45_macsec_remove()`, and `nxp_c45_handle_macsec_interrupt()`.

## Control Flow
The core driver includes this header, allocates `struct nxp_c45_phy`, and calls the MACsec functions unconditionally. Build-time stubs make those calls compile to successful no-ops when MACsec is unavailable, keeping the main driver free from repeated preprocessor branches.

## State and Persistence
The struct defines all software state that persists across NXP C45 callbacks. It is allocated with device-managed memory during probe. PTP queues and clock registration are explicitly initialized and cleaned up by the core driver; the MACsec pointer is populated only when hardware and kernel config support it.

## Dependencies and Integration Points
The header depends on PTP clock kernel types, phylib types from includers, skb queue types, and MACsec configuration symbols. It is the narrow integration contract between `nxp-c45-tja11xx.c` and `nxp-c45-tja11xx-macsec.c`.

## Risks
Because this is a private shared header, layout changes affect both core and MACsec files. The unconditional no-op stubs mean callers must not assume MACsec state exists after a successful stubbed probe/config-init. The PTP/MACsec fields concentrate multiple subsystems in one private struct, so lifetime ordering is important.

## Test Signals
Build-test with `CONFIG_MACSEC=y/m/n`, `CONFIG_PTP_1588_CLOCK` and `CONFIG_NETWORK_PHY_TIMESTAMPING` combinations, plus runtime probe/remove with and without MACsec ability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-cbtx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-cbtx.c

## Purpose
This file is the phylib driver for the 100BASE-TX PHY embedded in the NXP SJA1110 switch. It supplies reset handling, MDIX configuration/status, interrupt handling, and a single RX error ethtool statistic.

## Important APIs, Types, and Functions
The driver registers `PHY_ID_CBTX_SJA1110` in `cbtx_driver[]`. Key callbacks are `cbtx_soft_reset()`, `cbtx_config_init()`, `cbtx_read_status()`, `cbtx_config_aneg()`, `cbtx_config_intr()`, `cbtx_handle_interrupt()`, `cbtx_get_sset_count()`, `cbtx_get_strings()`, and `cbtx_get_stats()`.

## Control Flow
Soft reset first clears true power-down because the PHY cannot reset while powered down, then delegates to `genphy_soft_reset()`. Init defers actual MDIX programming by setting `phydev->mdix_ctrl = ETH_TP_MDI_AUTO`; config-aneg applies the MDIX mode and then runs generic autoneg. Read-status updates MDIX status from `CBTX_MODE_CTRL_STAT` and delegates link state to `genphy_read_status()`.

Interrupt configuration acknowledges latched status by reading `CBTX_IRQ_STAT`, then enables link-down, autoneg-complete, and energy-on events, or disables all events and acknowledges pending state. The interrupt handler reads and clears status, reads the enable mask, ignores disabled/unasserted events, and triggers the phylib state machine.

## State and Persistence
No private software state is used. Persistent state is in PHY registers for power-down, MDIX mode, IRQ enable/status, and the RX error counter. `phydev->mdix_ctrl` and `phydev->mdix` are the phylib-facing mirrors.

## Dependencies and Integration Points
The driver uses phylib Clause 22 helpers, generic autoneg/suspend/resume/status code, ethtool stats helpers, and module MDIO device matching.

## Risks
`cbtx_mdix_config()` returns success for unknown `mdix_ctrl` values instead of `-EINVAL`, which may hide unsupported control requests. Stats reads return `U64_MAX` on MDIO failure. Interrupt status semantics rely on read-to-clear behavior.

## Test Signals
Test reset from true power-down, auto/MDI/MDI-X configuration, link readout, IRQ enable/disable, link-down/autoneg IRQ delivery, RX error ethtool stat reads, and suspend/resume with the embedded switch PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-cbtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-tja11xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-tja11xx.c

## Purpose
This is the Clause 22 NXP TJA1100/TJA1101/TJA1102/TJA1102S BroadR-Reach/100BASE-T1 PHY driver. It manages power/wakeup, forced 100 Mbps full-duplex link operation, master/slave role, MII/RMII/RGMII-style interface selection, cable tests, SQI, hwmon temperature, statistics, interrupts, and special dual-port TJA1102 discovery.

## Important APIs, Types, and Functions
The driver uses `struct tja11xx_priv` to hold a `phy_device` pointer, hwmon state, and flags such as RMII refclk input. Core helpers include `tja11xx_check()`, `phy_modify_check()`, register-write enable/link-control helpers, `tja11xx_wakeup()`, `tja11xx_soft_reset()`, `tja11xx_config_aneg()`, `tja11xx_config_init()`, `tja11xx_read_status()`, SQI/stats functions, hwmon callbacks, DT parsing, probe functions, TJA1102 port matching/discovery, interrupt callbacks, and cable-test callbacks.

## Control Flow
Probe allocates private state, parses device-tree settings such as `nxp,rmii-refclk-in`, registers hwmon when supported, and for TJA1102 port 0 may create/register the second PHY device on the next MDIO address. Init enables configuration writes, forces autoneg disabled with 100/full defaults, programs interface mode per PHY variant and selected host interface, clears sleep confirmation, programs sleep request timeout, wakes the PHY, and acknowledges interrupts.

Config-aneg maps `phydev->master_slave_set` into the TJA master/slave bit, optionally starts cable test autoneg behavior when link is down and a cable-test operation is available, and then delegates generic config-aneg. Read-status updates link, master/slave state, communication status, and fixed 100/full state. Interrupt paths acknowledge and enable device-specific interrupt masks, then trigger the state machine on asserted events.

## State and Persistence
Private state persists in `phydev->priv`, while most behavior is hardware-register based. The driver uses `phydev` fields for forced autoneg, speed, duplex, master/slave configuration, interface mode, SQI, and stats. TJA1102 dual-port discovery creates a second `phy_device`, so bus/device lifetime is a key persistence concern.

## Dependencies and Integration Points
The file integrates with phylib, ethtool cable-test netlink, hwmon, device tree, MII register helpers, module PHY registration, and generic helpers such as `genphy_*`. It is a predecessor/parallel driver to the Clause 45 TJA11xx support in this subset.

## Risks
Wakeup and config-write sequences are hardware timing sensitive. Dual-port TJA1102 creation must avoid address conflicts and incorrect port matching. Cable-test autoneg side effects can surprise link bring-up if invoked at the wrong time. Interface mode flags differ by PHY variant and DT property. Temperature and stats reads must handle absent hardware support cleanly.

## Test Signals
Test each supported PHY ID, TJA1102 port0/port1 discovery, wake from sleep, all supported host interface modes, RMII refclk DT behavior, forced master/slave modes, link status and SQI, cable tests, hwmon reads, interrupts, stats, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/nxp-tja11xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.c

## Purpose
This helper file translates OPEN Alliance 1000BASE-T1 Time Delay Reflection diagnostic register values into Linux ethtool cable-test result codes and distances.

## Important APIs, Types, and Functions
It exports `oa_1000bt1_get_ethtool_cable_result_code()` and `oa_1000bt1_get_tdr_distance()` with `EXPORT_SYMBOL_GPL()`. Both operate on a 16-bit HDD.TDR-like register value using masks from `open_alliance_helpers.h`.

## Control Flow
`oa_1000bt1_get_ethtool_cable_result_code()` extracts TDR status and distance fields. Known statuses map to ethtool OK, open, same-short, and noise. Unknown statuses return resolution-not-possible when the distance field is the special `0x3f` value, otherwise unspecified. `oa_1000bt1_get_tdr_distance()` extracts the distance field, returns `-ERANGE` when resolution is not possible, or returns distance in centimeters by multiplying the meter-scale value by 100.

## State and Persistence
The file is stateless. It performs pure conversions and does not touch hardware directly.

## Dependencies and Integration Points
It depends on Linux bitfield helpers, ethtool netlink constants, errno values, and the companion header. PHY drivers that implement OPEN Alliance TDR can call these helpers after reading their device-specific diagnostic register.

## Risks
The helpers assume the caller provides a register formatted like the documented OPEN Alliance HDD.TDR layout. Distance scaling is coarse and may not match vendor-specific interpretations. The result-code helper prioritizes status except for unknown status with resolution-not-possible distance.

## Test Signals
Unit-style tests should cover every defined TDR status, the resolution-not-possible distance field, distance conversion for representative values, and unknown statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.h

## Purpose
This header defines the OPEN Alliance 1000BASE-T1 HDD.TDR bit layout and declares helper functions for converting TDR status and distance into Linux-facing diagnostics.

## Important APIs, Types, and Functions
Important definitions include activation masks/values, TDR status mask and status constants for short, open, noise, cable OK, test in progress, and test not possible, plus distance mask and special no-error/resolution-not-possible values. It declares `oa_1000bt1_get_ethtool_cable_result_code()` and `oa_1000bt1_get_tdr_distance()`.

## Control Flow
The header has no runtime control flow. Its constants are consumed by the companion C file and by drivers that need to program or interpret OPEN Alliance TDR registers.

## State and Persistence
There is no state. The header is a compile-time contract for bit interpretation.

## Dependencies and Integration Points
It uses `GENMASK()` and `u16` types from kernel headers included by consumers. It is intended for automotive Ethernet PHY drivers implementing OPEN Alliance advanced diagnostics.

## Risks
Because the actual register offset is device-specific, callers must not assume this header identifies where to read. Vendors may extend or vary the semantics, especially around distance resolution and in-progress/not-possible states.

## Test Signals
Build coverage for consumers, plus conversion tests through the C helper, are sufficient. Static checks should catch missing bitfield include dependencies in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-c45.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy-c45.c

## Purpose
This file implements generic Linux phylib helpers for IEEE Clause 45 PHYs. It covers PMA sleep/resume, forced PMA speed setup, BASE-T1 master/slave and autoneg advertisement, autoneg restart/status, link and partner advertisement reads, PMA ability discovery, EEE support, loopback, fast retrain, Open Alliance TC14 PLCA, Open Alliance cable test helpers, and OATC14 SQI/SQI+ reads.

## Important APIs, Types, and Functions
The file exports many helpers used by PHY drivers: `genphy_c45_pma_resume()`, `genphy_c45_pma_suspend()`, `genphy_c45_pma_setup_forced()`, `genphy_c45_an_config_aneg()`, `genphy_c45_an_disable_aneg()`, `genphy_c45_restart_aneg()`, `genphy_c45_check_and_restart_aneg()`, `genphy_c45_aneg_done()`, `genphy_c45_read_link()`, `genphy_c45_read_lpa()`, `genphy_c45_read_pma()`, `genphy_c45_read_mdix()`, `genphy_c45_read_eee_abilities()`, `genphy_c45_an_config_eee_aneg()`, `genphy_c45_pma_read_abilities()`, `genphy_c45_read_status()`, `genphy_c45_config_aneg()`, `genphy_c45_loopback()`, `genphy_c45_fast_retrain()`, PLCA get/set/status helpers, EEE ethtool helpers, OATC14 cable-test start/status helpers, and OATC14 SQI helpers.

Internal helpers include `genphy_c45_baset1_able()`, which caches `phydev->pma_extable`, `genphy_c45_pma_can_sleep()`, BASE-T1 LPA/status helpers, EEE capability readers, `oatc14_cable_test_get_result_code()`, and `oatc14_update_sqi_capability()`.

## Control Flow
Ability discovery reads PMA/AN/PCS MMD registers and populates `phydev->supported` and `phydev->supported_eee`. Autoneg configuration first constrains advertising to supported modes, configures EEE advertising, then selects BASE-T1 or conventional AN registers. Forced mode writes PMA CTRL1/CTRL2 speed/type and BASE-T1 master/slave/strap controls when applicable, then disables AN.

Status reading checks link across relevant MMDs while preserving latched-low semantics, resets speed/duplex/pause fields, reads LPA and BASE-T1 master/slave data for autoneg links, resolves link mode, or reads PMA speed for forced links. EEE ethtool set/get reads and writes EEE advertisement registers and restarts AN when changes require it.

PLCA helpers validate the OATC14 ID, read or modify control/timer/burst registers, disable before partial reconfiguration when requested, and enable at the end. OATC14 cable tests check HDD capability, set control/start bits, poll valid results, report ethtool pair-A results, and clear control. OATC14 SQI caches capability in `phydev->oatc14_sqi_capability` on first use and then reads SQI+ or SQI registers.

## State and Persistence
Most state is in `phydev`: supported link modes, EEE modes, link, speed, duplex, pause, partner advertising, master/slave fields, cached `pma_extable`, and cached OATC14 SQI capability. Hardware MMD registers persist forced speeds, AN advertisement, EEE advertisement, PLCA config, loopback, fast retrain, cable test, and low-power state.

## Dependencies and Integration Points
The file depends on MDIO/MII definitions, phylib internals, ethtool netlink constants, `mdio-open-alliance.h`, and exported symbol users throughout `drivers/net/phy`. Many device drivers in this subset call these helpers directly, including GPY, NCN26000, and NXP C45.

## Risks
Generic helpers must tolerate devices with incomplete or buggy optional registers. The file intentionally ignores some EEE capability read failures, which is pragmatic but can hide hardware issues. BASE-T1 and conventional Clause 45 paths share APIs but use different registers, so incorrect `pma_extable` detection can misconfigure devices. Latched-low link handling must remain consistent with polling vs IRQ behavior. PLCA partial updates must preserve unmodified fields correctly.

## Test Signals
Test with conventional Clause 45 copper, BASE-T1, and 10BASE-T1S/OATC14 PHYs. Cover forced speeds, autoneg restart/change detection, master/slave modes, LPA decoding, EEE enable/disable and advertised-mode validation, PMA suspend/resume unsupported cases, loopback, fast retrain, PLCA get/set/status, OATC14 cable tests, SQI/SQI+ capability caching, and exported-symbol build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-c45.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-caps.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy-caps.h

## Purpose
This internal phylib header declares the link capability abstraction used to convert among speed/duplex pairs, ethtool link modes, PHY interface modes, and link media.

## Important APIs, Types, and Functions
The anonymous enum defines capability indices from 10 half/full through 1.6T full duplex, with `LINK_CAPA_ALL` covering the complete mask. `struct link_capabilities` stores speed, duplex, and an ethtool linkmode mask. Declared functions include `phy_caps_init()`, `phy_caps_speeds()`, `phy_caps_linkmode_max_speed()`, `phy_caps_valid()`, `phy_caps_linkmodes()`, `phy_caps_from_interface()`, lookup helpers by linkmode or speed/duplex, and medium conversion helpers.

## Control Flow
The header itself has no runtime flow, but the declared implementation is intended to initialize capability tables, derive supported speeds, filter by maximum speed, validate requested speed/duplex combinations, and map interface/media constraints into ethtool linkmode sets.

## State and Persistence
There is no state in the header. Implementations likely maintain static capability data initialized by `phy_caps_init()`. Callers pass linkmode bitmaps that are modified or queried.

## Dependencies and Integration Points
It depends on `<linux/ethtool.h>` and `<linux/phy.h>`. The functions are internal phylib glue for PHY drivers, phylink, and ethtool-facing capability reporting.

## Risks
Capability translation tables must stay synchronized with ethtool link mode additions and PHY interface definitions. Incorrect duplex or medium mappings can cause advertised modes, validation, or interface selection to be wrong across many drivers.

## Test Signals
Test speed enumeration ordering, max-speed filtering, validity checks for half/full duplex, interface-to-capability mapping, medium lane filtering, and new ethtool link modes as they are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-caps.h -->
