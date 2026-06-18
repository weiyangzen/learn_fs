# subset-b-004696 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylink.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phylink.c

Purpose: Implements the kernel phylink core, which models a MAC-to-link relationship where the media side can be a fixed link, a phylib PHY, a PCS using in-band status, or an SFP cage with hot-pluggable modules. It normalizes firmware link descriptions, MAC capabilities, PCS capabilities, PHY capabilities, ethtool settings, EEE, Wake-on-LAN, MII ioctls, and SFP events into a single link state machine for MAC drivers.

Important APIs and functions: Exported entry points include `phylink_create()`, `phylink_destroy()`, `phylink_connect_phy()`, `phylink_fwnode_phy_connect()`, `phylink_disconnect_phy()`, `phylink_start()`, `phylink_stop()`, `phylink_suspend()`, `phylink_resume()`, ethtool helpers for ksettings, pause, EEE, WoL, MII ioctl, speed down/up, replay helpers, and PCS decode/config helpers such as `phylink_mii_c22_pcs_decode_state()` and `phylink_mii_c22_pcs_config()`. The central type is private `struct phylink`, which stores configured/requested/active autoneg modes, supported and advertised masks, current PHY/PCS/MAC state, SFP metadata, EEE state, WoL state, GPIO/IRQ/timer state, and workqueue resolver state.

Control flow: Creation initializes supported interfaces, default pause and EEE settings, parses fixed-link or in-band firmware properties, validates MAC/PCS capabilities, and registers an SFP upstream if present. Start performs an initial major MAC/PCS configuration, clears the stopped disable bit, starts fixed-link polling or IRQs, starts attached PHYs, and starts SFP upstream handling. Link changes from PHY, PCS, MAC, GPIO, timer, SFP, ethtool, or replay paths queue `phylink_resolve()`. The resolver serializes against PHY detach, combines fixed/PHY/PCS link data, applies manual pause overrides, forces link down before major interface changes, calls `phylink_major_config()` when interface or PCS configuration changes, and then calls MAC/PCS link-up or link-down callbacks and carrier updates.

State and persistence: All state is runtime-only in `struct phylink`; firmware and ethtool settings are reflected into `link_config`, `supported`, `supported_lpi`, `eee_cfg`, and WoL fields. Disable bits (`STOPPED`, `LINK`, `MAC_WOL`, `REPLAY`) gate resolver behavior. `state_mutex` protects link state and EEE/WoL-affecting transitions, while `phydev_mutex` prevents resolver races with attach/detach. Fixed links may persist a GPIO descriptor and IRQ; SFP state persists a bus reference, module support masks, possible interfaces, and selected port while the instance lives.

Dependencies and integration: Depends on phylib, phylink public headers, PCS callbacks, MAC driver callbacks, `phy-caps.h`, fixed PHY emulation via `swphy`, SFP bus upstream callbacks, fwnode/OF/ACPI parsing, GPIO, timers, workqueues, rtnl locking, ethtool link modes, EEE and WoL helpers, and MDIO clause 22/45 accessors. MAC drivers integrate by providing `phylink_config`, supported interface masks, MAC ops, optional PCS selection, and calling phylink lifecycle and notification helpers.

Risks and test signals: High-risk behavior is concentrated in capability validation across MAC/PCS/PHY/SFP, in-band negotiation selection, resolver locking, link-down-before-reconfigure sequencing, SFP hotplug with or without module PHYs, EEE clock stop coordination, WoL suspend/resume balance, and MII emulation for fixed or in-band links. Test fixed-link GPIO and polling, PHY attach/detach, C22 and C45 PHYs, SGMII/Base-X/USXGMII in-band modes, SFP optical and PHY modules, interface changes through ethtool, pause and EEE reconfiguration, WoL suspend/resume, replay begin/end, failed PCS/MAC callbacks, and MII ioctls with and without an attached PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Kconfig

Purpose: Defines the Qualcomm/Atheros PHY driver build options under the PHY subsystem. It separates the shared Qualcomm helper library from concrete PHY families so multiple drivers can select common register, interrupt, WoL, LED, cable-test, and statistic helpers.

Important options: `QCOM_NET_PHYLIB` is a hidden tristate selected by all Qualcomm driver families. `AT803X_PHY` builds support for AR8030, AR8031, AR8033, AR8035, and IPQ5018 and depends on `REGULATOR` because AR8031 exposes VDDIO/VDDH regulators. `QCA83XX_PHY` supports internal QCA833x switch PHYs. `QCA808X_PHY` supports QCA8081. `QCA807X_PHY` supports QCA8072/QCA8075 and selects `PHY_PACKAGE`, with an `OF_MDIO` dependency because package-level configuration is device-tree driven.

Control flow: This file has no runtime control flow. Kconfig evaluates dependencies and `select` clauses, then the adjacent Makefile maps enabled symbols to objects. The hidden shared symbol ensures `qcom-phy-lib.o` is linked whenever any family using the exported helpers is enabled.

State and persistence: State is build-time configuration only. Tristate choices determine built-in versus module output and ensure unavailable dependency combinations are rejected before compile time.

Dependencies and integration: Integrates with the parent PHY Kconfig tree, the qcom Makefile, regulator framework availability, OF MDIO package descriptions, and `PHY_PACKAGE` support for multi-PHY packages.

Risks and test signals: Main risks are missing `select QCOM_NET_PHYLIB` for a driver that uses shared symbols, dependency drift for regulator or package APIs, and modules that fail to link when a selected helper is not built. Test with each Qualcomm symbol as `m` and `y`, all disabled, and mixed combinations involving `OF_MDIO`, `REGULATOR`, and `PHY_PACKAGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Makefile

Purpose: Maps Qualcomm PHY Kconfig symbols to kbuild objects.

Important entries: `CONFIG_QCOM_NET_PHYLIB` builds `qcom-phy-lib.o`; `CONFIG_AT803X_PHY` builds `at803x.o`; `CONFIG_QCA83XX_PHY` builds `qca83xx.o`; `CONFIG_QCA808X_PHY` builds `qca808x.o`; `CONFIG_QCA807X_PHY` builds `qca807x.o`.

Control flow: kbuild expands each `obj-$(CONFIG_...)` line to either built-in object linkage, module linkage, or omission. Because family Kconfig options select `QCOM_NET_PHYLIB`, shared helper symbols are available to the family modules.

State and persistence: No runtime state. This is persistent build metadata only.

Dependencies and integration: Integrates with `drivers/net/phy/qcom/Kconfig`, module autoload tables in each C driver, and the kernel's composite object/module build process.

Risks and test signals: Risks are stale symbol names, missing object entries for new drivers, or helper object omission leading to unresolved exports. Test by building every legal built-in/module combination and confirming expected module/object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/at803x.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/at803x.c

Purpose: Implements Qualcomm Atheros AR803x-family and related IPQ5018 PHY support. It configures RGMII delays, fiber/copper page selection, SmartEEE, clock output, hibernation, PLL behavior, regulators, MII-port attachments, cable diagnostics, and several device-specific link/reset quirks.

Important APIs and functions: Driver callbacks are wired through `at803x_driver[]` for AR8030, AR8031/AR8033, AR8032, AR8035, AR9331, IPQ5018, and QCA9561. Key helpers include `at803x_probe()`, `at8031_probe()`, `at8035_probe()`, `ipq5018_probe()`, `at803x_config_init()`, `at8031_config_init()`, `ipq5018_config_init()`, `at803x_config_aneg()`, `at8031_read_status()`, `at803x_link_change_notify()`, `ipq5018_link_change_notify()`, and cable-test helpers. Private structs hold AT803x DT-derived flags and regulator handles, saved reset context, and IPQ5018 reset/DAC state.

Control flow: Probe allocates private state, parses DT properties, optionally registers AR8031 regulators, detects AR8031 fiber/1000Base-X mode from chip configuration, disables default 1588 WoL, or resets IPQ5018 through reset controls. Config init applies RX/TX delay settings based on RGMII interface mode, configures SmartEEE timing or disables it, sets clock output bits, disables hibernation when required, disables extended next page, and applies per-chip analog thresholds. Link-change callbacks reset AR8030 on link loss or toggle IPQ5018 FIFO reset. Cable tests either defer work to `get_status()` or program IPQ5018/QCA808x thresholds before shared status collection.

State and persistence: Runtime state is in `phydev->priv`, MDIO registers, optional regulator devices, reset controls, and hardware page selection. Context save/restore preserves selected registers across AR8030 hardware reset. No persistent storage is used; DT properties and straps are reapplied on probe or init.

Dependencies and integration: Depends on phylib, shared `qcom.h` helpers from `qcom-phy-lib.c`, regulators, reset controls, OF properties, `dt-bindings/net/qca-ar803x.h`, phylink link mode helpers for MII port support, and ethtool cable-test reporting.

Risks and test signals: Risks include wrong copper/fiber page selection, disruptive MDIX resets, invalid DT clock/SmartEEE properties, regulator registration failures, preserving context across hardware reset, IPQ5018 reset timing, and cable diagnostics that intentionally disturb autonegotiation. Test each PHY ID, RGMII delay variants, fiber and copper AR8031, WoL enable/disable, suspend/resume with WoL, regulator voltage selection, DT property validation, cable tests for two-pair and four-pair parts, link-loss reset quirks, and module autoload tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/at803x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca807x.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca807x.c

Purpose: Implements QCA8072 and QCA8075 PHY support, including PSGMII/QSGMII package configuration, combo copper/fiber port switching, DAC power tuning, LED offload, optional LED-as-GPIO output, shared hardware counters, cable-test integration, and WoL/tunable reuse from the AT803x helper library.

Important APIs and functions: Driver callbacks are in `qca807x_drivers[]`. Major helpers include `qca807x_probe()`, `qca807x_phy_package_probe_once()`, `qca807x_phy_package_config_init_once()`, `qca807x_config_init()`, `qca807x_read_status()`, `qca807x_read_fiber_status()`, `qca807x_attach_mii_port()`, `qca807x_configure_serdes()`, LED callbacks, optional GPIO chip callbacks, and stats callbacks using `qcom_phy_update_stats()`.

Control flow: Probe joins the PHY package, parses package-wide transmit drive strength and optional package mode once, parses per-PHY DAC DT flags, optionally registers a two-line GPIO controller, detects combo-port capability, and stores private state. Config init runs package initialization once, setting package mode, resetting PQSGMII analog logic, applying AZ workaround, setting TX drive strength, and preventing PSGMII hibernation; then it configures shared counters and DAC bias/amplitude policy. Status reads dispatch to C37 fiber status or AT803x copper status based on advertised fiber support and `phydev->port`. MII port attach exposes 1000Base-X/100Base-X interfaces, and enabling the port flips combo registers and fiber autodetection.

State and persistence: Per-package state stores selected interface package mode and PQSGMII TX drive strength. Per-PHY state stores DAC policy booleans and accumulated 64-bit stats. Optional GPIO state stores a `phy_device` pointer. Hardware state lives in package registers, MMD7 LED/counter registers, and copper/fiber page selection. State is runtime-only and rederived from DT plus hardware registers.

Dependencies and integration: Depends on phylib, OF MDIO package helpers, `PHY_PACKAGE`, optional `GPIOLIB`, `phy_port` callbacks for combo ports, shared Qualcomm LED/counter/WoL/interrupt/tunable helpers, C37 status helpers, and ethtool LED trigger rules.

Risks and test signals: Risks include package init races or wrong once-only behavior, mismatched forced package mode, destructive SerDes reset timing, combo port `phydev->port` mismatch, LED register differences between TP and fiber modes, GPIO use conflicting with LED control, and clear-on-read statistic accounting. Test QCA8072/QCA8075 probing across package addresses, PSGMII and QSGMII DT modes, SFP combo enable/disable, copper/fiber status reads, LED hw-control rules, GPIO output mode, cable tests, WoL, stats accumulation, and invalid DT drive-strength rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca807x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca808x.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca808x.c

Purpose: Implements the Qualcomm QCA8081 PHY driver for 1G/2.5G copper operation with SGMII or 2500Base-X host interfaces. It handles 802.3az analog tuning, fast retrain, master/slave seed randomization, 1G-only chip detection, cable diagnostics, LED offload and polarity, hardware counters, WoL, interrupts, and downshift tunables.

Important APIs and functions: The `qca808x_driver[]` entry supplies `probe`, `config_init`, `get_features`, `config_aneg`, `read_status`, `soft_reset`, cable-test callbacks, link-change notification, LED callbacks, and stats callbacks. Key helpers are `qca808x_phy_fast_retrain_config()`, `qca808x_phy_ms_seed_enable()`, `qca808x_fill_possible_interfaces()`, `qca808x_config_init()`, `qca808x_read_status()`, `qca808x_config_aneg()`, `qca808x_cable_test_start()`, LED parsing/control helpers, and `qca808x_led_polarity_set()`.

Control flow: Probe allocates private state and marks LED polarity unset. Config init defaults LEDs active-high unless overridden, programs 802.3az AFE/training registers, enables fast retrain and randomized slave seed when 2.5G is supported, fills possible host interfaces, enables shared counters, and sets ADC threshold. Feature discovery reads C45 PMA abilities, manually adds autoneg, and removes 2.5G for 1G-only chips. Autoneg setup applies AT803x MDIX preparation, handles forced C45 PMA setup, programs 2.5G advertisement in 10GBASE-T AN registers, and delegates to generic AN. Status updates LP 2.5G advertisement, reads generic status, decodes QCA808x-specific speed bits, selects SGMII or 2500Base-X interface, and refreshes seed behavior on link-down.

State and persistence: Private state stores global LED polarity policy and accumulated Qualcomm hardware stats. Master/slave seed values are random and written to debug registers at init, reset, and link-down. Possible host interface bits persist in `phydev->possible_interfaces`; hardware counters are accumulated in software because the hardware is configured read-clear.

Dependencies and integration: Depends on phylib C45 helpers, shared Qualcomm helpers from `qcom-phy-lib.c`, `qcom.h` register definitions, ethtool cable-test and LED trigger APIs, random number generation, and MDIO access to a companion SerDes FIFO address.

Risks and test signals: Risks include incorrect 1G-only detection, unstable master/slave negotiation if seed policy is wrong, forced-mode programming split between C45 PMA and C22 BMCR, interface switching errors at 2.5G, LED polarity being global rather than per LED, and link-change writes to `addr + 1`. Test 1G and 2.5G variants, autoneg and forced speeds, master/slave preferred/forced states, repeated soft resets, cable diagnostics, LED hw-control/brightness/blink/polarity conflicts, stats accumulation, suspend/resume, and SerDes FIFO reset on link transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca808x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca83xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca83xx.c

Purpose: Implements internal PHY support for QCA8337 and QCA8327 switch PHY variants. It applies switch-revision-specific analog and EEE workarounds, exposes a small ethtool statistic set, manages suspend/resume quirks, and toggles a DAC amplitude adjustment for QCA8327 at 100 Mbps.

Important APIs and functions: `qca83xx_driver[]` registers entries for QCA8337, QCA8327-A, and QCA8327-B. Key functions are `qca83xx_probe()`, `qca83xx_config_init()`, `qca8327_config_init()`, `qca83xx_link_change_notify()`, `qca83xx_suspend()`, `qca8337_suspend()`, `qca8327_suspend()`, `qca83xx_resume()`, and ethtool stats helpers `qca83xx_get_sset_count()`, `qca83xx_get_strings()`, and `qca83xx_get_stats()`.

Control flow: Probe allocates per-PHY statistic storage. Config init reads switch revision from `phydev->dev_flags`, applies revision-specific debug/MMD writes, and sets gigabit prefer-master. QCA8327 init first disables manual DAC amplitude control, then runs the common init. Link-change notification enables +6 percent DAC amplitude only while QCA8327 is running at 100 Mbps and clears it otherwise. Suspend clears selected green/hibernation debug bits; QCA8337 also invokes generic suspend, while QCA8327 avoids full PHY power-down and instead modifies BMCR to avoid unreliable ports. Resume reinitializes config, resets and restarts autoneg, polls reset completion, and delays briefly.

State and persistence: Per-device state is an accumulated `u64 stats[]` array. Revision information is passed through `dev_flags`. Hardware tweaks live in debug registers, MMD registers, and BMCR and are re-applied on init/resume. No persistent storage is used.

Dependencies and integration: Depends on phylib, shared AT803x debug register helpers, ethtool stats callbacks, switch driver-provided revision flags, and internal PHY IDs associated with qca8k switch hardware.

Risks and test signals: Risks include revision flag mismatch, undocumented analog/debug values, stat counters accumulating incorrectly when reads fail, QCA8327 suspend unreliability, and link-change DAC tuning not being cleared. Test all three PHY IDs, switch revisions 1/2/4, suspend/resume cycles, 100M and 1G link transitions, ethtool stats reads including MMD errors, and prefer-master negotiation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom-phy-lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom-phy-lib.c

Purpose: Provides shared helper functions for Qualcomm/Atheros PHY drivers. It centralizes debug register access, Wake-on-LAN setup, interrupt configuration and handling, speed/duplex/MDIX status decode, MDIX configuration, downshift tunables, cable diagnostic translation, LED force/hardware-control helpers, and common hardware statistic accumulation.

Important APIs and functions: Exported symbols include `at803x_debug_reg_read()`, `at803x_debug_reg_mask()`, `at803x_debug_reg_write()`, `at803x_set_wol()`, `at8031_set_wol()`, `at803x_get_wol()`, `at803x_ack_interrupt()`, `at803x_config_intr()`, `at803x_handle_interrupt()`, `at803x_read_specific_status()`, `at803x_config_mdix()`, `at803x_prepare_config_aneg()`, `at803x_read_status()`, `at803x_get_tunable()`, `at803x_set_tunable()`, `at803x_cdt_*()`, `qca808x_cable_test_get_status()`, LED helpers, and `qcom_phy_*stats()` helpers.

Control flow: Debug register access writes an address selector then reads or writes data. WoL programs the attached netdev MAC address into MMD registers, toggles WoL interrupt bits, clears latched status, and retriggers the state machine if other enabled interrupts were pending. Interrupt handling reads status and enable masks, filters unrelated interrupts, and calls `phy_trigger_machine()`. Status reads update link, skip redundant reads when autoneg link remains up, read LPA, decode speed/duplex/MDIX from vendor-specific status/function registers, and resolve pause. Downshift changes Smart Speed bits and reinitializes hardware after changes. Cable-test helpers start CDT, poll completion, translate pair codes to ethtool results, and report fault lengths. Stats helpers configure read-clear CRC counters and accumulate 32-bit/16-bit hardware counters into software 64-bit fields.

State and persistence: Shared state lives in caller-owned `phydev` registers and `struct qcom_phy_hw_stats`. WoL depends on the attached netdev MAC address. Counter state is software accumulated because hardware counters clear on read. No private global state is maintained.

Dependencies and integration: Depends on phylib, MDIO/MMD helpers, netdevice address validation, ethtool WoL/tunable/cable-test/LED/stat APIs, `qcom.h` register definitions, and exported-symbol linkage selected through `QCOM_NET_PHYLIB`.

Risks and test signals: Risks include non-atomic debug register address/data access on shared buses, interrupt status bits that require specific read ordering, WoL with invalid or missing netdev addresses, MDIX changes requiring soft reset, cable-test result misclassification, fault-length scaling, and read-clear counter loss if multiple readers race. Test interrupt enable/disable and IRQ filtering, WoL enable/disable with suspend paths, downshift get/set/default/disable, MDIX modes, status decode for AT803x and QCA808x masks, cable tests with open/short/cross-short/normal results, LED brightness/blink/hw-control transitions, and stats accumulation across repeated reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom-phy-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom.h

Purpose: Defines shared Qualcomm/Atheros PHY register constants, bit fields, cable-test encodings, LED encodings, hardware-stat structures, status-mask structures, and helper prototypes consumed by the qcom PHY drivers and `qcom-phy-lib.c`.

Important APIs and types: Important definitions cover AT803x specific function/status registers, interrupt masks, Smart Speed downshift fields, AT803x and QCA808x cable diagnostic fields, QCA808x LED global/pattern/force fields, WoL MAC address and control registers, debug address/data registers, RGMII delay and hibernation bits, QCA808x counter registers, `enum stat_access_type`, `struct at803x_hw_stat`, `struct at803x_ss_mask`, and `struct qcom_phy_hw_stats`. Function prototypes expose debug register operations, WoL, interrupts, status decode, MDIX/autoneg preparation, tunables, CDT helpers, LED helpers, and stats helpers.

Control flow: This header has no executable control flow, but it defines the register contract that controls runtime behavior in the C files. Bitfield macros using `GENMASK`, `BIT`, and `FIELD_PREP_CONST` keep status/result decoding aligned with hardware layouts.

State and persistence: No runtime state. Struct definitions specify caller-owned software state for stat accumulation and speed-mask decoding.

Dependencies and integration: Depends on Linux bitfield macros and phylib types through including C files. It is included by `at803x.c`, `qca807x.c`, `qca808x.c`, `qca83xx.c`, and `qcom-phy-lib.c`, making it the local ABI for shared helper symbols.

Risks and test signals: Risks are incorrect bit masks, mismatched QCA808x cable code composition, undocumented LED force semantics, and prototype drift with exported helper implementations. Test by building all Qualcomm drivers together and independently, validating cable diagnostics and LED behavior against hardware, checking downshift/status decode fields for each chip family, and running sparse/compile checks for prototype mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qsemi.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qsemi.c

Purpose: Provides a legacy phylib driver for the Quality Semiconductor QS6612 PHY used on RPX CLLF hardware. It performs a required de-isolation/init write and supports PHY interrupt masking, acknowledgement, and handling.

Important APIs and functions: The `qs6612_driver[]` entry matches PHY ID `0x00181440` with mask `0xfffffff0` and supplies `qs6612_config_init()`, `qs6612_config_intr()`, and `qs6612_handle_interrupt()`. `qs6612_ack_interrupt()` performs the documented multi-register read sequence needed to clear latched interrupt sources.

Control flow: Config init writes `0x0dc0` to the 100BaseTx PHY control register to allow operation on boards where the PHY powers up isolated. Interrupt enable first acknowledges any stale interrupt, then writes `MII_QS6612_IMR_INIT` to the interrupt mask register. Interrupt disable clears the mask and acknowledges leftovers. The IRQ handler reads the interrupt source register, ignores unrelated sources, acknowledges active sources because the register is not self-clearing, and triggers the phylib state machine.

State and persistence: No driver-private state exists. Hardware state consists of QS6612 mode/control/interrupt registers. Interrupt status bits are latched in hardware and cleared by ordered reads of ISR, BMSR, and EXPANSION.

Dependencies and integration: Depends on phylib, MII register definitions, module PHY registration, and the MDIO device table for autoloading. The file includes older networking and architecture headers, but runtime integration is through standard `struct phy_driver` callbacks.

Risks and test signals: Risks include reliance on preliminary register values, wrong interrupt clear ordering, interrupt storms if ISR bits are left latched, and sparse hardware availability. Test probe by MDIO ID, config-init de-isolation, interrupt enable/disable, IRQ handling for masked and unmasked sources, and fallback polling behavior when interrupts are not enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qsemi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qt2025.rs -->
# sources/distributed-fs/ceph-client/drivers/net/phy/qt2025.rs

Purpose: Implements a Rust phylib driver for the AMCC QT2025 10G SFP+ PHY. The driver performs hardware revision validation, initializes the integrated 8051 micro-controller, uploads firmware into MDIO-addressable SRAM, starts the controller from SRAM, and delegates link status to generic Clause 45 PHY status reading.

Important APIs and functions: The driver is registered with `kernel::module_phy_driver!` as `qt2025_phy`, advertises firmware `qt2025-2.0.3.3.fw`, and implements `kernel::net::phy::Driver` for `PhyQT2025`. Important methods are `probe()` and `read_status()`. It uses Rust kernel abstractions for firmware loading, C45 register addressing through `C45::new(Mmd, reg)`, and polling with `read_poll_timeout()`.

Control flow: Probe reads PMA/PMD register `0xd001` and rejects hardware revisions other than `0xb3`. It holds the micro-controller in reset, programs clock, mode, PCS seed/test registers, transmit/recovered clock configuration, releases reset for ROM execution, and requests firmware. Firmware larger than 24 KiB is rejected. Bytes 0..16 KiB are written to PCS registers starting at `0x8000`; bytes after 16 KiB are written to PHYXS registers starting at `0x8000`. The boot source is switched to SRAM, then PCS register `0xd7fd` is polled until it leaves boot states `0x00` and `0x10` or times out. Status reads call `genphy_read_status::<C45>()`.

State and persistence: No private Rust state is stored. Persistent runtime effects are hardware register programming and uploaded firmware in PHY SRAM, which must be redone after reset or reprobe. The firmware blob is external and requested by name.

Dependencies and integration: Depends on Rust-for-Linux kernel bindings, phylib Rust traits, firmware loader support, C45 MDIO access, kernel time/poll helpers, and availability of `qt2025-2.0.3.3.fw`. It integrates with phylib through the Rust module PHY driver macro and MDIO device table.

Risks and test signals: Risks include firmware absence, wrong hardware revision, MDIO write failures during byte-by-byte upload, firmware size overflow, poll timeout, and using standardized PCS test-pattern registers for vendor-specific purposes. Test with matching and nonmatching revisions, missing/oversized firmware, interrupted MDIO writes, successful firmware boot, reprobe after reset, and link status reporting through generic C45 status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/qt2025.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Kconfig

Purpose: Defines Realtek PHY driver build options, including optional hardware-monitoring support for temperature sensors on supported RTL822x devices.

Important options: `REALTEK_PHY` is the main tristate for RTL821x/RTL822x and fast Ethernet PHY support and selects `PHY_PACKAGE`. `REALTEK_PHY_HWMON` is a bool nested under `REALTEK_PHY`, depends on `HWMON`, and prevents the illegal combination where the Realtek driver is built in while hwmon is modular.

Control flow: This file has build-time control only. The nested `if REALTEK_PHY` makes the hwmon option available only when the Realtek driver is enabled.

State and persistence: State is Kconfig selection state only. The hwmon bool determines whether `realtek_hwmon.o` is included in the composite Realtek object.

Dependencies and integration: Integrates with the Realtek Makefile, phylib package support, and the hwmon subsystem. The dependency `!(REALTEK_PHY=y && HWMON=m)` protects built-in code from depending on modular hwmon symbols.

Risks and test signals: Risks are dependency drift with hwmon or package APIs and missed build combinations. Test `REALTEK_PHY` as disabled, module, and built-in; test hwmon enabled/disabled; and verify the forbidden built-in/module mix is rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Makefile

Purpose: Builds the Realtek PHY driver as a composite kbuild object with optional hwmon support.

Important entries: `realtek-y += realtek_main.o` always includes the main driver when `REALTEK_PHY` is enabled. `realtek-$(CONFIG_REALTEK_PHY_HWMON) += realtek_hwmon.o` conditionally includes temperature sensor support. `obj-$(CONFIG_REALTEK_PHY) += realtek.o` exposes the final built-in or module object.

Control flow: kbuild combines the listed objects into `realtek.o` according to Kconfig values. Runtime behavior is determined by which object files are linked.

State and persistence: No runtime state. This file persists build composition metadata.

Dependencies and integration: Integrates with `realtek/Kconfig`, `realtek_main.c`, and `realtek_hwmon.c`. Optional hwmon code is linked into the same driver object rather than a separate module.

Risks and test signals: Risks are object name drift, optional hwmon code not being linked when enabled, or unresolved `rtl822x_hwmon_init()` calls if Kconfig/Makefile diverge. Test Realtek built-in and module builds with hwmon on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek.h

Purpose: Provides the local Realtek PHY driver header used to share the hwmon initialization prototype with the main driver.

Important APIs and types: Includes `<linux/phy.h>` and declares `int rtl822x_hwmon_init(struct phy_device *phydev);`. Header guards prevent duplicate inclusion.

Control flow: No executable control flow.

State and persistence: No state is defined. The declaration allows caller-owned `struct phy_device` state to be passed into the hwmon registration helper.

Dependencies and integration: Integrates `realtek_main.c` with `realtek_hwmon.c` when `CONFIG_REALTEK_PHY_HWMON` links the optional object. It depends on phylib type definitions.

Risks and test signals: Risks are prototype drift and missing stubs if the main driver calls the function while hwmon support is not linked. Test all Realtek hwmon build combinations and compile checks for the shared prototype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_hwmon.c

Purpose: Adds optional hwmon temperature sensor support for Realtek RTL822x PHYs. It exposes current temperature and configured maximum temperature through a devm-registered hwmon device and clears the over-temperature alarm during initialization.

Important APIs and functions: `rtl822x_hwmon_init()` is the exported local initializer declared in `realtek.h`. Internal helpers include `rtl822x_hwmon_get_temp()` for signed 10-bit half-degree conversion and `rtl822x_hwmon_read()` for `hwmon_temp_input` and `hwmon_temp_max`. Static `hwmon_ops`, channel info, and chip info describe a read-only temperature channel.

Control flow: Init clears alarm bits in vendor MMD2 register `RTL822X_VND2_TSALRM`, then registers a hwmon device with `phydev` as driver data. Reads fetch raw sensor data from `RTL822X_VND2_TSRR` for input or `RTL822X_VND2_TSSR` shifted by six for maximum threshold, convert from signed 10-bit units at 0.5 degrees C to millidegrees C, and return `-EINVAL` for unsupported attributes.

State and persistence: No private state is allocated. The hwmon device is devm-managed under the PHY MDIO device. Hardware temperature/alarm/threshold state persists in vendor MMD registers; software exposes it read-only.

Dependencies and integration: Depends on the hwmon subsystem, phylib MMD accessors, Realtek main driver calling `rtl822x_hwmon_init()`, and Kconfig preventing impossible built-in/module dependencies.

Risks and test signals: Risks include ignoring negative MDIO read errors because raw reads are masked or shifted directly, signed conversion mistakes around bit 9, and stale threshold/alarm semantics across chip variants. Test hwmon registration, temp input and max reads for positive and negative raw values, MDIO read-error handling, alarm clear on init, and build/runtime behavior with hwmon disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_hwmon.c -->
