# Research: subset-b-004692

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.c

## Purpose
Implements the Microchip RDS PTP hardware clock and MII timestamper support used by the LAN887x T1 PHY path. It registers a PHC, attaches `phydev->mii_ts`, programs the PHY 1588/PTP register blocks, services timestamp FIFO interrupts, and matches hardware TX/RX timestamps back to SKBs by PTP sequence ID.

## Important APIs, Types, And Functions
- Exported entry points are `mchp_rds_ptp_probe()`, `mchp_rds_ptp_top_config_intr()`, and `mchp_rds_ptp_handle_interrupt()`.
- Register access helpers `mchp_rds_phy_read_mmd()`, `mchp_rds_phy_write_mmd()`, `mchp_rds_phy_modify_mmd()`, and `mchp_rds_phy_set_bits_mmd()` translate clock-vs-port offsets through the base addresses and selected MMD.
- PTP clock callbacks implement `adjfine`, `adjtime`, `gettime64`, `settime64`, `enable`, and `verify`.
- MII timestamp callbacks implement `txtstamp`, `rxtstamp`, `hwtstamp_set`, `hwtstamp_get`, and `ts_info`.
- Timestamp matching is split between `mchp_rds_ptp_match_tx_skb()`, `mchp_rds_ptp_match_rx_skb()`, and `mchp_rds_ptp_match_rx_ts()`.

## Control Flow
`mchp_rds_ptp_probe()` allocates `struct mchp_rds_ptp_clock`, creates pin descriptors, registers the PHC, initializes TX/RX queues and RX timestamp list state, binds callbacks into `phydev->mii_ts`, marks default timestamping enabled, then calls `mchp_rds_ptp_init()`. Initialization disables PTP/TSU, resets TSU state, configures latency correction, standalone operating mode, 250 MHz reference clock parameters, parser defaults, PTP versions, then reenables TSU and PTP.

`hwtstamp_set` maps user timestamping policy to parser layer bits, version filters, timestamp-enable registers, and one-step Sync insertion. It flushes stale software queues, drains both hardware FIFOs, enables or disables PTP interrupts based on RX filtering, then stores the active TX/RX policy.

The PHY interrupt handler repeatedly reads `MCHP_RDS_PTP_INT_STS`. RX and TX events drain hardware timestamp FIFO entries until capability counters report empty. Overflow events purge the matching software queue and read through FIFO slots. TX timestamps complete queued SKBs through `skb_complete_tx_timestamp()`. RX timestamps either attach to an already queued SKB and inject it through `netif_rx()`, or are retained on `rx_ts_list` until the matching SKB arrives.

## State And Persistence
Persistent runtime state lives in `struct mchp_rds_ptp_clock`: `tx_queue`, `rx_queue`, `rx_ts_list`, `hwts_tx_type`, `rx_filter`, selected parser layer/version, PHC lock, RX timestamp spinlock, PHC pin config, and event/perout ownership state. Hardware state is programmed in PHY MMD registers and survives until PHY reset or reconfiguration. The driver does not persist state across module unload or device reprobe.

## Dependencies And Integration Points
Depends on phylib MMD access, `ptp_clock_register()`, `linux/mii_timestamper.h`, PTP packet classification/parsing, SKB timestamp APIs, ethtool hardware timestamp configuration, and LAN887x top-level interrupt masking from `microchip_t1.c`. `phydev->default_timestamp = true` makes the PHY timestamp provider active by default.

## Risks
- `mchp_get_pulsewidth()` does not initialize `*pulse_width` if the requested duty-cycle on-time is larger than the largest supported value.
- `mchp_rds_ptp_get_sig_rx()` pushes `ETH_HLEN` before classification and returns early on some failures without an obvious matching pull, so malformed/non-PTP RX paths need careful review.
- TX/RX software queues have no timeout or bounded aging beyond FIFO flushes and policy resets.
- Timestamp matching uses only the PTP sequence ID; high-rate traffic with overlapping sequence IDs across flows could be ambiguous.
- Error paths after `ptp_clock_register()` do not visibly unregister the PHC, relying on probe failure behavior and devm allocations only for memory.

## Test Signals
Useful checks include building with `CONFIG_MICROCHIP_PHY_RDS_PTP`, probing LAN887x with interrupts enabled, validating `ethtool -T`, toggling `SIOCSHWTSTAMP`/netlink timestamp config, running `ptp4l` two-step and one-step Sync cases, exercising RX/TX FIFO overflow interrupts, and verifying perout pin 3 duty-cycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.h

## Purpose
Defines the Microchip RDS PTP register map, bit fields, driver state structures, and conditional public API used by `microchip_rds_ptp.c` and the LAN887x PHY driver.

## Important APIs, Types, And Constants
- Register definitions cover clock control, LTC seconds/nanoseconds, rate/step adjustment, parser configuration, timestamp FIFO entries, TSU reset/configuration, interrupt masks, and perout target/reload registers.
- `struct mchp_rds_ptp_clock` is the central state object embedding `struct mii_timestamper`, PHC handles, SKB queues, timestamp lists, parser policy, pin configuration, locks, and register base addresses.
- `struct mchp_rds_ptp_rx_ts` stores RX FIFO timestamp data until it can be matched to an SKB.
- Public declarations are `mchp_rds_ptp_probe()`, `mchp_rds_ptp_top_config_intr()`, and `mchp_rds_ptp_handle_interrupt()`.
- Inline stubs are provided when `CONFIG_MICROCHIP_PHY_RDS_PTP` is disabled.

## Control Flow
The header has no executable control flow beyond feature-gated inline stubs. Its macro layout mirrors the hardware blocks consumed by the implementation: clock/LTC control, port parser controls, ingress/egress FIFO fields, interrupt controls, and GPIO/perout controls.

## State And Persistence
The header declares in-memory state but performs no persistence. Hardware state represented by these constants is persisted in PHY registers until reset. The fallback stubs intentionally make PTP optional for consumers.

## Dependencies And Integration Points
Includes PTP clock, PTP classification, network timestamping, MII, and PHY headers. The API is consumed by `microchip_t1.c` for LAN887x PHC creation and interrupt dispatch, and by `microchip_rds_ptp.c` for implementation.

## Risks
- Macro correctness is critical because offsets are added to caller-supplied clock and port base addresses.
- The disabled-config stub for probe returns `NULL`, while the enabled probe uses `ERR_PTR()` for most failures; callers need to distinguish no support from error.
- The header exposes the full mutable `struct mchp_rds_ptp_clock`, so integration code can modify fields such as `event_pin`.

## Test Signals
Build both enabled and disabled `CONFIG_MICROCHIP_PHY_RDS_PTP` configurations, verify LAN887x compiles with the stubs, and validate register-offset use against hardware documentation or MDIO traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1.c

## Purpose
Implements Microchip automotive T1 PHY support for LAN87xx, LAN937x, and LAN887x devices. It covers extended register access, PHY initialization sequences, interrupt handling, forced master/slave configuration, SQI reporting, cable diagnostics, LAN887x PTP integration, statistics, interface mode setup, and driver registration.

## Important APIs, Types, And Functions
- `access_ereg()` and `access_ereg_modify_changed()` abstract LAN87xx/LAN937x banked extended-register access.
- `lan87xx_phy_init()`, `lan87xx_config_init()`, `lan87xx_config_aneg()`, and `lan87xx_read_status()` handle legacy LAN87xx/LAN937x setup.
- `lan887x_probe()`, `lan887x_phy_setup()`, `lan887x_phy_init()`, `lan887x_config_aneg()`, and `lan887x_config_phy_interface()` handle LAN887x C45 configuration.
- Cable diagnostics are split into LAN87xx and LAN887x paths with normal and hybrid modes for LAN887x fault length.
- `lan887x_get_stats()`, `lan887x_get_sqi()`, and `lan887x_get_sqi_100M()` expose ethtool statistics and signal quality.
- `microchip_t1_phy_driver[]` registers three PHY models.

## Control Flow
LAN87xx/LAN937x initialization performs a soft reset, writes hardware and DSP tuning sequences, conditionally applies slave-mode equalizer freezes, configures SQI measurement, polls hardware initialization, reads and clears interrupt sources, then configures RGMII delays. Interrupt setup masks/clears two interrupt banks and enables link-down plus communication-ready events.

LAN887x probe allocates private stats/PTP state and writes common PHY tuning tables. Config init probes the RDS PTP PHC once when interrupts are valid, enables the event pin mux, sets perout event pin 3, clears loopback, configures LED defaults, and selects RGMII or SGMII based on interface mode and efuse SKU restrictions. Autoneg configuration is effectively forced-mode: it resets speed-dependent hardware, sets C45 PMA forced speed, and applies 100M or 1000M link setup.

Cable tests first disable autoneg where needed, take the link down, program diagnostic thresholds, start the test, poll completion, read peak/gain/timing registers, classify OK/open/same-short, and restore normal PHY configuration. LAN887x can run a second hybrid diagnostic pass to compute distance to fault.

## State And Persistence
LAN887x private state stores accumulated stats, a `struct mchp_rds_ptp_clock *`, and `init_done`. LAN87xx/LAN937x use PHY register state without a private allocation. Hardware configuration writes persist in PHY/DSP/MMD registers until reset; cable diagnostics temporarily reset and reinitialize the PHY.

## Dependencies And Integration Points
Depends on phylib, ethtool cable test and stats APIs, C45 PMA helpers, sort support for SQI sample processing, and `microchip_rds_ptp.h` for LAN887x timestamping. Integration surfaces include `phy_driver` callbacks, MDIO ID table, PHY interrupt flow, and ethtool operations.

## Risks
- Long magic register sequences have high regression risk and little self-documenting context beyond comments.
- `lan87xx_cable_test_report()` uses a hybrid phase variable initialized to zero, so LAN87xx fault logic should be hardware-tested carefully.
- LAN887x PTP probing is tied to interrupt validity; polling-only deployments may not expose timestamping.
- `lan887x_get_stat()` accumulates raw counter reads; correctness depends on whether hardware counters are clear-on-read or delta-like.
- Forced-speed LAN887x behavior clears autoneg support and may surprise MACs expecting standard T1 autoneg.

## Test Signals
Build with and without `CONFIG_MICROCHIP_PHY_RDS_PTP`, probe each PHY ID, test RGMII and SGMII SKU combinations, run ethtool cable tests for OK/open/short cases, check SQI at 100M and 1000M, validate stats monotonicity, trigger link interrupts, and run PTP timestamping through LAN887x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1s.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1s.c

## Purpose
Implements Microchip 10BASE-T1S PHY support for LAN867x revisions B1/C1/C2/D0 and LAN865x Rev.B internal PHYs. The driver applies revision-specific application-note fixups, configures PLCA-related behavior, handles always-active 10M half-duplex status for older parts, and provides direct C45 MMD access for OPEN Alliance MAC-PHYs.

## Important APIs, Types, And Functions
- Fixup tables encode AN1699 and AN1760 register/value/mask sequences.
- `lan865x_revb_indirect_read()` and `lan865x_generate_cfg_offsets()` derive calibration offsets from configuration parameter memory.
- `lan865x_setup_cfgparam()` and `lan865x_setup_sqi_cfgparam()` compute offset-adjusted configuration register values.
- `lan867x_check_reset_complete()` verifies reset completion before fixups.
- `lan86xx_plca_set_cfg()` wraps generic PLCA configuration and toggles collision detection policy.
- `lan865x_phy_read_mmd()` and `lan865x_phy_write_mmd()` route C45 accesses directly through the MDIO bus for OA TC6 MAC-PHYs.

## Control Flow
Each PHY revision has a `config_init` callback. LAN865x Rev.B reads per-chip offsets, writes base fixups, injects calculated config parameters after the second write, configures SQI parameter registers, then writes SQI fixups. LAN867x Rev.C shares the first part of LAN865x fixups plus SQI setup. LAN867x Rev.B1 applies masked RMW fixups. LAN867x Rev.D0 applies its own values and sets link status selection for default CSMA/CD mode.

PLCA configuration first updates Rev.D0 link-status selection, delegates to `genphy_c45_plca_set_cfg()`, then disables collision detection when PLCA is enabled and re-enables it for CSMA/CD.

## State And Persistence
No private driver state is allocated. All state is in PHY registers: fixup values, offset-derived config parameters, PLCA configuration, collision detector enable, and Rev.D0 link-status selection. Older `read_status` reports a fixed logical link because the devices do not support autoneg and are limited to 10M half duplex.

## Dependencies And Integration Points
Depends on phylib C45 PLCA helpers, OA TC6 direct C45 bus operations, ethtool cable test/SQI helpers for Rev.D0, and the MDIO device table. The driver integrates via `microchip_t1s_driver[]` callbacks for config, status, PLCA, cable test, SQI, and MMD access.

## Risks
- Fixup tables are revision-sensitive and must track Microchip application-note revisions.
- Offset-derived config functions read previous cfg params but overwrite calculated fields; field preservation should be checked against datasheets.
- For older parts, always reporting link up can mask physical wiring or multidrop bus faults.
- Rev.D0 does not use `lan86xx_read_status`; behavior relies on generic status plus link-status selection policy.

## Test Signals
Probe every supported PHY ID, verify reset-complete handling, compare MDIO traces against AN1699/AN1760, toggle PLCA enabled/disabled and confirm collision detector state, test OA TC6 direct C45 access on LAN865x, and run Rev.D0 cable test and SQI ethtool paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mii_timestamper.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mii_timestamper.c

## Purpose
Provides a generic registry that lets MII timestamp controller devices expose per-port `struct mii_timestamper` instances to PHY consumers through device-tree node and port lookup.

## Important APIs, Types, And Functions
- `struct mii_timestamping_desc` stores list node, controller callbacks, and backing device.
- `register_mii_tstamp_controller()` registers a controller and its `mii_timestamping_ctrl`.
- `unregister_mii_tstamp_controller()` removes the descriptor for a device.
- `register_mii_timestamper()` looks up a controller by OF node, asks it to probe a channel, stores a device reference on success, and returns the timestamper.
- `unregister_mii_timestamper()` releases a channel and drops the stored device reference.

## Control Flow
Controllers register into a global list protected by `tstamping_devices_lock`. A PHY or bus consumer asks for a timestamper by device node and port. The registry scans descriptors, calls `probe_channel()`, and returns `-EPROBE_DEFER` when no controller is registered yet. Unregister skips static PHY-owned timestampers that lack a populated `mii_ts->device`.

## State And Persistence
State is process-global kernel memory: `mii_timestamping_devices` plus per-controller descriptors. References are held through `get_device()`/`put_device()` for active channels. No persistent storage exists.

## Dependencies And Integration Points
Depends on `linux/mii_timestamper.h`, Linux list/mutex/device lifetime APIs, and controller-supplied `probe_channel`/`release_channel` methods. It is an integration layer between independent timestamp controllers and PHY drivers.

## Risks
- The `list_add_tail()` call appears to pass the list head and new node in reversed order relative to the standard Linux API; that should be verified because it would corrupt the registry list.
- Matching only on `device->of_node` assumes node identity is stable and unique for the controller.
- Unregistering a controller while users hold timestampers relies on callers following lifetime rules and `release_channel()`.

## Test Signals
Build users of `CONFIG_NETWORK_PHY_TIMESTAMPING`, register multiple controllers, request and release ports, verify `-EPROBE_DEFER` before controller registration, and run list-debug/KASAN tests around register/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mii_timestamper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/motorcomm.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/motorcomm.c

## Purpose
Implements the Motorcomm YT8511, YT8521, YT8531, YT8531S, and YT8821 PHY drivers. It supports extended-register access, RGMII delay and drive-strength configuration, copper/fiber combo arbitration, WOL, LED hardware triggers, suspend/resume, autonegotiation, link status decoding, and YT8821 2.5G SerDes/UTP tuning.

## Important APIs, Types, And Functions
- `ytphy_read_ext()`, `ytphy_write_ext()`, and `ytphy_modify_ext()` implement page-select/data extended-register access, with locked wrappers for normal callers.
- `struct yt8521_priv` stores combo advertising, polling mode, strap mode, and active register page.
- `yt8521_probe()` classifies strap mode into UTP, fiber, or poll/combo mode and configures clock output.
- `yt8521_read_status()`, `yt8521_config_aneg()`, and `yt8521_get_features()` handle copper/fiber arbitration and per-page behavior.
- `ytphy_get_wol()`, `ytphy_set_wol()`, and `yt8531_set_wol()` expose magic-packet WOL.
- `yt8521_led_hw_control_*()` maps netdev LED triggers to hardware LED config bits.
- `yt8821_config_init()`, `yt8821_read_status()`, and helper init functions configure 2.5G operation and rate matching.

## Control Flow
YT8511 config selects an extension page, programs RGMII RX/TX delays based on `phydev->interface`, switches to Fast Ethernet delay page, and keeps PLL enabled in sleep. YT8521/YT8531 probes read strap mode and output-clock device-tree properties, then config init applies RGMII delay, auto-sleep, PLL, and drive-strength policies.

YT8521 combo mode saves the original advertising mask, configures UTP and fiber pages separately, then arbitrates active media on status reads with UTP priority. Link-up fixes the register page and `phydev->port`; link-down returns combo devices to an arbitrated state. Fiber forced/autoneg paths use fiber-specific MII advertisement and miscellaneous speed selection.

YT8821 init sets chip mode from interface, declares possible 2500BASE-X/SGMII interfaces, configures rate matching, initializes SerDes and UTP analog registers, disables auto sleep, and soft-resets. Status reads force UTP page, combine generic status with specific status register speed decoding, and update the MAC-facing interface when auto BX2500/SGMII mode is used.

## State And Persistence
Driver state is mostly hardware registers plus optional `yt8521_priv`. Combo mode persists selected active page until link down. WOL state stores MAC address and enable bits in common extended registers. Device-tree properties affect clock output, sleep, PLL, RGMII delays, RX drive strength, and optional TX clock inversion on YT8531 link changes.

## Dependencies And Integration Points
Depends on phylib, OF properties, ethtool WOL/LED linkmode helpers, genphy and C45 PMA helpers, and MDIO page management. It registers five `phy_driver` entries and an MDIO ID table.

## Risks
- Extended register helpers require correct MDIO locking; some LED callbacks call unlocked helpers and rely on caller serialization.
- `yt8531_set_wol()` assumes `phydev->attached_dev` and a valid MAC address, unlike `ytphy_set_wol()` which checks them.
- Combo-mode `combo_advertising` is initialized once; later advertising policy changes need careful validation.
- YT8821 dynamically changes `phydev->interface` based on link speed, which requires MAC/PCS support for live interface changes.
- Long YT8821 analog tuning sequences are magic-value heavy and hardware-revision sensitive.

## Test Signals
Probe all supported IDs, test RGMII delay device-tree values including invalid values, exercise YT8521 UTP/fiber media switching and autoneg, validate WOL suspend/resume wake, check LED trigger set/get, verify YT8531 drive-strength properties, and test YT8821 10/100/1000/2500 link transitions with rate matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/motorcomm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/Makefile

## Purpose
Defines how the Microsemi/Microchip VSC85xx PHY driver objects are built.

## Important APIs, Types, And Functions
This is a Kbuild fragment, not C code. `obj-$(CONFIG_MICROSEMI_PHY) := mscc.o` creates the composite module/object. `mscc-objs` always includes `mscc_main.o` and `mscc_serdes.o`; it conditionally adds `mscc_macsec.o` for `CONFIG_MACSEC` and `mscc_ptp.o` for `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Control Flow
Build-time control flow is entirely Kconfig-driven. Enabling the base PHY option builds the core and SerDes objects. MACsec and PTP support are compiled into the same composite object only when their configs are enabled.

## State And Persistence
No runtime state exists. The persistent effect is the object composition selected at build time.

## Dependencies And Integration Points
Integrates with Linux Kbuild, `CONFIG_MICROSEMI_PHY`, `CONFIG_MACSEC`, and `CONFIG_NETWORK_PHY_TIMESTAMPING`. The conditional object list corresponds to feature-gated declarations in `mscc.h`.

## Risks
Feature combinations must match the C preprocessor guards. Missing an object when a symbol is referenced, or compiling an object without its config dependencies, would surface as link or compile errors.

## Test Signals
Build `CONFIG_MICROSEMI_PHY=y/m` with MACsec and timestamping both disabled, each enabled alone, and both enabled together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc.h

## Purpose
Provides the shared register definitions, IDs, firmware metadata, private state structures, and cross-file function declarations for Microsemi/Microchip VSC85xx PHY support.

## Important APIs, Types, And Constants
- Defines standard, extended, GPIO, CSR, token-ring, test-page, 1588, and MACsec page/register constants.
- Lists supported PHY IDs, vendor ID, VDDMAC values, downshift/LED constants, supported LED mode masks, and internal 8051 firmware filenames/start addresses/CRCs.
- `struct vsc8531_private` stores LED modes, stats, package addressing, optional MACsec state, MII timestamper, PTP state, GPIO, timestamp locks, and RX SKB timestamp wait list.
- `struct vsc85xx_shared_private` provides a shared GPIO mutex for package-wide PHC operations.
- Declares CSR, base-PHY, SerDes MCB, processor command, MACsec, and PTP helper APIs.

## Control Flow
The header has no executable flow except inline stubs. Its conditional sections compile real MACsec/PTP hooks when enabled and no-op stubs when disabled, allowing core code to call feature hooks unconditionally.

## State And Persistence
The header defines private runtime state but does not allocate it. State spans per-PHY data, shared package data, optional MACsec flow lists/bitmaps, PTP locks and queues, and firmware/processor command metadata. Hardware state is represented by page/register macros.

## Dependencies And Integration Points
Included by MSCC core, SerDes, MACsec, and PTP implementation files. It integrates with phylib, optional `CONFIG_OF_MDIO`, `CONFIG_MACSEC`, and `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Risks
- Many macros encode page-specific and package-shared behavior; misuse can write the wrong PHY page or shared GPIO block.
- Optional stubs can hide missing feature support at runtime unless user-visible capabilities are also gated.
- PTP/MACsec members in the private struct impose locking/lifetime constraints across multiple implementation files.

## Test Signals
Compile all feature combinations, probe single-port and multi-port VSC85xx packages, validate firmware loading CRC paths, run LED mode configuration, MACsec offload tests, and PTP timestamping tests when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_fc_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_fc_buffer.h

## Purpose
Defines register offsets and bitfield helpers for the MSCC flow-control buffer block used by VSC85xx MAC/MACsec-style datapath configuration.

## Important APIs, Types, And Constants
Constants cover enable, mode, PPM rate adaptation thresholds, TX control/data queues, RX data queue, XON/XOFF thresholds, flow-control read thresholds, and frame-gap compensation. Bit helpers use `BIT()` and `GENMASK()` to pack 32-bit register values for queue start/end and threshold fields.

## Control Flow
No executable control flow. Consumers write these offsets and packed values through MSCC CSR/register access helpers.

## State And Persistence
No memory state is declared. Hardware state represented here controls TX/RX flow-control buffer enablement, pause reaction/generation, rate adaptation, queue partitioning, and thresholds.

## Dependencies And Integration Points
Requires Linux bit helpers through including C files. Expected consumers are MSCC MACsec/PTP/datapath code that configures buffering around the line MAC.

## Risks
- Queue range and threshold macros do not validate arguments; callers must keep values within field widths and avoid overlapping queue regions.
- Register meanings are hardware-specific and likely shared with MACsec/PTP datapath timing, so incorrect values can cause drops or pause storms.

## Test Signals
Compile MSCC MACsec/PTP users, validate generated CSR writes against datasheet field layouts, and run pause-frame/rate-adaptation traffic tests when the flow-control buffer is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_fc_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_mac.h

## Purpose
Defines the MSCC line-MAC register map, status/statistics offsets, packet formatting controls, pause controls, loopback bits, and the related 1588 top protocol-mode field.

## Important APIs, Types, And Constants
Register offsets cover MAC enable/mode/max length/tags/advanced checks/LFS/loopback/packet info, pause TX/RX controls, sticky status, 32-bit frame counters, and 40-bit byte counters. Bitfield macros configure RX/TX clocks, software resets, MAC enablement, preamble/IPG behavior, FCS/preamble insertion and stripping, padding, LPI/LF/RF relay, pause behavior, VLAN tag matching, loopback, and 1588 protocol mode.

## Control Flow
No executable control flow. It is a register definition header consumed by MSCC implementation files that perform CSR or paged register writes.

## State And Persistence
No software state is declared. Hardware state represented by these macros controls line-MAC datapath behavior and exposes sticky/error/statistics counters.

## Dependencies And Integration Points
Depends on Linux `BIT()`/`GENMASK()` availability through consumers. Integrates with MSCC MACsec, PTP, and core PHY code configuring the embedded line MAC.

## Risks
- Register values are 32-bit oriented; callers must use the correct CSR access width and target.
- Counter offsets include paired 40-bit MSB/LSB registers; readers must order reads carefully to avoid torn values.
- Packet formatting options interact with MACsec and PTP timestamping, especially FCS, preamble, padding, and PTP stall clock fields.

## Test Signals
Compile MSCC line-MAC consumers, validate MAC enable/reset sequencing, check packet counters under traffic, test pause frame behavior, test loopback modes, and verify PTP/MACsec packet formatting with timestamping enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_mac.h -->
