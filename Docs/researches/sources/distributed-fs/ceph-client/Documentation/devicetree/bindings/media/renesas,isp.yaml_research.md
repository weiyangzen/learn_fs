# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas R-Car ISP Channel Selector`. Description signal from the file: The R-Car ISP Channel Selector provides MIPI CSI-2 VC and DT filtering capabilities for the Renesas R-Car family of devices. It is used in conjunction with the R-Car VIN and CSI-2 modules, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car ISP Channel Selector`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a779a0-isp, renesas,r8a779g0-isp, renesas,r8a779h0-isp, renesas,rcar-gen4-isp.
- required node contract: compatible, reg, reg-names, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, reset-names, ports.
- property surface: `compatible` (ordered-items=2; ordered renesas,rcar-gen4-isp), `reg` (minItems=1, maxItems=2), `reg-names` (minItems=1, ordered-items=2; ordered cs, core), `interrupts` (minItems=1, maxItems=2), `interrupt-names` (minItems=1, ordered-items=2; ordered cs, core), `clocks` (minItems=1, maxItems=2), `clock-names` (minItems=1, ordered-items=2; ordered cs, core), `power-domains` (maxItems=1), `resets` (minItems=1, maxItems=2), `reset-names` (minItems=1, ordered-items=2; ordered cs, core), `renesas,vspx` (ref /schemas/types.yaml#/definitions/phandle), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Niklas Söderlund <niklas.soderlund@ragnatech.se>.
- schema id: http://devicetree.org/schemas/media/renesas,isp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, reset-names, ports`, optional top-level properties include `renesas,vspx`, and compatible coverage is `renesas,r8a779a0-isp, renesas,r8a779g0-isp, renesas,r8a779h0-isp, renesas,rcar-gen4-isp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
