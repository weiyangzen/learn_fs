<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5640.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5640.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5640.yaml` is a YAML Devicetree binding for RT5640/RT5639 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes) for RT5639/RT5640: * DMIC1 * DMIC2 * MICBIAS1 * IN1P * IN1N * IN2P * IN2N * IN3P * IN3N * HPOL * HPOR * LOUTL * LOUTR * SPOLP * SPOLN * SPORP * SPORN Additional pins on the device for RT5640: * MONOP * MONON

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5640.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5640`, `realtek,rt5639`, required properties `compatible`, `reg`, `interrupts`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`.

Key properties include:
- `compatible`: enum `realtek,rt5640`, `realtek,rt5639`
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const mclk
- `interrupts`: maxItems 1; The CODEC's interrupt output.
- `realtek,in1-differential`: Indicate MIC1 input is differential, rather than single-ended.
- `realtek,in2-differential`: Indicate MIC2 input is differential, rather than single-ended.
- `realtek,in3-differential`: Indicate MIC3 input is differential, rather than single-ended.
- `realtek,lout-differential`: Indicate LOUT output is differential, rather than single-ended.
- `realtek,dmic1-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which pin to be used as DMIC1 data pin.
- `realtek,dmic2-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which pin to be used as DMIC2 data pin.
- `realtek,jack-detect-source`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`, `4`, and 3 more; The Jack Detect source.
- `realtek,jack-detect-not-inverted`: Normal jack-detect switches give an inverted signal, set this bool in the rare case you've a jack-detect switch which is not inverted.
- `realtek,over-current-threshold-microamp`: enum `600`, `1500`, `2000`; micbias over-current detection threshold in µA
- `...`: 2 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Neil Armstrong <neil.armstrong@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 157 lines and 3684 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5640.yaml -->
