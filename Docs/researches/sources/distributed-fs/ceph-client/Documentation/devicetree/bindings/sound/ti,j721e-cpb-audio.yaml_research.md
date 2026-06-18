<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-audio.yaml

## Purpose
Devicetree binding schema for Texas Instruments J721e Common Processor Board Audio Support in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,j721e-cpb-audio`, `ti,j7200-cpb-audio`. The schema description narrows this to: The audio support on the board is using pcm3168a codec connected to McASP10 serializers in parallel setup. The pcm3168a SCKI clock is sourced from j721e AUDIO_REFCLK2 pin. In order to support 48KHz and 44.1KHz family of sampling rates the parent clock for AUDIO_REFCLK2 needs to be changed between PLL4 (for 48KHz) and PLL15 (for 44.1KHz). The same PLLs are used for McASP10's AUXCLK clock via different HSDIVIDER. Cl...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `clocks`, `clock-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `clocks`, `clock-names`; conditional branches include 2 `if`, 2 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`. Maintainer metadata routes binding review to Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,j721e-cpb-audio.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-audio.yaml -->
