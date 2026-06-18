<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml

## Purpose
Devicetree binding schema for Samsung Exynos5433 TM2(E) audio complex with WM5110 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,tm2-audio`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `audio-amplifier`, `audio-codec`, `samsung,audio-routing`, `i2s-controller`, `mic-bias-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `audio-amplifier`, `audio-codec`, `audio-routing`, `i2s-controller`, `mic-bias-gpios`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `audio-amplifier`, `audio-codec`, `audio-routing`, `i2s-controller`, `mic-bias-gpios`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,tm2.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml -->
