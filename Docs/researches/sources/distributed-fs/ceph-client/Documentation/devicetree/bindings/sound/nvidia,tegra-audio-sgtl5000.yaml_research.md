<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-sgtl5000.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-sgtl5000.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-sgtl5000.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with SGTL5000 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with SGTL5000 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-sgtl5000.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-sgtl5000([-_][a-z0-9]+)+$`, `nvidia,tegra-audio-sgtl5000`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

Key properties include:
- `compatible`
- `nvidia,audio-routing`: ref /schemas/types.yaml#/definitions/non-unique-string-array; minItems 2; A list of the connections between audio components. Each entry is a pair of strings, the first being the connection's sink, the second being the connection's source. Valid names for sources and sinks are the pins (documented in the binding document), and the jacks on the board.

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
describes board DAPM routing between jacks, pins, and codec widgets.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; routing arrays must use exact widget names and sink/source pairing.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; test invalid route widget names and odd-length route lists.
 Source read covered 67 lines and 1944 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-sgtl5000.yaml -->
