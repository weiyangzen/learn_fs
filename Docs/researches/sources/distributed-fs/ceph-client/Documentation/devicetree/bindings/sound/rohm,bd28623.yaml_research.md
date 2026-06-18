<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rohm,bd28623.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rohm,bd28623.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rohm,bd28623.yaml` is a YAML Devicetree binding for ROHM BD28623MUV Class D speaker amplifier for digital input. It falls in the rohm amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This codec does not have any control buses such as I2C, it detect format and rate of I2S signal automatically. It has two signals that can be connected to GPIOs reset and mute.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rohm,bd28623.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rohm,bd28623`, required properties `compatible`, `VCCA-supply`, `VCCP1-supply`, `VCCP2-supply`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const rohm,bd28623
- `#sound-dai-cells`: const 0
- `VCCA-supply`: regulator phandle for the VCCA (for analog) power supply
- `VCCP1-supply`: regulator phandle for the VCCP1 (for ch1) power supply
- `VCCP2-supply`: regulator phandle for the VCCP2 (for ch2) power supply
- `reset-gpios`: maxItems 1; GPIO specifier for the active low reset line
- `mute-gpios`: maxItems 1; GPIO specifier for the active low mute line

Maintainers listed by the binding are Katsuhiro Suzuki <katsuhiro@katsuster.net>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 70 lines and 1580 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rohm,bd28623.yaml -->
