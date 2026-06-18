# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml`, a memory-controller devicetree binding. The schema title is `Memory controller (MEMC) for Broadcom STB`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Memory controller (MEMC) for Broadcom STB`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,brcmstb-memc-ddr-rev-b.2.2, brcm,brcmstb-memc-ddr-rev-b.2.3, brcm,brcmstb-memc-ddr-rev-b.2.5, brcm,brcmstb-memc-ddr-rev-b.2.6, brcm,brcmstb-memc-ddr-rev-b.2.7, brcm,brcmstb-memc-ddr-rev-b.2.8, brcm,brcmstb-memc-ddr-rev-b.3.0, brcm,brcmstb-memc-ddr-rev-b.3.1, brcm,brcmstb-memc-ddr-rev-c.1.0, brcm,brcmstb-memc-ddr-rev-c.1.1, brcm,brcmstb-memc-ddr-rev-c.1.2, brcm,brcmstb-memc-ddr-rev-c.1.3, brcm,brcmstb-memc-ddr-rev-c.1.4, brcm,brcmstb-memc-ddr-rev-b.2.1, brcm,brcmstb-memc-ddr, brcm,brcmstb-memc-ddr-rev-b.2.0, and 2 more.
- required node contract: compatible, reg.
- property surface: `compatible`, `reg` (maxItems=1), `clock-frequency` (DDR PHY frequency in Hz).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Florian Fainelli <f.fainelli@gmail.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/brcm,brcmstb-memc-ddr.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg`, optional top-level properties include `clock-frequency`, and compatible coverage is `brcm,brcmstb-memc-ddr-rev-b.2.2, brcm,brcmstb-memc-ddr-rev-b.2.3, brcm,brcmstb-memc-ddr-rev-b.2.5, brcm,brcmstb-memc-ddr-rev-b.2.6, brcm,brcmstb-memc-ddr-rev-b.2.7, brcm,brcmstb-memc-ddr-rev-b.2.8, brcm,brcmstb-memc-ddr-rev-b.3.0, brcm,brcmstb-memc-ddr-rev-b.3.1, brcm,brcmstb-memc-ddr-rev-c.1.0, brcm,brcmstb-memc-ddr-rev-c.1.1, brcm,brcmstb-memc-ddr-rev-c.1.2, brcm,brcmstb-memc-ddr-rev-c.1.3, brcm,brcmstb-memc-ddr-rev-c.1.4, brcm,brcmstb-memc-ddr-rev-b.2.1, brcm,brcmstb-memc-ddr, brcm,brcmstb-memc-ddr-rev-b.2.0, and 2 more`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
