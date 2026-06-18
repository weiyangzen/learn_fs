<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8731.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8731.yaml

## Purpose
Devicetree binding schema for Wolfson Microelectromics WM8731 audio CODEC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8731`. The schema description narrows this to: Wolfson Microelectronics WM8731 audio CODEC Pins on the device (for linking into audio routes): * LOUT: Left Channel Line Output * ROUT: Right Channel Line Output * LHPOUT: Left Channel Headphone Output * RHPOUT: Right Channel Headphone Output * LLINEIN: Left Channel Line Input * RLINEIN: Right Channel Line Input * MICIN: Microphone Input

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `AVDD-supply`, `HPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `reg`, `compatible`, `AVDD-supply`, `HPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`reg`, `compatible`, `AVDD-supply`, `HPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8731.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8731.yaml -->
