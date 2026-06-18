# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Video Multiplexer`. Description signal from the file: Video multiplexers allow to select between multiple input ports. Video received on the active input port is passed through to the output port. Muxes described by this binding are controlled by a multiplexer controller..

## Purpose
The file defines the devicetree ABI for `Video Multiplexer`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: video-mux.
- required node contract: compatible, mux-controls.
- property surface: `compatible` (const video-mux), `mux-controls` (maxItems=1), `#address-cells` (const 1), `#size-cells` (const 0), `ports` (ref /schemas/graph.yaml#/properties/ports).
- child-node patterns: ^port@.
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; patternProperties: ^port@; closed schema via `additionalProperties: false`; 2 oneOf branch(es).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Sakari Ailus <sakari.ailus@linux.intel.com>, Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/video-mux.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- pattern children: ^port@.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, mux-controls`, optional top-level properties include `#address-cells, #size-cells, ports`, and compatible coverage is `video-mux`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
