<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml

## Purpose
Devicetree binding schema for TAS5805M audio amplifier in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas5805m`. The schema description narrows this to: The TAS5805M is a class D audio amplifier with a built-in DSP.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `pvdd-supply`, `pdn-gpios`, `ti,dsp-config-name`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/string`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/string`. Maintainer metadata routes binding review to Daniel Beer <daniel.beer@igorinstitute.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas5805m.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml -->
