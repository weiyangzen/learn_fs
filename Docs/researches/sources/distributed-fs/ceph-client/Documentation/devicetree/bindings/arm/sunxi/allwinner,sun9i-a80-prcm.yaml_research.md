# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun9i-a80-prcm.yaml

## Purpose
Device-tree schema for Allwinner A80 PRCM. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun9i-a80-prcm`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun9i-a80-prcm), `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/sunxi/allwinner,sun9i-a80-prcm.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun9i-a80-prcm`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
