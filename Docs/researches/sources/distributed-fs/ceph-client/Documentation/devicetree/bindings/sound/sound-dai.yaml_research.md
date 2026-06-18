<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml

## Purpose
Devicetree binding schema fragment for Digital Audio Interface consumer in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`. Maintainer metadata routes binding review to Rob Herring <robh@kernel.org>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sound-dai.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml -->
