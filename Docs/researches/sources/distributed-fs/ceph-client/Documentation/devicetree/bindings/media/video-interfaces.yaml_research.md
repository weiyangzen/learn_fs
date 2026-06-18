# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Common Properties for Video Receiver and Transmitter Interface Endpoints`. Description signal from the file: Video data pipelines usually consist of external devices, e.g. camera sensors, controlled over an I2C, SPI or UART bus, and SoC internal IP blocks, including video DMA engines and video data processors. SoC internal blocks are described by DT nodes, placed similarly to other SoC blocks. External devices are represented as child nodes of their respective bus controller nodes, e.g. I2C. Data interfaces on all video dev.

## Purpose
The file defines the devicetree ABI for `Common Properties for Video Receiver and Transmitter Interface Endpoints`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- property surface: `slave-mode` (Indicates that the link is run in slave mode. The default when this property is not specif), `bus-type` (ref /schemas/types.yaml#/definitions/uint32; enum 1, 2, 3, 4, 5, 6, 7), `bus-width` (ref /schemas/types.yaml#/definitions/uint32; maximum=64), `data-shift` (ref /schemas/types.yaml#/definitions/uint32; maximum=64), `hsync-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `vsync-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-enable-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `field-even-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `pclk-sample` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1, 2), `sync-on-green-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-lanes` (ref /schemas/types.yaml#/definitions/uint32-array; minItems=1, maxItems=8), `clock-lanes` (ref /schemas/types.yaml#/definitions/uint32; maximum=8), `clock-noncontinuous` (Allow MIPI CSI-2 non-continuous clock mode.), `link-frequencies` (ref /schemas/types.yaml#/definitions/uint64-array), `lane-polarities` (ref /schemas/types.yaml#/definitions/uint32-array; minItems=1, maxItems=9, item-enum=0/1), and 2 more.
- referenced schemas: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.
- Structural features: endpoint subnodes; 1 allOf composition block(s).
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Sakari Ailus <sakari.ailus@linux.intel.com>, Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/video-interfaces.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.

## Risks And Edge Cases
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `none declared`, optional top-level properties include `slave-mode, bus-type, bus-width, data-shift, hsync-active, vsync-active, data-active, data-enable-active, field-even-active, pclk-sample, sync-on-green-active, data-lanes, clock-lanes, clock-noncontinuous, link-frequencies, lane-polarities, and 2 more`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
