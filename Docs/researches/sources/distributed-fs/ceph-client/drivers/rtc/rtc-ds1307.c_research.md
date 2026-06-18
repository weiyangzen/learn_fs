# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1307.c

## Purpose
Large compatibility I2C RTC driver for DS1307-family and similar chips, including DS1307/1308/1337/1338/1339/1340/1341/1388/3231, M41T variants, MCP794xx, RX8025, RX8130, PT7C4338, and ISL12057 mappings. It handles core timekeeping, variant alarms, oscillator/status quirks, trickle charger setup, NVRAM, M41T offset/frequency test, DS3231 hwmon and common-clock outputs, and DS1388 watchdog support.

## Important APIs, types, and functions
- `enum ds_type` identifies supported chip families.
- `struct ds1307` stores variant type, device, regmap, name, RTC device, and optional common-clock hardware.
- `struct chip_desc` records per-variant alarm support, NVRAM offset/size, register offset, century handling, backup square-wave bits, IRQ handler, RTC ops table, trickle charger register/setup callback, and charger policy flags.
- `ds1307_get_time()` bulk-reads seven time registers at variant offset, validates oscillator/status bits per chip, decodes BCD date/time, handles RX8130 weekday bit-position format, and optional century support.
- `ds1307_set_time()` validates range, encodes BCD fields, sets century bits where available, clears oscillator-failure bits for several variants, starts MCP794xx oscillator/VBAT, writes the register block, and clears RX8130 voltage-loss flag.
- DS1337-style alarm ops read/write ALARM1/ALARM2/status/control registers and use A1IE/A1I.
- RX8130 alarm ops use minute/hour/day alarm registers, extension/flag/control registers, minute precision, and `rx8130_irq()`.
- MCP794xx alarm ops use alarm 0 registers, compute weekday from current RTC time, clear interrupt flag, and toggle `MCP794XX_BIT_ALM0_EN`.
- `m41txx_rtc_read_offset()` and `set_offset()` expose calibration offset in ppb using positive/negative step sizes.
- DS1388 watchdog ops start/stop/ping/set timeout through watchdog registers and register a watchdog device when enabled.
- `chips[]`, `ds1307_id[]`, and `ds1307_of_match[]` map device IDs/OF compatibles to variant descriptors.
- `ds1307_irq()` handles generic DS1337-like alarm IRQs by clearing status and disabling A1IE.
- `frequency_test` sysfs group is added for M41T variants.
- `ds1307_nvram_read/write()` expose variant NVRAM ranges via RTC nvmem.
- `ds1307_trickle_init()` interprets `trickle-resistor-ohms`, `aux-voltage-chargeable`, and deprecated `trickle-diode-disable`.
- DS3231 hwmon reads temperature registers in 0.25 C units.
- DS3231 common-clock support registers square-wave and 32 kHz clocks, avoiding SQW registration when the alarm feature uses the shared pin.
- `ds1307_probe()` creates regmap, selects variant, configures trickle charging, initializes oscillator/control/status quirks, converts 12-hour to 24-hour mode where needed, sets alarm/wakeup feature flags, requests IRQ, registers RTC, NVRAM, hwmon, clocks, and watchdog.

## Control flow
Probe is variant-driven: identify chip, apply optional charger setup, handle variant-specific oscillator/control/status cleanup, read base time registers, normalize hour mode, allocate/register RTC, request IRQ if alarm-capable, then attach optional subsystems. Runtime calls are selected by `chip_desc.rtc_ops` or the generic DS13xx ops. Alarm IRQ paths clear status and disable the alarm to preserve one-shot RTC semantics.

## State and persistence behavior
Persistent state lives in chip registers: time, status/oscillator flags, alarms, control bits, trickle charger, NVRAM/SRAM, calibration, temperature registers, clock-output enable bits, and watchdog registers. Software stores variant metadata, regmap, RTC device, and common-clock handles. Several paths update persistent status bits during probe or set-time, such as clearing oscillator failure flags and enabling battery-backed oscillator bits.

## Dependencies and integration points
Depends on I2C, regmap, RTC class, device properties/OF, nvmem, optional hwmon, optional common clock provider, optional watchdog core, and BCD helpers. Integration is broad: I2C ID table, OF compatible table, optional wakeup-source property, IRQs, RTC features, sysfs attributes, nvmem registration, hwmon registration, clock provider, and watchdog registration.

## Risks
- Very broad variant surface creates high regression risk from shared code changes.
- Oscillator-failure handling differs by chip; some reads return `-EINVAL`, some only warn/clear during probe/set-time.
- Century support depends on build option and chip bits; range is 2000-2099 unless century support and hardware allow beyond.
- Alarm semantics vary by variant: DS1337 full second/min/hour/day, RX8130 minute precision, MCP794xx computed weekday, shared SQW/alarm pin conflicts.
- Trickle charger DT settings can alter battery/supercap charging policy and must match hardware.
- Optional subsystems may silently not register on configuration or hardware constraints.
- The source shown contains duplicated-looking declarations in `ds1307_probe()` in this tree snapshot; compilation should confirm whether this is an artifact or actual issue.

## Test signals
Variant matrix probe tests, oscillator failure flags, set/read time across 1999/2099/2100 boundaries with/without century config, each alarm implementation and IRQ path, wakeup-source without IRQ, NVRAM read/write offsets, M41T offset and frequency_test sysfs, DS3231 temperature and clocks, DS1388 watchdog lifecycle, trickle charger DT permutations, and regmap error injection.
