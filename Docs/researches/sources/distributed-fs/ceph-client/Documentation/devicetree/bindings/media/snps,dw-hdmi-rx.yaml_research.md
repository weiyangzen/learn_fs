# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml`, a devicetree binding schema. The schema title is `Synopsys DesignWare HDMI RX Controller`. Description signal from the file: Synopsys DesignWare HDMI Input Controller preset on RK3588 SoCs allowing devices to receive and decode high-resolution video streams from external sources like media players, cameras, laptops, etc..

## Purpose
The file defines the devicetree ABI for `Synopsys DesignWare HDMI RX Controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx.
- required node contract: compatible, reg, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, pinctrl-0, hpd-gpios.
- property surface: `compatible` (ordered-items=2; ordered rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx), `reg` (maxItems=1), `interrupts` (maxItems=3), `interrupt-names` (ordered-items=3; ordered cec, hdmi, dma), `clocks` (maxItems=7), `clock-names` (ordered-items=7; ordered aclk, audio, cr_para, pclk, ref, hclk_s_hdmirx, hclk_vo1), `power-domains` (maxItems=1), `resets` (maxItems=4), `reset-names` (ordered-items=4; ordered axi, apb, ref, biu), `memory-region` (maxItems=1), `hpd-gpios` (maxItems=1), `rockchip,grf` (ref /schemas/types.yaml#/definitions/phandle), `rockchip,vo1-grf` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Dmitry Osipenko <dmitry.osipenko@collabora.com>.
- schema id: http://devicetree.org/schemas/media/snps,dw-hdmi-rx.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, pinctrl-0, hpd-gpios`, optional top-level properties include `reset-names, memory-region, rockchip,grf, rockchip,vo1-grf`, and compatible coverage is `rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
