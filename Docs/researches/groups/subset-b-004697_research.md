# subset-b-004697 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_main.c

## Purpose
`realtek_main.c` is the phylib driver collection for Realtek Ethernet PHYs, ranging from 10/100 RTL8201 parts through gigabit RTL8211 variants, multi-gigabit RTL822x/RTL8251/RTL8261 devices, RTL8224 cable-test-capable ports, internal NBASE-T PHYs, SFP dummy mode, and RTL9000A automotive Ethernet. It maps many PHY IDs and match predicates to `struct phy_driver` callbacks and hides Realtek-specific page, vendor-MMD, interrupt, WoL, LED, RGMII delay, SerDes, cable-test, and package-register behavior behind standard phylib/ethtool hooks.

## Important APIs, Types, And Functions
The private state is `struct rtl821x_priv`, carrying device-tree policy flags, an optional clock, and the saved RTL8211F interrupt-enable value. Page helpers are `rtl821x_read_page()`, `rtl821x_write_page()`, `rtl821x_read_ext_page()`, and `rtl821x_modify_ext_page()`. Probe/configuration functions include `rtl821x_probe()`, `rtl8211f_probe()`, `rtl8211e_config_init()`, `rtl8211f_config_init()`, `rtl822x_config_init()`, `rtl822xb_config_init()`, `rtl8224_config_init()`, and `rtl9000a_config_init()`.

Important operational callbacks include the RTL8201/RTL821x/RTL8211F/RTL8221B/RTL9000A interrupt ack/config/handler functions, `rtl8211f_get_wol()` and `rtl8211f_set_wol()`, LED offload functions for RTL8211E/F, `rtlgen_read_status()` and `rtlgen_decode_physr()`, vendor-MMD shims `rtlgen_*_mmd()`, `rtl822x*_read_mmd()` and `rtl822x*_write_mmd()`, SerDes/in-band functions `rtl822x_set_serdes_option_mode()`, `rtl822x_config_inband()`, and `rtl822x_inband_caps()`, and RTL8224 cable-test helpers.

## Control Flow
Driver binding flows through `module_phy_driver(realtek_drvs)`. Probe allocates private state, enables an optional PHY clock, reads Realtek DT booleans, and for RTL8211F disables PME events and optionally registers the PHY IRQ as a wake source. Config init then writes model-specific registers: RTL8211E/F set RGMII delays, RTL8211F applies ALDPS/SSC/CLKOUT policy, RTL822x selects SerDes option mode, RTL8224 applies package pair order/polarity, and RTL8366RB enables power save.

Status reads usually call a generic phylib status reader, then read `RTL_PHYSR` to recover actual speed, duplex, and master/slave state after downshift or NBASE-T negotiation. RTL822x additionally reads 2.5G/5G/10G advertisement and link-partner vendor registers, while Clause 45 paths combine generic C45 state with vendor C22-mapped registers for 1000Base-T and actual speed. Interrupt paths enable a model-specific mask, clear status by reading the interrupt status register, and call `phy_trigger_machine()` when enabled bits are observed. WoL writes the MAC address and magic-packet event bits into RTL8211F WoL pages and changes suspend interrupt routing to PME-only.

## State And Persistence
Persistent runtime state lives in `phydev`, page-selected PHY registers, optional `rtl821x_priv`, package registers for multiport RTL8224, and wakeup/clock state in the device model. The driver preserves board strap values unless a DT property or phylib interface mode requires overriding them. Suspend/resume paths coordinate power state with WoL and optional clocks, and several resume paths sleep 20 ms because internal Realtek PHYs are not immediately ready.

## Dependencies And Integration Points
The file depends on Linux phylib, ethtool netlink cable-test reporting, OF/device properties, wake IRQ helpers, optional clocks, LED netdev trigger hardware offload, and Realtek headers under `net/phy/realtek_phy.h` plus local `realtek.h`. Integration is almost entirely via `struct phy_driver` callbacks consumed by phylib, phylink in-band/rate-matching callbacks, ethtool WoL/cable-test/LED operations, and MDIO Clause 22/45 bus operations.

## Risks And Edge Cases
Many operations use undocumented magic register sequences, so regressions can be hardware- and revision-specific. Page switching must restore the previous page on all error paths; several lower-level RTL822x MMD accessors manually restore pages and can leave a wrong page if restore writes fail. RTL8211F ALDPS can stop RXC for long intervals and is wisely opt-in, but wrong DT usage can break MAC receive logic. WoL depends on `attached_dev->dev_addr`, valid IRQ wiring, and PME reset sequencing. `rtlgen_write_mmd()` appears suspicious for AN EEE advertisement because it passes `regnum` where the vendor register address is expected in one branch. Cable-test length conversion is vendor-derived and should be treated as approximate. RTL9000A `config_intr()` writes `GINMR` twice, which is harmless-looking but worth regression coverage.

## Test Signals
Useful signals include boot probe logs for each matched PHY ID, phylib link transitions across forced and autoneg modes, RGMII delay verification with each `phy-mode`, suspend/resume with and without WoL, wake-on-magic behavior, interrupt vs polling operation, LED hardware trigger get/set for all three LEDs, ethtool link-mode advertisement for 2.5G/5G/10G parts, SGMII/2500Base-X in-band mode changes, RTL8224 cable-test result reporting, and DT property validation for clock, ALDPS, SSC, pair order, and pair polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/rockchip.c

## Purpose
`rockchip.c` is a small phylib driver for Rockchip integrated 10/100 Ethernet PHYs matching `INTERNAL_EPHY_ID`. It applies analog/DSP tuning, disables problematic auto-MDIX behavior by default, supports explicit MDI/MDI-X control during autoneg configuration, and re-applies analog tuning when the PHY transitions to 100 Mbps.

## Important APIs, Types, And Functions
The main helpers are `rockchip_init_tstmode()`, `rockchip_close_tstmode()`, `rockchip_integrated_phy_analog_init()`, `rockchip_integrated_phy_config_init()`, `rockchip_link_change_notify()`, `rockchip_set_polarity()`, `rockchip_config_aneg()`, and `rockchip_phy_resume()`. The exported integration point is the `rockchip_phy_driver[]` array registered with `module_phy_driver()`.

## Control Flow
On config init, the driver reads `MII_INTERNAL_CTRL_STATUS`, clears `MII_AUTO_MDIX_EN`, writes the result, then enters the test register bank and writes a vendor analog amplitude value through `SMI_ADDR_TSTWRITE` plus `TSTCNTL_WR | WR_ADDR_A7CFG`. `config_aneg` first forces the requested MDI polarity if `phydev->mdix` is fixed, then delegates negotiation to `genphy_config_aneg()`. `link_change_notify` re-runs analog initialization when phylib reports `PHY_RUNNING` at 100 Mbps, because mode switching from 10BT to 100BT resets DSP/AFE registers. Resume calls `genphy_resume()` and then repeats config init.

## State And Persistence
There is no private allocation. State persists in PHY vendor registers and in phylib fields such as `phydev->mdix`, `state`, and `speed`. Test mode is only a transient access mechanism; the driver returns to the basic register bank after analog writes.

## Dependencies And Integration Points
The file depends on Linux phylib, MII constants, ethtool MDIX values, and module registration. Its callbacks integrate with phylib config, autoneg, suspend/resume, soft reset, and link-change notification.

## Risks And Edge Cases
Analog programming uses magic values and assumes the test-mode sequence is stable across matched revisions. `rockchip_phy_resume()` ignores the return value from `genphy_resume()`, so a resume error can be hidden by a later config result. Auto-MDIX is disabled during init as a board workaround, which may surprise deployments expecting automatic cable crossover unless user MDIX policy is applied later.

## Test Signals
Check probe matching, init register writes, 10-to-100 link transitions, forced MDI and MDI-X operation, autoneg restart behavior, suspend/resume after link loss, and failure injection for test-mode register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp-bus.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/sfp-bus.c

## Purpose
`sfp-bus.c` implements the rendezvous layer between an SFP socket driver and an upstream MAC/phylink user. It owns `struct sfp_bus`, parses module EEPROM identity into phylink capabilities, tracks references by firmware node, connects optional module PHY devices, and forwards module/link lifecycle events between socket and upstream callbacks.

## Important APIs, Types, And Functions
`struct sfp_bus` stores a `kref`, global list node, fwnode key, socket ops/device, upstream ops/private pointer, optional `phy_device`, registration/start flags, and `struct sfp_module_caps`. Public exports include `sfp_get_module_caps()`, `sfp_select_interface()`, `sfp_bus_find_fwnode()`, `sfp_bus_add_upstream()`, `sfp_bus_del_upstream()`, `sfp_get_name()`, `sfp_add_phy()`, `sfp_remove_phy()`, `sfp_link_up()`, `sfp_link_down()`, `sfp_module_insert()`, `sfp_module_remove()`, `sfp_module_start()`, `sfp_module_stop()`, `sfp_register_socket()`, and `sfp_unregister_socket()`.

## Control Flow
An upstream driver calls `sfp_bus_find_fwnode()` to resolve its `sfp` firmware reference, then `sfp_bus_add_upstream()` to attach operations. The socket driver calls `sfp_register_socket()` with `sfp_socket_ops`. If both sides are present, `sfp_register_bus()` calls upstream `link_down`, connects any already-probed module PHY, attaches the socket, starts it if the upstream is already started, and finally calls upstream `attach`. Removal reverses that through `sfp_unregister_bus()`.

EEPROM parsing starts in `sfp_module_insert()`, which calls `sfp_init_module()`. The parser decodes connector type into `caps.port`, determines whether a copper PHY may exist, derives link modes and possible host interfaces from base compliance, extended compliance, bitrate ranges, cable fields, and fibre-channel hints, then applies optional quirk support adjustments. `sfp_select_interface()` chooses the preferred `phy_interface_t` from requested link modes, prioritizing 25G, 10G, 5G, 2.5G, SGMII, 1000BASE-X, and 100BASE-X in that order.

## State And Persistence
The bus list is process-global and protected by `sfp_mutex`; bus attach/detach operations are serialized under RTNL. Bus objects persist until the last socket/upstream/reference user drops the `kref`. The current module capabilities are overwritten on each module insertion and remain readable through `sfp_get_module_caps()` while the module is present.

## Dependencies And Integration Points
The file integrates with firmware-node properties, phylink link-mode helpers, ethtool module EEPROM interfaces, RTNL locking, phylib `phy_device` attachment, and the local `sfp.h` socket ops contract. It is used by MAC/phylink users upstream and by `sfp.c` downstream.

## Risks And Edge Cases
Registration order matters; both socket-first and upstream-first paths must behave identically. `sfp_register_bus()` assumes `bus->upstream_ops` exists when it calls `attach`, so callers must only invoke it after upstream setup. Capability decoding is necessarily heuristic for modules with incomplete or incorrect EEPROM data. If a callback returns an error during registration, the code clears only the side that failed and relies on reference cleanup to avoid stale bus state.

## Test Signals
Exercise socket-first and upstream-first registration, upstream start before socket attach, module insertion/removal with and without onboard PHY, EEPROM capability parsing for optical, copper, passive DAC, 2.5G/5G/10G/25G cases, quirk capability overrides, `sfp_select_interface()` fallback warnings, and refcount cleanup after unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/sfp.c

## Purpose
`sfp.c` is the platform driver for SFF/SFP cages. It manages GPIO and soft EEPROM control/status signals, reads module EEPROM over I2C or SMBus, applies vendor quirks, negotiates module power and rate-select behavior, creates MDIO-over-I2C buses for copper modules, reports ethtool EEPROM and hwmon data, and runs the hotplug/device/link state machines that connect the socket to `sfp-bus.c`.

## Important APIs, Types, And Functions
`struct sfp` is the central state container: device, I2C adapter, optional MDIO bus, SFP bus, module PHY, GPIOs/IRQs, state masks, delayed works, module/device/main state-machine fields, EEPROM ID, power/rate-select fields, quirk pointer, hwmon data, and debugfs entry. `struct sff_data` describes SFF vs SFP GPIO requirements and module validation. Key functions include I2C/SMBus accessors, `sfp_i2c_mdiobus_create()`, soft-state helpers, hwmon readers, quirk fixups, `sfp_sm_mod_probe()`, `sfp_sm_module()`, `sfp_sm_main()`, `sfp_check_state()`, `sfp_probe()`, `sfp_remove()`, and the `sfp_module_ops` socket operations.

## Control Flow
Probe allocates `struct sfp`, gets the referenced I2C adapter, obtains optional GPIOs, reads initial state, asserts TX disable, emits an insert event if a module is already present, requests GPIO IRQs or enables polling, registers the socket with `sfp_register_socket()`, and creates debugfs. GPIO IRQs or poll work call `sfp_check_state()`, which snapshots hardware/soft state, computes changed presence/LOS/TX_FAULT bits, and dispatches events under RTNL and `sm_mutex`.

The module state machine waits for serial EEPROM readiness after insertion, retries slow EEPROM reads, validates checksums, handles broken byte-only EEPROMs, applies Cotsworks EEPROM repair, finds quirks, determines power and rate-select policy, reports insertion upstream, switches high-power modules if allowed, then reaches present state. The main state machine waits for upstream device-up, starts soft polling when A2 is usable, enables TX, handles TX fault recovery, creates MDIO-over-I2C for copper modules, probes C22/C45/RollBall PHYs, starts the module upstream, and reports link up/down based on LOS semantics. Removal or device-down unwinds PHY attachment, MDIO bus, module start, TX enable, and soft polling.

## State And Persistence
Hardware signal state is protected by `st_mutex`; module/device/link state is protected by `sm_mutex`; state-machine entry points usually run under RTNL. Persistent state includes EEPROM identity, quirk-selected masks, high-power status, rate-select thresholds, delayed work timers, optional registered `phy_device`, and optional hwmon registration. The driver writes module EEPROM/control bytes for soft TX disable, rate select, high-power selection, and one Cotsworks EEPROM correction path.

## Dependencies And Integration Points
The driver depends on platform/OF matching (`sff,sff` and `sff,sfp`), GPIO descriptors, I2C/SMBus, mdio-i2c, phylib, RTNL, workqueues, hwmon, debugfs, ethtool module EEPROM APIs, and `sfp-bus.c` socket operations. It is the downstream socket half used by phylink-capable network devices.

## Risks And Edge Cases
The state machines are timing-sensitive and must tolerate slow or broken modules. Byte-only EEPROM fallback disables coherent 16-bit hwmon reads. Some quirks deliberately ignore LOS/TX_FAULT pins or change MDIO protocol, so regression coverage needs real hardware variants. Cotsworks EEPROM rewriting is invasive and must not trigger on unrelated modules. Missing `tx-disable` can leave optical modules emitting when unplugged. Error handling must avoid leaving MDIO buses or module PHYs registered after removal or upstream detach.

## Test Signals
Use hotplug insertion/removal, boot-with-module-present, GPIO IRQ and polling-only cages, SMBus-only adapters, valid and invalid EEPROM checksums, high-power modules above and below host limits, RollBall and C45 copper modules, LOS polarity variants, TX fault recovery exhaustion, ethtool EEPROM page reads, hwmon registration and alarms, debugfs state output, upstream open/close sequencing, and remove/shutdown races with delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/sfp.h

## Purpose
`sfp.h` is the private header shared by the SFP socket driver and bus layer. It defines quirk and socket-operation contracts and declares the socket-to-bus notification functions implemented in `sfp-bus.c`.

## Important APIs, Types, And Functions
`struct sfp_quirk` matches vendor and part strings and can provide a capability adjustment callback plus a runtime fixup callback. `struct sfp_socket_ops` lets the bus call into a socket for attach/detach, start/stop, signal-rate selection, and ethtool module EEPROM access. Function declarations cover PHY attach/detach, link up/down, module insert/remove/start/stop, and socket register/unregister.

## Control Flow
`sfp.c` implements `sfp_socket_ops` and registers a socket with `sfp_register_socket()`. `sfp-bus.c` calls those ops when an upstream appears or changes state, while `sfp.c` calls the declared notification functions to tell the upstream side about module PHYs, link state, and module lifecycle.

## State And Persistence
The header owns no state. It forward-declares `struct sfp` and relies on `struct sfp_bus`, `struct phy_device`, EEPROM IDs, and ethtool structures from included Linux headers.

## Dependencies And Integration Points
The header includes `<linux/ethtool.h>` and `<linux/sfp.h>`. It is private to `drivers/net/phy`, not a UAPI contract, and forms the local integration boundary between `sfp.c` and `sfp-bus.c`.

## Risks And Edge Cases
Callback contracts are implicit: callers must honor RTNL/state-machine locking rules documented in the C files. Adding a socket operation requires updates to both struct initializers and registration logic. Because quirk matching uses fixed-width EEPROM strings, quirk callbacks must be conservative.

## Test Signals
Build coverage should catch signature drift. Runtime coverage comes from SFP registration, module insertion, PHY attachment, link notifications, and ethtool EEPROM operations that traverse every declared callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/sfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/smsc.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/smsc.c

## Purpose
`smsc.c` supports SMSC/Microchip LAN83C185, LAN8187, LAN8700, LAN911x internal, LAN8710/LAN8720, LAN8740, and LAN8742 PHYs. It layers vendor interrupt handling, Energy Detect Power-Down tuning, MDIX policy, optional reference clock enablement, statistics, and LAN874x Wake-on-LAN filters on top of generic phylib behavior.

## Important APIs, Types, And Functions
`struct smsc_hw_stat` describes ethtool statistics, and `struct smsc_phy_priv` stores EDPD policy and whether the single WoL pattern is currently ARP or multicast. Exported helpers include `smsc_phy_config_intr()`, `smsc_phy_handle_interrupt()`, `smsc_phy_config_init()`, `lan87xx_read_status()`, `smsc_phy_get_tunable()`, `smsc_phy_set_tunable()`, and `smsc_phy_probe()`. LAN-specific helpers include `lan87xx_config_aneg()`, `lan95xx_config_aneg_ext()`, `lan87xx_phy_config_init()`, `lan874x_phy_config_init()`, `lan874x_get_wol()`, `lan874x_set_wol()`, and pattern/CRC helpers.

## Control Flow
Probe allocates private state, defaults EDPD to enabled with a 640 ms wait, honors `smsc,disable-energy-detect`, stores `phydev->priv`, and optionally enables a 50 MHz reference clock. Config init disables EDPD automatically when IRQ mode is used unless the user explicitly set a tunable. LAN87xx init forces a known Auto-MDIX default. Autoneg config selects fixed MDI for forced links unless users requested another MDIX mode, writes `SPECIAL_CTRL_STS`, then delegates to generic autoneg.

Status reads call `genphy_read_status()` and, when link is down with EDPD enabled in polling mode, temporarily disable EDPD, poll for energy, then re-enable EDPD. Interrupt config acks by reading `MII_LAN83C185_ISF`, writes the mask register, and triggers phylib on relevant interrupt status bits. LAN874x WoL programs unicast/broadcast/magic bits, one ARP or multicast filter pattern, optional destination MAC registers, and reads back enabled modes.

## State And Persistence
Private EDPD and WoL pattern state persists in `phydev->priv`; hardware state persists in vendor MII and PCS MMD registers. Statistics are read directly from the PHY symbol error counter. The driver does not persist configuration outside runtime PHY registers.

## Dependencies And Integration Points
The file depends on phylib, MII helpers, ethtool tunables/WoL/statistics, optional clocks, OF/device properties, CRC16, Ethernet address helpers, and `<linux/smscphy.h>` register definitions. It registers a `struct phy_driver` table and exports common SMSC helpers for other modules.

## Risks And Edge Cases
EDPD is unreliable with interrupts, and the driver only allows polling-mode wake probing for timed EDPD values. `lan87xx_config_aneg()` writes `SPECIAL_CTRL_STS` without checking the write return before continuing. LAN874x supports only one pattern filter, so ARP and multicast wake are mutually exclusive. WoL programming assumes an attached net device for MAC address access when magic or unicast wake is requested. Clock rate assumptions may expose board-DT issues.

## Test Signals
Cover each PHY ID match, optional clock probe-defer/failure, EDPD tunable values including invalid ranges and IRQ rejection, polling-mode cable insertion while in EDPD, forced 10/100 MDIX behavior, interrupt mask/status handling, symbol-error ethtool stats, LAN874x magic/unicast/broadcast/ARP/multicast WoL programming, and suspend/resume with WoL-enabled devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/smsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ste10Xp.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/ste10Xp.c

## Purpose
`ste10Xp.c` is a phylib driver for STMicroelectronics STe101p and STe100p PHYs. It performs a software reset during initialization and provides vendor interrupt mask/status handling for autoneg-complete, remote-fault, and link-down events.

## Important APIs, Types, And Functions
The key functions are `ste10Xp_config_init()`, `ste10Xp_ack_interrupt()`, `ste10Xp_config_intr()`, and `ste10Xp_handle_interrupt()`. The `ste10xp_pdriver[]` table registers STe101p and STe100p IDs with generic suspend/resume and the driver-specific init/interrupt callbacks.

## Control Flow
Config init reads `MII_BMCR`, sets `BMCR_RESET`, writes it back, then busy-waits reading `MII_BMCR` until reset clears. Interrupt enable first clears pending status by reading `MII_XCIIS`, then writes `MII_XIE_DEFAULT_MASK` to `MII_XIE`; disable writes zero and acks afterward. The interrupt handler reads `MII_XCIIS`, checks the same mask, and triggers the phylib state machine when a relevant event occurred.

## State And Persistence
The driver has no private state. Runtime state lives in standard BMCR plus vendor interrupt registers. Interrupt configuration persists in PHY registers until changed, reset, suspend, or power loss.

## Dependencies And Integration Points
It depends on phylib, MII constants, module registration, and generic suspend/resume. It integrates only through `struct phy_driver` callbacks and MDIO device ID matching.

## Risks And Edge Cases
The reset wait loop has no timeout and could spin forever if the PHY never clears `BMCR_RESET` or MDIO reads fail after the initial write. The loop does not handle negative reads during polling. Interrupt mask comments mention STe101P but the logic is shared with STe100p.

## Test Signals
Probe both PHY IDs, verify reset completion, inject MDIO read/write failures, exercise interrupt enable/disable order, trigger each masked interrupt source, and test behavior when reset never clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ste10Xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/stubs.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/stubs.c

## Purpose
`stubs.c` exports the global `phylib_stubs` pointer used by built-in networking code when `CONFIG_PHYLIB` can be a module. It provides an indirection point so core code can call PHY-library functionality without directly depending on module-only symbols.

## Important APIs, Types, And Functions
The only symbol is `const struct phylib_stubs *phylib_stubs`, exported with `EXPORT_SYMBOL_GPL()`. The struct type is declared in `<linux/phylib_stubs.h>`.

## Control Flow
There is no executable control flow in this file. Initialization and assignment of the pointer occur elsewhere; this compilation unit only defines storage and exports it.

## State And Persistence
The pointer is global kernel state. It is initially null and remains whatever the PHY library registration code sets it to. Consumers must handle the possibility that phylib is not loaded or has not populated the table.

## Dependencies And Integration Points
The file depends on the phylib stubs header and module export machinery. It integrates built-in network stack code with a modular phylib provider.

## Risks And Edge Cases
The primary risk is lifetime and null-pointer misuse by consumers. Since the pointer is exported global state, changes to the underlying `struct phylib_stubs` contract must remain synchronized across providers and callers.

## Test Signals
Build both built-in and modular PHYLIB configurations, verify exported symbol availability with module loading, and exercise callers when `phylib_stubs` is null and after it is populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/swphy.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/swphy.c

## Purpose
`swphy.c` emulates a small set of Clause 22 MII registers from `struct fixed_phy_status` for fixed-link software PHYs. It lets code that expects MDIO-like register reads observe link, speed, duplex, pause, and basic gigabit capability without real PHY hardware.

## Important APIs, Types, And Functions
`struct swmii_regs` holds synthesized `bmsr`, `lpa`, `lpagb`, and `estat` fragments. Static tables encode supported bits by speed and duplex. Public exports are `swphy_validate_state()` and `swphy_read_reg()`. `swphy_decode_speed()` maps integer speeds 10/100/1000 to internal table indexes.

## Control Flow
Validation checks only linked states and rejects unknown speeds with `-EINVAL`. Register reads reject register numbers above `MII_REGS_NUM`, decode speed and duplex, combine speed and duplex bit tables with bitwise AND, set link/autoneg-complete and link-partner bits only when `state->link` is true, then returns synthesized values for BMCR, BMSR, PHY IDs, LPA, STAT1000, and ESTATUS. Clause 45-over-Clause 22 control/data registers return an error instead of fake data; unknown supported-range registers return `0xffff`.

## State And Persistence
There is no stored state. Every read is derived from the caller-provided `fixed_phy_status`. The exported functions are pure except for warning logs on invalid speed.

## Dependencies And Integration Points
The file depends on MII bit definitions, phylib/fixed PHY structures, and `swphy.h`. It is used by fixed PHY infrastructure and any consumer needing software MII register emulation.

## Risks And Edge Cases
`swphy_read_reg()` warns and returns zero for invalid speed, so callers should validate state first. Only 10/100/1000 are representable. It always reports BMCR autoneg enabled and does not emulate every MII register. Returning `-1` for unsupported registers follows this local convention but can be ambiguous for callers expecting negative errno values.

## Test Signals
Validate linked and unlinked states for 10/100/1000 half/full duplex, pause/asym-pause propagation, invalid speed rejection, register-boundary behavior, Clause 45 register rejection, and fixed PHY users reading BMCR/BMSR/LPA/STAT1000/ESTATUS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/swphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/swphy.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/swphy.h

## Purpose
`swphy.h` declares the software PHY emulation interface implemented by `swphy.c`. It keeps fixed PHY users independent from the implementation details of synthesized MII registers.

## Important APIs, Types, And Functions
The header forward-declares `struct fixed_phy_status` and declares `swphy_validate_state()` plus `swphy_read_reg()`.

## Control Flow
There is no control flow in the header. Consumers include it to validate a fixed-link status and to request an emulated MII register value.

## State And Persistence
The header owns no state and exposes no globals. All state comes from the caller-supplied `fixed_phy_status`.

## Dependencies And Integration Points
The include guard `SWPHY_H` prevents duplicate declarations. The header is local to the PHY subsystem and is included by `swphy.c` and fixed PHY code that needs these helpers.

## Risks And Edge Cases
The contract does not document exact return conventions for unsupported registers, so consumers must align with `swphy.c`. Any extension to support new speeds or registers requires keeping validation and read emulation synchronized.

## Test Signals
Build coverage for all includers, plus runtime fixed-link tests that call both declared functions through the fixed PHY stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/swphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/teranetics.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/teranetics.c

## Purpose
`teranetics.c` is a Clause 45 phylib driver for the Teranetics TN2020 10G PHY. It reports fixed 10G full-duplex operation and handles a copper-versus-fiber distinction through a vendor register when checking autonegotiation and link status.

## Important APIs, Types, And Functions
Key functions are `teranetics_aneg_done()`, `teranetics_read_status()`, and `teranetics_match_phy_device()`. The driver table sets `PHY_10GBIT_FEATURES`, uses `gen10g_config_aneg`, custom aneg/status callbacks, and matches device ID slot 3 against `PHY_ID_TN2020`.

## Control Flow
`teranetics_aneg_done()` reads VEND1 register 93; when it is zero, the port is treated as copper and generic C45 autoneg completion is used, otherwise fiber mode returns done unconditionally. `teranetics_read_status()` starts with link up, 10G, full duplex. For copper mode it requires all PHYXS lane sync/alignment bits in `MDIO_PHYXS_LNSTAT` and AN `MDIO_STAT1_LSTATUS`; missing bits clear link.

## State And Persistence
The driver stores no private state. Status is derived from Clause 45 MMD registers and written into `phydev->link`, `speed`, and `duplex` on each read.

## Dependencies And Integration Points
It depends on phylib, Clause 45 MDIO constants, ethtool feature definitions, and module MDIO matching. It integrates as a specialized 10G PHY driver.

## Risks And Edge Cases
The VEND1 register 93 mode test treats a zero read as copper but does not handle negative errors in `teranetics_aneg_done()`. Fiber mode unconditionally reports autoneg done and link remains up unless copper checks run, so incorrect mode detection can produce false carrier. Link status checks are narrow to TN2020 lane-ready semantics.

## Test Signals
Test C45 matching by device ID, copper and fiber mode register 93 values, PHYXS lane sync/alignment failures, AN link-status failures, and MDIO read errors during status and autoneg checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/teranetics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/uPD60620.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/uPD60620.c

## Purpose
`uPD60620.c` supports the Renesas uPD60620 PHY. It configures special modes for passive hub support and decodes link, speed, duplex, link-partner advertisement, and pause from vendor/basic MII registers.

## Important APIs, Types, And Functions
The two callbacks are `upd60620_config_init()` and `upd60620_read_status()`. The `upd60620_driver` table matches `UPD60620_PHY_ID` with mask `0xfffffffe` and installs those callbacks.

## Control Flow
Config init writes `PHY_SPM` with `0x0180 | phydev->mdio.addr`, enabling all speeds and half-duplex parallel detect while preserving the MDIO address bits. Status reads `MII_BMSR`; if autoneg complete or link status is set, it reads `PHY_PHYSCR`, checks speed bits, sets link, defaults to 10 half, upgrades to 100 and full duplex as indicated, reads `MII_LPA`, converts link-partner advertisement to linkmode bits, and resolves pause.

## State And Persistence
There is no private state. The special mode register persists in hardware until reset or reconfiguration. Each status read resets link-partner advertising and pause fields before decoding current hardware state.

## Dependencies And Integration Points
The file depends on phylib, standard MII register definitions, and module PHY registration. It integrates through `struct phy_driver` callbacks only.

## Risks And Edge Cases
The link condition accepts either autoneg complete or BMSR link status, which can report link in partially negotiated states. Only 10/100 speeds are decoded; unexpected `PHY_PHYSCR` speed bits leave link down. The config value is a magic special-mode setting that may be strap-sensitive.

## Test Signals
Verify special-mode writes for several MDIO addresses, status decoding for 10/100 half/full, no-link behavior, link-partner advertisement conversion, pause resolution, and MDIO read failures for BMSR, PHYSCR, and LPA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/uPD60620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/vitesse.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/vitesse.c

## Purpose
`vitesse.c` is the phylib driver collection for Vitesse/Microsemi PHYs including VSC82xx, VSC73xx, VSC86xx, and VSC8211/8221 devices. It provides model-specific initialization sequences, RGMII skew control, SGMII in-band configuration, downshift tunables, MDIX controls, interrupt handling, and forced-mode auto-crossover setup.

## Important APIs, Types, And Functions
Important helpers include `vsc824x_config_init()`, `vsc824x_add_skew()`, `vsc8662_inband_caps()`, `vsc8662_config_inband()`, `vsc73xx_read_page()`, `vsc73xx_write_page()`, `vsc73xx_get_downshift()`, `vsc73xx_set_downshift()`, `vsc73xx_config_init()`, `vsc738x_config_init()`, `vsc739x_config_init()`, `vsc73xx_mdix_set()`, `vsc73xx_read_status()`, `vsc8601_config_init()`, `vsc82xx_config_intr()`, `vsc82xx_handle_interrupt()`, `vsc8221_config_init()`, and `vsc82x4_config_aneg()`.

## Control Flow
Driver registration maps each PHY ID to the appropriate init and operation callbacks. VSC824x init writes auxiliary control/status and optionally applies TX/RX skew for `rgmii-id`. VSC8662 in-band config toggles MAC autoneg/bypass bits and soft-resets if the extended control bit changed. VSC738x/VSC739x init executes vendor application-note register sequences, then common VSC73xx setup configures receiver/LEDs, enables maximum downshift, and defaults MDIX to auto. VSC73xx autoneg writes MDIX policy then calls generic autoneg; status first reads current MDI/MDI-X indication, then delegates to `genphy_read_status()`. VSC82x4 forced 10/100 operation calls `genphy_setup_forced()` and writes extended reserved registers to keep auto crossover active.

## State And Persistence
There is no private allocation. Runtime policy persists in PHY registers and phylib fields (`mdix_ctrl`, `mdix`, interface mode, autoneg, speed). Page state is accessed through `read_page`/`write_page` callbacks for VSC73xx extended page operations.

## Dependencies And Integration Points
The driver depends on phylib, MII/ethtool constants, bitfield helpers, and module MDIO matching. Integration points include phylib config/init/aneg/status/interrupt callbacks, ethtool PHY downshift tunables, in-band negotiation callbacks, and page access callbacks.

## Risks And Edge Cases
Several initialization sequences are undocumented magic values from application notes, so revision-specific regressions are plausible. VSC738x revision 0 has a special sequence based on low PHY ID revision bits. Interrupt disable must read status before masking because some Vitesse parts cannot clear interrupts after disabling. `vsc73xx_mdix_get()` does not check for negative `phy_read()` return values before interpreting bits. Forced MDIX mode for VSC73xx cannot truly force MDIX and falls back to autoconfig.

## Test Signals
Test each matched PHY ID, RGMII-ID skew application and non-application, VSC8662 in-band enable/disable/bypass with reset behavior, VSC73xx downshift get/set including invalid counts, forced and autoneg MDIX modes, interrupt enable/disable and handler masks, VSC738x rev 0 and nonzero init paths, and forced 10/100 auto-crossover programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/vitesse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/xilinx_gmii2rgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/xilinx_gmii2rgmii.c

## Purpose
`xilinx_gmii2rgmii.c` is an MDIO driver for the Xilinx GMII-to-RGMII converter. It finds the real downstream PHY referenced by `phy-handle`, wraps that PHY driver's status and loopback callbacks, and programs the converter speed bits whenever the PHY speed changes.

## Important APIs, Types, And Functions
`struct gmii2rgmii` stores the attached `phy_device`, original `phy_driver`, copied wrapper `phy_driver`, and converter `mdio_device`. Main functions are `xgmiitorgmii_configure()`, `xgmiitorgmii_read_status()`, `xgmiitorgmii_set_loopback()`, and `xgmiitorgmii_probe()`.

## Control Flow
Probe allocates private data, enables an optional clock, parses `phy-handle`, finds the PHY device, defers if the PHY or its driver is not ready, copies the original driver structure, overrides `read_status` and `set_loopback`, stores private data on the real PHY's MDIO device, and replaces `phy_dev->drv` with the wrapper. Status and loopback callbacks call the original driver implementation or generic fallback first, then write `XILINX_GMII2RGMII_REG` speed bits for 10/100/1000 according to `phydev->speed`.

## State And Persistence
Persistent state is the wrapper object and the converter register value. The driver mutates the attached PHY's driver pointer at runtime; the original pointer is retained in private data for delegation.

## Dependencies And Integration Points
It depends on MDIO driver registration, phylib, OF MDIO lookup, optional clocks, and standard BMCR speed bits. It integrates between a converter MDIO device and an already registered external PHY.

## Risks And Edge Cases
The wrapper approach is invasive: it replaces `phy_dev->drv` and there is no remove callback restoring the original driver pointer. Probe deferral handles absent/not-ready PHYs, but lifetime coupling between converter and PHY must remain valid. `xgmiitorgmii_configure()` does not check MDIO read/write errors, so converter programming failures are silent. Unknown speeds fall through to 10 Mbps.

## Test Signals
Test probe ordering with PHY unavailable and later ready, optional clock failures, status changes at 10/100/1000, loopback configuration, MDIO write verification, removal/unbind behavior, and downstream PHY drivers with and without custom `read_status` or `set_loopback`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/xilinx_gmii2rgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/plip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/plip/Kconfig

## Purpose
`Kconfig` defines the build-time configuration option for the Parallel Line Internet Protocol network driver. It presents `CONFIG_PLIP` as a tristate option for parallel-port based local networking.

## Important APIs, Types, And Functions
The only symbol is `config PLIP`, a tristate prompt "PLIP (parallel port) support" with `depends on PARPORT`. The help text documents PLIP use cases, cable modes, documentation references, module name, and approximate kernel size impact.

## Control Flow
Kconfig evaluation exposes PLIP only when parallel-port support is enabled. The selected value drives the Makefile through `CONFIG_PLIP`: built-in, module, or omitted.

## State And Persistence
The persistent state is the user's kernel configuration. Selecting `M` builds `plip.ko`; selecting `Y` links it into the kernel image.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, `PARPORT`, the PLIP driver source selected by the Makefile, and user-facing documentation under `Documentation/networking/plip.rst`.

## Risks And Edge Cases
The help text is historically oriented and references old installation workflows and external URLs. The dependency only checks `PARPORT`; actual runtime use still depends on suitable parallel-port hardware and cabling. Compatibility with Linux 1.0.x PLIP is explicitly not supported.

## Test Signals
Run configuration tests with `PARPORT=n/y/m`, verify `CONFIG_PLIP` visibility and tristate behavior, confirm module naming as `plip`, and build all selected modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/plip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/plip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/plip/Makefile

## Purpose
`Makefile` connects the PLIP driver object to the kernel build system. It builds `plip.o` when `CONFIG_PLIP` is enabled as built-in or module.

## Important APIs, Types, And Functions
The sole build rule is `obj-$(CONFIG_PLIP) += plip.o`.

## Control Flow
Kbuild expands `obj-y` for built-in PLIP or `obj-m` for module PLIP based on the Kconfig value. If `CONFIG_PLIP` is unset, no object is added.

## State And Persistence
The file holds no runtime state. Build state is determined entirely by `.config` and Kbuild.

## Dependencies And Integration Points
It integrates with `drivers/net/plip/Kconfig`, the kernel recursive Make system, and the `plip.c` source object in the same directory.

## Risks And Edge Cases
The rule assumes `plip.c` exists and produces a single `plip.o`. Any future split into helper objects would require updating this Makefile to keep module linkage complete.

## Test Signals
Build with `CONFIG_PLIP=y`, `CONFIG_PLIP=m`, and unset; verify built-in object inclusion and module generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/plip/Makefile -->
