# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Raspberry Pi PiSP Image Signal Processor (ISP) Back End`. Description signal from the file: The Raspberry Pi PiSP Image Signal Processor (ISP) Back End is an image processor that fetches images in Bayer or Grayscale format from DRAM memory in tiles and produces images consumable by applications. The full ISP documentation is available at https://datasheets.raspberrypi.com/camera/raspberry-pi-image-signal-processor-specification.pdf.

## Purpose
The file defines the devicetree ABI for `Raspberry Pi PiSP Image Signal Processor (ISP) Back End`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,bcm2712-pispbe, raspberrypi,pispbe.
- required node contract: compatible, reg, interrupts, clocks.
- property surface: `compatible` (ordered-items=2; ordered raspberrypi,pispbe), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `iommus` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Raspberry Pi Kernel Maintenance <kernel-list@raspberrypi.com>, Jacopo Mondi <jacopo.mondi@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/raspberrypi,pispbe.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks`, optional top-level properties include `iommus`, and compatible coverage is `brcm,bcm2712-pispbe, raspberrypi,pispbe`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
