# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/img,ascii-lcd.yaml

## Purpose
Device-tree schema for ASCII LCD displays on Imagination Technologies boards. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Paul Burton <paulburton@kernel.org> and gives dt-schema a canonical contract for nodes matching `img,boston-lcd`, `mti,malta-lcd`, `mti,sead3-lcd`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum img,boston-lcd, mti,malta-lcd, mti,sead3-lcd), `reg` (items ?..1), `offset` (ref uint32; Offset in bytes to the LCD registers within the system controller). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/img,ascii-lcd.yaml`
- run `make dtbs_check` on DTS files using `img,boston-lcd`, `mti,malta-lcd`, `mti,sead3-lcd`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
