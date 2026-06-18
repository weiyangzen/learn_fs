<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320AIC3x Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320aic23`, `ti,tlv320aic3x`, `ti,tlv320aic33`, `ti,tlv320aic3007`, `ti,tlv320aic3106`, `ti,tlv320aic3104`. The schema description narrows this to: TLV320AIC3x are a series of low-power stereo audio codecs with stereo headphone amplifier, as well as multiple inputs and outputs programmable in single-ended or fully differential configurations. The serial control bus supports SPI or I2C protocols, while the serial audio data bus is programmable for I2S, left/right-justified, DSP, or TDM modes. The following pins can be referred in the sound node's audio routing...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `gpio-reset`, `ai3x-gpio-func`, `ai3x-micbias-vg`, `ai3x-ocmv`, `AVDD-supply`, `IOVDD-supply`, `DRVDD-supply`, `DVDD-supply`, `#sound-dai-cells`, `clocks`, `port`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`; conditional branches include 2 `oneOf`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Jai Luthra <j-luthra@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320aic3x.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml -->
