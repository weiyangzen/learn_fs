# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml`, a video codec/accelerator devicetree binding. The schema title is `STMicroelectronics STM32MP25 VDEC video decoder & VENC video encoder`. Description signal from the file: The STMicroelectronics STM32MP25 SOCs embeds a VDEC video hardware decoder peripheral based on Verisilicon VC8000NanoD IP (former Hantro G1) and a VENC video hardware encoder peripheral based on Verisilicon VC8000NanoE IP (former Hantro H1)..

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32MP25 VDEC video decoder & VENC video encoder`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32mp25-vdec, st,stm32mp25-venc.
- required node contract: compatible, reg, interrupts, clocks.
- property surface: `compatible` (enum st,stm32mp25-vdec, st,stm32mp25-venc), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `access-controllers` (minItems=1, maxItems=2).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Hugues Fruchet <hugues.fruchet@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32mp25-video-codec.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks`, optional top-level properties include `access-controllers`, and compatible coverage is `st,stm32mp25-vdec, st,stm32mp25-venc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
