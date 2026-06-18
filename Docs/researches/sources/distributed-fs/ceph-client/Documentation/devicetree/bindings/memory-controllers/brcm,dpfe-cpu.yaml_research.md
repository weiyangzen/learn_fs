# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml`, a memory-controller devicetree binding. The schema title is `DDR PHY Front End (DPFE) for Broadcom STB`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `DDR PHY Front End (DPFE) for Broadcom STB`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,bcm7271-dpfe-cpu, brcm,bcm7268-dpfe-cpu, brcm,dpfe-cpu.
- required node contract: compatible, reg, reg-names.
- property surface: `compatible` (ordered-items=2; ordered brcm,dpfe-cpu), `reg` (ordered-items=3), `reg-names` (ordered-items=3; ordered dpfe-cpu, dpfe-dmem, dpfe-imem).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Markus Mayer <mmayer@broadcom.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/brcm,dpfe-cpu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names`, optional top-level properties include `none declared`, and compatible coverage is `brcm,bcm7271-dpfe-cpu, brcm,bcm7268-dpfe-cpu, brcm,dpfe-cpu`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
