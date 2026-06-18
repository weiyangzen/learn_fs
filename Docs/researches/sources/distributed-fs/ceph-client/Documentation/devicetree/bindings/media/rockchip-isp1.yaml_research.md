# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Rockchip SoC Image Signal Processing unit v1`. Description signal from the file: Rockchip ISP1 is the Camera interface for the Rockchip series of SoCs which contains image processing, scaling, and compression functions..

## Purpose
The file defines the devicetree ABI for `Rockchip SoC Image Signal Processing unit v1`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains, ports.
- property surface: `compatible` (enum fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp), `reg` (maxItems=1), `interrupts` (minItems=1, maxItems=3), `interrupt-names` (ordered-items=3; ordered isp, mi, mipi), `clocks` (minItems=3, ordered-items=4), `clock-names` (minItems=3, ordered-items=4; ordered isp, aclk, hclk, pclk), `fsl,blk-ctrl` (ref /schemas/types.yaml#/definitions/phandle-array; maxItems=1), `iommus` (maxItems=1), `phys` (maxItems=1), `phy-names` (const dphy), `power-domains` (minItems=1, ordered-items=2), `power-domain-names` (minItems=1, ordered-items=2; ordered isp, csi2), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 3 allOf composition block(s); 3 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 3 conditional site(s): allOf[0], allOf[1], allOf[2]. The file includes 2 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Helen Koike <helen.koike@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip-isp1.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains, ports`, optional top-level properties include `interrupt-names, fsl,blk-ctrl, iommus, phys, phy-names, power-domain-names`, and compatible coverage is `fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
