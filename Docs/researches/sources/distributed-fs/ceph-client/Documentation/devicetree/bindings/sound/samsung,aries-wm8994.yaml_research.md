<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml

## Purpose
Devicetree binding schema for Samsung Aries audio complex with WM8994 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,aries-wm8994`, `samsung,fascinate4g-wm8994`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `cpu`, `codec`, `samsung,audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, `headset-detect-gpios`, `headset-key-gpios`, `io-channels`, `io-channel-names`, `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `cpu`, `codec`, `audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, plus 2 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Jonathan Bakker <xc-racer2@live.ca>.

## Risks and edge cases
missing required properties (`compatible`, `cpu`, `codec`, `audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,aries-wm8994.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml -->
