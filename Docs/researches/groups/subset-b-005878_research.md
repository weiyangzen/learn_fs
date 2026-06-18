# Research Report: subset-b-005878

Grouped research for Linux MFD headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each section preserves the source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77843-private.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max77843-private.h

This private MAX77843 header is the shared register and IRQ contract for the Maxim MAX77843 MFD core and its child drivers. It defines the I2C sub-addresses for TOPSYS, charger, fuel gauge, and MUIC functions, then maps register offsets for TOPSYS/haptic/LED, charger, fuel gauge, and MUIC banks. Important exported surface is not functions but constants: `enum max77843_sys_reg`, `enum max77843_charger_reg`, `enum max77843_fuelgauge`, `enum max77843_muic_reg`, `enum max77843_irq`, and `enum max77843_irq_muic`, plus bit masks for charger state, MUIC ADC/charger detection, switch routing, haptic mode, LED control, and SAFEOUT LDO enable/selection.

Control flow is imposed on users of this header: the MFD core must instantiate separate I2C clients/regmaps for the PMIC subsystems, demultiplex interrupt source bits in `INTSRC`, and child drivers must use the register-specific masks when updating bitfields. State is hardware-resident in registers such as charger config, MUIC switch path, interrupt masks, haptic config, and SAFEOUT control; this header declares no software persistence beyond stable numeric IDs consumed by child drivers. Dependencies are Linux I2C, regmap, bitops through `BIT()`, and MAX77843 child drivers for charger, MUIC, regulator, LED, haptic, and fuel-gauge style access.

Integration risks are mostly numeric ABI drift: changing enum order breaks IRQ mapping, confusing MUIC switch values can physically route USB/UART/audio incorrectly, and charger current macros are in microamps while register fields are small masks. Test signals include build coverage of all child drivers, regmap traces showing writes to the expected bank/client, IRQ storm/regression tests for charger and MUIC interrupts, and plug/charger tests that verify `CHG_INT_OK`, MUIC status masks, and SAFEOUT control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77843-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8907.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8907.h

This public MAX8907 header defines the MFD contract for the Maxim MAX8907 power-management chip. It maps the general, RTC, ADC/touch, charger, WLED, regulator, and sequencing registers; declares I2C addresses for general, ADC, and RTC clients; assigns regulator IDs from `MAX8907_MBATT` through `MAX8907_VRTC`; and gives IRQ number spaces for charger, general power-management, and RTC events. The main types are `struct max8907_platform_data`, carrying regulator init data and `pm_off`, and `struct max8907`, the core driver state with device pointer, IRQ mutex, I2C clients, regmaps, and `regmap_irq_chip_data` handles.

The header does not implement runtime flow, but it defines how the MFD core wires control: probe creates the general and RTC I2C/regmap contexts, registers IRQ chips for charger/on-off/RTC interrupt groups, and passes regulator init data to child regulators. Persistent state is split between hardware registers and the in-memory `struct max8907`; register values cover regulator voltages, enable masks, sequencing, charger, RTC alarms, and power-off behavior. Dependencies include mutexes, PM support, I2C/regmap definitions supplied elsewhere, regulator init data, and regmap IRQ.

Risks include overlapping numeric IRQ enums that reset to zero per group, so users must keep group context; regulator IDs are a public index into `init_data`; and `pm_off` makes power-off behavior platform-sensitive. Test signals include MFD probe with all three I2C addresses, regmap IRQ registration for all groups, regulator enumeration count matching `MAX8907_NUM_REGULATORS`, RTC alarm interrupt delivery, and system power-off tests when `pm_off` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8907.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8925.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8925.h

This header exposes the platform and helper API for the Maxim MAX8925 MFD. It defines regulator/sub-device IDs, charger current and top-off enums, register addresses for charger, general power management, touch/ADC, RTC, WLED, buck and LDO control, interrupt masks, and a flat `MAX8925_NR_IRQS` IRQ numbering. The central state type is `struct max8925_chip`, which stores device and I2C clients for main, ADC, and RTC functions, I/O and IRQ mutexes, IRQ base/core IRQ/TSC IRQ, and wakeup flags. Platform data is split into backlight, touch, power, and regulator init data fields.

Unlike many register-only headers, this file declares callable helpers: `max8925_reg_read`, `max8925_reg_write`, bulk read/write, `max8925_set_bits`, and lifecycle helpers `max8925_device_init` and `max8925_device_exit`. Control flow is that board/platform data configures child devices, the core initializes clients and IRQs, and children use the helper API to serialize register access through the MFD. State lives in hardware registers for regulators, charger, WLED, touch, RTC, and interrupt masks, while software state lives in `max8925_chip` and platform-data pointers.

Dependencies include I2C, mutexes, interrupts, regulator init data, and power-supply/backlight/touch child drivers. Risks include bitfield platform data widths for charger options, many individual regulator init pointers that can be misaligned with IDs, and helper users needing the correct I2C client for the target register bank. Test signals include helper read/write error-path coverage, IRQ masking/unmasking, charger policy validation for top-off and fast-charge settings, and probe/remove coverage that confirms child devices are cleaned up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8925.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8997-private.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8997-private.h

This private MAX8997/MAX8966 header is the low-level register, IRQ, and core-state contract for the MFD. It enumerates PMIC registers, MUIC registers and masks, haptic registers, RTC registers, interrupt source groups, individual PMIC/MUIC IRQs, GPIO masks, and chip variants. `struct max8997_dev` is the integration anchor: it stores PMIC/RTC/haptic/MUIC I2C clients, platform data, bus and IRQ locks, irqdomain, IRQ mask cache/current arrays, a battery platform device, hibernation register dump storage, and GPIO status cache.

The declared APIs are `max8997_irq_init`, `max8997_irq_resume`, and I2C register helpers for single, bulk, and masked-update access. Control flow flows from MFD probe into child registration: each child receives the shared `max8997_dev` and uses the helper functions against the correct I2C client. IRQ control is grouped by `enum max8997_irq_source`; the IRQ layer caches masks and maps hardware bits to virtual IRQs through an irqdomain. State persistence is explicit in `reg_dump`, used for hibernation restore across PMIC, MUIC, and haptic register ranges; GPIO state is also mirrored in memory.

Dependencies include I2C, irqdomain, exported symbols, mutexes, and public platform data from `max8997.h`. Risks include cross-bank register confusion, hibernation dump sizing depending on enum sentinels, unimplemented IRQ groups still present in enums, and stable IRQ enum ordering being required by irqdomain mappings. Test signals include suspend/hibernate resume restoring masks/registers, MUIC cable IRQ demux, RTC alarm IRQs, GPIO interrupt edge masks, and fault-injection of I2C helper failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8997-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8997.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8997.h

This public MAX8997/MAX8966 header describes board-facing platform data and child-driver configuration. It lists regulator IDs for LDOs, bucks, 32 kHz enables, charger controls, and SAFEOUT regulators. It defines regulator init records with optional DT nodes, MUIC register initialization records, MUIC path defaults and delayed cable detection, haptic motor/mode/PWM enums, haptic platform data, LED operating modes, LED brightness data, and the top-level `struct max8997_platform_data`.

Control flow is policy-oriented rather than executable: platform or DT parsing populates `max8997_platform_data`, the MFD core passes regulator arrays and child-specific pdata to regulator, MUIC, haptic, charger, and LED drivers, and those child drivers apply the public settings via private register helpers. State includes GPIO-DVS voltage tables for buck1/2/5, flags controlling whether those bucks may be independently changed, charger end-of-charge and timeout policy, MUIC default USB/UART paths, haptic waveform configuration, and initial LED modes/brightness.

Dependencies include regulator consumer/init types and device tree node references. Integration risks are called out by the comments: enabling GPIO-DVS for multiple bucks can cause one `set_voltage` request to affect another buck, and `ignore_gpiodvs_side_effect` changes how the regulator driver treats that hazard. Other risks include charger units/ranges, LED brightness range depending on mode, and MUIC path constants needing to match private register values. Test signals include regulator voltage changes with GPIO-DVS enabled and disabled, charger timeout/eoc programming, MUIC path initialization, haptic external/internal mode behavior, and LED current limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8997.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8998-private.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8998-private.h

This private MAX8998/LP3974/LP3979 header defines the register enum, IRQ enum, interrupt masks, variant IDs, and core state for the older Samsung/Maxim PMIC MFD. `MAX8998_NUM_IRQ_REGS` fixes four interrupt mask/status banks. The register enum covers IRQ, status, charger, active discharge, on/off, buck voltage, LDO voltage, backup charger, and low-battery configuration registers. The IRQ enum covers DC input, jig, power key, RTC watchdog/alarm, charger, and low-battery events.

`struct max8998_dev` stores shared runtime state: device and platform data, I2C clients for regulator and RTC functions, I/O and IRQ mutexes, IRQ base/irqdomain, hardware IRQ numbers, current and cached IRQ mask arrays, variant type, and wakeup flag. Declared APIs are IRQ lifecycle/resume helpers and register access helpers for read, write, bulk read/write, and masked update. Control flow is the standard MFD split: core probe initializes the shared struct and IRQ domain, then child drivers use helper APIs and register constants to operate regulators, charger, and RTC.

State lives primarily in PMIC registers, with IRQ masks mirrored in `irq_masks_cur`/`irq_masks_cache` for bus-lock synchronization. Dependencies include platform data from `max8998.h`, I2C, mutex, irqdomain, and variant-specific child code. Risks include enum register numbering being implicit rather than explicit addresses, variant differences for LP3974/LP3979, four-bank IRQ mask synchronization, and wakeup behavior across suspend. Test signals include IRQ masking cache coherency, RTC alarm and wake tests, regulator helper update tests, and variant probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8998-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8998.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/max8998.h

This public MAX8998 header defines regulator IDs and board/platform configuration consumed by the MAX8998 MFD and regulator/RTC/charger children. The regulator ID enum starts at `MAX8998_LDO2 = 2`, preserving the chip’s numbering rather than a zero-based compact list, then covers LDOs, bucks, 32 kHz enables, charger enable, SAFEOUTs, and charger current. `struct max8998_regulator_data` pairs a regulator ID with init constraints and optional DT node. `struct max8998_platform_data` supplies regulator arrays, IRQ base, ONO IRQ, buck DVS voltage tables/default indices, wakeup and RTC-delay quirks, and charger EOC/restart/timeout policy.

The file defines no executable control flow, but it constrains MFD probe and child setup. The MFD core reads platform data, registers children, and child drivers program hardware via private helpers. State/persistence is mostly board policy: buck voltage lock prevents changing preset BUCK1/2 DVS registers, voltage arrays provide DVS values, and `rtc_delay` models an LP3974 read-after-write timing bug. Dependencies are regulator machine/init data and device-tree node types.

Risks include the non-zero regulator ID base, invalid charger policy values being documented as leave-unchanged, buck voltage lock needing enforcement by the regulator driver, and variant-specific RTC delay. Test signals include regulator ID mapping, DVS table programming with lock enabled/disabled, charger EOC/restart/timeout boundaries, wakeup from suspend, and LP3974 RTC write/read sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max8998.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13783.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mc13783.h

This MC13783-specific header layers chip-specific regulator and IRQ constants on the common `mc13xxx.h` API. It includes `linux/mfd/mc13xxx.h`, defines MC13783 regulator IDs for switchers, PLL, audio, digital, RF, SIM, camera, vibrator, MMC, GPO, and power-gate regulators, and maps MC13783 IRQ names either to common `MC13XXX_IRQ_*` values or chip-specific numeric positions.

There is no direct control flow or function implementation in this file. Its role is to let MC13783 child drivers use stable symbolic IDs when registering regulators and requesting IRQs through common MC13xxx helpers. State and persistence are external: regulator state, charger/USB/audio events, and IRQ latches live in PMIC registers managed by the MC13xxx core. Dependencies are the common MC13xxx MFD core, regulator child drivers, IRQ users, and platform data using these IDs.

Risks include mixing common and MC13783-specific IRQ spaces, accidental renumbering of regulator IDs that are used as driver IDs, and stale definitions for rarely used USB/audio interrupts. Test signals include regulator registration count/order for MC13783, IRQ request/status tests for aliases such as ADCDONE and chip-specific lines such as USB/ID/SE1, and build coverage of child drivers using these names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13783.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13892.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mc13892.h

This MC13892-specific header is a compact regulator ID map for the Freescale/NXP MC13892 PMIC family on top of the common MC13xxx framework. It includes `mc13xxx.h` and defines IDs for switchers, boost, IO, PLL, digital, SD, USB, video, audio, camera, general-purpose regulators, GPOs, power-gate controls, and coincell supply.

The file has no functions or runtime control flow. Its constants are consumed by MC13892 regulator/platform data and child drivers that call the shared MC13xxx register, IRQ, and ADC APIs. State lives in hardware and in the common MC13xxx core; this header only names the indexes used to address regulator descriptors and initialization records. Dependencies are therefore the common MC13xxx header and the regulator child implementation.

Risks are ID drift and mismatch with regulator descriptor arrays: because the IDs are simple consecutive macros, reordering them breaks platform data silently. The file also does not define MC13892-specific IRQ aliases, so users must know when to use common `MC13XXX_IRQ_*` names. Test signals include regulator descriptor array coverage for all 24 IDs, probe tests with representative platform data/DT, and compile tests for downstream users of each macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13892.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13xxx.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mc13xxx.h

This is the common public API for the MC13xxx PMIC MFD family. It forward-declares `struct mc13xxx` and exports locking, register access, read-modify-write, IRQ request/free/status/mask/unmask, flag retrieval, and ADC conversion APIs. It also defines common IRQ numbers, audio subdevice IDs, regulator platform data, LED IDs and control bitfield helpers for MC13783/MC13892/MC34708, button debounce/reset flags, touchscreen timing data, codec SSI port selection, feature flags, and ADC register/mode constants.

Control flow is centered on the common MFD core: child drivers lock the core when needed, use `mc13xxx_reg_read/write/rmw` for PMIC register access, request PMIC interrupts by logical IRQ number, and perform ADC conversions with mode/channel/timing arguments. `mc13xxx_irq_request_nounmask` currently aliases `mc13xxx_irq_request`, so callers expecting different mask behavior should verify core semantics. State includes hardware registers, interrupt masks/pending bits, ADC conversion results, and platform-data-selected child devices. The core struct is intentionally opaque to keep children behind helper APIs.

Dependencies include Linux interrupt types, regulator init data, device tree nodes, LED/input/touch/audio consumers, and chip-specific headers such as MC13783/MC13892. Risks include concurrency misuse if callers bypass the lock discipline, 24-bit PMIC register masks being expressed as `u32`, ADC timing units (`ato`) being hardware-clock ticks, and platform feature flags controlling which children are instantiated. Test signals include RMW atomicity tests, IRQ mask/status behavior, ADC conversion modes for touchscreen and single/multi-channel reads, and platform-data coverage for regulators, LEDs, buttons, touchscreen, and codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mc13xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h

This header defines the MCP host/device abstraction used by older Linux MFD-style MCP bus support. `struct mcp` contains module ownership, operation callbacks, a spinlock, use count, serial clock rate, read/write timeout, and an embedded `attached_device`. `struct mcp_ops` supplies host operations for telecom/audio divisors, register read/write, and enable/disable. `struct mcp_driver` wraps a `device_driver` with MCP-specific probe/remove callbacks.

The API exposes wrapper functions for divisors, register access, enable/disable, host allocation/add/delete/free, and driver register/unregister. Control flow is bus-like: a host allocates and adds an `mcp`, a driver registers and probes against the attached device, and child code uses `mcp_reg_read/write` and enable/disable around hardware access. State is software-visible in `use_count`, lock-protected hardware access, clock settings, and driver data stored on the embedded device. `mcp_priv()` returns private memory immediately after the allocated `struct mcp`, so allocation size and type assumptions matter.

Dependencies include Linux device model, modules, spinlocks, and the MCP host implementation. Risks include lifetime and ownership bugs around the embedded device, races if operation wrappers do not consistently hold `lock`, and private-data layout misuse. Test signals include host allocation/free leak checks, driver probe/remove ordering, concurrent register access tests, clock divisor programming, and module unload behavior while devices are attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h

This OMAP Menelaus PMIC header exposes board integration and helper APIs for MMC slot power, voltage rails, sleep regulator configuration, and VCORE hardware limits. `struct menelaus_platform_data` provides an optional `late_init` callback. Exported functions register/unregister an MMC callback, configure MMC open-drain and slot power/card-detect behavior, set VMEM/VIO/VMMC/VAUX/DCDC voltages, select slot routing, read slot pin states, program VCORE roof/floor hardware values, and set regulator sleep bits.

Control flow is platform-service oriented: board or MMC code calls Menelaus helpers after the MFD driver is available, callbacks report card-mask changes, and voltage/sleep settings are applied to PMIC registers by the implementation. State lives in hardware regulator configuration, MMC slot state, callback registration, and sleep-enable bit masks such as `EN_VPLL_SLEEP` through `EN_VC_SLEEP`. This header does not expose a device struct, so the implementation likely owns singleton-style state.

Dependencies include the Menelaus MFD implementation, OMAP board/MMC users, integer voltage units in millivolts, and `u8`/`u32` kernel types. Risks include global callback lifetime, slot number ambiguity, voltage-range validation being hidden in implementation, and sleep bit masks accidentally disabling essential rails. Test signals include callback registration/unregistration order, MMC slot power and card-detect tests, voltage boundary checks, suspend/resume regulator sleep programming, and VCORE roof/floor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/motorola-cpcap.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/motorola-cpcap.h

This Motorola CPCAP header is a regmap-oriented register definition file for the CPCAP PMIC/audio/USB/ADC/charger/RTC/LED/GPIO device. It defines vendor and revision constants/macros, then assigns real register offsets for interrupt banks, resource assignment, version, macro interrupts, power/clock/RTC, switchers and regulators, audio codec blocks, coulomb counter, ADC, USB/ULPI, GPIO, display/keypad/RGB/camera/BT/privacy LEDs, one-wire/GCAI, and test registers. It also provides inline helpers `cpcap_get_revision()` and `cpcap_get_vendor()` and declares `cpcap_sense_virq()`.

Control flow is regmap based. Child drivers use these offsets with the shared regmap supplied by the MFD core. The inline helpers read `CPCAP_REG_VERSC1`, decode revision/vendor fields, and log via `dev_err()` on failure. `cpcap_sense_virq()` lets children query virtual IRQ sense state through the MFD/IRQ integration. State is hardware-resident across broad functional blocks, with no persistent software struct in this header.

Dependencies include Linux device and regmap APIs, virtual IRQ mapping in the CPCAP core, and children for regulators, RTC, audio, power, ADC, USB, LEDs, and GPIO. Risks include broad register coverage with sparse offsets, historical comments noting undocumented revision/vendor bits, and direct child access needing correct register width/endian regmap configuration. Test signals include revision/vendor decode tests against known raw values, regmap read/write smoke tests for representative banks, IRQ sense tests, and child probe tests that verify offsets match hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/motorola-cpcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mp2629.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mp2629.h

This compact MP2629 header defines shared MFD state and ADC channel identifiers for the Monolithic Power Systems MP2629 power-management/charger device. `struct mp2629_data` contains only a device pointer and regmap pointer, making regmap the central integration mechanism. `enum mp2629_adc_chan` enumerates battery voltage, system voltage, input voltage, battery current, input current, and an end sentinel.

There is no direct control flow here. The MFD core or parent driver owns the `mp2629_data` instance, child ADC/IIO/power-supply components use the regmap to access hardware, and channel IDs map consumers to conversion logic in implementation files. State is in hardware registers and in the shared `dev`/`regmap` pointers; the header does not define platform data or persistence.

Dependencies include Linux device and regmap APIs and child drivers that agree on the ADC channel order. Risks include enum order becoming ABI between MFD and ADC channel descriptors, lack of register definitions in this header requiring cross-file consistency, and all error handling living in implementation. Test signals include ADC channel count matching `MP2629_ADC_CHAN_END`, regmap availability at child probe, read scaling for voltage/current channels, and power-supply integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mp2629.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h

This MediaTek MT6323 core header defines the PMIC interrupt status numbering used by the MT6397-family MFD/IRQ framework. `enum MT6323_IRQ_STATUS_numbers` lists status bits for speaker left alarms, battery high/low, watchdog, power key, thermal high/low, VBATON, charger-valid/detect/overvoltage, and over-current/status lines for LDO, fast charger key, accessory detect, audio, RTC, VPROC, VSYS, and VPA. `MT6323_IRQ_STATUS_NR` is the sentinel.

The header has no functions; its control-flow role is to provide stable hardware IRQ indexes to the PMIC IRQ registration tables. The MFD core reads interrupt status registers from the MT6323 register map, maps these enum values into Linux IRQs, and child drivers request the logical IRQs relevant to their blocks. State is interrupt latch/mask state in hardware, not in this header.

Dependencies are the MediaTek PMIC wrapper/MFD IRQ implementation and the matching `mt6323/registers.h` offsets, especially `MT6323_INT_STATUS0/1` and interrupt mask/control registers. Risks include sparse numbering (`LDO = 16`) matching hardware bank boundaries, uppercase enum type style that differs from later MT headers, and enum order being used by IRQ tables. Test signals include IRQ table size matching `MT6323_IRQ_STATUS_NR`, power-key/charger/RTC interrupt delivery, and status-bank boundary tests around bit 16.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/registers.h

This MT6323 register header maps the PMIC register address space as symbolic offsets. It covers charger control (`CHR_CON*`), startup (`STRUP_CON*`), speaker (`SPK_CON*`), chip ID and top clock/reset/test/status registers, interrupt mask/status/control, over-current gear/control, SPI/DEW wrapper diagnostics and cipher/CRC registers, buck regulators for VPROC/VSYS/VPA, current sinks, analog and digital LDO blocks, efuse values and outputs, RTC mix registers, audio top, AUXADC data/control, and accessory-detect registers.

There are no functions or types; child drivers use these constants with a regmap supplied by the MFD core. Control flow is convention-based: set/clear companion registers allow atomic bit manipulation, status registers are read during IRQ demux and health checks, and regulator/ADC/audio/charger drivers address their block-specific ranges. State is entirely hardware register state, including volatile status/interrupts and persistent-ish efuse/trim values.

Dependencies include MT6323 core IRQ numbering, MediaTek PMIC regmap configuration with 16-bit aligned offsets, regulator, charger, audio, AUXADC, and accessory-detect drivers. Risks include silent breakage from wrong offsets, gaps in numbered register series, set/clr misuse, and treating efuse/DEW/test registers as normal writable configuration. Test signals include compile-time users resolving all symbols, regmap access traces for each functional block, IRQ status reads from `INT_STATUS0/1`, regulator enable/voltage tests, and ADC/accessory-detect smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h

This MT6328 core header defines PMIC IRQ status numbers for the MT6328 MFD. The enum covers power/home key press and release, thermal/battery high-low, RTC/audio/accessory-detect events, low-battery and impedance ADC events, over-current events for VPROC/VSYS/VLTE/VCORE/VPA/LDO, charger/overvoltage/VBATON/watchdog events, fuel-gauge thresholds, and speaker fault events. The numbering is sparse at hardware bank boundaries, with groups starting at 0, 16, and 32.

Control flow is indirect: these constants are used by the MFD IRQ tables to map bits in MT6328 interrupt status registers to Linux virqs. Child drivers request the mapped IRQs and the core handles register-level masking and demux. State is hardware interrupt status/mask data; this header only defines logical positions.

Dependencies include the MT6328 register header for `INT_CON*`, `INT_STATUS*`, and `INT_TYPE_CON*`, the MediaTek PMIC IRQ framework, and child drivers for keys, charger, battery/fuel gauge, audio, accessory detect, RTC, and regulators. Risks include sparse numbering, status count lacking an explicit `_NR` sentinel, and the closing include-guard comment naming MT6323 rather than MT6328. Test signals include IRQ table coverage for all enum values, edge tests for key press/release, charger plug/overvoltage events, and over-current interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/registers.h

This MT6328 register header defines a large 16-bit-offset PMIC map. It includes startup and analog startup registers, hardware/software chip ID, top status/control/test/clock/reset registers, interrupt mask/type/status registers, DEW wrapper diagnostics/cipher/CRC registers, buck and SMPS analog controls, VCORE/VPROC/VSRAM/VLTE/VPA regulator blocks, zero-cross and current-sink controls, analog/digital/special LDOs, speaker controls, OTP value/output ranges, RTC mix, fuel-gauge ADC, audio decode/encode/NCP blocks, AUXADC data/buffer/request/control/threshold/debug registers, accessory detect, charger controls, BATON, and EOSC/VRTC trim registers.

There is no executable code. Drivers consume these defines through regmap operations: regulators use buck/LDO ranges, IRQ core uses interrupt control/status/type registers, fuel gauge and AUXADC drivers use ADC blocks, audio uses codec analog blocks, and charger/power code uses charger and BATON registers. State is hardware state, with volatile status/ADC/IRQ registers and calibration/OTP registers.

Dependencies are the MT6328 core IRQ enum, MediaTek PMIC wrapper/regmap configuration, and child drivers for each functional block. Risks include high symbol volume, gaps and aliases in register sequences, `_SET`/`_CLR` register misuse, OTP/trim registers being sensitive, and 16-bit alignment assumptions. Test signals include register-map range validation, regmap readable/writeable/volatile tables if present, regulator voltage enable tests across VCORE/VPROC/VSRAM/VLTE/VPA, IRQ type/status tests, AUXADC channel reads, and charger plug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h

This MT6331 core header defines the IRQ status numbering and bank-size macros for the MT6331 PMIC. The enum covers power/home key, charger detect, thermal/battery high-low, RTC, audio, MAD, accessory-detect events, and over-current events for VDVFS11-14, GPU, VCORE1/2, VIO18, and LDO. It also defines `MT6331_IRQ_CON0_BASE/BITS` and `MT6331_IRQ_CON1_BASE/BITS` to describe interrupt bank layout for the MediaTek PMIC IRQ framework.

Control flow is limited to IRQ table construction: the MFD core uses base/bit counts to register interrupt banks, reads status registers, and exposes Linux virqs for child drivers. State is hardware interrupt status/mask state. The header has no functions or software storage.

Dependencies include matching register offsets in `mt6331/registers.h`, MediaTek PMIC IRQ structs/macros, and child drivers for keys, charger, RTC, audio, accessory detect, and regulators. A notable risk is that `MT6331_IRQ_CON1_BITS` references `MT6331_IRQ_STATUS_VDFS11_OC`, while the enum defines `MT6331_IRQ_STATUS_VDVFS11_OC`; this appears to be a typo that would break compilation if the macro is used. Other risks are sparse enum values and bank-boundary assumptions. Test signals include compiling users of the bank macros, IRQ table size checks, and interrupt injection across both banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h

This MT6331 register header maps the PMIC into symbolic 16-bit offsets. It includes startup registers, hardware/software ID and top status/control/test registers, clock/reset/interrupt control and type/status registers, DEW diagnostics and cipher/CRC registers, buck global and VDVFS11/12/13/14 regulator controls, VGPU, VCORE1/2, VIO18, buck calibration, zero-cross and current sinks, analog/system/digital LDO controls, OTP output/value ranges, RTC mix, extensive audio analog/digital/MAD registers, AUXADC data/status/request/control registers, and accessory-detect controls.

No runtime code is implemented. The MFD core and child drivers use these constants with regmap: IRQ code uses `INT_*`, regulator code uses buck/LDO blocks, audio drivers use `AUD*`, ADC code uses `AUXADC_*`, and accdet uses `ACCDET_*`. Hardware registers hold all state; this header is a naming layer for address stability.

Dependencies include `mt6331/core.h`, MediaTek PMIC regmap, and block-specific child drivers. Risks include large offset surface, gaps in register sequences, sensitive OTP/test/DEW registers, and dependence on exact 16-bit address spacing. Combined with the core-header typo in `MT6331_IRQ_CON1_BITS`, IRQ-bank users need compile coverage. Test signals include symbol resolution for regulator/audio/AUXADC/accessory drivers, regmap access tests for each block, IRQ status/type handling, and read-only/volatile range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h

This MT6332 core header defines the PMIC IRQ numbering and bank layout for a charger/flash/regulator-heavy companion PMIC. The enum covers charger completion and faults, thermal shutdown/regulator events, OTG and charger over-current/thermal/short conditions, flash timeout and LED open/short events, overvoltage and charger plug events, battery/fuel-gauge thresholds, speaker faults, BIF, WLED, and regulator over-current events for VDRAM, VDVFS2, VRF1/2, VPA, VSBST, and LDO. Bank macros describe four interrupt groups using base and bit-count values.

Control flow is IRQ-bank registration and demux by the MFD core. The core uses these constants with status/control registers to map hardware interrupt bits to Linux virqs; child drivers consume the virqs. State is hardware interrupt latch/mask state only.

Dependencies include `mt6332/registers.h`, MediaTek PMIC IRQ infrastructure, charger, flash/WLED, regulator, battery/fuel-gauge, speaker, BIF, and OTG consumers. Risks include sparse values at 0, 16, 32, 45, and 48, bank bit-count macros depending on inclusive arithmetic, and event names encoding hardware fault semantics that child drivers must not reinterpret incorrectly. Test signals include interrupt mapping tests for all four banks, charger/flash fault injection, over-current virq delivery, and build checks for bank macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/registers.h

This MT6332 register header defines an offset map beginning in the `0x8000` range. It covers chip ID, top/test/drive/status registers, flash and core controls, charger/status/boost controls, top clock/reset/interrupt controls and status registers, charger watchdog, DEW wrapper diagnostics, BIF, BATON, buck global controls, VDRAM, VDVFS2, VRF1/2, VPA, VSBST, buck calibration, AUXADC data/status/request/control, startup and fuel-gauge ADC, OTP output/value ranges, LDO controls, frequency meter, IWLED, speaker, test input/output muxes, debug, reset status, and an extended VDVFS2 register.

There is no function implementation. The register constants feed regmap operations in MFD and child drivers: charger/boost/flash/WLED blocks use the lower bank, regulator drivers use buck and LDO sections, ADC/fuel-gauge drivers use AUXADC/FGADC, BIF code uses BIF registers, and IRQ code uses `INT_CON*`/`INT_STATUS*`. State is in hardware registers, with volatile status and persistent calibration/OTP regions.

Dependencies include `mt6332/core.h`, MediaTek PMIC regmap configuration that supports high offsets, and child drivers for charger, flash/WLED, regulators, BIF, ADC/fuel gauge, speaker, and IRQ. Risks include high address base assumptions, large sparse register map, write hazards to OTP/test/debug registers, and matching four IRQ banks correctly. Test signals include regmap range tests including `0x8000+` addresses, IRQ status reads for all banks, charger/flash/WLED fault tests, regulator access tests, and AUXADC/FGADC reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/core.h

This MT6357 core header defines top-level interrupt group indexes, flat IRQ numbers, group base/bit-count macros, and a `MT6357_TOP_GEN(sp)` initializer macro for MediaTek PMIC IRQ descriptors. Groups include buck, LDO, PSC, SCK, BM, HK, XPP, audio, and misc top status shifts. IRQs cover regulator over-current/pre-over-current events, power/home keys, charger detect and voltage/baton/watchdog events, RTC, fuel-gauge/battery/auxadc events, audio/accessory detect, and SPI command alert.

Control flow is encoded in `MT6357_TOP_GEN(sp)`: IRQ table definitions can instantiate per-group metadata with hwirq base, number of interrupt registers derived from `MTK_PMIC_REG_WIDTH`, enable/status registers, shifts, and top-status offset. The MFD IRQ core uses that metadata to enable, mask, and read grouped interrupts. State is hardware interrupt top/status/mask data; this header stores no runtime state.

Dependencies include MT6357 register definitions for symbols such as `MT6357_BUCK_TOP_INT_CON0` and `MT6357_BUCK_TOP_INT_STATUS0`, the MediaTek PMIC IRQ type that has `.hwirq_base`, `.num_int_regs`, `.en_reg`, `.sta_reg`, and `.top_offset` fields, and `MTK_PMIC_REG_WIDTH`. Risks include macro token-pasting hiding missing register symbols until compile time, group bit counts requiring correct inclusive arithmetic, and sparse IRQ numbering. Test signals include compile coverage for all `MT6357_TOP_GEN()` uses, IRQ group registration count, key/charger/RTC/audio interrupt delivery, and over-current fault injection for buck/LDO groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/core.h -->
