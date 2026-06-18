# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6363-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6363 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 16 macro constants. Representative symbols are `MT6363_AUXADC_BATADC`, `MT6363_AUXADC_VCDT`, `MT6363_AUXADC_BAT_TEMP`, `MT6363_AUXADC_CHIP_TEMP`, `MT6363_AUXADC_VSYSSNS`, `MT6363_AUXADC_VTREF`, `MT6363_AUXADC_VCORE_TEMP`, `MT6363_AUXADC_VPROC_TEMP`, `MT6363_AUXADC_VGPU_TEMP`, `MT6363_AUXADC_VIN1`. numeric values span 0..15 across 16 direct numeric defines. Top naming groups: `MT6363_AUXADC` (16).

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
