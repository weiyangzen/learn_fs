# subset-b-005881 Research

Grouped source research for Linux MFD headers covering ROHM, Samsung, Richtek, ST, TI, syscon, timer, and radio tuner support code. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd718x7.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd718x7.h

## Purpose

This 313-line header is the shared register, regulator, voltage, reset, and interrupt contract for ROHM BD71837/BD71847 PMIC family support. Regulator, RTC, power-key, IRQ, and poweroff drivers include it so numeric register addresses and bit masks stay aligned with the chip datasheet.

## Important APIs, Types, and Functions

It defines `BD718XX_BUCK1` through `BD718XX_LDO7`, `BD718XX_REGULATOR_AMOUNT`, BD71837-only register aliases, common `BD718XX_REG_*` addresses, voltage selector counts, regulator enable/vsel/ramp masks, voltage-monitor masks, IRQ IDs, software reset settings, poweroff transition values, and power-button timing enums. There are no functions.

## Control Flow

No executable flow lives here. Runtime flow is table-driven: child drivers choose a regulator or IRQ enum, then use regmap writes/updates against these addresses and masks. Poweroff and reset code writes transition and reset fields using the protected mask values.

## State and Persistence Behavior

The file owns no storage. The represented state persists in PMIC registers, including OTP revision, reset source, power state, voltage selectors, monitor enables, interrupt latches, and lock bits. `REGLOCK_*` definitions are safety-critical because they gate writes to power sequence and regulator fields.

## Dependencies and Integration Points

It includes `rohm-generic.h` and `regmap.h`. Integration points are the ROHM MFD core, regulator framework, power/reset paths, regmap IRQ setup, and device-tree-configured DVS levels.

## Risks and Edge Cases

Variant-specific BD71837 and BD71847 definitions are interleaved; using a BD71837-only register on BD71847, or vice versa, would silently program the wrong address. Reset writes are especially risky because the comment explains bit 0 triggers reset and must not be copied from a read-modify-write source value.

## Test Signals

Build coverage for BD718xx MFD/regulator/RTC/poweroff drivers, regmap field tests for enable/vsel/ramp masks, IRQ mask-to-enum validation, and board boot/suspend/power-key tests that verify no unintended reset or regulator lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd718x7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd72720.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd72720.h

## Purpose

This 634-line header is the complete public register and IRQ map for the ROHM BD72720 PMIC. It spans regulator rails, GPIOs, RTC, power-state logic, charger, voltage monitor, coulomb counter, alarm, and interrupt status/source/mask registers across two I2C slave addresses.

## Important APIs, Types, and Functions

The file defines regulator IDs for 11 bucks and 11 LDOs, a large IRQ enum beginning with GPIO parent IRQs for device-tree xlate convenience, interrupt bit masks, common-register addresses behind I2C address `0x4b`, charger/monitor/counter registers behind address `0x4c` using `BD72720_I2C4C_ADDR_OFFSET`, GPIO IRQ type and drive masks, DVS state enable masks, voltage selector masks, RTC range markers, and detection bits such as `BD72720_MASK_DCIN_DET`.

## Control Flow

There is no local code flow. The MFD core and child drivers use the register enum as a logical address space and let regmap translate accesses. Interrupt handling follows the documented `_STAT` versus `_SRC` split: `_STAT` reports and acknowledges line events, while `_SRC` reflects current functional state.

## State and Persistence Behavior

All state is hardware-backed: DVS rail selections, GPIO modes, RTC time/alarm values, charger state, sampled voltage/current/coulomb data, interrupt enable/status/source fields, and alarm thresholds. The artificial `0x100` offset prevents address collisions between the two physical I2C register banks in one logical map.

## Dependencies and Integration Points

It includes `regmap.h` and integrates with ROHM MFD core probing, regulator DVS tables, GPIO/IRQ-controller child devices, RTC support, power-supply/charger code, fuel-gauge-like monitoring, and device-tree interrupt consumers attached to PMIC GPIO inputs.

## Risks and Edge Cases

The first two IRQ numbers are intentionally GPIO inputs, not register-order IRQs; changing this order would break device-tree consumers. Confusing `_STAT` and `_SRC` can either fail to ack IRQs or report stale functional state. Register offset handling must be consistent or charger-bank operations will hit common-bank registers.

## Test Signals

Compile coverage for all BD72720 children, IRQ domain xlate tests for GPIO1/GPIO2, regmap range tests for the `0x4c` offset, RTC alarm smoke tests, charger/power-supply property checks, and hardware tests for DVS and GPIO interrupt polarity programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd72720.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd957x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd957x.h

## Purpose

This 140-line header defines the ROHM BD957x/BD9576 PMIC regulator IDs, interrupt topology, watchdog, regulator trigger, voltage tuning, and fault threshold registers. It is mainly consumed by MFD, regulator, watchdog, and interrupt child drivers.

## Important APIs, Types, and Functions

It exports regulator IDs `BD957X_VD50` through `BD957X_VOUTS1`, top-level BD9576 IRQ IDs, `IRQS_SILENT_MS`, main and sub interrupt register addresses/masks, valid masks for under/over-voltage detection, watchdog config, power trigger registers, regulator enable/disable values, tune registers, OVD/UVD threshold registers, over-current warning/protection registers, and `BD957X_MAX_REGISTER`.

## Control Flow

No code executes here. The long comment describes expected IRQ flow: regmap-irq handles only the main status register, while sub-drivers inspect fine-grained fault status and may disable an IRQ briefly before delayed re-enable to avoid loops from level-asserted fault lines.

## State and Persistence Behavior

Runtime state is stored in PMIC status, mask, watchdog, trigger, and voltage registers. Interrupt state can persist while a hardware fault remains present, so sub-device handlers must acknowledge and clear the condition before enabling the line again.

## Dependencies and Integration Points

The header depends on common kernel bit macros and is integrated with regmap IRQ handling, regulator fault reporting, watchdog configuration, and power sequencing for BD957x platforms.

## Risks and Edge Cases

Fine-grained IRQs are only partly maskable and the hardware line remains asserted until the physical condition clears. Incorrect mask values can create interrupt storms or hide voltage/thermal faults. Tune and threshold masks differ by rail width.

## Test Signals

Build tests for BD957x MFD/regulator/watchdog drivers, interrupt storm regression tests for thermal/fault IRQs, regmap mask assertions for each fault class, and hardware fault-injection or lab tests that verify delayed IRQ re-enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd957x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96801.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96801.h

## Purpose

This 217-line header defines ROHM BD96801 PMIC control, watchdog, state, IRQ, mask, and regulator fault bit assignments. It distinguishes the chip's two physical interrupt lines, `INTB` and `ERRB`, and maps system, buck, and LDO event sources.

## Important APIs, Types, and Functions

The file defines control registers such as `BD96801_REG_WD_CONF`, `BD96801_REG_PMIC_STATE`, lock/unlock values, main/status/mask register ranges, `BD96801_MAX_REGISTER`, system error masks, ERRB IRQ enum values for system/buck/LDO shutdown and protection faults, INTB IRQ enum values for warning/detection events, and reusable buck/LDO IRQ masks.

## Control Flow

No local flow exists. The MFD IRQ setup uses the main register to discover which ERRB or INTB group is active, then regmap-irq or subdevice handlers resolve specific buck/LDO/system bits from the grouped status registers.

## State and Persistence Behavior

State persists in PMIC registers, including watchdog timeout/status, boot overtime, PMIC/external state, masked interrupt groups, lock state, and fault latches. Unlock/lock values gate protected writes.

## Dependencies and Integration Points

It integrates with ROHM MFD core, watchdog, regulator, and interrupt handling. Child regulators use the common buck/LDO masks for over-current, over/under-voltage, thermal warning, and shutdown classification.

## Risks and Edge Cases

ERRB and INTB IRQ spaces are separate enums; mixing them would mislabel faults. Protected register writes must respect lock sequencing. Gaps and group boundaries in the register map mean naive contiguous IRQ mapping can misroute events.

## Test Signals

Build coverage, regmap-irq mapping tests for each ERRB/INTB register group, watchdog configuration smoke tests, lock/unlock write tests, and regulator fault injection validating that warnings versus shutdown faults are reported distinctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96801.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96802.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96802.h

## Purpose

This 74-line header supplies BD96802-specific IRQ numbering for a reduced digital interface derived from BD96801. It avoids gaps in IRQ numbers for a chip variant with fewer buck/LDO blocks.

## Important APIs, Types, and Functions

It defines two enums: BD96802 ERRB IRQs for system errors and BUCK1/BUCK2 protection/shutdown faults, and BD96802 INTB IRQs for system warnings and BUCK1/BUCK2 over-current, voltage, and thermal-warning conditions. It intentionally reuses BD96801 register/mask definitions elsewhere.

## Control Flow

There is no executable flow. MFD and IRQ code select this compact enum when probing BD96802, while using BD96801-compatible register addresses for the reduced hardware block.

## State and Persistence Behavior

The header owns no state. It describes hardware IRQ latches that persist in BD96802 ERRB/INTB registers until acknowledged and cleared.

## Dependencies and Integration Points

It integrates with the BD96801-style ROHM MFD/IRQ implementation and regulator fault reporting, while exposing variant-correct IRQ numbers to child devices and device-tree interrupt consumers.

## Risks and Edge Cases

Using BD96801 IRQ numbering on BD96802 would create holes or mismatched Linux IRQ numbers. Assuming absent buck/LDO groups exist would cause invalid register reads or unhandled interrupt bits.

## Test Signals

Compile coverage for BD96802 probe paths, IRQ count/order validation against the regmap-irq tables, and hardware or emulated interrupt tests for both ERRB and INTB lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96802.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-generic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-generic.h

## Purpose

This 91-line header is the shared ROHM PMIC support contract. It defines chip IDs, a minimal regmap device wrapper, and generic dynamic-voltage-scaling descriptors used by ROHM regulator drivers across several PMIC families.

## Important APIs, Types, and Functions

Important exports include `enum rohm_chip_type`, `struct rohm_regmap_dev`, DVS level bit definitions for run/idle/suspend/LPSR/SNVS, `struct rohm_dvs_config`, and regulator helper prototypes `rohm_regulator_set_dvs_levels()` and `rohm_regulator_set_voltage_sel_restricted()` when `CONFIG_REGULATOR_ROHM` is enabled.

## Control Flow

No flow executes in the header. At runtime, ROHM regulator probe code reads device-tree DVS properties, uses `rohm_dvs_config` to map each state to register/mask/on-mask fields, and programs the PMIC through regmap.

## State and Persistence Behavior

`rohm_dvs_config` is static description data; actual state persists in PMIC voltage and enable registers. `ROHM_DVS_LEVEL_UNKNOWN` flags unsupported or unparsed levels.

## Dependencies and Integration Points

It includes `regmap.h` and `regulator/driver.h`, and integrates ROHM MFD cores with regulator framework descriptions and device-tree power-state configuration.

## Risks and Edge Cases

Conditional prototypes mean users must compile with regulator support or guard calls. Incorrect `level_map` or mask values can program a voltage for the wrong suspend/run state.

## Test Signals

ROHM regulator build tests with and without `CONFIG_REGULATOR_ROHM`, device-tree DVS parsing tests, and board suspend/resume tests verifying state-specific voltage and enable values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-shared.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-shared.h

## Purpose

This 21-line header contains shared RTC bit masks for ROHM BD70528 and BD71828 devices. It centralizes BCD field widths and alarm-enable masks used by ROHM RTC code.

## Important APIs, Types, and Functions

It defines masks for seconds, minutes, 24-hour mode, PM flag, hour, day, week, month, year, and alarm enable fields: `BD70528_MASK_RTC_SEC` through `BD70528_MASK_ALM_EN`. There are no types or functions.

## Control Flow

There is no flow. RTC drivers use these masks while reading or writing time/alarm registers through regmap.

## State and Persistence Behavior

The represented state persists in PMIC RTC registers and alarm control bits. The header itself has no storage.

## Dependencies and Integration Points

It is a leaf include for ROHM RTC implementations shared across related chips.

## Risks and Edge Cases

Misapplying the 24-hour and PM masks can corrupt hour conversion. Alarm enable mask width must match the chip's alarm register layout.

## Test Signals

RTC set/get tests across 12/24-hour values, alarm enable/disable tests, and BCD boundary tests for day/month/year field masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rsmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rsmu.h

## Purpose

This 38-line header is the shared core interface for Renesas Synchronization Management Unit devices, covering ClockMatrix, Sabre, and SnowLotus variants.

## Important APIs, Types, and Functions

It defines maximum bus transfer sizes, `enum rsmu_type` values for supported device families, and `struct rsmu_ddata`, which carries the backing device, regmap, serialization mutex, type, and current page for I2C/SPI driver use.

## Control Flow

No executable flow is defined. Subdevices receive `rsmu_ddata`, lock around multi-register transactions, use regmap for bus access, and rely on the parent to manage page selection.

## State and Persistence Behavior

`struct rsmu_ddata` holds runtime shared state. The mutex serializes bus/page-sensitive operations, and `page` tracks parent-driver paging state; hardware clock/synchronization state remains in the SMU.

## Dependencies and Integration Points

The header integrates Renesas MFD parent drivers with clock/PTP/synchronization child devices using Linux `device`, `regmap`, and `mutex` infrastructure.

## Risks and Edge Cases

Missing the lock around paged accesses can interleave transactions from subdevices and target the wrong page. Transfer sizes must respect the 255-byte read/write limits.

## Test Signals

Build coverage for I2C/SPI RSMU drivers, concurrent subdevice access tests, page-switch regression tests, and max-length regmap transfer checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rsmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rt5033-private.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rt5033-private.h

## Purpose

This 276-line private Richtek RT5033 header defines charger, regulator, flash LED, fuel-gauge, IRQ, and voltage/current conversion constants for the RT5033 MFD family.

## Important APIs, Types, and Functions

It exports `enum rt5033_reg`, charger status/control masks, charger mode/timer/current/voltage limit constants, regulator voltage ranges for buck/LDO/safe LDO, `enum rt5033_fuel_reg`, fuel-gauge present bit, PMIC IRQ masks, and charger model/manufacturer strings. There are no function declarations.

## Control Flow

The header is table data for child driver flow. Charger code decodes status registers, programs AICR/MIVR/timer/mode/current/voltage fields, regulator code maps selector values to microvolts, and fuel-gauge code addresses OCV/VBAT/SOC/config registers.

## State and Persistence Behavior

State persists in RT5033 registers: charger state, current/voltage limits, timer enables, OTG/high-impedance/UUG mode bits, regulator enables/vsel fields, fuel-gauge measurements, and IRQ status/mask bits.

## Dependencies and Integration Points

It is consumed by RT5033 MFD, charger, regulator, LED, fuel-gauge/power-supply, and IRQ handling code. It pairs with `rt5033.h` for the public parent-device structure.

## Risks and Edge Cases

Many constants encode hardware units and selector caps; off-by-one conversions can overprogram charge current or voltage. Charger current limiting distinguishes input-current AICR from fast-charge current. Reserved register holes must not be treated as contiguous writable areas.

## Test Signals

Charger property conversion tests, regulator selector-to-voltage tests, regmap reserved-register range checks, IRQ mask tests, and hardware charge/discharge tests for status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rt5033-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rt5033.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rt5033.h

## Purpose

This 34-line public RT5033 MFD header defines the parent device state and regulator IDs shared by RT5033 child drivers.

## Important APIs, Types, and Functions

It declares `enum rt5033_regulators` for buck, LDO, and safe LDO rails, and `struct rt5033_dev` containing `dev`, `regmap`, `regmap_irq_chip_data`, IRQ number, and wakeup flag. It includes regulator consumer, I2C, and regmap headers.

## Control Flow

No code executes here. The MFD core initializes `rt5033_dev`, populates regmap and IRQ data, and child devices use those fields for register access and wakeup-aware interrupt handling.

## State and Persistence Behavior

The struct holds runtime driver state; persistent power and IRQ state remains in the RT5033 hardware.

## Dependencies and Integration Points

It integrates the RT5033 MFD core with regulator, charger, LED, and fuel-gauge child drivers through shared parent data.

## Risks and Edge Cases

Children assume the parent filled `regmap` and `irq_data` before probing. Wakeup flag handling must match system suspend requirements or charger/PMIC interrupts may be missed.

## Test Signals

Probe/remove build tests, child-driver probe ordering checks, suspend wakeup tests, and regmap/IRQ data null-check paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rt5033.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rz-mtu3.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rz-mtu3.h

## Purpose

This 191-line header defines shared register offsets, bitfields, channel state, and access helpers for Renesas RZ MTU3 multi-function timer channels.

## Important APIs, Types, and Functions

It contains shared/channel-specific register offsets for 8-, 16-, and 32-bit accesses, mode/control bitfield macros, `enum rz_mtu3_channels`, `struct rz_mtu3_channel`, `struct rz_mtu3`, inline `rz_mtu3_request_channel()`/`rz_mtu3_release_channel()`, enable/disable/status prototypes, and read/write/update helpers for channel and shared registers.

## Control Flow

The inline request path locks the channel mutex, checks `is_busy`, marks the channel busy, and returns success or false. Release clears the flag under the same lock. Runtime child drivers then enable the channel and perform typed register accesses through the parent implementation.

## State and Persistence Behavior

`is_busy` is driver-owned allocation state; `struct rz_mtu3` owns the module clock and channel array. Timer count, compare, output, mode, and shared start registers persist in hardware while the module is powered.

## Dependencies and Integration Points

It includes clock, device, and mutex headers. Integration points include PWM, counter, clockevent, and timer child drivers that share MTU3 channels without colliding.

## Risks and Edge Cases

Channel 5 has different register layout and must use MTU5-specific offsets. Callers must release channels on failure paths. Mixed-width register access must match the hardware register size.

## Test Signals

Build coverage for MTU3 children, request/release concurrency tests, register offset tests for channel 5 versus others, and hardware PWM/counter enable-disable smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rz-mtu3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/core.h

## Purpose

This 144-line header is the shared Samsung S2M/S5M PMIC core contract. It defines common voltage/ramp constants, supported device types, parent-device data, platform data, regulator init data, and operation modes.

## Important APIs, Types, and Functions

Exports include minimum voltage and step macros, `enum sec_device_type`, `struct sec_pmic_dev`, `struct sec_platform_data`, `struct sec_regulator_data`, `struct sec_opmode_data`, and `enum sec_opmode`. Platform data includes regulator arrays, GPIO DVS tables, buck voltage tables, ramp settings, shutdown behavior, and WRSTBI disable configuration.

## Control Flow

The header has no executable flow. MFD probe code fills `sec_pmic_dev` and platform data from board files or device tree; regulator drivers consume opmode and DVS data to program each PMIC variant.

## State and Persistence Behavior

Driver runtime state lives in `sec_pmic_dev` and platform data. Hardware state persists in PMIC registers, GPIO DVS pins, buck/LDO operation mode fields, and warm-reset behavior.

## Dependencies and Integration Points

It forward-declares GPIO descriptors and integrates Samsung MFD core, regulator drivers, RTC/IRQ support, I2C regmap access, and platform/device-tree configuration.

## Risks and Edge Cases

Platform data contains variant-sensitive arrays and fixed-size buck GPIO/DVS fields; mismatched counts or indexes can program the wrong rail. Manual poweroff and WRSTBI settings affect shutdown and reset behavior.

## Test Signals

Build tests across supported Samsung PMIC variants, platform-data/device-tree parsing tests, regulator DVS table validation, suspend/reset behavior tests, and probe ordering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/irq.h

## Purpose

This 455-line header defines interrupt numbers and bit masks for Samsung S2MPA01, S2MPG10, S2MPG11, S2MPS11, S2MPS14, S2MPU02, S2MPU05, and S5M8767 PMIC families.

## Important APIs, Types, and Functions

It exports per-chip IRQ enums such as `s2mpa01_irq`, `s2mpg10_irq`, `s2mpg11_irq`, `s2mps11_irq`, `s2mps14_irq`, `s2mpu02_irq`, `s2mpu05_irq`, and `s5m8767_irq`, plus masks for power-key edges, cable/JIG events, RTC alarms/periodic events, thermal thresholds, watchdog/reset events, over-current warnings, power-meter warnings, NTC warnings, and top-level common IRQ sources.

## Control Flow

There is no executable flow. Samsung IRQ controller code maps status register bits into these Linux IRQ indexes, applies masks through per-chip mask registers, and exposes child interrupts to RTC, regulator, and power-key clients.

## State and Persistence Behavior

The represented state persists in PMIC interrupt status and mask registers. The enum ordering is part of the Linux IRQ ABI for subdrivers, and `*_IRQ_NR` values indicate chip-specific table sizes.

## Dependencies and Integration Points

It integrates Samsung MFD interrupt chips with power-key/input, RTC alarms, regulator thermal/OCP warnings, power-meter/NTC monitoring, and wakeup handling.

## Risks and Edge Cases

Several chips reuse masks but differ in enum order or event names. Inline mask definitions inside enum blocks must stay aligned with adjacent status registers. Incorrect IRQ count values can truncate or overrun regmap-irq tables.

## Test Signals

Regmap-irq table build tests for every chip, IRQ number-to-mask unit tests, wakeup interrupt tests for power-key/RTC, and fault-injection tests for thermal/OCP events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/rtc.h

## Purpose

This 170-line header defines Samsung S5M/S2MPS/S2MPG RTC register layouts and common bitfields for time, alarm, update, 12/24-hour, WTSR, and SMPL control.

## Important APIs, Types, and Functions

It defines `enum s5m_rtc_reg`, `enum s2mps_rtc_reg`, `enum s2mpg10_rtc_reg`, RTC I2C address, hour/alarm status bits, BCD/24-hour mode masks, per-variant update request bits, S5M update delay values, alarm enable mask, SMPL/WTSR enable masks, and S2MPG10 cold reset/timer fields.

## Control Flow

No local flow exists. RTC drivers use these enums to select register offsets, write time/alarm values, request update latching with the correct UDR/AUDR/WUDR bits, and enable wakeup/reset features.

## State and Persistence Behavior

RTC time, alarms, update latches, mode flags, WTSR, and SMPL settings persist in PMIC RTC registers, often on an RTC-specific I2C address.

## Dependencies and Integration Points

It integrates Samsung MFD regmap access with Linux RTC class drivers and PMIC wakeup/reset behavior.

## Risks and Edge Cases

Update bits differ between S2MPS13, S2MPS15, and older variants. Hour mode and PM bits need careful conversion. WTSR/SMPL can reset or power-cycle systems if configured incorrectly.

## Test Signals

RTC set/read/alarm tests for each layout, BCD and 12/24-hour conversion tests, update-bit timing tests, and suspend wake alarm validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpa01.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpa01.h

## Purpose

This 175-line header maps S2MPA01 PMIC registers, regulator IDs, voltage selector masks, enable fields, and buck ramp controls.

## Important APIs, Types, and Functions

It defines `enum s2mpa01_reg`, `enum s2mpa01_regulators` for 26 LDOs and 10 bucks, LDO/buck vsel masks and voltage counts, enable mask/shift, default ramp delay, per-buck ramp shift values, ramp enable shifts, and PMIC enable shift.

## Control Flow

No flow executes here. The S2MPA01 regulator driver indexes register enums and regulator IDs, then programs enable, voltage, and ramp fields through regmap.

## State and Persistence Behavior

Regulator voltage, enable, ramp, DVS pointer/data, OTP, status, and interrupt mask state persists in the PMIC. The header itself is compile-time ABI.

## Dependencies and Integration Points

It integrates with Samsung core, IRQ, RTC, and regulator code for S2MPA01 devices.

## Risks and Edge Cases

The large register enum includes reserved slots; drivers must not assume every entry is a usable regulator register. Ramp shift values differ by buck grouping.

## Test Signals

Regulator descriptor tests for all 36 rails, selector bounds tests, ramp-delay programming tests, and build coverage with Samsung MFD IRQ/RTC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpa01.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg10.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg10.h

## Purpose

This 478-line header defines S2MPG10 common, PMIC, power-meter, external-control, and regulator identifier maps for a modern Samsung PMIC.

## Important APIs, Types, and Functions

It exports common-register and interrupt-source definitions, a large PMIC register enum covering interrupts, status, buck/LDO controls, ultrasonic mode, discharge, ramp, DVS sync, sequencing, GPIO, OCP, PIF, fault output, and LDO sense registers; PCTRLSEL external-control encodings; meter registers for accumulation/filter/power warning data; and regulator IDs for 10 bucks and 31 LDOs.

## Control Flow

No executable flow exists. The MFD core addresses typed register windows, regulator code consumes control/output registers and external-control selectors, and monitoring code reads meter/accumulator registers.

## State and Persistence Behavior

Hardware state includes interrupt masks/status, rail voltages, external control source selection, DVS sequencing, GPIO configuration, power meter accumulators, OCP warning thresholds, and fault output settings.

## Dependencies and Integration Points

It integrates Samsung MFD, regulator, interrupt, power-meter/hwmon-like monitoring, GPIO, and sequencing support. It also pairs with `samsung/irq.h` for S2MPG10 IRQ names.

## Risks and Edge Cases

The PMIC has multiple logical register types; mixing common, PMIC, and meter spaces will target the wrong hardware area. External-control selector values are rail-specific, especially LDO20M.

## Test Signals

Compile coverage, regulator table size checks against `S2MPG10_REGULATOR_MAX`, meter register read tests, IRQ source routing tests, and external-control mode tests for PCTRLSEL/DCTRLSEL rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg11.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg11.h

## Purpose

This 434-line header defines S2MPG11 common, PMIC, meter, external-control, and regulator identifiers for another Samsung PMIC generation.

## Important APIs, Types, and Functions

It defines common registers and interrupt source masks, PMIC registers for interrupts/status, buck/buckboost/LDO controls, ultrasonic modes, DVS, sequencing, GPIO, OCP, PIF, and fault output, PCTRLSEL values for PWREN/MIF/AP/G3D/AOC/UFS controls, meter registers with power and NTC warning/filter data, and regulator IDs for buckboost, 10 bucks, BUCKD, BUCKA, and 15 LDOs.

## Control Flow

The header has no executable flow. Variant-specific Samsung MFD and regulator code use its register maps to configure rail state, sequencing, interrupts, and monitoring.

## State and Persistence Behavior

State persists in PMIC registers for rail configuration, external controls, IRQs, sequencing, OCP, NTC and power-meter samples, and fault output.

## Dependencies and Integration Points

It integrates with Samsung core and IRQ headers, regulator drivers, meter/thermal warning consumers, and GPIO/external power-control logic.

## Risks and Edge Cases

The register enum deliberately skips holes; assuming contiguous hardware at commented gaps is unsafe. S2MPG11 regulator and IRQ names differ from S2MPG10 despite similar structure.

## Test Signals

Variant probe tests, regulator ID count validation, meter/NTC warning register tests, IRQ mask mapping tests, and external-control selector validation on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps11.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps11.h

## Purpose

This 198-line header maps S2MPS11 PMIC registers and regulator IDs, plus selector, enable, voltage-count, ramp, and power-hold controls.

## Important APIs, Types, and Functions

It defines `enum s2mps11_reg`, `enum s2mps11_regulators` for 38 LDOs and 10 bucks, LDO/buck/buck9 vsel masks, voltage counts for buck groups, ramp delay, `S2MPS11_CTRL1_PWRHOLD_MASK`, per-buck ramp shift and ramp-enable shifts, and PMIC enable shift.

## Control Flow

No code flow exists. Regulator code indexes the register map by rail ID, then programs enable, voltage selector, ramp, and suspend/PWREN behavior through regmap.

## State and Persistence Behavior

Voltage, enable, ramp, PWRHOLD, interrupt, status, OTP, and DVS register state persists in the PMIC.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, shared IRQ/RTC definitions, and shutdown logic through PWRHOLD.

## Risks and Edge Cases

Buck voltage counts vary by buck group; using one selector range for all bucks is wrong. The comment notes suspend enable bits are shared with S2MPS14 definitions.

## Test Signals

Regulator descriptor bounds tests, PWRHOLD shutdown tests, ramp programming checks, and compile tests for S2MPS11 regulator/IRQ/RTC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps13.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps13.h

## Purpose

This 177-line header defines S2MPS13 PMIC register and regulator IDs, default ramp behavior, and warm-reset control mask.

## Important APIs, Types, and Functions

It exports `enum s2mps13_reg`, `enum s2mps13_regulators` for 40 LDOs, 10 bucks, and a buckboost rail, plus `S2MPS13_BUCK_RAMP_DELAY` and `S2MPS13_REG_WRSTBI_MASK`.

## Control Flow

No local flow exists. Regulator code uses rail IDs and register offsets to configure buck/LDO outputs, while core code can control WRSTBI behavior using the mask.

## State and Persistence Behavior

Regulator output, ramp, LDO DVS/discharge, WRSTBI, interrupt, status, and control state persist in PMIC registers.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator descriptors, shared IRQ definitions, and reset/warm-reset policy.

## Risks and Edge Cases

The file documents that datasheet ramp-control register details are unclear, so drivers rely on a default ramp delay. Changing that assumption should be validated on hardware.

## Test Signals

Regulator table size tests, default-ramp behavior checks, WRSTBI mask tests, and hardware voltage-transition measurements where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps13.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps14.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps14.h

## Purpose

This 134-line header defines S2MPS14 PMIC registers, regulator IDs, selector masks, enable semantics, default ramp delay, and external/suspend control encodings.

## Important APIs, Types, and Functions

It declares `enum s2mps14_reg`, `enum s2mps14_regulators` for 25 LDOs and 5 bucks, buck start selector values, ramp delay, LDO/buck vsel masks/counts, enable mask/shift, `S2MPS14_ENABLE_SUSPEND`, and `S2MPS14_ENABLE_EXT_CONTROL`.

## Control Flow

No executable flow exists. The regulator driver maps rail IDs to register controls and uses the enable mode encodings to support normal, suspend/PWREN, or external-control operation.

## State and Persistence Behavior

Regulator voltage, enable mode, discharge, WRSTBI, RTC control, interrupt, and status values persist in PMIC registers.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, shared IRQ/RTC handling, and external control pins such as LDO10EN/EMMCEN.

## Risks and Edge Cases

External-control enable value is encoded as zero in the enable field; code must not treat zero as necessarily disabled. Buck start selectors differ between BUCK4 and other bucks.

## Test Signals

Regulator mode tests for normal/suspend/external enable, selector bounds tests, and suspend-resume tests where PWREN controls rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps14.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps15.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps15.h

## Purpose

This 149-line header maps S2MPS15 registers and regulator IDs and provides common selector and enable field definitions.

## Important APIs, Types, and Functions

It exports `enum s2mps15_reg`, `enum s2mps15_regulators` for 27 LDOs and 11 bucks, LDO/buck vsel masks, enable shift/mask, and selector counts for LDO and buck rails.

## Control Flow

No flow executes. The S2MPS15 regulator driver uses these IDs and masks to configure rail voltage and enable state through regmap.

## State and Persistence Behavior

PMIC hardware stores interrupt, status, buck/LDO control, buckboost, ramp, LDO DVS, and discharge state. The header is compile-time layout state.

## Dependencies and Integration Points

It integrates Samsung MFD core, regulator framework, and shared IRQ/RTC definitions for S2MPS15 devices.

## Risks and Edge Cases

Buckboost registers are present in the register enum but not a separately named regulator ID here. Selector ranges are generic and still need per-rail descriptor constraints.

## Test Signals

Regulator ID count checks, selector range tests, probe/build coverage, and board voltage enable/disable smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu02.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu02.h

## Purpose

This 189-line header defines S2MPU02 registers, regulator IDs, voltage constraints, selector masks, suspend enable encodings, and buck ramp fields.

## Important APIs, Types, and Functions

It exports `enum S2MPU02_reg`, `enum S2MPU02_regulators` for 28 LDOs and 7 bucks, per-buck minimum voltage/step/start selector constants, LDO group voltage constants, LDO/buck vsel masks and counts, enable mask/shift, suspend enable/disable encodings, and ramp shift/mask definitions for BUCK1-4.

## Control Flow

There is no executable flow. Regulator descriptors use these constants to compute selector ranges and program voltage, enable, suspend, and ramp fields.

## State and Persistence Behavior

PMIC registers persist regulator control, DVS, warm reset, interrupt, status, and ramp state. Driver-owned state is elsewhere.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, and shared IRQ/RTC support for S2MPU02.

## Risks and Edge Cases

Voltage ranges vary significantly by buck and LDO group. `S2MPU02_DISABLE_SUSPEND` encodes `0x11 << 6`, which exceeds an 8-bit field if treated naively; consumers need to match existing driver semantics.

## Test Signals

Regulator conversion tests per buck/LDO group, suspend enable tests, ramp field tests, and build coverage for S2MPU02 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu02.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu05.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu05.h

## Purpose

This 183-line header defines S2MPU05 PMIC register and regulator IDs plus enable timing, voltage range, ramp, selector, and enable masks.

## Important APIs, Types, and Functions

It declares `enum S2MPU05_reg`, `enum S2MPU05_regulators` for 35 LDOs and 5 bucks, software enable mask, per-buck enable times, LDO/buck minimums and steps, ramp delay, enable shift/mask, vsel masks/counts, and PMIC enable shift.

## Control Flow

No code executes. Regulator drivers use the constants to describe enable delays, voltage maps, and regmap update masks for each rail.

## State and Persistence Behavior

State persists in PMIC registers for interrupts, status, control, OTP, timing, buck/LDO output, ramp, discharge, TCXO control, and MIF selection.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, and S2MPU05 IRQ definitions in `samsung/irq.h`.

## Risks and Edge Cases

Enable timing differs by buck and must be honored to avoid early consumer access. Mixed LDO/buck voltage step groups require careful regulator descriptor selection.

## Test Signals

Enable-time tests, regulator voltage conversion tests, probe/build coverage, and suspend/resume tests for TCXO or MIF-related rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu05.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s5m8767.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s5m8767.h

## Purpose

This 205-line header defines S5M8767 PMIC register IDs, regulator IDs, GPIO-controlled enable field, and buck DVS ramp values.

## Important APIs, Types, and Functions

It exports `enum s5m8767_reg`, `enum s5m8767_regulators` for 28 LDOs, 9 bucks, and 32 kHz enables, enable control shift/mask and GPIO-control value, `enum s5m8767_dvs_buck_ramp_values`, and DVS ramp shift/mask.

## Control Flow

No executable flow. Regulator and clock output drivers use register IDs and masks to configure enable modes, DVS voltage slots, and ramp speed.

## State and Persistence Behavior

PMIC state persists in interrupt/status, low-battery, DVS timer/ramp, buck/LDO, and clock output registers. GPIO-controlled enable settings depend on external pin state.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, shared IRQ/RTC handling, and 32 kHz clock consumers.

## Risks and Edge Cases

Buck2-4 each expose eight DVS registers; indexing mistakes can apply voltage to the wrong operating point. GPIO enable mode requires board pin configuration to match hardware.

## Test Signals

Regulator DVS slot tests, ramp encoding tests, GPIO enable-mode tests, 32 kHz output checks, and S5M8767 IRQ/RTC build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s5m8767.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sc27xx-pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/sc27xx-pmic.h

## Purpose

This 7-line header exposes one SC27xx PMIC helper for charger type detection.

## Important APIs, Types, and Functions

It declares `sprd_pmic_detect_charger_type(struct device *dev)`, returning `enum usb_charger_type`. The function is implemented outside this header.

## Control Flow

The header has no flow. Callers invoke the helper to ask the Spreadtrum PMIC layer to inspect charger state and return the detected USB charger type.

## State and Persistence Behavior

No state is stored in the header. Detected state comes from PMIC hardware and possibly charger-detection logic in the implementation.

## Dependencies and Integration Points

It integrates SC27xx PMIC support with USB charger/power-supply consumers. `struct device` and `enum usb_charger_type` are expected from included kernel context.

## Risks and Edge Cases

The prototype relies on external type declarations; include order must provide the USB charger enum. Detection may fail or return unknown depending on PMIC state.

## Test Signals

Compile tests for users of the helper, charger detection tests for supported cables, and error-path tests when PMIC access is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sc27xx-pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-core.h

## Purpose

This 531-line header is the central Silicon Labs Si476x radio tuner core interface. It defines core device state, locking helpers, frequency conversions, command argument/report types, command prototypes, status bits, interrupt flags, and property IDs.

## Important APIs, Types, and Functions

Key exports include chip/revision/cell enums, `enum si476x_power_state`, `struct si476x_core`, inline core lock/unlock and frequency conversion helpers, `struct si476x_func_info`, `struct si476x_power_down_args`, tune mode/smoothmetrics/injection-side enums, `struct si476x_rds_status_report`, RSQ/tune args, power/control/query command prototypes, I2C transfer API, interrupt/status bit enums, receiver property enums, RDS/audio property bit enums, and `devm_regmap_init_si476x()`.

## Control Flow

Core runtime flow is serialized by `cmd_lock`: clients power the chip, issue commands, wait on `command`/`tuning` queues for CTS/STC, and process IRQ or polling status. RDS flow uses a kfifo, wait queue, and work item to drain on-chip FIFO. Inline conversions switch frequency units by AM versus FM mode and V4L2 low-frequency units.

## State and Persistence Behavior

`struct si476x_core` holds persistent runtime state: I2C/regmap handles, MFD cells, user count, RDS FIFO, wait queues, atomic CTS/STC/is_alive flags, power-up parameters, power state, regulators, reset GPIO, pinmux, diversity mode, status monitor work, revision, and FIFO depth. Hardware retains tuner state and properties while powered.

## Dependencies and Integration Points

It includes kfifo, atomics, I2C, regmap, mutex, MFD core, V4L2, regulators, and the Si476x platform/report headers. Integration points are MFD child cells for radio/codec, V4L2 tuner operations, command transport, regmap, RDS handling, power management, and diversity support.

## Risks and Edge Cases

Command serialization is critical; bypassing `si476x_core_lock()` can interleave command/status transactions. Frequency conversion depends on current boot function. Polling mode has different RDS FIFO depth. `POWER_INCONSISTENT` prevents unsafe reuse after partial power-down.

## Test Signals

Build tests for radio/codec cells, command mock tests for CTS/STC waits, AM/FM/V4L2 frequency conversion tests, RDS FIFO drain tests, power-state transition tests, and property read/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-platform.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-platform.h

## Purpose

This 258-line header defines platform data, pinmux configuration, oscillator/power-up arguments, and phase diversity modes for Si476x radio tuners.

## Important APIs, Types, and Functions

It defines four selectable I2C addresses, enums for IQ, digital audio, IC link, analog audio, INTB/A1 pin functions, `struct si476x_pinmux`, oscillator bias/start/frequency/mode enums, `enum si476x_func`, `struct si476x_power_up_args`, `enum si476x_phase_diversity_mode`, and `struct si476x_platform_data`.

## Control Flow

No executable flow exists. Platform or device-tree data is converted into `si476x_platform_data`; core startup passes `power_up_parameters` to the POWER_UP command and configures pins through command helpers declared in `si476x-core.h`.

## State and Persistence Behavior

The structures store boot-time configuration for reset GPIO, power-up mode, oscillator settings, pin muxing, and diversity role. Hardware pin/function state persists while the tuner remains powered.

## Dependencies and Integration Points

It integrates board data with Si476x MFD core, command layer, audio interfaces, IRQ routing, IQ output, and multi-tuner diversity setups.

## Risks and Edge Cases

Pin function enum values are command ABI values, not arbitrary indexes. Wrong oscillator frequency or xmode can prevent boot. Diversity roles must match physical tuner wiring.

## Test Signals

Platform-data parsing tests, POWER_UP argument encoding tests, pin configuration command tests, I2C address probe tests, and diversity-mode hardware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-reports.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-reports.h

## Purpose

This 154-line header defines packed report structures returned by Si476x debug and command paths for received signal quality, audio/control filtering, AGC, and RDS block counts.

## Important APIs, Types, and Functions

It defines packed `struct si476x_rsq_status_report`, `struct si476x_acf_status_report`, `enum si476x_fmagc`, `struct si476x_agc_status_report`, and `struct si476x_rds_blockcount_report`.

## Control Flow

No flow executes. Command implementations fill these structures from raw device responses, and debugfs/V4L2 code interprets the decoded fields.

## State and Persistence Behavior

The structs are transient snapshots of tuner measurements: RSSI, SNR, multipath, AFC, antenna capacitance, RDS PI, blend/hicut/softmute, AGC gains, and RDS counts. They do not persist after the caller consumes them.

## Dependencies and Integration Points

It integrates Si476x command code with debugfs, V4L2 status reporting, and RDS/statistics consumers. Packed layout preserves command response ABI.

## Risks and Edge Cases

Packed layouts must match device response order and signedness. Several fields are poorly documented, so consumers should avoid inferring more than the command API guarantees.

## Test Signals

Response decoding tests using captured command bytes, packed-size checks, debugfs read tests, and V4L2 signal-quality reporting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/si476x-reports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sky81452.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/sky81452.h

## Purpose

This 18-line header defines platform data for the Skyworks SKY81452 MFD backlight/regulator device.

## Important APIs, Types, and Functions

It includes regulator machine constraints and defines `struct sky81452_platform_data` with a single `regulator_init_data` pointer.

## Control Flow

No local flow exists. The MFD core passes platform regulator constraints to child regulator code during probe.

## State and Persistence Behavior

The platform data is boot-time configuration. Hardware state is managed by SKY81452 child drivers and persists in device registers.

## Dependencies and Integration Points

It integrates SKY81452 MFD support with the regulator framework.

## Risks and Edge Cases

Missing or invalid regulator init data can leave supplies unconstrained. Since the structure is tiny, include-order and lifetime of platform data are the main concerns.

## Test Signals

Probe tests with and without regulator init data, regulator constraint validation, and build coverage for SKY81452 child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sky81452.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stm32-lptimer.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stm32-lptimer.h

## Purpose

This 99-line header defines STM32 low-power timer register offsets, bitfields, hardware feature bits, and parent data shared by LPTIMER child drivers.

## Important APIs, Types, and Functions

It exports `STM32_LPTIM_*` register offsets, ISR/ICR/IER/CR/CFGR/ARR/CCMR/HWCFGR/VERR bits, compare/update ready masks for MP15/MP25 variants, clock polarity constants, max auto-reload value, and `struct stm32_lptimer` with clock, regmap, encoder support, capture/compare channel count, and version.

## Control Flow

No code executes. Child drivers use parent-provided regmap and feature flags to configure counter, PWM, trigger, encoder, and capture/compare operations.

## State and Persistence Behavior

Hardware counter, compare, autoreload, interrupt, and configuration state persists in LPTIM registers. `struct stm32_lptimer` stores runtime parent-discovered capabilities.

## Dependencies and Integration Points

It includes clock and regmap headers and integrates STM32 MFD parent code with PWM, counter, trigger, and IIO/timer child devices.

## Risks and Edge Cases

MP25 adds different ready bits and extra compare/channel registers; drivers must check version/capabilities. Auto-reload is 16-bit. Update-ready bits must be observed before dependent writes.

## Test Signals

Build tests, variant capability detection tests, ARR/CMP update-ready timeout tests, encoder-channel tests, and PWM/counter hardware smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stm32-lptimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stm32-timers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stm32-timers.h

## Purpose

This 186-line header defines STM32 general-purpose timer register offsets, bitfields, DMA/IRQ metadata, parent state, and an optional DMA burst read helper.

## Important APIs, Types, and Functions

It exports `TIM_*` register offsets and bit macros, capture/compare and DMA request helper macros, hardware configuration fields, maximum prescaler/input-capture constants, encoder mode values, break/dead-time helpers, `enum stm32_timers_dmas`, `enum stm32_timers_irqs`, `struct stm32_timers_dma`, `struct stm32_timers`, and `stm32_timers_dma_burst_read()` with an `-ENODEV` stub when the MFD is not reachable.

## Control Flow

No direct runtime flow except the inline stub. Child drivers configure timer registers through regmap, optionally request DMA burst reads, and use IRQ/DMA metadata populated by the parent.

## State and Persistence Behavior

Timer counter, prescaler, auto-reload, capture/compare, DMA, break, trigger, and status state persists in hardware. Driver-owned DMA state includes completion, lock, active channel, and channel array.

## Dependencies and Integration Points

It integrates STM32 timer MFD parent with PWM, counter, IIO trigger/capture, DMAengine, interrupt, and regmap consumers.

## Risks and Edge Cases

Feature availability varies by timer IP and MP25 hardware fields. DMA burst access must serialize through the DMA lock and respect timeout. Channel helper macros assume 1-based channel numbers.

## Test Signals

Build tests with and without `CONFIG_MFD_STM32_TIMERS`, DMA burst read tests, PWM/capture/encoder hardware tests, IRQ line mapping tests, and register macro bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stm32-timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stmfx.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stmfx.h

## Purpose

This 122-line header defines register addresses, IRQ/function bits, runtime state, and function enable/disable APIs for the ST STMFX MFD expander.

## Important APIs, Types, and Functions

It exports chip, firmware, system, IRQ, GPIO, direction/type/pull, set/clear register addresses, max register, boot delay, chip/system/IRQ bitfields, `enum stmfx_irqs`, `enum stmfx_functions`, `struct stmfx`, and `stmfx_function_enable()`/`stmfx_function_disable()` prototypes.

## Control Flow

No code flow is local. The parent powers/resets the chip, waits boot time, enables functional blocks through system control bits, and IRQ code uses cached source-enable state under the bus lock.

## State and Persistence Behavior

`struct stmfx` stores regmap, regulator, IRQ domain, lock, IRQ source cache, and suspend/resume backups of SYS_CTRL and IRQ_OUT_PIN. Hardware persists GPIO state, IRQ enables/pending bits, and function enables.

## Dependencies and Integration Points

It includes regmap and integrates STMFX MFD parent with GPIO, touchscreen, IDD, IRQ domain, regulator, and suspend/resume support.

## Risks and Edge Cases

Function enables share SYS_CTRL bits; disabling one block must not disturb another. IRQ source cache must stay synchronized with hardware across suspend/resume. Boot delay is required after reset.

## Test Signals

Function enable reference tests, GPIO IRQ tests, suspend/resume backup-restore tests, boot-delay/probe tests, and regmap max-register checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stmfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stmpe.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stmpe.h

## Purpose

This 163-line header defines the STMicroelectronics STMPE MFD core interface for GPIO, keypad, touchscreen, ADC, PWM, and rotator variants.

## Important APIs, Types, and Functions

It exports ADC/touchscreen configuration macros, STMPE811 ADC registers, `enum stmpe_block`, `enum stmpe_partnum`, register-index enum `STMPE_IDX_*`, `struct stmpe`, bus access helpers `stmpe_reg_read/write`, block read/write, bit update, alt-function, enable/disable, `stmpe811_adc_common_init()`, and the GPIO no-request mask for STMPE811 touch.

## Control Flow

Parent and child drivers use `stmpe_enable()`/`disable()` to manage functional blocks and the bus access helpers to serialize register I/O. Variant-specific register offsets are accessed through `stmpe->regs` indexed by `STMPE_IDX_*`.

## State and Persistence Behavior

`struct stmpe` stores regulators, locks, device/client info, part/variant, register table, IRQ domain, GPIO count, IRQ enable caches, platform data, and ADC config. Hardware persists GPIO, IRQ, ADC, and block-enable state.

## Dependencies and Integration Points

It integrates STMPE MFD parent with I2C/SPI client info, GPIO, keypad, touchscreen, ADC, PWM, IRQ domain, and regulator support.

## Risks and Edge Cases

Register addresses differ by variant, so direct constants are unsafe except where explicitly variant-independent. IRQ enable caches must remain synchronized. Shared ADC settings affect touchscreen and ADC users.

## Test Signals

Variant probe tests, register-index table validation, block enable/disable tests, GPIO IRQ tests, ADC common init tests, and bus access error-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stmpe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stpmic1.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stpmic1.h

## Purpose

This 212-line header defines STPMIC1 PMIC register addresses, regulator/interrupt/control masks, pull-down settings, USB/boost controls, power-key behavior, and parent-device state.

## Important APIs, Types, and Functions

It exports status/control/register addresses from turn-on/off status through interrupt source registers, `PMIC_MAX_REGISTER_ADDRESS`, IRQ register count, voltage/enable/HPLP/standby masks, pull-down register/mask pairs for bucks/LDOs/VREF, ICC timeout masks, bypass and main control bits, pad control bits, VINLOW and USB/boost control bits, PONKEY turnoff fields, and `struct stpmic1`.

## Control Flow

No executable flow is in the header. Regulator, power, USB/boost, and IRQ code use these masks for regmap update/read/clear operations; MFD parent stores regmap and regmap-irq data in `struct stpmic1`.

## State and Persistence Behavior

PMIC hardware persists regulator voltage/enables, standby state, pull-down settings, mask/rank/reset behavior, interrupt pending/latch/mask/source state, watchdog, power-key, and USB boost/switch state.

## Dependencies and Integration Points

It integrates STPMIC1 MFD core with regulator, power/reset, USB boost, IRQ, regmap, and device wakeup handling.

## Risks and Edge Cases

Interrupt registers come in four parallel banks with pending, latch, clear, mask, set-mask, clear-mask, and source views; using the wrong bank can fail to clear or mask events. Power-key and software switch-off bits can shut down the system.

## Test Signals

Regulator mask tests, IRQ bank mapping tests, power-key turnoff tests, watchdog/boost smoke tests, and suspend/resume wakeup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stpmic1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stw481x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/stw481x.h

## Purpose

This 51-line header exposes shared STw481x PMIC register bits and parent state for ST-Ericsson/Linaro MFD children.

## Important APIs, Types, and Functions

It defines shared `STW_CONF1`, `STW_CONF2`, and `STW_VCORE_SLEEP` register addresses and masks for VMMC power/voltage, monitoring, wakeup, GPOs, and warning behavior, plus `struct stw481x` with I2C client and regmap.

## Control Flow

No code flow exists. Child drivers use the shared regmap to update shared configuration registers for regulators, MMC voltage, warning masks, and GPIO-like outputs.

## State and Persistence Behavior

Hardware persists VMMC/VAUX power-down and voltage selection, warning masks, GPO bits, and sleep voltage state. Runtime parent state holds the I2C/regmap handles.

## Dependencies and Integration Points

It integrates STw481x MFD support with I2C, regmap, regulator machine constraints, and bit operations.

## Risks and Edge Cases

Several registers are shared by more than one driver, so read-modify-write operations must preserve unrelated bits. VMMC voltage field values directly affect external card power.

## Test Signals

Regmap update-bit tests, MMC voltage selection tests, regulator child probe tests, and shared-register concurrency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/stw481x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sun4i-gpadc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/sun4i-gpadc.h

## Purpose

This 97-line header defines Allwinner sun4i/sun6i/sun8i GPADC/touchscreen register offsets, bitfields, IRQ IDs, autosuspend delay, and parent state.

## Important APIs, Types, and Functions

It exports control/status/data register addresses, macro builders for ADC delays, clock dividers, touch/ADC channel selection, filter, temperature period, FIFO control/status, IRQ IDs for FIFO and temperature data, `SUN4I_GPADC_AUTOSUSPEND_DELAY`, and `struct sun4i_gpadc_dev`.

## Control Flow

No executable flow. ADC, thermal, and touchscreen children use regmap/base access to configure sampling, channel selection, FIFO interrupts, and temperature conversion while sharing the MFD parent and IRQ chip.

## State and Persistence Behavior

Hardware persists ADC/touch control, FIFO status, temperature enable/period, interrupt enable/status, and sample data. Parent runtime state stores device, regmap, IRQ chip data, and MMIO base.

## Dependencies and Integration Points

It integrates the sun4i GPADC MFD core with IIO ADC, thermal, touchscreen, regmap-irq, runtime PM, and MMIO access.

## Risks and Edge Cases

Channel selection macros differ between sun4i and sun6i layouts. FIFO overrun/flush and interrupt bits must be handled carefully to avoid stale touch or temperature samples.

## Test Signals

ADC channel selection tests per SoC variant, thermal sample tests, touchscreen FIFO interrupt tests, runtime autosuspend tests, and regmap IRQ mapping checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sun4i-gpadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sy7636a.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/sy7636a.h

## Purpose

This 34-line header defines register addresses and masks for the SY7636A e-paper power management chip, especially VCOM control, VLDO adjustment, delays, faults, and thermistor readout.

## Important APIs, Types, and Functions

It exports operation mode bits `VCOMCTL` and `ONOFF`, VCOM low/high adjustment registers and 9-bit mask, VLDO adjustment register, power-on delay, fault flag register and power-good bit, thermistor readout, max register, VCOM shift/scale constants, and fault flag shift.

## Control Flow

No local flow exists. Regulator and hwmon/thermal-like users write VCOM/VLDO settings, read fault/thermistor values, and optionally let a GPIO control regulator operation.

## State and Persistence Behavior

State persists in SY7636A registers for operation mode, VCOM setting, VLDO voltage, delay, fault flags, and thermistor sample.

## Dependencies and Integration Points

It integrates SY7636A MFD/regulator support with display panel bias control and temperature/fault monitoring.

## Risks and Edge Cases

VCOM is a 9-bit value split across two registers; byte order and scale conversion must be correct. Fault flag shifting and power-good interpretation affect panel power sequencing.

## Test Signals

VCOM encode/decode tests, regulator on/off GPIO tests, thermistor read tests, fault flag tests, and panel power-sequence validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/sy7636a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon.h

## Purpose

This 80-line header is the generic Linux syscon API for looking up and registering regmaps backed by system-controller device nodes.

## Important APIs, Types, and Functions

When `CONFIG_MFD_SYSCON` is enabled it declares `device_node_to_regmap()`, `syscon_node_to_regmap()`, compatible and phandle lookup helpers including args and optional variants, and `of_syscon_register_regmap()`. When disabled, inline stubs return `ERR_PTR(-ENOTSUPP)`, `NULL` for optional lookup, or `-EOPNOTSUPP`.

## Control Flow

With syscon enabled, callers resolve device-tree nodes or phandles to shared regmaps. With syscon disabled, control returns immediately through stubs so callers can handle unsupported configuration.

## State and Persistence Behavior

The header owns no state. Registered regmaps represent shared SoC control registers whose values persist in hardware and are shared across unrelated drivers.

## Dependencies and Integration Points

It integrates device-tree consumers, MFD syscon provider registration, regmap clients, clock/reset/PHY/display/network drivers, and optional-property lookup behavior.

## Risks and Edge Cases

Callers must use `IS_ERR()` for required lookups and handle `NULL` from optional lookups. Shared syscon registers require masked updates to avoid clobbering other fields.

## Test Signals

Build tests with syscon enabled/disabled, phandle lookup tests, optional missing-property tests, and shared regmap update-bit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-matrix.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-matrix.h

## Purpose

This 112-line header defines Atmel AT91/SAMA5 MATRIX memory-controller system peripheral register offsets and bitfields.

## Important APIs, Types, and Functions

It exports variant-specific matrix register offsets, helper macros for master/slave configuration, ULBT, default master, arbitration, ITCM/DTCM sizing, priority registers, remap control, chip-select assignment, voltage IO selection, EBI/DDR IO settings, NAND selection, DDR multi-port enable, and USB pull-up control.

## Control Flow

No executable flow. SoC drivers use syscon regmaps and these macros to configure bus arbitration, remap behavior, EBI/DDR/NAND options, and USB pull-up routing.

## State and Persistence Behavior

State persists in system controller registers and affects memory bus topology, boot/remap behavior, chip-select routing, and IO voltage configuration.

## Dependencies and Integration Points

It integrates Atmel syscon consumers such as memory controller, NAND, USB, board init, and bus arbitration drivers.

## Risks and Edge Cases

Offsets vary by SoC; using the wrong variant offset can change unrelated system registers. IO voltage and chip-select settings are board-critical.

## Test Signals

Build tests for AT91/SAMA5 users, register offset validation per compatible, masked update tests, and boot/hardware tests for EBI/NAND/USB configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-matrix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-mc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-mc.h

## Purpose

This 140-line header defines legacy Atmel AT91 memory controller, EBI, SMC, SDRAMC, and burst flash controller register offsets and bitfields.

## Important APIs, Types, and Functions

It exports reset/abort status fields, master priority, EBI chip-select/config, SMC timing and mode fields, SDRAM mode/timing/control/refresh/low-power/interrupt fields, and burst flash controller mode fields.

## Control Flow

No code flow exists. Platform and memory-controller code writes timing, bus width, refresh, low-power, and chip-select fields through syscon or MMIO access.

## State and Persistence Behavior

These registers persist memory controller configuration that directly affects external memory, SDRAM refresh, bus width, wait states, and abort reporting.

## Dependencies and Integration Points

It integrates Atmel syscon/memory-controller users with EBI, SMC, SDRAMC, BFC, boot, and external memory setup code.

## Risks and Edge Cases

The macros `AT91_MPR_MSTP(n)` and `AT91_MC_EBI_CS(n)` reference `x` instead of the formal parameter, which is a latent macro bug if used. Timing and refresh misconfiguration can break memory access.

## Test Signals

Compile tests for macro users, external memory timing validation, SDRAM refresh tests, and static analysis for unused/broken parameter macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-smc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-smc.h

## Purpose

This 121-line header defines Atmel SMC/HSMC chip-select timing register layout, configuration structure, and helper APIs for static memory and NAND-like devices.

## Important APIs, Types, and Functions

It exports setup/pulse/cycle/mode/timings offset macros for SMC and HSMC layouts, timing field shifts, mode bitfields for read/write mode, external wait, bus width, TDF, page mode, and NAND timings, `struct atmel_hsmc_reg_layout`, `struct atmel_smc_cs_conf`, init/set/apply/get helper prototypes, and `atmel_hsmc_get_reg_layout()`.

## Control Flow

Driver flow initializes a `atmel_smc_cs_conf`, sets setup/pulse/cycle/timing values with validating helpers, then applies the result to a chip select using a regmap and optional HSMC layout.

## State and Persistence Behavior

Configuration lives in the stack/static struct until applied, then persists in SMC/HSMC hardware registers and controls external bus timing.

## Dependencies and Integration Points

It integrates Atmel memory controller support with device-tree, regmap, NAND, NOR, and other external bus devices.

## Risks and Edge Cases

Timing helpers must reject values outside bitfield capacity. SMC and HSMC register strides differ, so the correct layout function is required. Wrong timings can corrupt external memory transactions.

## Test Signals

Unit tests for timing/set helper bounds, apply/get round trips on mock regmap, device-tree layout tests, and hardware tests for NAND/NOR timing stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-st.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-st.h

## Purpose

This 45-line header defines AT91 system timer register offsets and bitfields for watchdog, periodic interval, real-time timer, status, interrupt, alarm, and current counter access.

## Important APIs, Types, and Functions

It exports `AT91_ST_CR`, `PIMR`, `WDMR`, `RTMR`, `SR`, `IER`, `IDR`, `IMR`, `RTAR`, and `CRTR` offsets, plus masks for watchdog restart, interval value, watchdog reset/external signal enables, real-time prescaler, status bits, alarm value, and current real-time value.

## Control Flow

No executable flow. Timer/watchdog/RTC-like code uses these constants to configure intervals, kick watchdog, enable interrupts, and read status/counter registers.

## State and Persistence Behavior

System timer and watchdog configuration persists in hardware and can trigger interrupts or reset events.

## Dependencies and Integration Points

It integrates AT91 syscon/timer/watchdog users through shared register definitions.

## Risks and Edge Cases

Watchdog restart/reset bits are high impact. Alarm and counter fields are limited width, so wraparound handling belongs in consumers.

## Test Signals

Timer interrupt tests, watchdog kick/reset tests, alarm wrap tests, and compile coverage for AT91 system timer users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-st.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/clps711x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/clps711x.h

## Purpose

This 90-line header defines CLPS711X system control and status register offsets and bit masks for legacy ARM SoC peripherals.

## Important APIs, Types, and Functions

It exports `SYSCON_OFFSET`, `SYSFLG_OFFSET`, SYSCON1/2/3 macros for keyboard scan, timers, buzzer, debug, LCD, codec, SIR, ADC clock, wake, UART/serial, DRAM, SSI, clock, DAI, and power bits, plus SYSFLG1/2 and generic UART busy/FIFO status bits.

## Control Flow

No local flow exists. CLPS711X platform drivers use syscon/regmap updates and reads to enable peripherals, select clocks, and inspect status.

## State and Persistence Behavior

System control bits persist in SoC registers and control peripheral clocks/functions. Status flags reflect live hardware state such as UART FIFOs, reset, power fail, card detect, and SSI bus state.

## Dependencies and Integration Points

It integrates CLPS711X syscon users across keyboard, timers, LCD, serial, audio/DAI, ADC, buzzer, and power/status drivers.

## Risks and Edge Cases

Several macros encode values by masking inputs; callers must pass already sensible values. Shared system registers require masked writes to avoid disabling unrelated peripherals.

## Test Signals

Build coverage for CLPS711X drivers, peripheral enable/disable tests, status bit read tests, and static checks for masked update usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/clps711x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx6q-iomuxc-gpr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx6q-iomuxc-gpr.h

## Purpose

This 472-line header defines i.MX6 IOMUXC general-purpose register offsets and bitfields for clocks, DMA request muxing, PCIe, USB, MIPI/LVDS/HDMI display routing, cache/QoS controls, SATA PHY, Ethernet clocks, MQS, CSI muxes, and related SoC glue.

## Important APIs, Types, and Functions

It exports `IOMUXC_GPR0` through `GPR13` offsets and many `IMX6Q_*`, `IMX6SL_*`, `IMX6SX_*`, `IMX6UL_*`, and `IMX6SLL_*` masks/values. Notable groups cover audio clock muxes, DMA request muxes, PCIe reset/refclk/power, USB ID, IPU/VPU/display muxing, LVDS format/width, cache controls, stop request/ack bits, SATA equalization/boost/level/speed settings, FEC clock direction, MQS control, CSI mux, and `MCLK_DIR(x)`.

## Control Flow

No code executes. Drivers obtain the IOMUXC GPR syscon regmap and perform masked updates when configuring PHYs, display pipelines, audio clocks, Ethernet clock direction, PCIe, SATA, and low-power stop controls.

## State and Persistence Behavior

The GPR fields persist in SoC system registers and directly affect pin mux glue, peripheral routing, clocking, resets, power states, cache policy, and PHY tuning.

## Dependencies and Integration Points

It includes bitops and integrates syscon consumers in PCIe, SATA, USB, DRM/display, Ethernet, audio, VPU/IPU, CSI, MQS, and low-power management drivers.

## Risks and Edge Cases

Many SoC variants share the header but not all fields. Some constants duplicate values or use raw shifts instead of `FIELD_PREP`; consumers must use the correct mask/value pair and avoid applying i.MX6Q fields to i.MX6SX/UL/SLL variants.

## Test Signals

Build tests for all i.MX6 variant drivers, syscon masked-update tests, board boot/display/network/PCIe/SATA smoke tests, and static checks for mask/value compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx6q-iomuxc-gpr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx7-iomuxc-gpr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx7-iomuxc-gpr.h

## Purpose

This 48-line header defines i.MX7 IOMUXC GPR offsets and selected bitfields for Ethernet clocking, CSI muxing, and PCIe PHY status/control.

## Important APIs, Types, and Functions

It exports `IOMUXC_GPR0` through `GPR22`, `IMX7D_GPR1_*` IRQ/ENET clock selection/direction masks, `IMX7D_GPR5_CSI_MUX_CONTROL_MIPI`, `IMX7D_GPR12_PCIE_PHY_REFCLK_SEL`, and `IMX7D_GPR22_PCIE_PHY_PLL_LOCKED`.

## Control Flow

No local flow exists. i.MX7 drivers use syscon regmap masked updates and reads to configure ENET clocks, CSI input muxing, and PCIe reference clock/PLL lock handling.

## State and Persistence Behavior

The state persists in IOMUXC GPR hardware registers and affects clock direction/source, camera routing, and PCIe PHY readiness.

## Dependencies and Integration Points

It integrates i.MX7 syscon consumers in Ethernet, media/CSI, and PCIe PHY/controller drivers.

## Risks and Edge Cases

PCIe PLL lock is a status bit, not a configuration bit. ENET clock source and direction masks must be updated atomically to avoid transient wrong clock routing.

## Test Signals

Board boot tests for Ethernet/CSI/PCIe, syscon regmap update tests, and PCIe PLL-lock wait-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx7-iomuxc-gpr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/xlnx-vcu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/xlnx-vcu.h

## Purpose

This 39-line header defines Xilinx VCU syscon register offsets for encoder/decoder enable, frame format, clocks, PLL, status, and gasket initialization.

## Important APIs, Types, and Functions

It exports register offsets such as `VCU_ECODER_ENABLE`, `VCU_DECODER_ENABLE`, memory depth, encoder/decoder color depth, range, frame size, color format, FPS, MCU/core/encoder/PLL/AXI clocks, video standards, status, core count, gasket init, and `VCU_GASKET_VALUE`.

## Control Flow

No executable flow. Xilinx media/clock drivers use these offsets through syscon/regmap to configure VCU encoder/decoder hardware and check status.

## State and Persistence Behavior

State persists in VCU control registers and describes active encoder/decoder configuration, clocking, PLL mode, buffer behavior, and gasket setup.

## Dependencies and Integration Points

It integrates Xilinx VCU syscon support with video codec drivers, clock configuration, and media pipeline setup.

## Risks and Edge Cases

The macro name `VCU_ECODER_ENABLE` appears misspelled but is ABI for users. Codec configuration fields must match firmware/hardware expectations for frame size, color, and clocks.

## Test Signals

Build tests for VCU consumers, register offset smoke tests, encoder/decoder bring-up tests, and media pipeline format/clock validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/syscon/xlnx-vcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tc3589x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tc3589x.h

## Purpose

This 157-line header defines Toshiba TC3589x MFD register addresses, block IDs, IRQ numbers, parent state, bus access helpers, keypad defaults, and platform data.

## Important APIs, Types, and Functions

It exports `enum tx3589x_block`, reset/keyboard IRQ masks, keyboard, manufacturer/version, clock, reset, GPIO, pull, interrupt, wake, open-drain, and direct register addresses, internal IRQ IDs/count, `struct tc3589x`, register/block read/write and bit-update prototypes, keypad rows/columns/debounce/settle constants, and `struct tc3589x_platform_data`.

## Control Flow

Parent and child drivers use bus helper functions for serialized I2C register access. The MFD enables requested blocks, maps internal IRQs through an IRQ domain, and child GPIO/keypad drivers operate on their register ranges.

## State and Persistence Behavior

`struct tc3589x` stores mutex, device, I2C client, IRQ domain, base IRQ, GPIO count, and platform data. Hardware persists GPIO direction/data/IRQ/wake state, keypad configuration, clocks, reset bits, and block enables.

## Dependencies and Integration Points

It integrates TC3589x MFD core with GPIO, keypad/input, IRQ domain, I2C, and platform-data block selection.

## Risks and Edge Cases

Shared register access must be locked. Block reset bits can disrupt child drivers. Keypad constants are tuning defaults and may not fit every board.

## Test Signals

GPIO and keypad child probe tests, register access helper tests, IRQ domain mapping tests, block enable/reset tests, and keypad matrix event tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tc3589x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu-register.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu-register.h

## Purpose

This 212-line header defines register maps and bit masks for TI LMU lighting/display-bias devices LM3631, LM3632, LM3633, LM3695, and LM36274.

## Important APIs, Types, and Functions

It exports per-chip register addresses for device control, brightness LSB/MSB, backlight configuration, modes, slopes, LDO/bias enables, boost/positive/negative output voltages, enable timing, LED mappings, ramps, current limits, patterns, OVP, PWM, fault status, monitor enable, and max-register values.

## Control Flow

No local flow exists. Backlight, LED, regulator, and monitor drivers select the register set by chip ID and program brightness, channel mode, bias supplies, OVP, PWM, ramp, and fault-monitor fields through regmap.

## State and Persistence Behavior

Hardware registers persist backlight brightness, LED bank/channel mapping, bias regulator output voltages, enable state, ramp timing, PWM mode, pattern generator values, and fault/monitor status.

## Dependencies and Integration Points

It includes bitops and integrates TI LMU MFD core with backlight, LED, regulator, and hwmon/fault-monitor consumers.

## Risks and Edge Cases

Different LMU chips reuse similar concepts at different addresses. Brightness width and channel mapping differ, so generic code must branch by chip. Voltage and current masks are hardware-limited.

## Test Signals

Per-chip regmap table tests, brightness encode tests, regulator voltage selector tests, LED channel mapping tests, OVP/fault status tests, and build coverage for each LMU ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu-register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu.h

## Purpose

This 87-line header defines the shared TI LMU device model, chip IDs, maximum-current enum, regulator IDs, notifier event, and parent runtime state.

## Important APIs, Types, and Functions

It exports `LMU_EVENT_MONITOR_DONE`, `enum ti_lmu_id`, `enum ti_lmu_max_current`, `enum lm363x_regulator_id`, and `struct ti_lmu` with device, regmap, optional enable GPIO, and blocking notifier head.

## Control Flow

No local code flow. The MFD parent initializes the shared struct, toggles the hardware enable GPIO as needed, and children use regmap plus notifier callbacks for monitor completion events.

## State and Persistence Behavior

`struct ti_lmu` stores runtime parent state and notifier list. Hardware persists lighting and bias configuration in chip registers.

## Dependencies and Integration Points

It integrates TI LMU MFD core with GPIO, regmap, notifier, backlight/LED, regulator, and monitoring subdrivers.

## Risks and Edge Cases

Notifier use requires careful ordering around monitor completion. Optional enable GPIO lifetime and polarity must match hardware. Regulator IDs span multiple chips, so child support must gate unsupported rails.

## Test Signals

Probe tests per LMU ID, notifier registration/notification tests, enable GPIO tests, regulator ID support tests, and child-driver build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti_am335x_tscadc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ti_am335x_tscadc.h

## Purpose

This 196-line header defines the TI AM335x touchscreen/ADC MFD register map, bitfield macros, timing constants, parent state, inline helpers, and sequencer management APIs.

## Important APIs, Types, and Functions

It exports IRQ, DMA, control, step, FIFO, and sequencer register offsets; bitfields for IRQ wake/enable, step config, delay, charge config, control, FIFO read, DMA, status, timing constants, cell count, `struct ti_tscadc_data`, `struct ti_tscadc_dev`, inline `ti_tscadc_dev_get()` and `ti_adc_with_touchscreen()`, and sequencer cache/update/done prototypes.

## Control Flow

Child drivers obtain the parent pointer from platform data, check whether touchscreen is present, coordinate access to the step-enable sequencer cache, and use wait queues/spinlock fields to arbitrate ADC versus touchscreen access.

## State and Persistence Behavior

`struct ti_tscadc_dev` stores regmap/MMIO/physical base, feature data, IRQ, MFD cells, control cache, sequencer enable cache, ADC wait/in-use flags, wait queue, spinlock, clock divider, and child pointers. Hardware persists sequencer, FIFO, IRQ, DMA, and control state.

## Dependencies and Integration Points

It integrates AM335x TSCADC MFD parent with IIO ADC, touchscreen input, MAGADC variants, DMA, IRQ, platform devices, and clock-rate configuration.

## Risks and Edge Cases

ADC and touchscreen share the sequencer, so cache synchronization and wait completion are critical. Timing macros encode hardware field widths; overflow can stall conversions. `IDLE_TIMEOUT_MS` is derived from worst-case conversion timing.

## Test Signals

Sequencer arbitration tests, ADC/touchscreen concurrent-use tests, FIFO/IRQ tests, timeout tests, compatible-specific clock-rate tests, and build coverage for MAGADC and TSCADC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ti_am335x_tscadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6105x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps6105x.h

## Purpose

This 97-line header defines the TI TPS6105x MFD register map, operation modes, platform data, and parent state for flashlight/torch/backlight or voltage-regulator use.

## Important APIs, Types, and Functions

It exports register addresses 0-3, mode/voltage/dimming/torch-current shifts and masks, current and voltage selector values, `enum tps6105x_mode`, `struct tps6105x_platform_data`, and `struct tps6105x` with platform data, I2C client, optional regulator device, and regmap.

## Control Flow

No local executable flow. The MFD core selects a fixed mode from platform data during probe, then registers LED/flash or regulator children that program register mode, current, voltage, and dimming fields.

## State and Persistence Behavior

Hardware registers persist selected mode, torch current, output voltage, dimming, and enable behavior. Parent runtime state stores regmap and optional regulator handle.

## Dependencies and Integration Points

It integrates TPS6105x MFD support with I2C, regmap, LED/flash, regulator framework, and platform regulator constraints.

## Risks and Edge Cases

Mode is not intended to be changed dynamically by unrelated children. Register 0 and 1 share mode encodings. Current selector names encode different ranges depending on hardware configuration.

## Test Signals

Mode-specific probe tests, LED brightness/current tests, regulator voltage tests, regmap mask update tests, and platform-data validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6105x.h -->
