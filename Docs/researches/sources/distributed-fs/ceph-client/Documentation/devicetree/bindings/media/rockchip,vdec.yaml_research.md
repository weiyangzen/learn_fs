# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml`, a video codec/accelerator devicetree binding. The schema title is `Rockchip Video Decoder (VDec)`. Description signal from the file: Rockchip SoCs have variants of the same stateless Video Decoder that can decodes H.264, HEVC, VP9 and AV1 streams, depending on the variant..

## Purpose
The file defines the devicetree ABI for `Rockchip Video Decoder (VDec)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3288-vdec, rockchip,rk3399-vdec, rockchip,rk3576-vdec, rockchip,rk3588-vdec, rockchip,rk3228-vdec, rockchip,rk3328-vdec.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains.
- property surface: `compatible`, `reg` (minItems=1, maxItems=3), `reg-names`, `interrupts` (maxItems=1), `clocks` (minItems=4, ordered-items=5), `clock-names` (minItems=4, ordered-items=5; ordered axi, ahb, cabac, core, hevc_cabac), `assigned-clocks`, `assigned-clock-rates`, `resets` (ordered-items=5), `reset-names` (ordered-items=5; ordered axi, ahb, cabac, core, hevc_cabac), `power-domains` (maxItems=1), `iommus` (maxItems=1), `sram` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Heiko Stuebner <heiko@sntech.de>.
- schema id: http://devicetree.org/schemas/media/rockchip,vdec.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains`, optional top-level properties include `reg-names, assigned-clocks, assigned-clock-rates, resets, reset-names, iommus, sram`, and compatible coverage is `rockchip,rk3288-vdec, rockchip,rk3399-vdec, rockchip,rk3576-vdec, rockchip,rk3588-vdec, rockchip,rk3228-vdec, rockchip,rk3328-vdec`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
