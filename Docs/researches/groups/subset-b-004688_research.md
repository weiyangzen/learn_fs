# Research Report: subset-b-004688

This grouped report covers Linux PHY drivers under `sources/distributed-fs/ceph-client/drivers/net/phy/`. Each section is source-tree-aligned and is delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-ptp.c

## Purpose
`bcm-phy-ptp.c` provides the Broadcom PHY hardware timestamping and PTP hardware clock helper used by supported Broadcom PHY drivers. In this tree it is wired through `broadcom.c` via `bcm_ptp_probe()`, `bcm_ptp_config_init()`, and `bcm_ptp_stop()`. It exposes a `mii_timestamper` for packet timestamping, registers a PHC via `ptp_clock_register()`, supports one periodic output or external timestamp pin, and programs Broadcom IEEE 1588 expansion registers through `bcm_phy_*_exp()` helpers.

## Important APIs, Types, And Functions
The central private object is `struct bcm_ptp_private`, which stores the owning `phy_device`, `mii_timestamper`, `ptp_clock`, `ptp_clock_info`, one `ptp_pin_desc`, a mutex for MDIO/PTP register sequencing, the TX timestamp queue, current TX/RX hwtstamp state, cached `NSE_CTRL`, pin activity, and delayed work for pin functions. `struct bcm_ptp_skb_cb` overlays `skb->cb` with sequence ID, PTP message type, expiry, and one-step discard state. `struct bcm_ptp_capture` is the normalized hardware timestamp record read from the timestamp FIFO.

The PHC callbacks are `bcm_ptp_gettimex()`, `bcm_ptp_settime()`, `bcm_ptp_adjtime()`, `bcm_ptp_adjfine()`, `bcm_ptp_enable()`, `bcm_ptp_verify()`, and `bcm_ptp_do_aux_work()`. The `mii_timestamper` callbacks are `bcm_ptp_rxtstamp()`, `bcm_ptp_txtstamp()`, `bcm_ptp_hwtstamp_set()`, `bcm_ptp_hwtstamp_get()`, and `bcm_ptp_ts_info()`. External users call exported `bcm_ptp_probe()`, `bcm_ptp_config_init()`, and `bcm_ptp_stop()`.

## Control Flow
Probe accepts only supported models, currently `PHY_ID_BCM54210E`, allocates state, registers a PHC, marks legacy timestamp selection with `phydev->default_timestamp`, installs `phydev->mii_ts`, and initializes queues and callbacks. Runtime PHC reads use `bcm_ptp_framesync_ts()`: disable active framesync mode, capture a pre/post system timestamp if requested, issue a CPU framesync with capture enabled, poll `INTR_STATUS` for `INTC_FSYNC`, read heartbeat registers, then restore the original `NSE_CTRL`. Setting and stepping time writes `TIME_CODE_*` and `NCO_TIME_*` through the shadow-load path and triggers `NSE_INIT`. Frequency adjustment converts scaled ppm into the Broadcom NCO base frequency and loads `NCO_FREQ_*` on a framesync.

For TX timestamping, `bcm_ptp_txtstamp()` parses the PTP header, records message type and sequence ID, handles one-step discard semantics for Sync/Pdelay Response, queues the skb, and schedules the PHC worker. `bcm_ptp_do_aux_work()` drains hardware timestamp records with `bcm_ptp_get_tstamp()` while matching them against queued skbs. RX timestamping expects the PHY to insert a 64-bit seconds/nanoseconds timestamp after the PTP header; `bcm_ptp_rxtstamp()` converts it to an skb hwtstamp and removes the inserted bytes.

Per-output and external timestamp operations share one pin. `bcm_ptp_perout_locked()` accepts only 1 PPS, writes period and pulse fields in 8 ns units, then delayed work schedules one-shot sync outputs aligned to whole seconds. `bcm_ptp_extts_locked()` configures framesync capture from SYNC1 and delayed work polls `INTR_STATUS` every quarter second, emits `PTP_CLOCK_EXTTS`, and reschedules.

## State And Persistence
All persistent state is kernel runtime state: PHY registers, `priv->nse_ctrl`, timestamping mode flags, `tx_queue`, `pin_active`, and scheduled work. There is no filesystem persistence. The hardware clock itself persists in PHY/NCO registers until reset or reconfigured. `bcm_ptp_stop()` cancels the PTP worker and active pin function, but does not unregister the PHC; ownership is devm/module lifetime through the caller.

## Dependencies And Integration Points
The file depends on phylib, Linux PTP clock APIs, net timestamping APIs, skb queues, delayed work, `ptp_classify` header parsing, and Broadcom register helpers from `bcm-phy-lib.h`. It integrates with MAC drivers through `phydev->mii_ts`, with ethtool timestamp reporting via `ts_info`, and with `broadcom.c` for lifecycle hooks. It writes Broadcom expansion registers such as `NSE_CTRL`, `TIME_SYNC`, `TX_EVENT_MODE`, `RX_EVENT_MODE`, and NCO/heartbeat registers.

## Risks And Edge Cases
Timestamp capture polling has a short fixed loop and can return `-ETIMEDOUT` if `INTC_FSYNC` does not arrive. TX matching uses only sequence ID and message type, so pathological duplicate PTP messages can be ambiguous. RX timestamp insertion assumes an 8-byte timestamp immediately after the PTP header and trims the skb in place. One pin can be configured as either perout or extts, so concurrent requests return `-EBUSY` unless the pin function matches. Perout is limited to 1 PPS and bounds pulse width to hardware limits. All hardware register sequences rely on the private mutex; callers must avoid independent unsynchronized writes to the same PTP registers.

## Test Signals
Useful test evidence includes successful `ethtool -T` PHC exposure, hwtstamp ioctl mode changes, `ptp4l` or `phc2sys` operation on BCM54210E, TX timestamp completion for two-step modes, one-step discard behavior, RX packet trimming with valid hwtstamps, and perout/extts pin events. Regression tests should exercise timeout paths, queue expiry, disabling timestamping while TX skbs are queued, and suspend/driver stop cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm54140.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm54140.c

## Purpose
`bcm54140.c` is a Broadcom BCM54140 quad SGMII/QSGMII copper/fiber Gigabit PHY driver. It handles per-port setup, package-global interrupt masking, hardware monitoring for temperature and supply rails, downshift and energy-detect power-down tunables, cable test delegation, and a B0 PLL erratum workaround.

## Important APIs, Types, And Functions
`struct bcm54140_priv` stores the package port index, base MDIO address, and hwmon alarm latch lock/state when `CONFIG_HWMON` is enabled. `enum bcm54140_global_phy` identifies package address zero for global register access. HWMON callbacks include visibility, read/write, string labels, alarm latching, and conversion helpers for temperature, 1.0 V, and 3.3 V readings. Package helpers `bcm54140_base_read_rdb()` and `bcm54140_base_write_rdb()` access global RDB registers through `__phy_package_*()` under the MDIO bus lock.

Driver callbacks are `bcm54140_probe()`, `bcm54140_config_init()`, `bcm54140_handle_interrupt()`, `bcm54140_config_intr()`, `bcm54140_get_tunable()`, and `bcm54140_set_tunable()`. It registers one `phy_driver` with `PHY_ID_BCM54140`, `PHY_POLL_CABLE_TEST`, `PHY_GBIT_FEATURES`, `genphy_suspend/resume`, `genphy_soft_reset`, and Broadcom RDB cable test helpers.

## Control Flow
Probe allocates private state, scans adjacent MDIO addresses to find a contiguous range of same-ID PHYs, derives the local port and package base address, joins the PHY package, and performs package-once hwmon initialization. The package scan walks forward and backward from the current address, reads PHY IDs directly with `mdiobus_read()`, and validates the discovered range is a multiple of four.

Config init first applies the B0 workaround when revision bits match: clear a spare bit, power down/up through BMCR, then restore the spare bit. It then unmasks link/speed/duplex events in the per-port RDB interrupt mask, configures LED link speed/activity behavior, and clears super-isolate mode. Interrupt configuration combines per-port and top-level state: the per-port ISR is read to acknowledge events, while the base/global top interrupt mask enables or disables the current port bit. `handle_interrupt()` reads per-port ISR and IMR, inverts the mask semantics, and triggers the PHY state machine when an enabled event is pending.

HWMON is enabled once per package by powering the monitor, selecting round-robin mode, and registering a device. Reads convert raw RDB monitor values to millidegrees C or millivolts; threshold writes clamp to representable ranges and write masked raw values. Alarm bits are latched in software because hardware ISR reads can clear status.

## State And Persistence
Runtime state lives in `phydev->priv`, the PHY package membership, hwmon alarm latch, and RDB/BMCR registers. Tunables persist only in PHY registers until reset. There is no persistent host storage. Package-global state is shared across the four ports, so the base address and `phy_package_init_once()` gate are important to avoid duplicate monitor registration.

## Dependencies And Integration Points
The driver depends on phylib, `bcm-phy-lib.h` RDB helpers, `phylib.h` package APIs, Linux hwmon, ethtool PHY tunables, and Broadcom cable-test helpers. It integrates with the kernel PHY driver table through `module_phy_driver()` and with userspace through hwmon sysfs and ethtool downshift/EDPD/cable-test interfaces.

## Risks And Edge Cases
The base-address scanner assumes all four ports are contiguous and the surrounding same-ID PHYs form ranges divisible by four; multiple adjacent packages are handled by modulo arithmetic but bad strap/addressing can fail probe. RDB register masks use inverted semantics for interrupt masks; mistakes can produce silent interrupt storms or missed link events. HWMON alarm reads have clear-on-read behavior and require the software latch lock to avoid losing alarms. The B0 workaround power-cycles the PHY during init and should only run on the affected revision.

## Test Signals
Testing should confirm one hwmon device per quad package, correct `temp*_input`, `in*_input`, min/max writes and alarm clear behavior, per-port IRQ delivery, link/speed/duplex update on interrupts, ethtool downshift values including disabled/default/count-one paths, EDPD 2700/5400 ms handling, and cable-test delegation. Multi-port tests should verify only the matching top-level IMR bit changes for each port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm54140.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm63xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm63xx.c

## Purpose
`bcm63xx.c` is a small driver for Broadcom 63xx SoC internal PHYs. Its main job is to initialize the integrated PHY interrupt register, advertise pause support within documented limits, and let the shared Broadcom interrupt handler drive phylib state changes.

## Important APIs, Types, And Functions
The file defines the BCM63xx interrupt register `MII_BCM63XX_IR` and bits for global enable, duplex, speed, link, and global mask. `bcm63xx_config_init()` programs supported pause and initial interrupt mask/event bits. `bcm63xx_config_intr()` toggles the global mask based on `phydev->interrupts`. The two `phy_driver` entries match two OUI variants of the same internal PHY and use `bcm_phy_handle_interrupt()`.

## Control Flow
On init the driver sets `ETHTOOL_LINK_MODE_Pause_BIT` but deliberately avoids setting asymmetric pause because the datasheet marks that bit read-only. It globally masks interrupts, then writes a register value that globally enables interrupts while unmasking duplex, speed, and link events. When phylib enables interrupts, pending Broadcom interrupt status is acknowledged with `bcm_phy_ack_intr()` before clearing the global mask; disabling sets the global mask first and then acknowledges pending state.

## State And Persistence
The driver keeps no private state. Its state is entirely the PHY interrupt register and phylib fields such as supported link modes. Register state is reset-bound and not persisted outside hardware.

## Dependencies And Integration Points
It depends on phylib and shared helpers from `bcm-phy-lib.h`. It registers through `module_phy_driver()` and supports two MDIO IDs. Link handling is delegated to `bcm_phy_handle_interrupt()` and generic PHY functionality.

## Risks And Edge Cases
The interrupt register combines enable, mask, and status bits with vendor-specific polarity. Incorrect ordering can lose pending link changes. Since no suspend/resume or reset callbacks are provided, platform reset sequencing relies on generic phylib behavior and the MAC/MDIO integration.

## Test Signals
Test by probing both ID variants, confirming initial pause support, checking that link/speed/duplex interrupts trigger `phy_trigger_machine()` through the shared handler, and verifying polling fallback still reads link normally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm7xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm7xxx.c

## Purpose
`bcm7xxx.c` supports Broadcom BCM7xxx internal transceivers across 28 nm GPHY/EPHY, 40 nm EPHY, and 16 nm EPHY families. It applies hardware-specific AFE calibration recipes, enables APD/EEE, exposes stats, preserves stats over suspend, implements synthetic MMD access for 28 nm EPHY shadow registers, and registers many internal PHY IDs.

## Important APIs, Types, And Functions
`struct bcm7xxx_phy_priv` stores the per-PHY stats shadow array used by shared Broadcom stat helpers. The main init families are `bcm7xxx_28nm_config_init()`, `bcm7xxx_28nm_ephy_config_init()`, `bcm7xxx_16nm_ephy_config_init()`, and legacy `bcm7xxx_config_init()`. AFE recipes include `bcm7xxx_28nm_d0_afe_config_init()`, `bcm7xxx_28nm_e0_plus_afe_config_init()`, `bcm7xxx_28nm_a0_patch_afe_config_init()`, `bcm7xxx_28nm_ephy_01_afe_config_init()`, and `bcm7xxx_16nm_ephy_afe_config()`.

Other key functions are `bcm7xxx_28nm_ephy_read_mmd()` and `bcm7xxx_28nm_ephy_write_mmd()` for AN/PCS EEE registers, `bcm7xxx_28nm_get_tunable()` and `bcm7xxx_28nm_set_tunable()` for downshift, `bcm7xxx_28nm_suspend()` for stats preservation, and `bcm7xxx_28nm_probe()` for private allocation and optional clock enable. Macro templates build the `phy_driver` table for each process/interface family.

## Control Flow
Probe allocates stats storage sized by `bcm_phy_get_sset_count()`, enables an optional MDIO-device clock, and performs a dummy BMSR read to work around first-MDIO-read failures. For 28 nm GPHYs, config init derives revision/patch from dev flags or PHY ID bits, does a dummy read, selects the appropriate AFE workaround, enables jumbo frames, reads downshift, enables EEE only when downshift is disabled, and enables auto power down. Resume reapplies this full setup and restarts autonegotiation.

For 28 nm EPHYs, init may enter shadow mode 2, program bias trim and TL4 calibration reset for revision 0x01, enable 100TX EEE through shadowed PCS/AN registers, and enable APD through shadow mode 1. The synthetic MMD methods map a small set of standard AN/PCS MMD registers to shadow-mode-2 registers, returning `-EOPNOTSUPP` for unsupported devnum/regnum pairs.

For 16 nm EPHYs, the driver performs a long deterministic PLL/AFE/RCAL calibration sequence, computes adjusted RCAL codes from expansion register data, enables EEE, configures DLL auto power down and clock behavior, and enables APD. Legacy 40 nm/65 nm config enables 64-clock MDIO, toggles shadow mode, writes bias/false-carrier registers, and has an IDDQ suspend recipe.

## State And Persistence
State lives in hardware registers, the private stats shadow, optional clock enable state, and phylib advertised/tunable fields. Suspend snapshots Broadcom stats under `phydev->lock` before generic suspend. Calibration state is not persisted in software; resume replays the recipes.

## Dependencies And Integration Points
The driver uses phylib, Broadcom helper functions in `bcm-phy-lib.h`, Broadcom PHY IDs/flags from `brcmphy.h`, optional clock management, ethtool tunables/stats, and MDIO MMD constants. It integrates with device-tree/platform data through `phydev->dev_flags` for revision/patch and generic PHY internal flags.

## Risks And Edge Cases
Most values are hardware magic from vendor errata; small register or delay changes can affect analog link quality. Shadow mode access must be reset on all error paths to avoid corrupting later MDIO operations. The read_mmd/write_mmd implementation intentionally supports only EEE-related AN/PCS registers. EEE is disabled when downshift is enabled because the combination can prevent link-up; tunable changes restart autoneg. The 16 nm calibration sequence has many unchecked `bcm_phy_write_misc()` calls, so failed MDIO writes may not always abort immediately.

## Test Signals
Validation should cover every macro family: 28 nm GPHY downshift/EEE/APD behavior, 28 nm EPHY synthetic MMD reads for EEE registers, 16 nm EPHY link after resume, legacy suspend IDDQ mode, ethtool stats continuity across suspend, optional clock enable, and known revisions that select each AFE recipe. Link interoperability and analog compliance tests are especially important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm7xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm84881.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm84881.c

## Purpose
`bcm84881.c` supports Broadcom BCM84881, BCM84891, and BCM84892 NBASE-T Clause 45 PHYs commonly found in SFP+ modules. It manages host-side interface selection, feature filtering, Clause 45 autonegotiation plus 1000Base-T advertisement, link-status resolution, in-band capability disabling, and BCM8489x LED offload support.

## Important APIs, Types, And Functions
`bcm84881_probe()` validates Clause 45 PMAPMD and AN MMD presence. `bcm84881_config_init()` accepts SGMII, 2500BASE-X, or 10GBASE-R and fills possible interfaces; `bcm8489x_config_init()` accepts only USXGMII and clears PMAPMD low-power once. `bcm84881_get_features()` uses C45 PMA abilities but clears unsupported 10M modes. `bcm84881_config_aneg()`, `bcm84881_aneg_done()`, and `bcm84881_read_status()` implement the link negotiation flow. LED functions map netdev LED triggers to PMAPMD mask/ctl registers for two LEDs.

## Control Flow
Probe fails non-C45 devices or packages missing PMAPMD/AN. Config init advertises possible host interfaces and rejects mismatches early. Autoneg waits for PMAPMD reset to clear so firmware does not overwrite advertisements, forces MDI auto, rejects disabled autoneg, applies generic C45 AN configuration, writes 1000Base-T advertisement through the embedded Clause 22 register window under MMD AN, and restarts AN if settings changed.

Read status first checks AN restart, then both C45 AN status and C22 BMSR to derive autoneg complete and link. It clears link partner state, resolves C45/C22 partner advertisement when complete, and rejects disabled autoneg by forcing link down. For USXGMII variants, it keeps the host interface fixed and relies on resolved copper speed. For BCM84881, it reads vendor register `0x4011` to update the host interface and speed based on the PHY's rate-adaptation mode, then reads MDIX.

LED control writes per-LED low and extended source masks, then sets the LED controller only if a source is active. Trigger support excludes unrepresentable 100-only offload because the hardware source lights for 100 and 1000 together.

## State And Persistence
No private state is allocated. Runtime state is in PHY C45 registers, possible interface bitmaps, phylib resolved speed/duplex/pause/mdix fields, and LED hardware registers. Register settings are reset-bound.

## Dependencies And Integration Points
The driver depends on Linux Clause 45 genphy helpers, phylib LED trigger APIs, PMAPMD/AN MMD access, and ethtool linkmode conversion helpers. It registers three PHY IDs and explicitly disables in-band negotiation via `.inband_caps` because the observed module does not provide a usable control word.

## Risks And Edge Cases
Support is intentionally incomplete and based on tested SFP+ module behavior. Autoneg disable is rejected because it does not work reliably. Host interface changes are inferred from a vendor register for non-USXGMII devices and must match MAC reconfiguration expectations. Clause 45 module autoloading is noted as problematic in a comment. LED trigger mapping has hardware precision limits.

## Test Signals
Test with BCM84881 SFP+ modules at 100M, 1G, 2.5G, 5G, and 10G where supported, verifying host interface transitions and MAC reconfiguration. Test BCM84891/92 in USXGMII without interface changes, autoneg restart behavior after advertisement changes, `ethtool -k/-s` link modes, LED brightness and trigger offload get/set, and failure on non-C45 or missing-MMD devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm84881.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm87xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm87xx.c

## Purpose
`bcm87xx.c` supports Broadcom BCM8706 and BCM8727 10G Clause 45 PHYs. It provides minimal feature advertisement, optional device-tree register initialization, fixed 10G status reading, LASI interrupt control, and custom matching using C45 device IDs.

## Important APIs, Types, And Functions
When OF MDIO is enabled, `bcm87xx_of_reg_init()` parses `broadcom,c45-reg-init` tuples of `<devid reg mask value>` and applies masked or direct MMD writes. `bcm87xx_get_features()` adds `10000baseR_FEC` support. `bcm87xx_read_status()` reads PMAPMD signal detect, PCS 10GBASE-R status, and PHYXS lane status. `bcm87xx_config_intr()` toggles PCS LASI control and acknowledges LASI status. `bcm87xx_match_phy_device()` matches C45 device ID slot 4 against the driver ID.

## Control Flow
Config init only applies optional OF register programming. Autoneg configuration returns `-EINVAL`, reflecting fixed/no-aneg operation. Status read checks three hardware conditions in sequence; any missing signal, PCS lock, or lane status clears link. On success it sets speed 10000, full duplex, and link up. Interrupt enable reads LASI control, clears pending status, sets bit 0 to enable; disable clears bit 0 and then reads status. The interrupt handler reads LASI status and triggers the PHY state machine when nonzero.

## State And Persistence
There is no driver-private state. Optional OF register initialization writes persistent-until-reset hardware configuration. Link state is reported in `phydev`.

## Dependencies And Integration Points
The driver depends on phylib, Clause 45 MMD access, optional OF MDIO properties, and generic 10G constants. It integrates via `module_phy_driver()` and two static PHY IDs. Device-tree board files can use `broadcom,c45-reg-init` for platform-specific register fixes.

## Risks And Edge Cases
`bcm87xx_handle_interrupt()` reads `BCM87XX_LASI_STATUS` through `phy_read()` rather than `phy_read_mmd(MDIO_MMD_PCS, ...)`, while `config_intr()` uses MMD access; this is a notable audit point. The OF tuple parser ignores trailing incomplete cells and uses mask semantics where `val = old & mask | val_bits`, which differs from common clear-mask/write semantics. No autoneg path exists.

## Test Signals
Test fixed 10G link up/down on signal loss, PCS loss, and PHYXS lane loss; LASI IRQ enable/disable; C45 device matching for both IDs; and representative `broadcom,c45-reg-init` board data including masked writes and direct writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm87xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/broadcom.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/broadcom.c

## Purpose
`broadcom.c` is the main Broadcom PHY driver collection for BCM54xx Gigabit PHYs, BCM54810/54811 BroadR-Reach PHYs, BCM54616S fiber/SerDes modes, Fast Ethernet BCM5221/5241/AC131 PHYs, and several internal switch PHY IDs. It centralizes Broadcom copper initialization, interrupt setup through shared helpers, RGMII delay handling, APD/IDDQ power management, Wake-on-LAN, PTP hook-up, statistics, link-change DAC wake tweaks, and BroadR-Reach status/autoneg support.

## Important APIs, Types, And Functions
`struct bcm54xx_phy_priv` stores stats, optional Broadcom PTP state, wake IRQ state, and BroadR-Reach mode. `struct bcm54616s_phy_priv` tracks whether the BCM54616S fiber path is 1000BASE-X. Init helpers include `bcm54xx_config_clock_delay()`, `bcm54210e_config_init()`, `bcm54612e_config_init()`, `bcm54616s_config_init()`, `bcm54xx_phydsp_config()`, `bcm54xx_adjust_rxrefclk()`, `bcm54811_config_init()`, and `bcm54xx_config_init()`.

Power/WoL functions are `bcm54xx_suspend()`, `bcm54xx_resume()`, `bcm54xx_iddq_set()`, `bcm54xx_phy_get_wol()`, `bcm54xx_phy_set_wol()`, and `bcm54xx_set_wakeup_irq()`. BroadR-Reach functions are `bcm5481x_set_brrmode()`, `bcm5481x_read_abilities()`, `bcm5481_config_aneg()`, `bcm54811_config_aneg()`, `bcm54811_read_status()`, and supporting LRE helpers. Fast Ethernet helpers are `brcm_fet_config_init()`, `brcm_fet_config_intr()`, `brcm_fet_handle_interrupt()`, `brcm_fet_suspend()`, `bcm5221_config_aneg()`, and `bcm5221_read_status()`.

## Control Flow
Common BCM54xx probe allocates stats, tries `bcm_ptp_probe()` for supported PTP-capable models, obtains an optional wake GPIO, requests a disabled wake IRQ if present, and marks the MDIO device wake-capable if either normal PHY interrupt or wake IRQ exists. Common config masks interrupts globally, programs the per-event interrupt mask, applies model-specific setup, runs PHY DSP workarounds, configures LEDs unless the PHY is on an SFP module, initializes PTP registers if present, and acknowledges Wake-on-LAN interrupt status.

RGMII delay setup updates the AUXCTL RX skew bit and shadow clock-control TX delay bit according to `phydev->interface`. BCM54210E can force master mode. BCM54612E/54811 can route CLK125 to LED4 when the reference clock is used. BCM54616S switches between SGMII and 1000BASE-X register sets by powering down SerDes, changing shadow mode, and powering interfaces back up. The PHY DSP path enables SMDSP, applies model-specific expansion register workarounds, and disables SMDSP again.

Suspend snapshots stats, stops active PTP workers, acknowledges WoL status, enables wake IRQ if WoL is active, otherwise powers down BMCR and optionally enters IDDQ. Resume disables wake IRQ, exits IDDQ, resumes BMCR, waits for internal reset to clear, optionally soft-resets, and reruns common config. Link-change notify adjusts DAC wake bits for 10M links when auto power down is enabled.

BroadR-Reach flow reads the `brr-mode` DT property, toggles the LRE overlay, switches supported link modes to single-pair/LDS capabilities, and uses LRE-specific autoneg/status functions. BCM54811 disables LDS autoneg in BRR mode because the datasheet requires a reserved bit to be cleared after reset. Fast Ethernet flow resets, programs interrupt masks, shadow LED/MDIX/APD state, and uses special suspend low-power writes; BCM5221 adds manual/auto MDIX programming and status decoding.

## State And Persistence
Driver state is held in `phydev->priv`, stats shadow arrays, optional PTP state owned by `bcm-phy-ptp.c`, wake IRQ enabled state, and BRR mode. Hardware state spans normal Clause 22 registers, Broadcom shadow registers, expansion registers, BMCR power state, WoL registers, and LRE registers. There is no filesystem persistence. Resume paths deliberately replay configuration because suspend/reset loses hardware state.

## Dependencies And Integration Points
The file depends on `bcm-phy-lib.h` for shared Broadcom register/stat/interrupt/WoL/LED helpers, `bcm-phy-ptp.c` exported helpers for PTP, phylib genphy/c37/LRE helpers, Linux GPIO/IRQ wake APIs, OF properties such as `brr-mode` and `enet-phy-lane-swap`, ethtool stats/WoL/LED interfaces, and Broadcom PHY IDs from `brcmphy.h`. It registers a large `phy_driver` array through `module_phy_driver()`.

## Risks And Edge Cases
Many branches are model-specific and register values are undocumented or errata-driven. SFP modules are deliberately excluded from LED reprogramming because LED pins may carry LOS signals. WoL support is suppressed unless an IRQ path exists, allowing MAC drivers to offer fallback wake. `bcm54xx_set_wakeup_irq()` calls IRQ wake helpers when `phy_interrupt_is_valid()` or `wake_irq` exists; platforms without a sideband GPIO but with normal PHY IRQ need valid IRQ wake behavior. Fast Ethernet reset tolerates `-EIO` on one read because of MDC turnaround limits. BroadR-Reach mode alters the meaning of supported, advertising, master/slave, and link partner data and must be kept separated from IEEE mode.

## Test Signals
Useful tests include probing each major model family, RGMII delay modes, CLK125 behavior with `PHY_BRCM_RX_REFCLK_UNUSED`, WoL enable/suspend/resume with main IRQ and wake GPIO, PTP exposure for BCM54210E, stats preservation across suspend, SFP LED non-reprogramming, BroadR-Reach DT mode supported/adverting/status paths, BCM54616S 1000BASE-X status, Fast Ethernet interrupt and suspend behavior, and BCM5221 MDIX manual/auto controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/broadcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/cicada.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/cicada.c

## Purpose
`cicada.c` is a legacy Cicada/Vitesse Cis8201/Cis8204 PHY driver. It performs basic extended-control initialization and implements vendor interrupt mask/status handling for link, speed, and duplex changes.

## Important APIs, Types, And Functions
The file defines Cicada extended control, interrupt mask/status, and auxiliary status register constants. `cis820x_config_init()` writes initial values to `MII_CIS8201_AUX_CONSTAT` and `MII_CIS8201_EXT_CON1`. `cis820x_ack_interrupt()` clears pending status by reading `MII_CIS8201_ISTAT`. `cis820x_config_intr()` enables or disables the interrupt mask. `cis820x_handle_interrupt()` triggers phylib on speed/link/duplex interrupt status.

## Control Flow
Initialization writes vendor defaults and returns the first error. When enabling interrupts, the driver acknowledges pending status first and writes `MII_CIS8201_IMASK_MASK`; when disabling, it writes zero to the mask register and then acknowledges. The IRQ handler reads status, treats any of the speed/link/duplex status bits as actionable, and calls `phy_trigger_machine()`.

## State And Persistence
There is no private state. Runtime state is only PHY register configuration and phylib link state.

## Dependencies And Integration Points
The driver depends on phylib and standard module/interrupt headers. It registers two PHY IDs through `module_phy_driver()`. Generic PHY code handles autonegotiation and link status outside the vendor interrupt/init paths.

## Risks And Edge Cases
The mask/status register naming is easy to confuse because the same high bits are used in mask and status definitions. The driver has no suspend/resume callbacks and no explicit reset handling. It includes many legacy headers that are not functionally used.

## Test Signals
Test Cis8201 and Cis8204 MDIO IDs, initialization writes, interrupt enable/disable ordering, and IRQ behavior for link, speed, and duplex changes. Polling mode should fall back to generic PHY status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/cicada.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/cortina.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/cortina.c

## Purpose
`cortina.c` is a minimal Cortina CS4340 EDC/CDR 10G Ethernet PHY driver. It validates the actual chip ID through Clause 45 reads and reports fixed 10G link status based on a GPIO interrupt/status register bit.

## Important APIs, Types, And Functions
`cortina_read_reg()` reads device 0 Clause 45 registers through `mdiobus_c45_read()`. `cortina_probe()` reads chip ID LSB/MSB registers, composes the PHY ID, and verifies it matches `phydev->drv->phy_id`. `cortina_read_status()` reads `VILLA_GLOBAL_GPIO_1_INTS`; bit `0x8` means EDC converged/link up and sets speed 10000, full duplex, and link up. The driver uses `gen10g_config_aneg()` for `.config_aneg`.

## Control Flow
Probe is a hard identity check for DT/MDIO binding correctness. Status read is single-register: if the EDC-converged bit is present, link is reported as 10G full duplex; otherwise link is down. Errors propagate from C45 reads. The driver table exposes `PHY_10GBIT_FEATURES` and one exact PHY ID.

## State And Persistence
No private state is kept. The only state is hardware status and phylib fields updated by `read_status()`.

## Dependencies And Integration Points
The driver depends on phylib, Clause 45 MDIO bus access, and generic 10G phylib helpers. It registers one `mdio_device_id` and integrates with device-tree/platform PHY matching.

## Risks And Edge Cases
The driver does not manage interrupts, power, reset, or detailed PCS state. Link state depends entirely on one vendor GPIO status bit. Probe composes ID as `id_lsb << 16 | id_msb`, so board expectations must match that register ordering.

## Test Signals
Test probe with correct and incorrect chip IDs, 10G link up/down based on `VILLA_GLOBAL_GPIO_1_INTS`, C45 read error propagation, and interoperability with MACs expecting fixed 10G full-duplex PHY status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/cortina.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/davicom.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/davicom.c

## Purpose
`davicom.c` supports Davicom DM9161E/B/C/A and DM9131 10/100 PHYs. It configures MII/RMII mode, scrambler/10BT defaults, isolates the PHY while changing autoneg settings, and implements vendor interrupt handling.

## Important APIs, Types, And Functions
Register definitions cover the DM9161 SCR, interrupt register, and 10BTCSR. `dm9161_config_init()` isolates the PHY, validates `phydev->interface`, writes MII or RMII SCR defaults, restores 10BTCSR, and enables autoneg. `dm9161_config_aneg()` isolates before delegating to `genphy_config_aneg()`. `dm9161_config_intr()`, `dm9161_ack_interrupt()`, and `dm9161_handle_interrupt()` implement link/speed/duplex interrupt handling.

## Control Flow
Initialization starts by writing `BMCR_ISOLATE`, then selects SCR value based on MII versus RMII. Unsupported interfaces return `-EINVAL`. After vendor register setup, BMCR is written with `BMCR_ANENABLE` to reconnect and enable autoneg. Interrupt enable clears pending state, unmasks stop/mask bits, and writes the interrupt register; disable masks all interrupt sources before acknowledging. The handler reads the interrupt register and triggers phylib only when change bits are present.

## State And Persistence
The driver has no private state. Register configuration persists until PHY reset. The DM9131 entry only wires interrupts and does not use the DM9161 config init/aneg paths.

## Dependencies And Integration Points
The file depends on phylib and generic autoneg. It registers four PHY IDs. MAC/platform integration must provide a supported `phydev->interface` for DM9161 variants.

## Risks And Edge Cases
Incorrect interface mode causes init failure. Isolating before autoneg/config changes can briefly remove the PHY from the bus/link path. Interrupt status and enable bits share one register with separate high/low fields. The `DM9161_DELAY` macro is unused.

## Test Signals
Test MII and RMII initialization, unsupported interface failure, autoneg after isolate, link/speed/duplex interrupt handling, and the DM9131 path where generic init is used but vendor interrupts are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/davicom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83640.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83640.c

## Purpose
`dp83640.c` is the National Semiconductor/TI DP83640 PHYTER driver with full PHY timestamping and PTP hardware clock support. It registers one PHC per MII bus, can synchronize multiple DP83640 PHYs on the same bus through broadcast writes and a calibration GPIO, handles TX/RX/event status frames, exposes `mii_timestamper`, and implements ordinary PHY interrupt handling.

## Important APIs, Types, And Functions
`struct dp83640_private` stores per-PHY timestamping state, queues, RX timestamp pool, `mii_timestamper`, and a pointer to the shared `dp83640_clock`. `struct dp83640_clock` represents one PHC per MDIO bus, tracks the current extended register page, the chosen master PHY, the list of slave PHYs, clock locks, pin config, and the registered `ptp_clock`. Timestamp formats are `struct phy_rxts`, `struct phy_txts`, and software `struct rxts`.

PHC callbacks are `ptp_dp83640_adjfine()`, `ptp_dp83640_adjtime()`, `ptp_dp83640_gettime()`, `ptp_dp83640_settime()`, `ptp_dp83640_enable()`, and `ptp_dp83640_verify()`. Timestamp callbacks are `dp83640_hwtstamp_set()`, `dp83640_hwtstamp_get()`, `dp83640_rxtstamp()`, `dp83640_txtstamp()`, and `dp83640_ts_info()`. Lifecycle paths are `dp83640_probe()`, `dp83640_remove()`, `dp83640_config_init()`, `dp83640_soft_reset()`, `dp83640_config_intr()`, and `dp83640_handle_interrupt()`.

## Control Flow
Probe ignores the broadcast pseudo-address, obtains/creates the per-bus clock under the global clock list mutex, allocates per-PHY state, installs `phydev->mii_ts`, initializes queues and RX timestamp pool, and either becomes the chosen PHC provider or joins the clock's slave list. The chosen PHY is selected by module parameter `chosen_phy` or first available PHY. Clock init allocates dynamic pin configuration based on `gpio_tab` module parameters and holds a device reference to the MDIO bus.

Extended register access is page-based. `ext_read()` and `ext_write()` update `PAGESEL` by broadcast when the shared cached page changes; callers hold `extreg_lock`. Time setting and stepping write four 16-bit words to `PTP_TDR` and issue `PTP_LOAD_CLK` or `PTP_STEP_CLK`; frequency adjustment writes rate high/low by broadcast. Config init recalibrates when a chosen PHY and slaves exist, otherwise enables broadcast writes, enables status frames, and turns on the PTP clock.

Calibration disables status frames, enables PTP clocks on all PHYs, programs a calibration event and trigger on a shared GPIO, reads master/slave event timestamps, computes offsets, steps slave clocks by the difference plus a 16 ns hardware correction, and restores status-frame config. Periodic output programs trigger registers with start time and pulse width. External timestamp enable programs event registers and emits `PTP_CLOCK_EXTTS` from decoded status frames.

RX/TX timestamps arrive through PHY status frames, not direct register polling in the packet path. `dp83640_rxtstamp()` consumes status frames, decodes embedded RX/TX/event records, queues ordinary PTP RX skbs until matching timestamps arrive, and releases unmatched packets after a short timeout. RX matching uses PTP message type, sequence ID, and a 12-bit CRC hash of source port identity. TX timestamping queues skbs for later completion, while one-step Sync packets are freed because hardware inserts the timestamp on the wire.

## State And Persistence
State is runtime-only: global `phyter_clocks`, module parameters, per-bus clock objects, chosen/slave lists, cached extended page, PHC registration, per-PHY queues, RX timestamp pool, and hardware PTP/status-frame registers. Remove disables status frames, cancels delayed work, purges queues, unregisters the PHC when removing the chosen PHY, and destroys the shared clock when no PHYs remain.

## Dependencies And Integration Points
The driver depends on phylib, PTP clock APIs, `ptp_classify`, skb timestamping APIs, multicast address management on the attached netdevice, `dp83640_reg.h` register definitions, module parameters, and standard PHY interrupts. It integrates with MAC drivers through `phydev->mii_ts` and multicast status frames, and with userspace through PHC, hwtstamp ioctl, ethtool timestamp info, and PTP pin configuration.

## Risks And Edge Cases
The design assumes status frames can be delivered to the attached netdevice; missing multicast programming or no attached device weakens timestamp delivery. One PHC per MII bus means chosen/slave selection and hot-unplug ordering matter. RX timestamp pool exhaustion drops timestamp records. Matching by sequence/type/hash can fail under collisions or delayed status frames. Several timestamp/frame structures are cast directly from skb data and depend on PHY status-frame endian config. Calibration requires a valid shared GPIO pin; if absent, PHYs are not calibrated. Broadcast writes target MDIO address 31 and must not conflict with real devices. Queue timeouts are only two jiffies, so high latency can produce software fallback/no timestamp.

## Test Signals
Strong tests include PHC registration per bus, `chosen_phy` selection, multi-PHY calibration with measured offsets, hwtstamp filter programming for PTP v1/v2 L2/L4, TX one-step and two-step completion, RX timestamp matching and timeout delivery, external timestamp events on configured pins, periodic output triggers, status-frame multicast add/remove, interrupt enable/disable, and remove/hot-unplug cleanup without leaked PHCs or queued skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83640_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83640_reg.h

## Purpose
`dp83640_reg.h` is the register-definition companion for `dp83640.c`. It defines extended page numbers, PTP/status-frame register addresses, and bitfield constants for the DP83640 PHYTER PTP hardware block.

## Important APIs, Types, And Functions
The file is a pure header guarded by `HAVE_DP83640_REGISTERS`; it defines no functions or types. Important register groups include page 4 PTP control/time/status/rate/timestamp/event data registers, page 5 trigger/event/TX/RX/status-frame configuration registers, and page 6 clock-output/status-frame/source/offset registers. Bit definitions cover `PTP_CTL` commands, timestamp ready interrupts, trigger active/error state, rate direction/temp-rate, event status/data, trigger/event programming, TX/RX timestamp matching, status-frame configuration, clock output, SFD GPIO, interrupt GPIO, clock source, and PTP offset.

## Control Flow
There is no executable control flow. `dp83640.c` consumes these constants to select pages, write `PTP_TDR`, command `PTP_CTL`, configure status frames, program triggers/events, and parse status frame/event metadata.

## State And Persistence
The header does not hold state. It names hardware state that persists in DP83640 registers until reset or driver reconfiguration.

## Dependencies And Integration Points
It is included by `dp83640.c` and is tightly coupled to the DP83640 datasheet/register layout. Constants such as `PSF_ENDIAN`, `RX_TS_EN`, `SYNC_1STEP`, `TRIG_*`, and `EVNT_*` form the contract between the driver and PTP hardware.

## Risks And Edge Cases
Incorrect bit definitions would silently corrupt timestamping, trigger, or event behavior. Some comments note ambiguous field lengths, such as RX timestamp reads. Because the header was generated, manual edits should be reviewed against the datasheet and driver use sites.

## Test Signals
Evidence is indirect: DP83640 PHC operations, hwtstamp configuration, status-frame parsing, external timestamp, trigger/perout, rate adjustment, and interrupt-ready bits all validate the register map. Static checks should confirm every used bitfield mask/shift matches expected register width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83640_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83822.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83822.c

## Purpose
`dp83822.c` supports TI DP83822, DP83825, and DP83826 10/100 PHY families. It handles copper and fiber modes, Wake-on-LAN with secure-on password, interrupt masking, RGMII/RMII mode details, LED/GPIO pin configuration and LED trigger offload, OF-tuned clock output and analog settings, DP83826 DAC amplitude tuning, suspend/resume WoL behavior, and per-model driver registration.

## Important APIs, Types, And Functions
`struct dp83822_private` stores fiber signal polarity, fiber enable state, DAC settings, WoL state, GPIO2 clock output selection, enabled LED pins, TX amplitude index, and MAC termination index. WoL is handled by `dp83822_config_wol()`, `dp83822_set_wol()`, and `dp83822_get_wol()`. Interrupts use `dp83822_config_intr()` and `dp83822_handle_interrupt()`. Link/status/config paths include `dp83822_read_status()`, `dp83822_config_init()`, `dp83825_config_init()`, `dp83826_config_init()`, `dp8382x_config_rmii_mode()`, and `dp83822_phy_reset()`.

OF and probe helpers are `dp83822_of_init()`, `dp83822_of_init_leds()`, `dp83826_of_init()`, `dp83822_read_straps()`, `dp83822_attach_mdi_port()`, `dp8382x_probe()`, `dp83822_probe()`, and `dp83826_probe()`. LED offload functions map netdev triggers with `dp83822_led_mode()`, `dp83822_led_hw_is_supported()`, `dp83822_led_hw_control_set()`, and `dp83822_led_hw_control_get()`.

## Control Flow
Probe allocates private state and initializes optional indexes to `-1`; DP83822 additionally parses OF clock output, TX amplitude, MAC termination, and LED nodes, while DP83826 parses DAC plus/minus properties. `attach_mdi_port()` either honors an explicit phy port medium or reads strap register `SOR1` to determine fiber versus copper, plus backward-compatible `ti,fiber-mode` and `ti,link-loss-low` properties.

Common DP83822 config applies optional GPIO2 clock output, TX amplitude, MAC termination, LED pin mux, RGMII delay bits derived from internal-delay helpers, and RGMII mode enable/disable. In fiber mode it enables FX, restricts supported/advertising to fiber modes, disables autoneg in BMCR and linkmode bitmaps, writes fiber advertisement, and optionally selects active-low signal detect. DP83825 config applies RMII mode and WoL. DP83826 config toggles RMII mode and writes DAC VOD registers if OF values differ from defaults.

WoL programming writes the attached netdevice MAC address into vendor registers in the PHY's word order, optionally writes secure-on password, sets magic/secure bits, clears pending indication, and stores the requested state in private memory. Interrupt configuration sets enabled lower bits in MISR1/MISR2 and global PHYSCR bits. The handler reads both MISR registers and uses the enabled lower byte shifted into status position to decide whether to trigger phylib.

Read status has a fiber special case: if FX mode is enabled and link is down, it ensures the FX enable bit remains set; then it calls `genphy_read_status()` and overrides duplex/speed from PHYSTS. Suspend skips generic suspend when WoL is enabled; resume clears WoL indication after generic resume.

## State And Persistence
Private state stores configuration derived from OF, WoL requested options, and strap-derived media mode. Hardware state includes MMD vendor registers for WoL, LED/GPIO routing, RGMII/RMII mode, line driver swing, impedance, DAC amplitude, and interrupt masks. WoL state is replayed in config init to survive reset. No filesystem persistence exists.

## Dependencies And Integration Points
The driver depends on phylib, MMD vendor register access, OF/device properties, `phy_port` media attachment, ethtool WoL/LED/analog property helpers, and generic PHY suspend/resume/status. It registers seven PHY IDs using model macros. Userspace interacts through ethtool WoL and LED trigger offload; device tree controls GPIO2 clock output, RMII mode, LED pins, fiber mode, link-loss polarity, TX amplitude, MAC termination, and DP83826 DAC offsets.

## Risks And Edge Cases
`dp83822_config_wol()` assumes `phydev->attached_dev` is available when enabling WoL and requires a valid MAC address. LED mux constraints are strict: LED0 and COL(GPIO2) cannot both be MLED, COL cannot be clock output and LED, and RX_D3/GPIO3 LED is RMII-only. Fiber mode disables autoneg and mutates supported/advertising linkmodes. Interrupt status bits share registers with enable bits; the handler intentionally masks status by enabled lower bits. OF property validation rejects values outside lookup tables. Some `phy_modify_mmd()` calls in config init are not checked before continuing for optional analog/clock settings.

## Test Signals
Test copper and fiber attach modes, strap detection, legacy `ti,fiber-mode`, RGMII delay combinations, RMII master/slave property, WoL magic and secure-on across suspend/resume, MISR interrupt status gating, LED trigger set/get for every valid pin, invalid LED mux/property failures, DP83826 DAC property encoding, TX amplitude and MAC termination property validation, and reset path replaying config init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83822.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83848.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/dp83848.c

## Purpose
`dp83848.c` supports TI/NS DP83848C, TI DP83620, and TI TLK10X 10/100 PHYs. It provides interrupt control/status handling and a DP83620-specific autoneg initialization workaround.

## Important APIs, Types, And Functions
The file defines PHY IDs, MICR/MISR registers, interrupt enable bits, and status bits. `dp83848_ack_interrupt()` clears pending interrupt status by reading MISR. `dp83848_config_intr()` toggles MICR global interrupt bits and MISR source enables. `dp83848_handle_interrupt()` checks enabled link/autoneg/speed/duplex status bits and triggers phylib. `dp83848_config_init()` adjusts `phydev->autoneg` for DP83620 based on BMCR because BMSR always reports autoneg ability.

## Control Flow
Interrupt enable reads MICR, acknowledges pending status, sets output enable and interrupt enable, writes MISR source enables, then writes MICR. Disable clears MICR interrupt enable and acknowledges status. The handler reads MISR and only handles the interrupt when any configured status bits are present. The driver macro registers common callbacks for all IDs, with optional config init only on DP83620.

## State And Persistence
There is no private state. Register settings and `phydev->autoneg` are runtime-only and reset-bound. Suspend/resume use generic phylib callbacks.

## Dependencies And Integration Points
The driver depends on phylib, generic soft reset/suspend/resume, and standard module registration. It sets `PHY_RST_AFTER_CLK_EN`, indicating reset should occur after PHY clock enable.

## Risks And Edge Cases
Interrupt enable/status bits share the MISR register with lower source enables and upper status bits. DP83620 autoneg detection relies on BMCR initial state rather than BMSR. The driver does not expose WoL, LED, or custom status handling beyond interrupts.

## Test Signals
Test all four IDs, IRQ enable/disable, link/speed/duplex/autoneg complete interrupt delivery, DP83620 BMCR autoneg-disabled detection, generic suspend/resume, and reset-after-clock sequencing on platforms that gate PHY clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/dp83848.c -->
