# Research: subset-b-004691

Grouped research report for MediaTek, Amlogic Meson, Micrel, and Microchip PHY driver files. Each section is source-tree aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge.c

## Purpose
This file registers the MediaTek MT7530 and MT7531 gigabit PHY drivers used by MediaTek switch-integrated PHYs. It provides chip-specific `config_init` callbacks that apply vendor-recommended analog, DSP, LPI, downshift, power-save, and TX-delay tuning through standard paged MDIO, vendor MMDs, and the MediaTek token-ring debug access helpers from `mtk-phy-lib.c`.

## Important APIs, Types, and Functions
The key helpers are `mtk_gephy_config_init`, `mt7530_phy_config_init`, and `mt7531_phy_config_init`. `mtk_gephy_config_init` is the common tuning sequence: enable hardware auto-downshift on `MTK_PHY_PAGE_EXTENDED_1`, increase slave DSP ready time via `mtk_tr_modify`, force the 100M LPI MSE thresholds, and set the near-echo offset. `mt7530_phy_config_init` adds an extended-page post-update timer write. `mt7531_phy_config_init` adds link-down power saving, RX ADC low-power biasing, and TX pair delay selection for normal and test modes. The `mtk_gephy_driver` table binds exact PHY IDs `MTK_GPHY_ID_MT7530` and `MTK_GPHY_ID_MT7531` to those callbacks, generic suspend/resume, no-ack interrupt handling, and MediaTek page accessors.

## Control Flow
At module load, `module_phy_driver` registers both `phy_driver` entries and the MDIO table exposes the exact IDs for autoloading. During PHY probe/init, phylib calls the matching entry's `config_init`; each callback runs its MDIO writes synchronously and returns zero unless the callback ignores helper errors. Interrupt callbacks intentionally do not configure PHY interrupt bits because the surrounding switch handles interrupt delivery; `genphy_handle_interrupt_no_ack` just reports link changes without a PHY-local ack cycle.

## State and Persistence Behavior
The file does not allocate private state. Its persistent effect is hardware register state in MT7530/MT7531 PHY pages, token-ring nodes, and vendor MMD registers. The page state is delegated to `mtk_phy_read_page` and `mtk_phy_write_page`, so phylib can save/restore pages around paged operations. Runtime power management is generic `genphy_suspend`/`genphy_resume`; resume depends on phylib re-running initialization when required by the broader PHY lifecycle.

## Dependencies and Integration Points
The file depends on Linux phylib, `bitfield.h`, and `mtk.h`. It integrates with `mtk-phy-lib.c` for token-ring register modification and MediaTek page selection, with MDIO MMD vendor device 1 for analog/DSP knobs, and with the DSA/switch stack by avoiding direct PHY interrupt management. `FIELD_PREP` and mask constants make the vendor register values explicit and keep bitfield packing aligned with kernel helper semantics.

## Risks and Test Signals
The largest risk is silent misprogramming: several writes use `phy_modify_*` helpers without checking return values, so transient MDIO failures during init may be hidden. Token-ring addresses and magic tuning values are hardware-specific and should not be generalized to other MediaTek PHYs. MT7531 TX delay settings affect signal timing, so regressions may appear as marginal links rather than immediate probe failures. Useful tests include boot/probe on MT7530 and MT7531 switch PHYs, link-up/link-down across 10/100/1000 speeds, autoneg downshift behavior with bad cabling, suspend/resume, and verifying that switch-level interrupts still trigger phylib state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-phy-lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-phy-lib.c

## Purpose
This file is the shared MediaTek Ethernet PHY support library. It provides token-ring debug register access, MediaTek page read/write callbacks, and common LED hardware-control helpers used by MediaTek gigabit and 2.5G PHY drivers.

## Important APIs, Types, and Functions
Token-ring access is implemented by `__mtk_tr_access`, `__mtk_tr_read`, `__mtk_tr_write`, `__mtk_tr_modify`, and the exported wrappers `mtk_tr_modify`, `__mtk_tr_set_bits`, and `__mtk_tr_clr_bits`. Page callbacks are `mtk_phy_read_page` and `mtk_phy_write_page`. LED support is exported through `mtk_phy_led_hw_is_supported`, `mtk_phy_led_hw_ctrl_get`, `mtk_phy_led_hw_ctrl_set`, `mtk_phy_led_num_dly_cfg`, `mtk_phy_hw_led_on_set`, `mtk_phy_hw_led_blink_set`, and `mtk_phy_leds_state_init`. These APIs expect `phydev->priv` to point at `struct mtk_socphy_priv`, which stores per-LED mode bits in `led_state`.

## Control Flow
The token-ring wrappers build a 16-bit command from channel, node, data address, and read/write direction, then access registers `0x10` through `0x12`. The public `mtk_tr_modify` selects the MediaTek token-ring page `MTK_PHY_PAGE_EXTENDED_52B5`, performs a read/modify/write, and restores the standard page. LED get reads the selected LED on/blink MMD registers, updates cached state bits, and optionally maps register bits to netdev LED trigger rules. LED set derives on/blink bitmasks from netdev trigger rules, updates cached state, writes the ON control register with masked link/duplex fields, and writes the blink register. Force-on and force-blink helpers clear conflicting netdev-control state before touching the hardware registers.

## State and Persistence Behavior
The library persists state in two places: PHY hardware registers and `struct mtk_socphy_priv.led_state`. The LED state bitmap has separate bit ranges for LED0 and LED1, offset by 16 bits, with bits for forced on, forced blink, and netdev-trigger ownership. `mtk_phy_leds_state_init` reconstructs this software state by calling the driver's `led_hw_control_get` callback for both LEDs after probe or reset. Token-ring helpers do not maintain software state; they are pure hardware read/modify/write operations.

## Dependencies and Integration Points
The file depends on phylib, netdev LED trigger identifiers, MMD vendor device 2 LED registers from `mtk.h`, and module symbol exports for sibling MediaTek PHY modules. It integrates with kernel LED hardware control callbacks through the signatures expected by phylib, with `mtk-ge.c` through `mtk_tr_modify` and page accessors, and with any newer MediaTek PHY driver that supplies per-family `on_set`, `rx_blink_set`, and `tx_blink_set` masks.

## Risks and Test Signals
The token-ring helpers use raw `__phy_read`/`__phy_write` and do not propagate low-level errors from internal read/write functions, so callers can miss failed accesses. `mtk_tr_modify` always restores to the standard page with status `0`, which may hide earlier page-selection failures. LED trigger translation is sensitive to mask correctness; the TX/RX blink masks in `mtk.h` must match the target PHY family or netdev LED rules will program the wrong activity bits. Test signals include build/link coverage for all MediaTek PHY modules, LED trigger set/get round trips for both LED indices, force-on/blink transitions clearing netdev mode, invalid LED index rejection, page restore after token-ring operations, and MDIO fault injection where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-phy-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk.h

## Purpose
This header is the shared private interface for MediaTek Ethernet PHY drivers. It centralizes common register addresses, page IDs, LED bit definitions, the MediaTek PHY private LED state structure, and function prototypes exported by `mtk-phy-lib.c`.

## Important APIs, Types, and Functions
Important constants include `MTK_PHY_AUX_CTRL_AND_STATUS`, `MTK_PHY_ENABLE_DOWNSHIFT`, `MTK_EXT_PAGE_ACCESS`, `MTK_PHY_PAGE_EXTENDED_1`, `MTK_PHY_PAGE_STANDARD`, and `MTK_PHY_PAGE_EXTENDED_52B5`. LED control definitions cover vendor MMD2 registers `MTK_PHY_LED0_ON_CTRL`, `MTK_PHY_LED1_ON_CTRL`, `MTK_PHY_LED0_BLINK_CTRL`, and `MTK_PHY_LED1_BLINK_CTRL`; on/blink bits for link speeds, duplex, link down, force on, polarity, enable, collision, error, and force blink; and aggregate masks for gigabit and 2.5G PHY families. `struct mtk_socphy_priv` currently stores the `led_state` bitmap. Prototypes expose token-ring modification, page access, LED rule validation, LED rule get/set, numeric blink-delay normalization, forced LED modes, and LED state initialization.

## Control Flow
The header has no executable control flow, but it defines the contracts that drive `mtk-phy-lib.c` and MediaTek PHY driver callbacks. The page constants determine how phylib selects normal and extended pages. The LED aggregate masks are passed by concrete drivers into the common LED helpers to translate high-level netdev trigger rules into hardware on/blink register programming.

## State and Persistence Behavior
`struct mtk_socphy_priv` is the only software state declared here. Its `led_state` field persists per-LED ownership and forced-mode bits across LED operations, with `MTK_PHY_LED_STATE_FORCE_ON`, `MTK_PHY_LED_STATE_FORCE_BLINK`, and `MTK_PHY_LED_STATE_NETDEV` used as base bit positions. Hardware state persists in PHY paged registers and MMD vendor registers named by the header.

## Dependencies and Integration Points
The header assumes inclusion in kernel PHY code where `BIT`, `GENMASK`, `u8`, `u16`, `u32`, `bool`, `unsigned long`, and `struct phy_device` are available from Linux headers. It integrates MediaTek-specific PHY modules with phylib page callbacks, netdev LED hardware control callbacks, and shared token-ring helpers. The declarations are module-exported from `mtk-phy-lib.c`, so dependent MediaTek PHY objects can be compiled separately.

## Risks and Test Signals
The aggregate TX blink masks for the gigabit and 2.5G sets currently mirror RX blink bits, which is either intentional hardware aliasing or a high-risk typo because TX trigger rules would not program TX-specific blink bits. Because this header encodes register ABI rather than behavior, mistakes surface as incorrect LED behavior, failed page access, or bad PHY tuning in consumers. Test signals include compile coverage of every MediaTek PHY consumer, LED trigger tests that separately exercise RX and TX activity at 10/100/1000/2500 where supported, and static review whenever new PHY families reuse the shared masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/meson-gxl.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/meson-gxl.c

## Purpose
This file implements the Amlogic Meson internal PHY driver entries for Meson GXL and G12A internal PHYs. It programs Meson GXL private test banks for fractional PLL setup and works around a known GXL autonegotiation/LPA corruption condition; the G12A entry reuses SMSC/LAN87xx-style support.

## Important APIs, Types, and Functions
Private bank access uses `meson_gxl_open_banks`, `meson_gxl_close_banks`, `meson_gxl_read_reg`, and `meson_gxl_write_reg` through test registers `TSTCNTL`, `TSTREAD1`, and `TSTWRITE`. `meson_gxl_config_init` enables the fractional PLL and writes `FR_PLL_DIV1` and `FR_PLL_DIV0` in the BIST bank. `meson_gxl_read_status` wraps `genphy_read_status` with a pre-check for completed autonegotiation, WOL-bank `LPI_STATUS_RSV12`, `MII_LPA`, and `MII_EXPANSION` consistency. The `meson_gxl_phy` table registers exact IDs `0x01814400` and `0x01803301`.

## Control Flow
Bank reads and writes toggle `TSTCNTL_TEST_MODE` to open private bank access, issue a read or write command with bank and register fields, then always close the bank access before returning. GXL init writes the PLL sequence once during phylib config initialization. Status reads check whether autonegotiation is complete; if it is not complete, control falls through to the generic status read. If autoneg is reported complete but the WOL status bit is missing or the link partner never acknowledged while claiming autoneg support, the driver restarts autoneg instead of trusting the corrupted LPA state.

## State and Persistence Behavior
There is no private software allocation. Persistent state is the internal PHY register state: test-bank access mode, fractional PLL configuration, and autonegotiation state. `meson_gxl_close_banks` attempts to leave test mode disabled after every private access. For G12A, persistent behavior is mostly inherited from `smsc_phy_probe`, `smsc_phy_config_init`, `lan87xx_read_status`, SMSC interrupt handlers, and tunable callbacks.

## Dependencies and Integration Points
The file depends on phylib, MII definitions, ethtool types, bitfield helpers, netdevice headers, and `linux/smscphy.h`. It integrates with generic phylib for reset, suspend/resume, autoneg restart, and unsupported MMD callbacks. Interrupt handling for both entries uses SMSC helper functions, so the internal PHYs are treated as compatible with that interrupt model even though the GXL bank programming is Amlogic-specific.

## Risks and Test Signals
The GXL autoneg workaround depends on undocumented/private WOL-bank bit semantics and may cause repeated autoneg restarts if the bit is unreliable. Bank access is not protected by an explicit MDIO bus lock in these helpers, so correctness depends on phylib's callback serialization. `meson_gxl_config_init` comments label both divider writes as `FR_PLL_DIV1`, which is harmless but can confuse maintenance. Test signals include Meson GXL boot/link at 10/100, repeated autoneg with partners that do and do not support autoneg, forced modes, suspend/resume, interrupt-driven link changes via SMSC helpers, and G12A regression coverage for SMSC tunables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/meson-gxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/micrel.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/micrel.c

## Purpose
This is the large Micrel/Microchip PHY family driver for many 10/100, gigabit, switch-integrated, and newer LAN88xx/LAN96xx PHYs. It covers KSZ80xx/87xx/88xx/90xx/91xx/94xx devices plus LAN8804, LAN8814, LAN8841, LAN8842, and LAN9645X. Responsibilities include probe-time private state allocation, LED and RMII clock strap handling, interrupt setup, autoneg and MDIX quirks, RGMII skew/delay programming, silicon errata, cable diagnostics, ethtool stats/SQI/MSE, suspend/resume, in-band configuration, and PHY timestamping/PTP support.

## Important APIs, Types, and Functions
Core state types are `struct kszphy_type`, `struct kszphy_priv`, `struct kszphy_ptp_priv`, `struct lan8814_shared_priv`, and `struct lan8842_priv`. Generic helpers include `kszphy_probe`, `kszphy_config_init`, `kszphy_config_reset`, `kszphy_config_intr`, `kszphy_handle_interrupt`, `kszphy_suspend`, `kszphy_resume`, and hardware stats callbacks. Family-specific setup includes `ksz8041_config_init`, `ksz8081_config_aneg/read_status`, `ksz8061_config_init`, `ksz9021_config_init`, `ksz9031_config_init/read_status/set_loopback`, `ksz9131_config_init/config_aneg/read_status`, `ksz9477_config_init`, `lan8804_config_init`, `lan8814_probe/config_init`, `lan8841_probe/config_init`, `lan8842_probe/config_init`, and `lan9645x_config_init/suspend`. Cable diagnostics are implemented by `ksz9x31_*` and `ksz886x_*` flows. PTP support is implemented through LAN8814 shared-clock functions and LAN8841 per-device PHC functions, both exposed via `struct mii_timestamper`.

## Control Flow
At module load, `module_phy_driver(ksphy_driver)` registers a broad driver table, and the MDIO table advertises the matching PHY IDs. Probe normally calls `kszphy_probe`, which allocates `kszphy_priv`, records `driver_data`, parses `micrel,led-mode`, handles optional `rmii-ref` clock rate and reference-clock select properties, detects fiber mode, and honors legacy dev flags. LAN8814 and LAN8842 have custom probe flows for package joining, coma-mode GPIO release, SKU/PTP detection, PTP clock registration once per package, and port-local timestamp initialization. Initialization callbacks apply per-family register tuning: broadcast/NAND tree disable, RMII clock selection, LED mode, fiber-mode link masks, RGMII pad skew or DLL delay, EDPD, force-master errata, KSZ9477 MMD errata, LAN8814 QSGMII/USGMII selection, LAN8841 PTP and analog errata, LAN8842 LED/short-center-tap fixes, and LAN9645X adjacent-port errata.

## State and Persistence Behavior
`kszphy_priv` persists driver data, optional clock handle, LED mode, RMII clock-selection state, cable-test restoration bits, generic hardware counters, PHY error counters, PTP state, and whether LAN8814 PTP is available. `kszphy_ptp_priv` persists MII timestamp callbacks, TX/RX skb queues, RX timestamp lists, PTP filter/layer/version settings, PHC registration, GPIO pin config, and locks. LAN8814 uses `lan8814_shared_priv` so a quad package has one shared PHC and common GPIO/PTP state; LAN8841 uses a per-PHY PHC; LAN8842 reuses the LAN8814 PTP block unless the SKU is LAN8832. Hardware persistence includes many vendor registers, MMD registers, extended page registers, clear-on-read counters, interrupt masks/status, PTP FIFOs, GPIO muxing, and in-band PCS autoneg settings. Suspend/resume paths re-enable clocks, reapply volatile register programming after power-down reset, and reconfigure interrupts where needed.

## Dependencies and Integration Points
The driver depends on phylib, ethtool netlink cable-test reporting, `linux/micrel_phy.h` IDs and bit definitions, OF properties, optional clocks, GPIO descriptors, PTP clock/timestamping APIs, skb timestamp helpers, and the internal `phylib.h` helpers. It integrates with netdev timestamping through `phydev->mii_ts` and `phydev->default_timestamp`, with ethtool through stats, cable test, SQI, MSE, fast-link-down tunables, and timestamp info, with phylib interrupt state machines through `phy_trigger_machine`, and with board descriptions through properties such as `micrel,led-mode`, `micrel,fiber-mode`, `micrel,force-master`, `*-skew-ps`, `*-skew-psec`, `coma-mode`, and RMII clock-selection flags.

## Risks and Test Signals
The file has a high hardware-regression surface: many callbacks program undocumented or errata-specific values, and several MDIO writes ignore return codes in long init sequences. PTP paths have concurrency and lifetime risk around skb queues, RX timestamp list matching, shared-package PHC locking, interrupt FIFO drains, and worker cancellation during suspend. RGMII delay and skew programming can break boards if DTS properties are wrong or reused outside RGMII modes. Cable diagnostics temporarily change autoneg, speed, master/slave, and MDIX state; restoration bugs can leave links misconfigured. Clear-on-read counters and SQI/MSE averaging need stable read sequencing. Test signals include allmodconfig/randconfig builds with and without PTP/timestamping/clk/GPIO support, probe/init for each matched ID, OF property matrix tests, suspend/resume with valid IRQs, interrupt and polling link changes, cable tests for open/short/normal pairs, PTP TX/RX hardware timestamping including FIFO overflow, perout/extts GPIO validation, in-band enable/disable on LAN8814/LAN8842, fast-link-down tunables, SQI/MSE at 100M and 1G, and traffic/link stability after each errata sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/micrel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/microchip.c

## Purpose
This file registers Microchip LAN88xx and LAN937x TX PHY support. LAN88xx handling covers internal LAN7800/LAN7850 PHYs with TR-register tuning, LED-mode device-tree configuration, WOL-aware suspend, downshift ethtool tunables, MDIX control, and link-change workarounds. LAN937x TX handling adds a compact PHY entry for MDIX control/status around generic autoneg/status.

## Important APIs, Types, and Functions
`struct lan88xx_priv` stores chip ID, chip revision, WOL options, and cached downshift count. Page callbacks are `lan88xx_read_page` and `lan88xx_write_page`. LAN88xx setup uses `lan88xx_probe`, `lan88xx_remove`, `lan88xx_config_init`, `lan88xx_config_TR_regs`, `lan88xx_TR_reg_set`, `lan88xx_config_aneg`, `lan88xx_link_change_notify`, `lan88xx_suspend`, `lan88xx_set_wol`, `lan88xx_get_tunable`, and `lan88xx_set_tunable`. LAN937x support is implemented by `lan937x_tx_read_mdix_status`, `lan937x_tx_read_status`, `lan937x_tx_set_mdix`, and `lan937x_tx_config_aneg`. The `microchip_phy_driver` table registers one masked LAN88xx entry and one model-matched LAN937x TX entry.

## Control Flow
LAN88xx probe allocates private state, defaults WOL off and downshift count to 2, optionally parses `microchip,led-modes` into the LED mode select register, reads chip ID/revision from MMD3, and attaches private data. Init enables zero-detect delay, runs a fixed list of TR-register DSP/EEE tuning writes, and restores the cached downshift setting. Autoneg first programs MDIX mode from `phydev->mdix_ctrl`, then calls `genphy_config_aneg`. Link-change notification handles two quirks on `PHY_NOLINK`: it reinitializes hardware and restarts autoneg to refresh stale `MII_LPA` after parallel detection, and in forced 100M mode temporarily switches to 10M before reapplying 100M while masking/clearing interrupts. LAN937x config and status simply wrap generic phylib functions with MDIX register programming and status decoding.

## State and Persistence Behavior
LAN88xx private software state persists WOL options so suspend can avoid powering down when wake is enabled, and persists downshift count so `config_init` can reapply it after reset. Hardware state includes extended page selection, TR page data, LED mode register bits, MMD PCS zero-detect delay, PHY control downshift bits, MDIX mode, interrupt mask/status during forced-mode workaround, and BMCR speed/autoneg bits. `lan88xx_remove` manually devm-frees the private allocation, although the allocation is also device-managed. LAN937x has no private allocation; it reflects MDIX mode directly in hardware register `LAN937X_MODE_CTRL_STATUS_REG` and `phydev` status fields.

## Dependencies and Integration Points
The file depends on phylib, MII/ethtool definitions, `linux/microchipphy.h`, device-tree helpers, delay helpers, and `dt-bindings/net/microchip-lan78xx.h` LED mode values. It integrates with ethtool PHY downshift tunables, WOL option plumbing, phylib page helpers, generic autoneg/status/suspend/resume, and DT-provided LED configuration. The LAN88xx masked ID intentionally distinguishes LAN88xx from LAN8742 while allowing future revisions.

## Risks and Test Signals
TR-register programming is a long sequence of magic 24-bit values; failures are logged but `lan88xx_config_TR_regs` continues, which can leave partially tuned hardware. `lan88xx_TR_reg_set` does not check the TR completion bit in a conventional way: it warns when bit 15 is clear after the write command, so hardware semantics should be verified. The forced-100M link workaround manipulates interrupt mask and BMCR during link changes, so ordering errors can cause missed interrupts or speed glitches. Probe writes LED mode before `phydev->priv` is set and ignores the write return value. Test signals include LAN7800/LAN7850 internal PHY probe, DT LED-mode validation including overflow/invalid values, downshift get/set boundaries, WOL suspend behavior, forced 100M long/short cable swaps, parallel-detection partners without autoneg, MDIX mode/status for LAN937x, and build coverage for masked and model-matched MDIO IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip.c -->
