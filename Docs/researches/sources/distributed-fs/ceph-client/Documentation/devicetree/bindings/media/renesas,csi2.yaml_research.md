# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas R-Car MIPI CSI-2 receiver`. Description signal from the file: The R-Car CSI-2 receiver device provides MIPI CSI-2 capabilities for the Renesas R-Car and RZ/G2 family of devices. It is used in conjunction with the R-Car VIN module, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car MIPI CSI-2 receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a774a1-csi2, renesas,r8a774b1-csi2, renesas,r8a774c0-csi2, renesas,r8a774e1-csi2, renesas,r8a7795-csi2, renesas,r8a7796-csi2, renesas,r8a77961-csi2, renesas,r8a77965-csi2, renesas,r8a77970-csi2, renesas,r8a77980-csi2, renesas,r8a77990-csi2, renesas,r8a779a0-csi2, renesas,r8a779g0-csi2, renesas,r8a779h0-csi2.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets, ports.
- property surface: `compatible` (ordered-items=1), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Niklas Söderlund <niklas.soderlund@ragnatech.se>.
- schema id: http://devicetree.org/schemas/media/renesas,csi2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets, ports`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r8a774a1-csi2, renesas,r8a774b1-csi2, renesas,r8a774c0-csi2, renesas,r8a774e1-csi2, renesas,r8a7795-csi2, renesas,r8a7796-csi2, renesas,r8a77961-csi2, renesas,r8a77965-csi2, renesas,r8a77970-csi2, renesas,r8a77980-csi2, renesas,r8a77990-csi2, renesas,r8a779a0-csi2, renesas,r8a779g0-csi2, renesas,r8a779h0-csi2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
