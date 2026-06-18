# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/sifive,ccache0.yaml

## Purpose
The SiFive Composable Cache Controller is used to provide access to fast copies of memory for masters in a Core Complex. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Paul Walmsley <paul.walmsley@sifive.com> and gives dt-schema a canonical contract for nodes matching `sifive,ccache0`, `sifive,fu540-c000-ccache`, `sifive,fu740-c000-ccache`, `eswin,eic7700-l3-cache`, `starfive,jh7100-ccache`, `starfive,jh7110-ccache`, `microchip,mpfs-ccache`, `microchip,pic64gx-ccache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items 3..?), `cache-block-size` (const 64), `cache-level` (enum 2, 3), `cache-sets` (enum 1024, 2048, 4096), `cache-size` (enum 2097152, 4194304), `cache-unified`, `next-level-cache`, `memory-region` (items ?..1; The reference to the reserved-memory for the L2 Loosely Integrated Memory region.). Required properties are `compatible`, `cache-block-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`, `interrupts`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 7 `allOf` composition block(s), 6 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/sifive,ccache0.yaml`
- run `make dtbs_check` on DTS files using `sifive,ccache0`, `sifive,fu540-c000-ccache`, `sifive,fu740-c000-ccache`, `eswin,eic7700-l3-cache`, `starfive,jh7100-ccache`, `starfive,jh7110-ccache`, `microchip,mpfs-ccache`, `microchip,pic64gx-ccache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
