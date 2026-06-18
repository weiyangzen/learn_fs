# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml`, a video codec/accelerator devicetree binding. The schema title is `Qualcomm SM8750 SoC Iris video encoder and decoder`. Description signal from the file: The Iris video processing unit on Qualcomm SM8750 SoC is a video encode and decode accelerator..

## Purpose
The file defines the devicetree ABI for `Qualcomm SM8750 SoC Iris video encoder and decoder`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: qcom,sm8750-iris.
- required node contract: compatible, dma-coherent, interconnects, interconnect-names, iommus, power-domain-names, resets, reset-names.
- property surface: `compatible` (enum qcom,sm8750-iris), `clocks` (maxItems=6), `clock-names` (ordered-items=6; ordered iface, core, vcodec0_core, iface1, core_freerun, vcodec0_core_freerun), `dma-coherent`, `interconnects` (maxItems=2), `interconnect-names` (ordered-items=2; ordered cpu-cfg, video-mem), `iommus` (maxItems=2), `operating-points-v2`, `opp-table`, `power-domains` (maxItems=4), `power-domain-names` (ordered-items=4; ordered venus, vcodec0, mxc, mmcx), `resets` (maxItems=4), `reset-names` (ordered-items=4; ordered bus0, bus1, core, vcodec0_core).
- referenced schemas: qcom,venus-common.yaml#.
- Structural features: closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/media/qcom,sm8750-iris.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: qcom,venus-common.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, dma-coherent, interconnects, interconnect-names, iommus, power-domain-names, resets, reset-names`, optional top-level properties include `clocks, clock-names, operating-points-v2, opp-table, power-domains`, and compatible coverage is `qcom,sm8750-iris`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: qcom,venus-common.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
