# subset-b-000614 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-cpcap.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-cpcap.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-cpcap.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with CPCAP CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with CPCAP CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-cpcap.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^motorola,tegra-audio-cpcap(-[a-z0-9]+)+$`, `nvidia,tegra-audio-cpcap`, required properties none declared, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

Key properties include:
- `compatible`
- `nvidia,audio-routing`: ref /schemas/types.yaml#/definitions/non-unique-string-array; minItems 2; A list of the connections between audio components. Each entry is a pair of strings, the first being the connection's sink, the second being the connection's source. Valid names for sources and sinks are the pins (documented in the binding document), and the jacks on the board.

Maintainers listed by the binding are Svyatoslav Ryhel <clamor95@gmail.com>.

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
 Source read covered 90 lines and 2411 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-cpcap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-graph-card.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-graph-card.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-graph-card.yaml` is a YAML Devicetree binding for Audio Graph based Tegra sound card driver. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This is based on generic audio graph card driver along with additional customizations for Tegra platforms. It uses the same bindings with additional standard clock DT bindings required for Tegra.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-graph-card.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-audio-graph-card`, `nvidia,tegra186-audio-graph-card`, `nvidia,tegra238-audio-graph-card`, `nvidia,tegra264-audio-graph-card`, required properties `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, and referenced common schemas `audio-graph.yaml#`.

Key properties include:
- `compatible`: enum `nvidia,tegra210-audio-graph-card`, `nvidia,tegra186-audio-graph-card`, `nvidia,tegra238-audio-graph-card`, `nvidia,tegra264-audio-graph-card`
- `clocks`: minItems 2
- `clock-names`
- `assigned-clocks`: maxItems 3; minItems 1
- `assigned-clock-parents`: maxItems 3; minItems 1
- `assigned-clock-rates`: maxItems 3; minItems 1
- `interconnects`
- `interconnect-names`
- `iommus`: maxItems 1

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `audio-graph.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; depends on common clock framework phandles and assigned-clock policy.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 201 lines and 5466 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-graph-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max9808x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max9808x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max9808x.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with MAX9808x CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with MAX9808x CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-max9808x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-max98088(-[a-z0-9]+)+$`, `nvidia,tegra-audio-max98088`, `^[a-z0-9]+,tegra-audio-max98089(-[a-z0-9]+)+$`, `nvidia,tegra-audio-max98089`, required properties none declared, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 95 lines and 2622 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max9808x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max98090.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max98090.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max98090.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with MAX98090 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with MAX98090 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-max98090.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-max98090(-[a-z0-9]+)+$`, `nvidia,tegra-audio-max98090`, `nvidia,tegra-audio-max98090-nyan-big`, `nvidia,tegra-audio-max98090-nyan-blaze`, `nvidia,tegra-audio-max98090-nyan`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 97 lines and 2559 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-max98090.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5631.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5631.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5631.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with RT5631 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with RT5631 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-rt5631.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-rt5631(-[a-z0-9]+)+$`, `nvidia,tegra-audio-rt5631`, required properties none declared, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 85 lines and 2335 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5631.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5640.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5640.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5640.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with RT5639 or RT5640 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with RT5639 or RT5640 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-rt5640.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-rt56(39|40)(-[a-z0-9]+)+$`, `nvidia,tegra-audio-rt5640`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 84 lines and 2149 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5640.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5677.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5677.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5677.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with RT5677 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with RT5677 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-rt5677.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-rt5677(-[a-z0-9]+)+$`, `nvidia,tegra-audio-rt5677`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 100 lines and 2566 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-rt5677.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-trimslice.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-trimslice.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-trimslice.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with TrimSlice CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with TrimSlice CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-trimslice.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra-audio-trimslice`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`.

Key properties include:
- `compatible`: const nvidia,tegra-audio-trimslice

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `nvidia,tegra-audio-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 33 lines and 839 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-trimslice.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8753.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8753.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8753.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with WM8753 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with WM8753 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-wm8753.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-wm8753(-[a-z0-9]+)+$`, `nvidia,tegra-audio-wm8753`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 79 lines and 1957 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8753.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8903.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8903.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8903.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with WM8903 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with WM8903 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-wm8903.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-wm8903(-[a-z0-9]+)+$`, `nvidia,tegra-audio-wm8903`, `ad,tegra-audio-plutux`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 93 lines and 2477 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8903.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8962.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8962.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8962.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with WM8962 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with WM8962 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-wm8962.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-wm8962(-[a-z0-9]+)+$`, `nvidia,tegra-audio-wm8962`, required properties `nvidia,i2s-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

Key properties include:
- `compatible`
- `nvidia,audio-routing`: ref /schemas/types.yaml#/definitions/non-unique-string-array; minItems 2; A list of the connections between audio components. Each entry is a pair of strings, the first being the connection's sink, the second being the connection's source. Valid names for sources and sinks are the pins (documented in the binding document), and the jacks on the board.

Maintainers listed by the binding are Svyatoslav Ryhel <clamor95@gmail.com>.

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
 Source read covered 88 lines and 2316 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm8962.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm9712.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm9712.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm9712.yaml` is a YAML Devicetree binding for NVIDIA Tegra audio complex with WM9712 CODEC. It falls in the tegra board sound-card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra audio complex with WM9712 CODEC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra-audio-wm9712.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `^[a-z0-9]+,tegra-audio-wm9712([-_][a-z0-9]+)+$`, `nvidia,tegra-audio-wm9712`, required properties `nvidia,ac97-controller`, and referenced common schemas `nvidia,tegra-audio-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

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
 Source read covered 76 lines and 1948 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra-audio-wm9712.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-asrc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-asrc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-asrc.yaml` is a YAML Devicetree binding for Tegra186 ASRC. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Asynchronous Sample Rate Converter (ASRC) converts the sampling frequency of the input signal from one frequency to another. It can handle over a wide range of sample rate ratios (freq_in/freq_out) from 1:24 to 24:1. ASRC has two modes of operation. One where ratio can be programmed in SW and the other where it gets...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra186-asrc.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra186-asrc`, `nvidia,tegra264-asrc`, `nvidia,tegra234-asrc`, `nvidia,tegra194-asrc`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^asrc@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^ASRC[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports; ASRC has seven input ports and six output ports. Accordingly ACIF (Audio Client Interfaces) port nodes are defined to represent the ASRC inputs (port 0 to 6) and outputs (port 7 to 12). These are connected to corresponding ports on AHUB (Audio Hub). Additional input (port 6) is for receiving ratio information from e...

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 83 lines and 2288 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-asrc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-dspk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-dspk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-dspk.yaml` is a YAML Devicetree binding for Tegra186 DSPK Controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Digital Speaker Controller (DSPK) can be viewed as a Pulse Density Modulation (PDM) transmitter that up-samples the input to the desired sampling rate by interpolation and then converts the over sampled Pulse Code Modulation (PCM) input to the desired 1-bit output via Delta Sigma Modulation (DSM).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra186-dspk.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra186-dspk`, `nvidia,tegra264-dspk`, `nvidia,tegra234-dspk`, `nvidia,tegra194-dspk`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `sound-name-prefix`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^dspk@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const dspk
- `assigned-clocks`: maxItems 1
- `assigned-clock-parents`: maxItems 1
- `assigned-clock-rates`: maxItems 1
- `sound-name-prefix`: pattern `^DSPK[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 101 lines and 2384 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra186-dspk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-ac97.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-ac97.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-ac97.yaml` is a YAML Devicetree binding for NVIDIA Tegra20 AC97 controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra20 AC97 controller.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra20-ac97.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra20-ac97`, required properties `compatible`, `reg`, `resets`, `reset-names`, `interrupts`, `clocks`, `dmas`, `dma-names`, `nvidia,codec-reset-gpios`, and 1 more, and referenced common schemas none declared.

Key properties include:
- `compatible`: const nvidia,tegra20-ac97
- `reg`: maxItems 1
- `resets`: maxItems 1
- `reset-names`: const ac97
- `interrupts`: maxItems 1
- `clocks`: maxItems 1
- `dmas`: maxItems 2
- `dma-names`
- `nvidia,codec-reset-gpios`: maxItems 1; Reset pin of external AC97 codec
- `nvidia,codec-sync-gpios`: maxItems 1; AC97 DAP _FS line

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 82 lines and 1731 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-ac97.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-das.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-das.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-das.yaml` is a YAML Devicetree binding for NVIDIA Tegra 20 DAS (Digital Audio Switch) controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra 20 DAS (Digital Audio Switch) controller.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra20-das.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra20-das`, required properties `compatible`, `reg`, and referenced common schemas none declared.

Key properties include:
- `compatible`: const nvidia,tegra20-das
- `reg`: maxItems 1

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 36 lines and 704 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-das.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-i2s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-i2s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-i2s.yaml` is a YAML Devicetree binding for NVIDIA Tegra20 I2S Controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The I2S Controller streams synchronous serial audio data between system memory and an external audio device. The controller supports the I2S Left Justified Mode, Right Justified Mode, and DSP mode formats.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra20-i2s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra20-i2s`, required properties `compatible`, `reg`, `resets`, `reset-names`, `interrupts`, `clocks`, `dmas`, `dma-names`, and referenced common schemas none declared.

Key properties include:
- `compatible`: const nvidia,tegra20-i2s
- `reg`: maxItems 1
- `resets`: maxItems 1
- `reset-names`: const i2s
- `interrupts`: maxItems 1
- `clocks`: minItems 1
- `dmas`: minItems 2
- `dma-names`
- `nvidia,fixed-parent-rate`: Specifies whether board prefers parent clock to stay at a fixed rate. This allows multiple Tegra20 audio components work simultaneously by limiting number of supportable audio rates.

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 77 lines and 1564 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-spdif.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-spdif.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-spdif.yaml` is a YAML Devicetree binding for NVIDIA Tegra20 S/PDIF Controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The S/PDIF controller supports both input and output in serial audio digital interface format. The input controller can digitally recover a clock from the received stream. The S/PDIF controller is also used to generate the embedded audio for HDMI output channel.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra20-spdif.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra20-spdif`, required properties `compatible`, `reg`, `resets`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const nvidia,tegra20-spdif
- `reg`: maxItems 1
- `resets`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`: minItems 2
- `clock-names`
- `dmas`: minItems 2
- `dma-names`
- `#sound-dai-cells`: const 0
- `nvidia,fixed-parent-rate`: Specifies whether board prefers parent clock to stay at a fixed rate. This allows multiple Tegra20 audio components work simultaneously by limiting number of supportable audio rates.

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 88 lines and 1797 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra20-spdif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-admaif.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-admaif.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-admaif.yaml` is a YAML Devicetree binding for Tegra210 ADMAIF. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. ADMAIF is the interface between ADMA and AHUB. Each ADMA channel that sends/receives data to/from AHUB must interface through an ADMAIF channel. ADMA channel sending data to AHUB pairs with ADMAIF Tx channel and ADMA channel receiving data from AHUB pairs with ADMAIF Rx channel.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-admaif.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-admaif`, `nvidia,tegra186-admaif`, `nvidia,tegra264-admaif`, `nvidia,tegra234-admaif`, `nvidia,tegra194-admaif`, required properties `compatible`, `reg`, `dmas`, `dma-names`, and referenced common schemas `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^admaif@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- dmas
- dma-names
- `interconnects`
- `interconnect-names`
- `iommus`: maxItems 1
- `ports`: ref /schemas/graph.yaml#/properties/ports; Contains list of ACIF (Audio CIF) port nodes for ADMAIF channels. The number of port nodes depends on the number of ADMAIF channels that SoC may have. These are interfaced with respective ACIF ports in AHUB (Audio Hub). Each port is capable of data transfers in both directions.

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; binds to DMA channels for PCM traffic; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; DMA name/order mismatches can produce silent probe or stream failures; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check DMA channel/name tuple counts.
 Source read covered 172 lines and 4513 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-admaif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-adx.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-adx.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-adx.yaml` is a YAML Devicetree binding for Tegra210 ADX. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Audio Demultiplexer (ADX) block takes an input stream with up to 16 channels and demultiplexes it into four output streams of up to 16 channels each. A byte RAM helps to form output frames by any combination of bytes from the input frame. Its design is identical to that of byte RAM in the AMX except that the dat...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-adx.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-adx`, `nvidia,tegra264-adx`, `nvidia,tegra234-adx`, `nvidia,tegra194-adx`, `nvidia,tegra186-adx`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^adx@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^ADX[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports; ADX has one input and four outputs. Accordingly ACIF (Audio Client Interface) port nodes are defined to represent ADX input (port 0) and outputs (ports 1 to 4). These are connected to corresponding ports on AHUB (Audio Hub).

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 79 lines and 2020 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-adx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ahub.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ahub.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ahub.yaml` is a YAML Devicetree binding for Tegra210 AHUB. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Audio Hub (AHUB) comprises a collection of hardware accelerators for audio pre-processing, post-processing and a programmable full crossbar for routing audio data across these accelerators. It has external interfaces such as I2S, DMIC, DSPK. It interfaces with ADMA engine through ADMAIF.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-ahub.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-ahub`, `nvidia,tegra186-ahub`, `nvidia,tegra234-ahub`, `nvidia,tegra264-ahub`, `nvidia,tegra194-ahub`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `#address-cells`, `#size-cells`, `ranges`, and referenced common schemas `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, `nvidia,tegra210-dmic.yaml#`, `nvidia,tegra210-admaif.yaml#`, `nvidia,tegra186-dspk.yaml#`, `nvidia,tegra210-mvc.yaml#`, `nvidia,tegra210-sfc.yaml#`, `nvidia,tegra210-amx.yaml#`, `nvidia,tegra210-adx.yaml#`, and 3 more.

Key properties include:
- `$nodename`: pattern `^ahub@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const ahub
- `assigned-clocks`: maxItems 1
- `assigned-clock-parents`: maxItems 1
- `assigned-clock-rates`: maxItems 1
- `#address-cells`: enum `1`, `2`
- `#size-cells`: enum `1`, `2`
- ranges
- `ports`: ref /schemas/graph.yaml#/properties/ports; Contains list of ACIF (Audio CIF) port nodes for AHUB (Audio Hub). These are connected to ACIF interfaces of AHUB clients. Thus the number of port nodes depend on the number of clients that AHUB may have depending on the SoC revision.

Pattern properties define child node classes: `^i2s@[0-9a-f]+$`, `^dmic@[0-9a-f]+$`, `^admaif@[0-9a-f]+$`, `^dspk@[0-9a-f]+$`, `^mvc@[0-9a-f]+$`, `^sfc@[0-9a-f]+$`, `^amx@[0-9a-f]+$`, `^adx@[0-9a-f]+$`, `^amixer@[0-9a-f]+$`, and 2 more.

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, `nvidia,tegra210-dmic.yaml#`, `nvidia,tegra210-admaif.yaml#`, `nvidia,tegra186-dspk.yaml#`, `nvidia,tegra210-mvc.yaml#`, `nvidia,tegra210-sfc.yaml#`, and 5 more, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; clock order, names, and rates must match the SoC driver expectation; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 197 lines and 5037 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ahub.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-amx.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-amx.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-amx.yaml` is a YAML Devicetree binding for Tegra210 AMX. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Audio Multiplexer (AMX) block can multiplex up to four input streams each of which can have maximum 16 channels and generate an output stream with maximum 16 channels. A byte RAM helps to form an output frame by any combination of bytes from the input frames.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-amx.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-amx`, `nvidia,tegra194-amx`, `nvidia,tegra264-amx`, `nvidia,tegra186-amx`, `nvidia,tegra234-amx`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^amx@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^AMX[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports; AMX has four inputs and one output. Accordingly ACIF (Audio Client Interfaces) port nodes are defined to represent AMX inputs (port 0 to 3) and output (port 4). These are connected to corresponding ports on AHUB (Audio Hub).

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 81 lines and 1975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-amx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-dmic.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-dmic.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-dmic.yaml` is a YAML Devicetree binding for Tegra210 DMIC Controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Digital MIC (DMIC) Controller is used to interface with Pulse Density Modulation (PDM) input devices. It converts PDM signals to Pulse Coded Modulation (PCM) signals. DMIC can be viewed as a PDM receiver.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-dmic.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-dmic`, `nvidia,tegra264-dmic`, `nvidia,tegra234-dmic`, `nvidia,tegra194-dmic`, `nvidia,tegra186-dmic`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^dmic@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const dmic
- `assigned-clocks`: maxItems 1
- `assigned-clock-parents`: maxItems 1
- `assigned-clock-rates`: maxItems 1
- `sound-name-prefix`: pattern `^DMIC[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 100 lines and 2316 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-dmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-i2s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-i2s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-i2s.yaml` is a YAML Devicetree binding for Tegra210 I2S Controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Inter-IC Sound (I2S) controller implements full-duplex, bi-directional and single direction point-to-point serial interfaces. It can interface with I2S compatible devices. I2S controller can operate both in master and slave mode.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-i2s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-i2s`, `nvidia,tegra264-i2s`, `nvidia,tegra234-i2s`, `nvidia,tegra194-i2s`, `nvidia,tegra186-i2s`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^i2s@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `clocks`: minItems 1
- `clock-names`: minItems 1
- `assigned-clocks`: maxItems 2; minItems 1
- `assigned-clock-parents`: maxItems 2; minItems 1
- `assigned-clock-rates`: maxItems 2; minItems 1
- `sound-name-prefix`: pattern `^I2S[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 117 lines and 2962 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mbdrc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mbdrc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mbdrc.yaml` is a YAML Devicetree binding for Tegra210 MBDRC. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Multi Band Dynamic Range Compressor (MBDRC) is part of Output Processing Engine (OPE) which interfaces with Audio Hub (AHUB) via Audio Client Interface (ACIF). MBDRC can be used as a traditional single full band or a dual band or a multi band dynamic processor.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-mbdrc.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-mbdrc`, `nvidia,tegra264-mbdrc`, `nvidia,tegra234-mbdrc`, `nvidia,tegra194-mbdrc`, `nvidia,tegra186-mbdrc`, required properties `compatible`, `reg`, and referenced common schemas none declared.

Key properties include:
- `compatible`
- `reg`: maxItems 1

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 48 lines and 1170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mbdrc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mixer.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mixer.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mixer.yaml` is a YAML Devicetree binding for Tegra210 Mixer. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Mixer supports mixing of up to ten 7.1 audio input streams and generate five outputs (each of which can be any combination of the ten input streams).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-mixer.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-amixer`, `nvidia,tegra264-amixer`, `nvidia,tegra234-amixer`, `nvidia,tegra194-amixer`, `nvidia,tegra186-amixer`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^amixer@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^MIXER[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports; Mixer has ten inputs and five outputs. Accordingly ACIF (Audio Client Interfaces) port nodes are defined to represent Mixer inputs (port 0 to 9) and outputs (port 10 to 14). These are connected to corresponding ports on AHUB (Audio Hub).

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 76 lines and 1863 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mixer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mvc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mvc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mvc.yaml` is a YAML Devicetree binding for Tegra210 MVC. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Master Volume Control (MVC) provides gain or attenuation to a digital signal path. It can be used in input or output signal path for per-stream volume control or it can be used as master volume control. The MVC block has one input and one output. The input digital stream can be mono or multi-channel (up to 7.1 c...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-mvc.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-mvc`, `nvidia,tegra264-mvc`, `nvidia,tegra234-mvc`, `nvidia,tegra194-mvc`, `nvidia,tegra186-mvc`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^mvc@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^MVC[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 78 lines and 1971 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-mvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ope.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ope.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ope.yaml` is a YAML Devicetree binding for Tegra210 OPE. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Output Processing Engine (OPE) is one of the AHUB client. It has PEQ (Parametric Equalizer) and MBDRC (Multi Band Dynamic Range Compressor) sub blocks for data processing.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-ope.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-ope`, `nvidia,tegra264-ope`, `nvidia,tegra234-ope`, `nvidia,tegra194-ope`, `nvidia,tegra186-ope`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, `nvidia,tegra210-peq.yaml#`, `nvidia,tegra210-mbdrc.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `#address-cells`: enum `1`, `2`
- `#size-cells`: enum `1`, `2`
- ranges
- `sound-name-prefix`: pattern `^OPE[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Pattern properties define child node classes: `^equalizer@[0-9a-f]+$`, `^dynamic-range-compressor@[0-9a-f]+$`.

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, `nvidia,tegra210-peq.yaml#`, `nvidia,tegra210-mbdrc.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 88 lines and 1997 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-ope.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-peq.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-peq.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-peq.yaml` is a YAML Devicetree binding for Tegra210 PEQ. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Parametric Equalizer (PEQ) is a cascade of biquad filters with each filter tuned based on certain parameters. It can be used to equalize the irregularities in the speaker frequency response. PEQ sits inside Output Processing Engine (OPE) which interfaces with Audio Hub (AHUB) via Audio Client Interface (ACIF).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-peq.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-peq`, `nvidia,tegra264-peq`, `nvidia,tegra234-peq`, `nvidia,tegra194-peq`, `nvidia,tegra186-peq`, required properties `compatible`, `reg`, and referenced common schemas none declared.

Key properties include:
- `compatible`
- `reg`: maxItems 1

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 49 lines and 1189 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-peq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-sfc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-sfc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-sfc.yaml` is a YAML Devicetree binding for Tegra210 SFC. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Sampling Frequency Converter (SFC) converts the sampling frequency of the input signal from one frequency to another. It supports sampling frequency conversions of streams of up to two channels (stereo).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra210-sfc.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra210-sfc`, `nvidia,tegra264-sfc`, `nvidia,tegra234-sfc`, `nvidia,tegra194-sfc`, `nvidia,tegra186-sfc`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `$nodename`: pattern `^sfc@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `sound-name-prefix`: pattern `^SFC[1-9]$`
- `ports`: ref /schemas/graph.yaml#/properties/ports

Maintainers listed by the binding are Jon Hunter <jonathanh@nvidia.com>, Mohan Kumar <mkumard@nvidia.com>, Sameer Pujar <spujar@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints.
 Source read covered 75 lines and 1776 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra210-sfc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-hda.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-hda.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-hda.yaml` is a YAML Devicetree binding for NVIDIA Tegra HDA controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The High Definition Audio (HDA) block provides a serial interface to audio codec. It supports multiple input and output streams.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra30-hda.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra30-hda`, `nvidia,tegra194-hda`, `nvidia,tegra234-hda`, `nvidia,tegra264-hda`, `nvidia,tegra186-hda`, `nvidia,tegra210-hda`, `nvidia,tegra124-hda`, `nvidia,tegra114-hda`, `nvidia,tegra132-hda`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, and referenced common schemas `/schemas/types.yaml#/definitions/string`.

Key properties include:
- `$nodename`: pattern `^hda@[0-9a-f]*$`
- `compatible`
- `reg`: maxItems 1
- `interrupts`: maxItems 1; The interrupt from the HDA controller
- `clocks`: maxItems 3; minItems 1
- `clock-names`: maxItems 3; minItems 1
- `resets`: maxItems 3; minItems 2
- `reset-names`: maxItems 3; minItems 2
- `power-domains`: maxItems 1
- `interconnects`: maxItems 2
- `interconnect-names`
- `iommus`: maxItems 1
- `nvidia,model`: ref /schemas/types.yaml#/definitions/string; The user-visible name of this sound complex. If this property is not specified then boards can use default name provided in hda driver.

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/string`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 198 lines and 4405 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-hda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-i2s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-i2s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-i2s.yaml` is a YAML Devicetree binding for NVIDIA Tegra30 I2S controller. It falls in the nvidia tegra audio controller or ahub binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NVIDIA Tegra30 I2S controller.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nvidia,tegra30-i2s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nvidia,tegra124-i2s`, `nvidia,tegra30-i2s`, `nvidia,tegra114-i2s`, required properties `compatible`, `reg`, `clocks`, `resets`, `reset-names`, `nvidia,ahub-cif-ids`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const i2s
- `resets`: maxItems 1
- `reset-names`: const i2s
- `nvidia,ahub-cif-ids`: ref /schemas/types.yaml#/definitions/uint32-array; list of AHUB CIF IDs

Maintainers listed by the binding are Thierry Reding <treding@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 67 lines and 1313 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nvidia,tegra30-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,lpc3220-i2s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,lpc3220-i2s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,lpc3220-i2s.yaml` is a YAML Devicetree binding for NXP LPC32XX I2S Controller. It falls in the nxp audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The I2S controller in LPC32XX SoCs, ASoC DAI.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nxp,lpc3220-i2s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nxp,lpc3220-i2s`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `nxp,lpc3220-i2s`
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`
- `dmas`
- `dma-names`
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are J.M.B. Downing <jonathan.downing@nautel.com>, Piotr Wojtaszczyk <piotr.wojtaszczyk@timesys.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 73 lines and 1359 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,lpc3220-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,tfa989x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,tfa989x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,tfa989x.yaml` is a YAML Devicetree binding for NXP/Goodix TFA989X (TFA1) Audio Amplifiers. It falls in the nxp audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: NXP/Goodix TFA989X (TFA1) Audio Amplifiers.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/nxp,tfa989x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `nxp,tfa9890`, `nxp,tfa9895`, `nxp,tfa9897`, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `nxp,tfa9890`, `nxp,tfa9895`, `nxp,tfa9897`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 0
- `rcv-gpios`: optional GPIO to be asserted when receiver mode is enabled.
- sound-name-prefix
- `vddd-supply`: regulator phandle for the VDDD power supply.

Maintainers listed by the binding are Stephan Gerhold <stephan@gerhold.net>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, `if`, `then`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 99 lines and 2132 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/nxp,tfa989x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/option,gtm601.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/option,gtm601.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/option,gtm601.yaml` is a YAML Devicetree binding for GTM601 UMTS modem audio interface CODEC. It falls in the devicetree sound binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device has no configuration interface. The sample rate and channels are based on the compatible string

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/option,gtm601.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `broadmobi,bm818`, `option,gtm601`, required properties `compatible`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are kernel@puri.sm.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 42 lines and 869 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/option,gtm601.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,apq8016-sbc-sndcard.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,apq8016-sbc-sndcard.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,apq8016-sbc-sndcard.yaml` is a YAML Devicetree binding for Qualcomm APQ8016 and similar sound cards. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm APQ8016 and similar sound cards.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,apq8016-sbc-sndcard.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,apq8016-sbc-sndcard`, `qcom,msm8916-qdsp6-sndcard`, required properties `compatible`, `reg`, `reg-names`, `model`, and referenced common schemas `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`.

Key properties include:
- `compatible`: enum `qcom,apq8016-sbc-sndcard`, `qcom,msm8916-qdsp6-sndcard`
- `reg`
- `reg-names`
- `audio-routing`: ref /schemas/types.yaml#/definitions/non-unique-string-array; A list of the connections between audio components. Each entry is a pair of strings, the first being the connection's sink, the second being the connection's source. Valid names could be power supplies, MicBias of codec and the jacks on the board.
- `aux-devs`: ref /schemas/types.yaml#/definitions/phandle-array; List of phandles pointing to auxiliary devices, such as amplifiers, to be added to the sound card.
- `model`: ref /schemas/types.yaml#/definitions/string; User visible long sound card name
- `pin-switches`: ref /schemas/types.yaml#/definitions/string-array; List of widget names for which pin switches should be created.
- `widgets`: ref /schemas/types.yaml#/definitions/non-unique-string-array; User specified audio sound widgets.

Pattern properties define child node classes: `.*-dai-link$`.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Stephan Gerhold <stephan@gerhold.net>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`; describes board DAPM routing between jacks, pins, and codec widgets.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; routing arrays must use exact widget names and sink/source pairing; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; test invalid route widget names and odd-length route lists.
 Source read covered 205 lines and 5549 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,apq8016-sbc-sndcard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-cpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-cpu.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-cpu.yaml` is a YAML Devicetree binding for Qualcomm Technologies Inc. LPASS CPU dai driver. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm Technologies Inc. SOC Low-Power Audio SubSystem (LPASS) that consist of MI2S interface for audio data transfer on external codecs. LPASS cpu driver is a module to configure Low-Power Audio Interface(LPAIF) core registers across different IP versions.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,lpass-cpu.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,lpass-cpu`, `qcom,apq8016-lpass-cpu`, `qcom,sc7180-lpass-cpu`, `qcom,sc7280-lpass-cpu`, required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `qcom,lpass-cpu`, `qcom,apq8016-lpass-cpu`, `qcom,sc7180-lpass-cpu`, `qcom,sc7280-lpass-cpu`
- `reg`: maxItems 6; minItems 1; LPAIF core registers
- `reg-names`: maxItems 6; minItems 1
- `clocks`: maxItems 10; minItems 3
- `clock-names`: maxItems 10; minItems 1
- `interrupts`: maxItems 4; minItems 1; LPAIF DMA buffer interrupt
- `interrupt-names`: maxItems 4; minItems 1
- `qcom,adsp`: ref /schemas/types.yaml#/definitions/phandle; Phandle for the audio DSP node
- `iommus`: maxItems 3; minItems 2; Phandle to apps_smmu node with sid mask
- `power-domains`: maxItems 1
- `power-domain-names`: maxItems 1
- `required-opps`: maxItems 1
- `#sound-dai-cells`: const 1
- `#address-cells`: const 1
- `...`: 1 additional schema properties omitted from this compact listing

Pattern properties define child node classes: `^dai-link@[0-9a-f]+$`.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Rohit kumar <quic_rohkumar@quicinc.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 290 lines and 6857 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-cpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-rx-macro.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-rx-macro.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-rx-macro.yaml` is a YAML Devicetree binding for LPASS(Low Power Audio Subsystem) RX Macro audio codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: LPASS(Low Power Audio Subsystem) RX Macro audio codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,lpass-rx-macro.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,sc7280-lpass-rx-macro`, `qcom,sm6115-lpass-rx-macro`, `qcom,sm8250-lpass-rx-macro`, `qcom,sm8450-lpass-rx-macro`, `qcom,sm8550-lpass-rx-macro`, `qcom,sc8280xp-lpass-rx-macro`, `qcom,kaanapali-lpass-rx-macro`, `qcom,sm8650-lpass-rx-macro`, `qcom,sm8750-lpass-rx-macro`, and 1 more, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 1
- `#clock-cells`: const 0
- `clocks`: maxItems 5; minItems 3
- `clock-names`: maxItems 5; minItems 3
- `clock-output-names`: maxItems 1
- `power-domains`: maxItems 2
- `power-domain-names`

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 157 lines and 3555 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-rx-macro.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-tx-macro.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-tx-macro.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-tx-macro.yaml` is a YAML Devicetree binding for LPASS(Low Power Audio Subsystem) TX Macro audio codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: LPASS(Low Power Audio Subsystem) TX Macro audio codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,lpass-tx-macro.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,sc7280-lpass-tx-macro`, `qcom,sm6115-lpass-tx-macro`, `qcom,sm8250-lpass-tx-macro`, `qcom,sm8450-lpass-tx-macro`, `qcom,sm8550-lpass-tx-macro`, `qcom,sc8280xp-lpass-tx-macro`, `qcom,kaanapali-lpass-tx-macro`, `qcom,sm8650-lpass-tx-macro`, `qcom,sm8750-lpass-tx-macro`, and 1 more, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 1
- `#clock-cells`: const 0
- `clocks`: maxItems 5; minItems 3
- `clock-names`: maxItems 5; minItems 3
- `clock-output-names`: maxItems 1
- `power-domains`: maxItems 2
- `power-domain-names`
- `qcom,dmic-sample-rate`: ref /schemas/types.yaml#/definitions/uint32; dmic sample rate

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 162 lines and 3701 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-tx-macro.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-va-macro.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-va-macro.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-va-macro.yaml` is a YAML Devicetree binding for LPASS(Low Power Audio Subsystem) VA Macro audio codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: LPASS(Low Power Audio Subsystem) VA Macro audio codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,lpass-va-macro.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,sc7280-lpass-va-macro`, `qcom,sm6115-lpass-va-macro`, `qcom,sm8250-lpass-va-macro`, `qcom,sm8450-lpass-va-macro`, `qcom,sm8550-lpass-va-macro`, `qcom,sc8280xp-lpass-va-macro`, `qcom,glymur-lpass-va-macro`, `qcom,kaanapali-lpass-va-macro`, `qcom,sm8650-lpass-va-macro`, and 2 more, required properties `compatible`, `reg`, `#sound-dai-cells`, `clock-names`, `clocks`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 1
- `#clock-cells`: const 0
- `clocks`: maxItems 4; minItems 1
- `clock-names`: maxItems 4; minItems 1
- `clock-output-names`: maxItems 1
- `power-domains`: maxItems 2
- `power-domain-names`
- `qcom,dmic-sample-rate`: ref /schemas/types.yaml#/definitions/uint32; dmic sample rate
- `vdd-micb-supply`: phandle to voltage regulator of MIC Bias

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 187 lines and 4082 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-va-macro.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-wsa-macro.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-wsa-macro.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-wsa-macro.yaml` is a YAML Devicetree binding for LPASS(Low Power Audio Subsystem) VA Macro audio codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: LPASS(Low Power Audio Subsystem) VA Macro audio codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,lpass-wsa-macro.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,sc7280-lpass-wsa-macro`, `qcom,sm8250-lpass-wsa-macro`, `qcom,sm8450-lpass-wsa-macro`, `qcom,sm8550-lpass-wsa-macro`, `qcom,sc8280xp-lpass-wsa-macro`, `qcom,glymur-lpass-wsa-macro`, `qcom,kaanapali-lpass-wsa-macro`, `qcom,sm8650-lpass-wsa-macro`, `qcom,sm8750-lpass-wsa-macro`, and 1 more, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 1
- `#clock-cells`: const 0
- `clocks`: maxItems 6; minItems 4
- `clock-names`: maxItems 6; minItems 4
- `clock-output-names`: maxItems 1
- `qcom,dmic-sample-rate`: ref /schemas/types.yaml#/definitions/uint32; dmic sample rate
- `vdd-micb-supply`: phandle to voltage regulator of MIC Bias

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 122 lines and 2899 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,lpass-wsa-macro.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,msm8916-wcd-digital-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,msm8916-wcd-digital-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,msm8916-wcd-digital-codec.yaml` is a YAML Devicetree binding for Qualcomm MSM8916 WCD Digital Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The digital WCD audio codec found on Qualcomm MSM8916 LPASS.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,msm8916-wcd-digital-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,msm8916-wcd-digital-codec`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const qcom,msm8916-wcd-digital-codec
- `reg`: maxItems 1
- `clocks`: maxItems 2
- `clock-names`
- `#sound-dai-cells`: const 1

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 55 lines and 1152 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,msm8916-wcd-digital-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-codec.yaml` is a YAML Devicetree binding for Qualcomm PM4125 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The audio codec IC found on Qualcomm PM4125/PM2250 PMIC. It has RX and TX Soundwire slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,pm4125-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,pm4125-codec`, required properties `compatible`, `reg`, `vdd-io-supply`, `vdd-cp-supply`, `vdd-mic-bias-supply`, `vdd-pa-vpos-supply`, `qcom,tx-device`, `qcom,rx-device`, `qcom,micbias1-microvolt`, and 3 more, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`.

Key properties include:
- `compatible`: const qcom,pm4125-codec
- `reg`: maxItems 1; Specifies the SPMI base address for the audio codec peripherals. The address space contains reset register needed to power-on the codec.
- `reg-names`: maxItems 1
- `vdd-io-supply`: A reference to the 1.8V I/O supply
- `vdd-cp-supply`: A reference to the charge pump I/O supply
- `vdd-mic-bias-supply`: A reference to the 3.3V mic bias supply
- `vdd-pa-vpos-supply`: A reference to the PA VPOS supply
- `qcom,tx-device`: ref /schemas/types.yaml#/definitions/phandle-array; A reference to Soundwire tx device phandle
- `qcom,rx-device`: ref /schemas/types.yaml#/definitions/phandle-array; A reference to Soundwire rx device phandle
- `qcom,micbias1-microvolt`: micbias1 voltage
- `qcom,micbias2-microvolt`: micbias2 voltage
- `qcom,micbias3-microvolt`: micbias3 voltage
- `qcom,mbhc-buttons-vthreshold-microvolt`: maxItems 8; minItems 8; Array of 8 Voltage threshold values corresponding to headset button0 - button7
- `#sound-dai-cells`: const 1

Maintainers listed by the binding are Alexey Klimov <alexey.klimov@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 134 lines and 3256 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-sdw.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-sdw.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-sdw.yaml` is a YAML Devicetree binding for Qualcomm SoundWire Slave devices on PM4125/PM2250 PMIC audio codec.. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The audio codec IC found on Qualcomm PM4125/PM2250 PMICs. It has RX and TX Soundwire slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,pm4125-sdw.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw20217010c00`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const sdw20217010c00
- `reg`: maxItems 1
- `qcom,tx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; minItems 2; Specifies static port mapping between device and host tx ports. In the order of the device port index which are adc1_port, adc23_port, dmic03_mbhc_port, dmic46_port. Supports maximum 2 tx soundwire ports. PM4125 TX Port 1 (ADC1,2 & DMIC0 & MBHC) <=> SWR0 Port 1 PM4125 TX Port 2 (ADC1 & DMIC0,1,2 & MBHC) <=> SWR0 Port 2
- `qcom,rx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 5; minItems 2; Specifies static port mapping between device and host rx ports. In the order of device port index which are hph_port, clsh_port, comp_port, lo_port, dsd port. Supports maximum 2 rx soundwire ports. PM4125 RX Port 1 (HPH_L/R) <==> SWR1 Port 1 (HPH_L/R) PM4125 RX Port 2 (COMP_L/R) <==> SWR1 Port 3 (COMP_L/R)

Maintainers listed by the binding are Alexey Klimov <alexey.klimov@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `oneOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`; integrates with SoundWire child-device topology.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 79 lines and 2038 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm4125-sdw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm8916-wcd-analog-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm8916-wcd-analog-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm8916-wcd-analog-codec.yaml` is a YAML Devicetree binding for Qualcomm PM8916 WCD Analog Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The analog WCD audio codec found on Qualcomm PM8916 PMIC.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,pm8916-wcd-analog-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,pm8916-wcd-analog-codec`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: const qcom,pm8916-wcd-analog-codec
- `reg`: maxItems 1
- `interrupts`: maxItems 14
- `interrupt-names`
- `vdd-cdc-io-supply`: 1.8V buck supply
- `vdd-cdc-tx-rx-cx-supply`: 1.8V SIDO buck supply
- `vdd-micbias-supply`: micbias supply
- `qcom,mbhc-vthreshold-low`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 5; minItems 5; Array of 5 threshold voltages in mV for 5-button detection on headset when MBHC is powered by an internal current source.
- `qcom,mbhc-vthreshold-high`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 5; minItems 5; Array of 5 threshold voltages in mV for 5-button detection on headset when MBHC is powered from micbias.
- `qcom,micbias-lvl`: ref /schemas/types.yaml#/definitions/uint32; Voltage (mV) for Mic Bias
- `qcom,hphl-jack-type-normally-open`: True if the HPHL pin on the jack is NO (Normally Open), false if it's NC (Normally Closed).
- `qcom,gnd-jack-type-normally-open`: True if the GND pin on the jack is NO (Normally Open), false if it's NC (Normally Closed).
- `qcom,micbias1-ext-cap`: True if micbias1 has an external capacitor.
- `qcom,micbias2-ext-cap`: True if micbias2 has an external capacitor.
- `...`: 1 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Konrad Dybcio <konradybcio@kernel.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 153 lines and 4433 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,pm8916-wcd-analog-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm-routing.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm-routing.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm-routing.yaml` is a YAML Devicetree binding for Qualcomm Audio Device Manager (Q6ADM) routing. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm Audio Device Manager (Q6ADM) routing node represents routing specific configuration.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6adm-routing.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6adm-routing`, required properties `compatible`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6adm-routing`
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

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
 Source read covered 39 lines and 792 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm-routing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm.yaml` is a YAML Devicetree binding for Qualcomm Audio Device Manager (Q6ADM). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Audio Device Manager (Q6ADM).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6adm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6adm`, required properties `compatible`, `routing`, and referenced common schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6adm-routing.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6adm`
- `routing`: ref /schemas/sound/qcom,q6adm-routing.yaml#; Qualcomm DSP LPASS audio routing

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6adm-routing.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 51 lines and 1121 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6adm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6afe.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6afe.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6afe.yaml` is a YAML Devicetree binding for Qualcomm Audio FrontEnd (Q6AFE). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Audio FrontEnd (Q6AFE).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6afe.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6afe`, required properties `compatible`, `dais`, and referenced common schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-clocks.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-ports.yaml#`, `/schemas/sound/qcom,q6usb.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6afe`
- `clock-controller`: ref /schemas/sound/qcom,q6dsp-lpass-clocks.yaml#; Qualcomm DSP LPASS clock controller
- `dais`: ref /schemas/sound/qcom,q6dsp-lpass-ports.yaml#; Qualcomm DSP audio ports
- `usbd`: ref /schemas/sound/qcom,q6usb.yaml#; Qualcomm DSP USB audio ports

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-clocks.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-ports.yaml#`, `/schemas/sound/qcom,q6usb.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 81 lines and 2024 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6afe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-dai.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-dai.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-dai.yaml` is a YAML Devicetree binding for Qualcomm Audio Process Manager Digital Audio Interfaces. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This binding describes the Qualcomm APM DAIs in DSP

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6apm-dai.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6apm-dais`, required properties `compatible`, `iommus`, and referenced common schemas none declared.

Key properties include:
- `compatible`: const qcom,q6apm-dais
- `iommus`: maxItems 2; minItems 1

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 34 lines and 669 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-dai.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-lpass-dais.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-lpass-dais.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-lpass-dais.yaml` is a YAML Devicetree binding for Qualcomm DSP LPASS (Low Power Audio SubSystem) Audio Ports. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm DSP LPASS (Low Power Audio SubSystem) Audio Ports.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6apm-lpass-dais.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6apm-lpass-dais`, required properties `compatible`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6apm-lpass-dais`
- `#sound-dai-cells`: const 1

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

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
 Source read covered 35 lines and 699 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm-lpass-dais.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm.yaml` is a YAML Devicetree binding for Qualcomm Audio Process Manager (Q6APM). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Audio Process Manager (Q6APM).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6apm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6apm`, required properties `compatible`, `bedais`, `dais`, and referenced common schemas `dai-common.yaml#`, `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6apm-lpass-dais.yaml#`, `/schemas/sound/qcom,q6apm-dai.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6apm`
- `bedais`: ref /schemas/sound/qcom,q6apm-lpass-dais.yaml#; Qualcomm DSP audio ports
- `dais`: ref /schemas/sound/qcom,q6apm-dai.yaml#; Qualcomm DSP audio ports
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6apm-lpass-dais.yaml#`, `/schemas/sound/qcom,q6apm-dai.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 68 lines and 1512 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6apm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm-dais.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm-dais.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm-dais.yaml` is a YAML Devicetree binding for Qualcomm Audio Stream Manager (Q6ASM). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Q6ASM is one of the APR audio services on Q6DSP. Each of its subnodes represent a dai with board specific configuration.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6asm-dais.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6asm-dais`, required properties `compatible`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: enum `qcom,q6asm-dais`
- `iommus`: maxItems 1
- `#sound-dai-cells`: const 1
- `#address-cells`: const 1
- `#size-cells`: const 0

Pattern properties define child node classes: `^dai@[0-9]+$`.

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 96 lines and 1909 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm-dais.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm.yaml` is a YAML Devicetree binding for Qualcomm Audio Stream Manager (Q6ASM). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Audio Stream Manager (Q6ASM).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6asm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6asm`, required properties `compatible`, `dais`, and referenced common schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6asm-dais.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6asm`
- `dais`: ref /schemas/sound/qcom,q6asm-dais.yaml#; Qualcomm DSP audio ports

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6asm-dais.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 68 lines and 1520 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6asm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6core.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6core.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6core.yaml` is a YAML Devicetree binding for Qualcomm Audio Core (Q6Core). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Audio Core (Q6Core).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6core.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6core`, required properties `compatible`, and referenced common schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6core`

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 39 lines and 818 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6core.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-clocks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-clocks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-clocks.yaml` is a YAML Devicetree binding for Qualcomm DSP LPASS Clock Controller. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This binding describes the Qualcomm DSP Clock Controller

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6dsp-lpass-clocks.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6afe-clocks`, `qcom,q6prm-lpass-clocks`, required properties `compatible`, `#clock-cells`, and referenced common schemas none declared.

Key properties include:
- `compatible`: enum `qcom,q6afe-clocks`, `qcom,q6prm-lpass-clocks`
- `#clock-cells`: const 2; Clock Id is followed by clock coupling attributes. 1 = for no coupled clock 2 = for dividend of the coupled clock 3 = for divisor of the coupled clock 4 = for inverted and no couple clock

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 41 lines and 944 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-clocks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-ports.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-ports.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-ports.yaml` is a YAML Devicetree binding for Qualcomm DSP LPASS(Low Power Audio SubSystem) Audio Ports. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This binding describes the Qualcomm DSP LPASS Audio ports

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6dsp-lpass-ports.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6afe-dais`, required properties `compatible`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: enum `qcom,q6afe-dais`
- `#sound-dai-cells`: const 1
- `#address-cells`: const 1
- `#size-cells`: const 0

Pattern properties define child node classes: `^dai@[0-9]+$`.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 167 lines and 4180 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6dsp-lpass-ports.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6prm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6prm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6prm.yaml` is a YAML Devicetree binding for Qualcomm Proxy Resource Manager (Q6PRM). It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Qualcomm Proxy Resource Manager (Q6PRM).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6prm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6prm`, required properties `compatible`, `clock-controller`, and referenced common schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-clocks.yaml#`.

Key properties include:
- `compatible`: enum `qcom,q6prm`
- `clock-controller`: ref /schemas/sound/qcom,q6dsp-lpass-clocks.yaml#; Qualcomm DSP LPASS clock controller

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/soc/qcom/qcom,apr-services.yaml#`, `/schemas/sound/qcom,q6dsp-lpass-clocks.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
depends on common clock framework phandles and assigned-clock policy.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 50 lines and 1149 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6prm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6usb.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6usb.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6usb.yaml` is a YAML Devicetree binding for Qualcomm ASoC DPCM USB backend DAI. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The USB port is a supported AFE path on the Q6 DSP. This ASoC DPCM backend DAI will communicate the required settings to initialize the XHCI host controller properly for enabling the offloaded audio stream. Parameters defined under this node will carry settings, which will be passed along during the QMI stream enabl...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,q6usb.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,q6usb`, required properties `compatible`, `#sound-dai-cells`, `qcom,usb-audio-intr-idx`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint16`.

Key properties include:
- `compatible`: enum `qcom,q6usb`
- `iommus`: maxItems 1
- `#sound-dai-cells`: const 1
- `qcom,usb-audio-intr-idx`: ref /schemas/types.yaml#/definitions/uint16; Desired XHCI interrupter number to use. Depending on the audio DSP on the platform, it will operate on a specific XHCI interrupter.

Maintainers listed by the binding are Wesley Cheng <quic_wcheng@quicinc.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint16`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 55 lines and 1386 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,q6usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,sm8250.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,sm8250.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,sm8250.yaml` is a YAML Devicetree binding for Qualcomm Technologies Inc. ASoC sound card drivers. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This bindings describes Qualcomm SoC based sound cards which uses LPASS internal codec for audio.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,sm8250.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `lenovo,yoga-c630-sndcard`, `qcom,db845c-sndcard`, `qcom,sdm845-sndcard`, `qcom,kaanapali-sndcard`, `qcom,sm8550-sndcard`, `qcom,sm8650-sndcard`, `qcom,sm8750-sndcard`, `qcom,sm8450-sndcard`, `fairphone,fp4-sndcard`, and 16 more, required properties `compatible`, `model`, and referenced common schemas `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

Key properties include:
- `compatible`
- `audio-routing`: ref /schemas/types.yaml#/definitions/non-unique-string-array; A list of the connections between audio components. Each entry is a pair of strings, the first being the connection's sink, the second being the connection's source. Valid names could be power supplies, MicBias of codec and the jacks on the board.
- `aux-devs`: ref /schemas/types.yaml#/definitions/phandle-array; List of phandles pointing to auxiliary devices, such as amplifiers, to be added to the sound card.
- `model`: ref /schemas/types.yaml#/definitions/string; User visible long sound card name

Pattern properties define child node classes: `.*-dai-link$`.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
describes board DAPM routing between jacks, pins, and codec widgets.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; routing arrays must use exact widget names and sink/source pairing.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; test invalid route widget names and odd-length route lists.
 Source read covered 217 lines and 5611 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,sm8250.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd9335.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd9335.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd9335.yaml` is a YAML Devicetree binding for Qualcomm WCD9335 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9335 Codec is a standalone Hi-Fi audio codec IC with in-built Soundwire controller and interrupt mux. It supports both I2S/I2C and SLIMbus audio interfaces.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd9335.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `slim217,1a0`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `dai-common.yaml#`.

Key properties include:
- `compatible`: const slim217,1a0
- `reg`: maxItems 1
- `clocks`: maxItems 2
- `clock-names`
- `interrupts`: maxItems 2
- `interrupt-names`
- interrupt-controller
- `#interrupt-cells`: const 1
- `reset-gpios`: maxItems 1
- `slim-ifc-dev`: ref /schemas/types.yaml#/definitions/phandle; SLIM IFC device interface
- `#sound-dai-cells`: const 1
- `vdd-buck-supply`: 1.8V buck supply
- `vdd-buck-sido-supply`: 1.8V SIDO buck supply
- `vdd-io-supply`: 1.8V I/O supply
- `...`: 4 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 156 lines and 3407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd9335.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd934x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd934x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd934x.yaml` is a YAML Devicetree binding for Qualcomm WCD9340/WCD9341 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9340/WCD9341 Codec is a standalone Hi-Fi audio codec IC. It has in-built Soundwire controller, pin controller, interrupt mux and supports both I2S/I2C and SLIMbus audio interfaces.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd934x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `slim217,250`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/gpio/qcom,wcd934x-gpio.yaml#`, `dai-common.yaml#`.

Key properties include:
- `compatible`: const slim217,250
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `reset-gpios`: maxItems 1; GPIO spec for reset line to use
- `slim-ifc-dev`: ref /schemas/types.yaml#/definitions/phandle; IFC device interface
- `clocks`: maxItems 1
- `clock-names`: const extclk
- `vdd-buck-supply`: A reference to the 1.8V buck supply
- `vdd-buck-sido-supply`: A reference to the 1.8V SIDO buck supply
- `vdd-rx-supply`: A reference to the 1.8V rx supply
- `vdd-tx-supply`: A reference to the 1.8V tx supply
- `vdd-vbat-supply`: A reference to the vbat supply
- `vdd-io-supply`: A reference to the 1.8V I/O supply
- `vdd-micbias-supply`: A reference to the micbias supply
- `...`: 18 additional schema properties omitted from this compact listing

Pattern properties define child node classes: `@[0-9a-f]+$`.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/gpio/qcom,wcd934x-gpio.yaml#`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 239 lines and 5772 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd934x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x-sdw.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x-sdw.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x-sdw.yaml` is a YAML Devicetree binding for Qualcomm SoundWire Slave devices on WCD9370/WCD9375. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9370/WCD9375 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire slave devices. This bindings is for the slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd937x-sdw.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw20217010a00`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

Key properties include:
- `compatible`: const sdw20217010a00
- `reg`: maxItems 1
- `qcom,tx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; minItems 4; Specifies static port mapping between device and host tx ports. In the order of the device port index which are adc1_port, adc23_port, dmic03_mbhc_port, dmic46_port. Supports maximum 4 tx soundwire ports. WCD9370 TX Port 1 (ADC1) <=> SWR2 Port 2 WCD9370 TX Port 2 (ADC2, 3) <=> SWR2 Port 2 WCD9370 TX Port 3 (DMIC0,1,...
- `qcom,rx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 5; minItems 5; Specifies static port mapping between device and host rx ports. In the order of device port index which are hph_port, clsh_port, comp_port, lo_port, dsd port. Supports maximum 5 rx soundwire ports. WCD9370 RX Port 1 (HPH_L/R) <==> SWR1 Port 1 (HPH_L/R) WCD9370 RX Port 2 (CLSH) <==> SWR1 Port 2 (CLSH) WCD9370 RX Port...
- `qcom,tx-channel-mapping`: ref /schemas/types.yaml#/definitions/uint8-array; maxItems 12; minItems 12; Specifies static channel mapping between slave and master tx port channels. In the order of slave port channels which is adc1, adc2, adc3, dmic0, dmic1, mbhc, dmic2, dmic3, dmci4, dmic5, dmic6, dmic7.
- `qcom,rx-channel-mapping`: ref /schemas/types.yaml#/definitions/uint8-array; maxItems 8; minItems 8; Specifies static channels mapping between slave and master rx port channels. In the order of slave port channels, which is hph_l, hph_r, clsh, comp_l, comp_r, lo, dsd_r, dsd_l.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`; integrates with SoundWire child-device topology.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 127 lines and 3789 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x-sdw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x.yaml` is a YAML Devicetree binding for Qualcomm WCD9370/WCD9375 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9370/WCD9375 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd937x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,wcd9370-codec`, `qcom,wcd9375-codec`, required properties `compatible`, `vdd-px-supply`, and referenced common schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`.

Key properties include:
- `compatible`
- `vdd-px-supply`: A reference to the 1.8V I/O supply

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 82 lines and 2148 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd937x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x-sdw.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x-sdw.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x-sdw.yaml` is a YAML Devicetree binding for Qualcomm SoundWire Slave devices on WCD9380/WCD9385. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9380/WCD9385 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire slave devices. This bindings is for the slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd938x-sdw.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw20217010d00`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const sdw20217010d00
- `reg`: maxItems 1
- `qcom,tx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; minItems 4; Specifies static port mapping between slave and master tx ports. In the order of slave port index.
- `qcom,rx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 5; minItems 5; Specifies static port mapping between slave and master rx ports. In the order of slave port index.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`; integrates with SoundWire child-device topology.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 70 lines and 1706 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x-sdw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x.yaml` is a YAML Devicetree binding for Qualcomm WCD9380/WCD9385 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9380/WCD9385 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire slave devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd938x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,wcd9380-codec`, `qcom,wcd9385-codec`, required properties `compatible`, and referenced common schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`.

Key properties include:
- `compatible`: enum `qcom,wcd9380-codec`, `qcom,wcd9385-codec`
- `mux-controls`: maxItems 1; A reference to the audio mux switch for switching CTIA/OMTP Headset types
- `us-euro-gpios`: maxItems 1; GPIO spec for swapping gnd and mic segments

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 84 lines and 2201 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd938x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x-sdw.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x-sdw.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x-sdw.yaml` is a YAML Devicetree binding for Qualcomm SoundWire devices on WCD9390/WCD9395. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9390/WCD9395 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire devices. This bindings is for the devices.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd939x-sdw.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw20217010e00`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const sdw20217010e00
- `reg`: maxItems 1
- `qcom,tx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; minItems 4; Specifies static port mapping between device and host tx ports. In the order of the device port index.
- `qcom,rx-port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 6; minItems 6; Specifies static port mapping between device and host rx ports. In the order of device port index.

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`; integrates with SoundWire child-device topology.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 69 lines and 1692 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x-sdw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x.yaml` is a YAML Devicetree binding for Qualcomm WCD9380/WCD9385 Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Qualcomm WCD9390/WCD9395 Codec is a standalone Hi-Fi audio codec IC. It has RX and TX Soundwire devices. The WCD9390/WCD9395 IC has a functionally separate USB-C Mux subsystem accessible over an I2C interface. The Audio Headphone and Microphone data path between the Codec and the USB-C Mux subsystems are external to...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd939x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `qcom,wcd9390-codec`, `qcom,wcd9395-codec`, required properties `compatible`, and referenced common schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`, `/schemas/graph.yaml#/properties/port`.

Key properties include:
- `compatible`
- `mode-switch`: Flag the port as possible handler of altmode switching
- `orientation-switch`: Flag the port as possible handler of orientation switching
- `port`: ref /schemas/graph.yaml#/properties/port; A port node to link the WCD939x Codec node to USB MUX subsystems for the purpose of handling altmode muxing and orientation switching to detect and enable Audio Accessory Mode.
- `vdd-px-supply`: A reference to the 1.2V PX supply

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `qcom,wcd93xx-common.yaml#`, `/schemas/graph.yaml#/properties/port`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 99 lines and 2938 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd939x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd93xx-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd93xx-common.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd93xx-common.yaml` is a YAML Devicetree binding for Common properties for Qualcomm WCD93xx Audio Codec. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Common properties for Qualcomm WCD93xx Audio Codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wcd93xx-common.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints none declared, required properties `reset-gpios`, `qcom,tx-device`, `qcom,rx-device`, `qcom,micbias1-microvolt`, `qcom,micbias2-microvolt`, `qcom,micbias3-microvolt`, `qcom,micbias4-microvolt`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle-array`.

Key properties include:
- `reset-gpios`: maxItems 1; GPIO spec for reset line to use
- `vdd-buck-supply`: A reference to the 1.8V buck supply
- `vdd-rxtx-supply`: A reference to the 1.8V rx supply
- `vdd-io-supply`: A reference to the 1.8V I/O supply
- `vdd-mic-bias-supply`: A reference to the 3.8V mic bias supply
- `qcom,tx-device`: ref /schemas/types.yaml#/definitions/phandle-array; A reference to Soundwire tx device phandle
- `qcom,rx-device`: ref /schemas/types.yaml#/definitions/phandle-array; A reference to Soundwire rx device phandle
- `qcom,micbias1-microvolt`: micbias1 voltage
- `qcom,micbias2-microvolt`: micbias2 voltage
- `qcom,micbias3-microvolt`: micbias3 voltage
- `qcom,micbias4-microvolt`: micbias4 voltage
- `qcom,hphl-jack-type-normally-closed`: Indicates that HPHL jack switch type is normally closed
- `qcom,ground-jack-type-normally-closed`: Indicates that Headset Ground switch type is normally closed
- `qcom,mbhc-headset-vthreshold-microvolt`: Voltage threshold value for headset detection
- `...`: 3 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: true`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
main risk is drift between schema constraints and the consuming ASoC driver.

### Test Signals
run `make dt_binding_check` for this schema.
 Source read covered 95 lines and 2404 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wcd93xx-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa881x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa881x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa881x.yaml` is a YAML Devicetree binding for Qualcomm WSA8810/WSA8815 Class-D Smart Speaker Amplifier. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. WSA8810 is a class-D smart speaker amplifier and WSA8815 is a high-output power class-D smart speaker amplifier. Their primary operating mode uses a SoundWire digital audio interface. This binding is for SoundWire interface.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wsa881x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw10217201000`, required properties `compatible`, `reg`, `powerdown-gpios`, `#thermal-sensor-cells`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const sdw10217201000
- `reg`: maxItems 1
- `powerdown-gpios`: maxItems 1; GPIO spec for Powerdown/Shutdown line to use
- `#thermal-sensor-cells`: const 0
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

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
 Source read covered 71 lines and 1595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa881x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa883x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa883x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa883x.yaml` is a YAML Devicetree binding for Qualcomm WSA8830/WSA8832/WSA8835 smart speaker amplifier. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. WSA883X is the Qualcomm Aqstic smart speaker amplifier Their primary operating mode uses a SoundWire digital audio interface. This binding is for SoundWire interface.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wsa883x.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw10217020200`, required properties `compatible`, `reg`, `vdd-supply`, `#thermal-sensor-cells`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const sdw10217020200
- `reg`: maxItems 1
- `powerdown-gpios`: maxItems 1; GPIO spec for Powerdown/Shutdown line to use (pin SD_N)
- `reset-gpios`: maxItems 1; Powerdown/Shutdown line to use (pin SD_N)
- `vdd-supply`: VDD Supply for the Codec
- `qcom,port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; minItems 4; Specifies static port mapping between slave and master ports. In the order of slave port index.
- `#thermal-sensor-cells`: const 0
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, `oneOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 98 lines and 2239 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa883x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa8840.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa8840.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa8840.yaml` is a YAML Devicetree binding for Qualcomm WSA8840/WSA8845/WSA8845H smart speaker amplifier. It falls in the qualcomm asoc/lpass binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. WSA884X is a family of Qualcomm Aqstic smart speaker amplifiers using SoundWire digital audio interface.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/qcom,wsa8840.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `sdw20217020400`, required properties `compatible`, `reg`, `#sound-dai-cells`, `vdd-1p8-supply`, `vdd-io-supply`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const sdw20217020400
- `reg`: maxItems 1
- `powerdown-gpios`: maxItems 1; Powerdown/Shutdown line to use (pin SD_N)
- `reset-gpios`: maxItems 1; Powerdown/Shutdown line to use (pin SD_N)
- `qcom,port-mapping`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 6; minItems 6; Specifies static port mapping between slave and master ports. In the order of slave port index.
- `#sound-dai-cells`: const 0
- vdd-1p8-supply
- vdd-io-supply

Maintainers listed by the binding are Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, `oneOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 83 lines and 1872 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/qcom,wsa8840.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc203.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc203.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc203.yaml` is a YAML Devicetree binding for Realtek ALC203 AC97 Audio Codec. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. ALC203 is a full duplex AC97 2.3 compatible stereo audio codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,alc203.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,alc203`, required properties `compatible`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const realtek,alc203
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Keguang Zhang <keguang.zhang@gmail.com>.

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
 Source read covered 36 lines and 683 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc203.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5623.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5623.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5623.yaml` is a YAML Devicetree binding for ALC5621/ALC5623 Audio Codec. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: ALC5621/ALC5623 Audio Codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,alc5623.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,alc5621`, `realtek,alc5623`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: enum `realtek,alc5621`, `realtek,alc5623`
- `reg`: maxItems 1
- `add-ctrl`: ref /schemas/types.yaml#/definitions/uint32; Default register value for Reg-40h, Additional Control Register. If absent or zero, the register is left untouched.
- `jack-det-ctrl`: ref /schemas/types.yaml#/definitions/uint32; Default register value for Reg-5Ah, Jack Detect Control Register. If absent or zero, the register is left untouched.

Maintainers listed by the binding are Mahdi Khosravi <mmk1776@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 54 lines and 1172 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5623.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5632.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5632.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5632.yaml` is a YAML Devicetree binding for ALC5632 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Pins on the device (for linking into audio routes): * SPK_OUTP * SPK_OUTN * HP_OUT_L * HP_OUT_R * AUX_OUT_P * AUX_OUT_N * LINE_IN_L * LINE_IN_R * PHONE_P * PHONE_N * MIC1_P * MIC1_N * MIC2_P * MIC2_N * MICBIAS1 * DMICDAT

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,alc5632.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,alc5632`, required properties `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, and referenced common schemas none declared.

Key properties include:
- `compatible`: const realtek,alc5632
- `reg`: maxItems 1
- `#gpio-cells`: const 2
- gpio-controller

Maintainers listed by the binding are Leon Romanovsky <leon@leon.nu>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 63 lines and 1125 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,alc5632.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015.yaml` is a YAML Devicetree binding for RT1015 Mono Class D Audio Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: RT1015 Mono Class D Audio Amplifier.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt1015.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt1015`, required properties `compatible`, `reg`, and referenced common schemas none declared.

Key properties include:
- `compatible`: enum `realtek,rt1015`
- `reg`: maxItems 1
- `realtek,power-up-delay-ms`: maxItems 1; Set a delay time for flush work to be completed, this vlaue is adjustable depending on platform.

Maintainers listed by the binding are Jack Yu <jack.yu@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 41 lines and 830 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015p.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015p.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015p.yaml` is a YAML Devicetree binding for Realtek rt1015p codec. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Rt1015p is a rt1015 variant which does not support I2C and only supports S24, 48kHz, 64FS.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt1015p.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt1015p`, `realtek,rt1019p`, required properties `compatible`, and referenced common schemas none declared.

Key properties include:
- `compatible`: enum `realtek,rt1015p`, `realtek,rt1019p`
- `sdb-gpios`: maxItems 1; GPIO used for shutdown control. 0 means shut down; 1 means power on.
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Tzung-Bi Shih <tzungbi@kernel.org>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 43 lines and 841 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1015p.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1016.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1016.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1016.yaml` is a YAML Devicetree binding for Reaktek RT1016 Stereo Class D Audio Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Reaktek RT1016 Stereo Class D Audio Amplifier.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt1016.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt1016`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: const realtek,rt1016
- `reg`: maxItems 1
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are oder_chiou@realtek.com.

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
 Source read covered 40 lines and 681 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1016.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1019.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1019.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1019.yaml` is a YAML Devicetree binding for RT1019 Mono Class-D Audio Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: RT1019 Mono Class-D Audio Amplifier.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt1019.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt1019`, required properties `compatible`, `reg`, and referenced common schemas none declared.

Key properties include:
- `compatible`: const realtek,rt1019
- `reg`: maxItems 1; I2C address of the device.

Maintainers listed by the binding are jack.yu@realtek.com.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas none declared, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 35 lines and 653 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt1019.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5514.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5514.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5514.yaml` is a YAML Devicetree binding for RT5514 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports both I2C and SPI. Pins on the device (for linking into audio routes) for I2C: * DMIC1L * DMIC1R * DMIC2L * DMIC2R * AMICL * AMICR

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5514.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5514`, required properties `compatible`, `reg`, and referenced common schemas `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`.

Key properties include:
- `compatible`: const realtek,rt5514
- `reg`: maxItems 1
- `clocks`
- `clock-names`
- `interrupts`: maxItems 1; The interrupt number to the cpu.
- `realtek,dmic-init-delay-ms`: Set the DMIC initial delay (ms) to wait it ready for I2C.
- spi-max-frequency
- `wakeup-source`: Flag to indicate this device can wake system (suspend/resume).

Maintainers listed by the binding are Animesh Agarwal <animeshagarwal28@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 70 lines and 1335 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5514.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5575.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5575.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5575.yaml` is a YAML Devicetree binding for ALC5575 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The device supports both I2C and SPI. I2C is mandatory, while SPI is optional depending on the hardware configuration. SPI is used for firmware loading if present.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5575.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5575`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`.

Key properties include:
- `compatible`: const realtek,rt5575
- `reg`: maxItems 1
- `spi-parent`: ref /schemas/types.yaml#/definitions/phandle-array; Optional phandle reference to the SPI controller used for firmware loading. The argument specifies the chip select.

Maintainers listed by the binding are Oder Chiou <oder_chiou@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 61 lines and 1318 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5575.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5616.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5616.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5616.yaml` is a YAML Devicetree binding for Realtek rt5616 ALSA SoC audio codec driver. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Pins on the device (for linking into audio routes) for RT5616: * IN1P * IN2P * IN2N * LOUTL * LOUTR * HPOL * HPOR

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5616.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5616`, required properties `compatible`, `reg`, and referenced common schemas `dai-common.yaml#`, `audio-graph-port.yaml#`.

Key properties include:
- `compatible`: const realtek,rt5616
- `reg`: maxItems 1
- `clocks`
- `clock-names`
- `port`: ref audio-graph-port.yaml#

Maintainers listed by the binding are Bard Liao <bardliao@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 61 lines and 1025 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5616.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5631.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5631.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5631.yaml` is a YAML Devicetree binding for ALC5631/RT5631 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes): * SPK_OUT_R_P * SPK_OUT_R_N * SPK_OUT_L_P * SPK_OUT_L_N * HP_OUT_L * HP_OUT_R * AUX_OUT2_LP * AUX_OUT2_RN * AUX_OUT1_LP * AUX_OUT1_RN * AUX_IN_L_JD * AUX_IN_R_JD * MONO_IN_P * MONO_IN_N * MIC1_P * MIC1_N * MIC2_P * MIC2_N * MONO_OUT_P...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5631.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,alc5631`, `realtek,rt5631`, required properties `compatible`, `reg`, and referenced common schemas `audio-graph-port.yaml#`.

Key properties include:
- `compatible`: enum `realtek,alc5631`, `realtek,rt5631`
- `reg`: maxItems 1
- `port`: ref audio-graph-port.yaml#

Maintainers listed by the binding are Animesh Agarwal <animeshagarwal28@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 67 lines and 1228 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5631.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5659.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5659.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5659.yaml` is a YAML Devicetree binding for RT5659/RT5658 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes) for RT5659/RT5658: * DMIC L1 * DMIC R1 * DMIC L2 * DMIC R2 * IN1P * IN1N * IN2P * IN2N * IN3P * IN3N * IN4P * IN4N * HPOL * HPOR * SPOL * SPOR * LOUTL * LOUTR * MONOOUT * PDML * PDMR * SPDIF

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5659.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5659`, `realtek,rt5658`, required properties `compatible`, `reg`, `interrupts`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`.

Key properties include:
- `compatible`: enum `realtek,rt5659`, `realtek,rt5658`
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`: maxItems 1
- `clock-names`: const mclk
- `realtek,dmic1-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`, `4`; Specify which pin to be used as DMIC1 data pin.
- `realtek,dmic2-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`, `4`; Specify which pin to be used as DMIC2 data pin.
- `realtek,jd-src`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which JD source be used.
- `realtek,ldo1-en-gpios`: maxItems 1; CODEC's LDO1_EN pin.
- `realtek,reset-gpios`: maxItems 1; CODEC's RESET pin.
- `ports`: ref /schemas/graph.yaml#/properties/ports
- `port`: ref audio-graph-port.yaml#

Maintainers listed by the binding are Animesh Agarwal <animeshagarwal28@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; graph endpoint numbering and remote-endpoint links must remain consistent; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; exercise graph endpoint validation for missing or mismatched remote endpoints; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 129 lines and 2718 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5659.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5677.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5677.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5677.yaml` is a YAML Devicetree binding for RT5677 audio CODEC. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This device supports I2C only. Pins on the device (for linking into audio routes): * IN1P * IN1N * IN2P * IN2N * MICBIAS1 * DMIC1 * DMIC2 * DMIC3 * DMIC4 * LOUT1 * LOUT2 * LOUT3

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5677.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5677`, required properties `compatible`, `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: const realtek,rt5677
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- gpio-controller
- `#gpio-cells`: const 2
- `realtek,pow-ldo2-gpio`: maxItems 1; CODEC's POW_LDO2 pin.
- `realtek,reset-gpio`: maxItems 1; CODEC's RESET pin. Active low.
- `realtek,gpio-config`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 6; minItems 6; Array of six 8bit elements that configures GPIO. 0 - floating (reset value) 1 - pull down 2 - pull up
- `realtek,jd1-gpio`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; Configures GPIO Mic Jack detection 1.
- `realtek,jd2-gpio`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; Configures GPIO Mic Jack detection 2.
- `realtek,jd3-gpio`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; Configures GPIO Mic Jack detection 3.

Pattern properties define child node classes: `^realtek,in[1-2]-differential$`, `^realtek,lout[1-3]-differential$`.

Maintainers listed by the binding are Animesh Agarwal <animeshagarwal28@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 135 lines and 2954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5677.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682.yaml` is a YAML Devicetree binding for Realtek rt5682 and rt5682i codecs. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Realtek rt5682 and rt5682i codecs.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5682.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5682`, `realtek,rt5682i`, required properties `compatible`, `reg`, `AVDD-supply`, `VBAT-supply`, `MICVDD-supply`, `DBVDD-supply`, `LDO1-IN-supply`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: enum `realtek,rt5682`, `realtek,rt5682i`
- `reg`: maxItems 1; I2C address of the device.
- `interrupts`: maxItems 1; The CODEC's interrupt output.
- `realtek,dmic1-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which GPIO pin be used as DMIC1 data pin.
- `realtek,dmic1-clk-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Specify which GPIO pin be used as DMIC1 clk pin.
- `realtek,jd-src`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Specify which JD source be used.
- `realtek,ldo1-en-gpios`: The GPIO that controls the CODEC's LDO1_EN pin.
- `realtek,btndet-delay`: ref /schemas/types.yaml#/definitions/uint32; The debounce delay for push button. The delay time is realtek,btndet-delay value multiple of 8.192 ms. If absent, the default is 16.
- `realtek,dmic-clk-rate-hz`: Set the clock rate (hz) for the requirement of the particular DMIC.
- `realtek,dmic-delay-ms`: Set the delay time (ms) for the requirement of the particular DMIC.
- `realtek,dmic-clk-driving-high`: Set the high driving of the DMIC clock out.
- `clocks`
- `clock-names`
- `#clock-cells`: const 1
- `...`: 7 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Bard Liao <bardliao@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 156 lines and 3871 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682s.yaml` is a YAML Devicetree binding for Realtek rt5682s codec. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Rt5682s(ALC5682I-VS) is a rt5682i variant which supports I2C only.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/realtek,rt5682s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `realtek,rt5682s`, required properties `compatible`, `reg`, `AVDD-supply`, `MICVDD-supply`, `DBVDD-supply`, `LDO1-IN-supply`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

Key properties include:
- `compatible`: const realtek,rt5682s
- `reg`: maxItems 1; I2C address of the device.
- `interrupts`: maxItems 1; The CODEC's interrupt output.
- `realtek,dmic1-data-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which GPIO pin be used as DMIC1 data pin.
- `realtek,dmic1-clk-pin`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; Specify which GPIO pin be used as DMIC1 clk pin.
- `realtek,jd-src`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Specify which JD source be used.
- `realtek,ldo1-en-gpios`: The GPIO that controls the CODEC's LDO1_EN pin.
- `realtek,dmic-clk-rate-hz`: Set the clock rate (hz) for the requirement of the particular DMIC.
- `realtek,dmic-delay-ms`: Set the delay time (ms) for the requirement of the particular DMIC.
- `realtek,amic-delay-ms`: Set the delay time (ms) for the requirement of the particular platform or AMIC.
- `realtek,dmic-clk-driving-high`: Set the high driving of the DMIC clock out.
- `clocks`
- `clock-names`
- `#clock-cells`: const 1
- `...`: 6 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Derek Fang <derek.fang@realtek.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 150 lines and 3711 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/realtek,rt5682s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,fsi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,fsi.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,fsi.yaml` is a YAML Devicetree binding for Renesas FIFO-buffered Serial Interface (FSI). It falls in the renesas audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Renesas FIFO-buffered Serial Interface (FSI).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/renesas,fsi.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `renesas,fsi2-sh73a0`, `renesas,fsi2-r8a7740`, `renesas,sh_fsi2`, `renesas,sh_fsi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`.

Key properties include:
- `$nodename`: pattern `^sound@.*`
- `compatible`
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`: maxItems 1
- `power-domains`: maxItems 1
- `#sound-dai-cells`: const 1

Pattern properties define child node classes: `^fsi(a|b),spdif-connection$`, `^fsi(a|b),stream-mode-support$`, `^fsi(a|b),use-internal-clock$`.

Maintainers listed by the binding are Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 87 lines and 1974 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,fsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,idt821034.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,idt821034.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,idt821034.yaml` is a YAML Devicetree binding for Renesas IDT821034 codec device. It falls in the renesas audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The IDT821034 codec is a four channel PCM codec with onchip filters and programmable gain setting. The time-slots used by the codec must be set and so, the properties 'dai-tdm-slot-num', 'dai-tdm-slot-width', 'dai-tdm-slot-tx-mask' and 'dai-tdm-slot-rx-mask' must be present in the ALSA sound card node for sub-nodes...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/renesas,idt821034.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `renesas,idt821034`, required properties `compatible`, `reg`, `spi-cpha`, `#sound-dai-cells`, `gpio-controller`, `#gpio-cells`, and referenced common schemas `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`.

Key properties include:
- `compatible`: const renesas,idt821034
- `reg`: maxItems 1; SPI device address.
- `spi-max-frequency`
- spi-cpha
- `#sound-dai-cells`: const 0
- `#gpio-cells`: const 2
- gpio-controller

Maintainers listed by the binding are Herve Codina <herve.codina@bootlin.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 75 lines and 1680 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,idt821034.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rsnd.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rsnd.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rsnd.yaml` is a YAML Devicetree binding for Renesas R-Car Sound Driver. It falls in the renesas audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Renesas R-Car Sound Driver.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/renesas,rsnd.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `renesas,rcar_sound-r8a7778`, `renesas,rcar_sound-r8a7779`, `renesas,rcar_sound-gen1`, `renesas,rcar_sound-r8a7742`, `renesas,rcar_sound-r8a7743`, `renesas,rcar_sound-r8a7744`, `renesas,rcar_sound-r8a7745`, `renesas,rcar_sound-r8a77470`, `renesas,rcar_sound-r8a7790`, and 18 more, required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, and referenced common schemas `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#/definitions/port-base`, `audio-graph-port.yaml#/definitions/endpoint-base`, `/schemas/types.yaml#/definitions/phandle-array`, `#/properties/port`, `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 5; minItems 1
- `reg-names`: maxItems 5; minItems 1
- `#sound-dai-cells`: enum `0`, `1`; it must be 0 if your system is using single DAI it must be 1 if your system is using multi DAIs This is used on simple-audio-card
- `#clock-cells`: enum `0`, `1`; it must be 0 if your system has audio_clkout it must be 1 if your system has audio_clkout0/1/2/3
- `#address-cells`: const 1
- `#size-cells`: const 0
- `clock-frequency`: for audio_clkout0/1/2/3
- `clkout-lr-asynchronous`: ref /schemas/types.yaml#/definitions/flag; audio_clkoutn is asynchronizes with lr-clock.
- power-domains
- `resets`: maxItems 11; minItems 1
- `reset-names`: maxItems 11; minItems 1
- `clocks`: maxItems 31; minItems 1; References to SSI/SRC/MIX/CTU/DVC/AUDIO_CLK clocks.
- `clock-names`: List of necessary clock names.
- `...`: 7 additional schema properties omitted from this compact listing

Pattern properties define child node classes: `rcar_sound,dai(@[0-9a-f]+)?$`, `ports(@[0-9a-f]+)?$`.

Maintainers listed by the binding are Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#/definitions/port-base`, `audio-graph-port.yaml#/definitions/endpoint-base`, `/schemas/types.yaml#/definitions/phandle-array`, `#/properties/port`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 541 lines and 14902 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rsnd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rz-ssi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rz-ssi.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rz-ssi.yaml` is a YAML Devicetree binding for Renesas RZ/{G2L,V2L} ASoC Sound Serial Interface (SSIF-2). It falls in the renesas audio controller/codec binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Renesas RZ/{G2L,V2L} ASoC Sound Serial Interface (SSIF-2).

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/renesas,rz-ssi.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `renesas,r9a07g043-ssi`, `renesas,r9a07g044-ssi`, `renesas,r9a07g054-ssi`, `renesas,r9a08g045-ssi`, `renesas,r9a08g046-ssi`, `renesas,rz-ssi`, required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `audio-graph-port.yaml#/definitions/port-base`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `interrupts`: maxItems 3; minItems 2
- `interrupt-names`
- `clocks`: maxItems 4
- `clock-names`
- `power-domains`: maxItems 1
- `resets`: maxItems 1
- `dmas`: maxItems 2; minItems 1
- `dma-names`
- `#sound-dai-cells`: const 0
- `port`: ref audio-graph-port.yaml#/definitions/port-base; Connection to controller providing I2S signals

Maintainers listed by the binding are Biju Das <biju.das.jz@bp.renesas.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `audio-graph-port.yaml#/definitions/port-base`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 114 lines and 2644 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/renesas,rz-ssi.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123.yaml` is a YAML Devicetree binding for Richtek RT9123/RTQ9124 Audio Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. RT9123 is a 3.2W mono Class-D audio amplifier that features high efficiency and performance with ultra-low quiescent current. The digital audio interface support various formats, including I2S, left-justified, right-justified, and TDM formats. RTQ9124 is an ultra-low output noise, digital input, mono-channel Class-D...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/richtek,rt9123.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `richtek,rt9123`, `richtek,rtq9124`, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `richtek,rt9123`, `richtek,rtq9124`
- `reg`: maxItems 1
- `#sound-dai-cells`: const 0
- `enable-gpios`: maxItems 1

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
 Source read covered 63 lines and 1513 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123p.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123p.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123p.yaml` is a YAML Devicetree binding for Richtek RT9123P Audio Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. RT9123P is a RT9123 variant which does not support I2C control.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/richtek,rt9123p.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `richtek,rt9123p`, required properties `compatible`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`: enum `richtek,rt9123p`
- `#sound-dai-cells`: const 0
- `enable-gpios`: maxItems 1
- `enable-delay-ms`: Delay time for 'ENABLE' pin changes intended to make I2S clocks ready to prevent speaker pop noise. The unit is in millisecond.

Maintainers listed by the binding are ChiYuan Huang <cy_huang@richtek.com>.

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
 Source read covered 48 lines and 988 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rt9123p.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rtq9128.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rtq9128.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rtq9128.yaml` is a YAML Devicetree binding for Richtek RTQ9128 Automative Audio Power Amplifier. It falls in the realtek codec or amplifier binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The RTQ9128 is a ultra-low output noise, high-efficiency, four-channel class-D audio power amplifier and delivering 4x75W into 4OHm at 10% THD+N from a 25V supply in automotive applications. The RTQ9154 is the family series of RTQ9128. The major change is to modify the package size. Beside this, whole functions are...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/richtek,rtq9128.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `richtek,rtq9128`, `richtek,rtq9154`, required properties `compatible`, `reg`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `enable-gpios`: maxItems 1
- `richtek,tdm-input-data2-select`: By default, if TDM mode is used, TDM data input will select 'DATA1' pin as the data source. This option will configure TDM data input source from 'DATA1' to 'DATA2' pin.
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
 Source read covered 69 lines and 1614 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/richtek,rtq9128.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,i2s-tdm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,i2s-tdm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,i2s-tdm.yaml` is a YAML Devicetree binding for Rockchip I2S/TDM Controller. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Rockchip I2S/TDM Controller is a Time Division Multiplexed audio interface found in various Rockchip SoCs, allowing up to 8 channels of audio over a serial interface.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,i2s-tdm.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,px30-i2s-tdm`, `rockchip,rk1808-i2s-tdm`, `rockchip,rk3308-i2s-tdm`, `rockchip,rk3568-i2s-tdm`, `rockchip,rk3588-i2s-tdm`, `rockchip,rv1126-i2s-tdm`, required properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`, `resets`, `reset-names`, and 1 more, and referenced common schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: enum `rockchip,px30-i2s-tdm`, `rockchip,rk1808-i2s-tdm`, `rockchip,rk3308-i2s-tdm`, `rockchip,rk3568-i2s-tdm`, `rockchip,rk3588-i2s-tdm`, and 1 more
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `dmas`: maxItems 2; minItems 1
- `dma-names`: maxItems 2; minItems 1
- `clocks`: minItems 3
- `clock-names`: minItems 3
- `resets`: maxItems 2; minItems 1; resets for the tx and rx directions
- `reset-names`: maxItems 2; minItems 1
- `port`: ref audio-graph-port.yaml#
- `power-domains`: maxItems 1
- `rockchip,grf`: ref /schemas/types.yaml#/definitions/phandle; The phandle of the syscon node for the GRF register.
- `rockchip,trcm-sync-tx-only`: Use TX BCLK/LRCK for both TX and RX.
- `rockchip,trcm-sync-rx-only`: Use RX BCLK/LRCK for both TX and RX.
- `...`: 4 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Nicolas Frattaroli <frattaroli.nicolas@gmail.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 191 lines and 4927 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,i2s-tdm.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3036-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3036-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3036-codec.yaml` is a YAML Devicetree binding for Rockchip RK3036 internal codec. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Rockchip RK3036 internal codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rk3036-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3036-codec`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `rockchip,grf`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`.

Key properties include:
- `compatible`: const rockchip,rk3036-codec
- `reg`: maxItems 1
- `clocks`
- `clock-names`
- `rockchip,grf`: ref /schemas/types.yaml#/definitions/phandle; The phandle of the syscon node for the GRF register.
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 58 lines and 1146 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3036-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3308-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3308-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3308-codec.yaml` is a YAML Devicetree binding for Rockchip RK3308 Internal Codec. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. This is the audio codec embedded in the Rockchip RK3308 SoC. It has 8 24-bit ADCs and 2 24-bit DACs. The maximum supported sampling rate is 192 kHz. It is connected internally to one out of a selection of the internal I2S controllers. The RK3308 audio codec has 8 independent capture channels, but some features work...

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rk3308-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3308-codec`, required properties `compatible`, `reg`, `rockchip,grf`, `clocks`, `resets`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `audio-graph-port.yaml#`.

Key properties include:
- `compatible`: const rockchip,rk3308-codec
- `reg`: maxItems 1
- `rockchip,grf`: ref /schemas/types.yaml#/definitions/phandle; Phandle to the General Register Files (GRF)
- `clocks`
- `clock-names`
- `port`: ref audio-graph-port.yaml#
- `resets`: maxItems 1
- `reset-names`
- `#sound-dai-cells`: const 0
- `rockchip,micbias-avdd-percent`: enum `50`, `55`, `60`, `65`, `70`, and 3 more; Voltage setting for the MICBIAS pins expressed as a percentage of AVDD. E.g. if rockchip,micbias-avdd-percent = 85 and AVDD = 3v3, then the MIC BIAS voltage will be 3.3 V * 85% = 2.805 V.

Maintainers listed by the binding are Luca Ceresoli <luca.ceresoli@bootlin.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle`, `audio-graph-port.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 102 lines and 2371 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3308-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3328-codec.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3328-codec.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3328-codec.yaml` is a YAML Devicetree binding for Rockchip rk3328 internal codec. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Rockchip rk3328 internal codec.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rk3328-codec.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3328-codec`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `rockchip,grf`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`.

Key properties include:
- `compatible`: const rockchip,rk3328-codec
- `reg`: maxItems 1
- `clocks`
- `clock-names`
- `rockchip,grf`: ref /schemas/types.yaml#/definitions/phandle; The phandle of the syscon node for the GRF register.
- `spk-depop-time-ms`: Speaker depop time in msec.
- `mute-gpios`: maxItems 1; GPIO specifier for external line driver control (typically the dedicated GPIO_MUTE pin)
- `#sound-dai-cells`: const 0

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch.
 Source read covered 74 lines and 1582 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3328-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3399-gru-sound.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3399-gru-sound.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3399-gru-sound.yaml` is a YAML Devicetree binding for Rockchip with MAX98357A/RT5514/DA7219 codecs on GRU boards. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. Schema title: Rockchip with MAX98357A/RT5514/DA7219 codecs on GRU boards.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rk3399-gru-sound.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3399-gru-sound`, required properties `compatible`, `rockchip,cpu`, `rockchip,codec`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle-array`.

Key properties include:
- `compatible`: const rockchip,rk3399-gru-sound
- `rockchip,cpu`: ref /schemas/types.yaml#/definitions/phandle-array; minItems 1; List of phandles to the Rockchip CPU DAI controllers connected to codecs
- `rockchip,codec`: ref /schemas/types.yaml#/definitions/phandle-array; maxItems 6; minItems 1; The phandles of the audio codecs connected to the Rockchip CPU DAI controllers
- `dmic-wakeup-delay-ms`: specify delay time (ms) for DMIC ready. If this option is specified, a delay is required for DMIC to get ready so that rt5514 can avoid recording before DMIC sends valid data

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `additionalProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
is selected by compatible strings in board DTS files.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node.
 Source read covered 60 lines and 1638 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3399-gru-sound.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3576-sai.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3576-sai.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3576-sai.yaml` is a YAML Devicetree binding for Rockchip Serial Audio Interface Controller. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The Rockchip Serial Audio Interface (SAI) controller is a flexible audio controller that implements the I2S, I2S/TDM and the PDM standards.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip,rk3576-sai.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3576-sai`, required properties `compatible`, `reg`, `dmas`, `dma-names`, `clocks`, `clock-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

Key properties include:
- `compatible`: const rockchip,rk3576-sai
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `dmas`: maxItems 2; minItems 1
- `dma-names`: minItems 1
- `clocks`
- `clock-names`
- `resets`: minItems 1
- `reset-names`: minItems 1
- `port`: ref audio-graph-port.yaml#
- `power-domains`: maxItems 1
- `#sound-dai-cells`: const 0
- `rockchip,sai-rx-route`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; Defines the mapping of the controller's SDI ports to actual input lanes, as well as the number of input lanes. rockchip,sai-rx-route = <3> would mean sdi3 is receiving from data0, and that there is only one receiving lane. This property's absence is to be understood as only one receiving lane being used if the contr...
- `rockchip,sai-tx-route`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 4; Defines the mapping of the controller's SDO ports to actual output lanes, as well as the number of output lanes. rockchip,sai-tx-route = <3> would mean sdo3 is sending to data0, and that there is only one transmitting lane. This property's absence is to be understood as only one transmitting lane being used if the c...

Maintainers listed by the binding are Nicolas Frattaroli <nicolas.frattaroli@collabora.com>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 144 lines and 3861 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip,rk3576-sai.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-i2s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-i2s.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-i2s.yaml` is a YAML Devicetree binding for Rockchip I2S controller. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The I2S bus (Inter-IC sound bus) is a serial link for digital audio data transfer between devices in the system.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip-i2s.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3066-i2s`, `rockchip,px30-i2s`, `rockchip,rk1808-i2s`, `rockchip,rk3036-i2s`, `rockchip,rk3128-i2s`, `rockchip,rk3188-i2s`, `rockchip,rk3228-i2s`, `rockchip,rk3288-i2s`, `rockchip,rk3308-i2s`, and 6 more, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `#sound-dai-cells`, and referenced common schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`
- `clock-names`
- `dmas`: maxItems 2; minItems 1
- `dma-names`
- `pinctrl-names`
- `power-domains`: maxItems 1
- `reset-names`
- `resets`: maxItems 2
- `port`: ref audio-graph-port.yaml#
- `rockchip,capture-channels`: ref /schemas/types.yaml#/definitions/uint32; Max capture channels, if not set, 2 channels default.
- `rockchip,playback-channels`: ref /schemas/types.yaml#/definitions/uint32; Max playback channels, if not set, 8 channels default.
- `...`: 2 additional schema properties omitted from this compact listing

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `dai-common.yaml#`, `audio-graph-port.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; depends on reset-controller bindings; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 140 lines and 3163 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-spdif.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-spdif.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-spdif.yaml` is a YAML Devicetree binding for Rockchip SPDIF transceiver. It falls in the rockchip audio controller/card binding area and defines how DTS authors describe this sound hardware or sound-card topology to Linux ASoC/OF probing. The S/PDIF audio block is a stereo transceiver that allows the processor to receive and transmit digital audio via a coaxial or fibre cable.

### Important APIs, Types, And Functions
This file has no runtime functions; its API surface is the dt-schema contract consumed by `dt_binding_check`, DTS validation, and the matching kernel drivers. Important schema entries are `$id` `http://devicetree.org/schemas/sound/rockchip-spdif.yaml#`, `$schema` `http://devicetree.org/meta-schemas/core.yaml#`, compatible constraints `rockchip,rk3066-spdif`, `rockchip,rk3228-spdif`, `rockchip,rk3328-spdif`, `rockchip,rk3366-spdif`, `rockchip,rk3368-spdif`, `rockchip,rk3399-spdif`, `rockchip,rk3568-spdif`, `rockchip,rk3128-spdif`, `rockchip,rk3188-spdif`, and 4 more, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `#sound-dai-cells`, and referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/port`, `dai-common.yaml#`.

Key properties include:
- `compatible`
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `clocks`
- `clock-names`
- `dmas`: maxItems 1
- `dma-names`: const tx
- `power-domains`: maxItems 1
- `rockchip,grf`: ref /schemas/types.yaml#/definitions/phandle; The phandle of the syscon node for the GRF register. Required property on RK3288.
- `#sound-dai-cells`: const 0
- `port`: ref /schemas/graph.yaml#/properties/port

Maintainers listed by the binding are Heiko Stuebner <heiko@sntech.de>.

### Control Flow
Validation starts by matching the node's `compatible` value, then applies local `properties`, inherited `$ref` schemas, required-property lists, array bounds, enum/pattern checks, and any conditional branches before rejecting undeclared fields according to the strictness flags. This schema uses composition or conditionals through `allOf`, so the active constraints can vary by compatible string or child-node shape. The embedded example provides a representative DTS fragment that is also compiled by dt-schema tests.

### State, Persistence, And Dependencies
The binding itself persists no runtime state. Its durable effect is the validation contract for source-controlled DTS files and the ABI expectation for existing device trees. Dependencies are the Devicetree meta-schema, referenced common sound schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/port`, `dai-common.yaml#`, and kernel driver match tables that must agree with the compatible strings and resource names.
Strictness settings are `unevaluatedProperties: false`, which makes validation sensitive to extra properties.

### Integration Points
participates in OF graph/audio-graph endpoint wiring; exports or consumes ALSA SoC DAI endpoints; depends on common clock framework phandles and assigned-clock policy; binds to DMA channels for PCM traffic; uses IRQ resources for runtime events; maps MMIO register resources through `reg`.
 At runtime, Open Firmware matching selects the relevant platform, codec, or machine driver; ALSA SoC then consumes the described clocks, routes, DAIs, DMA resources, interrupts, and graph links as applicable.

### Risks
strict property rejection means DTS typos or undocumented vendor extensions fail validation; conditional/allOf composition can make compatible-specific requirements easy to miss; clock order, names, and rates must match the SoC driver expectation; DMA name/order mismatches can produce silent probe or stream failures; register range mistakes may bind the wrong hardware block.

### Test Signals
run `make dt_binding_check` for this schema; compile DTS examples or in-tree boards using the compatible strings; validate the embedded example node; check min/max clock and clock-name tuples for every compatible branch; check DMA channel/name tuple counts.
 Source read covered 113 lines and 2501 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/rockchip-spdif.yaml -->

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
