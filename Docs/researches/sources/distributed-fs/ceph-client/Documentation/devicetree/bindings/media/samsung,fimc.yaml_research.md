# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC Camera Subsystem (FIMC)`. Description signal from the file: The S5P/Exynos SoC Camera subsystem comprises of multiple sub-devices represented by separate device tree nodes. Currently this includes: Fully Integrated Mobile Camera (FIMC, in the S5P SoCs series known as CAMIF), MIPI CSIS, FIMC-LITE and FIMC-IS (ISP)..

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC Camera Subsystem (FIMC)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,fimc.
- required node contract: compatible, #address-cells, #clock-cells, clocks, clock-names, clock-output-names, ranges, #size-cells.
- property surface: `compatible` (const samsung,fimc), `ranges`, `#address-cells` (const 1), `#size-cells` (const 1), `#clock-cells` (const 1), `clocks` (minItems=2, maxItems=4), `clock-names` (minItems=2, ordered-items=4; ordered sclk_cam0, sclk_cam1, pxl_async0, pxl_async1), `clock-output-names` (maxItems=2), `parallel-ports` (ref /schemas/graph.yaml#/properties/ports), `pinctrl-names` (minItems=1, ordered-items=4; ordered default, idle, active_a, active_b).
- child-node patterns: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$.
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,fimc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- pattern children: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, #address-cells, #clock-cells, clocks, clock-names, clock-output-names, ranges, #size-cells`, optional top-level properties include `parallel-ports, pinctrl-names`, and compatible coverage is `samsung,fimc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
