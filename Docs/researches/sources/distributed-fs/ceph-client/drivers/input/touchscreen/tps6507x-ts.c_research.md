<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c

## Purpose
`tps6507x-ts.c` is the touchscreen child driver for TPS65070/073/731/732 PMICs with a 10-bit touchscreen ADC. It exposes a polled single-touch input device, reads pressure/X/Y through the parent MFD register operations, and returns the ADC to standby after each poll so the PMIC touch interrupt path remains usable.

## Important APIs, Types, And Functions
`struct tps6507x_ts` stores the device, input device, parent `struct tps6507x_dev`, physical path, current `ts_event`, minimum pressure threshold, and pen-down state. `tps6507x_read_u8()` and `tps6507x_write_u8()` wrap parent MFD callbacks. `tps6507x_adc_conversion()` selects a touchscreen channel, starts conversion, polls the start bit until completion, and reads the 10-bit result from two ADC result registers. `tps6507x_adc_standby()` restores standby and waits for `TPS6507X_REG_TSC_INT` to clear. `tps6507x_ts_poll()` is the input polling handler.

## Control Flow
Probe obtains parent PMIC data and board/platform touchscreen init data, allocates state/input, sets min pressure from platform data or default, configures BUS_I2C identity, ABS_X/ABS_Y/ABS_PRESSURE ranges `0..1023`, calls ADC standby, installs input polling, sets poll interval from platform data or 30 ms, and registers input. On each poll, pressure is read first. If pressure falls below threshold and the driver believed the pen was down, it reports release. If pressure is above threshold, it reads X and Y, reports down if needed, reports coordinates and pressure, syncs, marks pen down, then always returns the ADC to standby.

## State And Persistence
State is volatile. Board data supplies optional IDs, poll interval, and pressure threshold. The ADC mode is repeatedly changed during polling and restored to standby each time. There are no sysfs controls or PM hooks in this child driver.

## Dependencies And Integration Points
It integrates with the TPS6507x MFD API, legacy platform data (`tps6507x_board` and `touchscreen_init_data`), input polling, and platform-driver registration. It is not DT/property-driven in this file.

## Risks
Conversion polling is a busy loop without an explicit timeout; a stuck `START_CONVERSION` bit can hang the polling callback. Probe requires platform data and returns `-ENODEV` if absent. The driver ignores direct PMIC interrupts and relies on polling. ADC standby errors after a failed conversion are not surfaced to input users.

## Test Signals
Validate platform data presence/defaults, pressure threshold transitions, ADC channel reads for pressure/X/Y, standby after every poll, stuck conversion behavior, poll interval configuration, and input release when pressure drops below threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c -->
