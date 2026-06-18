<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic32x4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic32x4.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320AIC32x4 Stereo Audio codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2505`, `ti,tlv320aic32x4`, `ti,tlv320aic32x6`. The schema description narrows this to: The TLV320AIC32x4 audio codec can be accessed using I2C or SPI

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `av-supply`, `dv-supply`, `iov-supply`, `ldoin-supply`, `reset-gpios`, `#sound-dai-cells`, `aic32x4-gpio-func`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `iov-supply`; conditional branches include 1 `if`, 1 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Maintainer metadata routes binding review to Alexander Stein <alexander.stein@ew.tq-group.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `iov-supply`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320aic32x4.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic32x4.yaml -->
