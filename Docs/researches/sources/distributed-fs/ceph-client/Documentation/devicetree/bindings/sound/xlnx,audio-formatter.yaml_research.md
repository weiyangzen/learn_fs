<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml

## Purpose
Devicetree binding schema for Xilinx PL audio formatter in the Linux ASoC sound subsystem. It documents and validates nodes matched by `xlnx,audio-formatter-1.0`. The schema description narrows this to: The IP core supports DMA, data formatting(AES<->PCM conversion) of audio samples.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Vincenzo Frascino <vincenzo.frascino@arm.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xlnx,audio-formatter.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml -->
