# sources/distributed-fs/ceph-client/drivers/power/supply/lp8727_charger.c

## Purpose
This I2C driver supports the TI/National LP8727 micro/mini USB IC with integrated charger. It detects attached power source type, controls DP/DM switch routing, configures charger parameters for AC or USB, and registers `ac`, `usb`, and `main_batt` power supplies.

## Important APIs, Types, and Functions
`struct lp8727_chg` stores device/client pointers, an I2C transfer mutex, registered supplies, platform data, detected device ID, selected charge parameters, IRQ number, delayed debounce work, and debounce duration. `lp8727_init_device()` clears interrupts and enables charge pump, ADC, ID200, interrupts, and charger detection. `lp8727_id_detection()` decodes ID/VBUS interrupt bits into TA, dedicated charger, USB charger, USB downstream, or none, chooses AC/USB charge parameters, and routes DP/DM. `lp8727_delayed_func()` reads interrupt registers after debounce, runs detection, re-enables charger detection, and notifies all supplies. Battery and charger property callbacks report online/status/health plus optional platform callback telemetry.

## Control Flow
Probe checks SMBus block support, parses DT or platform data for debounce and per-source charge params, allocates state, initializes hardware, registers three supplies, and requests a falling-edge threaded IRQ if present. The IRQ schedules delayed work instead of reading registers immediately.

## State and Persistence
Detected source type and active charge parameters persist in `devid` and `chg_param`. Hardware control registers persist switch routing and charger-control values. Battery voltage/capacity/temp/presence are not stored by this driver and are delegated to platform callbacks when present.

## Dependencies and Integration Points
It depends on I2C SMBus block operations, optional OF child nodes with `charger-type`, `eoc-level`, and `charging-current`, legacy `lp8727_platform_data`, IRQ lines, and the power-supply core. The battery descriptor uses `external_power_changed` to write selected charge current/EOC values.

## Risks
Several helper reads ignore return values and use the output byte regardless, so I2C failures can be misclassified. Battery property cases with missing callbacks return success without setting `val`, which can leak stale data to callers. `lp8727_parse_dt()` does not guard failed `of_property_read_string()` before `strcmp()`. The source detection state is IRQ/work driven and may be stale until an interrupt arrives.

## Test Signals
Validate register init, IRQ debounce, ID 0x5 and 0xB flows, DCP/USB/downstream routing, charge parameter writes on external-power change, absent IRQ polling behavior, DT parsing including malformed child nodes, high-temperature health mapping, and I2C error handling in detection helpers.
