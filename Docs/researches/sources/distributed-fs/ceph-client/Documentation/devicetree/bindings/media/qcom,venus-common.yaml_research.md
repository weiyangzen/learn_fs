# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml`, a video codec/accelerator devicetree binding. The schema title is `Qualcomm SoC Venus Video Encode and Decode Accelerators Common Properties`. Description signal from the file: The Venus IP is a video encode and decode accelerator present on Qualcomm platforms.

## Purpose
The file defines the devicetree ABI for `Qualcomm SoC Venus Video Encode and Decode Accelerators Common Properties`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- required node contract: reg, clocks, clock-names, interrupts, memory-region, power-domains.
- property surface: `reg` (maxItems=1), `clocks` (minItems=3, maxItems=7), `clock-names` (minItems=3, maxItems=7), `firmware-name` (maxItems=1), `interrupts` (maxItems=1), `iommus` (minItems=1, maxItems=20), `memory-region` (maxItems=1), `power-domains` (minItems=1, maxItems=4), `power-domain-names` (minItems=1, maxItems=4), `video-firmware` (Firmware subnode is needed when the platform does not have TrustZone.).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Stanimir Varbanov <stanimir.k.varbanov@gmail.com>, Vikash Garodia <quic_vgarodia@quicinc.com>.
- schema id: http://devicetree.org/schemas/media/qcom,venus-common.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `reg, clocks, clock-names, interrupts, memory-region, power-domains`, optional top-level properties include `firmware-name, iommus, power-domain-names, video-firmware`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
