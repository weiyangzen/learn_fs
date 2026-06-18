# sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq32k.c

## Purpose
TI BQ32000 I2C RTC driver. It exposes basic RTC read/set operations, initializes oscillator and optional trickle charger settings from device tree, and adds a sysfs control for the trickle-charge FET bypass bit.

## Important APIs, types, and functions
- `struct bq32k_regs` mirrors the seven contiguous time registers from seconds through years.
- `bq32k_read()` and `bq32k_write()` implement offset-prefixed I2C transfers. Writes use a fixed `MAX_LEN + 1` stack buffer, so all callers must keep transfer length within the hardware register span.
- `bq32k_rtc_read_time()` reads the register block, rejects oscillator failure via `BQ32K_OF`, and decodes BCD fields plus the century bit.
- `bq32k_rtc_set_time()` encodes `struct rtc_time`, enables century tracking, sets the century bit when `tm_year >= 100`, and writes the full register block.
- `trickle_charger_of_init()` recognizes `trickle-resistor-ohms` and `trickle-diode-disable` combinations, then programs `BQ32K_CFG2` and `BQ32K_TCH2`.
- `bq32k_sysfs_show/store_tricklecharge_bypass()` exposes `trickle_charge_bypass` by reading/updating `BQ32K_TCFE`.
- `bq32k_probe()` checks I2C functionality, clears `BQ32K_STOP`, warns on `BQ32K_OF`, applies trickle charger DT setup, registers the RTC, and creates sysfs.

## Control flow
Probe performs hardware readiness checks before registration. Runtime RTC operations go directly through the `rtc_class_ops` table. Removal only removes the sysfs file because device-managed registration and allocations handle the rest.

## State and persistence behavior
Persistent state is entirely in battery-backed BQ32000 registers: time/date, century state, oscillator failure/stop flags, trickle charger configuration, and bypass bit. The driver holds no private runtime state beyond the registered `rtc_device` pointer in client data. `BQ32K_OF` is not cleared by reads; setting time rewrites minutes and effectively clears the flag.

## Dependencies and integration points
Depends on Linux I2C, RTC class, BCD helpers, sysfs device attributes, and OF properties. Integrates through `module_i2c_driver()`, `i2c_device_id` `"bq32000"`, and OF compatible `"ti,bq32000"`.

## Risks
- `bq32k_write()` does not locally validate `len <= MAX_LEN`; current callers are safe, but future writes must respect it.
- Sysfs writes parse arbitrary integers as truthy/falsy and do not serialize with concurrent RTC operations beyond I2C bus serialization.
- Trickle charger DT validation is strict and returns an error for unsupported resistor/diode combinations, which can fail probe if the property is wrong.
- Time validity depends on the oscillator failure flag and battery condition.

## Test signals
Useful signals are successful probe, warning logs for oscillator stop/failure, `hwclock` read/set behavior, sysfs `trickle_charge_bypass` read/write, DT trickle charger cases, and I2C error injection on the offset read/write helpers.
