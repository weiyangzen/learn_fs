<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-sai.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-sai.yaml

## Purpose
Devicetree binding schema for STMicroelectronics STM32 Serial Audio Interface (SAI) in the Linux ASoC sound subsystem. It documents and validates nodes matched by `st,stm32f4-sai`, `st,stm32h7-sai`, `st,stm32mp25-sai`. The schema description narrows this to: The SAI interface (Serial Audio Interface) offers a wide set of audio protocols as I2S standards, LSB or MSB-justified, PCM/DSP, TDM, and AC'97. The SAI contains two independent audio sub-blocks. Each sub-block has its own clock generator and I/O lines controller.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `ranges`, `interrupts`, `resets`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `access-controllers`, `#sound-dai-cells`, `dmas`, `dma-names`, `st,sync`, plus 3 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^audio-controller@[0-9a-f]+$`.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 3 `allOf` block(s); then enforces required keys `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`; pattern-matched child/property blocks include `^audio-controller@[0-9a-f]+$`; conditional branches include 3 `if`, 3 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `resets`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `#sound-dai-cells`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Olivier Moysan <olivier.moysan@foss.st.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/st,stm32-sai.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-sai.yaml -->
