# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3403_thermal.c

## Purpose

`int3403_thermal.c` supports ACPI INT3403/INTC thermal participants. Depending on firmware type, it registers either a sensor-backed INT340x thermal zone or a charger/battery cooling device controlled through ACPI performance methods.

## Important APIs, Types, and Functions

`struct int3403_priv` records the platform device, ACPI device, participant type, and private sensor/cooling object. `int3403_sensor_add()` creates an INT340x zone and ACPI notify handler. `int3403_cdev_add()` evaluates `PPSS`, derives `max_state`, and registers a thermal cooling device with `int3403_cooling_ops`. Cooling callbacks use `PPPC` for current state and `SPPC` for setting state. `int3403_notify()` reacts to thermal event `0x90` and trip-point-changed event `0x81`.

## Control Flow

Probe first tries `_TMP`; success implies a sensor participant. Without `_TMP`, it reads `PTYP` and dispatches chargers and batteries to cooling-device setup. Sensor notifications update the thermal zone on violations and reread trips on performance trip changes. Removal chooses the matching teardown path by participant type.

## State and Persistence Behavior

State is per platform device and devm-managed except registered thermal objects. Firmware owns actual temperature, trip, and performance state; this driver only mirrors it through ACPI and Linux thermal abstractions.

## Dependencies and Integration Points

Dependencies are ACPI methods `_TMP`, `PTYP`, `PPSS`, `PPPC`, `SPPC`, Linux thermal zones/cooling devices, and `int340x_thermal_zone`. The ACPI ID table includes INT3403 plus several INTC IDs for newer platform participants.

## Risks and Test Signals

Risks include malformed `PPSS` packages, unsupported `PTYP`, missing notify removal on partial setup, and treating package count minus one as max cooling state without validating full package contents. Test signals include sensor and cooling-device probe variants, ACPI notify `0x81` trip refresh, `PPPC`/`SPPC` state round trips, and removal after both participant classes.
