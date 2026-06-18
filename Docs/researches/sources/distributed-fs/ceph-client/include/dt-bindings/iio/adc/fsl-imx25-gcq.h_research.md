# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/fsl-imx25-gcq.h

## Purpose
defines IIO channel, mode, or configuration constants for the fsl imx25 gcq binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 8 macro constants. Representative symbols are `MX25_ADC_REFP_YP`, `MX25_ADC_REFP_XP`, `MX25_ADC_REFP_EXT`, `MX25_ADC_REFP_INT`, `MX25_ADC_REFN_XN`, `MX25_ADC_REFN_YN`, `MX25_ADC_REFN_NGND`, `MX25_ADC_REFN_NGND2`. numeric values span 0..3 across 8 direct numeric defines. Top naming groups: `MX25_ADC` (8).

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
