<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,pdm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,pdm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,pdm.yaml` is a YAML Devicetree binding for Rockchip PDM controller. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Pulse Density Modulation Interface Controller (PDMC) is a PDM interface controller and decoder that support PDM format. It integrates a clock generator driving the PDM microphone and embeds filters which decimate the incoming bit stream to obtain most common audio rates.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,pdm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,pdm`, `rockchip,px30-pdm`, `rockchip,rk1808-pdm`, `rockchip,rk3308-pdm`, `rockchip,rk3568-pdm`, `rockchip,rv1126-pdm`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: enum `rockchip,pdm`, `rockchip,px30-pdm`, `rockchip,rk1808-pdm`, `rockchip,rk3308-pdm`, `rockchip,rk3568-pdm`, and 1 more
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`
- `clock-names`
- `dmas`: maxItems 1
- `dma-names`
- `power-domains`: maxItems 1
- `resets`
- `reset-names`
- `rockchip,path-map`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; Defines the mapping of PDM SDIx to PDM PATHx. By default, they are mapped one-to-one.
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 123 lines and 2841 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,pdm.yaml -->
