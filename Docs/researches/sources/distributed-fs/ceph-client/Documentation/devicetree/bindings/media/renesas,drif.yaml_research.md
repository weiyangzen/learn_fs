# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml`, a media ancillary controller devicetree binding. The schema title is `Renesas R-Car Gen3 Digital Radio Interface Controller (DRIF)`. Description signal from the file: R-Car Gen3 DRIF is a SPI like receive only slave device. A general representation of DRIF interfacing with a master device is shown below. +---------------------+ +---------------------+ | |-----SCK------->|CLK | | Master |-----SS-------->|SYNC DRIFn (slave) | | |-----SD0------->|D0 | | |-----SD1------->|D1 | +---------------------+ +---------------------+ As per datasheet, each DRIF channel (drifn) is made up of two.

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Gen3 Digital Radio Interface Controller (DRIF)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a7795-drif, renesas,r8a7796-drif, renesas,r8a77965-drif, renesas,r8a77990-drif, renesas,rcar-gen3-drif.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, renesas,bonding, power-domains.
- property surface: `compatible` (ordered-items=2; ordered renesas,rcar-gen3-drif), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `clock-names` (const fck), `resets` (maxItems=1), `dmas` (minItems=1, maxItems=2), `dma-names` (minItems=1, ordered-items=2; ordered rx, rx), `renesas,bonding` (ref /schemas/types.yaml#/definitions/phandle), `power-domains` (maxItems=1), `renesas,primary-bond` (Indicates that the channel acts as primary among the bonded channels.), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 2 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. DMA channel properties persist the binding between the hardware block and the DMA engine channels it relies on.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Ramesh Shanmugasundaram <rashanmu@gmail.com>, Fabrizio Castro <fabrizio.castro.jz@renesas.com>.
- schema id: http://devicetree.org/schemas/media/renesas,drif.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, renesas,bonding, power-domains`, optional top-level properties include `renesas,primary-bond, port`, and compatible coverage is `renesas,r8a7795-drif, renesas,r8a7796-drif, renesas,r8a77965-drif, renesas,r8a77990-drif, renesas,rcar-gen3-drif`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
