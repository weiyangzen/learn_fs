<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig

## Purpose
Defines the Intel Skylake INT3472 camera power-controller support option.

## Important Symbol
`INTEL_SKL_INT3472` is a tristate depending on ACPI, COMMON_CLK, I2C, GPIOLIB, LEDS_CLASS, and REGULATOR; it selects MFD core and I2C regmap.

## Control Flow And State
Build selection enables both discrete GPIO/power-gate and TPS68470 PMIC implementations plus a shared common library. Runtime behavior depends on ACPI `INT3472` device type and CLDB data.

## Dependencies And Integration Points
Integrates ACPI camera power controllers with clk, regulator, GPIO, LED, MFD, I2C, and sensor driver lookup mechanisms.

## Risks And Test Signals
Risks are incorrect built-in/module choices on ChromeOS-style systems where OpRegion/GPIO support must exist before sensor probing. Test built-in and module builds plus camera probe order on ChromeOS and Windows-designed hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig -->
