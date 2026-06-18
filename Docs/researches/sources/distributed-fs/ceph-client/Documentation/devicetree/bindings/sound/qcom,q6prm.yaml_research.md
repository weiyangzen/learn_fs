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
