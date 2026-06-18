# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/holtek,ht16k33.yaml

## Purpose
Device-tree schema for Holtek HT16K33 RAM mapping 16*8 LED controller with keyscan. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Robin van der Gracht <robin@protonic.nl> and gives dt-schema a canonical contract for nodes matching `adafruit,3108`, `adafruit,3130`, `holtek,ht16k33`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `refresh-rate-hz` (items ?..1; Display update interval in Hertz for dot-matrix displays), `debounce-delay-ms`, `linux,keymap`, `linux,no-autorepeat` (Disable keyrepeat), `default-brightness-level` (Initial brightness level), `led` (ref common.yaml#). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/input/input.yaml#, /schemas/input/matrix-keymap.yaml#, /schemas/leds/common.yaml#, example includes dt-bindings/input/input.h, dt-bindings/interrupt-controller/irq.h, dt-bindings/leds/common.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/holtek,ht16k33.yaml`
- run `make dtbs_check` on DTS files using `adafruit,3108`, `adafruit,3130`, `holtek,ht16k33`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
