# subset-b-004687 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/phy/Kconfig

## Purpose
Defines the PHY-layer Kconfig surface for phylib, phylink, SFP support, fixed PHY emulation, optional LED integration, Rust PHY abstractions, and individual Ethernet PHY drivers. The selected symbols determine which driver objects in this directory and its subdirectories are built and which helper infrastructure is available to MAC drivers and PHY drivers.

## Important APIs, Types, and Functions
This is declarative Kconfig rather than executable code. Important symbols include `PHYLINK`, `PHYLIB`, `SWPHY`, `PHY_PACKAGE`, `LED_TRIGGER_PHY`, `PHYLIB_LEDS`, `FIXED_PHY`, `RUST_PHYLIB_ABSTRACTIONS`, and `SFP`. Driver symbols in this work item include `AS21XXX_PHY`, `AIR_EN8811H_PHY`, `AMD_PHY`, `ADIN_PHY`, `ADIN1100_PHY`, `AQUANTIA_PHY` from the sourced Aquantia Kconfig, `AX88796B_PHY`, `AX88796B_RUST_PHY`, `BCM_CYGNUS_PHY`, `BCM_NET_PHYLIB`, and `BCM_NET_PHYPTP`.

## Control Flow and State
Runtime behavior is determined indirectly through dependency and select relationships. `PHYLINK` selects `PHYLIB` and `SWPHY`; `SFP` depends on I2C, PHYLINK, and compatible HWMON settings; `PHYLIB_LEDS` is enabled by OF when LED class support is compatible; Rust PHY support requires `RUST` and built-in `PHYLIB`. Individual driver symbols gate module/built-in compilation and helper library availability. There is no persistent runtime state in this file.

## Dependencies and Integration Points
The file integrates with the directory Makefile, kernel configuration front ends, and external subsystem symbols such as `LEDS_TRIGGERS`, `LEDS_CLASS`, `I2C`, `HWMON`, `RUST`, `PTP_1588_CLOCK_OPTIONAL`, `NETWORK_PHY_TIMESTAMPING`, `MACSEC`, SoC architecture symbols, and MDIO bus drivers. It sources vendor submenus for Aquantia, MediaTek, Qualcomm, and Realtek drivers.

## Risks and Test Signals
Risks are build-graph regressions: missing selects for helper libraries, impossible dependencies, Rust driver visibility when C fallback is expected, or enabling drivers without required MDIO/PTP/HWMON infrastructure. Test signals are `allmodconfig`, `allyesconfig`, `randconfig`, no-Rust and Rust-enabled builds, plus checking that each selected symbol results in the expected object from `drivers/net/phy/Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/Makefile

## Purpose
Maps PHY-layer Kconfig symbols to built objects. It builds the phylib core, phylink, MDIO helpers, SFP support, timestamping support, vendor PHY drivers, and subdirectories.

## Important APIs, Types, and Functions
The main aggregates are `libphy-y`, which contains core phylib objects such as `phy.o`, `phy-c45.o`, `phy-core.o`, `phy_device.o`, `linkmode.o`, `phy_link_topology.o`, `phy_caps.o`, `mdio_bus_provider.o`, `phy_port.o`, and `mdio_device.o`, and symbol-gated `obj-$(CONFIG_...)` lines for each driver. For this subset, relevant mappings include `adin.o`, `adin1100.o`, `air_en8811h.o`, `amd.o`, `aquantia/`, `as21xxx.o`, `ax88796b.o` or `ax88796b_rust.o`, `bcm-cygnus.o`, `bcm-phy-lib.o`, and `bcm-phy-ptp.o`.

## Control Flow and State
There is no runtime control flow. Build-time flow is conditional: `stubs.o` is forced into `obj-y` whenever `CONFIG_PHYLIB` is set so built-in consumers can link; SFP bus support is collected through `sfp-obj-*`; `CONFIG_AX88796B_RUST_PHY` switches the AX88796B implementation from C to Rust while keeping the same `CONFIG_AX88796B_PHY` driver selection.

## Dependencies and Integration Points
This file is consumed by Kbuild and depends on the Kconfig symbols defined in this directory and vendor subdirectories. It ties the top-level PHY subsystem to subdirectories such as `aquantia/`, `mediatek/`, `mscc/`, `qcom/`, and `realtek/`, and to optional modules for PTP, HWMON-backed drivers, Rust drivers, and MACSEC-enabled objects.

## Risks and Test Signals
Risks are stale Kconfig/object names, duplicate or missing objects, unexpected built-in/module linkage, and the Rust/C AX88796B switch diverging from user expectation. Test signals include building each relevant symbol as `y` and `m`, checking module names with `modinfo`, and ensuring that `CONFIG_AX88796B_RUST_PHY=y` produces `ax88796b_rust.o` instead of the C object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/adin.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/adin.c

## Purpose
Implements the Analog Devices ADIN1200 and ADIN1300 industrial Ethernet PHY driver. It handles interface-mode setup, RGMII/RMII board properties, downshift, EDPD, fast link-down, clock output, MDI/MDIX control, interrupts, statistics, Clause 45-over-Clause 22 access, soft reset, and ethtool cable diagnostics.

## Important APIs, Types, and Functions
The driver registers two `struct phy_driver` entries matching `PHY_ID_ADIN1200` and `PHY_ID_ADIN1300`. Important private types are `adin_cfg_reg_map`, `adin_clause45_mmd_map`, `adin_hw_stat`, and `adin_priv`. Key functions include `adin_config_init`, `adin_config_rgmii_mode`, `adin_config_rmii_mode`, `adin_config_clk_out`, `adin_config_zptm100`, `adin_config_aneg`, `adin_read_status`, `adin_soft_reset`, `adin_get_tunable`, `adin_set_tunable`, `adin_read_mmd`, `adin_write_mmd`, `adin_phy_config_intr`, `adin_phy_handle_interrupt`, and the cable-test pair `adin_cable_test_start` and `adin_cable_test_get_status`.

## Control Flow and State
Probe allocates `adin_priv` to accumulate ethtool counters. `config_init` sets `mdix_ctrl` to auto, programs RGMII or RMII according to `phydev->interface`, enables default downshift and EDPD, configures optional clock output, and applies the low common-mode impedance property. Autoneg setup clears diagnostic clock mode, enables linking, applies requested MDI/MDIX mode, then delegates to `genphy_config_aneg`. Status reads update MDI/MDIX from control/status registers before `genphy_read_status`. Cable test disables normal linking, starts cable diagnostics in vendor MMD registers, polls for completion, then reports pair result and fault length through ethtool netlink.

## Dependencies and Integration Points
Depends on phylib Clause 22 access, vendor MMD access, generic PHY helpers, ethtool tunables and cable-test reporting, device properties such as `adi,rx-internal-delay-ps`, `adi,tx-internal-delay-ps`, `adi,fifo-depth-bits`, `adi,phy-output-clock`, `adi,phy-output-reference-clock`, and `adi,low-cmode-impedance`. It exposes MDIO device table entries for module autoloading.

## Risks and Test Signals
Risks include unsupported board-property values silently falling back to defaults, wrong RGMII delay or RMII FIFO depth, Clause 45 translation gaps returning `-EINVAL`, counter accumulation double-counting if hardware counters are not clear-on-read as assumed, and cable diagnostics leaving normal link state disabled on error. Test signals include RGMII/RMII mode bring-up, ethtool tunable get/set, interrupt-driven link changes, `ethtool --cable-test`, suspend/resume, and MMD EEE register access through the custom read/write callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/adin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/adin1100.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/adin1100.c

## Purpose
Implements the Analog Devices ADIN1100-family 10BASE-T1L PHY driver, covering ADIN1100, ADIN1110, and ADIN2111 IDs. It supports Clause 45 operation, 10BASE-T1L transmit-level configuration, forced/autoneg modes, master/slave status, powerdown, loopback, interrupts, soft reset, and signal quality indication.

## Important APIs, Types, and Functions
The main private type is `adin_priv`, which records whether 2.4 V transmit level is supported, requested, and explicitly configured. Important functions include `adin_get_features`, `adin_config_aneg`, `adin_read_status`, `adin_config_intr`, `adin_phy_handle_interrupt`, `adin_set_powerdown_mode`, `adin_suspend`, `adin_resume`, `adin_set_loopback`, `adin_soft_reset`, `adin_get_sqi`, and `adin_get_sqi_max`.

## Control Flow and State
Probe allocates `adin_priv`. Feature discovery reads `MDIO_PMA_10T1L_STAT`, records 2.4 V capability, reads optional `phy-10base-t1l-2.4vpp`, sets basic port bits, and delegates to `genphy_c45_pma_read_abilities`. Forced mode uses `genphy_c45_pma_setup_forced`, programs the 2.4 V PMA bit based on policy, then sets `ADIN_FORCED_MODE_EN`. Autoneg mode clears forced mode, optionally advertises/request high transmit level, disables high-level advertisement when configured off or unsupported, and calls `genphy_c45_config_aneg`. Status delegates to generic C45 status and then maps vendor master/slave instance bits into `phydev->master_slave_state`.

## Dependencies and Integration Points
Depends on Clause 45 phylib helpers, 10BASE-T1L MDIO definitions, device property APIs, phylib SQI hooks, interrupt callbacks, and PMA/AN/PCS MMD registers. It integrates with ethtool through SQI, loopback, and master/slave state exposed by phylib.

## Risks and Test Signals
Risks include misinterpreting 2.4 V capability versus explicit board policy, forced mode leaving stale autoneg advertisement, powerdown polling timeouts, and `adin_get_sqi` using the wrong MMD constant when reading MSE. Test signals include autoneg and forced 10BASE-T1L links, master/slave reporting, suspend/resume powerdown readiness, loopback enable/disable, link interrupt delivery, and SQI values from 0 to 7 on real links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/adin1100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/air_en8811h.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/air_en8811h.c

## Purpose
Implements Airoha EN8811H and AN8811HB 2.5G PHY support. The driver loads required MD32 firmware, accesses internal PBUS registers through an MDIO page window, configures SerDes polarity, exposes hardware LED controls, registers optional clock outputs, handles rate matching, and decodes link status.

## Important APIs, Types, and Functions
The private state `en8811h_priv` stores firmware version, MCU restart state, three LED states/rules, a `clk_hw`, associated `phy_device`, and saved clock-output state. Important functions include PBUS helpers `air_buckpbus_reg_read`, `air_buckpbus_reg_write`, `air_buckpbus_reg_modify`, firmware loaders `en8811h_load_firmware` and `an8811hb_load_firmware`, `en8811h_wait_mcu_ready`, CRC helper `an8811hb_check_crc`, probe functions for both chips, config-init functions for both chips, LED callbacks `air_led_blink_set`, `air_led_brightness_set`, `air_led_hw_control_set/get`, clock ops for both variants, `en8811h_config_aneg`, `en8811h_read_status`, `en8811h_clear_intr`, and `en8811h_handle_interrupt`.

## Control Flow and State
Probe allocates private state, loads firmware from chip-specific files, marks required MMDs present because MDIO_DEVS registers are empty, initializes default LED rules, registers a clock provider when common clock support is enabled, and configures LED GPIO pins as outputs. Config-init restarts the MCU on later invocations, programs EN8811H mode 1 for 2500Base-X rate adaptation, applies SerDes polarity from generic or legacy properties, and enables user-defined LED mode. AN8811HB uses separate polarity registers and firmware CRC checks. Link status uses generic link update and AN reads, adds 2.5G LP ability from standard or vendor registers, resolves pause, reads actual speed from `AIR_AUX_CTRL_STATUS`, forces full duplex, and sets `RATE_MATCH_PAUSE`.

## Dependencies and Integration Points
Depends on firmware files declared with `MODULE_FIRMWARE`, phylib C45 helpers, page-select support, LED netdev trigger APIs, PHY common polarity properties, common clock framework, device properties, unaligned little-endian firmware writes, and MDIO vendor MMD/PBUS register access. The driver integrates with MACs through rate matching and 2500Base-X/SerDes configuration.

## Risks and Test Signals
Risks include missing firmware causing probe failure, MDIO page restore bugs around PBUS access, long MCU-ready polling, firmware-version conditionals for 2.5G LP ability, divergent EN8811H versus AN8811HB polarity semantics, LED state/rules drifting after manual brightness/blink operations, and global `clk_save_context`/`clk_restore_context` affecting unrelated clocks. Test signals include firmware load logs and version reads, 10/100/1000/2500 full-duplex links, autoneg-disabled rejection, link interrupts, LED hardware-control triggers, clock-output enable/rate tests, suspend/resume, and polarity property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/air_en8811h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/amd.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/amd.c

## Purpose
Provides a small PHY driver for AMD AM79C874 and Altima AC101L PHYs, mainly to handle their interrupt status/control register.

## Important APIs, Types, and Functions
The driver registers two `struct phy_driver` entries with IDs `PHY_ID_AM79C874` and `PHY_ID_AC101L`. Important functions are `am79c_ack_interrupt`, `am79c_config_init`, `am79c_config_intr`, and `am79c_handle_interrupt`.

## Control Flow and State
Initialization is a no-op. Interrupt enable first acknowledges pending BMSR and vendor interrupt status, then writes link and autoneg-complete enables into register 17. Interrupt disable masks the register then acknowledges pending status. The ISR reads register 17 and triggers the PHY state machine only when link-down or autoneg-done status bits are present.

## Dependencies and Integration Points
Depends on basic Clause 22 phylib reads/writes, `MII_BMSR`, IRQ callbacks in `struct phy_driver`, and MDIO module matching. Generic phylib handles the actual link configuration and status behavior.

## Risks and Test Signals
Risks are limited but include wrong interrupt-mask polarity, losing an interrupt if BMSR/status read order is changed, and no special handling for chip errata outside interrupts. Test signals are compile coverage, probe/autoload by MDIO ID, interrupt-driven link-down and autoneg-complete events, and fallback polling behavior when interrupts are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Kconfig

## Purpose
Defines the Aquantia PHY driver build option under the PHY driver menu.

## Important APIs, Types, and Functions
The `AQUANTIA_PHY` tristate symbol enables support for Aquantia AQ1202, AQ2104, AQR105, and AQR405-class devices and selects `CRC_ITU_T`, which is needed by the firmware loader for image and mailbox CRC validation.

## Control Flow and State
There is no runtime control flow. Build-time state is whether the Aquantia driver is disabled, built in, or built as a module. Selecting `CRC_ITU_T` ensures the helper is linked whenever the driver can call `crc_itu_t`.

## Dependencies and Integration Points
The symbol is sourced by the parent PHY Kconfig and consumed by `aquantia/Makefile`, which builds the multi-object `aquantia.o` module.

## Risks and Test Signals
Risks are missing helper selects or stale help text that under-represents the many newer AQR devices supported by `aquantia_main.c`. Test signals include `CONFIG_AQUANTIA_PHY=m/y` builds and confirming `CRC_ITU_T` is available for firmware-loading builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Makefile

## Purpose
Defines how the Aquantia PHY driver is linked from its submodules.

## Important APIs, Types, and Functions
`aquantia-objs` always includes `aquantia_main.o`, `aquantia_firmware.o`, and `aquantia_leds.o`. When `CONFIG_HWMON` is set, it also includes `aquantia_hwmon.o`. `obj-$(CONFIG_AQUANTIA_PHY)` emits the final `aquantia.o` object.

## Control Flow and State
Build-time composition is conditional on HWMON. Runtime behavior in `aquantia.h` stubs out `aqr_hwmon_probe` when HWMON is not reachable, while this Makefile ensures the implementation is linked only when needed.

## Dependencies and Integration Points
Depends on the parent `CONFIG_AQUANTIA_PHY` symbol and optional `CONFIG_HWMON`. Integrates the firmware, LED, HWMON, and main driver modules into one PHY driver.

## Risks and Test Signals
Risks include mismatched stubs and object composition, unresolved HWMON symbols, or missing LED/firmware objects from the aggregate. Test signals are Aquantia builds with HWMON enabled and disabled, plus module symbol checks for `aqr_firmware_load`, LED callbacks, and `aqr_hwmon_probe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia.h

## Purpose
Provides shared register definitions, data structures, firmware fingerprint helpers, SGMII statistics descriptors, private state, and cross-module prototypes for the Aquantia PHY driver.

## Important APIs, Types, and Functions
Important register groups include VEND1 global control/reset, mailbox interfaces, firmware ID, per-speed global configuration, LED provisioning/drive registers, thermal registers, interrupt masks/status, reserved firmware status, and C22EXT SGMII stats. Key types are `aqr107_hw_stat`, `aqr_global_syscfg`, `enum aqr_rate_adaptation`, and `struct aqr107_priv`. The header declares `aqr_hwmon_probe`, `aqr_firmware_load`, Aquantia LED callbacks, `aqr_phy_led_active_low_set`, `aqr_phy_led_polarity_set`, and `aqr_wait_reset_complete`.

## Control Flow and State
The header has no direct runtime flow except the HWMON stub selected by `IS_REACHABLE(CONFIG_HWMON)`. It defines persistent driver state: accumulated SGMII stats, a 64-bit firmware fingerprint, saved LED polarity bitmaps, a global-configuration readiness flag, and per-speed host-interface/rate-adaptation mappings.

## Dependencies and Integration Points
Includes `linux/device.h` and `linux/phy.h` and is shared by `aquantia_main.c`, `aquantia_firmware.c`, `aquantia_hwmon.c`, and `aquantia_leds.c`. It encodes hardware ABI fields used by phylib, ethtool stats, LED class integration, HWMON, firmware loading, and interface-mode selection.

## Risks and Test Signals
Risks are incorrect masks or register addresses affecting multiple modules, HWMON stub divergence, firmware fingerprint mistakes changing interface translation, and private state layout assumptions across modules. Test signals include compile coverage with and without HWMON, LED polarity persistence after reset, SGMII stat reads, firmware fingerprint logs, and register dumps against datasheet values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_firmware.c

## Purpose
Loads Aquantia firmware into PHY DRAM and IRAM when no firmware is already running. Firmware can come from an NVMEM cell or from a filesystem firmware file named by device property.

## Important APIs, Types, and Functions
Important helpers include `aqr_fw_validate_get`, endian-safe readers `aqr_fw_get_be16`, `aqr_fw_get_le16`, `aqr_fw_get_le24`, memory loader `aqr_fw_load_memory`, boot parser `aqr_fw_boot`, source-specific loaders `aqr_firmware_load_nvmem` and `aqr_firmware_load_fs`, and exported `aqr_firmware_load`. `struct aqr_fw_header` describes the packed offsets/sizes for IRAM and DRAM sections.

## Control Flow and State
`aqr_firmware_load` first calls `aqr_wait_reset_complete`; if firmware appears to be running, it returns without loading. On timeout, it tries the `firmware` NVMEM cell, allowing probe defer or success, then falls back to `firmware-name` and `request_firmware`. `aqr_fw_boot` validates the file CRC, primary offset, section header bounds, word alignment, DRAM/IRAM bounds, and version string. It stalls the embedded processor, writes DRAM and IRAM through mailbox registers with running CRC verification, clears reset/low-power state, pulses UP reset, and releases the processor.

## Dependencies and Integration Points
Depends on `crc_itu_t`, firmware loader APIs, NVMEM consumer APIs, unaligned access helpers, Aquantia mailbox register definitions from `aquantia.h`, and `aqr_wait_reset_complete` from the main module. Device tree or firmware-node data supplies `firmware-name` or an NVMEM cell named `firmware`.

## Risks and Test Signals
Risks include accepting malformed firmware, integer/bounds mistakes in section parsing, mailbox writes without error checking on every setup write, CRC mismatch from endianness assumptions, and assuming a timeout means no firmware is running. Test signals include booting with already-loaded firmware, NVMEM and filesystem firmware paths, invalid CRC and malformed offset tests, mailbox CRC mismatch injection, and confirmation that the PHY reports a firmware ID after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_hwmon.c

## Purpose
Adds HWMON temperature support for Aquantia PHYs, exposing current temperature, warning/failure thresholds, and alarm bits.

## Important APIs, Types, and Functions
Key callbacks are `aqr_hwmon_is_visible`, `aqr_hwmon_read`, `aqr_hwmon_write`, and exported `aqr_hwmon_probe`. Helpers include `aqr_hwmon_get`, `aqr_hwmon_set`, `aqr_hwmon_test_bit`, and `aqr_hwmon_status1`. The HWMON channel table exposes chip timezone registration and temperature attributes.

## Control Flow and State
Read operations verify the sensor type, optionally check the valid bit before reading current temperature, convert signed 16-bit 1/256 degree Celsius values to millidegrees, and return alarm bits from general status. Write operations range-check threshold values to signed 8-bit degree limits represented in millidegrees, convert to register units, and write vendor thermal provisioning registers. Probe sanitizes the MDIO device name to alphanumeric characters and registers a devm HWMON device.

## Dependencies and Integration Points
Depends on `CONFIG_HWMON`, phylib MMD reads/writes, HWMON core, thermal register definitions from `aquantia.h`, and `devm_hwmon_device_register_with_info`. It is called from `aqr107_probe` when HWMON is reachable.

## Risks and Test Signals
Risks include returning `-EBUSY` if the valid bit is not set, incorrect signed temperature conversion, threshold range rejection surprising users, and sanitized-name collisions. Test signals include `sensors` output, reading current temperature under valid/invalid conditions, writing min/max/critical thresholds, alarm-bit changes, and builds with HWMON disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_leds.c

## Purpose
Implements Aquantia PHY LED class callbacks for forced brightness, hardware netdev trigger rules, and active-low/active-high polarity control.

## Important APIs, Types, and Functions
Exports `aqr_phy_led_brightness_set`, `aqr_phy_led_hw_is_supported`, `aqr_phy_led_hw_control_get`, `aqr_phy_led_hw_control_set`, `aqr_phy_led_active_low_set`, and `aqr_phy_led_polarity_set`. It supports up to `AQR_MAX_LEDS` LEDs and netdev triggers for link, link speeds 100M through 10G, RX, and TX.

## Control Flow and State
Brightness writes clear link/activity hardware rules and optionally force the LED on. Hardware-control set maps requested trigger bits into `AQR_LED_PROV(index)` link and activity bits; get reverses that mapping from hardware. Polarity set validates requested PHY LED modes, records forced active-low/high choices in `aqr107_priv` so `aquantia_main.c` can restore them after reset, and writes the drive register through `aqr_phy_led_active_low_set`.

## Dependencies and Integration Points
Depends on phylib LED callbacks, Aquantia LED provisioning/drive registers from `aquantia.h`, and the `aqr107_priv` LED polarity bitmaps. Driver-table entries in `aquantia_main.c` expose these callbacks for supported AQR devices.

## Risks and Test Signals
Risks include unsupported trigger combinations being accepted in future without hardware support, brightness changes clearing hardware rules, polarity state only persisting when forced modes are set, and off-by-one LED index validation. Test signals include LED class brightness, hardware trigger set/get for each speed/activity bit, active-low/high mode persistence across soft reset, and invalid index/mode rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_main.c

## Purpose
Implements the main Aquantia PHY driver for many AQ/AQR devices. It handles feature discovery, autonegotiation, forced modes, interrupts, link/status decoding, interface and rate-matching discovery, firmware-load probe path, statistics, downshift tunables, suspend/resume, LED and HWMON integration, and in-band host-interface configuration.

## Important APIs, Types, and Functions
The driver table matches AQ1202, AQ2104, AQR105, AQR106, AQR107, AQCS109, AQR405, AQR111/B0, AQR112, AQR412/C, AQR113/C, AQR114C, AQR115/C, and AQR813. Key functions include `aqr107_probe`, `aqr_config_aneg`, `aqr105_config_aneg`, `aqr105_setup_forced`, `aqr_read_status`, `aqr_gen1_read_status`, `aqr_gen2_read_status`, `aqr_gen1_read_rate`, `aqr_translate_interface`, `aqr_wait_reset_complete`, `aqr_build_fingerprint`, `aqr_gen1_config_init`, `aqr_gen2_read_global_syscfg`, `aqr_gen2_fill_interface_modes`, `aqr_gen4_config_init`, `aqr107_get_tunable`, `aqr107_set_tunable`, `aqr107_get_stats`, `aqr107_link_change_notify`, `aqr_gen2_inband_caps`, and `aqr_gen2_config_inband`.

## Control Flow and State
Probe allocates `aqr107_priv`, loads firmware if needed, and registers HWMON. Gen1 config validates the requested host interface, waits for firmware readiness, builds a firmware fingerprint when available, sets default downshift, applies optional MDI pair order, and restores saved LED polarity. Gen2/gen4 config additionally reads per-speed global system configuration and possible interfaces, with gen4 polling global config registers and clearing PMA TX disable. Autoneg writes standard C45 advertisement plus vendor 1000/2500/5000 bits and MDIX mode. Status reads LP 1000Base-T bits, MDIX state, standard C45 status, vendor host-interface type, vendor line speed, and rate-matching mode from cached global config. In-band configuration toggles USXGMII AN or per-speed global config AN bits.

## Dependencies and Integration Points
Depends on phylib C45 helpers, ethtool stats/tunables, LED callbacks from `aquantia_leds.c`, firmware and HWMON helpers, device-tree property `marvell,mdi-cfg-order`, MDIO vendor MMDs, PMA/AN/PHYXS registers, and host MACs consuming `possible_interfaces`, `rate_matching`, and in-band capabilities.

## Risks and Test Signals
Risks include incorrect device-table callback selection across many variants, firmware fingerprint based 10G-QXGMII translation being too narrow, global config reads racing firmware readiness, stale cached rate adaptation after firmware changes, autoneg vendor bits diverging from standard linkmode state, and LED polarity restoration only after driver-managed resets. Test signals include link tests at 10M through 10G, forced AQR105 modes, USXGMII/10G-QXGMII/SGMII/2500BASE-X interface reporting, downshift tunables, interrupts, suspend/resume processor-intensive operation waits, ethtool SGMII stats, HWMON registration, LED callbacks, and in-band enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/as21xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/as21xxx.c

## Purpose
Implements Aeonsemi AS21xxx 10G/5G/2.5G Clause 45 PHY support. The driver handles pre-firmware generic ID matching, firmware loading, IPC command synchronization, status decoding through mapped Clause 22 registers, PTP clock enable, rate-adaptation configuration, and LED hardware controls.

## Important APIs, Types, and Functions
Important state is `struct as21xxx_priv`, which stores IPC parity and a mutex protecting IPC access. Firmware and IPC functions include `aeon_firmware_load`, `aeon_firmware_boot`, `aeon_ipc_send_cmd`, `aeon_ipc_send_msg`, `aeon_ipc_sync_parity`, `aeon_ipc_get_fw_version`, and `aeon_dpc_ra_enable`. PHY callbacks include `as21xxx_probe`, `as21xxx_match_phy_device`, `as21xxx_read_status`, `as21xxx_led_brightness_set`, `as21xxx_led_hw_is_supported`, `as21xxx_led_hw_control_get`, `as21xxx_led_hw_control_set`, and `as21xxx_led_polarity_set`.

## Control Flow and State
Before firmware is loaded, devices expose the generic `PHY_ID_AS21XXX`. The first driver entry uses `as21xxx_match_phy_device` to detect Aeonsemi vendor IDs, load firmware from the `firmware-name` property, synchronize IPC parity using two NOOP commands, and then return so the newly exposed exact PHY ID can match a real driver entry. Normal probe allocates private state, initializes the mutex, synchronizes IPC, logs firmware version, enables PTP clock, and enables DPC rate adaptation. Status reads link through mapped C22-in-C45 registers, avoids reporting link while BMCR autoneg restart is set, reads LPA including 1000Base-T status from mapped registers, resolves autoneg linkmode, or decodes forced speed from a vendor speed register.

## Dependencies and Integration Points
Depends on firmware loader APIs, Open Firmware `firmware-name`, Clause 45 phylib MMD access, mapped Clause 22 registers in the AN MMD, MDIO module matching, mutex protection for IPC, phylib LED callbacks, PTP-clock vendor bit, and ethtool netdev trigger definitions.

## Risks and Test Signals
Risks include firmware load in `match_phy_device` being unusual and order-sensitive, IPC parity desynchronization, firmware-reported return size overruns guarded but still hardware-dependent, unsupported firmware alignment, an apparent speed-switch mask typo using `VEND1_SPEED_STATUS` instead of `VEND1_SPEED_MASK`, and LED index checks using `>` instead of `>=` for `AEON_MAX_LEDS`. Test signals include cold-boot generic-ID probe, firmware load and exact-ID rematch, IPC firmware version log, autoneg and forced speed reporting, master/slave failure paths, LED trigger validation, PTP clock enable readback, and concurrent LED/status operations while IPC is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/as21xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b.c

## Purpose
Implements the C Asix PHY driver for AX88772A, AX88772C, and AX88796B devices. It mainly provides a reset workaround and an AX88772A link-partner advertisement workaround.

## Important APIs, Types, and Functions
The driver registers three `struct phy_driver` entries. Important functions are `asix_soft_reset`, `asix_ax88772a_read_status`, and `asix_ax88772a_link_change_notify`.

## Control Flow and State
`asix_soft_reset` writes zero to BMCR before `genphy_soft_reset` because these PHYs require the reset bit to toggle. AX88772A status update first checks link, seeds speed and duplex from BMCR as a fallback, then reads LPA and resolves autoneg only if autoneg is complete. Link-change notify reinitializes hardware and restarts autoneg when the PHY enters `PHY_NOLINK`, avoiding stale LPA data with certain partners.

## Dependencies and Integration Points
Depends on Clause 22 phylib, generic suspend/resume/reset helpers, PHY internal flag support, and MDIO device table matching. The Makefile can replace this C implementation with the Rust version when `CONFIG_AX88796B_RUST_PHY` is enabled.

## Risks and Test Signals
Risks include reset workarounds affecting other Asix models, restart-on-nolink causing unexpected renegotiation timing, and C/Rust implementation drift. Test signals include AX88772A links with older switches whose LPA reads as zero, soft reset on AX88796B hardware, suspend/resume on internal USB PHY variants, and build tests with the Rust switch disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b_rust.rs -->
# sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b_rust.rs

## Purpose
Provides a Rust reference implementation of the Asix PHY driver equivalent to `ax88796b.c`, using the Rust phylib abstractions.

## Important APIs, Types, and Functions
The module is registered by `kernel::module_phy_driver!` with `PhyAX88772A`, `PhyAX88772C`, and `PhyAX88796B`. It uses `kernel::net::phy::{Device, Driver, DeviceId}` and `reg::C22`. Important callbacks are `asix_soft_reset`, `PhyAX88772A::read_status`, `suspend`, `resume`, `soft_reset`, `link_change_notify`, and the simpler reset callbacks for AX88772C and AX88796B.

## Control Flow and State
The Rust reset helper writes `C22::BMCR` to zero then calls `genphy_soft_reset`, matching the C reset workaround. AX88772A status flow mirrors the C driver: update link, return if down, seed speed/duplex from BMCR, read LPA, and resolve autoneg if complete. Link-change notify ignores errors from `init_hw` and `start_aneg`, matching the best-effort C behavior. There is no private persistent state.

## Dependencies and Integration Points
Depends on `RUST_PHYLIB_ABSTRACTIONS`, the kernel Rust prelude, C UAPI constants, and the parent Makefile selecting this object when `CONFIG_AX88796B_RUST_PHY` is true. It exposes the same device IDs and module metadata shape through Rust macros.

## Risks and Test Signals
Risks include Rust abstraction behavior diverging from C phylib semantics, ignored errors in link-change notify hiding restart failures, and mismatched device-table/module names relative to the C implementation. Test signals include Rust-enabled kernel builds, module autoload for each device ID, behavior comparison against the C driver on AX88772A/AX88772C/AX88796B hardware, and reset/link renegotiation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b_rust.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-cygnus.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-cygnus.c

## Purpose
Implements Broadcom Cygnus and Omega internal PHY support, using the shared Broadcom PHY library for register access, interrupts, EEE, APD, downshift, stats, and AFE workarounds.

## Important APIs, Types, and Functions
Private state `bcm_omega_phy_priv` stores a statistics shadow array. Important functions are `bcm_cygnus_afe_config`, `bcm_cygnus_config_init`, `bcm_cygnus_resume`, `bcm_omega_config_init`, `bcm_omega_resume`, `bcm_omega_get_tunable`, `bcm_omega_set_tunable`, `bcm_omega_get_phy_stats`, and `bcm_omega_probe`.

## Control Flow and State
Cygnus config masks interrupts globally, configures the interrupt mask register to unmask link/speed/duplex events, applies several AFE calibration writes, advertises EEE, and enables APD. Resume repeats config-init and restarts autoneg. Omega config logs revision once, performs a dummy BMSR read to work around a first-MDIO-read issue, applies 28 nm A0/B0 AFE config for revision 0, reads downshift state, enables EEE only when downshift is disabled, and enables APD. Omega tunable writes update downshift, adjust EEE accordingly, and restart autoneg.

## Dependencies and Integration Points
Depends on `bcm-phy-lib.h`, Broadcom PHY register definitions in `linux/brcmphy.h`, generic phylib, ethtool tunables/stats, and Broadcom internal PHY IDs. Driver entries wire shared library callbacks for interrupts and stats.

## Risks and Test Signals
Risks include AFE magic values being revision-specific, interrupt mask polarity confusion, EEE and downshift interaction causing link failures, resume not preserving user tunables, and stats shadow allocation mismatches. Test signals include Cygnus/Omega hardware bring-up, interrupt-driven link/speed changes, resume link recovery, downshift tunable get/set, EEE advertisement with downshift enabled/disabled, and ethtool stats accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-cygnus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.c

## Purpose
Provides shared helper code for Broadcom PHY drivers. It abstracts Broadcom expansion, shadow, misc, and RDB register access; interrupt handling; APD and EEE control; downshift; statistics; AFE calibration; jumbo mode; cable diagnostics; Wake-on-LAN; LED brightness; and BroadR-Reach/LRE advertisement.

## Important APIs, Types, and Functions
Exported accessors include `bcm_phy_write_exp`, `bcm_phy_read_exp`, `bcm_phy_modify_exp`, `bcm54xx_auxctl_read/write`, `bcm_phy_write_misc/read_misc`, `bcm_phy_write_shadow/read_shadow`, and RDB read/write/modify helpers. Functional exports include `bcm_phy_ack_intr`, `bcm_phy_config_intr`, `bcm_phy_handle_interrupt`, `bcm_phy_enable_apd`, `bcm_phy_set_eee`, `bcm_phy_downshift_get/set`, `bcm_phy_get_sset_count`, `bcm_phy_get_strings`, `bcm_phy_get_stats`, `bcm_phy_update_stats_shadow`, `bcm_phy_r_rc_cal_reset`, `bcm_phy_28nm_a0b0_afe_config_init`, `bcm_phy_enable_jumbo`, cable-test helpers, `bcm_phy_set_wol`, `bcm_phy_get_wol`, `bcm_phy_wol_isr`, `bcm_phy_led_brightness_set`, `bcm_setup_lre_master_slave`, `bcm_config_lre_aneg`, and `bcm_config_lre_advert`.

## Control Flow and State
The access helpers select an indirect register window, optionally take the MDIO bus lock, read or write data, and often restore default selection. Interrupt config toggles the global ECR interrupt mask and acknowledges pending ISR. APD and EEE perform read-modify-write on shadow and C45 vendor registers, with EEE advertisement based on supported link modes. Downshift maps ethtool counts to Broadcom wirespeed bits and retry fields. Stats add clear/freeze-style hardware counters into caller-provided shadow storage. Cable tests force autoneg with no capabilities, optionally switch RDB devices to legacy access, start ECD, poll completion, report per-pair result and lengths, then restore RDB access. WOL programs pattern/mask registers and wake IRQ behavior. LRE helpers translate linkmode advertisements and master/slave settings to Broadcom registers.

## Dependencies and Integration Points
Depends on `linux/brcmphy.h` register definitions, phylib MDIO locking and MMD helpers, ethtool tunables/stats/netlink cable test/WOL data, netdevice MAC address helpers, and exported symbols consumed by Broadcom-specific PHY drivers such as Cygnus, Broadcom 54xx, 7xxx, 54140, and related modules.

## Risks and Test Signals
Risks include indirect-access helpers being called under the wrong lock variant, failure to restore RDB access after cable-test errors, APD/EEE policy surprises under forced mode, downshift range arithmetic around `DOWNSHIFT_DEV_DISABLE`, WOL pattern masking mistakes, stat accumulation over saturating counters, and shared magic AFE values impacting unrelated PHY revisions. Test signals include lockdep under nested MDIO operations, interrupt enable/disable and ISR delivery, APD wake, EEE advertisement reads, downshift ethtool tunables, cable-test result/length reporting with and without RDB, WOL magic/unicast/multicast/broadcast wake, LED brightness control, jumbo packet reception, and BroadR-Reach autoneg tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.h

## Purpose
Declares the shared Broadcom PHY helper interface and 28 nm misc register tuple macros consumed by Broadcom PHY drivers.

## Important APIs, Types, and Functions
Defines `MISC_ADDR` and AFE/PLL/DSP register tuples such as `DSP_TAP10`, `PLL_PLLCTRL_1`, `AFE_RXCONFIG_0`, and `AFE_TX_CONFIG`. Declares expansion, auxctl, misc, shadow, and RDB accessors; interrupt helpers; APD, EEE, downshift, stats, calibration, jumbo, cable-test, optional PTP, WOL, LED brightness, and LRE autoneg functions. Inline helpers `bcm_phy_write_exp_sel` and `bcm_phy_read_exp_sel` add the expansion select bit.

## Control Flow and State
This header has no runtime control flow except optional PTP stubs selected by `CONFIG_BCM_NET_PHYPTP`. It defines API contracts for callers to provide stats shadow storage and to choose locked or unlocked register access variants.

## Dependencies and Integration Points
Includes `linux/brcmphy.h`, `linux/phy.h`, and `linux/interrupt.h`, forward-declares `struct ethtool_wolinfo`, and is included by Broadcom PHY drivers that share common register sequences. The PTP section bridges to `bcm-phy-ptp` when enabled while allowing non-PTP builds to compile.

## Risks and Test Signals
Risks include prototype drift with `bcm-phy-lib.c`, incorrect use of unlocked `__bcm_*` helpers outside an MDIO bus lock, PTP stub mismatch, and tuple macro arguments being misread as single register constants. Test signals are all Broadcom PHY driver builds, PTP-enabled and disabled builds, sparse/prototype checks, and runtime tests that exercise each exported helper from at least one consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.h -->
