<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5645.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5645.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5645.yaml` is a YAML Devicetree binding for RT5650/RT5645 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes) for RT5645/RT5650: * DMIC L1 * DMIC R1 * DMIC L2 * DMIC R2 * IN1P * IN1N * IN2P * IN2N * Haptic Generator * HPOL * HPOR * LOUTL * LOUTR * PDM1L * PDM1R * SPOL * SPOR

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5645.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5645`, `realtek,rt5650`, required properties `compatible`, `reg`, `interrupts`, `avdd-supply`, `cpvdd-supply`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: enum `realtek,rt5645`, `realtek,rt5650`
- `reg`: maxItems 1
- `interrupts`: maxItems 1; The CODEC's interrupt output.
- `avdd-supply`: Power supply for AVDD, providing 1.8V.
- `cpvdd-supply`: Power supply for CPVDD, providing 1.8V.
- `hp-detect-gpios`: maxItems 1; A GPIO spec for the external headphone detect pin. If jd-mode = 0, we will get the JD status by getting the value of hp-detect-gpios.
- `cbj-sleeve-gpios`: maxItems 1; A GPIO spec to control the external combo jack circuit to tie the sleeve/ring2 contacts to the ground or floating. It could avoid some electric noise from the active speaker jacks.
- `realtek,in2-differential`: Indicate MIC2 input are differential, rather than single-ended.
- `realtek,dmic1-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`, `4`; Specify which pin to be used as DMIC1 data pin.
- `realtek,dmic2-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; Specify which pin to be used as DMIC2 data pin.
- `realtek,jd-mode`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; The JD mode of rt5645/rt5650.

Maintainers listed by the binding are Animesh Agarwal <animeshagarwal28@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 131 lines and 3299 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5645.yaml -->
