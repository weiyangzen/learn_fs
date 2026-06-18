# subset-b-005875 Research

Grouped research for Linux MFD-related headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each section preserves the original source path and is bounded for deterministic split into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/as3711.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/as3711.h

Purpose: This header is the shared contract for the AMS AS3711 PMIC MFD driver and its regulator/backlight child drivers. It defines the AS3711 register addresses, regulator IDs, parent device state, and board/platform configuration used by non-DT or board-specific integrations.

Important APIs, types, and constants: The register map covers voltage registers for four step-down regulators and eight LDOs, step-down control, GPIO signal registers, current-sink controls, step-up/backlight controls, regulator/charger status, interrupt status banks, and ASIC ID registers. `AS3711_MAX_REG`, `AS3711_NUM_REGS`, and the regulator enum establish the regmap bounds and regulator descriptor indexes. `struct as3711` carries the parent `device` and `regmap`. Platform data is split into `struct as3711_regulator_pdata`, `struct as3711_bl_pdata`, and `struct as3711_platform_data`, with step-up/backlight feedback enums describing SU2 voltage/current feedback routing.

Control flow: The header contains no executable control flow. Runtime flow is parent MFD probe creating a regmap, child drivers using these register constants and IDs, and optional platform data steering regulator initialization and backlight feedback/current settings.

State and persistence: Persistent state is hardware register state in the PMIC. Kernel state is limited to the `as3711` regmap pointer and platform data passed during device creation; no file or disk persistence exists.

Dependencies and integration points: It depends on regulator platform data types by pointer, forward-declares `device` and `regmap`, and integrates with regulator and backlight subdrivers through shared IDs and register addresses.

Risks: Incorrect regulator ID ordering can bind child regulator descriptors to the wrong rails. SU2 feedback and current limits are board-sensitive and can damage or misconfigure backlight hardware if wrong. Register constants are sparse and direct, so datasheet drift must be handled carefully.

Test signals: Build coverage from AS3711 MFD/regulator/backlight drivers, probe logs showing ASIC ID reads, regulator registration count matching `AS3711_REGULATOR_MAX`, and hardware tests for voltage programming, GPIO status, interrupts, and backlight current modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/as3711.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/as3722.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/as3722.h

Purpose: This header defines the public AS3722 PMIC register, bitfield, IRQ, and helper interface used by the AS3722 MFD core and child drivers such as regulators, GPIO, RTC, ADC, watchdog, and power management.

Important APIs, types, and constants: The register constants cover step-down and LDO voltage/control registers, GPIO controls and signal registers, startup/reset/watchdog/standby registers, PWM, RTC, ADC, interrupt mask/status banks, ASIC ID, lock, and fuse registers. Bit masks define regulator voltage selectors, regulator enable bits, LDO3 operating modes, step-down fast-mode bits, power-off, interrupt sources, ADC conversion controls, GPIO modes/functions, RTC wake enables, watchdog controls, external enable controls, and fuse interpretation. `enum as3722_irq` maps regmap IRQ indexes across four interrupt banks. `struct as3722` stores the parent device, regmap, chip IRQ, IRQ flags, optional internal pull-ups, AC OK power-on behavior, and regmap IRQ data. Inline helpers wrap `regmap_read`, `regmap_write`, bulk I/O, `regmap_update_bits`, and `regmap_irq_get_virq`.

Control flow: Child drivers call inline helpers, which directly dispatch to regmap and regmap-irq. Probe control flow is external: the MFD core initializes `struct as3722`, configures optional pull-ups and AC OK startup behavior, registers regmap IRQs, and exposes virtual IRQs.

State and persistence: State resides in PMIC registers and in `struct as3722` flags describing board/chip configuration. RTC and watchdog state persist in hardware domains as long as the PMIC power domain supports them.

Dependencies and integration points: It includes `linux/regmap.h` and integrates tightly with regmap IRQ, regulator descriptors, GPIO/RTC/ADC/watchdog clients, and board/device-tree configuration handled by the MFD core.

Risks: Interrupt enum order must match the regmap IRQ table. Some comments and names mix SD2/SD6 temperature wording, so consumers must validate against the datasheet. Voltage selector boundaries and DNU ranges must be honored by regulators. Internal pull-up and AC OK settings affect board-level boot behavior.

Test signals: Compile all AS3722 subdrivers, verify regmap readable/writable ranges, confirm IRQ virq mapping for every `AS3722_IRQ_*`, exercise regulator voltage tables and GPIO mode programming, and validate RTC/ADC/watchdog behavior on hardware or an I2C/regmap mock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/as3722.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2603c.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2603c.h

Purpose: This file provides Actions Semi ATC2603C PMIC register definitions and interrupt indexes for the ATC260x MFD core and its regulator, power, RTC, audio, GPIO, and IR-related consumers.

Important APIs, types, and constants: `enum atc2603c_irq_def` maps the ATC2603C IRQ lines for audio, overvoltage, overcurrent, overtemperature, undervoltage, alarm, on/off, SGPIO, IR, remote control, and power input. Register definitions span PMU system control/status/pending, battery/VBUS/wall input, DC/DC and LDO controls, protection status/enables, charger, ADC channels, RTC, efuse, firmware-use scratch registers, abnormal status, mux/SGPIO/PWM, IR controller, audio input/output, PCM, reset, interrupt pending/mask, MFP/GPIO/pad controls, debug, chip version, and TWSI address. Bit masks define wake sources, wake flags, on/off press handling, state timers, interrupt masks, reset blocks, and external IRQ pad enable.

Control flow: There is no code flow in the header. Runtime flow is device match selecting this register table through `atc260x/core.h`, configuring regmap and regmap IRQ descriptors, then subdrivers using the constants to access chip functions.

State and persistence: Hardware registers hold PMU, RTC, charger, ADC, and wake state. Some firmware-use registers may act as scratch persistence across PMIC-controlled resets depending on hardware behavior.

Dependencies and integration points: It relies on common Linux `BIT`/`GENMASK` macros through included users. It is included by `atc260x/core.h`, making it part of the variant-selection contract.

Risks: Several registers are explicitly marked undocumented, so behavior may be revision-sensitive. The BIST definitions reuse low addresses `0x0A`/`0x0B`, which require context-aware interpretation. Wrong IRQ mask mapping can hide power fault events.

Test signals: Validate ATC2603C probe detects chip version, regmap can read PMU and INTS registers, regmap IRQs fire for on/off and power input, regulators program expected DC/LDO controls, and suspend/resume wake masks match enabled sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2603c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2609a.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2609a.h

Purpose: This header supplies ATC2609A PMIC register addresses, IRQ indexes, and core bit masks for Actions Semi ATC260x support. It is the ATC2609A variant counterpart to the ATC2603C register header.

Important APIs, types, and constants: `enum atc2609a_irq_def` defines audio, OV/OC/OT/UV, alarm, on/off, wakeup, IR, remote control, and power input IRQ indexes. Register groups cover PMU system controls, battery/VBUS/wall inputs, charging, five DC/DC rails, ten LDOs, fault interrupts/status, ADC channels, RTC, efuse, power status, battery/fuel-related calibration tables, power-on controls, IR controller, audio, PCM, CMU reset, interrupt pending/mask, MFP/GPIO/pad/debug, chip version, PWSI, and TWSI. Masks define wake enables/flags, on/off reset/long-short press behavior, S2/S3 timers, input wake detection, interrupt mask bits, CMU reset bits, and external IRQ pad enable.

Control flow: No executable code exists. The MFD core uses the chip match to select this register and IRQ layout; child drivers use the constants for regmap operations and regmap-irq mappings.

State and persistence: PMIC register state includes power sequencing, charger, ADC, RTC, wake flags, fuel-gauge/calibration data, GPIO, and IR state. No kernel persistence beyond runtime regmap state is defined in the header.

Dependencies and integration points: Included by `atc260x/core.h`; used by ATC260x parent and child devices. Consumers depend on Linux bit macros and variant-specific regmap register widths configured elsewhere.

Risks: ATC2609A register layout differs significantly from ATC2603C despite similar names. IRQ bit 7 is `WKUP` rather than `SGPIO`, and register offsets for regulators/fuel-gauge features differ. Copying constants across variants would misprogram power rails.

Test signals: Probe/match tests for ATC2609A, register readback of `CHIP_VER`, IRQ tests for `WKUP` and on/off, regulator voltage/current programming across DC0-DC4 and LDO0-LDO9, RTC alarm wake, and power input detection events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/atc2609a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/core.h

Purpose: This is the shared core interface for Actions Semi ATC260x PMIC MFD drivers. It ties variant register headers to a common `struct atc260x` runtime object and declares the match/probe entry points used by bus-specific front ends.

Important APIs, types, and constants: `enum atc260x_type` distinguishes ATC2603A, ATC2603C, and ATC2609A; `enum atc260x_ver` encodes silicon revisions A through H. `struct atc260x` stores parent device, regmap, regmap IRQ chip and data, a custom regmap mutex pointer, MFD cells, parent IRQ, chip type/version/name, revision register, and optional initialization register table. The exported functions are `atc260x_match_device()` and `atc260x_device_probe()`.

Control flow: A bus driver allocates/fills `struct atc260x`, creates a regmap, calls `atc260x_match_device()` to pick variant-specific cells, IRQ chip, revision register, and regmap configuration, then calls `atc260x_device_probe()` to initialize registers, IRQs, and MFD children.

State and persistence: Runtime state is in `struct atc260x`; hardware state is in the PMIC registers selected by the variant headers. The `init_regs` pointer represents boot-time register programming, not persistent kernel storage.

Dependencies and integration points: It includes the ATC2603C and ATC2609A variant headers, uses regmap/regmap-irq, MFD cells, device model, mutexes, and bus front ends.

Risks: Variant matching is central; a wrong `ic_type` or `rev_reg` will expose the wrong register map and child cells. Custom regmap locking must be consistent across all child accesses.

Test signals: Unit or probe tests should confirm each compatible string selects the expected `ic_type`, `ic_ver`, cell list, IRQ chip, and regmap config. Runtime validation includes child device creation, regmap IRQ registration, and init register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atmel-hlcdc.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/atmel-hlcdc.h

Purpose: This header defines the shared Atmel HLCDC/XLCDC MFD register bits and parent state used by display, PWM, and other HLCDC child drivers.

Important APIs, types, and constants: Register macros cover configuration slots, signal polarity/dither/guard timing, enable/disable/status/IRQ registers, XLCDC attribute update bits, clock selection/divider fields, block enable bits for pixel/sync/display/PWM/SIP/XLCDC blocks, and interrupt/status bits including start-of-frame, sync disable, FIFO error, and layer status. `struct atmel_hlcdc` stores the shared regmap, optional LVDS PLL clock, peripheral/system/slow clocks, and IRQ.

Control flow: The header has no functions. Parent probe initializes regmap and clocks, then child drivers use the shared `atmel_hlcdc` object to enable clocks, configure display timing or PWM functions, and handle IRQ status.

State and persistence: Hardware registers hold display signal configuration, block enable state, clock dividers, and interrupt state. Clock framework references are runtime kernel state and are not persistent.

Dependencies and integration points: Includes `linux/clk.h` and `linux/regmap.h`; integrates with DRM/display, PWM, clock framework, IRQ handling, and MFD child registration.

Risks: Clock divider macro `ATMEL_HLCDC_CLKDIV(div)` assumes a valid divider greater than or equal to two. HLCDC vs XLCDC bit layouts differ for mode and attribute update masks. Misprogrammed polarity or guard timing creates display sync faults rather than clean probe failures.

Test signals: Build child display/PWM drivers, verify clocks are acquired and prepared, confirm regmap writes to enable blocks and configure timings, exercise IRQ status handling for SOF/FIFO errors, and test both HLCDC and XLCDC-compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/atmel-hlcdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/axp20x.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/axp20x.h

Purpose: This is the shared Allwinner/X-Powers AXP PMIC family contract. It defines variant IDs, register maps, regulator IDs, IRQ IDs, device state, a variable-width register helper, and core match/probe/remove APIs.

Important APIs, types, and constants: `enum axp20x_variants` covers AXP152, AXP192, AXP202/209, AXP221/223, AXP288, AXP313A/323, AXP717, AXP803/806/809/813, and AXP15060. Register constants cover power inputs/outputs, regulators, charger, power-off, PEK key, ADC, GPIO, battery/fuel-gauge, OCV tables, Type-C fields, and multi-bank IRQ enable/status registers. Separate regulator-ID enums define each variant's child regulator numbering. IRQ enums map event numbers across variants, intentionally preserving gaps and out-of-bit-order PEK press/release ordering where needed. `struct axp20x_dev` carries device, IRQ, regmap, regmap IRQ data, variant, MFD cells, and selected regmap/IRQ configs. `axp20x_read_variable_width()` combines adjacent 8-bit registers into a 9-16 bit value. Public APIs are `axp20x_match_device()`, `axp20x_device_probe()`, and `axp20x_device_remove()`.

Control flow: Bus-specific drivers set `dev`, create regmap, call match to select variant-specific cells/configs, then probe to register IRQs and MFD children. Child drivers use variant register constants and regulator/IRQ IDs. The inline variable-width helper performs two sequential reads and returns either a negative error or the assembled value.

State and persistence: Persistent hardware state includes RTC/charger/fuel-gauge/OCV and power-control registers, depending on PMIC power domains. Kernel runtime state lives in `axp20x_dev` and regmap/regmap-irq structures.

Dependencies and integration points: Includes `linux/regmap.h`; integrates with regulator, power-supply, GPIO, ADC/IIO, RTC, PEK input, watchdog/poweroff, Type-C/charger, and MFD frameworks.

Risks: Variant-specific register reuse is extensive; using the wrong variant ID can touch unrelated hardware. IRQ enums are not uniformly zero-based, and gaps matter for regmap IRQ tables. Variable-width reads assume high byte at `reg` and low byte at `reg + 1`; callers must pass valid widths and readable adjacent registers.

Test signals: Probe each supported variant table, compare regulator counts to `*_REG_ID_MAX`, validate IRQ bank mappings including PEK order, run regmap range/cache tests, exercise ADC variable-width reads, and verify poweroff/charger/fuel-gauge behavior on boards with real PMICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/axp20x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bcm2835-pm.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/bcm2835-pm.h

Purpose: This minimal header defines shared state for the Raspberry Pi/Broadcom BCM2835-family power-management MFD driver.

Important APIs, types, and constants: `enum bcm2835_soc` distinguishes BCM2835, BCM2711, and BCM2712 integration variants. `struct bcm2835_pm` stores the parent device, mapped PM register base, ASB base, RP1/video ASB base, and selected SoC type. The header includes `linux/regmap.h`, although this struct itself uses raw `void __iomem *` mappings rather than a regmap pointer.

Control flow: No functions are declared. Runtime flow is in the MFD/platform driver: map MMIO regions, select SoC variant, populate `struct bcm2835_pm`, and register child functions that use the base pointers.

State and persistence: State is MMIO hardware register state plus runtime mapping pointers. No persistent kernel data is defined.

Dependencies and integration points: Integrates with platform/MMIO resource mapping, Raspberry Pi PM domains, reset/power subdrivers, and SoC variant handling.

Risks: Different SoCs have different ASB/RPIVID address availability; consumers must check the selected `soc` and valid mapped bases. Raw MMIO access requires correct barriers and register definitions elsewhere.

Test signals: Probe on each compatible SoC, validate resource mapping success, confirm child drivers only access available ASB blocks, and exercise power/reset domains that rely on the shared PM object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bcm2835-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bcm590xx.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/bcm590xx.h

Purpose: This header defines the shared Broadcom BCM590xx PMU MFD device structure, chip IDs, revision IDs, and dual-regmap layout.

Important APIs, types, and constants: PMU ID constants identify BCM59054 and BCM59056. Revision constants encode known digital and analog revision values for those chips. `enum bcm590xx_regmap_type` distinguishes primary and secondary register maps. Max-register constants bound the primary (`0xe7`) and secondary (`0xf0`) regmaps. `struct bcm590xx` stores the parent device, primary and secondary I2C clients, primary and secondary regmaps, PMU ID, and digital/analog revisions.

Control flow: No functions are declared. Parent probe reads ID/revision registers over I2C, initializes both regmaps, stores them in `struct bcm590xx`, and registers child devices that choose the required register map.

State and persistence: Hardware state lives in PMU registers across two I2C address spaces. Kernel state tracks the two bus clients and regmaps plus chip identity.

Dependencies and integration points: Includes device, I2C, and regmap headers; integrates with MFD children that require PMU regulator, power, or auxiliary functions and must address the correct regmap.

Risks: Primary/secondary register-map selection is a common failure point; a correct offset on the wrong I2C client is still wrong hardware. Revision constants are limited to known variants and may need extension for new silicon.

Test signals: Probe should verify both I2C clients/regmaps initialize, PMU ID matches supported IDs, revision reads match expected values, and child accesses route through the correct `BCM590XX_REGMAP_*` map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bcm590xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bd9571mwv.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/bd9571mwv.h

Purpose: This header defines register and IRQ constants for ROHM BD9571MWV-M and BD9574MWF-M PMIC MFD support, especially backup mode, DVFS/AVS, GPIO, protection, and interrupt handling.

Important APIs, types, and constants: Register constants include vendor/product/revision identification, I2C/FUSA controls, backup mode control/status/recovery/timers, AVS monitoring and VID registers, DVFS initialization/set/max/boost/monitor registers, GPIO direction/output/input/debounce/interrupt/mask, keep registers, protection and system error status registers, interrupt request/mask, BD9574-specific SSCG and reset/protection controls, and the access key. Product-code constants distinguish BD9571MWV and BD9574MWF. Interrupt request bit masks map mode, protection, GPIO, 128-hour/BKUP_HOLD, watchdog, and backup-trigger events. `enum bd9571mwv_irqs` defines the regmap IRQ indexes.

Control flow: The header is declarative. MFD probe validates vendor/product ID, configures regmap and regmap IRQs, then child drivers use register constants for regulators, GPIO, watchdog/backup, and system status.

State and persistence: Backup/keep registers and PMIC protection logs can persist through some system power states. Runtime kernel state is outside this header.

Dependencies and integration points: Includes device and regmap headers. Integrates with Renesas/R-Car board power management, regulator/DVFS control, GPIO, and interrupt consumers.

Risks: BD9574-specific registers overlap the common namespace but are not valid on BD9571. Backup/DDR keep-on bits control critical retention rails. Access-key protected writes must be sequenced correctly by implementation code.

Test signals: Verify vendor/product ID detection for both products, IRQ mapping for every `BD9571MWV_IRQ_*`, GPIO interrupt behavior, DVFS voltage programming, backup-mode retention bits, and protection/error status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bd9571mwv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bq257xx.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/bq257xx.h

Purpose: This header defines TI BQ257xx/BQ25703 charger register constants, field masks, unit conversions, ADC controls, and the shared charger device object.

Important APIs, types, and constants: Register addresses are 16-bit-spaced charger configuration/status locations: charge options, charge current, maximum charge voltage, OTG voltage/current, input voltage/current, minimum system voltage, charger/prochot status, DPM current, ADC readings, manufacturer/device ID, and ADC options. Field definitions include watchdog timing, charge-current mask and microamp limits, charge-voltage mask and microvolt limits, OTG voltage/current ranges, minimum VSYS range, charger fault/status bits, input current DPM conversion, battery/input/system ADC masks and units, ADC channel enables, ADC conversion start/full-scale bits, and OTG enable. `struct bq257xx_device` stores the I2C client and regmap.

Control flow: No functions are declared. The charger driver uses the constants to translate power-supply/regulator requests into register values through regmap, and uses ADC/status fields for charger state reporting.

State and persistence: Charger configuration and ADC/status state are hardware registers. Watchdog settings may reset charger state if the driver does not service or disable the timer.

Dependencies and integration points: Requires I2C and regmap types via including consumers. Integrates with power-supply and regulator/OTG paths, and with the MFD parent if split into subfunctions.

Risks: Unit conversions are central; off-by-one or offset mistakes can over/under-charge. Register widths are 16-bit, so regmap configuration must match chip endianness/word size. Watchdog default behavior can revert charger programming.

Test signals: Regmap tests for 16-bit register access, conversion tests for current/voltage min/max/step values, charger state/fault decoding, ADC channel enable/readback, OTG enable, and watchdog disable/timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/bq257xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cgbc.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/cgbc.h

Purpose: This header defines the Congatec Board Controller MFD data structures and command helper API used by child drivers to exchange commands with the board controller.

Important APIs, types, and constants: `struct cgbc_version` stores feature, major, and minor revision bytes. `struct cgbc_device_data` stores mapped session and command I/O memory windows, the active session ID, parent device, version, and a mutex. `cgbc_command()` is the exported command transaction helper, taking command buffer/size, data buffer/size, and an optional returned status byte.

Control flow: Child drivers call `cgbc_command()`, which is expected to serialize command writes/reads using `cgbc_device_data.lock`, session state, and the two I/O windows. The exact command protocol is implemented elsewhere.

State and persistence: Runtime state includes the session ID and version. Hardware/firmware may maintain board-controller session state across calls; no filesystem persistence exists.

Dependencies and integration points: It relies on MMIO (`void __iomem`), `struct device`, `struct mutex`, and `u8` definitions from including contexts. It integrates with child drivers that expose board-controller features such as monitoring, GPIO, or platform controls.

Risks: The include guard is incomplete: the file has `#ifndef _LINUX_MFD_CGBC_H_` but no matching `#define _LINUX_MFD_CGBC_H_`, so multiple inclusion in one translation unit is not prevented. Command buffer sizes are caller supplied and need strict validation in implementation code.

Test signals: Build tests should catch duplicate inclusion or missing type includes depending on include order. Runtime tests should exercise serialized concurrent commands, command status propagation, session creation/recovery, and invalid size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cgbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/core.h

Purpose: This is the generic Linux MFD core public header. It defines how an MFD parent describes child devices/cells and declares the APIs that register and remove those children.

Important APIs, types, and constants: `MFD_RES_SIZE()` and `MFD_CELL_*` macros construct common `struct mfd_cell` initializers for OF, OF-with-reg, ACPI, basic resource, and name-only cells. Dependency levels are `MFD_DEP_LEVEL_NORMAL` and `MFD_DEP_LEVEL_HIGH`. `struct mfd_cell_acpi_match` matches ACPI IDs or ADRs. `struct mfd_cell` includes child name/id/level, suspend/resume callbacks, platform data and size, ACPI/software-node/OF matching data, optional `of_reg`, resource arrays, resource-conflict behavior, runtime-PM callback suppression, and parent-supply mappings. `mfd_get_cell()` fetches the creating cell from a platform device. Public APIs include `mfd_add_devices()`, `mfd_add_hotplug_devices()`, `mfd_remove_devices()`, `mfd_remove_devices_late()`, and devres-managed `devm_mfd_add_devices()`.

Control flow: Parent drivers build `mfd_cell` arrays and call add APIs. The MFD core creates platform devices, attaches copied cell metadata/platform data/resources, maps IRQ domains/bases, and later removes devices through explicit or managed cleanup.

State and persistence: State is runtime platform-device and resource metadata. Platform data is copied into child devices; no persistent storage is involved.

Dependencies and integration points: Includes `linux/platform_device.h`; integrates with platform bus, OF/ACPI matching, software nodes, IRQ domains, resources, runtime PM, regulators, and devres.

Risks: Incorrect `pdata_size` or resource arrays can produce child memory corruption or invalid resources. `ignore_resource_conflicts` weakens safety. Matching duplicate OF compatibles without `of_reg` can bind the wrong child node. Parent supply mapping affects regulator lookup ownership.

Test signals: Build and probe tests for MFD parents, child platform-device creation count, OF/ACPI matching, resource and IRQ assignment, devm cleanup on probe failure, suspend/resume callback dispatch, and duplicate resource conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs40l50.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/cs40l50.h

Purpose: This header defines the shared Cirrus Logic CS40L50 advanced haptic MFD/core interface, including register constants, DSP queue commands, firmware names, device state, and core probe/remove/PM exports.

Important APIs, types, and constants: Register constants cover power supply and error release, boost low-power mode, interrupt status/mask banks, DSP memory regions, queue pointers, system info, core base, timing constants, PM algorithm ID, DSP queue command IDs, firmware filenames, and device/revision IDs. `enum cs40l50_irq_list` maps DSP queue, global error, UVLO, boost, temperature, and amplifier short interrupts. `enum cs40l50_wseqs` names power-on, standby, and active DSP write sequences. `struct cs40l50` stores device, regmap, mutex, `cs_dsp`, reset GPIO, regmap IRQ data, firmware/bin handles, DSP write sequences, IRQ, device ID, and revision. Exports include `cs40l50_dsp_write()`, `cs40l50_probe()`, `cs40l50_remove()`, `cs40l50_regmap`, and `cs40l50_pm_ops`.

Control flow: Bus front ends instantiate `struct cs40l50` and call common probe. Common code resets hardware, validates IDs, loads firmware/bin assets, initializes DSP sequences and IRQs, and uses DSP queue writes for hibernate/playback/control commands. PM ops manage autosuspend and low-power transitions.

State and persistence: Firmware and DSP state live in device memory while powered. Kernel state tracks loaded firmware handles, DSP sequence cache, IRQ data, and runtime PM state. No disk persistence beyond firmware files requested by the driver.

Dependencies and integration points: Depends on Cirrus `cs_dsp`, firmware loader, GPIO descriptors, PM, regmap, and regmap-irq. Integrates with haptics/input/FF child behavior and bus front ends.

Risks: DSP queue command sequencing and hibernate prevention must be serialized by `lock`. Firmware filenames are ABI-like asset names. IRQ masks use absolute register offsets; wrong regmap width or volatile tables can break interrupt clearing.

Test signals: Probe ID/revision validation, reset GPIO pulse timing, firmware load success/failure, DSP queue command completion, IRQ handling for global/boost/temp/amp faults, runtime suspend/resume, and haptic playback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs40l50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43-regs.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43-regs.h

Purpose: This dense header is the CS42L43/CS42L43B register and bitfield map. It is consumed by the CS42L43 MFD core and audio, soundwire, GPIO, SPI bridge, accessory-detect, amplifier, PLL, firmware/MCU, and codec subdrivers.

Important APIs, types, and constants: Register definitions span general interrupt status/masks, device/revision IDs, reset, drive strength, GPIO, clocking and sample-rate selection, PLL, PDM/ADC/decimator controls, digital volume/ramping, ASP/I2S configuration, routing/mixer inputs, ASRC/ISRC enables, headset/tip/ring/mic detect, block enables, SPI master and software-to-SPI bridge, headphone path, EQ coefficient/control, many interrupt and shadow status blocks, MCU boot/config/firmware status, and CS42L43B-specific register relocations/extensions. Bitfield masks and shifts are provided for every major register group. Magic values include `CS42L43_DEVID_VAL`, `CS42L43B_DEVID_VAL`, soft reset value, and firmware mission-control disable value.

Control flow: No functions are implemented. Driver control flow uses these constants to reset the device, validate variant IDs, configure clock/PLL/sample-rate domains, route audio mixers, enable functional blocks, program headset/accessory detection, operate the embedded SPI bridge, service interrupts, and coordinate MCU firmware configuration.

State and persistence: Hardware register state includes audio routing, gain/mute/ramp settings, PLL and sample rates, GPIO levels, headset detection state, SPI bridge transaction status, MCU boot/config flags, and interrupt shadows. Firmware state may persist while MCU memory remains powered.

Dependencies and integration points: This header is paired with `cs42l43.h` and regmap configuration. It integrates with ALSA SoC, SoundWire, GPIO, regulator/reset handling, interrupt controller, SPI controller, and firmware/configuration paths.

Risks: The file contains duplicate definitions for several CS42L43B firmware mission-control addresses; duplicate identical macros are harmless for C preprocessing but increase maintenance risk. Variant-specific addresses must be selected by device ID. Many masks are 32-bit; regmap val width must match. Incorrect mixer source or block-enable programming can create silent audio rather than obvious errors.

Test signals: Regmap readable/volatile/default tests, ID-based variant selection, soft reset, PLL lock/lost-lock IRQs, ASP/PDM/ASRC routing audio tests, headset/tip/ring detection interrupts, SPI bridge transfer tests, MCU firmware config handshake, and CS42L43B-specific decimator/register address coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43.h

Purpose: This header defines the external core state and IRQ numbering for Cirrus Logic CS42L43 MFD support.

Important APIs, types, and constants: `CS42L43_N_SUPPLIES` fixes the number of core bulk supplies. `enum cs42l43_irq_numbers` enumerates high-level IRQs for PLL lock, headphone startup/shutdown, headset detection, tip/ring debounce and presence detect, bias sense, DC detect, amplifier clock/supply/startup/shutdown/thermal/short faults, GPIO edges, headphone current limit, and load detection. `struct cs42l43` stores device, regmap, optional SoundWire slave, regulators, reset GPIO, parent IRQ, embedded regmap IRQ chip and data, boot work, attach/detach/firmware completions, firmware error, SoundWire frequency, PLL mutex, SoundWire PLL/attach/hardware-lock flags, and variant ID.

Control flow: Core probe initializes supplies/reset/regmap/IRQ data and schedules boot or firmware work. SoundWire attach/detach paths complete synchronization objects. Child drivers use `pll_lock` and state flags to coordinate PLL ownership and transport state.

State and persistence: Runtime state includes completions for asynchronous attach/detach/firmware, `firmware_error`, PLL activity, attachment and hardware lock flags, and variant ID. Hardware register/firmware state is described by `cs42l43-regs.h`.

Dependencies and integration points: Includes completion, mutex, regmap, regulator, and workqueue headers; forward-declares GPIO and SoundWire types. It integrates with SoundWire, regulators, reset GPIO, regmap IRQ, ALSA SoC, SPI bridge, GPIO, and firmware loading.

Risks: Asynchronous SoundWire attach/detach and firmware completions can race child access if not checked. PLL state is shared and must be guarded by `pll_lock`. IRQ enum order must match the regmap IRQ table built from register masks.

Test signals: Probe and remove tests for I2C/SoundWire variants, supply enable/disable sequencing, reset and firmware completion paths, PLL lock serialization, IRQ mapping for all enum values, and SoundWire attach/detach race handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da8xx-cfgchip.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da8xx-cfgchip.h

Purpose: This header defines TI DaVinci DA8xx `CFGCHIP` syscon register offsets and bitfields for consumers configuring PLL/EDMA, capture routing, USB PHY, EMAC/uPP/PRU, and McASP mute behavior.

Important APIs, types, and constants: `CFGCHIP(n)` converts a CFGCHIP register index into a 32-bit offset. CFGCHIP0 bits cover PLL0 master lock and EDMA3_0 transfer-controller default burst sizes. CFGCHIP1 bits cover eCAP source selection for three capture modules, HPI byte/address behavior, HPI enable, EDMA3_1 burst size, eHRPWM TBCLK sync, and McASP0 AMUTE source selection. CFGCHIP2 bits cover USB PHY clock-good, VBUS sense, reset, OTG mode override, PHY clock muxes, power-down, suspend, PLL, session/VBUS detection, and reference frequency. CFGCHIP3 bits cover RMII selection, uPP TX clock source, PLL1 lock, async clock, PRU event select, divider enable, and EMIFA clock source. CFGCHIP4 has McASP AMUTE clear.

Control flow: No functions exist. Syscon consumers combine masks and values with regmap updates to configure SoC-level muxes and PHY modes before enabling peripheral drivers.

State and persistence: Register state is SoC system-controller state and may survive peripheral driver unbind until reset or explicit reconfiguration.

Dependencies and integration points: Includes `linux/bitops.h`; integrates with syscon/regmap users in USB PHY, PWM/eCAP, EDMA, audio/McASP, networking, PRU, and clock/reset paths.

Risks: Several macros are named `CFGCHIP0_EDMA31...` inside the CFGCHIP1 section, which is historically confusing. These are global SoC controls; wrong updates can break unrelated peripherals. Field values must be masked before writes to avoid clobbering neighboring muxes.

Test signals: Consumer driver tests should verify regmap update masks, USB host/device OTG mode selection, reference-clock choices, eCAP routing, EDMA burst configuration, and no unexpected changes in unrelated CFGCHIP fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da8xx-cfgchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da903x.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da903x.h

Purpose: This header defines the legacy Dialog DA9030/DA9034/DA9035 PMIC MFD subdevice IDs, platform data, event/status masks, notifier APIs, and raw register helper APIs.

Important APIs, types, and constants: The unified subdevice ID enum lists DA9030 LEDs, vibrator, WLED, buck/LDO regulators, battery charger, DA9034 LED/vibrator/WLED/touch/regulators, and DA9035 buck3. LED/vibrator flag macros describe blink/duty and mode/frequency options. Platform data structs cover DA9034 touch, backlight, DA9030 battery parameters/callbacks, per-subdevice metadata, and top-level subdevice arrays. Event masks define DA9030/DA9034 power, charger, ADC, USB, touchscreen, headset, and watchdog events. Status masks expose current ONKEY, charger, USB/session, pen, headset, and hook-switch state. Public APIs include notifier registration/unregistration, status query, and low-level `da903x_write/read/writes/reads/update/set_bits/clr_bits`.

Control flow: Child drivers register notifiers for event masks, query status synchronously, and call raw I/O helpers to access PMIC registers through the parent. The parent MFD dispatches events and mediates register access.

State and persistence: Battery configuration is platform data. Runtime PMIC status/events live in hardware. Notifier subscriptions are kernel runtime state.

Dependencies and integration points: Integrates with LED, input/touchscreen, backlight, regulator, power-supply, notifier, and parent MFD code. It forward-declares `power_supply_info`.

Risks: Raw register helpers are exposed but documented as only for DA903x subdevice drivers; external misuse can bypass policy. Event bit numbering extends beyond 16 bits and must be stored in sufficiently wide masks. Platform callbacks for battery low/critical need safe context handling.

Test signals: Compile subdrivers, notifier delivery for selected event masks, status query correctness, raw I/O helper error propagation, LED/vibrator platform flags, battery threshold/callback behavior, and DA9030 vs DA9034 event/status differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da903x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/da9052.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9052/da9052.h

Purpose: This is the DA9052/DA9053 PMIC core interface. It declares ADC channels, IRQ indexes, chip IDs, the shared runtime object, regmap wrappers, device lifecycle APIs, and IRQ helper APIs.

Important APIs, types, and constants: ADC constants name VDDOUT, charge current, battery temperature/voltage, external ADC inputs, TSI, junction temperature, backup battery, and TSI mux channels. IRQ constants map four event banks into 32 logical IRQs. `enum da9052_chip_id` distinguishes DA9052 and DA9053 variants. `struct da9052` stores device, regmap, ADC lock, ADC completion, IRQ base/data, chip ID/IRQ, fault log, and optional `fix_io` hook for post-transfer SoC I/O workarounds. Inline wrappers implement single and group read/write and update operations via regmap, invoking `fix_io` after successful I/O. APIs include manual ADC read, temperature read, device init/exit, regmap config, IRQ init/exit, request/free IRQ, and IRQ enable/disable variants.

Control flow: Bus probe creates `struct da9052`, calls device init, initializes regmap IRQs, and registers children. Subdrivers use wrapper APIs; after each successful regmap operation the optional `fix_io` hook can perform required interface recovery.

State and persistence: ADC synchronization uses `auxadc_lock` and `done`. Fault logs and RTC/power state are hardware-backed. `fix_io` represents runtime bus workaround state.

Dependencies and integration points: Includes interrupt, regmap, slab, completion, list, MFD core, and `reg.h`. Integrates with regulator, GPIO, ADC/hwmon, RTC, touchscreen, charger, and IRQ consumers.

Risks: Wrapper functions return register values directly for reads, so callers must distinguish negative errors from valid unsigned register values. Group read assigns `val[i]` before checking `ret`, though it returns on error. `fix_io` must be safe after every touched register.

Test signals: Regmap wrapper tests with and without `fix_io`, ADC completion/timeout paths, IRQ request/free/enable/disable, fault-log readout, probe/init/exit cleanup, and child device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/da9052.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/pdata.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9052/pdata.h

Purpose: This header defines platform data for non-DT DA9052 PMIC board integrations.

Important APIs, types, and constants: `DA9052_MAX_REGULATORS` is 14. `struct da9052_pdata` contains LED platform data, an optional board init callback, IRQ and GPIO bases, an APM-use flag, and an array of regulator init-data pointers indexed by DA9052 regulator IDs.

Control flow: Board code passes this structure to the DA9052 MFD core. During initialization, the core may call `init(da9052)`, use IRQ/GPIO bases, provide LED data to LED children, and pass regulator init data to regulator children.

State and persistence: The structure is static board/runtime configuration. It has no persistence beyond platform device data and does not itself hold hardware state.

Dependencies and integration points: It forward-declares `struct da9052` and references LED and regulator platform data types supplied by including code. Integrates with DA9052 MFD, LED, GPIO, IRQ, APM, and regulator frameworks.

Risks: The regulator array must be ordered exactly as expected by DA9052 regulator descriptors. Callback failure semantics depend on core implementation. Legacy base-number fields can conflict with dynamically allocated GPIO/IRQ numbering.

Test signals: Board-file compile coverage, regulator init-data count/order checks, init callback success/failure behavior, LED platform data propagation, and IRQ/GPIO base assignment in child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/reg.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9052/reg.h

Purpose: This is the DA9052 PMIC register and bitfield catalog used by the DA9052 core and child drivers.

Important APIs, types, and constants: Register definitions cover page selection, status, park, events, fault log, IRQ masks, system controls, power-down disable, interface/reset, GPIO pairs, power sequencer IDs/status/timers, buck/LDO/supply/pulldown controls, charger and backup battery, LED boost/current/dimming, ADC manual/continuous/result/threshold registers, TSI controls/results, RTC counters/alarms/seconds, and page configuration. Bit masks describe status and event bits, IRQ mask bits, fault-log causes, system control and shutdown/deepsleep/watchdog fields, interface polarity/type, GPIO pin/type/mode fields, sequencer steps, regulator enable/config/voltage fields, charger currents/timers, LED enable/ramp/current, ADC mux/conversion/auto channels, TSI mux and coordinate LSB packing, and RTC calendar/alarm fields.

Control flow: There is no code. Subdrivers use these constants in regmap updates and DA9052 wrapper calls to configure power rails, detect events, read ADC/TSI/RTC state, and handle charger/LED functions.

State and persistence: Hardware state includes event latches, fault logs, sequencer state, regulator voltages, charger state, ADC/TSI samples, and RTC counters. Some fault/RTC information persists across selected reset/power states.

Dependencies and integration points: Included by `da9052.h`; integrates with regulators, charger, LED, ADC/hwmon, touchscreen, RTC, GPIO, and IRQ logic.

Risks: Many masks use uppercase hex and plain constants rather than `BIT`/`GENMASK`, so field composition must be manual and carefully shifted. Typos such as `EALRAM` and repeated comments are historical ABI names that consumers may already rely on. Page selection matters for registers above page 0.

Test signals: Regmap field tests for status/event/IRQ banks, regulator voltage enable programming, charger current/threshold programming, ADC result packing, TSI coordinate unpacking, RTC BCD/range handling if applicable, and fault-log decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9052/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/core.h

Purpose: This header defines the DA9055 PMIC core runtime structure, logical IRQ IDs, regmap I/O wrappers, and lifecycle exports.

Important APIs, types, and constants: IRQ IDs cover alarm, tick, nonkey, regulator, and hwmon events. `struct da9055` stores regmap, regmap IRQ data, parent device, I2C client, IRQ base, and chip IRQ. Inline wrappers provide single register read/write, bulk read, raw bulk write, and update-bits helpers. Exported APIs are `da9055_device_init()`, `da9055_device_exit()`, and `da9055_regmap_config`.

Control flow: I2C probe initializes regmap and `struct da9055`, then calls device init to set up IRQs and MFD children. Child drivers use the inline wrappers for register access.

State and persistence: Runtime state is `struct da9055` plus regmap/regmap-irq data. Hardware state includes PMIC system, regulator, ADC, RTC, and event registers defined in `reg.h`.

Dependencies and integration points: Includes interrupt and regmap headers; references `i2c_client` and `device` types through including contexts. Integrates with regulators, RTC, hwmon/ADC, onkey, and IRQ child functions.

Risks: `da9055_reg_read()` returns either a negative error or a positive register value, so callers must not cast blindly to unsigned. Raw group writes depend on regmap configuration permitting raw writes. IRQ constants are sparse and must match regmap IRQ chip definitions.

Test signals: Probe/init/exit cleanup, regmap wrapper error propagation, bulk read/write behavior, IRQ registration and child IRQ delivery, and child driver access to the shared `da9055` state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/pdata.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/pdata.h

Purpose: This header defines legacy platform data for DA9055 PMIC board integrations.

Important APIs, types, and constants: `DA9055_MAX_REGULATORS` is 8. `enum gpio_select` represents unavailable, GPIO1, or GPIO2 hardware control selection. `struct da9055_pdata` contains an optional board init callback, IRQ/GPIO bases, regulator init-data pointers, a reset-mode RTC enable flag, and `reg_ren`/`reg_rsel` arrays describing GPIO-controlled regulator enable/state and A/B voltage set selection.

Control flow: Board data is passed to the MFD core, which may call `init()`, configure base IDs, initialize regulators with supplied constraints, enable RTC reset-mode behavior, and pass GPIO control mappings to regulator code.

State and persistence: This is static board configuration. It influences hardware regulator mode and RTC behavior but stores no dynamic hardware state.

Dependencies and integration points: Forward-declares `struct da9055` and references regulator init data. Integrates with DA9055 MFD, regulator, GPIO, IRQ, and RTC code.

Risks: `reg_ren` and `reg_rsel` are pointers and need arrays sized to regulator descriptors; mismatched lengths can cause invalid reads in consumers. GPIO selection values are hardware-specific and can alter regulator state unexpectedly.

Test signals: Platform-data compile and probe tests, regulator init-data index validation, RTC reset-enable behavior, GPIO-controlled regulator enable/set selection, and init callback error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/reg.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/reg.h

Purpose: This header is the DA9055 register/bitfield map for system control, GPIO, regulators, ADC, sequencer, RTC, OTP, trim, configuration, and monitoring features.

Important APIs, types, and constants: Register constants define page control, status/fault/event/IRQ mask banks, controls A-E, power-down disable, GPIO control/mode, buck/LDO controls, ADC manual/continuous/result/thresholds, 32 kHz enable, buck current limits and modes, A/B voltage set registers, OTP count/address/data, RTC count/alarm/seconds, interface/config/trim registers, and general-purpose IDs. `DA9055_MAX_REGISTER_CNT` bounds the map. Bitfields define page write mode, status/fault/event/mask bits, debounce/reset/watchdog/system enable/shutdown/wakeup controls, GPIO pin/type/write-enable/mode, regulator enable/GPI/pulldown/voltage set selection, ADC mux/mode/result scaling, startup/reset timing, buck/LDO voltage ranges and sleep modes, OTP locks, RTC fields and alarm/tick bits, 32 kHz trim, IRQ type, VDD fault thresholds, shutdown modes, pull-up/down, monitor enables, and monitor index selection.

Control flow: No functions are present. DA9055 subdrivers use these definitions with regmap wrappers from `core.h` to program regulators, monitor ADC/VDD, configure GPIO, service events, and manage RTC/OTP/configuration.

State and persistence: Hardware state includes event latches, regulator A/B voltage sets, RTC counters, OTP/configuration, trim values, GP IDs, and monitor configuration. OTP and some config/trim data are persistent hardware state.

Dependencies and integration points: Included by DA9055 drivers for regulator, RTC, hwmon, GPIO, and core IRQ handling.

Risks: There are historical misspellings such as `VBMEM_SEL_SHIT`, `REGUALTOR`, and `ALARAM`; consumers must use exact names or clean up carefully. Some monitor index masks define values beyond the nominal two-bit mask (`DA9055_MON_A10_IDX_LDO6` is `0x4`), which needs datasheet confirmation.

Test signals: Register field encode/decode tests for regulator voltage ranges, A/B selection, GPIO modes, ADC scaling, RTC alarm/tick, OTP lock handling, VDD fault thresholds, and monitor index programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9055/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9062/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9062/core.h

Purpose: This header defines the Dialog DA9061/DA9062 PMIC core type, compatible variants, logical IRQ numbers, and shared runtime structure.

Important APIs, types, and constants: `enum da9062_compatible_types` distinguishes DA9061 and DA9062 compatible handling. `enum da9061_irqs` maps DA9061 IRQs across banks A-C, while `enum da9062_irqs` adds alarm and tick and defines the DA9062 IRQ count. `struct da9062` stores parent device, regmap, regmap IRQ data, and selected chip type.

Control flow: Bus probe detects compatible type, initializes regmap from `registers.h`, registers the correct regmap IRQ chip using the matching enum layout, and creates MFD children.

State and persistence: Runtime state is the `struct da9062` object and regmap IRQ data. Hardware state is the DA9061/DA9062 PMIC register set defined in `registers.h`.

Dependencies and integration points: Includes interrupt support and the DA9062 register map. Integrates with regulator, RTC, watchdog, onkey, GPIO, and hwmon/power-management child drivers.

Risks: DA9061 and DA9062 have different IRQ counts and event availability; using the wrong enum/table will misroute interrupts. The struct is intentionally small, so child drivers depend on shared regmap and chip type rather than copied platform data.

Test signals: Probe both DA9061 and DA9062 compatibles, verify IRQ count/table selection, regmap IRQ delivery for onkey/watchdog/temp/GPI events, and child creation for variant-appropriate functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9062/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9062/registers.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9062/registers.h

Purpose: This header defines the DA9062AA/DA9061-compatible PMIC device IDs, variant IDs, paged register addresses, and bitfields used by the DA9062 core and children.

Important APIs, types, and constants: IDs define device, metal revision, and variant revision values plus I2C page-select shift. Register constants span page/status/fault/event/IRQ masks, controls A-F, power-down disable, GPIO controls/modes/output/wakeup, four buck controls, four LDO controls, dynamic voltage control, RTC counters/alarms/seconds, sequencer state and step IDs, wait/32 kHz/reset, buck current limits/configs, A/B buck and LDO voltage registers, backup battery charger, interface/config registers, trim, GP IDs, and device/variant/customer/config IDs. Bitfields define page/write/revert, status/event/mask bits, power/watchdog/RTC/shutdown/debounce controls, GPIO modes, regulator enables/GPI/voltage selections/configs, RTC and alarm fields, sequencer steps, buck current/mode/voltage sleep bits, backup charger current/voltage, interface base address, PM/IRQ voltage/type fields, auto modes, shutdown/delay/reset behavior, oscillator trim/frequency, and identity masks.

Control flow: No code executes in the header. The core and child drivers use these definitions with regmap to detect the PMIC variant, configure events/IRQs, program regulators and DVC A/B selections, manage RTC/alarm/tick, sequence power rails, and configure GPIO/wakeup behavior.

State and persistence: Hardware state includes fault logs, event latches, power sequencing, regulator A/B sets, RTC counters, backup charger configuration, trim, GP IDs, and identity/config registers. RTC and selected fault/config registers can persist across low-power states depending on supply domains.

Dependencies and integration points: Paired with `da9062/core.h`; used by regulator, RTC, watchdog, onkey, GPIO, hwmon, and MFD core code. Relies on Linux `BIT` macros via including source.

Risks: Paged addresses above `0x100` require correct regmap paging. DA9061/DA9062 share much of the table but not all events/children. Field names use `AA` silicon suffix throughout and some mixed-case names (`nONKEY`) that must be preserved for compatibility.

Test signals: Regmap paging tests, identity/variant readback, IRQ mask/event mapping, regulator voltage and DVC A/B selection tests, RTC alarm/tick handling, GPIO wake/mode/output programming, sequencer step configuration, and backup battery charger settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9062/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9063/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/da9063/core.h

Purpose: This header defines the Dialog DA9063/DA9063L MFD core interface, child driver names, chip/variant IDs, IRQ numbering, shared runtime state, and core init APIs.

Important APIs, types, and constants: Driver-name macros identify core, regulators, LEDs, watchdog, hwmon, onkey, RTC, and vibration children. `PMIC_CHIP_ID_DA9063` is the expected chip ID. `enum da9063_type` distinguishes DA9063 and DA9063L. `enum da9063_variant_codes` lists AD, BB, CA, DA, and EA variant codes. `enum da9063_irqs` maps onkey, alarm, tick, ADC ready, sequencer, wake, temperature, comparator, LDO limit, regulator UV/OV, DVC ready, VDD monitor, warning, and GPI0-GPI15 interrupts. `struct da9063` stores device, type, variant code, flags, software-PM flag, regmap, chip IRQ, IRQ base, and regmap IRQ data. APIs are `da9063_device_init()` and `da9063_irq_init()`.

Control flow: Probe detects chip/variant, initializes `struct da9063`, configures regmap IRQs, then registers MFD children named by the macros. Child drivers use shared regmap and IRQ numbers.

State and persistence: Runtime state includes type, variant, flags, software power-management mode, and regmap IRQ data. Hardware state is in registers declared by the included DA9063 register map.

Dependencies and integration points: Includes interrupt support and `da9063/registers.h`. Integrates with regulator, LED, watchdog, hwmon, onkey, RTC, vibration, IRQ, and power-management paths.

Risks: DA9063L has a reduced feature set compared with DA9063; child registration must respect `type` and variant. `use_sw_pm` changes power-management behavior and must match platform expectations. IRQ enum ordering must match regmap IRQ tables.

Test signals: Chip/variant ID detection, DA9063 vs DA9063L child set selection, IRQ init and delivery for all event banks, software-PM mode behavior, and probe/remove cleanup of all named child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9063/core.h -->
