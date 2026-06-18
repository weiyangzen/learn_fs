# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/gpio.h

## Purpose
defines the generic GPIO active level, single-ended/open-drain/open-source, sleep retention, pull-up/down, and transitory flags used in the flag cell of GPIO Devicetree specifiers.

## Important APIs, Types, and Functions
The exported API is a set of bit-mask macros such as `GPIO_ACTIVE_HIGH`, `GPIO_ACTIVE_LOW`, `GPIO_OPEN_DRAIN`, `GPIO_OPEN_SOURCE`, `GPIO_PULL_UP`, and `GPIO_PULL_DOWN`. `GPIO_ASIS` is the all-zero default.

## Control Flow
There is no executable flow. DTS/DTSI files encode these macros in GPIO phandles; the Devicetree compiler substitutes constants; GPIO library parsing code later interprets the bits.

## State, Persistence, and Dependencies
The header stores no runtime state. Persistence is the ABI value baked into compiled device trees, so bit positions must remain stable. It has only its include guard and is consumed by board DTS files, GPIO controller bindings, and kernel GPIO-of translation helpers.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The risk is ABI drift: changing bit assignments breaks existing DTBs. Combining mutually exclusive flags such as open-drain and open-source also depends on downstream validation.

## Test Signals
Compile representative DTS users and verify `of_get_named_gpiod_flags()` or equivalent consumers decode polarity, drive mode, sleep, and pull flags as expected.
