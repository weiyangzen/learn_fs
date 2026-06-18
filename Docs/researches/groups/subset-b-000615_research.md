# subset-b-000615 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml

## Purpose
Devicetree binding schema for Samsung Aries audio complex with WM8994 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,aries-wm8994`, `samsung,fascinate4g-wm8994`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `cpu`, `codec`, `samsung,audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, `headset-detect-gpios`, `headset-key-gpios`, `io-channels`, `io-channel-names`, `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `cpu`, `codec`, `audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, plus 2 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Jonathan Bakker <xc-racer2@live.ca>.

## Risks and edge cases
missing required properties (`compatible`, `cpu`, `codec`, `audio-routing`, `extcon`, `main-micbias-supply`, `headset-micbias-supply`, `earpath-sel-gpios`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,aries-wm8994.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,aries-wm8994.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,arndale.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,arndale.yaml

## Purpose
Devicetree binding schema for Insignal Arndale boards audio complex in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,arndale-alc5631`, `samsung,arndale-rt5631`, `samsung,arndale-wm1811`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `samsung,audio-codec`, `samsung,audio-cpu`, `samsung,model`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `samsung,audio-codec`, `samsung,audio-cpu`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `samsung,audio-codec`, `samsung,audio-cpu`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,arndale.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,arndale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,midas-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,midas-audio.yaml

## Purpose
Devicetree binding schema for Samsung Midas audio complex with WM1811 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,midas-audio`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `cpu`, `codec`, `samsung,audio-routing`, `mic-bias-supply`, `submic-bias-supply`, `headset-mic-bias-supply`, `fm-sel-gpios`, `lineout-sel-gpios`, `headset-detect-gpios`, `headset-key-gpios`, `io-channels`, `io-channel-names`, `samsung,headset-4pole-threshold-microvolt`, plus 2 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `cpu`, `codec`, `audio-routing`, `mic-bias-supply`, `submic-bias-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `cpu`, `codec`, `audio-routing`, `mic-bias-supply`, `submic-bias-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,midas-audio.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,midas-audio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,odroid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,odroid.yaml

## Purpose
Devicetree binding schema for Samsung Exynos Odroid XU3/XU4 audio complex with MAX98090 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `hardkernel,odroid-xu3-audio`, `hardkernel,odroid-xu4-audio`, `samsung,odroid-xu3-audio`, `samsung,odroid-xu4-audio`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `cpu`, `codec`, `samsung,audio-routing`, `samsung,audio-widgets`, `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `cpu`, `codec`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `cpu`, `codec`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,odroid.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,odroid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,smdk5250.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,smdk5250.yaml

## Purpose
Devicetree binding schema for Samsung SMDK5250 audio complex with WM8994 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,smdk-wm8994`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `samsung,audio-codec`, `samsung,i2s-controller`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `samsung,audio-codec`, `samsung,i2s-controller`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `samsung,audio-codec`, `samsung,i2s-controller`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,smdk5250.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,smdk5250.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,snow.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,snow.yaml

## Purpose
Devicetree binding schema for Google Snow audio complex with MAX9809x codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `google,snow-audio-max98090`, `google,snow-audio-max98091`, `google,snow-audio-max98095`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `codec`, `cpu`, `samsung,audio-codec`, `samsung,i2s-controller`, `samsung,model`, `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `codec`, `cpu`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `codec`, `cpu`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,snow.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,snow.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml

## Purpose
Devicetree binding schema for Samsung Exynos5433 TM2(E) audio complex with WM5110 codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,tm2-audio`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `audio-amplifier`, `audio-codec`, `samsung,audio-routing`, `i2s-controller`, `mic-bias-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `audio-amplifier`, `audio-codec`, `audio-routing`, `i2s-controller`, `mic-bias-gpios`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `sound-card-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `audio-amplifier`, `audio-codec`, `audio-routing`, `i2s-controller`, `mic-bias-gpios`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung,tm2.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung,tm2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung-i2s.yaml

## Purpose
Devicetree binding schema for Samsung SoC I2S controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `samsung,s3c6410-i2s`, `samsung,s5pv210-i2s`, `samsung,exynos5420-i2s`, `samsung,exynos7-i2s`, `samsung,exynos7-i2s1`, `tesla,fsd-i2s`, and 1 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#address-cells`, `#size-cells`, `reg`, `dmas`, `dma-names`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `interrupts`, `samsung,idma-addr`, `power-domains`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `dmas`, `dma-names`, `clocks`, `clock-names`; conditional branches include 4 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#address-cells`, `#size-cells`, `reg`, `dmas`, `dma-names`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `dmas`, `dma-names`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/samsung-i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/samsung-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml

## Purpose
Devicetree binding schema fragment for Generic Serial MIDI Interface in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: Generic MIDI interface using a serial device. This denotes that a serial device is dedicated to MIDI communication, either to an external MIDI device through a DIN5 or other connector, or to a known hardwired MIDI controller. This device must be a child node of a serial node. Can only be set to use standard baud rates corresponding to supported rates of the parent serial device. If the standard MIDI baud of 31.25...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `current-speed`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/serial/serial-peripheral-props.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/serial/serial-peripheral-props.yaml#`. Maintainer metadata routes binding review to Daniel Kaehn <kaehndan@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/serial-midi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/serial-midi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-amplifier.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-amplifier.yaml

## Purpose
Devicetree binding schema for Simple Audio Amplifier in the Linux ASoC sound subsystem. It documents and validates nodes matched by `dioo,dio2125`, `simple-audio-amplifier`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `enable-gpios`, `VCC-supply`, `sound-name-prefix`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Jerome Brunet <jbrunet@baylibre.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/simple-audio-amplifier.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-amplifier.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-mux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-mux.yaml

## Purpose
Devicetree binding schema for Simple Audio Multiplexer in the Linux ASoC sound subsystem. It documents and validates nodes matched by `simple-audio-mux`. The schema description narrows this to: Simple audio multiplexers are driven using gpios, allowing to select which of their input line is connected to the output line.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `mux-gpios`, `state-labels`, `idle-state`, `sound-name-prefix`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/mux/mux-controller.yaml#/properties/idle-state`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `mux-gpios`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/mux/mux-controller.yaml#/properties/idle-state`. Maintainer metadata routes binding review to Alexandre Belloni <aleandre.belloni@bootlin.com>.

## Risks and edge cases
missing required properties (`compatible`, `mux-gpios`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/simple-audio-mux.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-audio-mux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml

## Purpose
Devicetree binding schema for Simple Audio Card Driver in the Linux ASoC sound subsystem. It documents and validates nodes matched by `simple-audio-card`, `simple-scu-audio-card`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#address-cells`, `#size-cells`, `label`, `simple-audio-card,name`, `simple-audio-card,widgets`, `simple-audio-card,routing`, `simple-audio-card,frame-master`, `simple-audio-card,bitclock-master`, `simple-audio-card,frame-inversion`, `simple-audio-card,bitclock-inversion`, `simple-audio-card,format`, `simple-audio-card,mclk-fs`, `simple-audio-card,aux-devs`, plus 30 more.
- Reusable local definitions: `frame-master`, `bitclock-master`, `frame-inversion`, `bitclock-inversion`, `system-clock-frequency`, `system-clock-direction-out`, `system-clock-fixed`, `mclk-fs`, `aux-devs`, `convert-rate`, plus 9 more.
- Pattern properties/child-node shapes: `^simple-audio-card,cpu(@[0-9a-f]+)?$`, `^simple-audio-card,codec(@[0-9a-f]+)?$`, `^simple-audio-card,plat(@[0-9a-f]+)?$`, `^simple-audio-card,dai-link(@[0-9a-f]+)?$`, `^iio-aux(-.+)?$`, `^cpu(-[0-9]+)?$`, `^codec(-[0-9]+)?$`.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string-array`, `tdm-slot.yaml#`, plus 20 more.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`; pattern-matched child/property blocks include `^simple-audio-card,cpu(@[0-9a-f]+)?$`, `^simple-audio-card,codec(@[0-9a-f]+)?$`, `^simple-audio-card,plat(@[0-9a-f]+)?$`, `^simple-audio-card,dai-link(@[0-9a-f]+)?$`, `^iio-aux(-.+)?$`, `^cpu(-[0-9]+)?$`, plus 1 more; 7 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#address-cells`, `#size-cells`, `sound-dai`, `clocks`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string-array`, `tdm-slot.yaml#`, plus 20 more. Maintainer metadata routes binding review to Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/simple-card.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 7 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/simple-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/snps,designware-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/snps,designware-i2s.yaml

## Purpose
Devicetree binding schema for DesignWare I2S controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `canaan,k210-i2s`, `snps,designware-i2s`, `starfive,jh7110-i2stx0`, `starfive,jh7110-i2stx1`, `starfive,jh7110-i2srx`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `starfive,syscon`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle-array`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 6 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`; conditional branches include 2 `oneOf`, 5 `if`, 5 `then`, 3 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`, `dai-common.yaml#`. Maintainer metadata routes binding review to Jose Abreu <joabreu@synopsys.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/snps,designware-i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/snps,designware-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-aio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-aio.yaml

## Purpose
Devicetree binding schema for UniPhier AIO audio system in the Linux ASoC sound subsystem. It documents and validates nodes matched by `socionext,uniphier-ld11-aio`, `socionext,uniphier-ld20-aio`, `socionext,uniphier-pxs2-aio`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `reset-names`, `resets`, `socionext,syscon`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^port@[0-9]$`.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`; pattern-matched child/property blocks include `^port@[0-9]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to <alsa-devel@alsa-project.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/socionext,uniphier-aio.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-aio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-evea.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-evea.yaml

## Purpose
Devicetree binding schema for UniPhier EVEA SoC-internal sound codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `socionext,uniphier-evea`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^port@[0-9]$`.
- External schema APIs: `dai-common.yaml#`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`; pattern-matched child/property blocks include `^port@[0-9]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to <alsa-devel@alsa-project.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clock-names`, `clocks`, `reset-names`, `resets`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/socionext,uniphier-evea.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/socionext,uniphier-evea.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-codecs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-codecs.yaml

## Purpose
Devicetree binding schema for Sophgo CV1800B Internal ADC/DAC Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `sophgo,cv1800b-sound-adc`, `sophgo,cv1800b-sound-dac`. The schema description narrows this to: Internal ADC and DAC audio codecs integrated in the Sophgo CV1800B SoC. Codecs expose a single DAI and are intended to be connected to an I2S/TDM controller via an ASoC machine driver.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Anton D. Stavinskii <stavinsky@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sophgo,cv1800b-codecs.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-codecs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-i2s.yaml

## Purpose
Devicetree binding schema for Sophgo CV1800B I2S/TDM controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `sophgo,cv1800b-i2s`. The schema description narrows this to: I2S/TDM controller found in CV1800B / Sophgo SG2002/SG2000 SoCs.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `dmas`, `dma-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Anton D. Stavinskii <stavinsky@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sophgo,cv1800b-i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sophgo,cv1800b-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-card-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-card-common.yaml

## Purpose
Devicetree binding schema fragment for Board Sound Card Common Properties in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `audio-routing`, `ignore-suspend-widgets`, `model`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `model`.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `model`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/string`. Maintainer metadata routes binding review to Mark Brown <broonie@kernel.org>.

## Risks and edge cases
missing required properties (`model`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sound-card-common.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-card-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml

## Purpose
Devicetree binding schema fragment for Digital Audio Interface consumer in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `sound-dai`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/phandle-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `sound-dai`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`. Maintainer metadata routes binding review to Rob Herring <robh@kernel.org>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sound-dai.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sound-dai.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/spacemit,k1-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/spacemit,k1-i2s.yaml

## Purpose
Devicetree binding schema for K1 I2S controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `spacemit,k1-i2s`. The schema description narrows this to: The I2S bus (Inter-IC sound bus) is a serial link for digital audio data transfer between devices in the system.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, `port`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Troy Mitchell <troy.mitchell@linux.spacemit.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/spacemit,k1-i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/spacemit,k1-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,pcm-platform.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,pcm-platform.yaml

## Purpose
Devicetree binding schema for Spreadtrum DMA platform in the Linux ASoC sound subsystem. It documents and validates nodes matched by `sprd,pcm-platform`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `dmas`, `dma-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `dmas`, `dma-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `dmas`, `dma-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sprd,pcm-platform.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,pcm-platform.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml

## Purpose
Devicetree binding schema for Spreadtrum Multi-Channel Data Transfer controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `sprd,sc9860-mcdt`. The schema description narrows this to: The Multi-channel data transfer controller is used for sound stream transmission between the audio subsystem and other AP/CP subsystem. It supports 10 DAC channels and 10 ADC channels, and each channel can be configured with DMA mode or interrupt mode.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `interrupts`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/sprd,sc9860-mcdt.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/sprd,sc9860-mcdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-i2s.yaml

## Purpose
Devicetree binding schema for STMicroelectronics STM32 SPI/I2S Controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `st,stm32h7-i2s`, `st,stm32mp25-i2s`. The schema description narrows this to: The SPI/I2S block supports I2S/PCM protocols when configured on I2S mode. Only some SPI instances support I2S.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `resets`, `#clock-cells`, `port`, `access-controllers`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `audio-graph-port.yaml#`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 3 `allOf` block(s); then enforces required keys `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`; conditional branches include 2 `if`, 2 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `resets`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `audio-graph-port.yaml#`, `dai-common.yaml#`. Maintainer metadata routes binding review to Olivier Moysan <olivier.moysan@foss.st.com>.

## Risks and edge cases
missing required properties (`compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/st,stm32-i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-i2s.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-spdifrx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-spdifrx.yaml

## Purpose
Devicetree binding schema for STMicroelectronics STM32 S/PDIF receiver (SPDIFRX) in the Linux ASoC sound subsystem. It documents and validates nodes matched by `st,stm32h7-spdifrx`. The schema description narrows this to: The SPDIFRX peripheral, is designed to receive an S/PDIF flow compliant with IEC-60958 and IEC-61937.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `resets`, `port`, `access-controllers`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `resets`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Olivier Moysan <olivier.moysan@foss.st.com>.

## Risks and edge cases
missing required properties (`compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/st,stm32-spdifrx.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/st,stm32-spdifrx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml

## Purpose
Devicetree binding schema for StarFive JH7110 PWM-DAC Controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `starfive,jh7110-pwmdac`. The schema description narrows this to: The PWM-DAC Controller uses PWM square wave generators plus RC filters to form a DAC for audio play in StarFive JH7110 SoC. This audio play controller supports 16 bit audio format, up to 48K sampling frequency, up to left and right dual channels.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Hal Feng <hal.feng@starfivetech.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/starfive,jh7110-pwmdac.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-pwmdac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-tdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-tdm.yaml

## Purpose
Devicetree binding schema for StarFive JH7110 TDM Controller in the Linux ASoC sound subsystem. It documents and validates nodes matched by `starfive,jh7110-tdm`. The schema description narrows this to: The TDM Controller is a Time Division Multiplexed audio interface integrated in StarFive JH7110 SoC, allowing up to 8 channels of audio over a serial interface. The TDM controller can operate both in master and slave mode.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Walker Chen <walker.chen@starfivetech.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/starfive,jh7110-tdm.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/starfive,jh7110-tdm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/tdm-slot.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/tdm-slot.yaml

## Purpose
Devicetree binding schema fragment for Time Division Multiplexing (TDM) Slot Parameters in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `dai-tdm-slot-num`, `dai-tdm-slot-width`, `dai-tdm-idle-mode`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^dai-tdm-slot-[rt]x-mask$`, `^dai-tdm-slot-[rt]x-idle-mask$`.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; pattern-matched child/property blocks include `^dai-tdm-slot-[rt]x-mask$`, `^dai-tdm-slot-[rt]x-idle-mask$`.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are none declared. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32-array`. Maintainer metadata routes binding review to Liam Girdwood <lgirdwood@gmail.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/tdm-slot.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/tdm-slot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/test-component.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/test-component.yaml

## Purpose
Devicetree binding schema fragment for Test Component in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `compatible`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/test-component.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/test-component.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-ivi-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-ivi-audio.yaml

## Purpose
Devicetree binding schema for Texas Instruments J721e Common Processor Board Audio Support in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,j721e-cpb-ivi-audio`. The schema description narrows this to: The Infotainment board plugs into the Common Processor Board, the support of the extension board is extending the CPB audio support, described in: sound/ti,j721e-cpb-audio.txt The audio support on the Infotainment Expansion Board consists of McASP0 connected to two pcm3168a codecs with dedicated set of serializers to each. The SCKI for pcm3168a is sourced from j721e AUDIO_REFCLK0 pin. In order to support 48KHz and...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `ti,ivi-mcasp`, `ti,ivi-codec-a`, `ti,ivi-codec-b`, `clocks`, `clock-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `ti,ivi-mcasp`, `ti,ivi-codec-a`, `ti,ivi-codec-b`, `clocks`, plus 1 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`. Maintainer metadata routes binding review to Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `ti,ivi-mcasp`, `ti,ivi-codec-a`, `ti,ivi-codec-b`, `clocks`, plus 1 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,j721e-cpb-ivi-audio.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,j721e-cpb-ivi-audio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap-twl4030.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap-twl4030.yaml

## Purpose
Devicetree binding schema for Texas Instruments SoC with twl4030 based audio setups in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,omap-twl4030`. The schema description narrows this to: Audio setups on TI OMAP SoCs using TWL4030-family audio codec connected via a McBSP port.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `ti,model`, `ti,mcbsp`, `ti,codec`, `ti,mcbsp-voice`, `ti,jack-det-gpio`, `ti,audio-routing`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/non-unique-string-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `ti,model`, `ti,mcbsp`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/non-unique-string-array`. Maintainer metadata routes binding review to Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `ti,model`, `ti,mcbsp`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,omap-twl4030.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap-twl4030.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap4-mcpdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap4-mcpdm.yaml

## Purpose
Devicetree binding schema for OMAP McPDM in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,omap4-mcpdm`. The schema description narrows this to: OMAP ALSA SoC DAI driver using McPDM port used by TWL6040

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `reg-names`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to Misael Lopez Cruz <misael.lopez@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `reg-names`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,omap4-mcpdm.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,omap4-mcpdm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1681.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1681.yaml

## Purpose
Devicetree binding schema for Texas Instruments PCM1681 8-channel Digital-to-Analog Converter in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,pcm1681`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>, Kevin Lu <kevin-lu@ti.com>, Baojun Xu <baojun.xu@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm1681.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1681.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1754.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1754.yaml

## Purpose
Devicetree binding schema for Texas Instruments PCM1754 Stereo DAC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,pcm1754`. The schema description narrows this to: The PCM1754 is a simple stereo DAC that is controlled via hardware gpios.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `vcc-supply`, `#sound-dai-cells`, `format-gpios`, `mute-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `#sound-dai-cells`, `vcc-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Stefan Kerkmann <s.kerkmann@pengutronix.de>.

## Risks and edge cases
missing required properties (`compatible`, `#sound-dai-cells`, `vcc-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm1754.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm1754.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm3168a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm3168a.yaml

## Purpose
Devicetree binding schema for Texas Instruments PCM3168A Audio Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,pcm3168a`. The schema description narrows this to: The Texas Instruments PCM3168A is a 24-bit Multi-channel Audio CODEC with 96/192kHz sampling rate, supporting both SPI and I2C bus access.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `reset-gpios`, `#sound-dai-cells`, `VDD1-supply`, `VDD2-supply`, `VCCAD1-supply`, `VCCAD2-supply`, `VCCDA1-supply`, `VCCDA2-supply`, `ports`, `port@0`, plus 1 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `audio-graph-port.yaml#/definitions/port-base`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `VDD1-supply`, `VDD2-supply`, `VCCAD1-supply`, `VCCAD2-supply`, plus 2 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `audio-graph-port.yaml#/definitions/port-base`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Damien Horsley <Damien.Horsley@imgtec.com>, Geert Uytterhoeven <geert+renesas@glider.be>, Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `VDD1-supply`, `VDD2-supply`, `VCCAD1-supply`, `VCCAD2-supply`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm3168a.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm3168a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm512x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm512x.yaml

## Purpose
Devicetree binding schema for PCM512x and TAS575x audio CODECs/amplifiers in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,pcm5121`, `ti,pcm5122`, `ti,pcm5141`, `ti,pcm5142`, `ti,pcm5242`, `ti,tas5754`, and 1 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `AVDD-supply`, `DVDD-supply`, `CPVDD-supply`, `clocks`, `#sound-dai-cells`, `pll-in`, `pll-out`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `AVDD-supply`, `DVDD-supply`, `CPVDD-supply`; conditional branches include 1 `if`, 1 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Animesh Agarwal <animeshagarwal28@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `AVDD-supply`, `DVDD-supply`, `CPVDD-supply`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm512x.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm512x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm6240.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm6240.yaml

## Purpose
Devicetree binding schema for Texas Instruments PCM6240 Family Audio ADC/DAC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,adc3120`, `ti,adc5120`, `ti,pcm3120`, `ti,pcm5120`, `ti,pcm6120`, `ti,adc6120`, and 15 more compatible strings. The schema description narrows this to: The PCM6240 Family is a big family of Audio ADC/DAC for different Specifications, range from Personal Electric to Automotive Electric, even some professional fields. Specifications about the audio chip can be found at: https://www.ti.com/lit/gpn/tlv320adc3120 https://www.ti.com/lit/gpn/tlv320adc5120 https://www.ti.com/lit/gpn/tlv320adc6120 https://www.ti.com/lit/gpn/dix4192 https://www.ti.com/lit/gpn/pcm1690 https...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `interrupts`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`; conditional branches include 1 `oneOf`, 1 `if`, 1 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,pcm6240.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,pcm6240.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,src4xxx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,src4xxx.yaml

## Purpose
Devicetree binding schema for Texas Instruments SRC4392 in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,src4392`. The schema description narrows this to: The SRC4392 is a digital audio codec that can be connected via I2C or SPI. Currently, only I2C bus is supported.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#sound-dai-cells`, `reg`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `#sound-dai-cells`, `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Matt Flax <flatmax@flatmax.com>.

## Risks and edge cases
missing required properties (`#sound-dai-cells`, `compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,src4xxx.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,src4xxx.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2562.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2562.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2562 Smart PA in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2562`, `ti,tas2564`, `ti,tas2110`. The schema description narrows this to: The TAS2562 is a mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. Integrated speaker voltage and current sense provides for real time monitoring of loudspeaker behavior. Specifications about the audio amplifier can be found at: https://www.ti.com/lit/gpn/tas2562 https://www.ti.com/lit/gpn/tas2564 https://www.ti.com/lit/gpn/tas2110

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `shut-down-gpios`, `shutdown-gpios`, `interrupts`, `ti,imon-slot-no`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Andrew Davis <afd@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas2562.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2562.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2770.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2770.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2770 Smart PA in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2770`, `ti,tas5770l`. The schema description narrows this to: The TAS2770 is a mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. Integrated speaker voltage and current sense provides for real time monitoring of loudspeaker behavior.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `shutdown-gpios`, `interrupts`, `ti,imon-slot-no`, `ti,vmon-slot-no`, `ti,asi-format`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Shi Fu <shifu0704@thundersoft.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas2770.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2770.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2563/TAS2781 SmartAMP in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2020`, `ti,tas2118`, `ti,tas2120`, `ti,tas2320`, `ti,tas2563`, `ti,tas2568`, and 14 more compatible strings. The schema description narrows this to: The TAS2118/TAS2X20 is mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. The TAS257x is mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. Integrated speaker voltage and current sense provides for real time monitoring of loudspeaker behavior. The TAS2563/TAS2781 is a mono, digita...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `interrupts`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 8 `allOf` block(s); then enforces required keys `compatible`, `reg`; conditional branches include 1 `oneOf`, 7 `if`, 7 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas2781.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas2781.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas27xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas27xx.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS2764/TAS2780 Smart PA in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas2764`, `ti,tas2780`, `ti,sn012776`. The schema description narrows this to: The TAS2764/TAS2780 is a mono, digital input Class-D audio amplifier optimized for efficiently driving high peak power into small loudspeakers. Integrated speaker voltage and current sense provides for real time monitoring of loudspeaker behavior.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `shutdown-gpios`, `interrupts`, `ti,imon-slot-no`, `ti,vmon-slot-no`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas27xx.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas27xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas57xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas57xx.yaml

## Purpose
Devicetree binding schema for Texas Instruments TAS5711/TAS5717/TAS5719/TAS5721 stereo power amplifiers in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas5707`, `ti,tas5711`, `ti,tas5717`, `ti,tas5719`, `ti,tas5721`, `ti,tas5733`, and 1 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `pdn-gpios`, `clocks`, `clock-names`, `AVDD-supply`, `DVDD-supply`, `HPVDD-supply`, `PVDD_AB-supply`, `PVDD_CD-supply`, `PVDD_A-supply`, `PVDD_B-supply`, `PVDD_C-supply`, plus 5 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `audio-graph-port.yaml#`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 4 `allOf` block(s); then enforces required keys `compatible`, `reg`, `#sound-dai-cells`; conditional branches include 3 `if`, 3 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `audio-graph-port.yaml#`, `dai-common.yaml#`. Maintainer metadata routes binding review to Neil Armstrong <neil.armstrong@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `#sound-dai-cells`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas57xx.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas57xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml

## Purpose
Devicetree binding schema for TAS5805M audio amplifier in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tas5805m`. The schema description narrows this to: The TAS5805M is a class D audio amplifier with a built-in DSP.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `pvdd-supply`, `pdn-gpios`, `ti,dsp-config-name`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/string`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/string`. Maintainer metadata routes binding review to Daniel Beer <daniel.beer@igorinstitute.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tas5805m.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tas5805m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adc3xxx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adc3xxx.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320ADC3001/TLV320ADC3101 Stereo ADC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320adc3001`, `ti,tlv320adc3101`. The schema description narrows this to: Texas Instruments TLV320ADC3001 and TLV320ADC3101 Stereo ADC https://www.ti.com/product/TLV320ADC3001 https://www.ti.com/product/TLV320ADC3101

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `#gpio-cells`, `gpio-controller`, `reset-gpios`, `clocks`, `ti,dmdin-gpio1`, `ti,dmclk-gpio2`, `ti,micbias1-gpo`, `ti,micbias2-gpo`, `ti,micbias1-vg`, `ti,micbias2-vg`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; conditional branches include 1 `dependencies`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Ricard Wanderlof <ricardw@axis.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320adc3xxx.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adc3xxx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320ADCX140 Quad Channel Analog-to-Digital Converter in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320adc3140`, `ti,tlv320adc5140`, `ti,tlv320adc6140`. The schema description narrows this to: The TLV320ADCX140 are multichannel (4-ch analog recording or 8-ch digital PDM microphones recording), high-performance audio, analog-to-digital converter (ADC) with analog inputs supporting up to 2V RMS. The TLV320ADCX140 family supports line and microphone Inputs, and offers a programmable microphone bias or supply voltage generation. Specifications can be found at: https://www.ti.com/lit/ds/symlink/tlv320adc3140...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `areg-supply`, `avdd-supply`, `iovdd-supply`, `ti,mic-bias-source`, `ti,vref-source`, `ti,pdm-edge-select`, `ti,gpi-config`, `ti,gpio-config`, `ti,asi-tx-drive`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^ti,gpo-config-[1-4]$`.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`; pattern-matched child/property blocks include `^ti,gpo-config-[1-4]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Maintainer metadata routes binding review to Andrew Davis <afd@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320adcx140.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320adcx140.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml

## Purpose
Devicetree binding schema for Texas Instruments TLV320AIC3x Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320aic23`, `ti,tlv320aic3x`, `ti,tlv320aic33`, `ti,tlv320aic3007`, `ti,tlv320aic3106`, `ti,tlv320aic3104`. The schema description narrows this to: TLV320AIC3x are a series of low-power stereo audio codecs with stereo headphone amplifier, as well as multiple inputs and outputs programmable in single-ended or fully differential configurations. The serial control bus supports SPI or I2C protocols, while the serial audio data bus is programmable for I2S, left/right-justified, DSP, or TDM modes. The following pins can be referred in the sound node's audio routing...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `gpio-reset`, `ai3x-gpio-func`, `ai3x-micbias-vg`, `ai3x-ocmv`, `AVDD-supply`, `IOVDD-supply`, `DRVDD-supply`, `DVDD-supply`, `#sound-dai-cells`, `clocks`, `port`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`; conditional branches include 2 `oneOf`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to Jai Luthra <j-luthra@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320aic3x.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320aic3x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml

## Purpose
Devicetree binding schema for Texas Instruments - tlv320aic31xx Codec module in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tlv320aic310x`, `ti,tlv320aic311x`, `ti,tlv320aic3100`, `ti,tlv320aic3110`, `ti,tlv320aic3120`, `ti,tlv320aic3111`, and 2 more compatible strings. The schema description narrows this to: CODEC output pins: * HPL * HPR * SPL, devices with stereo speaker amp * SPR, devices with stereo speaker amp * SPK, devices with mono speaker amp * MICBIAS CODEC input pins: * MIC1LP, devices with ADC * MIC1RP, devices with ADC * MIC1LM, devices with ADC * AIN1, devices without ADC * AIN2, devices without ADC The pins can be used in referring sound node's audio-routing property.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`, `reset-gpios`, `ai31xx-micbias-vg`, `ai31xx-ocmv`, `gpio-reset`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Maintainer metadata routes binding review to Shenghao Ding <shenghao-ding@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `HPVDD-supply`, `SPRVDD-supply`, `SPLVDD-supply`, `AVDD-supply`, `IOVDD-supply`, `DVDD-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tlv320dac3100.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tlv320dac3100.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tpa6130a2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tpa6130a2.yaml

## Purpose
Devicetree binding schema for Texas Instruments - tpa6130a2 Codec module in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,tpa6130a2`, `ti,tpa6140a2`. The schema description narrows this to: Stereo, analog input headphone amplifier

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `Vdd-supply`, `power-gpio`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `Vdd-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Sebastian Reichel <sre@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `Vdd-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,tpa6130a2.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,tpa6130a2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,ts3a227e.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,ts3a227e.yaml

## Purpose
Devicetree binding schema for Texas Instruments TS3A227E Autonomous Audio Accessory Detection and Configuration Switch in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,ts3a227e`. The schema description narrows this to: The TS3A227E detect headsets of 3-ring and 4-ring standards and switches automatically to route the microphone correctly. It also handles key press detection in accordance with the Android audio headset specification v1.0.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `ti,micbias`, `ti,debounce-release-ms`, `ti,debounce-press-ms`, `ti,debounce-insertion-ms`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `interrupts`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Dylan Reid <dgreid@chromium.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,ts3a227e.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,ts3a227e.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,twl4030-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,twl4030-audio.yaml

## Purpose
Devicetree binding schema for Texas Instruments TWL4030-family Audio Module in the Linux ASoC sound subsystem. It documents and validates nodes matched by `ti,twl4030-audio`. The schema description narrows this to: The audio module within the TWL4030-family of companion chips consists of an audio codec and a vibra driver. This binding describes the parent node for these functions.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `codec`, `ti,enable-vibra`, `ti,digimic_delay`, `ti,ramp_delay_value`, `ti,hs_extmute`, `ti,hs_extmute_gpio`, `ti,offset_cncl_path`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`. Maintainer metadata routes binding review to Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/ti,twl4030-audio.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/ti,twl4030-audio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/trivial-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/trivial-codec.yaml

## Purpose
Devicetree binding schema for Trivial Audio Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `adi,ssm2602`, `adi,ssm2603`, `adi,ssm2604`, `adi,ssm3515`, `cirrus,cs4265`, `cirrus,cs4341a`, and 25 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `reset-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Rob Herring <robh@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/trivial-codec.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/trivial-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,arizona.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,arizona.yaml

## Purpose
Devicetree binding schema fragment for Cirrus Logic/Wolfson Microelectronics Arizona class audio SoCs in the Linux ASoC sound subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: These devices are audio SoCs with extensive digital capabilities and a range of analogue I/O. This document lists sound specific bindings, see the primary binding document ../mfd/arizona.yaml

## Important APIs/types/functions
- Schema property keys observed: `#sound-dai-cells`, `wlf,inmode`, `wlf,out-mono`, `wlf,dmic-ref`, `wlf,max-channels-clocked`, `wlf,spk-fmt`, `wlf,spk-mute`, `wlf,out-volume-limit`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s).

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,arizona.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,arizona.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8524.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8524.yaml

## Purpose
Devicetree binding schema for Wolfson WM8524 24-bit 192KHz Stereo DAC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8524`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `#sound-dai-cells`, `wlf,mute-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `wlf,mute-gpios`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `wlf,mute-gpios`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8524.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8524.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8782.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8782.yaml

## Purpose
Devicetree binding schema for Wolfson Microelectromics WM8782 audio CODEC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8782`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `Vdda-supply`, `Vdd-supply`, `wlf,fsampen`, `#sound-dai-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `Vdda-supply`, `Vdd-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `Vdda-supply`, `Vdd-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8782.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8782.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8804.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8804.yaml

## Purpose
Devicetree binding schema for WM8804 audio codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8804`. The schema description narrows this to: This device supports both I2C and SPI (configured with pin strapping on the board).

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `#sound-dai-cells`, `PVDD-supply`, `DVDD-supply`, `wlf,reset-gpio`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `reg`, `compatible`, `PVDD-supply`, `DVDD-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`reg`, `compatible`, `PVDD-supply`, `DVDD-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8804.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8804.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8903.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8903.yaml

## Purpose
Devicetree binding schema for WM8903 audio codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8903`. The schema description narrows this to: This device supports I2C only. Pins on the device (for linking into audio routes): * IN1L * IN1R * IN2L * IN2R * IN3L * IN3R * DMICDAT * HPOUTL * HPOUTR * LINEOUTL * LINEOUTR * LOP * LON * ROP * RON * MICBIAS

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `micdet-cfg`, `micdet-delay`, `gpio-cfg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `compatible`, `reg`, `gpio-controller`, `#gpio-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `gpio-controller`, `#gpio-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8903.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8903.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8940.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8940.yaml

## Purpose
Devicetree binding schema for Wolfson WM8940 Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8940`.

## Important APIs/types/functions
- Schema property keys observed: `#sound-dai-cells`, `compatible`, `reg`, `spi-max-frequency`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `#sound-dai-cells`, `compatible`, `reg`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `#sound-dai-cells`, `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`#sound-dai-cells`, `compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8940.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8940.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8960.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8960.yaml

## Purpose
Devicetree binding schema for Wolfson WM8960 audio codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8960`. The schema description narrows this to: Wolfson WM8960 audio codec Pins on the device (for linking into audio routes): Outputs: * HP_L : Left Headphone/Line Output * HP_R : Right Headphone/Line Output * SPK_LP : Left Speaker Output (Positive) * SPK_LN : Left Speaker Output (Negative) * SPK_RP : Right Speaker Output (Positive) * SPK_RN : Right Speaker Output (Negative) * OUT3 : Mono, Left, Right or buffered midrail output for capless mode Inputs: * LINPU...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`, `AVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `SPKVDD1-supply`, `SPKVDD2-supply`, `wlf,capless`, `wlf,gpio-cfg`, `wlf,hp-cfg`, `wlf,shared-lrclk`, plus 1 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`, `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`, `dai-common.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8960.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8960.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml

## Purpose
Devicetree binding schema for Wolfson WM8962 Ultra-Low Power Stereo CODEC in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8962`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `interrupts`, `#sound-dai-cells`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, `SPKVDD1-supply`, `SPKVDD2-supply`, `spk-mono`, plus 3 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, plus 2 more; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `interrupts`, `#sound-dai-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `audio-graph-port.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD-supply`, `DCVDD-supply`, `MICVDD-supply`, `PLLVDD-supply`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8962.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8962.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8978.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8978.yaml

## Purpose
Devicetree binding schema for Wolfson WM8978 Codec in the Linux ASoC sound subsystem. It documents and validates nodes matched by `wlf,wm8978`.

## Important APIs/types/functions
- Schema property keys observed: `#sound-dai-cells`, `compatible`, `reg`, `spi-max-frequency`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `#sound-dai-cells`, `compatible`, `reg`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `#sound-dai-cells`, `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to patches@opensource.cirrus.com.

## Risks and edge cases
missing required properties (`#sound-dai-cells`, `compatible`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/wlf,wm8978.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/wlf,wm8978.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml

## Purpose
Devicetree binding schema for Xilinx PL audio formatter in the Linux ASoC sound subsystem. It documents and validates nodes matched by `xlnx,audio-formatter-1.0`. The schema description narrows this to: The IP core supports DMA, data formatting(AES<->PCM conversion) of audio samples.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`. Maintainer metadata routes binding review to Vincenzo Frascino <vincenzo.frascino@arm.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xlnx,audio-formatter.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,audio-formatter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,i2s.yaml

## Purpose
Devicetree binding schema for Xilinx I2S PL block in the Linux ASoC sound subsystem. It documents and validates nodes matched by `xlnx,i2s-receiver-1.0`, `xlnx,i2s-transmitter-1.0`. The schema description narrows this to: The IP supports I2S based playback/capture audio.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `xlnx,dwidth`, `xlnx,num-channels`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `xlnx,dwidth`, `xlnx,num-channels`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vincenzo Frascino <vincenzo.frascino@arm.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `xlnx,dwidth`, `xlnx,num-channels`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xlnx,i2s.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,spdif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,spdif.yaml

## Purpose
Devicetree binding schema for Xilinx SPDIF IP in the Linux ASoC sound subsystem. It documents and validates nodes matched by `xlnx,spdif-2.0`. The schema description narrows this to: The IP supports playback and capture of SPDIF audio.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `xlnx,spdif-mode`, `xlnx,aud_clk_i`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vincenzo Frascino <vincenzo.frascino@arm.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xlnx,spdif.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xlnx,spdif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml

## Purpose
Devicetree binding schema for XMOS XVF3500 VocalFusion Voice Processor in the Linux ASoC sound subsystem. It documents and validates nodes matched by `usb20b1,0013`. The schema description narrows this to: The XMOS XVF3500 VocalFusion Voice Processor is a low-latency, 32-bit multicore controller for voice processing. https://www.xmos.com/xvf3500/

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/usb/usb-device.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/usb/usb-device.yaml#`. Maintainer metadata routes binding review to Javier Carrasco <javier.carrasco@wolfvision.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xmos,xvf3500.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml

## Purpose
Devicetree binding schema for Qualcomm SoundWire Controller in the Linux SoundWire subsystem. It documents and validates nodes matched by `qcom,soundwire-v1.3.0`, `qcom,soundwire-v1.5.0`, `qcom,soundwire-v1.5.1`, `qcom,soundwire-v1.6.0`, `qcom,soundwire-v1.7.0`, `qcom,soundwire-v2.0.0`, and 3 more compatible strings. The schema description narrows this to: The Qualcomm SoundWire controller along with its board specific bus parameters.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, `wakeup-source`, `qcom,din-ports`, `qcom,dout-ports`, plus 11 more.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint16-array`, `soundwire-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, plus 2 more; conditional branches include 6 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SoundWire bus schema and Qualcomm or generic SoundWire controller drivers; child peripherals rely on SoundWire addressing and interrupt/clock/reset resources described here. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint16-array`, `soundwire-controller.yaml#`. Maintainer metadata routes binding review to Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Srinivasa Rao Mandadapu <quic_srivasam@quicinc.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#sound-dai-cells`, `#address-cells`, `#size-cells`, plus 2 more) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; DAI phandle cell mismatches surface late as ASoC link creation or probe failures.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=soundwire/qcom,soundwire.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/qcom,soundwire.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml

## Purpose
Devicetree binding schema fragment for SoundWire Controller Common Properties in the Linux SoundWire subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: SoundWire busses can be described with a node for the SoundWire controller device and a set of child nodes for each SoundWire slave on the bus.

## Important APIs/types/functions
- Schema property keys observed: `$nodename`, `#address-cells`, `#size-cells`, `compatible`, `reg`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f],[0-9a-f]$`.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `#address-cells`, `#size-cells`; pattern-matched child/property blocks include `^.*@[0-9a-f],[0-9a-f]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `#address-cells`, `#size-cells`, `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SoundWire bus schema and Qualcomm or generic SoundWire controller drivers; child peripherals rely on SoundWire addressing and interrupt/clock/reset resources described here. Maintainer metadata routes binding review to Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Vinod Koul <vkoul@kernel.org>.

## Risks and edge cases
missing required properties (`#address-cells`, `#size-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=soundwire/soundwire-controller.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml

## Purpose
Devicetree binding schema for Analog Devices AXI SPI Engine Controller in the Linux SPI subsystem. It documents and validates nodes matched by `adi,axi-spi-engine-1.00.a`. The schema description narrows this to: The AXI SPI Engine controller is part of the SPI Engine framework[1] and allows memory mapped access to the SPI Engine control bus. This allows it to be used as a general purpose software driven SPI controller as well as some optional advanced acceleration and offloading capabilities. [1] https://wiki.analog.com/resources/fpga/peripherals/spi_engine

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `trigger-sources`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f]+`.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; pattern-matched child/property blocks include `^.*@[0-9a-f]+`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`. Maintainer metadata routes binding review to Michael Hennerich <Michael.Hennerich@analog.com>, Nuno Sá <nuno.sa@analog.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/adi,axi-spi-engine.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/airoha,en7581-snand.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/airoha,en7581-snand.yaml

## Purpose
Devicetree binding schema for SPI-NAND flash controller for Airoha ARM SoCs in the Linux SPI subsystem. It documents and validates nodes matched by `airoha,en7581-snand`, `airoha,en7523-snand`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Lorenzo Bianconi <lorenzo@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/airoha,en7581-snand.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/airoha,en7581-snand.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun4i-a10-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun4i-a10-spi.yaml

## Purpose
Devicetree binding schema for Allwinner A10 SPI Controller in the Linux SPI subsystem. It documents and validates nodes matched by `allwinner,sun4i-a10-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f]+`.
- External schema APIs: `spi-controller.yaml`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; pattern-matched child/property blocks include `^.*@[0-9a-f]+`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml`. Maintainer metadata routes binding review to Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/allwinner,sun4i-a10-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun4i-a10-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun6i-a31-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun6i-a31-spi.yaml

## Purpose
Devicetree binding schema for Allwinner A31 SPI Controller in the Linux SPI subsystem. It documents and validates nodes matched by `allwinner,sun50i-r329-spi`, `allwinner,sun55i-a523-spi`, `allwinner,sun6i-a31-spi`, `allwinner,sun8i-h3-spi`, `allwinner,sun8i-r40-spi`, `allwinner,sun50i-h6-spi`, and 6 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f]+`.
- External schema APIs: `spi-controller.yaml`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; pattern-matched child/property blocks include `^.*@[0-9a-f]+`; conditional branches include 1 `oneOf`, 1 `if`, 1 `then`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml`. Maintainer metadata routes binding review to Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/allwinner,sun6i-a31-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/allwinner,sun6i-a31-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a1-spifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a1-spifc.yaml

## Purpose
Devicetree binding schema for Amlogic A1 SPI Flash Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,a1-spifc`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `power-domains`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `power-domains`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Martin Kurbanov <mmkurbanov@sberdevices.ru>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,a1-spifc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a1-spifc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml

## Purpose
Devicetree binding schema for SPI flash controller for Amlogic ARM SoCs in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,a4-spifc`. The schema description narrows this to: The Amlogic SPI flash controller is an extended version of the Amlogic NAND flash controller. It supports SPI Nor Flash and SPI NAND Flash(where the Host ECC HW engine could be enabled).

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `amlogic,rx-adj`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Liang Yang <liang.yang@amlogic.com>, Feng Chen <feng.chen@amlogic.com>, Xianwei Zhao <xianwei.zhao@amlogic.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,a4-spifc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spisg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spisg.yaml

## Purpose
Devicetree binding schema for Amlogic SPI Scatter-Gather Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,a4-spisg`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Xianwei Zhao <xianwei.zhao@amlogic.com>, Sunny Luo <sunny.luo@amlogic.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,a4-spisg.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spisg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml

## Purpose
Devicetree binding schema for Amlogic Meson SPI Communication Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,meson-gx-spicc`, `amlogic,meson-axg-spicc`, `amlogic,meson-g12a-spicc`. The schema description narrows this to: The Meson SPICC is a generic SPI controller for general purpose Full-Duplex communications with dedicated 16 words RX/TX PIO FIFOs.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `interrupts`, `reg`, `resets`, `clocks`, `clock-names`, `pinctrl-0`, `pinctrl-1`, `pinctrl-2`, `pinctrl-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 3 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; conditional branches include 2 `if`, 2 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `interrupts`, `reg`, `resets`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Neil Armstrong <neil.armstrong@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,meson-gx-spicc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml

## Purpose
Devicetree binding schema for Amlogic Meson SPI Flash Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,meson6-spifc`, `amlogic,meson-gxbb-spifc`. The schema description narrows this to: The Meson SPIFC is a controller optimized for communication with SPI NOR memories, without DMA support and a 64-byte unified transmit / receive buffer.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Neil Armstrong <neil.armstrong@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,meson6-spifc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml

## Purpose
Devicetree binding schema for Andes ATCSPI200 SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `andestech,qilai-spi`, `andestech,ae350-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `num-cs`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `@[0-9a-f]+$`.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `dmas`, `dma-names`; pattern-matched child/property blocks include `@[0-9a-f]+$`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to CL Wang <cl634@andestech.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `dmas`, `dma-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/andestech,ae350-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/apple,spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/apple,spi.yaml

## Purpose
Devicetree binding schema for Apple ARM SoC SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `apple,t6020-spi`, `apple,t8103-spi`, `apple,t8112-spi`, `apple,t6000-spi`, `apple,spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `interrupts`, `power-domains`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `interrupts`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `interrupts`, `power-domains`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Hector Martin <marcan@marcan.st>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/apple,spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/apple,spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/arm,pl022-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/arm,pl022-peripheral-props.yaml

## Purpose
Devicetree binding schema fragment for Peripheral-specific properties for Arm PL022 SPI controller in the Linux SPI subsystem. It documents reusable node properties rather than a single top-level compatible.

## Important APIs/types/functions
- Schema property keys observed: `pl022,interface`, `pl022,com-mode`, `pl022,rx-level-trig`, `pl022,tx-level-trig`, `pl022,ctrl-len`, `pl022,wait-state`, `pl022,duplex`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are none declared. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Linus Walleij <linusw@kernel.org>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/arm,pl022-peripheral-props.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/arm,pl022-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml

## Purpose
Devicetree binding schema for Aspeed SMC controllers in the Linux SPI subsystem. It documents and validates nodes matched by `aspeed,ast2700-fmc`, `aspeed,ast2700-spi`, `aspeed,ast2600-fmc`, `aspeed,ast2600-spi`, `aspeed,ast2500-fmc`, `aspeed,ast2500-spi`, and 2 more compatible strings. The schema description narrows this to: This binding describes the Aspeed Static Memory Controllers (FMC and SPI) of the AST2400, AST2500, AST2600 and AST2700 SOCs.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Chin-Ting Kuo <chin-ting_kuo@aspeedtech.com>, Cédric Le Goater <clg@kaod.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/aspeed,ast2600-fmc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml

## Purpose
Devicetree binding schema for Atmel SPI device in the Linux SPI subsystem. It documents and validates nodes matched by `atmel,at91rm9200-spi`, `microchip,lan9691-spi`, `microchip,sam9x60-spi`, `microchip,sam9x7-spi`, `microchip,sama7d65-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `dmas`, `dma-names`, `atmel,fifo-size`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Tudor Ambarus <tudor.ambarus@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/atmel,at91rm9200-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,quadspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,quadspi.yaml

## Purpose
Devicetree binding schema for Atmel Quad Serial Peripheral Interface (QSPI) in the Linux SPI subsystem. It documents and validates nodes matched by `atmel,sama5d2-qspi`, `microchip,sam9x60-qspi`, `microchip,sam9x7-ospi`, `microchip,sama7d65-qspi`, `microchip,sama7d65-ospi`, `microchip,sama7g5-qspi`, and 1 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `#address-cells`, `#size-cells`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `#address-cells`, `#size-cells`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Tudor Ambarus <tudor.ambarus@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/atmel,quadspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,quadspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/axiado,ax3000-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/axiado,ax3000-spi.yaml

## Purpose
Devicetree binding schema for Axiado AX3000 SoC SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `axiado,ax3000-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `num-cs`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vladimir Moravcevic <vmoravcevic@axiado.com>, Tzu-Hao Wei <twei@axiado.com>, Swark Yang <syang@axiado.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/axiado,ax3000-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/axiado,ax3000-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-aux-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-aux-spi.yaml

## Purpose
Devicetree binding schema for Broadcom BCM2835 Auxiliary SPI1/2 Controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm2835-aux-spi`. The schema description narrows this to: The BCM2835 contains two forms of SPI master controller. One is known simply as SPI0, and the other as the "Universal SPI Master," which is part of the auxiliary block. This binding applies to the SPI1 and SPI2 auxiliary controllers.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Karan Sanghavi <karansanghvi98@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm2835-aux-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-aux-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-spi.yaml

## Purpose
Devicetree binding schema for Broadcom BCM2835 SPI0 controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm2835-spi`, `brcm,bcm2711-spi`, `brcm,bcm7211-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Florian Fainelli <florian.fainelli@broadcom.com>, Kanak Shilledar <kanakshilledar111@protonmail.com>, Stefan Wahren <wahrenst@gmx.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm2835-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm2835-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml

## Purpose
Devicetree binding schema for Broadcom Broadband SoC High Speed SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm6328-hsspi`, `brcm,bcm47622-hsspi`, `brcm,bcm4908-hsspi`, `brcm,bcm63138-hsspi`, `brcm,bcm63146-hsspi`, `brcm,bcm63148-hsspi`, and 12 more compatible strings. The schema description narrows this to: Broadcom Broadband SoC supports High Speed SPI master controller since the early MIPS based chips such as BCM6328 and BCM63268. This initial rev 1.0 controller was carried over to recent ARM based chips, such as BCM63138, BCM4908 and BCM6858. The old MIPS based chip should continue to use the brcm,bcm6328-hsspi compatible string. The recent ARM based chip is required to use the brcm,bcmbca-hsspi-v1.0 as part of it...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`; conditional branches include 1 `oneOf`, 1 `if`, 1 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to William Zhang <william.zhang@broadcom.com>, Kursad Oney <kursad.oney@broadcom.com>, Jonas Gorski <jonas.gorski@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm63xx-hsspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml

## Purpose
Devicetree binding schema for Broadcom BCM6348/BCM6358 SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm6368-spi`, `brcm,bcm6362-spi`, `brcm,bcm63268-spi`, `brcm,bcm6358-spi`, `brcm,bcm6348-spi`. The schema description narrows this to: Broadcom "Low Speed" SPI controller found in many older MIPS based Broadband SoCs. This controller has a limitation that can not keep the chip select line active between the SPI transfers within the same SPI message. This can terminate the transaction to some SPI devices prematurely. The issue can be worked around by the controller's prepend mode.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Jonas Gorski <jonas.gorski@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm63xx-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml

## Purpose
Devicetree binding schema for Broadcom SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,spi-bcm7425-qspi`, `brcm,spi-bcm7429-qspi`, `brcm,spi-bcm7435-qspi`, `brcm,spi-bcm7445-qspi`, `brcm,spi-bcm7216-qspi`, `brcm,spi-bcm7278-qspi`, and 5 more compatible strings. The schema description narrows this to: The Broadcom SPI controller is a SPI master found on various SOCs, including BRCMSTB (BCM7XXX), Cygnus, NSP and NS2. The Broadcom Master SPI hw IP consists of: MSPI : SPI master controller can read and write to a SPI slave device BSPI : Broadcom SPI in combination with the MSPI hw IP provides acceleration for flash reads and be configured to do single, double, quad lane io with 3-byte and 4-byte addressing support...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `native-endian`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `reg`, `reg-names`, `interrupts`, `interrupt-names`; conditional branches include 2 `oneOf`; 4 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/flag`. Maintainer metadata routes binding review to Kamal Dasu <kdasu.kdev@gmail.com>, Rafał Miłecki <rafal@milecki.pl>.

## Risks and edge cases
missing required properties (`reg`, `reg-names`, `interrupts`, `interrupt-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,spi-bcm-qspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 4 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml

## Purpose
Devicetree binding schema fragment for Peripheral-specific properties for the Cadence QSPI controller. in the Linux SPI subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: See spi-peripheral-props.yaml for more info.

## Important APIs/types/functions
- Schema property keys observed: `cdns,read-delay`, `cdns,tshsl-ns`, `cdns,tsd2d-ns`, `cdns,tchsh-ns`, `cdns,tslch-ns`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are none declared. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vaishnav Achath <vaishnav.a@ti.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cdns,qspi-nor-peripheral-props.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml

## Purpose
Devicetree binding schema for Cadence Quad/Octal SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `amd,pensando-elba-qspi`, `amd,versal2-ospi`, `intel,lgm-qspi`, `intel,socfpga-qspi`, `mobileye,eyeq5-ospi`, `starfive,jh7110-qspi`, and 6 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `cdns,fifo-depth`, `cdns,fifo-width`, `cdns,trigger-address`, `cdns,is-decoded-cs`, `cdns,rclk-en`, `power-domains`, `resets`, `reset-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^flash@[0-9a-f]+$`.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `cdns,qspi-nor-peripheral-props.yaml`.

## Control flow
The schema control flow is declarative: validation first composes 5 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `#address-cells`, `#size-cells`; pattern-matched child/property blocks include `^flash@[0-9a-f]+$`; conditional branches include 2 `oneOf`, 4 `if`, 4 `then`, 3 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `cdns,qspi-nor-peripheral-props.yaml`. Maintainer metadata routes binding review to Vaishnav Achath <vaishnav.a@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `#address-cells`, `#size-cells`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cdns,qspi-nor.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,xspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,xspi.yaml

## Purpose
Devicetree binding schema for Cadence XSPI Controller in the Linux SPI subsystem. It documents and validates nodes matched by `cdns,xspi-nor`, `marvell,cn10-xspi-nor`. The schema description narrows this to: The XSPI controller allows SPI protocol communication in single, dual, quad or octal wire transmission modes for read/write access to slaves such as SPI-NOR flash.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`; conditional branches include 1 `if`, 1 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Parshuram Thombare <pthombar@cadence.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cdns,xspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,xspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cirrus,ep9301-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cirrus,ep9301-spi.yaml

## Purpose
Devicetree binding schema for EP93xx SoC SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `cirrus,ep9301-spi`, `cirrus,ep9302-spi`, `cirrus,ep9307-spi`, `cirrus,ep9312-spi`, `cirrus,ep9315-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Alexander Sverdlin <alexander.sverdlin@gmail.com>, Nikita Shubin <nikita.shubin@maquefel.me>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cirrus,ep9301-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cirrus,ep9301-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/faraday,ftssp010.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/faraday,ftssp010.yaml

## Purpose
Devicetree binding schema for Faraday FTSSP010 SPI Controller in the Linux SPI subsystem. It documents and validates nodes matched by `faraday,ftssp010`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `interrupts`, `reg`, `cs-gpios`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `interrupts`, `reg`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `interrupts`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Linus Walleij <linusw@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `interrupts`, `reg`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/faraday,ftssp010.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/faraday,ftssp010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi-peripheral-props.yaml

## Purpose
Devicetree binding schema fragment for Peripheral-specific properties for Freescale DSPI controller in the Linux SPI subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: See spi-peripheral-props.yaml for more info.

## Important APIs/types/functions
- Schema property keys observed: `fsl,spi-cs-sck-delay`, `fsl,spi-sck-cs-delay`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are none declared. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vladimir Oltean <olteanv@gmail.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,dspi-peripheral-props.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi.yaml

## Purpose
Devicetree binding schema for ARM Freescale DSPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,vf610-dspi`, `fsl,ls1021a-v1.0-dspi`, `fsl,ls1012a-dspi`, `fsl,ls1028a-dspi`, `fsl,ls1043a-dspi`, `fsl,ls1046a-dspi`, and 6 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `spi-num-chipselects`, `big-endian`, `bus-num`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `spi-num-chipselects`; conditional branches include 1 `oneOf`; 2 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`. Maintainer metadata routes binding review to Frank Li <Frank.Li@nxp.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `spi-num-chipselects`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,dspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 2 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,dspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml

## Purpose
Devicetree binding schema for Freescale eSPI (Enhanced Serial Peripheral Interface) controller in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,mpc8536-espi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`, `fsl,csbef`, `fsl,csaft`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`. Maintainer metadata routes binding review to J. Neuschäfer <j.ne@posteo.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,espi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi-fsl-qspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi-fsl-qspi.yaml

## Purpose
Devicetree binding schema for Freescale Quad Serial Peripheral Interface (QuadSPI) in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,vf610-qspi`, `fsl,imx6sx-qspi`, `fsl,imx7d-qspi`, `fsl,imx6ul-qspi`, `fsl,ls1021a-qspi`, `fsl,ls2080a-qspi`, and 3 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`; conditional branches include 1 `oneOf`, 1 `if`, 1 `then`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `resets`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Han Xu <han.xu@nxp.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,spi-fsl-qspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi-fsl-qspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi.yaml

## Purpose
Devicetree binding schema for Freescale SPI (Serial Peripheral Interface) controller in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,spi`, `aeroflexgaisler,spictrl`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `cell-index`, `mode`, `interrupts`, `clock-frequency`, `cs-gpios`, `fsl,spisel_boot`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `mode`, `interrupts`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `spi-controller.yaml#`. Maintainer metadata routes binding review to J. Neuschäfer <j.ne@posteo.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `mode`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml

## Purpose
Devicetree binding schema for Freescale (Enhanced) Configurable Serial Peripheral Interface (CSPI/eCSPI) for i.MX in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,imx1-cspi`, `fsl,imx21-cspi`, `fsl,imx27-cspi`, `fsl,imx31-cspi`, `fsl,imx35-cspi`, `fsl,imx51-ecspi`, and 16 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `fsl,spi-rdy-drctl`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Shawn Guo <shawnguo@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl-imx-cspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/hpe,gxp-spifi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/hpe,gxp-spifi.yaml

## Purpose
Devicetree binding schema for HPE GXP spi controller flash interface in the Linux SPI subsystem. It documents and validates nodes matched by `hpe,gxp-spifi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Nick Hawkins <nick.hawkins@hpe.com>, Jean-Marie Verdun <verdun@hpe.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/hpe,gxp-spifi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/hpe,gxp-spifi.yaml -->
