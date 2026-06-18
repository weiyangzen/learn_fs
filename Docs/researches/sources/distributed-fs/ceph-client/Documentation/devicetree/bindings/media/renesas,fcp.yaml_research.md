# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml`, a devicetree binding schema. The schema title is `Renesas R-Car Frame Compression Processor (FCP)`. Description signal from the file: The FCP is a companion module of video processing modules in the Renesas R-Car Gen3 and RZ/G2 SoCs. It provides data compression and decompression, data caching, and conversion of AXI transactions in order to reduce the memory bandwidth. There are three types of FCP: FCP for Codec (FCPC), FCP for VSP (FCPV) and FCP for FDP (FCPF). Their configuration and behaviour depend on the module they are paired with. These DT b.

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Frame Compression Processor (FCP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,fcpv, renesas,fcpf, renesas,r9a07g043u-fcpvd, renesas,r9a07g044-fcpvd, renesas,r9a07g054-fcpvd, renesas,r9a09g056-fcpvd, renesas,r9a09g057-fcpvd.
- required node contract: compatible, reg, clocks, power-domains, resets.
- property surface: `compatible`, `reg` (maxItems=1), `clocks` (minItems=1, ordered-items=3), `clock-names` (ordered-items=3; ordered aclk, pclk, vclk), `iommus` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/renesas,fcp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, power-domains, resets`, optional top-level properties include `clock-names, iommus`, and compatible coverage is `renesas,fcpv, renesas,fcpf, renesas,r9a07g043u-fcpvd, renesas,r9a07g044-fcpvd, renesas,r9a07g054-fcpvd, renesas,r9a09g056-fcpvd, renesas,r9a09g057-fcpvd`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
