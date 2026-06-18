<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml

## Purpose
Devicetree binding schema for Spreadtrum Multi-Channel Data Transfer controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `sprd,sc9860-mcdt`. The schema description narrows this to: The Multi-channel data transfer controller is used for sound stream transmission between the audio subsystem and other AP/CP subsystem. It supports 10 DAC channels and 10 ADC channels, and each channel can be configured with DMA mode or interrupt mode.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `interrupts`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sprd,sc9860-mcdt.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml -->
