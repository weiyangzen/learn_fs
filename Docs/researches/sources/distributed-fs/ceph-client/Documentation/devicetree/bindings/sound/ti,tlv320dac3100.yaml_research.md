<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml

## Purpose
Devicetree binding schema for Texas Instruments - tlv320aic31xx Codec module in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320aic310x`, `ti,tlv320aic311x`, `ti,tlv320aic3100`, `ti,tlv320aic3110`, `ti,tlv320aic3120`, `ti,tlv320aic3111`, and 2 more compatible strings. The schema description narrows this to: CODEC output pins: * HPL * HPR * SPL, devices with stereo speaker amp * SPR, devices with stereo speaker amp * SPK, devices with mono speaker amp * MICBIAS CODEC input pins: * MIC1LP, devices with ADC * MIC1RP, devices with ADC * MIC1LM, devices with ADC * AIN1, devices without ADC * AIN2, devices without ADC The pins can be used in referring sound node's audio-routing property.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`, `reset-gpios`, `ai31xx-micbias-vg`, `ai31xx-ocmv`, `gpio-reset`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320dac3100.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml -->
