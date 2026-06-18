        <!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/fsl,imx95-cm7-sof.yaml -->
        # sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/fsl,imx95-cm7-sof.yaml

        ## Purpose
        `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/fsl,imx95-cm7-sof.yaml` is a devicetree YAML binding for **NXP imx95 CM7 core**. NXP imx95 CM7 core used for audio processing. It describes a codec, microphone, speaker amplifier, or fixed audio endpoint attached through I2C, GPIO, SoundWire-like, or simple platform wiring. The schema id is `http://devicetree.org/schemas/sound/fsl,imx95-cm7-sof.yaml#` and the binding is maintained by Daniel Baluta <daniel.baluta@nxp.com>. I read the complete 64-line source file for this report.

        ## Important APIs, Types, and Schema Contracts
        This file has no executable functions or C types; its API surface is the dt-schema contract that board `.dts` files and Linux ASoC drivers rely on. Compatible values captured by the schema: `fsl,imx95-cm7-sof`. Required properties: `compatible`, `reg`, `reg-names`, `memory-region`, `memory-region-names`, `port`. Notable optional or pattern properties: `reg-names`, `memory-region`, `memory-region-names`, `port`. Child-node or graph-shaped entry points: none declared.

        Key property contracts:
        - `compatible`: const fsl,imx95-cm7-sof
- `reg`: maxItems 1
- `reg-names`: const sram
- `memory-region`: maxItems 1
- `memory-region-names`: const dma
- `port`: ref audio-graph-port.yaml#; SAI3 port.

        Referenced schema dependencies are `audio-graph-port.yaml#`, `fsl,sof-cpu.yaml#`. These `$ref` links integrate this binding with common devicetree type definitions, graph/audio graph ports, DAI common properties, GPIO, clock, interrupt, reserved-memory, and sound-card helper schemas as applicable.

        ## Control Flow and Validation Logic
        Runtime control flow is external to this YAML: `dt_binding_check` loads the file, resolves `$ref`s, applies `properties`, `patternProperties`, `required`, and branch constraints, then validates DTS nodes whose `compatible` matches this binding. The important branch logic in this file is:
        - No explicit `if`/`then`, dependency, or conditional schema branches are present.

        The validation result controls whether downstream kernel drivers can assume resources such as clocks, DMA names, reset lines, graph endpoints, or codec phandles are present and ordered correctly. The property closure mode is `unevaluatedProperties: false`, so unknown DTS properties are rejected unless admitted by referenced schemas.

        ## State and Persistence Behavior
        The binding is declarative and persists only as source-controlled schema text. It does not allocate kernel state, store runtime data, or mutate hardware. Persistent behavior comes from the DTS ABI: once a property, compatible string, clock name, DAI cell count, or routing spelling is accepted here and used by board files, it becomes part of the stable devicetree contract that drivers and boot firmware may depend on.

        ## Dependencies and Integration Points
        Primary integration points are Linux devicetree validation, board DTS files under architecture trees, and ASoC codec, platform, and machine drivers that match the compatible strings or consume the phandles described here. This binding is in the sound schema namespace and commonly integrates with `sound-dai`, `audio-routing`, `audio-graph-card`, `simple-audio-card`, GPIO controls, clock/reset providers, DMA controllers, pinctrl states, reserved memory, and power domains depending on the properties listed above. Example starts with `cm7-cpu@80000000 {`.

        ## Risks and Edge Cases
        The main risk is ABI drift between schema, DTS examples, and driver expectations. Required property changes can break existing boards; loosening constraints can hide invalid hardware descriptions. Ordered arrays such as `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, and routing/link tuples are especially sensitive because drivers often index them positionally. Compatible fallback lists and conditional branches must be kept aligned with actual hardware differences. Pattern properties and child nodes need careful review because a typo in a regex, port name, or DAI-link node can either reject valid boards or admit malformed topology.

        ## Test Signals
        Useful validation signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/fsl,imx95-cm7-sof.yaml` and `make dtbs_check` against boards using the compatible strings above. The embedded example block should compile under dt-schema (present), all `$ref`s should resolve, and any DTS node using this binding should satisfy required keys, property ordering, array lengths, conditional constraints, and the `unevaluatedProperties: false` closure rule.
        <!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/fsl,imx95-cm7-sof.yaml -->
