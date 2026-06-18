# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC series MIPI CSI-2 receiver (MIPI CSIS)`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC series MIPI CSI-2 receiver (MIPI CSIS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis.
- required node contract: compatible, reg, bus-width, clocks, clock-names, interrupts, vddio-supply, vddcore-supply.
- property surface: `compatible` (enum samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis), `reg` (maxItems=1), `#address-cells` (const 1), `#size-cells` (const 0), `bus-width` (ref /schemas/types.yaml#/definitions/uint32; enum 2, 4), `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered csis, sclk_csis), `clock-frequency` (The IP's main (system bus) clock frequency in Hz.), `interrupts` (maxItems=1), `phys` (maxItems=1), `phy-names` (ordered-items=1; ordered csis), `power-domains` (maxItems=1), `vddio-supply` (MIPI CSIS I/O and PLL voltage supply (e.g. 1.8V).), `vddcore-supply` (MIPI CSIS Core voltage supply (e.g. 1.1V).).
- child-node patterns: ^port@[34]$.
- referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^port@[34]$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 2 anyOf branch(es); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4210-csis.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- pattern children: ^port@[34]$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, bus-width, clocks, clock-names, interrupts, vddio-supply, vddcore-supply`, optional top-level properties include `#address-cells, #size-cells, clock-frequency, phys, phy-names, power-domains`, and compatible coverage is `samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
