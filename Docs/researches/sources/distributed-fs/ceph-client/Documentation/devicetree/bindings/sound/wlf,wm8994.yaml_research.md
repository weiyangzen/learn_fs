<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8994.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8994.yaml

## Purpose
Devicetree binding schema for Wolfson WM1811/WM8994/WM8958 audio codecs in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm1811`, `wlf,wm8994`, `wlf,wm8958`. The schema description narrows this to: These devices support both I2C and SPI (configured with pin strapping on the board). Pins on the device (for linking into audio routes): IN1LN, IN1LP, IN2LN, IN2LP:VXRN, IN1RN, IN1RP, IN2RN, IN2RP:VXRP, SPKOUTLP, SPKOUTLN, SPKOUTRP, SPKOUTRN, HPOUT1L, HPOUT1R, HPOUT2P, HPOUT2N, LINEOUT1P, LINEOUT1N, LINEOUT2P, LINEOUT2N.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `AVDD1-supply`, `AVDD2-supply`, `CPVDD-supply`, `DBVDD-supply`, `DBVDD1-supply`, plus 19 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `AVDD2-supply`, `CPVDD-supply`, `SPKVDD1-supply`, `SPKVDD2-supply`; conditional branches include 1 `if`, 1 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `AVDD2-supply`, `CPVDD-supply`, `SPKVDD1-supply`, `SPKVDD2-supply`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8994.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8994.yaml -->
