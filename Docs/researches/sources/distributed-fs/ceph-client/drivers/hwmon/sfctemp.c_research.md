# sources/distributed-fs/ceph-client/drivers/hwmon/sfctemp.c

Purpose: platform hwmon driver for StarFive JH7100/JH7110 temperature sensors. It controls clocks/resets/power state and exposes temperature plus enable control.

Important APIs/types/functions: `struct sfctemp` stores MMIO base, sense/bus clocks, sense/bus resets, and enabled state. `sfctemp_enable()` sequences clocks, resets, power-up, and run. `sfctemp_disable()` stops conversion and powers down. `sfctemp_convert()` reads DOUT and applies fixed calibration.

Control flow: probe maps registers, acquires clocks/resets, asserts resets, registers a cleanup action, enables the sensor, and registers hwmon. Runtime writes to `temp_enable` call enable/disable; reads return enabled state or converted temperature.

State and persistence: enabled state mirrors hardware sequencing. Cleanup disables sensor on device removal. No measurement cache exists.

Dependencies/integration: platform MMIO, clk, reset controls, hwmon, OF matching.

Risks: no lock protects concurrent enable/read/write. Conversion assumes fixed constants for both compatible strings. `temp_input` returns `-ENODATA` when disabled. Probe leaves sensor enabled by default.

Test signals: clock/reset error unwinds, enable/disable sysfs behavior, DOUT conversion sanity, remove cleanup, and both StarFive compatibles.
