# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml`, a media capture or video pipeline devicetree binding. The schema title is `STMicroelectronics STM32 DCMIPP Digital Camera Memory Interface Pixel Processor`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32 DCMIPP Digital Camera Memory Interface Pixel Processor`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32mp13-dcmipp, st,stm32mp25-dcmipp.
- required node contract: compatible, reg, interrupts, clocks, resets, port.
- property surface: `compatible` (enum st,stm32mp13-dcmipp, st,stm32mp25-dcmipp), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (minItems=1, ordered-items=2), `clock-names` (minItems=1, ordered-items=2; ordered kclk, mclk), `resets` (maxItems=1), `power-domains` (maxItems=1), `access-controllers` (minItems=1, maxItems=2), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Hugues Fruchet <hugues.fruchet@foss.st.com>, Alain Volmat <alain.volmat@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32-dcmipp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, resets, port`, optional top-level properties include `clock-names, power-domains, access-controllers`, and compatible coverage is `st,stm32mp13-dcmipp, st,stm32mp25-dcmipp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
