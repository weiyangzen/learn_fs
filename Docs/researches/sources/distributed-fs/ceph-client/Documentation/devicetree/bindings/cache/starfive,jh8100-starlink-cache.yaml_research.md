# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/starfive,jh8100-starlink-cache.yaml

## Purpose
StarFive's StarLink Cache Controller manages the L3 cache shared between clusters of CPU cores. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Joshua Yeong <joshua.yeong@starfivetech.com> and gives dt-schema a canonical contract for nodes matching `starfive,jh8100-starlink-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1). Required properties are `compatible`, `reg`, `cache-block-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/starfive,jh8100-starlink-cache.yaml`
- run `make dtbs_check` on DTS files using `starfive,jh8100-starlink-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
