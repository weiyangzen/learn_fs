<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320ADCX140 Quad Channel Analog-to-Digital Converter in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320adc3140`, `ti,tlv320adc5140`, `ti,tlv320adc6140`. The schema description narrows this to: The TLV320ADCX140 are multichannel (4-ch analog recording or 8-ch digital PDM microphones recording), high-performance audio, analog-to-digital converter (ADC) with analog inputs supporting up to 2V RMS. The TLV320ADCX140 family supports line and microphone Inputs, and offers a programmable microphone bias or supply voltage generation. Specifications can be found at: https://www.ti.com/lit/ds/symlink/tlv320adc3140...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `areg-supply`, `avdd-supply`, `iovdd-supply`, `ti,mic-bias-source`, `ti,vref-source`, `ti,pdm-edge-select`, `ti,gpi-config`, `ti,gpio-config`, `ti,asi-tx-drive`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^ti,gpo-config-[1-4]$`.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`; pattern-matched child/property blocks include `^ti,gpo-config-[1-4]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Maintainer metadata routes binding review to Andrew Davis <afd@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320adcx140.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml -->
