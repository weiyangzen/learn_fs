# sources/distributed-fs/ceph-client/include/linux/ds2782_battery.h

## Purpose
This header declares platform data for DS278x battery fuel gauge drivers.

## Important APIs, types, and functions
The only type is `struct ds278x_platform_data`, with `int rsns` representing the sense resistor value or related board-specific calibration.

## Control flow, state, and persistence
No runtime logic is present. The platform data is supplied by board code or device setup and consumed during driver probe.

## Dependencies and integration points
It has no external includes. It integrates with legacy platform-data based battery/power-supply drivers.

## Risks and test signals
The main risk is unit ambiguity or an unset resistor value causing wrong current/capacity calculations. Tests should verify probe behavior with valid, missing, and boundary `rsns` values and compare reported power-supply properties against calibration data.
