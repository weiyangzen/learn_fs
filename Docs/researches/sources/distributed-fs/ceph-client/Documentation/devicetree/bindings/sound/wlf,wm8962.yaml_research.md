<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml

## Purpose
Devicetree binding schema for Wolfson WM8962 Ultra-Low Power Stereo CODEC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8962`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `interrupts`, `#sound-dai-cells`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, `SPKVDD1-supply`, `SPKVDD2-supply`, `spk-mono`, plus 3 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, plus 2 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8962.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml -->
