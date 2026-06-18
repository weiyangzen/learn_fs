<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65010.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65010.h

## Purpose
`tps65010.h` is the public MFD-facing contract for the older TI TPS65010/TPS65011/TPS65012/TPS65013 power-management chips. It names the 8-bit charger, regulator, LED, vibrator, GPIO, interrupt-mask, and acknowledge registers and exposes board glue for packaging the GPIO/LED pins into Linux GPIO/LED users.

## Important APIs, Types, and Functions
The register map covers charger status/configuration (`TPS_CHGSTATUS`, `TPS_CHGCONFIG`), regulator status/control (`TPS_REGSTATUS`, `TPS_VDCDC1`, `TPS_VDCDC2`, `TPS_VREGS1`), LED timing (`TPS_LED*_ON`, `TPS_LED*_PER`), interrupt masks/acks, and default GPIO config. Exported helpers include `tps65010_set_vbus_draw()`, `tps65010_set_gpio_out_value()`, `tps65010_set_led()`, `tps65010_set_vib()`, `tps65010_set_low_pwr()`, `tps65010_config_vregs1()`, `tps65013_set_low_pwr()`, and `tps65010_config_vdcdc2()`. `struct tps65010_board` carries GPIO output masks plus setup/teardown callbacks.

## Control Flow
This header does not implement logic; it defines the calls that board and subdevice drivers use to request PMIC state changes. Typical flow is board probe registering the MFD/I2C device, optional GPIO setup callback after the GPIO chip is live, and subdrivers using exported helpers to write full registers or individual feature bits.

## State and Persistence Behavior
Persistent hardware state is in PMIC registers: charge source, current limit, regulator voltage/enable state, low-power mode, LED blink periods, vibrator enable, interrupt masks, and GPIO defaults. `struct tps65010_board` is boot-time platform data; it is not persisted beyond device lifetime.

## Dependencies and Integration Points
The file forward-declares `struct gpio_chip` and `struct i2c_client` and integrates with legacy I2C board data, GPIO registration, LED behavior, USB VBUS current policy, and regulator/power-control board code.

## Risks and Test Signals
Risks include full-register writes in `tps65010_config_vregs1()` and `tps65010_config_vdcdc2()` clobbering unrelated bits, using TPS65013-only bits on other variants, invalid GPIO/LED identifiers, and wrong VBUS draw values causing USB power violations. Test signals are I2C readback of touched registers, GPIO direction/value tests, LED/vibrator functional tests, USB current-limit transitions for 0/100/500 mA, and suspend/resume checks for low-power mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65010.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6507x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps6507x.h

## Purpose
`tps6507x.h` defines the shared register and device-data interface for TPS65070-family PMICs. It supports charger/power-path control, interrupt state, ADC/touchscreen conversion, DCDC/LDO regulators, power-good status, slew configuration, and white LED control.

## Important APIs, Types, and Functions
Important register groups are `TPS6507X_REG_PPATH1`, `TPS6507X_REG_INT`, `TPS6507X_REG_CHGCONFIG*`, `TPS6507X_REG_ADCONFIG`, `TPS6507X_REG_TSCMODE`, `TPS6507X_REG_ADRESULT_*`, `TPS6507X_REG_CON_CTRL*`, DCDC voltage registers, LDO controls, and WLED controls. `struct tps6507x_board` links regulator and touchscreen init data. `struct tps6507x_dev` stores the parent device, I2C client, low-level `read_dev()`/`write_dev()` callbacks, and a PMIC child pointer.

## Control Flow
The MFD core owns I2C access and exposes the function-pointer read/write path to children. Touchscreen/ADC users select an input or TSC mode, start conversion through `ADCONFIG`, then consume result registers when conversion-done is set. Regulator users update enable and voltage fields through the shared device callbacks.

## State and Persistence Behavior
State is persisted in PMIC registers for source detection, charging enable/current, ADC input selection, touchscreen mode, regulator enable/voltage, DCDC high/low settings, LDO settings, and WLED state. Software state is limited to the live `struct tps6507x_dev` and board init pointers.

## Dependencies and Integration Points
This header references regulator and touchscreen platform data types, `struct device`, and `struct i2c_client`. It integrates the MFD parent with regulator and touchscreen/ADC subdrivers and provides register constants for power-path and interrupt handling.

## Risks and Test Signals
Risks include duplicate macro definitions for `TPS6507X_CON_CTRL1_*`, malformed ADC input selection, stale conversion-done polling, and unsynchronized child access through raw callbacks. Test signals are regulator voltage/enable readback, ADC conversion completion and decoded result width, interrupt masking/unmasking for AC/USB/TSC/PB events, WLED control readback, and probe tests that reject missing callback pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6507x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65086.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65086.h

## Purpose
`tps65086.h` is the shared MFD definition for TI TPS65086 PMIC variants. It names device ID, IRQ, buck, LDO, power-good, fault, shutdown, and pin-enable registers and defines the parent state object used by regulator and IRQ subdrivers.

## Important APIs, Types, and Functions
Key constants include `TPS65086_DEVICEID*`, `TPS65086_IRQ`, `TPS65086_IRQ_MASK`, buck control/VID/sleep registers, `TPS65086_LDOA*`, `TPS65086_PIN_EN_*`, `TPS65086_GPO*`, `TPS65086_PG_STATUS*`, and fault/temperature status registers. Field masks identify die temperature, shutdown, and fault IRQs, part/revision fields, and VID encodings. `enum tps65086_irqs` exposes `DIETEMP`, `SHUTDN`, and `FAULT`. `struct tps65086` stores `dev`, `regmap`, `chip_id`, regulator config, parent IRQ, and `regmap_irq_chip_data`.

## Control Flow
The header contains no executable helpers. The MFD probe reads ID registers, selects regulator config by chip ID, initializes a regmap IRQ chip for the three top-level interrupt sources, and child drivers use the parent regmap to manage regulators, pin-enable overrides, GPO power-good routing, and fault status.

## State and Persistence Behavior
PMIC registers persist regulator voltage, sleep voltage, enable masks, pin overrides, GPO routing, power-good state, shutdown source, and fault/temperature status. Software keeps the resolved chip ID and regmap IRQ data only for the live device.

## Dependencies and Integration Points
The header depends on `<linux/device.h>` and `<linux/regmap.h>`. It integrates with MFD core data, regmap, regmap-irq, regulator config tables, board/device-tree matching, and fault/thermal reporting.

## Risks and Test Signals
Risks include confusing overlapping addresses such as `PIN_EN_MASK2`/`SWVTT_EN` and `PIN_EN_OVR2`/`GPOCTRL`, incorrect VID mask selection across buck/LDO classes, and lost fault interrupts if mask/status constants diverge from regmap IRQ tables. Test signals include chip ID decode tests, regmap IRQ firing for die temperature/shutdown/fault, regulator voltage selector tests, fault-status readback after injected events, and suspend/resume readback of sleep controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65086.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65090.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65090.h

## Purpose
`tps65090.h` provides the core interface for the TPS65090 PMIC family. It defines interrupt numbers, regulator IDs, register addresses, platform regulator data, and inline regmap-backed helpers for subdevice register access.

## Important APIs, Types, and Functions
The IRQ namespace covers VAC/VSYS/battery/charging status and overload events for DCDC and FET outputs. Regulator IDs cover DCDC1-3, FET1-7, and LDO1-2. `struct tps65090` stores the parent `device`, regmap, and IRQ chip data. `struct tps65090_regulator_plat_data` carries regulator init data, external-control GPIO configuration, and overcurrent wait fields. Inline helpers are `tps65090_write()`, `tps65090_read()`, `tps65090_set_bits()`, and `tps65090_clr_bits()`.

## Control Flow
Subdrivers retrieve the parent state with `dev_get_drvdata()`, then perform regmap writes, reads, or update-bits operations. `set_bits()` and `clr_bits()` take a bit number, convert it with `BIT(bit_num)`, and update the target register. Probe-time platform data controls whether regulators are controlled internally or through external GPIOs.

## State and Persistence Behavior
Hardware registers store interrupt masks/status, charger controls/status, and ADC outputs. Platform data persists only for the lifetime of the device and determines regulator constraints, supplied consumers, low-current charging, external GPIO use, and overcurrent delay programming.

## Dependencies and Integration Points
The file depends on `linux/irq.h`, `linux/regmap.h`, regulator init data, GPIO descriptors, and MFD parent driver data. It integrates with charger, regulator, GPIO-descriptor, regmap-irq, and board platform-data paths.

## Risks and Test Signals
Risks include passing a bit mask instead of a bit number to the inline set/clear helpers, stale 8-bit truncation in `tps65090_read()`, invalid overcurrent wait values outside 0-3, and external-control GPIO polarity mismatches. Test signals are regmap update-bits unit tests, regulator enable path coverage for internal and GPIO control, overcurrent IRQ mapping tests, ADC register reads, and charger status transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65090.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65217.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65217.h

## Purpose
`tps65217.h` is the PMIC contract for TPS65217. It defines the I2C ID, complete register map, protected-write levels, regulator IDs, backlight data, interrupt numbering, board init data, parent state, and register access prototypes.

## Important APIs, Types, and Functions
Register constants cover charger/power-path, interrupt, WLED, mux, status, password, power-good, DCDC/LDO/load-switch definition, enable, UVLO, and sequencing registers. `enum tps65217_regulator_id` names DCDC1-3 and LDO1-4. Backlight enums define current source and PWM/dimming frequency. `struct tps65217_board` carries regulator init data, device-tree nodes, and optional backlight platform data. `struct tps65217` stores regulator descriptors, regmap, strobe table, IRQ domain, mutex, mask, and IRQ. APIs are `tps65217_reg_read()`, `tps65217_reg_write()`, `tps65217_set_bits()`, and `tps65217_clear_bits()`.

## Control Flow
The MFD core initializes regmap and IRQ domain, then children call the accessors. Protected writes use the caller-provided level (`TPS65217_PROTECT_NONE`, `L1`, or `L2`) so the implementation can unlock via the password register before modifying sensitive power registers.

## State and Persistence Behavior
PMIC state includes charger status/config, WLED duty/current, mux status, regulator voltages/enables, UVLO thresholds, power-good masks, and sequencing delays. Software tracks IRQ mask state, regulator descriptors, and strobe bytes needed for protected writes.

## Dependencies and Integration Points
The header depends on I2C, regmap through implementation, regulator descriptors/machine data, mutexes, IRQ domains, and device-tree nodes. It integrates with regulator, power supply/charger, backlight, and IRQ controller subdrivers.

## Risks and Test Signals
Risks include using the wrong protection level, full-mask updates to power sequencing registers, mismatches between `TPS65217_REG_MAX` and `TPS65217_MAX_REGISTER`, and unguarded IRQ mask changes. Test signals are protected-write failure injection, regulator selector/enable readback, WLED brightness tests, IRQ domain mapping for USB/AC/PB, and suspend/resume sequencing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65217.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65218.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65218.h

## Purpose
`tps65218.h` defines the MFD interface for TPS65218 PMICs. It describes status, interrupt, enable, configuration, DCDC/LDO/load-switch, slew, and sequence registers plus regulator/IRQ IDs and parent state.

## Important APIs, Types, and Functions
The register map includes `CHIPID`, `INT1/INT2`, interrupt masks, status/control/flag, password, enable/config registers, DCDC1-4 controls, slew rate, LDO1, and sequence registers. `enum tps65218_regulator_id` names six DCDCs, one LDO, and two load-switch regulators. `enum tps65218_irqs` maps two interrupt bytes into virtual IRQ IDs. `struct tps65218` holds device pointer, ID, revision, lock, IRQ mask/data, regulator descriptors, regmap, and protected-write strobes. APIs are `tps65218_reg_write()`, `tps65218_set_bits()`, and `tps65218_clear_bits()`.

## Control Flow
Probe reads chip/revision, initializes regmap IRQ handling for INT1/INT2, and exposes regulator/load-switch children. Register writes route through helpers that accept a protection level; sensitive registers are unlocked via the password/strobe mechanism before regmap writes.

## State and Persistence Behavior
Persistent hardware state includes FSEAL/EEPROM/status bits, AC/PB states, charger acquisition, DCDC/LDO voltages, load-switch enables/current flags, UVLO, GPO behavior, slew settings, and power-up/down slots. Software state is live-only: revision, regmap, IRQ masks, lock, descriptors, and strobe table.

## Dependencies and Integration Points
The header depends on I2C, regulator driver/machine APIs, bitops, mutex, regmap, and regmap-irq through the core implementation. It integrates regulator, load-switch, interrupt, and board configuration consumers.

## Risks and Test Signals
Risks include invalid protected-write sequencing, confusing `TPS65218_MAX_REG_ID` with the actual number of regulators, using LS3 definitions when only two LS regulators are exposed, and stale IRQ masks across resume. Test signals include revision decode, protected-write readback, regmap IRQ tests for INT1/INT2 events, regulator voltage/enable tests, LS fault IRQ injection, and power-sequence register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65218.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65219.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65219.h

## Purpose
`tps65219.h` is the shared register contract for TPS65214, TPS65215, and TPS65219 PMICs. It captures chip-specific aliases, regulator layouts, sequence slots, interrupt sources/subinterrupts, standby and MFP controls, residual-voltage handling, and the parent regmap/IRQ state.

## Important APIs, Types, and Functions
`enum pmic_id` names the three supported chips. Registers span ID/NVM, enable, buck/LDO voltage, sequence slots, power-slot durations, general/MFP/standby/OC-deglitch config, UV and effect masks, main and sub-IRQ registers, NVM commands, power-up status, and factory config. The large anonymous IRQ enum lists LDO, buck, thermal, residual-voltage, timeout, and power-button subevents. Separate regulator and top-level IRQ enums exist for TPS65214, TPS65215, and TPS65219. `struct tps65219` stores `dev`, `regmap`, and regmap IRQ data.

## Control Flow
The MFD driver selects tables by `pmic_id`, because several register addresses and IRQ source positions are chip-specific aliases. Regulator and IRQ subdrivers use the shared regmap and constants to manage voltage selectors, enables, standby masks, sequence slots, and subinterrupt dispatch from `INT_SOURCE`.

## State and Persistence Behavior
Hardware persists voltage selectors, standby enable bits, sequence slots, power durations, MFP behavior, I2C address/NVM storage, UV/retry masks, residual-voltage events, thermal events, and power-button status. The software object only owns live regmap and IRQ-chip data.

## Dependencies and Integration Points
The file depends on bitops, regmap, and regulator descriptors. It integrates with TI PMIC MFD core, regulator drivers, regmap-irq nested interrupt handling, thermal/error event reporting, power-button input handling, and device-tree chip matching.

## Risks and Test Signals
Risks include selecting the wrong alias set for TPS65214/TPS65215, duplicated enum values for variant-specific residual-voltage events, stale comments/TODOs around standby masks, and incorrect top-level source positions. Test signals are per-chip register-table tests, regulator count/name tests, IRQ source-to-subevent dispatch tests for all variants, NVM command lock tests, power-button edge events, and thermal/residual-voltage interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65219.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6586x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps6586x.h

## Purpose
`tps6586x.h` defines the public MFD interface for TPS6586x PMIC variants. It covers version CRC IDs, regulator and interrupt IDs, slew-rate settings, subdevice platform data, and low-level register/IRQ helpers for child drivers.

## Important APIs, Types, and Functions
Slew-rate constants encode instantaneous through 7040 uV steps plus set/mask bits. Version constants identify TPS658621A/CD, TPS658623/624/640/643 variants. Regulator IDs cover system, three switching modules, ten LDOs, and RTC LDO. Interrupt IDs cover PLDO/PSM events, comparator, ADC, RTC alarms, charger/source events, resume, and low-system voltage. `struct tps6586x_platform_data` carries subdevices, GPIO/IRQ bases, `pm_off`, and regulator init data. Helper prototypes include read/write/bulk read/write, set/clear/update bits, IRQ virtual mapping, and version readout.

## Control Flow
The parent driver registers child devices from `subdevs`, provides register access wrappers over the chip bus, maps hardware IRQ IDs to Linux IRQs through `tps6586x_irq_get_virq()`, and exposes chip version for variant-specific child behavior.

## State and Persistence Behavior
Hardware state includes regulator enables/voltages/slew rates, ADC/comparator events, RTC alarm events, charger status, and GPIO/IRQ routing. Platform data persists only during device lifetime and controls child instantiation, base numbers, and power-off support.

## Dependencies and Integration Points
The header references `struct device`, device-tree nodes, and regulator init data. It integrates with MFD child registration, regulator, RTC, ADC/comparator, GPIO, interrupt, and system-poweroff paths.

## Risks and Test Signals
Risks include using helpers outside subdevice drivers, mismatched IRQ IDs and regmap IRQ tables, board-file GPIO/IRQ base collisions, and version-specific regulator differences hidden behind shared IDs. Test signals are version decode tests, bulk read/write boundary tests, update-bits readback, virtual IRQ mapping tests, regulator slew-rate programming, and system power-off integration when `pm_off` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6586x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65910.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65910.h

## Purpose
`tps65910.h` defines the shared interface for TPS65910 and TPS65911 PMICs. It combines RTC, backup, regulator, charger/thermal, sleep control, GPIO, interrupt, and board-data definitions used by the MFD core and subdrivers.

## Important APIs, Types, and Functions
The register map includes RTC time/alarm/control, backup registers, pullups, reference/VRTC/VIO/VDD/LDO rails, thermal and backup battery charge, DCDC/device control, sleep keep/off assignment registers, interrupt status/masks, GPIO registers, and revision ID. TPS65911-specific aliases add VDDCTRL and LDO1-8. IRQ macros map TPS65910 and TPS65911 event layouts. Regulator indexes and sleep-control flags define the regulator driver's ABI. `struct tps65910_board` carries GPIO/IRQ bases, thresholds, clock/sleep flags, PM-off, sleep keep-on flags, GPIO sleep config, external sleep control masks, and regulator init data. `struct tps65910` stores I2C, regmap, ID, parsed board data, and IRQ data.

## Control Flow
The parent driver reads chip ID/revision, installs regmap IRQ tables appropriate to TPS65910 or TPS65911, parses board/OF data, and child drivers use the register constants for RTC, regulator, GPIO, and power-management operations. `tps65910_chip_id()` is a simple accessor over stored ID.

## State and Persistence Behavior
Hardware persists RTC time/alarm/compensation, backup bytes, regulator voltage/mode, GPIO state, sleep keep/off mappings, interrupt masks, thresholds, and device power state. Software caches parsed platform data, chip ID, and regmap IRQ state while probed.

## Dependencies and Integration Points
The header depends on GPIO and regmap headers, I2C via struct use, regulator init data, and board/device-tree parsing in implementation. Integration points include RTC, regulator, GPIO, IRQ, thermal/hotdie, power button, charger, clock, and PM-off paths.

## Risks and Test Signals
Risks include TPS65910/TPS65911 register-layout confusion, duplicated generic GPIO/thermal masks colliding with other headers, incorrect regulator indexes for TPS65911 aliases, and sleep assignment mistakes that power down required rails. Test signals include per-variant IRQ table tests, RTC alarm/periodic interrupt tests, GPIO edge tests, regulator selector and external sleep-control tests, PM-off behavior, and resume validation of interrupt masks and sleep keep-on bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65910.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65912.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps65912.h

## Purpose
`tps65912.h` is the MFD contract for TPS65912/TPS6591x PMIC support. It defines a compact register map for DCDC, LDO, thermal, clocks, device control, keep/off sequencing, GPIO, VMON, LEDs, load switches, interrupt status/masks, and core initialization hooks.

## Important APIs, Types, and Functions
Registers cover DCDC1-4 control/op/AVS/limit, LDO1-10, thermal, 32 kHz clock, device control, serial config, keep-on/set-off/default-voltage/discharge, EN1-EN4 assignments, PGOOD, four interrupt status/mask bytes, GPIO1-5, VMON, LEDA/B/C controls, load switch, spare, and version. IRQ enum entries map power hold, VMON, power-on, hotdie, GPIO edges, and PGOOD events for DCDC/LDO rails. `struct tps65912` stores `dev`, `regmap`, parent IRQ, and IRQ chip data. It exports `tps65912_regmap_config` and `tps65912_device_init()`.

## Control Flow
Bus-specific code supplies a regmap using the exported config and calls `tps65912_device_init()`. The MFD core sets up IRQ handling and child devices; regulator/GPIO/LED/thermal users program their register groups via regmap.

## State and Persistence Behavior
Hardware persists DCDC/LDO modes and voltage limits, AVS enable state, thermal status, clock settings, keep-on/off mappings, GPIO control, PGOOD status, LED sequencing, and interrupt masks. Software state is a live regmap plus regmap-irq bookkeeping.

## Dependencies and Integration Points
The header depends on device and regmap APIs. It integrates with I2C/SPI bus frontends, MFD core, regulator, GPIO, LED, thermal/VMON, interrupt, and power sequencing subdrivers.

## Risks and Test Signals
Risks include repeated macro names (`DCDCCTRL_TSTEP*`) shared across DCDC groups, generic GPIO/THERM names colliding in broad includes, wrong interrupt byte mapping, and insufficient validation of LED/loadswitch register ranges. Test signals are regmap-config readable/writable tests, device-init failure paths, IRQ events across all four status bytes, regulator AVS/limit readback, GPIO edge tests, LED sequence tests, and bus frontend probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps65912.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6594.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps6594.h

## Purpose
`tps6594.h` is the large shared register and IRQ definition header for TPS6594, TPS6593, LP8764, TPS65224, and TPS652G1 PMIC-class devices. It covers paged register addressing, buck/LDO/VMON/GPIO control, power-state FSM, ESM, RTC, ADC, CRC, watchdog, volatile regmap tables, and core initialization.

## Important APIs, Types, and Functions
`enum pmic_id` names chip families, and `TPS6594_REG_TO_PAGE()` maps 16-bit register addresses to pages. Register macros cover page 0 PMIC control and status, page 1 serial interface/I2C IDs, and page 4 watchdog registers. Field macros describe regulator enables, voltage selectors, power-good windows, GPIO muxing, trigger masks, IRQ masks, status bits, PGOOD routing, RTC BCD fields, ADC result fields, CRC controls, and watchdog question/answer windows. `enum tps6594_irqs` and `enum tps65224_irqs` provide separate IRQ namespaces with string names. `struct tps6594` stores device, chip ID, bus address/chip-select, CRC mode, regmap, IRQ, and IRQ data. APIs include `tps6594_device_init()` and volatile access-table exports.

## Control Flow
Bus-specific drivers create the regmap, optionally enable CRC, set chip identity, then call `tps6594_device_init()`. The core chooses chip-specific volatile tables and IRQ chips. Children use calculated register macros for per-instance bucks, LDOs, GPIOs, watchdog, RTC, and power-fault handling.

## State and Persistence Behavior
Hardware state is extensive: rail voltage/enables, group selections, FSM triggers, masks, interrupt and status latches, recovery counters, ESM counters, RTC/alarm/scratch registers, ADC conversion state, CRC registers, watchdog counters/windows, and communication error flags. Software caches chip identity, CRC use, bus register value, regmap, and IRQ data.

## Dependencies and Integration Points
The header depends on device and regmap APIs. It integrates with I2C/SPI frontends, regmap paging/CRC, regmap-irq, regulator, GPIO, RTC, watchdog, ADC, ESM/safety, thermal/fault, and power sequencing drivers.

## Risks and Test Signals
Risks include chip-family register alias mistakes, page/address calculation errors, choosing TPS6594 IRQ names for TPS65224 or vice versa, CRC enable mismatch between bus and regmap, duplicate/typo macros such as `MASk`, and watchdog/ESM safety register misprogramming. Test signals are per-chip regmap-access-table tests, CRC transaction tests, IRQ name/count validation, regulator/GPIO calculated-address tests, RTC alarm tests, watchdog question-answer sequence tests, ADC conversion tests for TPS65224, and fault-injection for severe/moderate/FSM errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps6594.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps68470.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/tps68470.h

## Purpose
`tps68470.h` defines register addresses and masks for the Intel-used TPS68470 PMIC, primarily camera-support power, clocks, GPIOs, PLL configuration, reset, and revision access.

## Important APIs, Types, and Functions
The register map names PLL divider/control registers, clock configuration, seven GPIO control pairs, simple GPIO input/output registers, voltage-value registers for VCM/VAUX/VIO/VSIO/VA/VD, enable controls, reset, and revision ID. Masks define voltage selector widths, enable bits, PLL enable, clock output modes, default PLL/oscillator values, output shifts, GPIO control register calculators, and GPIO modes for input, input pull-up, CMOS output, and open-drain output.

## Control Flow
There are no functions or structs. Consumers use the constants with the parent regmap. Clock code programs PLL/divider and output mode registers, regulator code sets voltage selectors and enable bits, and GPIO code computes per-GPIO control registers with `TPS68470_GPIO_CTL_REG_A/B(x)`.

## State and Persistence Behavior
Hardware persists PLL and clock routing, GPIO direction/mode/output state, regulator voltage selectors and enables, secondary I2C enable, reset state, and revision ID. No software state is declared by this header.

## Dependencies and Integration Points
The header relies on `BIT()` and `GENMASK()` from common kernel bitops being available to includers. It integrates with MFD, regmap, clock, GPIO, and regulator drivers for camera sensor power management.

## Risks and Test Signals
Risks include off-by-one GPIO register calculation, confusing `SHIFT` macros that hold masks for some fields, writing reset mask blindly, and using default PLL values without board-clock validation. Test signals are regmap readback of voltage/enables, GPIO mode tests for all seven pins, clock-rate and PLL enable tests, revision register detection, and camera probe sequences that verify rails and clocks come up in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/tps68470.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/twl.h

## Purpose
`twl.h` is the central public header for TWL4030/TWL5031/TWL6030/TWL6032-family PM and audio codec devices. It defines module IDs, register offsets that must be shared across subdrivers, I2C accessors, interrupt offsets, power-bus message encoding, board platform data, regulator IDs, and feature flags.

## Important APIs, Types, and Functions
Core enums identify common, TWL4030-only, and TWL6030-only modules. APIs include `twl_rev()`, class helpers, `twl_set_regcache_bypass()`, multi-byte/single-byte `twl_i2c_*` helpers, 16-bit little-endian helpers, type/version/HFCLK queries, TWL6030 interrupt mask/unmask, `twl4030_sih_setup()`, `twl4030_remove_script()`, and `twl4030_power_off()`. Structs define clock, charger, GPIO, MADC, keypad, USB PHY, power scripts, resource configs, codec/vibra/audio data, and regulator driver hooks. Macros encode GPIO, INTBR, keypad, MADC, charger, PM master, power resources, power-bus messages, and regulator IDs.

## Control Flow
Subdrivers address registers as `{module id, offset}` and the TWL core maps that pair to the proper I2C slave and absolute address. Board power scripts are arrays of encoded power-bus messages downloaded or removed by the PM core, and SIH setup creates nested IRQ handling for shared interrupt blocks.

## State and Persistence Behavior
Hardware state spans module register files, interrupt masks, GPIO direction/debounce/pulls, PM master scripts, power-resource states, charger data, keypad rows/cols, USB PHY settings, clocks, and regulators. Software state is platform data and script/resource configuration consumed at probe.

## Dependencies and Integration Points
The header depends on kernel types and matrix keypad data. It integrates with I2C/regmap core, IRQ/SIH handling, GPIO, keypad, MADC, charger, USB PHY, audio, vibra, regulator, clock, and OMAP power-management code.

## Risks and Test Signals
Risks include wrong module ID to slave mapping, broad exported register constants encouraging cross-driver coupling, endian mistakes in 16-bit helpers, power-bus script errors that affect sleep/wake/reset, and class-specific TWL4030/TWL6030 register confusion. Test signals are I2C helper read/write tests, SIH nested IRQ tests, power script encoding tests, regulator ID mapping tests per chip class, keypad matrix tests, USB PHY callbacks, and suspend/resume power-resource validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl4030-audio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/twl4030-audio.h

## Purpose
`twl4030-audio.h` defines TWL4030 audio codec register offsets, bitfields, codec resource IDs, and resource/MCLK helper APIs used by audio and vibra subdrivers.

## Important APIs, Types, and Functions
The register map covers codec mode, analog/digital mic paths, ADC/DAC controls, audio and voice interfaces, TX/RX PGAs, Bluetooth interface, ear/headset/pre-driver/handsfree outputs, ALC, boost, soft volume, DTMF, APLL, misc settings, PCM/BT muxing, RX path, vibra control, and analog mic gain. Bitfields define APLL sample rates, interface format/width, mic bias and input enables, output gains, pop/ramp delays, APLL input frequencies, smooth volume, FM loop, digital mic swap, and vibra routing. `enum twl4030_audio_res` identifies power and APLL resources. APIs are `twl4030_audio_disable_resource()`, `twl4030_audio_enable_resource()`, and `twl4030_audio_get_mclk()`.

## Control Flow
Codec users enable the shared power/APLL resources before programming audio paths, set codec/APLL rates and interface formats, then enable ADC/DAC/output blocks. Resource helpers mediate shared power/reference use between codec and vibra/audio clients.

## State and Persistence Behavior
Hardware persists codec mode, APLL rate/input, mic bias, analog/digital path enables, interface format, gain, pop/ramp timing, DTMF, vibra control, and misc clock/loop settings. Software state is not declared, except resource IDs used by the implementation.

## Dependencies and Integration Points
The header integrates with the TWL4030 MFD core, ASoC codec driver, vibra driver, clock/MCLK configuration, and audio platform data from `twl.h`.

## Risks and Test Signals
Risks include unsupported APLL rate encodings, failing to enable shared resources before register writes, incorrect interface width/format matching with the CPU DAI, and pop/noise from bad ramp timing. Test signals are ASoC playback/capture path tests, MCLK reporting, resource refcount tests, vibra enable tests, codec register readback for sample rates and format, and suspend/resume audio path restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl4030-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl6040.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/twl6040.h

## Purpose
`twl6040.h` defines the MFD-facing interface for the TWL6040/TWL6041 audio companion chip. It provides register/bit definitions, IRQ IDs, PLL clock selectors, parent device state, register helpers, power and PLL APIs, and revision access.

## Important APIs, Types, and Functions
Registers cover ASIC ID/revision, interrupt ID/mask, charge pump, LDOs, HP/LP PLLs, mic/headset/handsfree/ear/vibra controls, gains, hooks/GPOs, loopback, trims, ACC control, and status. IRQs cover thermal, plug, hook, handsfree, vibra, and ready events. `struct twl6040` stores regmap, IRQ data, regulator supplies, clocks, mutexes, MFD cells, ready completion, optional audio power GPIO, power refcount, revision, PLL/sysclk/mclk rates, and IRQ numbers. APIs include reg read/write, set/clear bits, `twl6040_power()`, `twl6040_set_pll()`, `twl6040_get_pll()`, `twl6040_get_sysclk()`, `twl6040_get_vibralr_status()`, and `twl6040_get_revid()`.

## Control Flow
The parent powers supplies/clocks and waits for `READY` before children use audio paths. PLL selection configures HPPLL or LPPLL from a given input/output rate, while regmap IRQ data maps chip events to Linux IRQs. Power calls use `power_count` to share chip power among children.

## State and Persistence Behavior
Hardware persists PLL, LDO, charge pump, mic/output/vibra/GPO, interrupt mask, loopback, trim, and status bits. Software tracks power refcount, ready completion, revision, selected PLL, clock rates, and IRQ mapping.

## Dependencies and Integration Points
The header depends on interrupt, MFD core, regulator consumer, clock, regmap, GPIO descriptor, mutex, and completion infrastructure. It integrates with ASoC codec, vibra, GPIO, regulator, clock, and interrupt subdrivers.

## Risks and Test Signals
Risks include power refcount imbalance, not waiting for ready before register access, wrong PLL selector for requested rate, stale revision-specific behavior, and IRQ masking races. Test signals are power on/off refcount tests, PLL rate programming tests, ready IRQ/completion tests, vibra status readback, codec audio smoke tests, and suspend/resume with supplies and clocks toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/twl6040.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ucb1x00.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ucb1x00.h

## Purpose
`ucb1x00.h` defines the MFD interface for Philips/NXP UCB1x00 mixed-signal chips attached through MCP/SIB. It covers GPIO, interrupt, audio/telecom, touchscreen, ADC, ID, mode registers, child-driver registration, clock helpers, raw register access, GPIO access, and ADC control.

## Important APIs, Types, and Functions
Register constants include IO data/dir, interrupt rising/falling/status/clear, telecom/audio controls, touchscreen control, ADC control/data, ID, and mode. `struct ucb1x00` stores MCP link, IRQ state, ADC mutex, IO lock/cache, ID, GPIO chip, device, child device lists, and wake/mask state. `struct ucb1x00_driver` provides add/remove/suspend/resume callbacks for child clients. Inline helpers wrap MCP clock enable/disable, clock rate, register read/write, and audio/telecom divisors. Exported APIs register/unregister child drivers, set/read GPIOs, and enable/read/disable ADC.

## Control Flow
The parent MCP driver enables the SIB clock before register access. Child drivers register through the UCB bus list, receive `ucb1x00_dev`, and call GPIO/ADC helpers. ADC reads are serialized by `adc_mutex`; IO direction/output updates are cached and protected by `io_lock`; IRQ enables are tracked separately for rising and falling edges.

## State and Persistence Behavior
Hardware state includes GPIO direction/data, interrupt masks/status, audio/telecom mode, touchscreen bias/mode, ADC conversion state, and mode bits. Software caches IO direction/output, ADC control, IRQ masks/wake state, chip ID, and child driver/device lists.

## Dependencies and Integration Points
The header depends on MCP, device model, GPIO, GPIO driver API, mutexes, spinlocks, and list management. It integrates with touchscreen, ADC, GPIO, audio/telecom, wakeup, and legacy SA-11x0-style MCP infrastructure.

## Risks and Test Signals
Risks include register access without enabling the MCP clock, ADC/GPIO races if locks are bypassed, child driver list lifetime bugs, 16-bit mask misuse, and wake IRQ state mismatches. Test signals are MCP enable/disable balance tests, GPIO direction/value tests, ADC conversion valid-bit polling, touchscreen IRQ tests, child add/remove lifecycle tests, and suspend/resume reset callback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ucb1x00.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/upboard-fpga.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/upboard-fpga.h

## Purpose
`upboard-fpga.h` defines the MFD data structures and register IDs for the UP Board CPLD/FPGA companion device. It supports platform/firmware ID reads, function enable registers, GPIO enable/direction registers, bit-banged control GPIOs, and per-board FPGA metadata.

## Important APIs, Types, and Functions
`UPBOARD_REGISTER_SIZE` sets a 16-bit register width assumption. `enum upboard_fpgareg` names platform ID, firmware ID, function enable, GPIO enable, GPIO direction, and `UPBOARD_REG_MAX`. `enum upboard_fpga_type` distinguishes UP and UP2 FPGA variants. `struct upboard_fpga_data` pairs the type with a regmap configuration. `struct upboard_fpga` stores device, regmap, enable/reset/clear/strobe/datain/dataout GPIO descriptors, firmware version, and variant data.

## Control Flow
The parent driver selects an `upboard_fpga_data` variant, initializes regmap through the variant config, toggles control GPIOs as needed for serial register access, reads firmware/platform IDs, and child drivers use shared regmap/register IDs for function and GPIO enablement.

## State and Persistence Behavior
FPGA registers persist platform/firmware identity, enabled peripheral functions, enabled GPIO banks, and GPIO direction settings. Software keeps the firmware version and live GPIO descriptors for the parent device lifetime.

## Dependencies and Integration Points
The header relies on `struct device`, `struct regmap`, `struct regmap_config`, and GPIO descriptors from includers. It integrates with MFD parent probing, regmap, GPIO, pin/function enable subdrivers, and board-specific ACPI/device-tree matching.

## Risks and Test Signals
Risks include variant regmap mismatch, incorrect 16-bit register assumptions, control GPIO sequencing errors, stale firmware-version compatibility checks, and function-enable bits conflicting with GPIO use. Test signals are platform/firmware ID readback, UP vs UP2 probe tests, GPIO bank enable/direction readback, control GPIO timing tests, and child device probing against enabled functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/upboard-fpga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/viperboard.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/viperboard.h

## Purpose
`viperboard.h` defines USB protocol constants and packed message formats for Nano River Technologies Viperboard MFD support, especially its USB-backed I2C, ADC, and GPIO functions.

## Important APIs, Types, and Functions
Constants define USB IN/OUT endpoints, a 512-byte I2C message limit, I2C bus frequency command values, I2C write/read/address command values, USB control request types, timeout, and vendor request IDs for I2C frequency, I2C transfer, major/minor version, ADC, and GPIO banks. Packed structs describe I2C write/read headers, status response, write/read messages with payload, address messages, and parent `struct vprbrd` containing USB device, mutex, shared transfer buffer, and platform device.

## Control Flow
The USB parent serializes access with `vprbrd.lock`, fills one of the packed request buffers, sends vendor control/bulk transfers to the fixed endpoints/requests, and child platform devices implement I2C/GPIO/ADC behavior using the shared buffer and protocol constants.

## State and Persistence Behavior
Hardware/firmware state includes selected I2C frequency, GPIO bank state, ADC state, and active USB transfer status. Software state is minimal: USB device pointer, one mutex-protected buffer sized for the largest write message, and embedded child platform device.

## Dependencies and Integration Points
The header depends on Linux types and USB APIs. It integrates with the MFD parent, USB core, I2C adapter implementation, GPIO controller, ADC interface, and platform-device child registration.

## Risks and Test Signals
Risks include packed-struct ABI drift, endianness assumptions for unannotated `u16` fields, buffer overrun if payload length exceeds `VPRBRD_I2C_MSG_LEN`, concurrent child transfers without the mutex, and USB timeout handling. Test signals are USB descriptor/probe tests, firmware version requests, I2C transfer tests at each supported frequency, oversized-message rejection, GPIOA/B request tests, ADC request tests, and disconnect-during-transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/viperboard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/registers.h

## Purpose
`wcd934x/registers.h` is the Qualcomm WCD934x audio codec register map and bitfield header. It covers RPM/clock/reset, chip ID/efuse, CPE/DMIC, interrupt controller, analog bias/MBHC/mic bias/headphone/class-H, digital TX/RX paths, companders, boost, sidetone, input/output muxing, SoundWire/Slimbus port registers, and register-window constants.

## Important APIs, Types, and Functions
The file is macro-only. It defines 32 IRQ IDs across four interrupt status groups plus `WCD934X_NUM_IRQS`. Register macros span low codec/RPM pages, analog blocks around `0x0600`, clock and MBHC controls, CDC TX/RX/compander/boost blocks, mux/router blocks, CPR/TLMM/debug blocks, and Slimbus port generator macros. Field masks define MCLK rates, efuse state, DMIC rate, bias/precharge, MBHC detection, mic-bias voltage/enable, headphone PA controls, RX/TX PCM rates, mute/clock/reset bits, boost clocking, and register window selection (`WCD934X_WINDOW_START/LENGTH`).

## Control Flow
Drivers use this header with regmap and codec component code. Probe reads chip ID/efuse, configures clocks and bias, sets up regmap IRQs from the IRQ IDs, programs MBHC/mic bias/headphone paths, and uses generated path/port macros to address repeated TX/RX and Slimbus blocks.

## State and Persistence Behavior
Hardware persists codec clock/reset, efuse sense state, interrupt masks/status/clears, analog bias, MBHC thresholds/results, mic bias voltages, headphone/ear/class-H state, TX/RX path rates/volumes/mutes, compander state, boost state, mux routing, and Slimbus port config. No software state is declared here.

## Dependencies and Integration Points
The header relies on `BIT()` and `GENMASK()` from includers. It integrates with Qualcomm WCD934x MFD/core code, ASoC codec paths, MBHC/headset detection, Slimbus/SoundWire transport, regmap windows, IRQ handling, clocks, and regulators.

## Risks and Test Signals
Risks include duplicate macro definitions, hard-coded repeated-block offsets drifting from hardware, wrong register-window selection for high addresses, IRQ index mismatches, and unsafe analog path ordering causing pops or overcurrent. Test signals are regmap-readable range/window tests, IRQ mask/status/clear tests for all 32 IDs, codec playback/capture path tests, MBHC insertion/button threshold tests, mic-bias voltage readback, Slimbus port config tests, and suspend/resume restoration of clock/bias state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/wcd934x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/wcd934x.h

## Purpose
`wcd934x/wcd934x.h` declares the minimal parent-device state for Qualcomm WCD934x MFD/audio codec support. It connects regmap, device identity, GPIO descriptors, and IRQ bookkeeping to codec child drivers.

## Important APIs, Types, and Functions
`struct wcd934x_ddata` contains the parent `device`, Slimbus device pointer, regmap, reset GPIO descriptor, master-bias GPIO descriptor, device ID, per-IRQ-type counters, and regmap IRQ chip data. There are no function prototypes or register constants in this file; those live in `registers.h`.

## Control Flow
The parent driver creates/populates `wcd934x_ddata`, controls reset and master-bias GPIOs during probe and power sequencing, initializes regmap and IRQ data, and supplies this state to codec/child drivers. IRQ type counters allow software to track interrupt configuration/use per logical type.

## State and Persistence Behavior
Software state includes regmap, reset/mbias GPIO ownership, hardware device ID, IRQ counters, and IRQ chip data for the device lifetime. Hardware state controlled through this struct includes reset line and master-bias enable line; detailed codec register state is external to this header.

## Dependencies and Integration Points
The header depends on Slimbus, GPIO descriptor, IRQ, and regmap APIs. It integrates with Qualcomm WCD934x Slimbus probing, regmap, regmap-irq, reset/bias GPIO handling, and ASoC codec subdrivers.

## Risks and Test Signals
Risks include missing GPIO descriptors on boards that require explicit reset/bias, mismatched device ID with register map assumptions, IRQ count underflow/overflow if not paired, and lifetime issues between Slimbus parent and codec children. Test signals are probe/remove tests with optional GPIOs, reset/bias sequencing tests, device ID readback, IRQ registration/unregistration balance, and codec child probe using populated parent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/wcd934x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/auxadc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/auxadc.h

## Purpose
`wm831x/auxadc.h` defines WM831x auxiliary ADC data/control/comparator bitfields, ADC input IDs, request tracking, and the public asynchronous/synchronous read APIs.

## Important APIs, Types, and Functions
Bitfields cover ADC data source and 12-bit data, AUX enable/convert/sleep/force/rate, input selection bits for calibration/backup/wall/battery/USB/system/battery-temp/chip-temp/AUX1-4, comparator status/enable bits, and comparator source/reference fields. `enum wm831x_auxadc` lists all readable inputs and calibration inputs. `enum wm831x_auxadc_src` names hardware data-source values. `struct wm831x_auxadc_req` stores list node, owner chip, input, completion, data source, and data. APIs are `wm831x_auxadc_read()`, `wm831x_auxadc_read_irq()`, `wm831x_auxadc_read_result()`, `wm831x_auxadc_read_uv()`, `wm831x_auxadc_read_temp()`, and `wm831x_auxadc_read_data()`.

## Control Flow
Callers request a conversion for an input; the implementation queues/serializes requests through the parent auxadc state, starts conversion, completes via IRQ or polling, and returns raw data, microvolts, temperature, or split source/data depending on API. IRQ completion uses `wm831x_auxadc_read_irq()`.

## State and Persistence Behavior
Hardware persists AUX control, selected inputs, comparator thresholds/enables, and latest conversion data. Software request state persists in `struct wm831x_auxadc_req` until completion and parent queues/active masks in `struct wm831x`.

## Dependencies and Integration Points
The header depends on completions, lists, and the parent `struct wm831x`. It integrates with power/charger, thermal, hwmon/IIO-like consumers, interrupt handling, and calibration paths.

## Risks and Test Signals
Risks include reading stale data before source matches requested input, request lifetime misuse for async reads, comparator enable/status confusion, calibration errors in uV/temp helpers, and concurrent conversions without parent locking. Test signals are conversion completion tests, source/data mismatch tests, concurrent request queue tests, uV/temp conversion validation, comparator interrupt tests, and suspend/resume ADC control restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/core.h

## Purpose
`wm831x/core.h` is the main WM831x/WM832x MFD core contract. It defines parent IDs, a large shared register map, selected bitfields, parent state, IRQ helper, device I/O APIs, initialization/suspend/shutdown hooks, regmap config, and OF matching.

## Important APIs, Types, and Functions
Register constants span reset/revision/security, system control, interrupts, GPIO levels, RTC, watchdog, OTP/security key, DC/DC and LDO regulators, charger/status LEDs/current sinks, clock/FLL, unique IDs, and OTP controls. Bitfields include chip/revision IDs, ON-pin control, clock output, XTAL/FLL, and FLL tuning. `enum wm831x_parent` identifies WM8310/11/12/20/21/25/26. `struct wm831x` stores I/O lock, device, regmap, platform data, type, IRQ domain/masks, revision flags, GPIO state caches, AUXADC queue/active state, security key lock, and locked state. APIs include register read/write/lock/unlock/set-bits/bulk-read, device init/suspend/shutdown, IRQ init/exit, AUXADC init, and `wm831x_irq()`.

## Control Flow
Bus frontends instantiate regmap and call `wm831x_device_init()`, which identifies the chip, configures IRQs, initializes children, and records revision flags. Register writes to protected areas are mediated by `wm831x_reg_unlock()`/`wm831x_reg_lock()`. IRQ code maps chip IRQs through an IRQ domain and caches mask values.

## State and Persistence Behavior
Hardware persists regulator, charger, RTC, watchdog, GPIO, clock/FLL, interrupt, OTP, and security state. Software tracks IRQ masks/cache, GPIO pending updates/levels, AUXADC pending/active conversions, soft-shutdown flag, revision capability flags, and security-key lock state.

## Dependencies and Integration Points
The header depends on regmap, IRQ domains, mutexes, regulator and platform data declarations, OF match tables, and AUXADC declarations. It integrates with regulator, RTC, watchdog, GPIO, charger, LED, clock/FLL, AUXADC, IRQ, poweroff/shutdown, and device-tree matching.

## Risks and Test Signals
Risks include protected-register writes without lock sequencing, stale IRQ mask caches, revision flag misuse (`has_gpio_ena`, `has_cs_sts`, charger wake), AUXADC queue races, and broad register-map constants drifting from volatile/readable tables. Test signals are regmap read/write and lock tests, IRQ mask cache synchronization tests, GPIO update flush tests, AUXADC queue tests, device init per parent ID, suspend/shutdown tests, and regulator/RTC/watchdog child probe smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/gpio.h

## Purpose
`wm831x/gpio.h` defines bitfields for WM831x GPIO control registers. It is a small shared header for GPIO direction, pull, interrupt, power-domain, polarity, open-drain, enable/tri-state, function selection, and pull helper values.

## Important APIs, Types, and Functions
The file is macro-only. `WM831X_GPN_DIR`, `WM831X_GPN_PULL_MASK`, `WM831X_GPN_INT_MODE`, `WM831X_GPN_PWR_DOM`, `WM831X_GPN_POL`, `WM831X_GPN_OD`, `WM831X_GPN_ENA`, `WM831X_GPN_TRI`, and `WM831X_GPN_FN_MASK` describe each GPIOx control register. Convenience values `WM831X_GPIO_PULL_NONE`, `WM831X_GPIO_PULL_DOWN`, and `WM831X_GPIO_PULL_UP` encode pull selection in the shared field.

## Control Flow
There are no functions. GPIO/pinctrl drivers compute the GPIO control register address from `core.h` register constants, compose these masks based on requested GPIO direction, pull, interrupt mode, polarity, and alternate function, then update the parent regmap.

## State and Persistence Behavior
Hardware persists each GPIO pin's direction, pull mode, interrupt mode, power domain, polarity, open-drain mode, enable/tri-state state, and function selector. Software state is maintained in the parent `struct wm831x` GPIO caches rather than here.

## Dependencies and Integration Points
This header integrates with WM831x core regmap/IRQ handling, GPIO controller code, pin function configuration, and wake/interrupt policy. It relies on includers to provide the core register addresses and regmap access.

## Risks and Test Signals
Risks include interpreting `GPN_ENA` versus `GPN_TRI` incorrectly on variants, writing pull bits without preserving function bits, polarity mistakes for IRQs, and using unsupported alternate functions. Test signals are GPIO direction/value tests, pull-up/down readback, open-drain tests, interrupt polarity/mode tests, variant tests for enable/tri-state behavior, and suspend/resume retention checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/gpio.h -->
