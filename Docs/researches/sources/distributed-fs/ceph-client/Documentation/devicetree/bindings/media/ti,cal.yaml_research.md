# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml`, a devicetree binding schema. The schema title is `Texas Instruments DRA72x CAMERA ADAPTATION LAYER (CAL)`. Description signal from the file: The Camera Adaptation Layer (CAL) is a key component for image capture applications. The capture module provides the system interface and the processing capability to connect CSI2 image-sensor modules to the DRA72x device. CAL supports 2 camera port nodes on MIPI bus..

## Purpose
The file defines the devicetree ABI for `Texas Instruments DRA72x CAMERA ADAPTATION LAYER (CAL)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal.
- required node contract: compatible, reg, reg-names, interrupts, ti,camerrx-control.
- property surface: `compatible` (enum ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal), `reg` (minItems=2, ordered-items=3), `reg-names` (minItems=2, ordered-items=3; ordered cal_top, cal_rx_core0, cal_rx_core1), `interrupts` (maxItems=1), `ti,camerrx-control` (ref /schemas/types.yaml#/definitions/phandle-array; ordered-items=1), `clocks` (maxItems=1), `clock-names` (const fck), `power-domains` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Benoit Parrot <bparrot@ti.com>.
- schema id: http://devicetree.org/schemas/media/ti,cal.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, interrupts, ti,camerrx-control`, optional top-level properties include `clocks, clock-names, power-domains, ports`, and compatible coverage is `ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
