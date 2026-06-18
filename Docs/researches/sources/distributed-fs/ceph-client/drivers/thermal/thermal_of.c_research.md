# sources/distributed-fs/ceph-client/drivers/thermal/thermal_of.c

## Purpose
`thermal_of.c` parses Device Tree thermal-zone descriptions and registers thermal zones tied to sensor devices through resource-managed helpers.

## Important APIs, Types, and Functions
Important helpers parse trip types/properties, locate the thermal zone that references a sensor phandle/id, read polling delays and zone parameters, match cooling maps, and register/unregister OF-backed zones. Public APIs are `devm_thermal_of_zone_register` and `devm_thermal_of_zone_unregister`.

## Control Flow
Registration finds the `thermal-zones` child that references the caller's sensor and id, allocates trip descriptors from the `trips` subnode, reads polling delay properties, initializes `thermal_zone_params` from `sustainable-power` and `coefficients`, installs OF `should_bind`, optionally maps `critical-action` to reboot/shutdown callbacks, registers with trips, frees temporary trip storage, and enables the zone. Cooling binding later resolves the zone by name, walks `cooling-maps`, matches the trip phandle and cdev OF node, and returns lower/upper state limits plus contribution weight.

## State and Persistence Behavior
Device nodes are reference-counted and trips are copied into thermal-core state. Devres owns the registration cleanup; unregister disables and unregisters the zone. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on OF phandle parsing, thermal core registration with trips, thermal zone params, cooling-device maps, and critical reboot/shutdown helpers. Platform sensor drivers call it after setting their `.get_temp` operations.

## Risks and Edge Cases
Malformed DT can fail registration through missing `temperature`, `hysteresis`, `type`, `thermal-sensors`, or cooling cells. The framework currently treats coefficients as slope/offset for one sensor, so multi-sensor zone modeling is limited.

## Test Signals
DT schema/probe tests for valid and malformed thermal zones, cooling-map binding tests, critical-action behavior, trip sysfs visibility after registration, and devm unregister on probe failure/remove.
