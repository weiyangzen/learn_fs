# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/gpio-7-segment.yaml

## Purpose
Device-tree schema for GPIO based LED segment display. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Chris Packham <chris.packham@alliedtelesis.co.nz> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const gpio-7-segment), `segment-gpios` (items 7..8; An array of GPIOs one per segment.). Required properties are `segment-gpios`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/gpio/gpio.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/gpio-7-segment.yaml`
- run `make dtbs_check` on DTS files using `gpio-7-segment` nodes
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
