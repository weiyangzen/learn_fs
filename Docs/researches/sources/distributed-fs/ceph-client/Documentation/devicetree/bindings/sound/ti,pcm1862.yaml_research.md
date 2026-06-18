<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1862.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1862.yaml

## Purpose
Devicetree binding schema for Texas Instruments PCM186x Universal Audio ADC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,pcm1862`, `ti,pcm1863`, `ti,pcm1864`, `ti,pcm1865`. The schema description narrows this to: The Texas Instruments PCM186x family are multi-channel audio ADCs that support both I2C and SPI control interfaces, selected by pin strapping. These devices include on-chip programmable gain amplifiers and support differential or single-ended analog inputs. CODEC input pins: * VINL1 * VINR1 * VINL2 * VINR2 * VINL3 * VINR3 * VINL4 * VINR4 The pins can be used in referring sound node's audio-routing property.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `iovdd-supply`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `iovdd-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Ranganath V N <vnranganath.20@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `iovdd-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm1862.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1862.yaml -->
