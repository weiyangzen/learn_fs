<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9120.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9120.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9120.yaml` is a YAML Devicetree binding for Richtek RT9120 Class-D audio amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The RT9120 is a high efficiency, I2S-input, stereo audio power amplifier delivering 2*20W into 8 Ohm BTL speaker loads. It supports the wide input voltage range from 4.5V to 26.4V to meet the need on most common applications like as TV, monitors. home entertainment, electronic music equipment.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/richtek,rt9120.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `richtek,rt9120`, required properties `compatible`, `reg`, `dvdd-supply`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `richtek,rt9120`
- `reg`: maxItems 1; I2C device address
- `pwdnn-gpios`: maxItems 1; GPIO used for power down, low active
- `dvdd-supply`: Supply for the default on DVDD power, voltage domain must be 3P3V or 1P8V
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are ChiYuan Huang <cy_huang@richtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 62 lines and 1366 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9120.yaml -->
