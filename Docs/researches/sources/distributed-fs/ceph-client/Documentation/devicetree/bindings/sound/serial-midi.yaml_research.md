<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml

## Purpose
Devicetree binding schema fragment for Generic Serial MIDI Interface in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: Generic MIDI interface using a serial device. This denotes that a serial device is dedicated to MIDI communication, either to an external MIDI device through a DIN5 or other connector, or to a known hardwired MIDI controller. This device must be a child node of a serial node. Can only be set to use standard baud rates corresponding to supported rates of the parent serial device. If the standard MIDI baud of 31.25...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `current-speed`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/serial/serial-peripheral-props.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/serial/serial-peripheral-props.yaml#`. Maintainer metadata routes binding review to Daniel Kaehn <kaehndan@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/serial-midi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml -->
