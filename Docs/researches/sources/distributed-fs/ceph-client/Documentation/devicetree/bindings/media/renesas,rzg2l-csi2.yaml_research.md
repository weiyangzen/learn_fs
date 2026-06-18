# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas RZ/G2L (and alike SoC's) MIPI CSI-2 receiver`. Description signal from the file: The CSI-2 receiver device provides MIPI CSI-2 capabilities for the Renesas RZ/G2L (and alike SoCs). MIPI CSI-2 is part of the CRU block which is used in conjunction with the Image Processing module, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas RZ/G2L (and alike SoC's) MIPI CSI-2 receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r9a07g043-csi2, renesas,r9a07g044-csi2, renesas,r9a07g054-csi2, renesas,rzg2l-csi2, renesas,r9a09g047-csi2, renesas,r9a09g057-csi2.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, ports.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks`, `clock-names`, `power-domains` (maxItems=1), `resets` (ordered-items=2), `reset-names` (ordered-items=2; ordered presetn, cmn-rstb), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>.
- schema id: http://devicetree.org/schemas/media/renesas,rzg2l-csi2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, ports`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r9a07g043-csi2, renesas,r9a07g044-csi2, renesas,r9a07g054-csi2, renesas,rzg2l-csi2, renesas,r9a09g047-csi2, renesas,r9a09g057-csi2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
