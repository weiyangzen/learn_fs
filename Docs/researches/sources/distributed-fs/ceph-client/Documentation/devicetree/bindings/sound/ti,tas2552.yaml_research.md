<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2552.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2552.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2552 Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2552`. The schema description narrows this to: The TAS2552 can receive its reference clock via MCLK, BCLK, IVCLKIN pin or use the internal 1.8MHz. This CLKIN is used by the PLL. In addition to PLL, the PDM reference clock is also selectable: PLL, IVCLKIN, BCLK or MCLK. For system integration the dt-bindings/sound/tas2552.h header file provides defined values to select and configure the PLL and PDM reference clocks.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `vbat-supply`, `iovdd-supply`, `avdd-supply`, `enable-gpio`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `vbat-supply`, `iovdd-supply`, `avdd-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>, Kevin Lu <kevin-lu@ti.com>, Baojun Xu <baojun.xu@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `vbat-supply`, `iovdd-supply`, `avdd-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas2552.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2552.yaml -->
