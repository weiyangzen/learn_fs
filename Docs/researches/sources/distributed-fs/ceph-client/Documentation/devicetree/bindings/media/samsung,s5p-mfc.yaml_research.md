# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml`, a video codec/accelerator devicetree binding. The schema title is `Samsung Exynos Multi Format Codec (MFC)`. Description signal from the file: Multi Format Codec (MFC) is the IP present in Samsung SoCs which supports high resolution decoding and encoding functionalities..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos Multi Format Codec (MFC)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos5433-mfc, samsung,mfc-v5, samsung,mfc-v6, samsung,mfc-v7, samsung,mfc-v8, samsung,mfc-v10, tesla,fsd-mfc, samsung,exynos3250-mfc.
- required node contract: compatible, reg, clocks, clock-names, interrupts.
- property surface: `compatible`, `reg` (maxItems=1), `clocks` (minItems=1, maxItems=3), `clock-names` (minItems=1, maxItems=3), `interrupts` (maxItems=1), `iommus` (minItems=1, maxItems=2), `iommu-names` (minItems=1, ordered-items=2; ordered left, right), `power-domains` (maxItems=1), `memory-region` (minItems=1, maxItems=2).
- Structural features: closed schema via `additionalProperties: false`; 6 allOf composition block(s); 6 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 6 conditional site(s): allOf[0], allOf[1], allOf[2], allOf[3], allOf[4], allOf[5]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Marek Szyprowski <m.szyprowski@samsung.com>, Aakarsh Jain <aakarsh.jain@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,s5p-mfc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, clock-names, interrupts`, optional top-level properties include `iommus, iommu-names, power-domains, memory-region`, and compatible coverage is `samsung,exynos5433-mfc, samsung,mfc-v5, samsung,mfc-v6, samsung,mfc-v7, samsung,mfc-v8, samsung,mfc-v10, tesla,fsd-mfc, samsung,exynos3250-mfc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
