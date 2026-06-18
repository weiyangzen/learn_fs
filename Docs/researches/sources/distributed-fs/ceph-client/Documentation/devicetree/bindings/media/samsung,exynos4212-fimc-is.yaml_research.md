# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung Exynos4212/4412 SoC Imaging Subsystem (FIMC-IS)`. Description signal from the file: The FIMC-IS is a subsystem for processing image signal from an image sensor. The Exynos4x12 SoC series FIMC-IS V1.5 comprises of a dedicated ARM Cortex-A5 processor, ISP, DRC and FD IP blocks and peripheral devices such as UART, I2C and SPI bus controllers, PWM and ADC..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos4212/4412 SoC Imaging Subsystem (FIMC-IS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos4212-fimc-is.
- required node contract: compatible, reg, #address-cells, clocks, clock-names, interrupts, ranges, samsung,pmu-syscon, #size-cells.
- property surface: `compatible` (enum samsung,exynos4212-fimc-is), `reg` (maxItems=1), `ranges`, `#address-cells` (const 1), `#size-cells` (const 1), `clocks` (maxItems=21), `clock-names` (ordered-items=21; ordered lite0, lite1, ppmuispx, ppmuispmx, isp, drc, fd, mcuisp, and 13 more), `interrupts` (maxItems=2), `iommus` (maxItems=4), `iommu-names` (ordered-items=4; ordered isp, drc, fd, mcuctl), `power-domains` (maxItems=1), `samsung,pmu-syscon` (ref /schemas/types.yaml#/definitions/phandle).
- child-node patterns: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$.
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4212-fimc-is.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- pattern children: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, #address-cells, clocks, clock-names, interrupts, ranges, samsung,pmu-syscon, #size-cells`, optional top-level properties include `iommus, iommu-names, power-domains`, and compatible coverage is `samsung,exynos4212-fimc-is`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
