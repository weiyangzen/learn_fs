<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml

## Purpose
Devicetree binding schema for Qualcomm SoundWire Controller in the Linux SoundWire subsystem. It documents and validates nodes matched by `qcom,soundwire-v1.3.0`, `qcom,soundwire-v1.5.0`, `qcom,soundwire-v1.5.1`, `qcom,soundwire-v1.6.0`, `qcom,soundwire-v1.7.0`, `qcom,soundwire-v2.0.0`, and 3 more compatible strings. The schema description narrows this to: The Qualcomm SoundWire controller along with its board specific bus parameters.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, `wakeup-source`, `qcom,din-ports`, `qcom,dout-ports`, plus 11 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint16-array`, `soundwire-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, plus 2 more; conditional branches include 6 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SoundWire bus schema and Qualcomm or generic SoundWire controller drivers; child peripherals rely on SoundWire addressing and interrupt/clock/reset resources described here. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint16-array`, `soundwire-controller.yaml#`. Maintainer metadata routes binding review to Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Srinivasa Rao Mandadapu <quic_srivasam@quicinc.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=soundwire/qcom,soundwire.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml -->
