<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml

## Purpose
Devicetree binding schema for StarFive JH7110 PWM-DAC Controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `starfive,jh7110-pwmdac`. The schema description narrows this to: The PWM-DAC Controller uses PWM square wave generators plus RC filters to form a DAC for audio play in StarFive JH7110 SoC. This audio play controller supports 16 bit audio format, up to 48K sampling frequency, up to left and right dual channels.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Hal Feng <hal.feng@starfivetech.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/starfive,jh7110-pwmdac.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml -->
