        <!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/maxim,max98090.yaml -->
        # sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/maxim,max98090.yaml

        ## Purpose
        `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/maxim,max98090.yaml` is a devicetree YAML binding for **Maxim Integrated MAX98090/MAX98091 audio codecs**. Pins on the device (for linking into audio routes): MIC1, MIC2, DMICL, DMICR, IN1, IN2, IN3, IN4, IN5, IN6, IN12, IN34, IN56, HPL, HPR, SPKL, SPKR, RCVL, RCVR, MICBIAS. It describes a codec, microphone, speaker amplifier, or fixed audio endpoint attached through I2C, GPIO, SoundWire-like, or simple platform wiring. The schema id is `http://devicetree.org/schemas/sound/maxim,max98090.yaml#` and the binding is maintained by Krzysztof Kozlowski <krzk@kernel.org>. I read the complete 84-line source file for this report.

        ## Important APIs, Types, and Schema Contracts
        This file has no executable functions or C types; its API surface is the dt-schema contract that board `.dts` files and Linux ASoC drivers rely on. Compatible values captured by the schema: `maxim,max98090`, `maxim,max98091`. Required properties: `compatible`, `reg`, `interrupts`. Notable optional or pattern properties: `maxim,dmic-freq`, `maxim,micbias`. Child-node or graph-shaped entry points: none declared.

        Key property contracts:
        - `compatible`: enum [maxim,max98090, maxim,max98091]
- `reg`: maxItems 1
- `interrupts`: maxItems 1
- `maxim,dmic-freq`: ref /schemas/types.yaml#/definitions/uint32; DMIC clock frequency.
- `maxim,micbias`: ref /schemas/types.yaml#/definitions/uint32; enum [0, 1, 2, 3]; Micbias voltage applied to the analog mic, valid voltages value are: 0 - 2.2v 1 - 2.55v 2 - 2.4v 3 - 2.8v.

        Referenced schema dependencies are `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. These `$ref` links integrate this binding with common devicetree type definitions, graph/audio graph ports, DAI common properties, GPIO, clock, interrupt, reserved-memory, and sound-card helper schemas as applicable.

        ## Control Flow and Validation Logic
        Runtime control flow is external to this YAML: `dt_binding_check` loads the file, resolves `$ref`s, applies `properties`, `patternProperties`, `required`, and branch constraints, then validates DTS nodes whose `compatible` matches this binding. The important branch logic in this file is:
        - No explicit `if`/`then`, dependency, or conditional schema branches are present.

        The validation result controls whether downstream kernel drivers can assume resources such as clocks, DMA names, reset lines, graph endpoints, or codec phandles are present and ordered correctly. The property closure mode is `unevaluatedProperties: false`, so unknown DTS properties are rejected unless admitted by referenced schemas.

        ## State and Persistence Behavior
        The binding is declarative and persists only as source-controlled schema text. It does not allocate kernel state, store runtime data, or mutate hardware. Persistent behavior comes from the DTS ABI: once a property, compatible string, clock name, DAI cell count, or routing spelling is accepted here and used by board files, it becomes part of the stable devicetree contract that drivers and boot firmware may depend on.

        ## Dependencies and Integration Points
        Primary integration points are Linux devicetree validation, board DTS files under architecture trees, and ASoC codec, platform, and machine drivers that match the compatible strings or consume the phandles described here. This binding is in the sound schema namespace and commonly integrates with `sound-dai`, `audio-routing`, `audio-graph-card`, `simple-audio-card`, GPIO controls, clock/reset providers, DMA controllers, pinctrl states, reserved memory, and power domains depending on the properties listed above. Example starts with `i2c {`.

        ## Risks and Edge Cases
        The main risk is ABI drift between schema, DTS examples, and driver expectations. Required property changes can break existing boards; loosening constraints can hide invalid hardware descriptions. Ordered arrays such as `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, and routing/link tuples are especially sensitive because drivers often index them positionally. Compatible fallback lists and conditional branches must be kept aligned with actual hardware differences. Pattern properties and child nodes need careful review because a typo in a regex, port name, or DAI-link node can either reject valid boards or admit malformed topology.

        ## Test Signals
        Useful validation signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/maxim,max98090.yaml` and `make dtbs_check` against boards using the compatible strings above. The embedded example block should compile under dt-schema (present), all `$ref`s should resolve, and any DTS node using this binding should satisfy required keys, property ordering, array lengths, conditional constraints, and the `unevaluatedProperties: false` closure rule.
        <!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/maxim,max98090.yaml -->
