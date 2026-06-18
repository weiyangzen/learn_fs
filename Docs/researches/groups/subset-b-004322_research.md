# subset-b-004322 Research

Grouped research report for the requested DSA switch driver files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_main.c

## Purpose

This file implements the Microchip LAN937x family-specific DSA switch operations that sit underneath the common KSZ driver framework. It handles variant PHY address maps, MDIO/VPHY access setup, switch reset, CPU and user port setup, MTU and ageing-time programming, RGMII delay tuning, phylink capability reporting, credit-based shaper register writes, and switch lifecycle hooks. The code is not a standalone bus driver; it is integrated through `ksz_common.h`, `ksz9477.h`, and `lan937x.h` and is invoked by the broader Microchip KSZ/LAN937x DSA driver.

## Important APIs, Types, And Functions

The variant address tables `lan9370_phy_addr`, `lan9371_phy_addr`, `lan9372_phy_addr`, `lan9373_phy_addr`, and `lan9374_phy_addr` map logical ports to internal PHY addresses, with `LAN937X_NO_PHY` marking RGMII/SGMII-style ports. `lan937x_create_phy_addr_map()` selects a table by `dev->info->chip_id` and optionally adds an offset derived from `REG_SW_CFG_STRAP_VAL` strap bits when side MDIO is used. `lan937x_mdio_bus_preinit()` clears `SW_PHY_REG_BLOCK` and selects SPI-indirect or side-MDIO access in `REG_VPHY_SPECIAL_CTRL__2`.

`lan937x_internal_phy_read()` and `lan937x_internal_phy_write()` implement indirect VPHY transactions through `REG_VPHY_IND_ADDR__2`, `REG_VPHY_IND_DATA__2`, and `REG_VPHY_IND_CTRL__2`, polling `VPHY_IND_BUSY`. Public wrappers `lan937x_r_phy()` and `lan937x_w_phy()` expose this to the common driver. `lan937x_reset_switch()` resets the switch, enables link auto ageing, masks global/port interrupts, acknowledges POR readiness, and reads the port interrupt status.

Port and switch setup are split across `lan937x_port_setup()`, `lan937x_config_cpu_port()`, `lan937x_setup()`, `lan937x_switch_init()`, `lan937x_teardown()`, and `lan937x_switch_exit()`. Runtime knobs include `lan937x_change_mtu()`, `lan937x_set_ageing_time()`, `lan937x_setup_rgmii_delay()`, `lan937x_phylink_get_caps()`, and `lan937x_tc_cbs_set_cinc()`.

## Control Flow

Initialization first builds a PHY address map and preinitializes the PHY access path according to whether side MDIO or SPI is used. Switch reset asserts `SW_RESET`, enables automatic ageing, then masks and acknowledges interrupts. Generic setup enables global VLAN filtering semantics (`ds->vlan_filtering_is_global`), half-duplex backoff behavior, MIB freeze, disables output clocks, and disables global VPHY support.

CPU port configuration iterates DSA CPU ports, records `dev->cpu_port`, enables tail tagging on the CPU port, enables queue splitting, backpressure, 802.1p priority, flow control on non-internal-PHY ports, and assigns port membership. User ports are then forced to disabled STP state. MTU changes compute frame length including VLAN header, FCS, and LAN937x tag for CPU ports, toggle jumbo mode at `FR_MIN_SIZE`, and write `PORT_MAX_FR_SIZE`.

The ageing timer path chooses seconds or microseconds mode depending on millisecond granularity, preserves a usable multiplier when possible, rejects values beyond hardware capacity, writes multiplier bits in `REG_SW_LUE_CTRL_0`, and splits the 20-bit period across `REG_SW_AGE_PERIOD__1` and `REG_SW_AGE_PERIOD__2`. RGMII delay setup only applies if per-port parsed RGMII delay flags are present and writes characterization values through DLL reset sequences.

## State And Persistence Behavior

Persistent driver state lives in `struct ksz_device` and its `dev->info`, `dev->ports`, `dev->phy_addr_map`, `dev->cpu_port`, and DSA switch pointers. Hardware state is persisted in switch registers until reset: global MAC/LUE settings, interrupt masks, VPHY access mode, per-port tail tags, member maps, MTU size, ageing timer, and RGMII tuning. There is no file-backed state. Several helper writes ignore return values in port setup and delay tuning, so later errors may only surface as bad link behavior rather than probe failure.

## Dependencies And Integration Points

The file depends on Linux regmap, DSA, phylink, bridge/VLAN definitions, and Microchip KSZ common helpers such as `ksz_read32()`, `ksz_rmw16()`, `ksz_pwrite16()`, `ksz9477_port_queue_split()`, `ksz_port_stp_state_set()`, and `dev->dev_ops->cfg_port_member()`. It consumes register definitions from `lan937x_reg.h` and variant helpers from `lan937x.h`. DSA integration is visible in CPU/user port iteration, `dsa_user_ports()`, `dsa_upstream_port()`, and CPU-port MTU tag accounting.

## Risks

The side-MDIO PHY address offset logic is strap-sensitive; incorrect straps or chip IDs can silently map ports to wrong PHYs. VPHY indirect reads return `0xffff` for non-internal PHYs but error codes for transaction failures, so callers must distinguish absent PHYs from bus errors. RGMII delay writes do not propagate errors. Ageing-time conversion is sensitive to millisecond-vs-second mode and integer rounding. `lan937x_teardown()` is empty, so cleanup relies on outer KSZ/DSA teardown and `lan937x_switch_exit()` reset behavior.

## Test Signals

Useful validation signals are successful probe for each LAN9370-LAN9374 chip ID, correct MDIO discovery in both SPI-indirect and side-MDIO modes, `ip link set mtu` behavior across the jumbo threshold and CPU-port tag overhead, bridge ageing-time programming including sub-second values and oversized rejection, RGMII TX/RX delay link stability, DSA tail-tag packet flow through CPU ports, and absence of unexpected global/port interrupt storms after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_reg.h

## Purpose

This header defines LAN937x register addresses, bit fields, masks, port address translation, frame-size constants, RGMII delay constants, and the DSA tag length used by `lan937x_main.c` and the Microchip KSZ common driver code. It is the hardware contract for programming global switch blocks, virtual PHY access, per-port MAC/xMII/classification/shaping controls, and LAN937x-specific port numbering.

## Important APIs, Types, And Definitions

`PORT_CTRL_ADDR(port, addr)` builds per-port register addresses by combining a block offset with the 1-based hardware port selector. Global definitions cover `REG_GLOBAL_CTRL_0`, interrupt status/mask registers, strap registers, `REG_SW_OPERATION`, LUE ageing/VLAN controls, MAC controls, ALU fields, and VPHY indirect access registers. Per-port definitions cover interrupt bits, `REG_PORT_CTRL_0`, T1/TX PHY register base offsets, xMII controls, DLL delay fields, MAC frame-size controls, priority controls, and credit increment shaping.

Key constants include `SWITCH_INT_MASK`, `SW_PHY_REG_BLOCK`, `SW_RESET`, `SW_LINK_AUTO_AGING`, `SW_AGE_CNT_M`, `SW_AGE_CNT_IN_MICROSEC`, `VPHY_IND_BUSY`, `VPHY_IND_WRITE`, `VPHY_MDIO_INTERNAL_ENABLE`, `VPHY_SPI_INDIRECT_ENABLE`, `PORT_TAIL_TAG_ENABLE`, `PORT_JUMBO_PACKET`, `PORT_MAX_FR_SIZE`, `FR_MIN_SIZE`, `PORT_TUNE_ADJ`, `PORT_DLL_RESET`, and `LAN937X_TAG_LEN`.

## Control Flow

The header has no runtime control flow, but its definitions directly shape driver sequences. Reset and interrupt masking use global operation and interrupt fields. PHY access uses the VPHY address/data/control triplet and busy bit. Port setup uses `PORT_CTRL_ADDR()` with MAC, xMII, and priority offsets. Ageing-time code splits multiplier and period values across the LUE fields. MTU code uses `FR_MIN_SIZE` and `PORT_MAX_FR_SIZE`, while CPU-port MTU adjustment uses `LAN937X_TAG_LEN`.

## State And Persistence Behavior

All definitions refer to hardware state persisted in LAN937x registers: interrupt masks/status, strap overrides, LUE state, ALU content, VPHY mode, port tail tagging, xMII delay tuning, MAC frame-size controls, priority selection, and shaper credit increments. The header itself stores no software state.

## Dependencies And Integration Points

The header assumes Linux bit helpers such as `BIT()`, `GENMASK()`, `FIELD_PREP()`, and `FIELD_GET()` are available through including C files. It integrates with `lan937x_main.c`, common KSZ register helpers, DSA tag accounting, and traffic-control CBS code. The port constants `LAN937X_RGMII_1_PORT` and `LAN937X_RGMII_2_PORT` are zero-based translations of datasheet port numbers used by delay setup.

## Risks

Incorrect bit masks or port offset calculations would cause writes to the wrong hardware block. The similar global and per-port interrupt names require careful use of `REG_SW_*` versus `REG_PORT_*`. `FR_MIN_SIZE` and `LAN937X_TAG_LEN` feed packet-size enforcement, so drift from hardware framing requirements can cause dropped frames or undersized jumbo programming. RGMII delay constants are characterization-derived values and may require board-level validation.

## Test Signals

Compile coverage should catch missing macro dependencies. Runtime signals include successful switch reset, stable VPHY indirect read/write polling, correct interrupt masking, expected MTU threshold behavior, and link stability on both RGMII ports after delay programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mdio.c

## Purpose

This file is the MDIO transport driver for MediaTek MT7530, MT7621, and MT7531 switch variants. It allocates `struct mt7530_priv`, builds a regmap over an MDIO bus using MT7530 page/register addressing, handles reset/regulator resources for standalone versus MCM hardware, creates MT7531 SGMII PCS instances, and registers the shared DSA switch implementation from `mt7530.c`.

## Important APIs, Types, And Functions

`mt7530_regmap_write()` and `mt7530_regmap_read()` translate 32-bit switch register accesses into MDIO page register writes/reads via page register `0x1f`, low word register `r`, and high word register `0x10`. `mt7530_mdio_regmap_lock()` and `_unlock()` use nested MDIO locking for PCS regmaps. `mt7531_create_sgmii()` allocates per-port regmap configs for port 5/6 SGMII blocks and calls `mtk_pcs_lynxi_create()`.

The OF match table maps `"mediatek,mt7621"`, `"mediatek,mt7530"`, and `"mediatek,mt7531"` to `mt753x_table[]` entries. `mt7530_probe()` allocates state, calls `mt7530_probe_common()`, detects `"mediatek,mcm"`, obtains either reset control or reset GPIO, obtains core/io regulators for MT7530, initializes the MDIO regmap, assigns `create_sgmii` for MT7531, and calls `dsa_register_switch()`. Remove and shutdown paths disable regulators, call `mt7530_remove_common()`, destroy PCS instances, or shut down DSA.

## Control Flow

Probe begins from the MDIO driver core. Shared initialization sets up the DSA switch, operations, locks, and variant data. The transport-specific code then gathers reset and power resources, creates the regmap, installs the optional SGMII factory, and registers the switch. During shared DSA setup, `mt753x_setup()` in `mt7530.c` calls back into `priv->create_sgmii` for MT7531. Remove disables power rails, unregisters the switch through common removal, and tears down SGMII PCS objects.

## State And Persistence Behavior

Software state is held in devm-managed `struct mt7530_priv`, the MDIO regmap, regulator handles, optional reset GPIO or reset controller, and PCS pointers in `priv->ports[5]` and `[6]`. Hardware state is programmed through MDIO pages and survives until reset or power removal. `regmap_config.disable_locking = true` places locking responsibility on driver-level MDIO and DSA paths.

## Dependencies And Integration Points

The file depends on Linux MDIO, regmap, reset, regulator, GPIO, OF, DSA, and `pcs-mtk-lynxi`. Its key integration point is `mt7530_probe_common()`/`mt7530_remove_common()` and the exported `mt753x_table[]` from `mt7530.c`. It registers as an `mdio_driver`, not as a platform driver, and is selected by compatible strings in devicetree.

## Risks

The MDIO regmap translation assumes the switch page scheme and 32-bit split access order; broken locking or partial writes can corrupt register transactions. Remove disables `core_pwr` and `io_pwr` unconditionally, so error logs are possible if those pointers were not valid for a non-MT7530 path. SGMII PCS cleanup must match creation: if port 6 creation fails after port 5 succeeds, the error path destroys port 5. MCM detection changes reset sequencing, so devicetree must accurately describe the hardware.

## Test Signals

Probe should succeed for all three compatible strings with correct chip detection in shared setup. Signals include correct MDIO register reads through regmap, successful regulator enable/disable on MT7530, reset GPIO/control transitions, SGMII PCS creation on MT7531AE/BE, DSA switch registration, and clean shutdown via `dsa_switch_shutdown()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mmio.c

## Purpose

This file is the platform/MMIO transport driver for MT7530-family switch IP embedded in newer SoCs, including Airoha AN7583/EN7581 and MediaTek MT7988. It maps the switch register resource, creates an MMIO regmap, obtains a reset controller, invokes shared MT7530 DSA initialization, and registers the switch.

## Important APIs, Types, And Functions

The OF match table maps `"airoha,an7583-switch"`, `"airoha,en7581-switch"`, and `"mediatek,mt7988-switch"` to `mt753x_table[]` entries. `sw_regmap_config` defines a 16-bit register, 32-bit value, stride-4 switch regmap with `MT7530_CREV` as maximum register. `mt7988_probe()` allocates `struct mt7530_priv`, marks `priv->bus = NULL`, calls `mt7530_probe_common()`, obtains an unnamed reset control, maps MMIO resource 0 with `devm_platform_ioremap_resource()`, initializes `devm_regmap_init_mmio()`, and registers the DSA switch. Remove calls `mt7530_remove_common()`; shutdown calls `dsa_switch_shutdown()`.

## Control Flow

The platform driver probe path is short: allocate state, run common setup, acquire reset, map registers, create regmap, and register the switch. Once registered, the shared `mt753x_setup()` path calls the variant setup function from `mt753x_table[]`; for these compatibles that is `mt7988_setup()`, which resets the switch, applies AN7583-specific GEPHY connection tweaks if needed, resets switch PHYs, and uses MT7531-style common initialization.

## State And Persistence Behavior

State is devm-managed through platform device lifetime: `struct mt7530_priv`, reset controller, ioremapped base, and MMIO regmap. `priv->bus = NULL` is significant because shared code skips MDIO locking and reads live MMIO stats directly instead of using the delayed MDIO stats cache. Hardware state persists in the SoC switch register block until reset.

## Dependencies And Integration Points

The file depends on the platform bus, OF matching, reset framework, MMIO regmap, DSA, and the shared MT7530 implementation. It exports no symbols and is registered with `module_platform_driver()`. Shared code distinguishes this transport through `priv->bus == NULL`, affecting mutex behavior and statistics reads.

## Risks

The driver assumes one MMIO resource and one reset control. A bad compatible-to-variant mapping selects wrong capabilities and setup hooks. Because no MDIO bus exists at this layer, any PHY access goes through the shared indirect access functions configured in `mt753x_table[]`. The maximum register set in `sw_regmap_config` must cover all registers used by AN7583/EN7581/MT7988 paths.

## Test Signals

Useful tests include platform probe on each compatible, successful MMIO regmap reads of chip ID/trap registers, reset assertion/deassertion, DSA registration, live ethtool/stat reads without delayed cache, and AN7583-specific link bring-up after `AN7583_GEPHY_CONN_CFG` programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.c

## Purpose

This file contains the shared MediaTek/Airoha MT753x DSA switch implementation used by the MDIO and MMIO transport drivers. It provides register access wrappers, FDB/MDB/VLAN operations, port matrix and bridge behavior, phylink and PCS integration, statistics, interrupt-backed internal MDIO bus setup, switch reset/setup for multiple variants, mirroring, EEE/LPI controls, TBF offload, and the exported `mt753x_table[]` variant dispatch table.

## Important APIs, Types, And Functions

Register access is centralized through `mt7530_mii_read()`, `mt7530_mii_write()`, `mt7530_read()`, `mt7530_write()`, `mt7530_rmw()`, `mt7530_set()`, and `mt7530_clear()`, with MDIO transports using nested MDIO locking and MMIO transports skipping it. Core PLL MMD access for MT7530 uses `core_write()`, `core_rmw()`, `core_set()`, and `core_clear()`.

FDB and MDB handling uses `mt7530_fdb_write()`, `mt7530_fdb_read()`, `mt7530_fdb_cmd()`, `mt7530_port_fdb_add()`, `mt7530_port_fdb_del()`, `mt7530_port_fdb_dump()`, `mt7530_port_mdb_add()`, and `mt7530_port_mdb_del()`. VLAN handling uses `mt7530_vlan_cmd()`, `mt7530_hw_vlan_update()`, `mt7530_hw_vlan_add()`, `mt7530_hw_vlan_del()`, `mt7530_setup_vlan0()`, `mt7530_port_vlan_filtering()`, `mt7530_port_vlan_add()`, and `mt7530_port_vlan_del()`.

Port behavior is managed by `mt753x_cpu_port_enable()`, `mt7530_port_enable()`, `mt7530_port_disable()`, `mt7530_update_port_member()`, bridge join/leave and bridge flag callbacks, STP state mapping, MTU programming, mirroring callbacks, and TBF qdisc offload. Link handling is split into variant capability callbacks (`mt7530_mac_port_get_caps()`, `mt7531_mac_port_get_caps()`, `mt7988_mac_port_get_caps()`, `en7581_mac_port_get_caps()`), MAC configuration callbacks, PCS ops, and `mt753x_phylink_mac_ops`.

Setup entry points are `mt7530_setup()`, `mt7531_setup()`, `mt7531_setup_common()`, `mt7988_setup()`, and the DSA `.setup` wrapper `mt753x_setup()`. Public exports are `mt753x_table[]`, `mt7530_probe_common()`, and `mt7530_remove_common()`.

## Control Flow

Transport probe calls `mt7530_probe_common()`, which allocates and initializes `dsa_switch`, variant info, locks, delayed stats work, DSA ops, and phylink MAC ops. DSA registration later invokes `mt753x_setup()`, which dispatches to the variant `sw_setup`, configures IRQ and internal MDIO support, initializes PCS structures, creates SGMII PCS where applicable, and starts delayed stats polling for MDIO transports.

MT7530 setup enables regulators in the MDIO transport case, toggles reset GPIO/control, waits for trap register stability, verifies chip ID and XTAL support, resets switch/PHY/register blocks, tunes TRGMII and PLL settings, enables link-local frame trapping to CPU, resets MIB counters, forces all links down, disables forwarding and learning by default, enables CPU ports, initializes VLAN 0, optionally configures port 5 PHY muxing, optionally registers LED GPIOs, and flushes the FDB. MT7531 setup follows a similar reset and ID check path, detects dual SGMII, adjusts PLL/GPIO/EEE settings, disables EEE advertisement, then enters common setup. MT7988/EN7581/AN7583 setup uses reset control and MT7531 common setup, with an AN7583 GEPHY clock/power tweak.

Bridge and VLAN control flow maintains a software port matrix in `priv->ports[port].pm`. Enabling a user port adds its CPU port to the matrix; bridge join adds same-bridge peer ports unless both are isolated; bridge leave removes peers and returns to matrix mode. VLAN filtering flips ports between fallback/security modes, updates PVID and accepted-frame policy, and writes VLAN table entries with CPU ports stack-tagged. FDB/MDB operations serialize under `reg_mutex`, write address table registers, and run hardware table commands with timeout polling.

## State And Persistence Behavior

Main software state lives in `struct mt7530_priv`: variant ID/info, DSA switch, regmap, bus/reset/regulator/GPIO handles, port states, PCS objects, mirror bitmaps, IRQ domain, active CPU-port bitmap, locks, and stats cache. Per-port state in `struct mt7530_port` tracks enablement, isolation, port matrix, PVID, SGMII PCS, and cached `rtnl_link_stats64`. MDIO-connected switches cache stats through delayed work to avoid expensive synchronous MDIO reads; MMIO-connected switches read stats directly. Hardware state includes ATU/FDB, VLAN table, port control, PMCR link force bits, MIB counters, interrupt masks/status, PLL/strap overrides, PHY indirect access, and special-tag CPU forwarding.

## Dependencies And Integration Points

The file is tightly integrated with Linux DSA (`struct dsa_switch_ops`, CPU/user port iteration, bridge offload state, HSR helpers), phylink, ethtool stats APIs, switchdev FDB/MDB/VLAN objects, traffic-control TBF offload, regmap IRQ, internal MDIO bus registration, GPIO library for MT7530 LED GPIOs, reset/regulator frameworks, and MediaTek LynxI PCS through the MDIO wrapper. It relies on the register and type definitions in `mt7530.h` and is shared by `mt7530-mdio.c` and `mt7530-mmio.c`.

## Risks

Hardware table operations rely on busy polling; timeout handling is present but partial table state can persist after failures. `mt7530_port_fdb_dump()` currently returns `0` even if callback or search errors occur after `err`, which can hide dump failures. VLAN programming is global-table based and serialized by `reg_mutex`; missed locking would corrupt membership or egress-tag state. Link-local frame trapping is an approximation of IEEE 802.1Q behavior due to hardware limitations and can over-trap or under-trap some reserved MAC addresses. MT7530 port 5 muxing depends on devicetree topology discovery and can misconfigure hardware if the PHY-handle relationship is wrong. MDIO stats caching introduces staleness and delayed work lifetime risks, mitigated by canceling work in teardown. Variant capability callbacks must stay aligned with port wiring and table IDs.

## Test Signals

High-value tests include DSA probe and removal for every `mt753x_table[]` ID, bridge join/leave with isolated and non-isolated ports, VLAN-aware/unaware transitions including PVID removal, FDB/MDB add/delete/dump, STP state transitions, CPU-port conduit failover on MT7530/MT7621, MTU changes through jumbo thresholds, ethtool standard/RMON/control stats, delayed stats polling on MDIO transports, phylink negotiation for RGMII/TRGMII/SGMII/1000BASE-X/2500BASE-X/internal ports, EEE LPI timer validation, mirror add/delete single-monitor constraints, TBF replace/destroy, IRQ-backed internal MDIO registration, and link-local control-frame delivery to CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.h

## Purpose

This header is the shared register, bitfield, enum, structure, and prototype definition file for the MT753x DSA driver. It describes the hardware register map for MT7530/MT7621/MT7531/MT7988/EN7581/AN7583 families and defines the software state structures consumed by both MDIO and MMIO transport drivers and the shared implementation.

## Important APIs, Types, And Definitions

Core constants define port and PHY counts, FDB size, all-member masks, DSA header length, maximum MTU, and variant IDs. The register definitions cover global forwarding control, CPU forwarding, reserved MAC trapping, ATU/FDB access, VLAN table access, ageing, egress rate limiting, STP states, port control/security/VLAN/PVID, PMCR/PMSR link configuration, EEE, MIB counters, SGMII, reset/interrupt/PHY indirect access, trap/strap registers, PLL controls, TRGMII, RGMII, GPIO/LED, special-tag config, AN7583 GEPHY configuration, and chip ID registers.

The header defines important enums for variant IDs, CPU forwarding modes, FDB commands, VLAN commands, FIDs, STP states, port modes, VLAN egress/port attributes, PHY IAC commands, MDIO start fields, MT7531 GP modes and clock skew, XTAL selection, and port 5 mode. Important structures include `mt7530_mib_desc`, `mt7530_fdb`, `mt7530_port`, `mt753x_pcs`, `mt753x_info`, `mt7530_priv`, `mt7530_hw_vlan_entry`, `mt7530_hw_stats`, and `mt7530_dummy_poll`.

The exported interface consists of `mt7530_probe_common()`, `mt7530_remove_common()`, and `extern const struct mt753x_info mt753x_table[]`. `MIB_DESC()` and `INIT_MT7530_DUMMY_POLL()` are local construction helpers used by `mt7530.c`.

## Control Flow

The header has no executable control flow, but its function-pointer structures drive runtime dispatch. `struct mt753x_info` binds each variant to PCS ops, setup function, PHY read/write methods, capability callback, and optional MAC config callback. `struct mt7530_priv` carries enough state for transport-specific probe code to call common setup and for DSA callbacks to find regmap, bus, reset, per-port state, IRQ domain, PCS, active CPU ports, and stats work.

## State And Persistence Behavior

The state model is explicit in `struct mt7530_priv` and `struct mt7530_port`. Driver-persistent state includes port enable/isolation flags, port matrix, PVID, mirror bitmaps, PCS pointers, active CPU port bitmap, IRQ domain, and cached stats. Hardware-persistent state is represented by register macros and written by `mt7530.c`: forwarding matrices, VLAN/FDB tables, PMCR link bits, MIB counters, PLLs, PHY indirect controls, and special tag controls.

## Dependencies And Integration Points

The header assumes Linux networking and driver types such as `struct dsa_switch`, `struct phylink_pcs`, `struct phylink_config`, `struct mii_bus`, `struct regmap`, `struct reset_control`, `struct regulator`, `struct gpio_desc`, `struct irq_domain`, `struct mdio_device`, `struct delayed_work`, and `struct rtnl_link_stats64`. It is included by both transport drivers and the shared implementation, so changes here affect all MT753x variants.

## Risks

Register macros are dense and variant-dependent. Conditional macros such as `MT753X_MIRROR_REG()`, `MT753X_MIRROR_EN()`, and `MT753X_FORCE_MODE()` must include every variant with compatible register semantics; missing a new variant can silently program MT7530-style fields on MT7531-style hardware. `MT7530_MAX_MTU` embeds tag/header assumptions. Structure fields such as `stats_lock`, `stats_work`, `irq_domain`, and `create_sgmii` require lifecycle discipline in the implementation.

## Test Signals

Compile-time coverage across all enabled variants is the first signal. Runtime signals include correct variant dispatch through `mt753x_table[]`, expected port capabilities, functioning PHY access path for C22/C45, correct mirror register selection, MTU maximum reporting, stats cache behavior, and no regmap range failures for registers referenced by variant setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.c

## Purpose

This file implements a legacy Marvell 88E6060 DSA switch driver over MDIO. It detects the switch, resets and initializes global/port state, configures trailer tagging, sets simple port-based VLAN isolation, exposes internal PHY read/write operations, reports phylink capabilities, and registers as an MDIO driver.

## Important APIs, Types, And Functions

`reg_read()` and `reg_write()` access switch registers at `priv->sw_addr + addr` using nested MDIO operations. `mv88e6060_get_name()` reads `PORT_SWITCH_ID` from port 0 and identifies A0/B0/generic 88E6060 revisions. `mv88e6060_get_tag_protocol()` returns `DSA_TAG_PROTO_TRAILER`.

Setup is split into `mv88e6060_switch_reset()`, `mv88e6060_setup_global()`, `mv88e6060_setup_addr()`, `mv88e6060_setup_port()`, and `mv88e6060_setup()`. PHY operations are `mv88e6060_phy_read()` and `mv88e6060_phy_write()`. `mv88e6060_phylink_get_caps()` derives supported MAC/PHY interfaces from `PORT_STATUS`. Probe/remove/shutdown are implemented by `mv88e6060_probe()`, `mv88e6060_remove()`, and `mv88e6060_shutdown()`.

## Control Flow

Probe allocates `mv88e6060_priv`, stores bus and switch base address, validates the chip ID, allocates a `dsa_switch`, fills `num_ports`, `priv`, and ops, stores it as driver data, and registers with DSA. DSA setup resets the switch by disabling all ports, waiting for TX queues to drain, issuing `GLOBAL_ATU_CONTROL_SWRESET | LEARNDIS`, and polling `GLOBAL_STATUS_INIT_READY`. It then programs global controls, assigns a random switch MAC address, and configures each non-unused port.

Each configured port is placed in forwarding state. CPU ports enable trailer and ingress mode; user ports forward only to their CPU port. `PORT_VLAN_MAP` gives each port its own database and controls allowed peers. `PORT_ASSOC_VECTOR` records the source port vector. Phylink capabilities reject unsupported SNI mode, advertise 10/100 and pause, and set interface modes based on whether the port has internal PHY or MII-style external capability.

## State And Persistence Behavior

Software state is minimal: MDIO bus, switch base address, and DSA switch pointer in `struct mv88e6060_priv`. Hardware state includes port control, VLAN maps, association vectors, global MAC, global control, ATU learning disable/reset, and forwarding state. The setup path generates a random MAC address on each initialization; no persistent configured address is stored.

## Dependencies And Integration Points

The driver depends on Linux MDIO, DSA, phylink, jiffies/delay helpers, and Ethernet random address helpers. It integrates with DSA through `struct dsa_switch_ops`, trailer tagging, HSR simple join/leave helpers, and the MDIO driver model with compatible `"marvell,mv88e6060"`. It is separate from the newer `mv88e6xxx` driver family and explicitly supports the 88E6060 exception.

## Risks

The driver is intentionally simple and lacks advanced switchdev features such as VLAN table management, FDB operations, stats, IRQs, and devlink. Learning is globally disabled, so forwarding behavior depends on static port maps. Reset timeout relies on `GLOBAL_STATUS_INIT_READY` within one second. The PHY address mapping assumes ports map directly to MDIO addresses 0-5. `mv88e6060_phy_write()` returns `0xffff` for invalid ports despite being an error path, which is unusual for write semantics.

## Test Signals

Validation signals include probe detection for A0/B0 revisions, reset completion, CPU trailer-tag traffic, user-port isolation through CPU-only VLAN maps, phylink capability output for ports 0-5, internal PHY reads/writes, DSA registration/removal/shutdown, and no forwarding leakage between user ports outside CPU-mediated paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.h

## Purpose

This header defines the Marvell 88E6060 register layout, bit fields, constants, and private driver state consumed by `mv88e6060.c`. It covers six ports, per-port status/control/VLAN/association/counter registers, global status/control/MAC/ATU registers, and the small `struct mv88e6060_priv` state object.

## Important APIs, Types, And Definitions

`MV88E6060_PORTS` fixes the DSA port count at six. `REG_PORT(p)` maps a logical port to the hardware MDIO address offset, and `REG_GLOBAL` identifies the global register block. Port definitions include `PORT_STATUS`, `PORT_SWITCH_ID`, revision masks and values, `PORT_CONTROL` flags for trailer/header/ingress/VLAN/state, `PORT_VLAN_MAP`, `PORT_ASSOC_VECTOR`, and RX/TX counter registers. Global definitions cover `GLOBAL_STATUS`, switch modes, init-ready and interrupt bits, global MAC address registers, global control bits, ATU control reset/learning/size/age fields, ATU operation codes, ATU data fields, and ATU MAC registers.

`struct mv88e6060_priv` stores the MDIO bus, switch base address, and DSA switch pointer. The comment notes single-chip versus multi-chip addressing, although the C file uses direct `sw_addr + addr` accesses.

## Control Flow

The header has no executable control flow. Its definitions drive chip detection, reset polling, global setup, per-port forwarding/trailer setup, port VLAN mapping, source association, PHY register access, and phylink status interpretation in `mv88e6060.c`.

## State And Persistence Behavior

The defined registers represent persistent switch hardware state: port forwarding states, trailer mode, ingress mode, VLAN maps, association vectors, switch MAC address, global frame-size/interrupt controls, ATU reset/learning/aging, and ATU entries. The private struct is runtime-only and devm-allocated by probe.

## Dependencies And Integration Points

The header depends on Linux integer and bit macro availability through its including C file. It is private to the 88E6060 driver and intentionally distinct from `mv88e6xxx` shared headers.

## Risks

Register constants are compact and hardware-specific. The direct MDIO addressing model means an incorrect `sw_addr` or `REG_PORT()` offset can target the wrong device address on a shared bus. Some defined ATU operation fields are not currently used by the C file, so future feature additions must confirm semantics against hardware documentation rather than assuming newer mv88e6xxx behavior.

## Test Signals

Compile-time inclusion through `mv88e6060.c` should validate symbol availability. Runtime tests should confirm switch ID decoding, register reads from all six ports, global reset readiness, trailer mode bit programming, and expected port VLAN map values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6060.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the main Marvell 88E6xxx DSA switch driver family, its optional PTP support, and optional LED support. It explicitly describes the family driver as supporting most 88E6xxx chips except 88E6060, which is handled by the separate `mv88e6060.c` driver.

## Important APIs, Types, And Options

`NET_DSA_MV88E6XXX` is a tristate option depending on `NET_DSA` and selecting `IRQ_DOMAIN`, `NET_DSA_TAG_EDSA`, and `NET_DSA_TAG_DSA`. `NET_DSA_MV88E6XXX_PTP` is a bool controlled by whether the base driver and `PTP_1588_CLOCK` are built-in or modular-compatible. `NET_DSA_MV88E6XXX_LEDS` defaults to yes, depends on the base driver, LED class availability compatible with the base build mode, and LED triggers.

## Control Flow

Kconfig evaluation controls which objects are compiled from the paired Makefile. Enabling the base driver builds `mv88e6xxx.o`; enabling PTP adds hardware timestamp support objects; enabling LED support adds LED control objects. The selected DSA tag protocols and IRQ domain support ensure required subsystems are available.

## State And Persistence Behavior

There is no runtime state. Persistent effects are kernel configuration symbols recorded in the build configuration and used by Makefile conditionals and preprocessor paths.

## Dependencies And Integration Points

The file integrates with the kernel networking DSA menu, PTP clock subsystem, LED subsystem, and the `mv88e6xxx/Makefile`. Its explicit exclusion of 88E6060 is an integration boundary with `drivers/net/dsa/mv88e6060.c`.

## Risks

Dependency expressions for PTP and LED support must preserve built-in/module compatibility. If a feature object is added to the Makefile without a matching Kconfig dependency, builds can fail or expose unusable options. The LED dependency on `LEDS_CLASS=y || LEDS_CLASS=NET_DSA_MV88E6XXX` is important to avoid module/builtin ordering issues.

## Test Signals

Useful signals are configuration matrix builds for built-in and module variants, with and without `PTP_1588_CLOCK`, `LEDS_CLASS`, and `LEDS_TRIGGERS`, plus verification that the base option selects both DSA tag protocols and IRQ domain support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Makefile

## Purpose

This Makefile lists the object composition for the Marvell 88E6xxx DSA switch driver. It builds a single composite `mv88e6xxx.o` from core chip logic, global register blocks, port/PHY/PCS/SerDes support, switchdev, devlink, tracing, TC flower/TCAM support, and optional PTP and LED objects.

## Important APIs, Types, And Targets

`obj-$(CONFIG_NET_DSA_MV88E6XXX) += mv88e6xxx.o` attaches the composite object to the base Kconfig symbol. `mv88e6xxx-objs` includes required objects such as `chip.o`, `devlink.o`, `global1.o`, `global1_atu.o`, `global1_vtu.o`, `global2.o`, `global2_avb.o`, `global2_scratch.o`, `pcs-6185.o`, `pcs-6352.o`, `pcs-639x.o`, `phy.o`, `port.o`, `port_hidden.o`, `serdes.o`, `smi.o`, `switchdev.o`, `trace.o`, `tcflower.o`, and `tcam.o`. Conditional additions include `hwtstamp.o` and `ptp.o` for `CONFIG_NET_DSA_MV88E6XXX_PTP`, and `leds.o` for `CONFIG_NET_DSA_MV88E6XXX_LEDS`. `CFLAGS_trace.o := -I$(src)` makes the local trace header discoverable.

## Control Flow

The Makefile has build control flow only: Kbuild includes the composite object when the base symbol is enabled and appends optional feature objects when their symbols are enabled. The resulting module or built-in object exposes the complete mv88e6xxx driver implementation.

## State And Persistence Behavior

There is no runtime state in this file. Build configuration controls persistent artifacts in the kernel build tree, including whether PTP timestamping and LED control code is linked.

## Dependencies And Integration Points

The file depends on Kconfig symbols from `mv88e6xxx/Kconfig` and Kbuild composite-object semantics. It integrates feature-specific objects with common driver code and sets a local include path needed by the tracing framework.

## Risks

Object list ordering can matter when initialization sections or trace definitions rely on symbols being present. Optional feature objects must remain synchronized with Kconfig dependencies and source-level `#ifdef` expectations. Missing `CFLAGS_trace.o` would break trace header discovery for tracing builds.

## Test Signals

Build the driver as built-in and module with base-only, PTP-enabled, LED-enabled, and combined configurations. Confirm `mv88e6xxx.o` includes expected optional objects and that `trace.o` compiles with its local include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Makefile -->
