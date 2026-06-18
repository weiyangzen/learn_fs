# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Xilinx MIPI CSI-2 Receiver Subsystem`. Description signal from the file: The Xilinx MIPI CSI-2 Receiver Subsystem is used to capture MIPI CSI-2 traffic from compliant camera sensors and send the output as AXI4 Stream video data for image processing. The subsystem consists of a MIPI D-PHY in slave mode which captures the data packets. This is passed along the MIPI CSI-2 Rx IP which extracts the packet data. The optional Video Format Bridge (VFB) converts this data to AXI4 Stream video data.

## Purpose
The file defines the devicetree ABI for `Xilinx MIPI CSI-2 Receiver Subsystem`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: xlnx,mipi-csi2-rx-subsystem-5.0.
- required node contract: compatible, reg, interrupts, clocks, clock-names, ports.
- property surface: `compatible` (ordered-items=1), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (ordered-items=2), `clock-names` (ordered-items=2; ordered lite_aclk, video_aclk), `xlnx,csi-pxl-format` (ref /schemas/types.yaml#/definitions/uint32), `xlnx,vfb` (Present when Video Format Bridge is enabled in IP configuration), `xlnx,en-csi-v2-0` (Present if CSI v2 is enabled in IP configuration.), `xlnx,en-vcx` (When present, there are maximum 16 virtual channels, else only 4.), `xlnx,en-active-lanes` (Present if the number of active lanes can be re-configured at runtime in the Protocol Conf), `video-reset-gpios` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Vishal Sagar <vishal.sagar@amd.com>.
- schema id: http://devicetree.org/schemas/media/xilinx/xlnx,csi2rxss.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, ports`, optional top-level properties include `xlnx,csi-pxl-format, xlnx,vfb, xlnx,en-csi-v2-0, xlnx,en-vcx, xlnx,en-active-lanes, video-reset-gpios`, and compatible coverage is `xlnx,mipi-csi2-rx-subsystem-5.0`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
