# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml`, a memory-controller devicetree binding. The schema title is `LPDDR2 SDRAM compliant to JEDEC JESD209-2`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `LPDDR2 SDRAM compliant to JEDEC JESD209-2`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: elpida,ECB240ABACN, elpida,B8132B2PB-6D-F, jedec,lpddr2-nvm, jedec,lpddr2-s2, jedec,lpddr2-s4.
- required node contract: compatible, density, io-width.
- property surface: `compatible`, `revision-id1` (ref /schemas/types.yaml#/definitions/uint32; maximum=255), `revision-id2` (ref /schemas/types.yaml#/definitions/uint32; maximum=255), `tRRD-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tWTR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tXP-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRTP-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tCKE-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRPab-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRCD-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tWR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRASmin-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tCKESR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tFAW-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16).
- child-node patterns: ^lpddr2-timings.
- referenced schemas: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- Structural features: patternProperties: ^lpddr2-timings; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/ddr/jedec,lpddr2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- pattern children: ^lpddr2-timings.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, density, io-width`, optional top-level properties include `revision-id1, revision-id2, tRRD-min-tck, tWTR-min-tck, tXP-min-tck, tRTP-min-tck, tCKE-min-tck, tRPab-min-tck, tRCD-min-tck, tWR-min-tck, tRASmin-min-tck, tCKESR-min-tck, tFAW-min-tck`, and compatible coverage is `elpida,ECB240ABACN, elpida,B8132B2PB-6D-F, jedec,lpddr2-nvm, jedec,lpddr2-s2, jedec,lpddr2-s4`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- cross-check JEDEC density, IO width, frequency, and timing values against the memory datasheet.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
