<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c

## Purpose
`sun4i-ts.c` drives the Allwinner sun4i/sun5i/sun6i resistive touchscreen and temperature sensor block. It deliberately exposes reliable single-touch input only, while also registering hwmon and thermal-zone temperature interfaces for the shared ADC sensor.

## Important APIs, Types, And Functions
`struct sun4i_ts_data` stores the device, optional input device, MMIO base, IRQ, FIFO-ignore flag, last temperature sample, and temperature conversion coefficients. `sun4i_ts_irq()` handles both touch and temperature interrupts. `sun4i_ts_irq_handle_input()` reads X/Y FIFO samples, ignores the first sample after an up event, reports `BTN_TOUCH`, and handles releases. `sun4i_get_temp()` converts raw ADC temperature data into millidegrees using SoC-specific formulas. `sun4i_ts_probe()` configures MMIO registers, optional input, hwmon, and thermal.

## Control Flow
Probe sets temperature coefficients by compatible string, checks `allwinner,ts-attached`, optionally allocates a `BUS_HOST` input device, maps MMIO, requests IRQ, configures ADC clock/acquisition, touch sensitivity, filter type, temperature period, stylus debounce, and touch mode. It registers hwmon groups and a thermal OF zone, enables temperature IRQs, and registers input if a panel is attached. Input open enables temp/data/up IRQs and flushes FIFO; close leaves only temp IRQ enabled.

## State And Persistence
The driver maintains `ignore_fifo_data` to suppress stale coordinates after pen-up and `temp_data` initialized to `-1` until the first temperature IRQ. Register programming is redone only at probe; there is no PM callback in this file. Hardware state is disabled in remove.

## Dependencies And Integration Points
It integrates with OF platform matching, MMIO register access, input core, hwmon sysfs (`temp1_input`, `temp1_label`), thermal OF zones, and Allwinner-specific DT properties (`allwinner,ts-attached`, `allwinner,tp-sensitive-adjust`, `allwinner,filter-type`).

## Risks
Temperature conversion for some SoCs is based on approximate or external formulas and is documented as inaccurate. If no touchscreen is attached, only thermal/hwmon paths are active. FIFO handling assumes each data-pending interrupt has X followed by Y. The single-touch policy ignores hardware dual-touch because reported dual coordinates are considered unusable.

## Test Signals
Test with and without `allwinner,ts-attached`, verify hwmon and thermal reads after first IRQ, confirm first coordinate after release is ignored, exercise touch down/up interrupts, validate compatible-specific temp coefficients, and check remove disables interrupt masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c -->
