<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c

## Purpose
Provides clock and GPIO-backed regulator registration helpers for INT3472 discrete camera power controllers.

## Important APIs, Types, And Functions
`skl_int3472_enable_clk()` toggles either a GPIO or an ACPI DSM image-clock control. `skl_int3472_register_clock()` registers a clock with clkdev lookup for the sensor device, deriving frequency from the sensor `SSDB` buffer. `skl_int3472_register_dsm_clock()` and `skl_int3472_register_gpio_clock()` select DSM or GPIO control. `skl_int3472_register_regulator()` creates GPIO-enabled regulators with lower/upper-case supply aliases and optional second sensor consumer.

## Control Flow
GPIO resources parsed by `discrete.c` call into this file when a GPIO is a clock enable or power rail. Clocks toggle in `.prepare/.unprepare` because GPIO operations can sleep. Regulators use empty ops with `ena_gpiod` and status-change constraints.

## State And Persistence
State is embedded in `int3472_discrete_device`: clock handle, clkdev lookup, enable GPIO, regulator descriptors, supply maps, and registered regulator devices. Hardware GPIO/DSM state follows framework enable counts.

## Dependencies And Integration Points
Depends on ACPI DSM, clk provider/clkdev, GPIO descriptors, regulator core, and INT3472 platform data definitions.

## Risks And Test Signals
Risks include incorrect sensor name lookups, clock frequency read failures returning zero, supply-name length limits, duplicate clock registration, and GPIO ownership cleanup. Test sensor driver `clk_get()`, regulator consumer lookup with case variants, power sequencing delays, and cleanup after probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c -->
