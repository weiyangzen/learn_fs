<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5651.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5651.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5651.yaml` is a YAML Devicetree binding for Realtek RT5651 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes) for RT5651: * DMIC L1 * DMIC R1 * IN1P * IN2P * IN2N * IN3P * HPOL * HPOR * LOUTL * LOUTR * PDML * PDMR

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5651.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5651`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: const realtek,rt5651
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const mclk
- `#sound-dai-cells`: const 0
- `realtek,in2-differential`: Indicate MIC2 input are differential, rather than single-ended.
- `realtek,dmic-en`: Indicates DMIC is used.
- `realtek,jack-detect-source`: ref /schemas/types.yaml#/definitions/uint32; enum `1`, `2`, `3`; Select jack-detect input pin.
- `realtek,jack-detect-not-inverted`: Normal jack-detect switches give an inverted (active-low) signal. Set this bool in the rare case you've a jack-detect switch which is not inverted.
- `realtek,over-current-threshold-microamp`: enum `600`, `1500`, `2000`; Micbias over-current detection threshold in µA.
- `realtek,over-current-scale-factor`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; Micbias over-current detection scale factor: 0: scale current by 0.5 1: scale current by 0.75 2: scale current by 1.0 3: scale current by 1.5

Maintainers listed by the binding are Bard Liao <bardliao@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 100 lines and 2109 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5651.yaml -->
