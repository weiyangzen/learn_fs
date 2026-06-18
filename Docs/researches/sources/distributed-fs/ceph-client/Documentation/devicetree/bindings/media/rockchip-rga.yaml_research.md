# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml`, a devicetree binding schema. The schema title is `Rockchip 2D raster graphic acceleration controller (RGA)`. Description signal from the file: RGA is a standalone 2D raster graphic acceleration unit. It accelerates 2D graphics operations, such as point/line drawing, image scaling, rotation, BitBLT, alpha blending and image blur/sharpness..

## Purpose
The file defines the devicetree ABI for `Rockchip 2D raster graphic acceleration controller (RGA)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3288-rga, rockchip,rk3399-rga, rockchip,rk3228-rga, rockchip,rk3568-rga, rockchip,rk3588-rga.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, reset-names.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=3), `clock-names` (ordered-items=3; ordered aclk, hclk, sclk), `power-domains` (maxItems=1), `resets` (maxItems=3), `reset-names` (ordered-items=3; ordered core, axi, ahb).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Jacob Chen <jacob-chen@iotwrt.com>, Ezequiel Garcia <ezequiel@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip-rga.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, reset-names`, optional top-level properties include `power-domains`, and compatible coverage is `rockchip,rk3288-rga, rockchip,rk3399-rga, rockchip,rk3228-rga, rockchip,rk3568-rga, rockchip,rk3588-rga`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
