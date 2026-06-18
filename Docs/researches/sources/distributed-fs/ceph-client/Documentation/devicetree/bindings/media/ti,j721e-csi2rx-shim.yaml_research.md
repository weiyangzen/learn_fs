# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml`, a media capture or video pipeline devicetree binding. The schema title is `TI J721E CSI2RX Shim`. Description signal from the file: The TI J721E CSI2RX Shim is a wrapper around Cadence CSI2RX bridge that enables sending captured frames to memory over PSI-L DMA. In the J721E Technical Reference Manual (SPRUIL1B) it is referred to as "SHIM" under the CSI_RX_IF section..

## Purpose
The file defines the devicetree ABI for `TI J721E CSI2RX Shim`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,j721e-csi2rx-shim.
- required node contract: compatible, reg, dmas, dma-names, power-domains, ranges, #address-cells, #size-cells.
- property surface: `compatible` (const ti,j721e-csi2rx-shim), `dmas` (maxItems=1), `dma-names` (ordered-items=1; ordered rx0), `reg` (maxItems=1), `power-domains` (maxItems=1), `ranges`, `#address-cells`, `#size-cells`.
- child-node patterns: ^csi-bridge@.
- referenced schemas: cdns,csi2rx.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^csi-bridge@; closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. DMA channel properties persist the binding between the hardware block and the DMA engine channels it relies on.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Jai Luthra <jai.luthra@linux.dev>.
- schema id: http://devicetree.org/schemas/media/ti,j721e-csi2rx-shim.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: cdns,csi2rx.yaml#.
- pattern children: ^csi-bridge@.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, dmas, dma-names, power-domains, ranges, #address-cells, #size-cells`, optional top-level properties include `none declared`, and compatible coverage is `ti,j721e-csi2rx-shim`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: cdns,csi2rx.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
