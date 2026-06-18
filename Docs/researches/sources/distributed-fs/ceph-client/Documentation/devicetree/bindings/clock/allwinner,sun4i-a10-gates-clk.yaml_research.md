# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-gates-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Bus Gates Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-gates-clk`, `allwinner,sun4i-a10-axi-gates-clk`, `allwinner,sun4i-a10-ahb-gates-clk`, `allwinner,sun5i-a10s-ahb-gates-clk`, `allwinner,sun5i-a13-ahb-gates-clk`, `allwinner,sun7i-a20-ahb-gates-clk`, `allwinner,sun6i-a31-ahb1-gates-clk`, `allwinner,sun8i-a23-ahb1-gates-clk`, `allwinner,sun9i-a80-ahb0-gates-clk`, `allwinner,sun9i-a80-ahb1-gates-clk`, plus 21 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 1; This additional argument passed to that clock is the offset of the bit controlling this particular g), `clock-indices` (items 1..64), `clock-output-names` (items 1..64). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-indices`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-gates-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-gates-clk`, `allwinner,sun4i-a10-axi-gates-clk`, `allwinner,sun4i-a10-ahb-gates-clk`, `allwinner,sun5i-a10s-ahb-gates-clk`, `allwinner,sun5i-a13-ahb-gates-clk`, `allwinner,sun7i-a20-ahb-gates-clk`, `allwinner,sun6i-a31-ahb1-gates-clk`, `allwinner,sun8i-a23-ahb1-gates-clk`, `allwinner,sun9i-a80-ahb0-gates-clk`, `allwinner,sun9i-a80-ahb1-gates-clk`, plus 21 more
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
