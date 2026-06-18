# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Qualcomm X1E80100 Camera Subsystem (CAMSS)`. Description signal from the file: The CAMSS IP is a CSI decoder and ISP present on Qualcomm platforms..

## Purpose
The file defines the devicetree ABI for `Qualcomm X1E80100 Camera Subsystem (CAMSS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: qcom,x1e80100-camss.
- required node contract: compatible, reg, reg-names, clocks, clock-names, interrupts, interrupt-names, interconnects, interconnect-names, iommus, power-domains, power-domain-names, vdd-csiphy-0p8-supply, vdd-csiphy-1p2-supply, and 1 more.
- property surface: `compatible` (const qcom,x1e80100-camss), `reg` (maxItems=17), `reg-names` (ordered-items=17; ordered csid0, csid1, csid2, csid_lite0, csid_lite1, csid_wrapper, csiphy0, csiphy1, and 9 more), `clocks` (maxItems=29), `clock-names` (ordered-items=29; ordered camnoc_nrt_axi, camnoc_rt_axi, core_ahb, cpas_ahb, cpas_fast_ahb, cpas_vfe0, cpas_vfe1, cpas_vfe_lite, and 21 more), `interrupts` (maxItems=13), `interrupt-names` (ordered-items=13; ordered csid0, csid1, csid2, csid_lite0, csid_lite1, csiphy0, csiphy1, csiphy2, and 5 more), `interconnects` (maxItems=4), `interconnect-names` (ordered-items=4; ordered ahb, hf_mnoc, sf_mnoc, sf_icp_mnoc), `iommus` (maxItems=8), `power-domains` (ordered-items=3), `power-domain-names` (ordered-items=3; ordered ife0, ife1, top), `vdd-csiphy-0p8-supply` (0.8V supply to a PHY.), `vdd-csiphy-1p2-supply` (1.2V supply to a PHY.), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Bryan O'Donoghue <bryan.odonoghue@linaro.org>.
- schema id: http://devicetree.org/schemas/media/qcom,x1e80100-camss.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, clocks, clock-names, interrupts, interrupt-names, interconnects, interconnect-names, iommus, power-domains, power-domain-names, vdd-csiphy-0p8-supply, vdd-csiphy-1p2-supply, and 1 more`, optional top-level properties include `none declared`, and compatible coverage is `qcom,x1e80100-camss`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
