<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2563/TAS2781 SmartAMP in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2020`, `ti,tas2118`, `ti,tas2120`, `ti,tas2320`, `ti,tas2563`, `ti,tas2568`, and 14 more compatible strings. The schema description narrows this to: The TAS2118/TAS2X20 is mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. The TAS257x is mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. Integrated speaker voltage and current sense provides for real time monitoring of loudspeaker behavior. The TAS2563/TAS2781 is a mono, digita...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `interrupts`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 8 `allOf` block(s); then enforces required keys `compatible`, `reg`; conditional branches include 1 `oneOf`, 7 `if`, 7 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas2781.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml -->
