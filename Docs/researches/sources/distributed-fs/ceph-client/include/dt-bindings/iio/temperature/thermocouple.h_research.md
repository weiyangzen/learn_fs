# sources/distributed-fs/ceph-client/include/dt-bindings/iio/temperature/thermocouple.h

## Purpose
defines thermocouple type identifiers for IIO temperature sensor bindings.

## Important APIs, Types, and Functions
The exported API is 8 macro constants. Representative symbols are `THERMOCOUPLE_TYPE_B`, `THERMOCOUPLE_TYPE_E`, `THERMOCOUPLE_TYPE_J`, `THERMOCOUPLE_TYPE_K`, `THERMOCOUPLE_TYPE_N`, `THERMOCOUPLE_TYPE_R`, `THERMOCOUPLE_TYPE_S`, `THERMOCOUPLE_TYPE_T`. numeric values span 0..7 across 8 direct numeric defines. Top naming groups: `THERMOCOUPLE_TYPE` (8).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with thermocouple-capable IIO sensor bindings and drivers that select conversion tables by type.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Changing numeric type ids or accepting invalid combinations can make temperature conversion use the wrong thermocouple curve.

## Test Signals
DTS compile tests and driver unit/probe tests should check each type maps to the intended conversion behavior.
