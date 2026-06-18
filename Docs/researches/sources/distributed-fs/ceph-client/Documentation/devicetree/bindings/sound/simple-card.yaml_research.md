<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml

## Purpose
Devicetree binding schema for Simple Audio Card Driver in the Linux ASoC sound subsystem. It documents and validates nodes matched by `simple-audio-card`, `simple-scu-audio-card`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#address-cells`, `#size-cells`, `label`, `simple-audio-card,name`, `simple-audio-card,widgets`, `simple-audio-card,routing`, `simple-audio-card,frame-master`, `simple-audio-card,bitclock-master`, `simple-audio-card,frame-inversion`, `simple-audio-card,bitclock-inversion`, `simple-audio-card,format`, `simple-audio-card,mclk-fs`, `simple-audio-card,aux-devs`, plus 30 more.
- Reusable local definitions: `frame-master`, `bitclock-master`, `frame-inversion`, `bitclock-inversion`, `system-clock-frequency`, `system-clock-direction-out`, `system-clock-fixed`, `mclk-fs`, `aux-devs`, `convert-rate`, plus 9 more.
- Pattern properties/child-node shapes: `^simple-audio-card,cpu(@[0-9a-f]+)?$`, `^simple-audio-card,codec(@[0-9a-f]+)?$`, `^simple-audio-card,plat(@[0-9a-f]+)?$`, `^simple-audio-card,dai-link(@[0-9a-f]+)?$`, `^iio-aux(-.+)?$`, `^cpu(-[0-9]+)?$`, `^codec(-[0-9]+)?$`.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string-array`, `tdm-slot.yaml#`, plus 20 more.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`; pattern-matched child/property blocks include `^simple-audio-card,cpu(@[0-9a-f]+)?$`, `^simple-audio-card,codec(@[0-9a-f]+)?$`, `^simple-audio-card,plat(@[0-9a-f]+)?$`, `^simple-audio-card,dai-link(@[0-9a-f]+)?$`, `^iio-aux(-.+)?$`, `^cpu(-[0-9]+)?$`, plus 1 more; 7 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#address-cells`, `#size-cells`, `sound-dai`, `clocks`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string-array`, `tdm-slot.yaml#`, plus 20 more. Maintainer metadata routes binding review to Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/simple-card.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 7 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml -->
