# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun4i-a10-mbus.yaml

## Purpose
The MBUS controller drives the MBUS that other devices in the SoC will use to perform DMA. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun5i-a13-mbus`, `allwinner,sun8i-a33-mbus`, `allwinner,sun8i-a50-mbus`, `allwinner,sun8i-a83t-mbus`, `allwinner,sun8i-h3-mbus`, `allwinner,sun8i-r40-mbus`, `allwinner,sun8i-v3s-mbus`, `allwinner,sun8i-v536-mbus`, `allwinner,sun20i-d1-mbus`, `allwinner,sun50i-a64-mbus`, plus 5 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun5i-a13-mbus, allwinner,sun8i-a33-mbus, allwinner,sun8i-a50-mbus, allwinner,sun8i-a83t-mbus...), `reg` (items 1..?), `reg-names` (items 1..?), `interrupts` (items ?..1; MBUS PMU activity interrupt.), `clocks` (items 1..?), `clock-names` (items 1..?), `#address-cells`, `#size-cells`, `#interconnect-cells` (const 1; The content of the cell is the MBUS ID.), `dma-ranges` (See section 2.3.9 of the DeviceTree Specification.). Required properties are `#interconnect-cells`, `compatible`, `reg`, `clocks`, `dma-ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/sun50i-a64-ccu.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/sunxi/allwinner,sun4i-a10-mbus.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun5i-a13-mbus`, `allwinner,sun8i-a33-mbus`, `allwinner,sun8i-a50-mbus`, `allwinner,sun8i-a83t-mbus`, `allwinner,sun8i-h3-mbus`, `allwinner,sun8i-r40-mbus`, `allwinner,sun8i-v3s-mbus`, `allwinner,sun8i-v536-mbus`, `allwinner,sun20i-d1-mbus`, `allwinner,sun50i-a64-mbus`, plus 5 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
