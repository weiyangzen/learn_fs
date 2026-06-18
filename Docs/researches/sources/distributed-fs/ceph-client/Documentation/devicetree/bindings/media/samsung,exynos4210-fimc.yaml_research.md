# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC Fully Integrated Mobile Camera`. Description signal from the file: Each FIMC device should have an alias in the aliases node, in the form of fimc<n>, where <n> is an integer specifying the IP block instance..

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC Fully Integrated Mobile Camera`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc.
- required node contract: compatible, reg, clocks, clock-names, samsung,pix-limits.
- property surface: `compatible` (enum samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc), `reg` (maxItems=1), `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered fimc, sclk_fimc), `clock-frequency` (Maximum FIMC local clock (LCLK) frequency.), `interrupts` (maxItems=1), `iommus` (maxItems=1), `power-domains` (maxItems=1), `samsung,cam-if` (The FIMC IP block includes the camera input interface.), `samsung,isp-wb` (The FIMC IP block has the ISP writeback input.), `samsung,lcd-wb` (The FIMC IP block has the LCD writeback input.), `samsung,mainscaler-ext` (FIMC IP supports extended image size and has CIEXTEN register.), `samsung,min-pix-alignment` (ref /schemas/types.yaml#/definitions/uint32-array; ordered-items=2), `samsung,min-pix-sizes` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems=2), `samsung,pix-limits` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems=4), `samsung,rotators` (ref /schemas/types.yaml#/definitions/uint32), and 1 more.
- referenced schemas: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4210-fimc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, clock-names, samsung,pix-limits`, optional top-level properties include `clock-frequency, interrupts, iommus, power-domains, samsung,cam-if, samsung,isp-wb, samsung,lcd-wb, samsung,mainscaler-ext, samsung,min-pix-alignment, samsung,min-pix-sizes, samsung,rotators, samsung,sysreg`, and compatible coverage is `samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
