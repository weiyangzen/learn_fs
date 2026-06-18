<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8904.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8904.yaml

## Purpose
Devicetree binding schema for Wolfson WM8904/WM8912 audio codecs in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8904`, `wlf,wm8912`. The schema description narrows this to: Pins on the device (for linking into audio routes): IN1L, IN1R, IN2L, IN2R, IN3L, IN3R, HPOUTL, HPOUTR, LINEOUTL, LINEOUTR, MICBIAS

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `wlf,in1l-as-dmicdat1`, `wlf,in1r-as-dmicdat2`, `wlf,gpio-cfg`, `wlf,micbias-cfg`, plus 5 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint16-matrix`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, plus 1 more; conditional branches include 1 `dependencies`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint16-matrix`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `dai-common.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, plus 1 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8904.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8904.yaml -->
