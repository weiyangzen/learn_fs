# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-a1-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson a1 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 62 preprocessor constants. Representative symbols are `GPIOP_0`, `GPIOP_1`, `GPIOP_2`, `GPIOP_3`, `GPIOP_4`, `GPIOP_5`, `GPIOP_6`, `GPIOP_7`, `GPIOP_8`, `GPIOP_9`. The file uses guard `_DT_BINDINGS_MESON_A1_GPIO_H` and has no header dependencies. numeric values span 0..61 across 62 direct numeric defines.

## Control Flow
There is no executable control flow. Pinctrl/GPIO device-tree entries use these names in specifier cells; the C preprocessor resolves them before DTB generation; the matching GPIO or pinctrl driver receives the resulting integer offset.

## State, Persistence, and Dependencies
The header has no mutable state or persistence logic. The persistent contract is the numeric namespace encoded into DTBs and expected by the platform GPIO/pinctrl driver. Integration is through DTS includes under the same SoC family, gpio-ranges and pinctrl bindings, and platform drivers that map these offsets to register banks or port/pin tuples.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Risks are off-by-one numbering, bank-boundary mistakes, duplicate values, and renumbering a published pin. Those errors route interrupts or GPIO consumers to the wrong hardware line.

## Test Signals
Useful signals are dtbs_check coverage, DTS compile coverage for every symbolic pin group, driver probe on boards using first/last pins in each bank, and duplicate-value scans across the header.
