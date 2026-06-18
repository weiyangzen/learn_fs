# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adi,ad5592r.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad5592r binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 9 macro constants. Representative symbols are `CH_MODE_UNUSED`, `CH_MODE_ADC`, `CH_MODE_DAC`, `CH_MODE_DAC_AND_ADC`, `CH_MODE_GPIO`, `CH_OFFSTATE_PULLDOWN`, `CH_OFFSTATE_OUT_LOW`, `CH_OFFSTATE_OUT_HIGH`, `CH_OFFSTATE_OUT_TRISTATE`. numeric values span 0..8 across 9 direct numeric defines. Top naming groups: `CH_MODE` (5), `CH_OFFSTATE` (4).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
