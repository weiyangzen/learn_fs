<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rockchip-audio-max98090.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rockchip-audio-max98090.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rockchip-audio-max98090.yaml` is a YAML Devicetree binding for Rockchip audio complex with MAX98090 codec. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Rockchip audio complex with MAX98090 codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rockchip-audio-max98090.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rockchip-audio-max98090`, required properties `compatible`, `rockchip,model`, `rockchip,i2s-controller`, and referenced common schemas `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`.

Key properties include:
- `compatible`: const rockchip,rockchip-audio-max98090
- `rockchip,model`: ref /schemas/types.yaml#/definitions/string; The user-visible name of this sound complex.
- `rockchip,i2s-controller`: ref /schemas/types.yaml#/definitions/phandle; Phandle to the Rockchip I2S controller.
- `rockchip,audio-codec`: ref /schemas/types.yaml#/definitions/phandle; Phandle to the MAX98090 audio codec.
- `rockchip,headset-codec`: ref /schemas/types.yaml#/definitions/phandle; Phandle to the external chip for jack detection.
- `rockchip,hdmi-codec`: ref /schemas/types.yaml#/definitions/phandle; Phandle to the HDMI device for HDMI codec.

Maintainers listed by the binding are Fabio Estevam <festevam@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 59 lines and 1553 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rockchip-audio-max98090.yaml -->
