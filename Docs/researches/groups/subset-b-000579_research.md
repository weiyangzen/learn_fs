# Research: subset-b-000579

Grouped research for Linux devicetree IIO binding schemas from the Ceph client source snapshot. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports. The source files were parsed completely as YAML and summarized from their schema contracts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml

### Purpose
`adi,adf4350.yaml` defines the devicetree schema for Analog Devices ADF4350/ADF4351 wideband synthesizer. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Michael Hennerich <michael.hennerich@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,adf4350.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adf4350`, `adi,adf4351`. Top-level required properties are `compatible`, `reg`, `clocks`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..20000000); `clocks` (max 1 item(s); Clock to provide CLKIN reference clock signal.); `clock-names` (const `clkin`); `#clock-cells` (const `0`); `clock-output-names` (max 1 item(s)); `gpios` (max 1 item(s); Lock detect GPIO.); `adi,channel-spacing` (ref `/schemas/types.yaml#/definitions/uint32`; Channel spacing in Hz (influences MODULUS).); `adi,power-up-frequency` (ref `/schemas/types.yaml#/definitions/uint32`; If set the PLL tunes to this frequency (in Hz) on driver probe.); `adi,reference-div-factor` (ref `/schemas/types.yaml#/definitions/uint32`; If set the driver skips dynamic calculation and uses this default value instead.); `adi,reference-doubler-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables reference doubler.); `adi,reference-div2-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables reference divider.); `adi,phase-detector-polarity-positive-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables positive phase detector polarity. Default negative.); `adi,lock-detect-precision-6ns-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables 6ns lock detect precision. Default = 10ns.); `adi,lock-detect-function-integer-n-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables lock detect for integer-N mode. Default = factional-N mode.); `adi,charge-pump-current` (ref `/schemas/types.yaml#/definitions/uint32`; Charge pump current in mA. Default = 2500mA.); `adi,muxout-select` (range 0..6; ref `/schemas/types.yaml#/definitions/uint32`; On chip multiplexer output selection. Valid values for the multiplexer output are: 0: Three-State Output (default) 1:...); `adi,low-spur-mode-enable` (ref `/schemas/types.yaml#/definitions/flag`; Enables low spur mode. Default = Low noise mode.); plus 11 additional property schema(s).
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#clock-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; clock framework: `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,channel-spacing`, `adi,power-up-frequency`, `adi,reference-div-factor`, `adi,reference-doubler-enable`, `adi,reference-div2-enable`, `adi,phase-detector-polarity-positive-enable`, `adi,lock-detect-precision-6ns-enable`, `adi,lock-detect-function-integer-n-enable`, ... encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4350.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml

### Purpose
`adi,adf4377.yaml` defines the devicetree schema for ADF4377 Microwave Wideband Synthesizer with Integrated VCO. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The ADF4377 is a high performance, ultralow jitter, dual output integer-N phased locked loop (PLL) with integrated voltage controlled oscillator (VCO) ideally suited for data converter and mixed signal front end (MxFE) clock applications. https://www.analog.com/en/products/adf4377.html https://www.analog.com/en/products/adf4378.html Maintainer coverage is Antoniu Miclaus <antoniu.miclaus@analog.com>, Dragos Bogdan <dragos.bogdan@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,adf4377.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adf4377`, `adi,adf4378`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..10000000); `clocks` (max 1 item(s)); `clock-names` (External clock that provides reference input frequency.); `#clock-cells` (const `0`); `clock-output-names` (max 1 item(s)); `chip-enable-gpios` (max 1 item(s); GPIO that controls the Chip Enable Pin.); `clk1-enable-gpios` (max 1 item(s); GPIO that controls the Enable Clock 1 Output Buffer Pin.); `clk2-enable-gpios` (max 1 item(s); GPIO that controls the Enable Clock 2 Output Buffer Pin.); `adi,muxout-select` (enum `high_z`, `lock_detect`, `muxout_low`, `f_div_rclk_2`, `f_div_nclk_2`, `muxout_high`; On chip multiplexer output selection. high_z - MUXOUT Pin set to high-Z. lock_detect - MUXOUT Pin set to lock detecto...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#clock-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 1 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; clock framework: `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,muxout-select` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adf4377.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml

### Purpose
`adi,admfm2000.yaml` defines the devicetree schema for ADMFM2000 Dual Microwave Down Converter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Dual microwave down converter module with input RF and LO frequency ranges from 0.5 to 32 GHz and an output IF frequency range from 0.1 to 8 GHz. It consists of a LNA, mixer, IF filter, DSA, and IF amplifier for each down conversion path. Maintainer coverage is Kim Seer Paller <kimseer.paller@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,admfm2000.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,admfm2000`. Top-level required properties are `compatible`. Important property contracts include: `#address-cells` (const `1`); `#size-cells` (const `0`)
Child-node API is expressed through `patternProperties`: `^channel@[0-1]$` (Represents a channel of the device.); required `reg`, `switch-gpios`, `attenuation-gpios`.
Local reusable definitions are none. Provider or bus cell contracts are `#address-cells` (const `1`); `#size-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Nested child-node schemas add risk because missing `#address-cells`, `#size-cells`, `reg`, or phandle links can pass local review but fail dtbs_check for real boards. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml

### Purpose
`adi,admv1013.yaml` defines the devicetree schema for ADMV1013 Microwave Upconverter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Wideband, microwave upconverter optimized for point to point microwave radio designs operating in the 24 GHz to 44 GHz frequency range. https://www.analog.com/en/products/admv1013.html Maintainer coverage is Antoniu Miclaus <antoniu.miclaus@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,admv1013.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,admv1013`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`, `vcm-supply`, `vcc-drv-supply`, `vcc2-drv-supply`, `vcc-vva-supply`, `vcc-amp1-supply`, `vcc-amp2-supply`, `vcc-env-supply`, `vcc-bg-supply`, `vcc-bg2-supply`, `vcc-mixer-supply`, `vcc-quad-supply`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..1000000); `clocks` (min 1 item(s); Definition of the external clock.); `clock-names`; `vcm-supply` (Analog voltage regulator.); `vcc-drv-supply` (RF Driver voltage regulator.); `vcc2-drv-supply` (RF predriver voltage regulator.); `vcc-vva-supply` (VVA Control Circuit voltage regulator.); `vcc-amp1-supply` (RF Amplifier 1 voltage regulator.); `vcc-amp2-supply` (RF Amplifier 2 voltage regulator.); `vcc-env-supply` (Envelope Detector voltage regulator.); `vcc-bg-supply` (Mixer Chip Band Gap Circuit voltage regulator.); `vcc-bg2-supply` (VGA Chip Band Gap Circuit voltage regulator.); `vcc-mixer-supply` (Mixer voltage regulator.); `vcc-quad-supply` (Quadruppler voltage regulator.); `adi,detector-enable` (type `boolean`; Enable the Envelope Detector available at output pins VENV_P and VENV_N. Disable to reduce power consumption.); `adi,input-mode` (enum `iq`, `if`; Select the input mode. iq - in-phase quadrature (I/Q) input if - complex intermediate frequency (IF) input); `adi,quad-se-mode` (enum `se-neg`, `se-pos`, `diff`; Switch the LO path from differential to single-ended operation. se-neg - Single-Ended Mode, Negative Side Disabled. s...); plus 1 additional property schema(s).
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#clock-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; regulator supplies: `vcm-supply`, `vcc-drv-supply`, `vcc2-drv-supply`, `vcc-vva-supply`, `vcc-amp1-supply`; clock framework: `clocks`, `clock-names`, `#clock-cells`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,detector-enable`, `adi,input-mode`, `adi,quad-se-mode` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1013.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml

### Purpose
`adi,admv1014.yaml` defines the devicetree schema for ADMV1014 Microwave Downconverter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Wideband, microwave downconverter optimized for point to point microwave radio designs operating in the 24 GHz to 44 GHz frequency range. https://www.analog.com/en/products/admv1014.html Maintainer coverage is Antoniu Miclaus <antoniu.miclaus@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,admv1014.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,admv1014`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`, `vcm-supply`, `vcc-if-bb-supply`, `vcc-vga-supply`, `vcc-vva-supply`, `vcc-lna-3p3-supply`, `vcc-lna-1p5-supply`, `vcc-bg-supply`, `vcc-quad-supply`, `vcc-mixer-supply`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..1000000); `clocks` (max 1 item(s)); `clock-names` (External clock that provides the Local Oscillator input.); `vcm-supply` (Common-mode voltage regulator.); `vcc-if-bb-supply` (BB and IF supply voltage regulator.); `vcc-vga-supply` (RF Amplifier supply voltage regulator.); `vcc-vva-supply` (VVA Control Circuit supply voltage regulator.); `vcc-lna-3p3-supply` (Low Noise Amplifier 3.3V supply voltage regulator.); `vcc-lna-1p5-supply` (Low Noise Amplifier 1.5V supply voltage regulator.); `vcc-bg-supply` (Band Gap Circuit supply voltage regulator.); `vcc-quad-supply` (Quadruple supply voltage regulator.); `vcc-mixer-supply` (Mixer supply voltage regulator.); `adi,input-mode` (enum `iq`, `if`; Select the input mode. iq - in-phase quadrature (I/Q) input if - complex intermediate frequency (IF) input); `adi,detector-enable` (type `boolean`; Digital Rx Detector Enable. The Square Law Detector output is available at output pin VDET.); `adi,p1db-compensation-enable` (type `boolean`; Turn on bits to optimize P1dB.); `adi,quad-se-mode` (enum `se-neg`, `se-pos`, `diff`; Switch the LO path from differential to single-ended operation. se-neg - Single-Ended Mode, Negative Side Disabled. s...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; regulator supplies: `vcm-supply`, `vcc-if-bb-supply`, `vcc-vga-supply`, `vcc-vva-supply`, `vcc-lna-3p3-supply`; clock framework: `clocks`, `clock-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,input-mode`, `adi,detector-enable`, `adi,p1db-compensation-enable`, `adi,quad-se-mode` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv1014.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml

### Purpose
`adi,admv4420.yaml` defines the devicetree schema for ADMV4420 K Band Downconverter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The ADMV4420 is a highly integrated, double balanced, active mixer with an integrated fractional-N synthesizer, ideally suited for next generation K band satellite communications Maintainer coverage is Nuno Sa <nuno.sa@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,admv4420.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,admv4420`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..1000000); `adi,lo-freq-khz` (ref `/schemas/types.yaml#/definitions/uint32`; LO Frequency); `adi,ref-ext-single-ended-en` (type `boolean`; External reference selected.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,lo-freq-khz`, `adi,ref-ext-single-ended-en` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admv4420.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml

### Purpose
`adi,adrf6780.yaml` defines the devicetree schema for ADRF6780 Microwave Upconverter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Wideband, microwave upconverter optimized for point to point microwave radio designs operating in the 5.9 GHz to 23.6 GHz frequency range. https://www.analog.com/en/products/adrf6780.html Maintainer coverage is Antoniu Miclaus <antoniu.miclaus@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,adrf6780.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adrf6780`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..1000000); `clocks` (min 1 item(s); Definition of the external clock.); `clock-names`; `clock-output-names` (max 1 item(s)); `adi,vga-buff-en` (type `boolean`; RF Variable Gain Amplifier Buffer Enable. Gain is controlled by the voltage on the VATT pin.); `adi,lo-buff-en` (type `boolean`; Local Oscillator Amplifier Enable. Disable to put the part in a power down state.); `adi,if-mode-en` (type `boolean`; Intermediate Frequency Mode Enable. Either IF Mode or I/Q Mode can be enabled at a time.); `adi,iq-mode-en` (type `boolean`; I/Q Mode Enable. Either IF Mode or I/Q Mode can be enabled at a time.); `adi,lo-x2-en` (type `boolean`; Double the Local Oscillator output frequency from the Local Oscillator Input Frequency. Either LOx1 or LOx2 can be en...); `adi,lo-ppf-en` (type `boolean`; Local Oscillator input frequency equal to the Local Oscillator output frequency (LO x1). Either LOx1 or LOx2 can be e...); `adi,lo-en` (type `boolean`; Enable additional cirtuitry in the LO chain. Disable to put the part in a power down state.); `adi,uc-bias-en` (type `boolean`; Enable all bias circuitry thourghout the entire part. Disable to put the part in a power down state.); `adi,lo-sideband` (type `boolean`; Switch to the Lower LO Sideband. By default the Upper LO sideband is enabled.); `adi,vdet-out-en` (type `boolean`; VDET Output Select Enable. Expose the RF detector output to the VDET external pin.); `#clock-cells` (const `0`)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#clock-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; clock framework: `clocks`, `clock-names`, `clock-output-names`, `#clock-cells`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,vga-buff-en`, `adi,lo-buff-en`, `adi,if-mode-en`, `adi,iq-mode-en`, `adi,lo-x2-en`, `adi,lo-ppf-en`, `adi,lo-en`, `adi,uc-bias-en`, ... encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,adrf6780.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml

### Purpose
`adi,adxrs290.yaml` defines the devicetree schema for Analog Devices ADXRS290 Dual-Axis MEMS Gyroscope. It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Bindings for the Analog Devices ADXRS290 dual-axis MEMS gyroscope device. https://www.analog.com/media/en/technical-documentation/data-sheets/ADXRS290.pdf Maintainer coverage is Nishant Malpani <nish.malpani25@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/adi,adxrs290.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adxrs290`. Top-level required properties are `compatible`, `reg`, `spi-max-frequency`, `spi-cpol`, `spi-cpha`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..5000000); `spi-cpol` allowed with common binding semantics; `spi-cpha` allowed with common binding semantics; `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/adi,adxrs290.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml

### Purpose
`bosch,bmg160.yaml` defines the devicetree schema for Bosch BMG160 triaxial rotation sensor (gyroscope). It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is H. Nikolaus Schaller <hns@goldelico.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/bosch,bmg160.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmg160`, `bosch,bmi055_gyro`, `bosch,bmi088_gyro`, `bosch,bmx055-gyro`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `spi-max-frequency` (range ..10000000); `interrupts` (1-2 item(s); Should be configured with type IRQ_TYPE_EDGE_RISING. If two interrupts are provided, expected order is INT1 and INT2.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/bosch,bmg160.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml

### Purpose
`invensense,itg3200.yaml` defines the devicetree schema for Invensense ITG-3200 Gyroscope. It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Triple-axis, digital output gyroscope with a three 16-bit analog-to-digital converters (ADCs) for digitizing the gyro outputs, a user-selectable internal low-pass filter bandwidth, and a Fast-Mode I2C. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/invensense,itg3200.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,itg3200`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vlogic-supply` allowed with common binding semantics; `interrupts` (max 1 item(s)); `mount-matrix` (an optional 3x3 mounting rotation matrix.); `clocks` (max 1 item(s)); `clock-names`
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vlogic-supply`; clock framework: `clocks`, `clock-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,itg3200.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml

### Purpose
`invensense,mpu3050.yaml` defines the devicetree schema for Invensense MPU-3050 Gyroscope. It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/invensense,mpu3050.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,mpu3050`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vlogic-supply` allowed with common binding semantics; `interrupts` (max 1 item(s); Interrupt mapping for the trigger interrupt from the internal oscillator.); `mount-matrix` allowed with common binding semantics; `i2c-gate` (ref `/schemas/i2c/i2c-controller.yaml`; The MPU-3050 will pass through and forward the I2C signals from the incoming I2C bus, alternatively drive traffic to...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/i2c/i2c-controller.yaml`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vlogic-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml

### Purpose
`nxp,fxas21002c.yaml` defines the devicetree schema for NXP FXAS21002C Gyroscope. It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: 3 axis digital gyroscope device with an I2C and SPI interface. http://www.nxp.com/products/sensors/gyroscopes/3-axis-digital-gyroscope:FXAS21002C Maintainer coverage is Rui Miguel Silva <rmfrfs@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/nxp,fxas21002c.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `nxp,fxas21002c`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor); `vddio-supply` (Regulator that provides power to the bus); `reset-gpios` (max 1 item(s); GPIO connected to reset); `interrupts` (1-2 item(s); Either interrupt may be triggered on rising or falling edges.); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`; the interrupt/data ready line will be configured as open drain, which is useful if several sensors share the same int...); `spi-max-frequency` (range ..2000000)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/nxp,fxas21002c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml

### Purpose
`maxim,max30100.yaml` defines the devicetree schema for Maxim MAX30100 heart rate and pulse oximeter sensor. It is an IIO health binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Matt Ranostay <matt.ranostay@konsulko.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/health/maxim,max30100.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max30100`. Top-level required properties are `compatible`, `reg`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Connected to ADC_RDY pin.); `maxim,led-current-microamp` (2-2 item(s); LED current whilst the engine is running. First indexed value is the configuration for the RED LED, and second value...); `maxim,pulse-width-us` (enum `200`, `400`, `800`, `1600`; default `1600`; LED pulse width in microseconds. Appropriate pulse width depends on factors such as optical window absorption, LED-to...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO health drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `maxim,led-current-microamp`, `maxim,pulse-width-us` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30100.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml

### Purpose
`maxim,max30102.yaml` defines the devicetree schema for Maxim MAX30101/2 heart rate and pulse oximeter and MAX30105 particle-sensor. It is an IIO health binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Matt Ranostay <matt.ranostay@konsulko.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/health/maxim,max30102.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max30102`, `maxim,max30105`, `maxim,max30101`. Top-level required properties are `compatible`, `reg`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Connected to ADC_RDY pin.); `maxim,red-led-current-microamp` (range 0..50800; RED LED current. Each step is approximately 200 microamps.); `maxim,ir-led-current-microamp` (range 0..50800; IR LED current. Each step is approximately 200 microamps.); `maxim,green-led-current-microamp` (range 0..50800; Green LED current. Each step is approximately 200 microamps.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 1 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO health drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `maxim,red-led-current-microamp`, `maxim,ir-led-current-microamp`, `maxim,green-led-current-microamp` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/maxim,max30102.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml

### Purpose
`ti,afe4403.yaml` defines the devicetree schema for Texas Instruments AFE4403 Heart rate and Pulse Oximeter. It is an IIO health binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/health/ti,afe4403.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,afe4403`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `tx-supply` (Supply to transmitting LEDs.); `interrupts` (max 1 item(s); Connected to ADC_RDY pin.); `reset-gpios` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable; regulator supplies: `tx-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO health drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4403.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml

### Purpose
`ti,afe4404.yaml` defines the devicetree schema for Texas Instruments AFE4404 Heart rate and Pulse Oximeter. It is an IIO health binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/health/ti,afe4404.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,afe4404`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `tx-supply` (Supply to transmitting LEDs.); `interrupts` (max 1 item(s); Connected to ADC_RDY pin.); `reset-gpios` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `tx-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO health drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/health/ti,afe4404.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml

### Purpose
`dht11.yaml` defines the devicetree schema for DHT11 humidity + temperature sensor. It is an IIO humidity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: A simple and low cost module providing a non standard single GPIO based interface. It is believed the part is made by aosong but don't have absolute confirmation of this, or what the aosong part number is. Maintainer coverage is Harald Geyer <harald@ccbib.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/humidity/dht11.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `dht11`. Top-level required properties are `compatible`, `gpios`. Important property contracts include: `reg` (max 1 item(s)); `gpios` (max 1 item(s); Single, interrupt capable, GPIO used to communicate with the device.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO humidity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/dht11.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml

### Purpose
`sciosense,ens210.yaml` defines the devicetree schema for ScioSense ENS210 temperature and humidity sensor. It is an IIO humidity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Temperature and Humidity sensor. Datasheet: https://www.sciosense.com/wp-content/uploads/2024/04/ENS21x-Datasheet.pdf https://www.sciosense.com/wp-content/uploads/2023/12/ENS210-Datasheet.pdf Maintainer coverage is Joshua Felmeden <jfelmeden@thegoodpenguin.co.uk>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/humidity/sciosense,ens210.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `sciosense,ens210a`, `sciosense,ens211`, `sciosense,ens212`, `sciosense,ens213a`, `sciosense,ens215`, `sciosense,ens210`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO humidity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/sciosense,ens210.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml

### Purpose
`st,hts221.yaml` defines the devicetree schema for HTS221 STM humidity + temperature sensor. It is an IIO humidity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Humidity and temperature sensor with I2C interface and data ready interrupt. Maintainer coverage is Lorenzo Bianconi <lorenzo@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/humidity/st,hts221.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,hts221`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `drive-open-drain` (type `boolean`; The interrupt/data ready line will be configured as open drain, which is useful if several sensors share the same int...); `vdd-supply` allowed with common binding semantics; `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO humidity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/st,hts221.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml

### Purpose
`ti,hdc2010.yaml` defines the devicetree schema for HDC2010/HDC2080 humidity and temperature iio sensors. It is an IIO humidity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Relative humidity and temperature sensors on I2C bus Datasheets are available at: http://www.ti.com/product/HDC2010/datasheet http://www.ti.com/product/HDC2080/datasheet Maintainer coverage is Eugene Zaikonnikov <ez@norophonic.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/humidity/ti,hdc2010.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,hdc2010`, `ti,hdc2080`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `vdd-supply` allowed with common binding semantics; `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO humidity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc2010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml

### Purpose
`ti,hdc3020.yaml` defines the devicetree schema for HDC3020/HDC3021/HDC3022 humidity and temperature iio sensors. It is an IIO humidity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://www.ti.com/lit/ds/symlink/hdc3020.pdf The HDC302x is an integrated capacitive based relative humidity (RH) and temperature sensor. Maintainer coverage is Li peiyu <579lpy@gmail.com>, Javier Carrasco <javier.carrasco.cruz@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/humidity/ti,hdc3020.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,hdc3021`, `ti,hdc3022`, `ti,hdc3020`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `reg` (max 1 item(s)); `reset-gpios` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO humidity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/humidity/ti,hdc3020.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml

### Purpose
`adi,ad5933.yaml` defines the devicetree schema for Analog Devices AD5933/AD5934 Impedance Converter, Network Analyzer. It is an IIO impedance analyzer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://www.analog.com/media/en/technical-documentation/data-sheets/AD5933.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/AD5934.pdf Maintainer coverage is Marcelo Schmitt <marcelo.schmitt1@gmail.com>, Gabriel Capella <gabriel@capella.pro>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/impedance-analyzer/adi,ad5933.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,ad5933`, `adi,ad5934`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` (The regulator supply for DVDD, AVDD1 and AVDD2 when they are connected together. Used to calculate voltage scaling of...); `clocks` (max 1 item(s)); `clock-names` (const `mclk`)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`; clock framework: `clocks`, `clock-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO impedance analyzer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/impedance-analyzer/adi,ad5933.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml

### Purpose
`adi,adis16460.yaml` defines the devicetree schema for Analog Devices ADIS16460 and similar IMUs. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Analog Devices ADIS16460 and similar IMUs https://www.analog.com/media/en/technical-documentation/data-sheets/ADIS16460.pdf Maintainer coverage is Dragos Bogdan <dragos.bogdan@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/adi,adis16460.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adis16460`. Top-level required properties are `compatible`, `reg`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `spi-cpha` allowed with common binding semantics; `spi-cpol` allowed with common binding semantics; `spi-cs-inactive-delay-ns` (range 16000..; default `16000`); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16460.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml

### Purpose
`adi,adis16475.yaml` defines the devicetree schema for Analog Devices ADIS16475 and similar IMUs. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Analog Devices ADIS16475 and similar IMUs https://www.analog.com/media/en/technical-documentation/data-sheets/ADIS16475.pdf Maintainer coverage is Nuno Sa <nuno.sa@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/adi,adis16475.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adis16475-1`, `adi,adis16475-2`, `adi,adis16475-3`, `adi,adis16477-1`, `adi,adis16477-2`, `adi,adis16477-3`, `adi,adis16470`, `adi,adis16465-1`, `adi,adis16465-2`, `adi,adis16465-3`, `adi,adis16467-1`, `adi,adis16467-2`, `adi,adis16467-3`, `adi,adis16500`, `adi,adis16501`, `adi,adis16505-1`, `adi,adis16505-2`, `adi,adis16505-3`, `adi,adis16507-1`, `adi,adis16507-2`, `adi,adis16507-3`, `adi,adis16575-2`, `adi,adis16575-3`, `adi,adis16576-2`, `adi,adis16576-3`, `adi,adis16577-2`, `adi,adis16577-3`. Top-level required properties are `compatible`, `reg`, `interrupts`, `spi-cpha`, `spi-cpol`. Important property contracts include: `reg` (max 1 item(s)); `spi-cpha` allowed with common binding semantics; `spi-cpol` allowed with common binding semantics; `spi-max-frequency` (range ..2000000); `spi-cs-inactive-delay-ns` (range 16000..; default `16000`); `interrupts` (max 1 item(s)); `clocks` (max 1 item(s)); `reset-gpios` (max 1 item(s); Must be the device tree identifier of the RESET pin. If specified, it will be asserted during driver probe. As the li...); `adi,sync-mode` (range 0..3; ref `/schemas/types.yaml#/definitions/uint32`; Configures the device SYNC pin. The following modes are supported 0 - output_sync 1 - direct_sync 2 - scaled_sync 3 -...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 4 top-level `allOf` entry(s), 3 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable; clock framework: `clocks`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,sync-mode` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16475.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml

### Purpose
`adi,adis16480.yaml` defines the devicetree schema for Analog Devices ADIS16480 and similar IMUs. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Marcelo Schmitt <marcelo.schmitt@analog.com>, Nuno Sa <nuno.sa@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/adi,adis16480.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adis16375`, `adi,adis16480`, `adi,adis16485`, `adi,adis16486`, `adi,adis16488`, `adi,adis16489`, `adi,adis16490`, `adi,adis16495-1`, `adi,adis16495-2`, `adi,adis16495-3`, `adi,adis16497-1`, `adi,adis16497-2`, `adi,adis16497-3`, `adi,adis16545-1`, `adi,adis16545-2`, `adi,adis16545-3`, `adi,adis16547-1`, `adi,adis16547-2`, `adi,adis16547-3`, `adi,adis16487`. Top-level required properties are `compatible`, `reg`, `interrupts`, `spi-cpha`, `spi-cpol`, `spi-max-frequency`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s); Accepted interrupt types are: * IRQ_TYPE_EDGE_RISING * IRQ_TYPE_EDGE_FALLING); `interrupt-names` (1-2 item(s); Default if not supplied is DIO1.); `spi-cpha` allowed with common binding semantics; `spi-cpol` allowed with common binding semantics; `reset-gpios` (max 1 item(s); Connected to RESET pin which is active low.); `clocks` (max 1 item(s); If not provided, then the internal clock is used.); `clock-names` (enum `sync`, `pps`; sync: In sync mode, the internal clock is disabled and the frequency of the external clock signal establishes therate...); `adi,ext-clk-pin` (enum `DIO1`, `DIO2`, `DIO3`, `DIO4`; ref `/schemas/types.yaml#/definitions/string`; The DIOx line to be used as an external clock input. Each DIOx pin supports only one function at a time (data ready l...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/string`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable; clock framework: `clocks`, `clock-names`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,ext-clk-pin` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16480.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml

### Purpose
`adi,adis16550.yaml` defines the devicetree schema for Analog Devices ADIS16550 and similar IMUs. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Nuno Sa <nuno.sa@analog.com>, Ramona Gradinariu <ramona.gradinariu@analog.com>, Antoniu Miclaus <antoniu.miclaus@analog.com>, Robert Budai <robert.budai@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/adi,adis16550.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adis16550`. Top-level required properties are `compatible`, `reg`, `interrupts`, `spi-cpha`, `spi-cpol`, `spi-max-frequency`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `spi-cpha` allowed with common binding semantics; `spi-cpol` allowed with common binding semantics; `spi-max-frequency` (range ..15000000); `vdd-supply` allowed with common binding semantics; `interrupts` (max 1 item(s)); `reset-gpios` (max 1 item(s); Active low RESET pin.); `clocks` (max 1 item(s); If not provided, then the internal clock is used.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable; regulator supplies: `vdd-supply`; clock framework: `clocks`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/adi,adis16550.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml

### Purpose
`bosch,bmi160.yaml` defines the devicetree schema for Bosch BMI160. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Inertial Measurement Unit with Accelerometer, Gyroscope and externally connectable Magnetometer https://www.bosch-sensortec.com/bst/products/all_products/bmi160 Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,bmi160.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmi160`, `bosch,bmi120`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `interrupt-names` (enum `INT1`, `INT2`; set to "INT1" if INT1 pin should be used as interrupt input, set to "INT2" if INT2 pin should be used instead); `drive-open-drain` (type `boolean`; set if the specified interrupt pin should be configured as open drain. If not set, defaults to push-pull.); `vdd-supply` (provide VDD power to the sensor.); `vddio-supply` (provide VDD IO power to the sensor.); `mount-matrix` (an optional 3x3 mounting rotation matrix)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi160.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml

### Purpose
`bosch,bmi270.yaml` defines the devicetree schema for Bosch BMI270 6-Axis IMU. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: BMI270 is a 6-axis inertial measurement unit that can measure acceleration and angular velocity. The sensor also supports configurable interrupt events such as motion, step counter, and wrist motion gestures. The sensor can communicate I2C or SPI. https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi270/ Maintainer coverage is Alex Lanzano <lanzano.alex@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,bmi270.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmi260`, `bosch,bmi270`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`; set if the specified interrupt pins should be configured as open drain. If not set, defaults to push-pull.); `mount-matrix` (an optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi270.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml

### Purpose
`bosch,bmi323.yaml` defines the devicetree schema for Bosch BMI323 6-Axis IMU. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: BMI323 is a 6-axis inertial measurement unit that supports acceleration and gyroscopic measurements with hardware fifo buffering. Sensor also provides events information such as motion, steps, orientation, single and double tap detection. Maintainer coverage is Jagath Jog J <jagathjog1996@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,bmi323.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmi323`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`; set if the specified interrupt pin should be configured as open drain. If not set, defaults to push-pull.); `mount-matrix` (an optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bmi323.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml

### Purpose
`bosch,bno055.yaml` defines the devicetree schema for Bosch BNO055. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Inertial Measurement Unit with Accelerometer, Gyroscope, Magnetometer and internal MCU for sensor fusion https://www.bosch-sensortec.com/products/smart-sensors/bno055/ Maintainer coverage is Andrea Merello <andrea.merello@iit.it>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,bno055.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bno055`. Top-level required properties are `compatible`. Important property contracts include: `reg` (max 1 item(s)); `reset-gpios` (max 1 item(s)); `clocks` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; clock framework: `clocks`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,bno055.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml

### Purpose
`bosch,smi240.yaml` defines the devicetree schema for Bosch smi240 imu. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Inertial Measurement Unit with Accelerometer and Gyroscope with a measurement range of +/-300 degrees /s and up to 16g. https://www.bosch-semiconductors.com/mems-sensors/highly-automated-driving/smi240/ Maintainer coverage is Jianping Shen <Jianping.Shen@de.bosch.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,smi240.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,smi240`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi240.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml

### Purpose
`bosch,smi330.yaml` defines the devicetree schema for Bosch SMI330 6-Axis IMU. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: SMI330 is a 6-axis inertial measurement unit that supports acceleration and gyroscopic measurements with hardware fifo buffering. Sensor also provides events information such as motion, no-motion and tilt detection. Maintainer coverage is Stefan Gutmann <stefam.gutmann@de.bosch.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/bosch,smi330.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,smi330`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` (provide VDD power to the sensor.); `vddio-supply` (provide VDD IO power to the sensor.); `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`; set if the interrupt pin(s) should be configured as open drain. If not set, defaults to push-pull.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/bosch,smi330.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml

### Purpose
`invensense,icm42600.yaml` defines the devicetree schema for InvenSense ICM-426xx Inertial Measurement Unit. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: 6-axis MotionTracking device that combines a 3-axis gyroscope and a 3-axis accelerometer. It has a configurable host interface that supports I3C, I2C and SPI serial communication, features a 2kB FIFO and 2 programmable interrupts with ultra-low-power wake-on-motion support to minimize system power consumption. Other industry-leading features include InvenSense on-chip APEX Motion Processing engine for gesture recognition, activity classificati... Maintainer coverage is Jean-Baptiste Maneyrol <jean-baptiste.maneyrol@tdk.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/invensense,icm42600.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,icm42600`, `invensense,icm42602`, `invensense,icm42605`, `invensense,icm42622`, `invensense,icm42631`, `invensense,icm42686`, `invensense,icm42688`. Top-level required properties are `compatible`, `reg`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`); `vdd-supply` (Regulator that provides power to the sensor); `vddio-supply` (Regulator that provides power to the bus); `spi-cpha` allowed with common binding semantics; `spi-cpol` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm42600.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml

### Purpose
`invensense,icm45600.yaml` defines the devicetree schema for InvenSense ICM-45600 Inertial Measurement Unit. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: 6-axis MotionTracking device that combines a 3-axis gyroscope and a 3-axis accelerometer. It has a configurable host interface that supports I3C, I2C and SPI serial communication, features up to 8kB FIFO and 2 programmable interrupts with ultra-low-power wake-on-motion support to minimize system power consumption. Other industry-leading features include InvenSense on-chip APEX Motion Processing engine for gesture recognition, activity classifi... Maintainer coverage is Remi Buisson <remi.buisson@tdk.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/invensense,icm45600.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,icm45605`, `invensense,icm45606`, `invensense,icm45608`, `invensense,icm45634`, `invensense,icm45686`, `invensense,icm45687`, `invensense,icm45688p`, `invensense,icm45689`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s)); `interrupt-names` (min 1 item(s); Choose chip interrupt pin to be used as interrupt input.); `drive-open-drain` (type `boolean`); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `mount-matrix` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,icm45600.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml

### Purpose
`invensense,mpu6050.yaml` defines the devicetree schema for InvenSense MPU-6050 Six-Axis (Gyro + Accelerometer) MEMS MotionTracking Device. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: These devices support both I2C and SPI bus interfaces. Maintainer coverage is Jean-Baptiste Maneyrol <jean-baptiste.maneyrol@tdk.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/invensense,mpu6050.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,iam20380`, `invensense,iam20680`, `invensense,icm20608`, `invensense,icm20609`, `invensense,icm20689`, `invensense,icm20602`, `invensense,icm20690`, `invensense,mpu6000`, `invensense,mpu6050`, `invensense,mpu6500`, `invensense,mpu6515`, `invensense,mpu6880`, `invensense,mpu9150`, `invensense,mpu9250`, `invensense,mpu9255`, `invensense,icm20600`, `invensense,icm20608d`, `invensense,iam20680hp`, `invensense,iam20680ht`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `mount-matrix` allowed with common binding semantics; `invensense,level-shifter` (type `boolean`; From ancient platform data struct: false: VLogic, true: VDD); `i2c-gate` (ref `/schemas/i2c/i2c-controller.yaml`; These devices also support an auxiliary i2c bus via an i2c-gate.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 1 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/i2c/i2c-controller.yaml`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `invensense,level-shifter` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/invensense,mpu6050.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml

### Purpose
`nxp,fxos8700.yaml` defines the devicetree schema for Freescale FXOS8700 Inertial Measurement Unit. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Accelerometer and magnetometer combo device with an i2c and SPI interface. https://www.nxp.com/products/sensors/motion-sensors/6-axis/digital-motion-sensor-3d-accelerometer-2g-4g-8g-plus-3d-magnetometer:FXOS8700CQ Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/nxp,fxos8700.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `nxp,fxos8700`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/nxp,fxos8700.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml

### Purpose
`st,lsm6dsx.yaml` defines the devicetree schema for STM 6-axis (acc + gyro) IMU Mems sensors. It is an IIO imu binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Devices have both I2C and SPI interfaces. Maintainer coverage is Lorenzo Bianconi <lorenzo@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/imu/st,lsm6dsx.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,lsm6ds3`, `st,lsm6ds3h`, `st,lsm6dsl`, `st,lsm6dsm`, `st,ism330dlc`, `st,lsm6dso`, `st,asm330lhh`, `st,lsm6dsox`, `st,lsm6dsr`, `st,lsm6ds3tr-c`, `st,ism330dhcx`, `st,lsm9ds1-imu`, `st,lsm6ds0`, `st,lsm6dsrx`, `st,lsm6dst`, `st,lsm6dsop`, `st,lsm6dsv`, `st,lsm6dso16is`, `st,asm330lhhx`, `st,asm330lhhxg1`, `st,lsm6dstx`, `st,lsm6dsv16x`, `st,ism330is`, `st,asm330lhb`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s); Supports up to 2 interrupt lines via the INT1 and INT2 pins.); `vdd-supply` (if defined provides VDD power to the sensor.); `vddio-supply` (if defined provides VDD IO power to the sensor.); `st,drdy-int-pin` (enum `1`, `2`; ref `/schemas/types.yaml#/definitions/uint32`; The pin on the package that will be used to signal data ready); `st,pullups` (type `boolean`; enable/disable internal i2c controller pullup resistors.); `st,disable-sensor-hub` (type `boolean`; Enable/disable internal i2c controller slave autoprobing at bootstrap. Disable sensor-hub is useful if i2c controller...); `drive-open-drain` (type `boolean`; The interrupt/data ready line will be configured as open drain, which is useful if several sensors share the same int...); `wakeup-source` (ref `/schemas/types.yaml#/definitions/flag`); `mount-matrix` (an optional 3x3 mounting rotation matrix)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/iio/iio.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO imu drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `st,drdy-int-pin`, `st,pullups`, `st,disable-sensor-hub` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/imu/st,lsm6dsx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml

### Purpose
`adux1020.yaml` defines the devicetree schema for Analog Devices ADUX1020 Photometric sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Photometric sensor over an i2c interface. https://www.analog.com/media/en/technical-documentation/data-sheets/ADUX1020.pdf Maintainer coverage is Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/adux1020.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,adux1020`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/adux1020.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml

### Purpose
`ams,as73211.yaml` defines the devicetree schema for AMS AS73211 JENCOLOR(R) Digital XYZ Sensor and AMS AS7331 UV Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: AMS AS73211 XYZ True Color Sensor with I2C Interface https://ams.com/documents/20143/36005/AS73211_DS000556_3-01.pdf/a65474c0-b302-c2fd-e30a-c98df87616df AMS AS7331 UVA, UVB and UVC Sensor with I2C Interface https://ams.com/documents/20143/9106314/AS7331_DS001047_4-00.pdf Maintainer coverage is Christian Eggers <ceggers@arri.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/ams,as73211.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ams,as73211`, `ams,as7331`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s); I2C address of the device (0x74...0x77).); `interrupts` (max 1 item(s); Interrupt specifier for the READY interrupt generated by the device.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ams,as73211.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml

### Purpose
`amstaos,tsl2563.yaml` defines the devicetree schema for AMS TAOS TSL2563 ambient light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensor with an i2c interface. Maintainer coverage is Sebastian Reichel <sre@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/amstaos,tsl2563.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `amstaos,tsl2560`, `amstaos,tsl2561`, `amstaos,tsl2562`, `amstaos,tsl2563`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `amstaos,cover-comp-gain` (enum `1`, `16`; ref `/schemas/types.yaml#/definitions/uint32`; Multiplier for gain compensation)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `amstaos,cover-comp-gain` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2563.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml

### Purpose
`amstaos,tsl2591.yaml` defines the devicetree schema for AMS/TAOS TSL2591 Ambient Light Sensor (ALS). It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: AMS/TAOS TSL2591 is a very-high sensitivity light-to-digital converter that transforms light intensity into a digital signal. Maintainer coverage is Joe Sandom <joe.g.sandom@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/amstaos,tsl2591.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `amstaos,tsl2591`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Interrupt (INT:Pin 2) Active low. Should be set to IRQ_TYPE_EDGE_FALLING. interrupt is used to detect if the light in...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/amstaos,tsl2591.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml

### Purpose
`avago,apds9300.yaml` defines the devicetree schema for Avago Gesture/RGB/ALS/Proximity sensors. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet: https://www.avagotech.com/docs/AV02-1077EN Datasheet: https://www.avagotech.com/docs/AV02-4191EN Datasheet: https://www.avagotech.com/docs/AV02-4755EN Maintainer coverage is Subhajit Ghosh <subhajit.ghosh@tweaklogic.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/avago,apds9300.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `avago,apds9300`, `avago,apds9306`, `avago,apds9960`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/avago,apds9300.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml

### Purpose
`bh1750.yaml` defines the devicetree schema for ROHM BH1750 ambient light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensor with an i2c interface. Maintainer coverage is Tomasz Duszynski <tduszyns@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/bh1750.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `rohm,bh1710`, `rohm,bh1715`, `rohm,bh1721`, `rohm,bh1750`, `rohm,bh1751`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `reset-gpios` (max 1 item(s); GPIO connected to the DVI reset pin (active low))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/bh1750.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml

### Purpose
`brcm,apds9160.yaml` defines the devicetree schema for Broadcom Combined Proximity & Ambient light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet: https://docs.broadcom.com/docs/APDS-9160-003-DS Maintainer coverage is Mikael Gonella-Bolduc <m.gonella.bolduc@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/brcm,apds9160.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `brcm,apds9160`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `ps-cancellation-duration` (range ..63; ref `/schemas/types.yaml#/definitions/uint32`; default `0`; Proximity sensor cancellation pulse duration in half clock cycles. This parameter determines a cancellation pulse dur...); `ps-cancellation-current-picoamp` (range 60000..276000; Proximity sensor crosstalk cancellation current in picoampere. This parameter adjusts the current in steps of 2400 pA...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/brcm,apds9160.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml

### Purpose
`capella,cm3605.yaml` defines the devicetree schema for Capella Microsystems CM3605 Ambient Light and Short Distance Proximity Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The CM3605 is an entirely analog part. However, it requires quite a bit of software logic to interface a host operating system. This ALS and proximity sensor was one of the very first deployed in mobile handsets, notably it is used in the very first Nexus One Android phone from 2010. Maintainer coverage is Linus Walleij <linusw@kernel.org>, Kevin Tsai <ktsai@capellamicro.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/capella,cm3605.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `capella,cm3605`. Top-level required properties are `compatible`, `aset-gpios`, `interrupts`, `io-channels`, `io-channel-names`. Important property contracts include: `aset-gpios` (max 1 item(s); ASET line (drive low to activate the ALS, should be flagged GPIO_ACTIVE_LOW)); `interrupts` (max 1 item(s); Connected to the POUT (proximity sensor out) line. The edge detection must be set to IRQ_TYPE_EDGE_BOTH so as to dete...); `io-channels` (max 1 item(s); ADC channel used for converting the voltage from AOUT to a digital representation.); `io-channel-names` (const `aout`); `vdd-supply` allowed with common binding semantics; `capella,aset-resistance-ohms` (enum `50000`, `100000`, `300000`, `600000`; Sensitivity calibration resistance. Note that calibration curves are only provided for specific allowed values. Defau...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `capella,aset-resistance-ohms` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm3605.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml

### Purpose
`capella,cm36651.yaml` defines the devicetree schema for Capella CM36651 I2C Proximity and Color Light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Beomho Seo <beomho.seo@samsung.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/capella,cm36651.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `capella,cm36651`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vled-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vled-supply` (Supply for the IR_LED which is part of the cm36651 for proximity detection.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vled-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/capella,cm36651.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml

### Purpose
`dynaimage,al3010.yaml` defines the devicetree schema for Dyna-Image AL3000a/AL3010 sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is David Heidelberg <david@ixit.cz>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/dynaimage,al3010.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `dynaimage,al3000a`, `dynaimage,al3010`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml

### Purpose
`dynaimage,al3320a.yaml` defines the devicetree schema for Dyna-Image AL3320A sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is David Heidelberg <david@ixit.cz>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/dynaimage,al3320a.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `dynaimage,al3320a`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/dynaimage,al3320a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml

### Purpose
`isl29018.yaml` defines the devicetree schema for Intersil 29018/29023/29035 Ambient Light, Infrared Light, and Proximity Sensor
. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient and infrared light sensing with proximity detection over an i2c interface. https://www.renesas.com/us/en/www/doc/datasheet/isl29018.pdf https://www.renesas.com/us/en/www/doc/datasheet/isl29023.pdf https://www.renesas.com/us/en/www/doc/datasheet/isl29035.pdf Maintainer coverage is Brian Masney <masneyb@onstation.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/isl29018.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `isil,isl29018`, `isil,isl29023`, `isil,isl29035`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vcc-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/isl29018.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml

### Purpose
`liteon,ltr390.yaml` defines the devicetree schema for Lite-On LTR390 ALS and UV Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The Lite-On LTR390 is an ALS (Ambient Light Sensor) and a UV sensor in a single package with i2c address of 0x53. Datasheet: https://optoelectronics.liteon.com/upload/download/DS86-2015-0004/LTR-390UV_Final_%20DS_V1%201.pdf Maintainer coverage is Anshul Dalal <anshulusr@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/liteon,ltr390.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `liteon,ltr390`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Level interrupt pin with open drain output. The sensor pulls this pin low when the measured reading is greater than s...); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr390.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml

### Purpose
`liteon,ltr501.yaml` defines the devicetree schema for LiteON LTR501 I2C Proximity and Light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Nikita Travkin <nikita@trvn.ru>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/liteon,ltr501.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `liteon,ltr501`, `liteon,ltr559`, `liteon,ltr301`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `interrupts` (max 1 item(s)); `proximity-near-level` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `../common.yaml#`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltr501.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml

### Purpose
`liteon,ltrf216a.yaml` defines the devicetree schema for LTRF216A Ambient Light Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensing with an i2c interface. Maintainer coverage is Shreeya Patel <shreeya.patel@collabora.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/liteon,ltrf216a.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `liteon,ltr308`, `liteon,ltrf216a`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/liteon,ltrf216a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml

### Purpose
`maxim,max44009.yaml` defines the devicetree schema for MAX44009 Ambient Light Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Robert Eshleman <bobbyeshleman@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/maxim,max44009.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max44009`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s); Default address is 0x4a); `interrupts` (max 1 item(s); Should be configured with type IRQ_TYPE_EDGE_FALLING)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/maxim,max44009.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml

### Purpose
`noa1305.yaml` defines the devicetree schema for ON Semiconductor NOA1305 Ambient Light Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient sensing with an i2c interface. https://www.onsemi.com/pub/Collateral/NOA1305-D.PDF Maintainer coverage is Martyn Welch <martyn.welch@collabora.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/noa1305.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `onnn,noa1305`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vin-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vin-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/noa1305.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml

### Purpose
`rohm,bh1745.yaml` defines the devicetree schema for ROHM BH1745 colour sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: BH1745 is an I2C colour sensor with red, green, blue and clear channels. It has a programmable active low interrupt pin. Interrupt occurs when the signal from the selected interrupt source channel crosses set interrupt threshold high/low level. Maintainer coverage is Mudit Sharma <muditsharma.info@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/rohm,bh1745.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `rohm,bh1745`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bh1745.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml

### Purpose
`rohm,bu27034anuc.yaml` defines the devicetree schema for ROHM BU27034ANUC ambient light sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: ROHM BU27034ANUC is an ambient light sensor with 2 channels and 2 photo diodes capable of detecting a very wide range of illuminance. Typical application is adjusting LCD and backlight power of TVs and mobile phones. Maintainer coverage is Matti Vaittinen <mazziesaccount@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/rohm,bu27034anuc.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `rohm,bu27034anuc`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/rohm,bu27034anuc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml

### Purpose
`sharp,gp2ap002.yaml` defines the devicetree schema for Sharp GP2AP002A00F and GP2AP002S00F proximity and ambient light sensors. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Proximity and ambient light sensor with IR LED for the proximity sensing and an analog output for light intensity. The ambient light sensor output is not available on the GP2AP002S00F variant. Maintainer coverage is Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/sharp,gp2ap002.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `sharp,gp2ap002a00f`, `sharp,gp2ap002s00f`. Top-level required properties are `compatible`, `reg`, `interrupts`, `sharp,proximity-far-hysteresis`, `sharp,proximity-close-hysteresis`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); an interrupt for proximity, usually a GPIO line); `vdd-supply` (VDD power supply a phandle to a regulator); `vio-supply` (VIO power supply a phandle to a regulator); `io-channels` (max 1 item(s); ALSOUT ADC channel to read the ambient light); `io-channel-names` (const `alsout`); `sharp,proximity-far-hysteresis` (ref `/schemas/types.yaml#/definitions/uint8`; Hysteresis setting for "far" object detection, this setting is device-unique and adjust the optical setting for proxi...); `sharp,proximity-close-hysteresis` (ref `/schemas/types.yaml#/definitions/uint8`; Hysteresis setting for "close" object detection, this setting is device-unique and adjust the optical setting for pro...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint8`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `sharp,proximity-far-hysteresis`, `sharp,proximity-close-hysteresis` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap002.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml

### Purpose
`sharp,gp2ap020a00f.yaml` defines the devicetree schema for Sharp GP2AP020A00F I2C Proximity/ALS sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The proximity detector sensor requires power supply for its built-in led. Maintainer coverage is Kyungmin Park <kyungmin.park@samsung.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/sharp,gp2ap020a00f.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `sharp,gp2ap020a00f`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vled-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vled-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vled-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/sharp,gp2ap020a00f.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml

### Purpose
`st,uvis25.yaml` defines the devicetree schema for ST UVIS25 uv sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Lorenzo Bianconi <lorenzo.bianconi83@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/st,uvis25.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,uvis25`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,uvis25.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml

### Purpose
`st,vl6180.yaml` defines the devicetree schema for STMicro VL6180 ALS, range and proximity sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Proximity sensing module incorporating time of flight sensor Datasheet at https://www.st.com/resource/en/datasheet/vl6180x.pdf Maintainer coverage is Manivannan Sadhasivam <manivannanece23@gmail.com>, Peter Meerwald-Stadler <pmeerw@pmeerw.net>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/st,vl6180.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,vl6180`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/st,vl6180.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml

### Purpose
`stk33xx.yaml` defines the devicetree schema for Sensortek STK33xx I2C Ambient Light and Proximity sensor
. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light and proximity sensor over an i2c interface. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/stk33xx.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `sensortek,stk3310`, `sensortek,stk3311`, `sensortek,stk3335`, `sensortek,stk3013`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `proximity-near-level` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `../common.yaml#`. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/stk33xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml

### Purpose
`ti,opt3001.yaml` defines the devicetree schema for Texas Instruments OPT3001 Ambient Light Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The device supports interrupt-driven and interrupt-less operation, depending on whether an interrupt property has been populated into the DT. Maintainer coverage is Andreas Dannenberg <dannenberg@ti.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/ti,opt3001.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,opt3001`, `ti,opt3002`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Should be configured with type IRQ_TYPE_EDGE_FALLING)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt3001.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml

### Purpose
`ti,opt4001.yaml` defines the devicetree schema for Texas Instruments OPT4001 Ambient Light Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensor with an i2c interface. Last part of compatible is for the packaging used. Picostar is a 4 pinned SMT and sot-5x3 is a 8 pinned SOT. https://www.ti.com/lit/gpn/opt4001 Maintainer coverage is Stefan Windfeldt-Prytz <stefan.windfeldt-prytz@axis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/ti,opt4001.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,opt4001-picostar`, `ti,opt4001-sot-5x3`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 1 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4001.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml

### Purpose
`ti,opt4060.yaml` defines the devicetree schema for Texas Instruments OPT4060 RGBW Color Sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Texas Instrument RGBW high resolution color sensor over I2C. https://www.ti.com/lit/gpn/opt4060 Maintainer coverage is Per-Daniel Olsson <perdaniel.olsson@axis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/ti,opt4060.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,opt4060`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/ti,opt4060.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml

### Purpose
`tsl2583.yaml` defines the devicetree schema for AMS/TAOS Ambient Light Sensor (ALS). It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensing with an i2c interface. Maintainer coverage is Brian Masney <masneyb@onstation.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/tsl2583.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `amstaos,tsl2580`, `amstaos,tsl2581`, `amstaos,tsl2583`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vcc-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2583.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml

### Purpose
`tsl2772.yaml` defines the devicetree schema for AMS/TAOS Ambient Light Sensor (ALS) and Proximity Detector. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensing and proximity detection with an i2c interface. https://ams.com/documents/20143/36005/TSL2772_DS000181_2-00.pdf Maintainer coverage is Brian Masney <masneyb@onstation.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/tsl2772.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `amstaos,tsl2571`, `amstaos,tsl2671`, `amstaos,tmd2671`, `amstaos,tsl2771`, `amstaos,tmd2771`, `amstaos,tsl2572`, `amstaos,tsl2672`, `amstaos,tmd2672`, `amstaos,tsl2772`, `amstaos,tmd2772`, `avago,apds9930`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `amstaos,proximity-diodes` (1-2 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; Proximity diodes to enable); `interrupts` (max 1 item(s)); `led-max-microamp` (enum `13000`, `25000`, `50000`, `100000`; Current for the proximity LED); `vdd-supply` (Regulator that provides power to the sensor); `vddio-supply` (Regulator that provides power to the bus)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32-array`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `amstaos,proximity-diodes` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/tsl2772.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml

### Purpose
`upisemi,us5182.yaml` defines the devicetree schema for UPISEMI us5182d I2C ALS and Proximity sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/upisemi,us5182.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `upisemi,usd5182`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `upisemi,glass-coef` (ref `/schemas/types.yaml#/definitions/uint32`; default `1000`; glass attenuation factor - compensation factor of resolution 1000 for material transmittance.); `upisemi,dark-ths` (8-8 item(s); ref `/schemas/types.yaml#/definitions/uint16-array`; 16-bit thresholds (adc counts) corresponding to every scale.); `upisemi,upper-dark-gain` (ref `/schemas/types.yaml#/definitions/uint8`; default `0`; 8-bit dark gain compensation factor(4 int and 4 fractional bits - Q4.4) applied when light > threshold.); `upisemi,lower-dark-gain` (ref `/schemas/types.yaml#/definitions/uint8`; default `22`; 8-bit dark gain compensation factor(4 int and 4 fractional bits - Q4.4) applied when light < threshold.); `upisemi,continuous` (ref `/schemas/types.yaml#/definitions/flag`; This chip has two power modes: one-shot (chip takes one measurement and then shuts itself down) and continuous (chip...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint16-array`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/types.yaml#/definitions/flag`. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `upisemi,glass-coef`, `upisemi,dark-ths`, `upisemi,upper-dark-gain`, `upisemi,lower-dark-gain`, `upisemi,continuous` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/upisemi,us5182.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml

### Purpose
`vishay,vcnl4000.yaml` defines the devicetree schema for VISHAY VCNL4000 ambient light and proximity sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Ambient light sensing with proximity detection over an i2c interface. Maintainer coverage is Peter Meerwald <pmeerw@pmeerw.net>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/vishay,vcnl4000.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `capella,cm36672p`, `vishay,vcnl4000`, `vishay,vcnl4010`, `vishay,vcnl4020`, `vishay,vcnl4040`, `vishay,vcnl4200`, `capella,cm36686`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `interrupts` (max 1 item(s)); `vdd-supply` (Regulator providing power to the "VDD" pin.); `vio-supply` (Regulator providing power for pull-up of the I/O lines. Does not connect to the sensor directly, but is needed for th...); `vled-supply` (Regulator providing power to the IR anode pin.); `reg` (max 1 item(s)); `proximity-near-level` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `../common.yaml#`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vio-supply`, `vled-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml

### Purpose
`vishay,vcnl4035.yaml` defines the devicetree schema for VISHAY VCNL4035 ambient Light and proximity sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet at https://www.vishay.com/docs/84251/vcnl4035x01.pdf Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/vishay,vcnl4035.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `vishay,vcnl4035`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,vcnl4035.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml

### Purpose
`vishay,veml6030.yaml` defines the devicetree schema for VEML3235, VEML6030, VEML6035 and VEML7700 Ambient Light Sensors (ALS). It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Bindings for the ambient light sensors veml6030 and veml6035 from Vishay Semiconductors over an i2c interface. Irrespective of whether interrupt is used or not, application can get the ALS and White channel reading from IIO raw interface. If the interrupts are used, application will receive an IIO event whenever configured threshold is crossed. Specifications about the sensors can be found at: https://www.vishay.com/docs/80131/veml3235.pdf htt... Maintainer coverage is Rishi Gupta <gupt21@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/vishay,veml6030.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `vishay,veml3235`, `vishay,veml6030`, `vishay,veml6035`, `vishay,veml7700`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); interrupt mapping for IRQ. Configure with IRQ_TYPE_LEVEL_LOW. Refer to interrupt-controller/interrupts.txt for generi...); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 3 top-level `allOf` entry(s), 3 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6030.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml

### Purpose
`vishay,veml6046x00.yaml` defines the devicetree schema for Vishay VEML6046X00 High accuracy RGBIR color sensor. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: VEML6046X00 datasheet at https://www.vishay.com/docs/80173/veml6046x00.pdf Maintainer coverage is Andreas Klinger <ak@it-klinger.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/vishay,veml6046x00.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `vishay,veml6046x00`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6046x00.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml

### Purpose
`vishay,veml6075.yaml` defines the devicetree schema for Vishay VEML6070 UVA, VEML6075 UVA/B and VEML6040 RGBW sensors. It is an IIO light binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: VEML6040 datasheet at https://www.vishay.com/docs/84276/veml6040.pdf Maintainer coverage is Javier Carrasco <javier.carrasco.cruz@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/light/vishay,veml6075.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `vishay,veml6040`, `vishay,veml6070`, `vishay,veml6075`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vishay,rset-ohms` (range 75000..1200000; default `270000`; Resistor used to select the integration time.); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 1 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO light drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `vishay,rset-ohms` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/light/vishay,veml6075.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml

### Purpose
`allegromicro,als31300.yaml` defines the devicetree schema for Allegro MicroSystems ALS31300 3-D Linear Hall Effect sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Neil Armstrong <neil.armstrong@linaro.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/allegromicro,als31300.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `allegromicro,als31300-500`, `allegromicro,als31300-1000`, `allegromicro,als31300-2000`. Top-level required properties are `compatible`. Important property contracts include: `$nodename`; `reg` (max 1 item(s)); `vcc-supply` (5.5V supply); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/allegromicro,als31300.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml

### Purpose
`asahi-kasei,ak8974.yaml` defines the devicetree schema for Asahi Kasei AK8974 magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/asahi-kasei,ak8974.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `alps,hscdtd008a`, `asahi-kasei,ak8974`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s); Data ready (DRDY) and interrupt (INT1) lines from the chip. The DRDY interrupt must be placed first. The interrupts c...); `avdd-supply` allowed with common binding semantics; `dvdd-supply` allowed with common binding semantics; `mount-matrix` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `avdd-supply`, `dvdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8974.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml

### Purpose
`asahi-kasei,ak8975.yaml` defines the devicetree schema for AsahiKASEI AK8975 magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Albrieux <jonathan.albrieux@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/asahi-kasei,ak8975.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `asahi-kasei,ak8975`, `asahi-kasei,ak8963`, `asahi-kasei,ak09911`, `asahi-kasei,ak09912`, `asahi-kasei,ak09916`, `asahi-kasei,ak09918`, `ak8975`, `ak8963`, `ak09911`, `ak09912`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `gpios` (max 1 item(s); AK8975 has a "Data ready" pin (DRDY) which informs that data is ready to be read and is possible to listen on it. If...); `interrupts` (max 1 item(s); interrupt for DRDY pin. Triggered on rising edge.); `vdd-supply` (an optional regulator that needs to be on to provide VDD power to the sensor.); `vid-supply` (an optional regulator that needs to be on to provide VID power to the sensor.); `mount-matrix` (an optional 3x3 mounting rotation matrix.); `reset-gpios` (max 1 item(s); an optional pin needed for AK09911 to set the reset state. This should be usually active low)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vid-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/asahi-kasei,ak8975.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml

### Purpose
`bosch,bmc150_magn.yaml` defines the devicetree schema for Bosch BMC150 magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Supports a range of parts, some of which form part of a multi die package that also contains other sensors. The interface is independent however, so a separate driver is used to support the magnetometer part. Datasheet at: http://ae-bst.resource.bosch.com/media/products/dokumente/bmc150/BST-BMC150-DS000-04.pdf Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/bosch,bmc150_magn.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmc150_magn`, `bosch,bmc156_magn`, `bosch,bmm150`, `bosch,bmm150_magn`, `bosch,bmx055-magn`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `interrupts` (max 1 item(s)); `mount-matrix` (an optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/bosch,bmc150_magn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml

### Purpose
`fsl,mag3110.yaml` defines the devicetree schema for Freescale MAG3110 magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/fsl,mag3110.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `fsl,mag3110`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/fsl,mag3110.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml

### Purpose
`honeywell,hmc5843.yaml` defines the devicetree schema for Honeywell HMC5843 magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Neil Brown <neilb@suse.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/honeywell,hmc5843.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `honeywell,hmc5843`, `honeywell,hmc5883`, `honeywell,hmc5883l`, `honeywell,hmc5983`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/honeywell,hmc5843.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml

### Purpose
`infineon,tlv493d-a1b6.yaml` defines the devicetree schema for Infineon Technologies TLV493D Low-Power 3D Magnetic Sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Dixit Parmar <dixitparmar19@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/infineon,tlv493d-a1b6.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `infineon,tlv493d-a1b6`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `$nodename`; `reg` (max 1 item(s)); `vdd-supply` (2.8V to 3.5V VDD supply); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/infineon,tlv493d-a1b6.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml

### Purpose
`pni,rm3100.yaml` defines the devicetree schema for PNI RM3100 3-axis magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Song Qiang <songqiang1304521@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/pni,rm3100.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `pni,rm3100`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/pni,rm3100.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml

### Purpose
`silabs,si7210.yaml` defines the devicetree schema for Si7210 magnetic position and temperature sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Silabs Si7210 I2C Hall effect magnetic position and temperature sensor. https://www.silabs.com/documents/public/data-sheets/si7210-datasheet.pdf Maintainer coverage is Antoni Pokusinski <apokusinski01@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/silabs,si7210.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `silabs,si7210`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/silabs,si7210.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml

### Purpose
`ti,tmag5273.yaml` defines the devicetree schema for TI TMAG5273 Low-Power Linear 3D Hall-Effect Sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The TI TMAG5273 is a low-power linear 3D Hall-effect sensor. This device integrates three independent Hall-effect sensors in the X, Y, and Z axes. The device has an integrated temperature sensor available. The TMAG5273 can be configured through the I2C interface to enable any combination of magnetic axes and temperature measurements. An integrated angle calculation engine (CORDIC) provides full 360 degrees  angular position information for both on-axi... Maintainer coverage is Gerald Loacker <gerald.loacker@wolfvision.net>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/ti,tmag5273.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,tmag5273`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `#io-channel-cells` (const `1`); `ti,angle-measurement` (enum `False`, `x-y`, `y-z`, `x-z`; ref `/schemas/types.yaml#/definitions/string`; Enables angle measurement in the selected plane. If not specified, "x-y" will be anables as default.); `vcc-supply` (A regulator providing 1.7 V to 3.6 V supply voltage on the VCC pin, typically 3.3 V.); `interrupts` (max 1 item(s); The low active interrupt can be configured to be fixed width or latched. Interrupt events can be configured to be gen...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/string`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `ti,angle-measurement` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/ti,tmag5273.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml

### Purpose
`voltafield,af8133j.yaml` defines the devicetree schema for Voltafield AF8133J magnetometer sensor. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Ondrej Jirman <megi@xff.cz>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/voltafield,af8133j.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `voltafield,af8133j`. Top-level required properties are `compatible`, `reg`, `avdd-supply`, `dvdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `reset-gpios` (A signal for active low reset input of the sensor. (optional; if not used, software reset over I2C will be used instead)); `avdd-supply` (A regulator that provides AVDD power (Working power, usually 3.3V) to the sensor.); `dvdd-supply` (A regulator that provides DVDD power (Digital IO power, 1.8V - AVDD) to the sensor.); `mount-matrix` (An optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `avdd-supply`, `dvdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/voltafield,af8133j.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml

### Purpose
`yamaha,yas530.yaml` defines the devicetree schema for Yamaha YAS530 family of magnetometer sensors. It is an IIO magnetometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The Yamaha YAS530 magnetometers is a line of 3-axis magnetometers first introduced by Yamaha in 2009 with the YAS530. They are successors of Yamaha's first magnetometer YAS529. Over the years this magnetometer has been miniaturized and appeared in a number of different variants. Maintainer coverage is Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/magnetometer/yamaha,yas530.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `yamaha,yas530`, `yamaha,yas532`, `yamaha,yas533`, `yamaha,yas535`, `yamaha,yas536`, `yamaha,yas537`, `yamaha,yas539`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `$nodename`; `reg` (max 1 item(s)); `reset-gpios` (max 1 item(s); The YAS530 sensor has a RSTN pin used to reset the logic inside the sensor. This GPIO line should connect to that pin...); `interrupts` (max 1 item(s); Interrupt for INT pin for interrupt generation. The polarity, whether the interrupt is active on the rising or the fa...); `vdd-supply` (An optional regulator providing core power supply on the VDD pin, typically 1.8 V or 3.0 V.); `iovdd-supply` (An optional regulator providing I/O power supply for the I2C interface on the IOVDD pin, typically 1.8 V.); `mount-matrix` (An optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 2 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `iovdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO magnetometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/magnetometer/yamaha,yas530.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml

### Purpose
`io-channel-mux.yaml` defines the devicetree schema for I/O channel multiplexer. It is an IIO multiplexer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: If a multiplexer is used to select which hardware signal is fed to e.g. an ADC channel, these bindings describe that situation. For each non-empty string in the channels property, an io-channel will be created. The number of this io-channel is the same as the index into the list of strings in the channels property, and also matches the mux controller state. The mux controller state is described in Documentation/devicetree/bindings/mux/mux-cont... Maintainer coverage is Peter Rosin <peda@axentia.se>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/multiplexer/io-channel-mux.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `io-channel-mux`. Top-level required properties are `compatible`, `io-channels`, `io-channel-names`, `mux-controls`, `channels`. Important property contracts include: `io-channels` (max 1 item(s); Channel node of the parent channel that has multiplexed input.); `io-channel-names` (const `parent`); `mux-controls` allowed with common binding semantics; `mux-control-names` allowed with common binding semantics; `channels` (ref `/schemas/types.yaml#/definitions/non-unique-string-array`; List of strings, labeling the mux controller states. An empty string for a state means that the channel is not availa...); `settle-time-us` (default `0`; Time required for analog signals to settle after muxing.); `#io-channel-cells` (const `1`)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/non-unique-string-array`. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO multiplexer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/multiplexer/io-channel-mux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml

### Purpose
`adi,ad5272.yaml` defines the devicetree schema for Analog Devices AD5272 digital potentiometer. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet: https://www.analog.com/en/products/ad5272.html Maintainer coverage is Phil Reid <preid@electromag.com.au>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/adi,ad5272.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,ad5272-020`, `adi,ad5272-050`, `adi,ad5272-100`, `adi,ad5274-020`, `adi,ad5274-100`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `reset-gpios` (max 1 item(s); Active low signal to the AD5272 RESET input.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/adi,ad5272.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml

### Purpose
`max5432.yaml` defines the devicetree schema for Maxim Integrated MAX5432-MAX5435 Digital Potentiometers. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Maxim Integrated MAX5432-MAX5435 Digital Potentiometers connected via I2C Datasheet: https://datasheets.maximintegrated.com/en/ds/MAX5432-MAX5435.pdf Maintainer coverage is Martin Kaiser <martin@kaiser.cx>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/max5432.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max5432`, `maxim,max5433`, `maxim,max5434`, `maxim,max5435`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/max5432.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml

### Purpose
`microchip,mcp41010.yaml` defines the devicetree schema for Microchip MCP41010/41050/41100/42010/42050/42100 Digital Potentiometer. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet: https://ww1.microchip.com/downloads/en/devicedoc/11195c.pdf Maintainer coverage is Chris Coffey <cmc@babblebit.net>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/microchip,mcp41010.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `microchip,mcp41010`, `microchip,mcp41050`, `microchip,mcp41100`, `microchip,mcp42010`, `microchip,mcp42050`, `microchip,mcp42100`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp41010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml

### Purpose
`microchip,mcp4131.yaml` defines the devicetree schema for Microchip MCP413X/414X/415X/416X/423X/424X/425X/426X Digital Potentiometer. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Slawomir Stepien <sst@poczta.fm>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/microchip,mcp4131.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `microchip,mcp4131-103`, `microchip,mcp4131-104`, `microchip,mcp4131-502`, `microchip,mcp4131-503`, `microchip,mcp4132-103`, `microchip,mcp4132-104`, `microchip,mcp4132-502`, `microchip,mcp4132-503`, `microchip,mcp4141-103`, `microchip,mcp4141-104`, `microchip,mcp4141-502`, `microchip,mcp4141-503`, `microchip,mcp4142-103`, `microchip,mcp4142-104`, `microchip,mcp4142-502`, `microchip,mcp4142-503`, `microchip,mcp4151-103`, `microchip,mcp4151-104`, `microchip,mcp4151-502`, `microchip,mcp4151-503`, `microchip,mcp4152-103`, `microchip,mcp4152-104`, `microchip,mcp4152-502`, `microchip,mcp4152-503`, `microchip,mcp4161-103`, `microchip,mcp4161-104`, `microchip,mcp4161-502`, `microchip,mcp4161-503`, `microchip,mcp4162-103`, `microchip,mcp4162-104`, `microchip,mcp4162-502`, `microchip,mcp4162-503`, `microchip,mcp4231-103`, `microchip,mcp4231-104`, `microchip,mcp4231-502`, `microchip,mcp4231-503`, `microchip,mcp4232-103`, `microchip,mcp4232-104`, `microchip,mcp4232-502`, `microchip,mcp4232-503`, ... (64 total). Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4131.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml

### Purpose
`microchip,mcp4531.yaml` defines the devicetree schema for Microchip mcp4531 and similar potentiometers.. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Family of I2C digital potentiometer Datasheets at: * volatile https://ww1.microchip.com/downloads/en/DeviceDoc/22096b.pdf * non-volatile https://ww1.microchip.com/downloads/en/DeviceDoc/22107B.pdf Part numbers as follows: mcp4ABC-XXX where A = 5 (1 wiper), 6 (2 wipers) B = 3 (7-bit, volatile), 4 (7-bit, non-volatile), 5 (8-bit, volatile), 6 (8-bit, non-volatile), C: 1 (potentiometer), 2 (rheostat) XXX = 502 (5 kOhms), 103 (10 kOhms), 503 (50 k... Maintainer coverage is Peter Rosin <peda@axentia.se>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/microchip,mcp4531.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `microchip,mcp4531-502`, `microchip,mcp4531-103`, `microchip,mcp4531-503`, `microchip,mcp4531-104`, `microchip,mcp4532-502`, `microchip,mcp4532-103`, `microchip,mcp4532-503`, `microchip,mcp4532-104`, `microchip,mcp4541-502`, `microchip,mcp4541-103`, `microchip,mcp4541-503`, `microchip,mcp4541-104`, `microchip,mcp4542-502`, `microchip,mcp4542-103`, `microchip,mcp4542-503`, `microchip,mcp4542-104`, `microchip,mcp4551-502`, `microchip,mcp4551-103`, `microchip,mcp4551-503`, `microchip,mcp4551-104`, `microchip,mcp4552-502`, `microchip,mcp4552-103`, `microchip,mcp4552-503`, `microchip,mcp4552-104`, `microchip,mcp4561-502`, `microchip,mcp4561-103`, `microchip,mcp4561-503`, `microchip,mcp4561-104`, `microchip,mcp4562-502`, `microchip,mcp4562-103`, `microchip,mcp4562-503`, `microchip,mcp4562-104`, `microchip,mcp4631-502`, `microchip,mcp4631-103`, `microchip,mcp4631-503`, `microchip,mcp4631-104`, `microchip,mcp4632-502`, `microchip,mcp4632-103`, `microchip,mcp4632-503`, `microchip,mcp4632-104`, ... (64 total). Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `#io-channel-cells` (const `1`)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/microchip,mcp4531.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml

### Purpose
`renesas,x9250.yaml` defines the devicetree schema for Renesas X9250 quad potentiometers. It is an IIO potentiometer binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The Renesas X9250 integrates four digitally controlled potentiometers. On each potentiometer, the X9250T has a 100 kOhms total resistance and the X9250U has a 50 kOhms total resistance. Maintainer coverage is Herve Codina <herve.codina@bootlin.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiometer/renesas,x9250.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `renesas,x9250t`, `renesas,x9250u`. Top-level required properties are `compatible`, `reg`, `vcc-supply`, `avp-supply`, `avn-supply`, `#io-channel-cells`. Important property contracts include: `reg` (max 1 item(s)); `vcc-supply` (Regulator for the VCC power supply.); `avp-supply` (Regulator for the analog V+ power supply.); `avn-supply` (Regulator for the analog V- power supply.); `#io-channel-cells` (const `1`); `spi-max-frequency` (range ..2000000); `wp-gpios` (max 1 item(s); GPIO connected to the write-protect pin.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml`. Integration hints from the schema and examples are: SPI; regulator supplies: `vcc-supply`, `avp-supply`, `avn-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiometer drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiometer/renesas,x9250.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml

### Purpose
`ti,lmp91000.yaml` defines the devicetree schema for Texas Instruments LMP91000 series of potentiostats with I2C control. It is an IIO potentiostat binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Typically used as a signal conditioner for chemical sensors. LMP91000: https://www.ti.com/lit/ds/symlink/lmp91000.pdf LMP91002: https://www.ti.com/lit/ds/symlink/lmp91002.pdf Maintainer coverage is Matt Ranostay <matt.ranostay@konsulko.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/potentiostat/ti,lmp91000.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,lmp91000`, `ti,lmp91002`. Top-level required properties are `compatible`, `reg`, `io-channels`. Important property contracts include: `reg` (max 1 item(s)); `io-channels` (max 1 item(s)); `ti,external-tia-resistor` (ref `/schemas/types.yaml#/definitions/flag`; If the property ti,tia-gain-ohm is not defined this needs to be set to signal that an external resistor value is bein...); `ti,tia-gain-ohm` (enum `2750`, `3500`, `7000`, `14000`, `35000`, `120000`, `350000`; ref `/schemas/types.yaml#/definitions/uint32`; Internal resistor for the transimpedance amplifier.); `ti,rload-ohm` (enum `10`, `33`, `50`, `100`; ref `/schemas/types.yaml#/definitions/uint32`; Internal resistor load applied to the gas sensor. Default 100 Ohms.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO potentiostat drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `ti,external-tia-resistor`, `ti,tia-gain-ohm`, `ti,rload-ohm` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/potentiostat/ti,lmp91000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml

### Purpose
`aosong,adp810.yaml` defines the devicetree schema for aosong adp810 differential pressure sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: ADP810 is differential pressure and temperature sensor. It has I2C bus interface with fixed address of 0x25. This sensor supports 8 bit CRC for reliable data transfer. It can measure differential pressure in the range -500 to 500Pa and temperate in the range -40 to +85 degree celsius. Maintainer coverage is Akhilesh Patil <akhilesh@ee.iitb.ac.in>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/aosong,adp810.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `aosong,adp810`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/aosong,adp810.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml

### Purpose
`asc,dlhl60d.yaml` defines the devicetree schema for All Sensors DLH series low voltage digital pressure sensors. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Bindings for the All Sensors DLH series pressure sensors. Specifications about the sensors can be found at: https://www.allsensors.com/cad/DS-0355_Rev_B.PDF Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/asc,dlhl60d.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `asc,dlhl60d`, `asc,dlhl60g`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s); I2C device address); `interrupts` (max 1 item(s); interrupt mapping for EOC(data ready) pin)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/asc,dlhl60d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml

### Purpose
`bmp085.yaml` defines the devicetree schema for BMP085/BMP180/BMP280/BME280/BMP380 pressure iio sensors. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Pressure, temperature and humidity iio sensors with i2c and spi interfaces Specifications about the sensor can be found at: https://www.bosch-sensortec.com/bst/products/all_products/bmp180 https://www.bosch-sensortec.com/bst/products/all_products/bmp280 https://www.bosch-sensortec.com/bst/products/all_products/bme280 https://www.bosch-sensortec.com/bst/products/all_products/bmp380 https://www.bosch-sensortec.com/bst/products/all_products/bmp580 Maintainer coverage is Andreas Klinger <ak@it-klinger.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/bmp085.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `bosch,bmp085`, `bosch,bmp180`, `bosch,bmp280`, `bosch,bme280`, `bosch,bmp380`, `bosch,bmp580`. Top-level required properties are `compatible`, `vddd-supply`, `vdda-supply`. Important property contracts include: `reg` (max 1 item(s)); `vddd-supply` (digital voltage regulator (see regulator/regulator.txt)); `vdda-supply` (analog voltage regulator (see regulator/regulator.txt)); `reset-gpios` (max 1 item(s); A GPIO line handling reset of the sensor. As the line is active low, it should be marked GPIO_ACTIVE_LOW (see gpio/gp...); `interrupts` (max 1 item(s)); `drive-open-drain` (type `boolean`; set if the interrupt pin should be configured as open drain. If not set, defaults to push-pull configuration.); `spi-max-frequency` (range ..10000000)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 3 top-level `allOf` entry(s), 2 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vddd-supply`, `vdda-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/bmp085.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml

### Purpose
`fsl,mpl3115.yaml` defines the devicetree schema for MPL3115 precision pressure sensor with altimetry. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: MPL3115 is a pressure/altitude and temperature sensor with I2C interface. It features two programmable interrupt lines which indicate events such as data ready or pressure/temperature threshold reached. https://www.nxp.com/docs/en/data-sheet/MPL3115A2.pdf Maintainer coverage is Antoni Pokusinski <apokusinski01@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/fsl,mpl3115.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `fsl,mpl3115`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `interrupts` (1-2 item(s)); `interrupt-names` (1-2 item(s)); `drive-open-drain` (type `boolean`; set if the specified interrupt pins should be configured as open drain. If not set, defaults to push-pull.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/fsl,mpl3115.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml

### Purpose
`honeywell,abp2030pa.yaml` defines the devicetree schema for Honeywell abp2030pa pressure sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Honeywell pressure sensor of model abp2030pa. This sensor has an I2C and SPI interface. There are many models with different pressure ranges available. The vendor calls them "ABP2 series". All of them have an identical programming model and differ in the pressure range and measurement unit. To support different models one needs to specify its pressure triplet. For custom silicon chips not covered by the Honeywell ABP2 series datasheet, the pre... Maintainer coverage is Petre Rodan <petre.rodan@subdimension.ro>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/honeywell,abp2030pa.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `honeywell,abp2030pa`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Optional interrupt for indicating end of conversion. SPI variants of ABP2 chips do not provide this feature.); `honeywell,pressure-triplet` (enum `001BA`, `1.6BA`, `2.5BA`, `004BA`, `006BA`, `008BA`, `010BA`, `012BA`, `001BD`, `1.6BD`, `2.5BD`, `004BD`, ...; ref `/schemas/types.yaml#/definitions/string`; Case-sensitive five character string that defines pressure range, unit and type as part of the device nomenclature. I...); `honeywell,pmin-pascal` (Minimum pressure value the sensor can measure in pascal.); `honeywell,pmax-pascal` (Maximum pressure value the sensor can measure in pascal.); `spi-max-frequency` (range ..800000); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 1 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/string`, `/schemas/spi/spi-peripheral-props.yaml`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `honeywell,pressure-triplet`, `honeywell,pmin-pascal`, `honeywell,pmax-pascal` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,abp2030pa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml

### Purpose
`honeywell,hsc030pa.yaml` defines the devicetree schema for Honeywell TruStability HSC and SSC pressure sensor series. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: support for Honeywell TruStability HSC and SSC digital pressure sensor series. These sensors have either an I2C, an SPI or an analog interface. Only the digital versions are supported by this driver. There are 118 models with different pressure ranges available in each family. The vendor calls them "HSC series" and "SSC series". All of them have an identical programming model but differ in pressure range, unit and transfer function. To support... Maintainer coverage is Petre Rodan <petre.rodan@subdimension.ro>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/honeywell,hsc030pa.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `honeywell,hsc030pa`. Top-level required properties are `compatible`, `reg`, `honeywell,transfer-function`, `honeywell,pressure-triplet`. Important property contracts include: `reg` (max 1 item(s)); `honeywell,transfer-function` (enum `0`, `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; Transfer function which defines the range of valid values delivered by the sensor. 0 - A, 10% to 90% of 2^14 1 - B, 5...); `honeywell,pressure-triplet` (enum `001BA`, `1.6BA`, `2.5BA`, `004BA`, `006BA`, `010BA`, `1.6MD`, `2.5MD`, `004MD`, `006MD`, `010MD`, `016MD`, ...; ref `/schemas/types.yaml#/definitions/string`; Case-sensitive five character string that defines pressure range, unit and type as part of the device nomenclature. I...); `honeywell,pmin-pascal` (Minimum pressure value the sensor can measure in pascal. To be specified only if honeywell,pressure-triplet is set to...); `honeywell,pmax-pascal` (Maximum pressure value the sensor can measure in pascal. To be specified only if honeywell,pressure-triplet is set to...); `vdd-supply` (Provide VDD power to the sensor (either 3.3V or 5V depending on the chip)); `spi-max-frequency` (range ..800000)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`, `/schemas/spi/spi-peripheral-props.yaml`. Integration hints from the schema and examples are: SPI; I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `honeywell,transfer-function`, `honeywell,pressure-triplet`, `honeywell,pmin-pascal`, `honeywell,pmax-pascal` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,hsc030pa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml

### Purpose
`honeywell,mprls0025pa.yaml` defines the devicetree schema for Honeywell mprls0025pa pressure sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Honeywell pressure sensor of model mprls0025pa. This sensor has an I2C and SPI interface. There are many models with different pressure ranges available. The vendor calls them "mpr series". All of them have the identical programming model and differ in the pressure range, unit and transfer function. To support different models one need to specify its pressure triplet as well as the transfer function. For custom silicon chips not covered by the... Maintainer coverage is Andreas Klinger <ak@it-klinger.de>, Petre Rodan <petre.rodan@subdimension.ro>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/honeywell,mprls0025pa.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `honeywell,mprls0025pa`. Top-level required properties are `compatible`, `reg`, `honeywell,transfer-function`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Optional interrupt for indicating End-of-conversion. If not present, the driver loops for a while until the received...); `reset-gpios` (max 1 item(s); Optional GPIO for resetting the device. If not present the device is not reset during the probe.); `honeywell,transfer-function` (enum `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; Transfer function which defines the range of valid values delivered by the sensor. 1 - A, 10% to 90% of 2^24 (1677722...); `honeywell,pressure-triplet` (enum `0001BA`, `01.6BA`, `02.5BA`, `0060MG`, `0100MG`, `0160MG`, `0250MG`, `0400MG`, `0600MG`, `0001BG`, `01.6BG`, `02.5BG`, ...; ref `/schemas/types.yaml#/definitions/string`; Case-sensitive five character string that defines pressure range, unit and type as part of the device nomenclature. I...); `honeywell,pmin-pascal` (Minimum pressure value the sensor can measure in pascal.); `honeywell,pmax-pascal` (Maximum pressure value the sensor can measure in pascal.); `spi-max-frequency` (range ..800000); `vdd-supply` (provide VDD power to the sensor.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 1 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`, `/schemas/spi/spi-peripheral-props.yaml`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `honeywell,transfer-function`, `honeywell,pressure-triplet`, `honeywell,pmin-pascal`, `honeywell,pmax-pascal` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/honeywell,mprls0025pa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml

### Purpose
`hoperf,hp03.yaml` defines the devicetree schema for HopeRF HP03 digital pressure/temperature sensors. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Digital pressure and temperature sensor with an I2C interface. Maintainer coverage is Marek Vasut <marex@denx.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/hoperf,hp03.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `hoperf,hp03`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `xclr-gpios` (max 1 item(s); The XCLR pin is a reset of the ADC in the chip, it must be pulled HI before the conversion and readout of the value f...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/hoperf,hp03.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml

### Purpose
`infineon,dps310.yaml` defines the devicetree schema for Infineon DPS310 barometric pressure and temperature sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The DPS310 is a barometric pressure and temperature sensor with an I2C interface. Maintainer coverage is Eddie James <eajames@linux.ibm.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/infineon,dps310.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `infineon,dps310`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `#io-channel-cells` (const `0`); `vdd-supply` (Voltage supply for the chip's analog blocks.); `vddio-supply` (Digital voltage supply for the chip's digital blocks and I/O interface.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/infineon,dps310.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml

### Purpose
`invensense,icp10100.yaml` defines the devicetree schema for InvenSense ICP-101xx Barometric Pressure Sensors. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Support for ICP-101xx family: ICP-10100, ICP-10101, ICP-10110, ICP-10111. Those devices uses a simple I2C communication bus, measuring the pressure in a ultra-low noise at the lowest power. Datasheet: https://product.tdk.com/system/files/dam/doc/product/sensor/pressure/capacitive-pressure/data_sheet/ds-000186-icp-101xx.pdf Maintainer coverage is Jean-Baptiste Maneyrol <jean-baptiste.maneyrol@tdk.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/invensense,icp10100.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,icp10101`, `invensense,icp10110`, `invensense,icp10111`, `invensense,icp10100`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/invensense,icp10100.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml

### Purpose
`meas,ms5611.yaml` defines the devicetree schema for Measurement Specialities ms5611 and similar pressure sensors. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Pressure sensors from MEAS Switzerland with SPI and I2C bus interfaces. Maintainer coverage is Tomasz Duszynski <tduszyns@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/meas,ms5611.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `meas,ms5607`, `meas,ms5611`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `spi-max-frequency` (range ..20000000)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/meas,ms5611.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml

### Purpose
`murata,zpa2326.yaml` defines the devicetree schema for Murata ZPA2326 pressure sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Pressure sensor from Murata with SPI and I2C bus interfaces. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/murata,zpa2326.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `murata,zpa2326`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vref-supply` allowed with common binding semantics; `interrupts` (max 1 item(s)); `spi-max-frequency` (range ..1000000)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vref-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/murata,zpa2326.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml

### Purpose
`rohm,bm1390.yaml` defines the devicetree schema for ROHM BM1390 pressure sensor. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: BM1390GLV-Z is a pressure sensor which performs internal temperature compensation for the MEMS. Pressure range is from 300 hPa to 1300 hPa and sample averaging and IIR filtering is built in. Temperature measurement is also supported. Maintainer coverage is Matti Vaittinen <mazziesaccount@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/rohm,bm1390.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `rohm,bm1390glv-z`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/rohm,bm1390.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml

### Purpose
`sensirion,sdp500.yaml` defines the devicetree schema for sdp500/sdp510 pressure sensor with I2C bus interface. It is an IIO pressure binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Pressure sensor from Sensirion with I2C bus interface. There is no software difference between sdp500 and sdp510. Maintainer coverage is Petar Stoykov <petar.stoykov@prodrive-technologies.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/pressure/sensirion,sdp500.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `sensirion,sdp510`, `sensirion,sdp500`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO pressure drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/pressure/sensirion,sdp500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml

### Purpose
`ams,as3935.yaml` defines the devicetree schema for Austrian Microsystems AS3935 Franklin lightning sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: This lightning distance sensor uses an I2C or SPI interface. The binding currently only covers the SPI option. Maintainer coverage is Matt Ranostay <matt.ranostay@konsulko.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/ams,as3935.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ams,as3935`. Top-level required properties are `compatible`, `reg`, `spi-cpha`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..2000000); `spi-cpha` allowed with common binding semantics; `interrupts` (max 1 item(s)); `ams,tuning-capacitor-pf` (range 0..120; ref `/schemas/types.yaml#/definitions/uint32`; Calibration tuning capacitor stepping value. This will require using the calibration data from the manufacturer.); `ams,nflwdth` (ref `/schemas/types.yaml#/definitions/uint32`; Set the noise and watchdog threshold register on startup. This will need to set according to the noise from the MCU b...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `ams,tuning-capacitor-pf`, `ams,nflwdth` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/ams,as3935.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml

### Purpose
`awinic,aw96103.yaml` defines the devicetree schema for Awinic's AW96103 capacitive proximity sensor and similar. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Awinic's AW96103/AW96105 proximity sensor. The specific absorption rate (SAR) is a metric that measures the degree of absorption of electromagnetic radiation emitted by wireless devices, such as mobile phones and tablets, by human tissue. In mobile phone applications, the proximity sensor is primarily used to detect the proximity of the human body to the phone. When the phone approaches the human body, it will actively reduce the transmit powe... Maintainer coverage is Wang Shuaijie <wangshuaijie@awinic.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/awinic,aw96103.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `awinic,aw96103`, `awinic,aw96105`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vcc-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Generated by the device to announce that a close/far proximity event has happened.); `vcc-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/awinic,aw96103.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml

### Purpose
`devantech-srf04.yaml` defines the devicetree schema for Devantech SRF04 and Maxbotix mb1000 ultrasonic range finder. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Bit-banging driver using two GPIOs: - trigger-gpio is raised by the driver to start sending out an ultrasonic burst - echo-gpio is held high by the sensor after sending ultrasonic burst until it is received once again Specifications about the devices can be found at: https://www.robot-electronics.co.uk/htm/srf04tech.htm https://www.maxbotix.com/documents/LV-MaxSonar-EZ_Datasheet.pdf Maintainer coverage is Andreas Klinger <ak@it-klinger.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/devantech-srf04.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `devantech,srf04`, `maxbotix,mb1000`, `maxbotix,mb1010`, `maxbotix,mb1020`, `maxbotix,mb1030`, `maxbotix,mb1040`. Top-level required properties are `compatible`, `trig-gpios`, `echo-gpios`. Important property contracts include: `trig-gpios` (max 1 item(s); Definition of the GPIO for the triggering (output) This GPIO is set for about 10 us by the driver to tell the device...); `echo-gpios` (max 1 item(s); Definition of the GPIO for the echo (input) This GPIO is set by the device as soon as an ultrasonic burst is sent out...); `power-gpios` (max 1 item(s); Definition of the GPIO for power management of connected peripheral (output). This GPIO can be used by the external h...); `startup-time-ms` (range 0..1000; default `100`; This is the startup time the device needs after a resume to be up and running.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/devantech-srf04.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml

### Purpose
`google,cros-ec-mkbp-proximity.yaml` defines the devicetree schema for ChromeOS EC MKBP Proximity Sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Google's ChromeOS EC sometimes has the ability to detect user proximity. This is implemented on the EC as near/far logic and exposed to the OS via an MKBP switch bit. Maintainer coverage is Stephen Boyd <swboyd@chromium.org>, Benson Leung <bleung@chromium.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/google,cros-ec-mkbp-proximity.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `google,cros-ec-mkbp-proximity`. Top-level required properties are `compatible`. Important property contracts include: `label` (Name for proximity sensor)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/google,cros-ec-mkbp-proximity.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml

### Purpose
`maxbotix,mb1232.yaml` defines the devicetree schema for MaxBotix I2CXL-MaxSonar ultrasonic distance sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: MaxBotix I2CXL-MaxSonar ultrasonic distance sensor of type mb1202, mb1212, mb1222, mb1232, mb1242, mb7040 or mb7137 using the i2c interface for ranging Specifications about the devices can be found at: https://www.maxbotix.com/documents/I2CXL-MaxSonar-EZ_Datasheet.pdf Maintainer coverage is Andreas Klinger <ak@it-klinger.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/maxbotix,mb1232.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxbotix,mb1202`, `maxbotix,mb1212`, `maxbotix,mb1222`, `maxbotix,mb1232`, `maxbotix,mb1242`, `maxbotix,mb7040`, `maxbotix,mb7137`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Interrupt used to announce the preceding reading request has finished and that data is available. If no interrupt is...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/maxbotix,mb1232.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml

### Purpose
`murata,irsd200.yaml` defines the devicetree schema for Murata IRS-D200 PIR sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: PIR sensor for human detection. Maintainer coverage is Waqar Hameed <waqar.hameed@axis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/murata,irsd200.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `murata,irsd200`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vdd-supply`. Important property contracts include: `reg`; `interrupts` (max 1 item(s); Type should be IRQ_TYPE_EDGE_RISING.); `vdd-supply` (3.3 V supply voltage.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/murata,irsd200.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml

### Purpose
`nicera,d3323aa.yaml` defines the devicetree schema for Nicera D3-323-AA PIR sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: PIR sensor for human detection. Datasheet: https://www.endrich.com/Datenbl%C3%A4tter/Sensoren/D3-323-AA_e.pdf Maintainer coverage is Waqar Hameed <waqar.hameed@axis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/nicera,d3323aa.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `nicera,d3323aa`. Top-level required properties are `compatible`, `vdd-supply`, `vout-clk-gpios`, `data-gpios`. Important property contracts include: `vdd-supply` (Supply voltage (1.8 to 5.5 V).); `vout-clk-gpios` (max 1 item(s); GPIO for clock and detection. After reset, the device signals with two falling edges on this pin that it is ready for...); `data-gpios` (max 1 item(s); GPIO for data reading and writing. This is denoted "DO (SI)" in datasheet. During configuration, this pin is used for...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/nicera,d3323aa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml

### Purpose
`parallax-ping.yaml` defines the devicetree schema for Parallax PING))) and LaserPING range finder. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Bit-banging driver using one GPIO: - ping-gpios is raised by the driver to start measurement - direction of ping-gpio is then switched into input with an interrupt for receiving distance value as PWM signal Specifications about the devices can be found at: http://parallax.com/sites/default/files/downloads/28041-LaserPING-2m-Rangefinder-Guide.pdf http://parallax.com/sites/default/files/downloads/28015-PING-Documentation-v1.6.pdf Maintainer coverage is Andreas Klinger <ak@it-klinger.de>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/parallax-ping.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `parallax,ping`, `parallax,laserping`. Top-level required properties are `compatible`, `ping-gpios`. Important property contracts include: `ping-gpios` (max 1 item(s); Definition of the GPIO for the triggering and echo (output and input) This GPIO is set for about 5 us by the driver t...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/parallax-ping.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml

### Purpose
`rfdigital,rfd77402.yaml` defines the devicetree schema for RF Digital RFD77402 ToF sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The RF Digital RFD77402 is a Time-of-Flight (ToF) proximity and distance sensor providing up to 200 mm range measurement over an I2C interface. Maintainer coverage is Shrikant Raskar <raskar.shree97@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/rfdigital,rfd77402.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `rfdigital,rfd77402`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Interrupt asserted when a new distance measurement is available.); `vdd-supply` (Regulator that provides power to the sensor.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/rfdigital,rfd77402.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml

### Purpose
`semtech,sx9310.yaml` defines the devicetree schema for Semtech's SX9310 capacitive proximity sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Semtech's SX9310/SX9311 capacitive proximity/button solution. Specifications about the devices can be found at: https://www.semtech.com/products/smart-sensing/sar-sensors/sx9310 Maintainer coverage is Daniel Campello <campello@chromium.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/semtech,sx9310.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `semtech,sx9310`, `semtech,sx9311`. Top-level required properties are `compatible`, `reg`, `#io-channel-cells`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); The sole interrupt generated by the device used to announce the preceding reading request has finished and that data...); `vdd-supply` (Main power supply); `svdd-supply` (Host interface power supply); `#io-channel-cells` (const `1`); `semtech,cs0-ground` (type `boolean`; Indicates the CS0 sensor is connected to ground.); `semtech,combined-sensors` (1-4 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; List of which sensors are combined and represented by CS3. Possible values are - 3 - CS3 (internal) 0 1 - CS0 + CS1 1...); `semtech,resolution` (enum `coarsest`, `very-coarse`, `coarse`, `medium-coarse`, `medium`, `fine`, `very-fine`, `finest`; Capacitance measure resolution. Refer to datasheet for more details.); `semtech,startup-sensor` (enum `0`, `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; default `0`; Sensor used for start-up proximity detection. The combined sensor is represented by the value 3. This is used for ini...); `semtech,proxraw-strength` (enum `0`, `2`, `4`, `8`; ref `/schemas/types.yaml#/definitions/uint32`; default `2`; PROXRAW filter strength. A value of 0 represents off, and other values represent 1-1/N.); `semtech,avg-pos-strength` (enum `0`, `16`, `64`, `128`, `256`, `512`, `1024`, `4294967295`; ref `/schemas/types.yaml#/definitions/uint32`; default `16`; Average positive filter strength. A value of 0 represents off and UINT_MAX (4294967295) represents infinite. Other va...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/iio/iio.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `svdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `semtech,cs0-ground`, `semtech,combined-sensors`, `semtech,resolution`, `semtech,startup-sensor`, `semtech,proxraw-strength`, `semtech,avg-pos-strength` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9310.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml

### Purpose
`semtech,sx9324.yaml` defines the devicetree schema for Semtech's SX9324 capacitive proximity sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Semtech's SX9324 proximity sensor. Maintainer coverage is Gwendal Grignou <gwendal@chromium.org>, Daniel Campello <campello@chromium.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/semtech,sx9324.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `semtech,sx9324`. Top-level required properties are `compatible`, `reg`, `#io-channel-cells`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Generated by device to announce preceding read request has finished and data is available or that a close/far proximi...); `vdd-supply` (Main power supply); `svdd-supply` (Host interface power supply); `#io-channel-cells` (const `1`); `semtech,ph0-pin` (3-3 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; Array of 3 entries. Index represent the id of the CS pin. Value indicates how each CS pin is used during phase 0. Eac...); `semtech,ph1-pin` (3-3 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; Same as ph0-pin for phase 1.); `semtech,ph2-pin` (3-3 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; Same as ph0-pin for phase 2.); `semtech,ph3-pin` (3-3 item(s); ref `/schemas/types.yaml#/definitions/uint32-array`; Same as ph0-pin for phase 3.); `semtech,ph01-resolution` (enum `8`, `16`, `32`, `64`, `128`, `256`, `512`, `1024`; ref `/schemas/types.yaml#/definitions/uint32`; default `128`; Capacitance measurement resolution. For phase 0 and 1. Higher the number, higher the resolution.); `semtech,ph23-resolution` (enum `8`, `16`, `32`, `64`, `128`, `256`, `512`, `1024`; ref `/schemas/types.yaml#/definitions/uint32`; default `128`; Capacitance measurement resolution. For phase 2 and 3); `semtech,startup-sensor` (enum `0`, `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; default `0`; Phase used for start-up proximity detection. It is used when we enable a phase to remove static offset and measure on...); `semtech,ph01-proxraw-strength` (range 0..7; ref `/schemas/types.yaml#/definitions/uint32`; default `1`; PROXRAW filter strength for phase 0 and 1. A value of 0 represents off, and other values represent 1-1/2^N.); `semtech,ph23-proxraw-strength` (range 0..7; ref `/schemas/types.yaml#/definitions/uint32`; default `1`; Same as proxraw-strength01, for phase 2 and 3.); `semtech,avg-pos-strength` (enum `0`, `16`, `64`, `128`, `256`, `512`, `1024`, `4294967295`; ref `/schemas/types.yaml#/definitions/uint32`; default `16`; Average positive filter strength. A value of 0 represents off and UINT_MAX (4294967295) represents infinite. Other va...); `semtech,cs-idle-sleep` (enum `hi-z`, `gnd`, `vdd`; State of CS pins during sleep mode and idle time.); `semtech,int-comp-resistor` (enum `lowest`, `low`, `high`, `highest`; Internal resistor setting for compensation.); `semtech,input-precharge-resistor-ohms` (range 0..30000; default `4000`; Pre-charge input resistance in Ohm.); plus 1 additional property schema(s).
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/iio/iio.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `svdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `semtech,ph0-pin`, `semtech,ph1-pin`, `semtech,ph2-pin`, `semtech,ph3-pin`, `semtech,ph01-resolution`, `semtech,ph23-resolution`, `semtech,startup-sensor`, `semtech,ph01-proxraw-strength`, ... encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9324.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml

### Purpose
`semtech,sx9360.yaml` defines the devicetree schema for Semtech's SX9360 capacitive proximity sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Semtech's SX9360 proximity sensor. Maintainer coverage is Gwendal Grignou <gwendal@chromium.org>, Daniel Campello <campello@chromium.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/semtech,sx9360.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `semtech,sx9360`. Top-level required properties are `compatible`, `reg`, `#io-channel-cells`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Generated by device to announce preceding read request has finished and data is available or that a close/far proximi...); `vdd-supply` (Main power supply); `svdd-supply` (Host interface power supply); `#io-channel-cells` (const `1`); `semtech,resolution` (enum `8`, `16`, `32`, `64`, `128`, `256`, `512`, `1024`; ref `/schemas/types.yaml#/definitions/uint32`; default `128`; Capacitance measurement resolution. For both phases, "reference" and "measurement". Higher the number, higher the res...); `semtech,proxraw-strength` (range 0..7; ref `/schemas/types.yaml#/definitions/uint32`; default `1`; PROXRAW filter strength for both phases. A value of 0 represents off, and other values represent 1-1/2^N.); `semtech,avg-pos-strength` (enum `0`, `16`, `64`, `128`, `256`, `512`, `1024`, `4294967295`; ref `/schemas/types.yaml#/definitions/uint32`; default `16`; Average positive filter strength. A value of 0 represents off and UINT_MAX (4294967295) represents infinite. Other va...); `semtech,input-precharge-resistor-ohms` (range 0..30000; default `0`; Pre-charge input resistance in Ohm.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are `#io-channel-cells` (const `1`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `svdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `semtech,resolution`, `semtech,proxraw-strength`, `semtech,avg-pos-strength`, `semtech,input-precharge-resistor-ohms` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9360.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml

### Purpose
`semtech,sx9500.yaml` defines the devicetree schema for Semtech's SX9500 capacitive proximity button device. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/semtech,sx9500.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `semtech,sx9500`. Top-level required properties are `compatible`, `reg`, `interrupts`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `reset-gpios` (max 1 item(s); GPIO connected to the active low reset pin.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/semtech,sx9500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml

### Purpose
`st,vl53l0x.yaml` defines the devicetree schema for ST VL53L0X/VL53L1X ToF ranging sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Song Qiang <songqiang1304521@gmail.com>, Siratul Islam <email@sirat.me>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/st,vl53l0x.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,vl53l0x`, `st,vl53l1x`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `reset-gpios` (max 1 item(s); Phandle to the XSHUT GPIO. Used for hardware reset.); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 1 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/st,vl53l0x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml

### Purpose
`tyhx,hx9023s.yaml` defines the devicetree schema for TYHX HX9023S capacitive proximity sensor. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: TYHX HX9023S proximity sensor. Datasheet can be found here: http://www.tianyihexin.com/ueditor/php/upload/file/20240614/1718336303992081.pdf Maintainer coverage is Yasin Lee <yasin.lee.x@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/tyhx,hx9023s.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `tyhx,hx9023s`. Top-level required properties are `compatible`, `reg`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s); Generated by device to announce preceding read request has finished and data is available or that a close/far proximi...); `vdd-supply` allowed with common binding semantics; `firmware-name` (max 1 item(s)); `#address-cells` (const `1`); `#size-cells` (const `0`)
Child-node API is expressed through `patternProperties`: `^channel@[0-4]$`.
Local reusable definitions are none. Provider or bus cell contracts are `#address-cells` (const `1`); `#size-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/iio/adc/adc.yaml`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Nested child-node schemas add risk because missing `#address-cells`, `#size-cells`, `reg`, or phandle links can pass local review but fail dtbs_check for real boards. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/tyhx,hx9023s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml

### Purpose
`vishay,vcnl3020.yaml` defines the devicetree schema for Integrated Proximity Sensor With Infrared Emitter. It is an IIO proximity binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The VCNL3020 is a fully integrated proximity sensor. Fully integrated means that the infrared emitter is included in the package. It has 16-bit resolution. It includes a signal processing IC and features standard I2C communication interface. It features an interrupt function. Specifications about the devices can be found at: https://www.vishay.com/docs/84150/vcnl3020.pdf Maintainer coverage is Ivan Mikhaylov <i.mikhaylov@yadro.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/proximity/vishay,vcnl3020.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `vishay,vcnl3020`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` (Regulator that provides power to the sensor); `vddio-supply` (Regulator that provides power to the bus); `vishay,led-current-microamp` (enum `0`, `10000`, `20000`, `30000`, `40000`, `50000`, `60000`, `70000`, `80000`, `90000`, `100000`, `110000`, ...; default `20000`; The driver current for the LED used in proximity sensing.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO proximity drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `vishay,led-current-microamp` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/proximity/vishay,vcnl3020.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml

### Purpose
`adi,ad2s1210.yaml` defines the devicetree schema for Analog Devices AD2S1210 Resolver-to-Digital Converter. It is an IIO resolver binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The AD2S1210 is a complete 10-bit to 16-bit resolution tracking resolver-to-digital converter, integrating an on-board programmable sinusoidal oscillator that provides sine wave excitation for resolvers. The AD2S1210 allows the user to read the angular position or the angular velocity data directly from the parallel outputs or through the serial interface. The mode of operation of the communication channel (parallel or serial) is selected by t... Maintainer coverage is Michael Hennerich <michael.hennerich@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/resolver/adi,ad2s1210.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,ad2s1210`. Top-level required properties are `compatible`, `reg`, `spi-cpha`, `avdd-supply`, `dvdd-supply`, `vdrive-supply`, `clocks`, `sample-gpios`, `assigned-resolution-bits`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..25000000); `spi-cpha` allowed with common binding semantics; `avdd-supply` (A 4.75 to 5.25 V regulator that powers the Analog Supply Voltage (AVDD) pin.); `dvdd-supply` (A 4.75 to 5.25 V regulator that powers the Digital Supply Voltage (DVDD) pin.); `vdrive-supply` (A 2.3 to 5.25 V regulator that powers the Logic Power Supply Input (VDrive) pin.); `clocks` (max 1 item(s); External oscillator clock (CLKIN).); `reset-gpios` (max 1 item(s); GPIO connected to the /RESET pin. As the line needs to be low for the reset to be active, it should be configured as...); `sample-gpios` (max 1 item(s); GPIO connected to the /SAMPLE pin. As the line needs to be low to trigger a sample, it should be configured as GPIO_A...); `mode-gpios` (2-2 item(s); GPIO lines connected to the A0 and A1 pins. These pins select the data transfer mode.); `resolution-gpios` (2-2 item(s); GPIO lines connected to the RES0 and RES1 pins. These pins select the resolution of the digital output. If omitted, i...); `fault-gpios` (2-2 item(s); GPIO lines connected to the LOT and DOS pins. These pins combined indicate the type of fault present, if any. As thes...); `adi,fixed-mode` (enum `config`, `velocity`, `position`; ref `/schemas/types.yaml#/definitions/string`; This is used to indicate the selected mode if A0 and A1 are hard-wired instead of connected to GPIOS (i.e. mode-gpios...); `assigned-resolution-bits` (enum `10`, `12`, `14`, `16`; Resolution of the digital output required by the application. This determines the precision of the angle and/or the m...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/string`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; regulator supplies: `avdd-supply`, `dvdd-supply`, `vdrive-supply`; clock framework: `clocks`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO resolver drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,fixed-mode` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s1210.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml

### Purpose
`adi,ad2s90.yaml` defines the devicetree schema for Analog Devices AD2S90 Resolver-to-Digital Converter. It is an IIO resolver binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Datasheet: https://www.analog.com/en/products/ad2s90.html Maintainer coverage is Matheus Tavares <matheus.bernardino@usp.br>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/resolver/adi,ad2s90.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,ad2s90`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `spi-max-frequency` (range ..830000; Chip's max frequency, as specified in its datasheet, is 2Mhz. But a 600ns delay is expected between the application o...); `spi-cpol` allowed with common binding semantics; `spi-cpha` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO resolver drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/resolver/adi,ad2s90.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml

### Purpose
`samsung,sensorhub-rinato.yaml` defines the devicetree schema for Samsung Sensorhub driver. It is an generic IIO binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Sensorhub is a MCU which manages several sensors and also plays the role of a virtual sensor device. Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/samsung,sensorhub-rinato.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `samsung,sensorhub-rinato`, `samsung,sensorhub-thermostat`. Top-level required properties are `compatible`, `reg`, `interrupts`, `ap-mcu-gpios`, `mcu-ap-gpios`, `mcu-reset-gpios`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `ap-mcu-gpios` (max 1 item(s); Application Processor to sensorhub line - used during communication); `mcu-ap-gpios` (max 1 item(s); Sensorhub to Application Processor - used during communication); `mcu-reset-gpios` (max 1 item(s); Reset the sensorhub.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO iio drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/samsung,sensorhub-rinato.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml

### Purpose
`st,st-sensors.yaml` defines the devicetree schema for STMicroelectronics MEMS sensors. It is an generic IIO binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: The STMicroelectronics sensor devices are pretty straight-forward I2C or SPI devices, all sharing the same device tree descriptions no matter what type of sensor it is. Note that whilst this covers many STMicro MEMs sensors, some more complex IMUs need their own bindings. Maintainer coverage is Denis Ciocca <denis.ciocca@st.com>, Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/st,st-sensors.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `st,h3lis331dl-accel`, `st,lis2de12`, `st,lis2dw12`, `st,lis2hh12`, `st,lis2dh12-accel`, `st,lis2ds12`, `st,lis302dl`, `st,lis331dl-accel`, `st,lis331dlh-accel`, `st,lis3de`, `st,lis3dh-accel`, `st,lis3dhh`, `st,lis3l02dq`, `st,lis3lv02dl-accel`, `st,lng2dm-accel`, `st,lsm303agr-accel`, `st,lsm303c-accel`, `st,lsm303dl-accel`, `st,lsm303dlh-accel`, `st,lsm303dlhc-accel`, `st,lsm303dlm-accel`, `st,lsm330-accel`, `st,lsm330d-accel`, `st,lsm330dl-accel`, `st,lsm330dlc-accel`, `st,iis328dq`, `silan,sc7a20`, `st,l3g4200d-gyro`, `st,l3g4is-gyro`, `st,l3gd20-gyro`, `st,l3gd20h-gyro`, `st,lsm330-gyro`, `st,lsm330d-gyro`, `st,lsm330dl-gyro`, `st,lsm330dlc-gyro`, `st,lsm9ds0-gyro`, `st,iis2mdc`, `st,lis2mdl`, `st,lis3mdl-magn`, `st,lsm303agr-magn`, ... (57 total). Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-2 item(s); interrupt line(s) connected to the DRDY line(s) and/or the Inertial interrupt lines INT1 and INT2 if these exist. Thi...); `vdd-supply` allowed with common binding semantics; `vddio-supply` allowed with common binding semantics; `st,drdy-int-pin` (enum `1`, `2`; ref `/schemas/types.yaml#/definitions/uint32`; the pin on the package that will be used to signal "data ready" (valid values 1 or 2). This property is not configura...); `drive-open-drain` (ref `/schemas/types.yaml#/definitions/flag`; the interrupt/data ready line will be configured as open drain, which is useful if several sensors share the same int...); `mount-matrix` (an optional 3x3 mounting rotation matrix.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 2 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`. Integration hints from the schema and examples are: SPI; I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vddio-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO iio drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `st,drdy-int-pin` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/st,st-sensors.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml

### Purpose
`adi,ltc2983.yaml` defines the devicetree schema for Analog Devices LTC2983, LTC2986, LTM2985 Multi-sensor Temperature system. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Analog Devices LTC2983, LTC2984, LTC2986, LTM2985 Multi-Sensor Digital Temperature Measurement Systems https://www.analog.com/media/en/technical-documentation/data-sheets/2983fc.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/2984fb.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/29861fa.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ltm2985.pdf Maintainer coverage is Nuno Sa <nuno.sa@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/adi,ltc2983.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,ltc2983`, `adi,ltc2986`, `adi,ltm2985`, `adi,ltc2984`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vdd-supply`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `adi,mux-delay-config-us` (range ..255; default `0`; Extra delay prior to each conversion, in addition to the internal 1ms delay, for the multiplexer to switch input conf...); `adi,filter-notch-freq` (range 0..2; ref `/schemas/types.yaml#/definitions/uint32`; default `0`; Notch frequency of the digital filter. 0 - 50/60Hz rejection 1 - 60Hz rejection 2 - 50Hz rejection); `#address-cells` (const `1`); `#size-cells` (const `0`)
Child-node API is expressed through `patternProperties`: `^thermocouple@` (Thermocouple sensor.); `^diode@` (Diode sensor.); `^rtd@` (RTD sensor.); required `adi,rsense-handle`; `^thermistor@` (Thermistor sensor.); required `adi,rsense-handle`; `^adc@` (Direct ADC sensor.); `^temp@` (Active analog temperature sensor.); required `adi,custom-temp`; `^rsense@` (Sense resistor sensor.); required `adi,rsense-val-milli-ohms`.
Local reusable definitions are `sensor-node`. Provider or bus cell contracts are `#address-cells` (const `1`); `#size-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 6 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `#/$defs/sensor-node`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/int64-matrix`, `/schemas/types.yaml#/definitions/uint64-matrix`, `/schemas/types.yaml#/definitions/uint32-array`. Integration hints from the schema and examples are: SPI; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `adi,mux-delay-config-us`, `adi,filter-notch-freq` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Nested child-node schemas add risk because missing `#address-cells`, `#size-cells`, `reg`, or phandle links can pass local review but fail dtbs_check for real boards. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/adi,ltc2983.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml

### Purpose
`maxim,max31855k.yaml` defines the devicetree schema for Maxim MAX31855 and similar thermocouples. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://datasheets.maximintegrated.com/en/ds/MAX6675.pdf https://datasheets.maximintegrated.com/en/ds/MAX31855.pdf Maintainer coverage is Matt Ranostay <matt.ranostay@konsulko.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/maxim,max31855k.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max6675`, `maxim,max31855`, `maxim,max31855k`, `maxim,max31855j`, `maxim,max31855n`, `maxim,max31855s`, `maxim,max31855t`, `maxim,max31855e`, `maxim,max31855r`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `spi-cpha` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 2 top-level `allOf` entry(s), 1 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31855k.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml

### Purpose
`maxim,max31856.yaml` defines the devicetree schema for Maxim MAX31856 thermocouple support. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://datasheets.maximintegrated.com/en/ds/MAX31856.pdf Maintainer coverage is Jonathan Cameron <jic23@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/maxim,max31856.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max31856`. Top-level required properties are `compatible`, `reg`, `spi-cpha`. Important property contracts include: `reg` (max 1 item(s)); `spi-cpha` allowed with common binding semantics; `thermocouple-type` (ref `/schemas/types.yaml#/definitions/uint32`; Type of thermocouple (THERMOCOUPLE_TYPE_K if omitted). Use defines in dt-bindings/iio/temperature/thermocouple.h. Sup...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31856.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml

### Purpose
`maxim,max31865.yaml` defines the devicetree schema for Maxim MAX31865 Resistance Temperature Detector.. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://datasheets.maximintegrated.com/en/ds/MAX31865.pdf Maintainer coverage is Navin Sankar Velliangiri <navin@linumiz.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/maxim,max31865.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `maxim,max31865`. Top-level required properties are `compatible`, `reg`, `spi-cpha`. Important property contracts include: `reg` (max 1 item(s)); `maxim,3-wire` (type `boolean`; Identifies the number of wires used by the RTD. Setting this property enables 3-wire RTD connection. Else 2-wire or 4...); `spi-cpha` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Integration hints from the schema and examples are: SPI. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `maxim,3-wire` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/maxim,max31865.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml

### Purpose
`melexis,mlx90614.yaml` defines the devicetree schema for Melexis MLX90614/MLX90615 contactless IR temperature sensor. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: http://melexis.com/Infrared-Thermometer-Sensors/Infrared-Thermometer-Sensors/MLX90614-615.aspx Maintainer coverage is Peter Meerwald <pmeerw@pmeerw.net>, Crt Mori <cmo@melexis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/melexis,mlx90614.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `melexis,mlx90614`, `melexis,mlx90615`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `wakeup-gpios` (max 1 item(s); GPIO connected to the SDA line to hold low in order to wake up the device. In normal operation, the GPIO is set as in...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90614.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml

### Purpose
`melexis,mlx90632.yaml` defines the devicetree schema for Melexis MLX90632 and MLX90635 contactless Infra Red temperature sensor. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90632 There are various applications for the Infra Red contactless temperature sensor and MLX90632 is most suitable for consumer applications where measured object temperature is in range between -20 to 200 degrees Celsius with relative error of measurement below 1 degree Celsius in object temperature range for industrial applications. Since it can operate and measure a... Maintainer coverage is Crt Mori <cmo@melexis.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/melexis,mlx90632.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `melexis,mlx90632`, `melexis,mlx90635`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s); Default is 0x3a, but can be reprogrammed.); `vdd-supply` (provide VDD power to the sensor.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/melexis,mlx90632.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml

### Purpose
`microchip,mcp9600.yaml` defines the devicetree schema for Microchip MCP9600 and similar thermocouple EMF converters. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: https://ww1.microchip.com/downloads/en/DeviceDoc/MCP960X-Data-Sheet-20005426.pdf Maintainer coverage is Andrew Hepp <andrew.hepp@ahepp.dev>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/microchip,mcp9600.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `microchip,mcp9600`, `microchip,mcp9601`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `interrupts` (1-6 item(s)); `interrupt-names` (1-6 item(s)); `thermocouple-type` (ref `/schemas/types.yaml#/definitions/uint32`; default `3`; Type of thermocouple (THERMOCOUPLE_TYPE_K if omitted). Use defines in dt-bindings/iio/temperature/thermocouple.h. Sup...); `microchip,vsense` (type `boolean`; This flag indicates that the chip has been wired with VSENSE to enable open and short circuit detect.); `vdd-supply` allowed with common binding semantics
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 2 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 1 top-level `allOf` entry(s), 1 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/types.yaml#/definitions/uint32`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Vendor-specific properties such as `microchip,vsense` encode device configuration and are easy to mismatch against datasheet units or driver expectations. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/microchip,mcp9600.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml

### Purpose
`ti,tmp006.yaml` defines the devicetree schema for TI TMP006 IR thermopile sensor. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: TI TMP006 - Infrared Thermopile Sensor in Chip-Scale Package. https://cdn.sparkfun.com/datasheets/Sensors/Temp/tmp006.pdf Maintainer coverage is Peter Meerwald <pmeerw@pmeerw.net>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/ti,tmp006.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,tmp006`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` (provide VDD power to the sensor.); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp006.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml

### Purpose
`ti,tmp007.yaml` defines the devicetree schema for IR thermopile sensor with integrated math engine. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: http://www.ti.com/lit/ds/symlink/tmp007.pdf Maintainer coverage is Manivannan Sadhasivam <manivannanece23@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/ti,tmp007.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,tmp007`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s); The I2C address of the sensor (changeable via ADR pins) ------------------------------ |ADR1 | ADR0 | Device Address|...); `interrupts` (max 1 item(s))
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; interrupt-capable. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp007.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml

### Purpose
`ti,tmp117.yaml` defines the devicetree schema for TI TMP117 - Digital temperature sensor with integrated NV memory. It is an IIO temperature binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: TI TMP116/117 - Digital temperature sensor with integrated NV memory that supports I2C interface. https://www.ti.com/lit/gpn/tmp116 https://www.ti.com/lit/gpn/tmp117 Maintainer coverage is Puranjay Mohan <puranjay12@gmail.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/temperature/ti,tmp117.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `ti,tmp116`, `ti,tmp117`. Top-level required properties are `compatible`, `reg`, `vcc-supply`. Important property contracts include: `reg` (max 1 item(s)); `vcc-supply` (provide VCC power to the sensor.); `label` (Unique name to identify which device this is.)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C; regulator supplies: `vcc-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO temperature drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/temperature/ti,tmp117.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/incomplete-devices.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/incomplete-devices.yaml

### Purpose
`incomplete-devices.yaml` defines the devicetree schema for Rejected, Legacy or Incomplete Devices. It is a repository-wide compatibility quarantine schema: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Some devices will not or should not get a proper Devicetree bindings, but their compatibles are present in Linux drivers for various reasons. Examples are devices using ACPI PRP0001 with non-updatable firmware/ACPI tables or old PowerPC platforms without in-tree DTS. Following list of devices is an incomplete schema with a goal to pass DT schema checks on undocumented compatibles but also reject any DTS file using such un-approved compatible.... Maintainer coverage is Rob Herring <robh@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/incomplete-devices.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `broadcom,bcm5241`, `ltr,ltrf216a`, `AAPL,3500`, `AAPL,7500`, `AAPL,8500`, `AAPL,9500`, `AAPL,accelerometer_1`, `AAPL,e411`, `AAPL,Gossamer`, `AAPL,PowerBook1998`, `AAPL,ShinerESB`, `adm1030`, `amd-0137`, `B5221`, `bmac+`, `burgundy`, `cobalt`, `cy28508`, `daca`, `fcu`, `gatwick`, `gmac`, `heathrow`, `heathrow-ata`, `heathrow-media-bay`, `i2sbus`, `i2s-modem`, `iMac`, `K2-GMAC`, `k2-i2c`, `K2-Keylargo`, `K2-UATA`, `kauai-ata`, `Keylargo`, `keylargo-ata`, `keylargo-media-bay`, `lm87cimt`, `MAC,adm1030`, `MAC,ds1775`, `MacRISC`, ... (220 total). Top-level required properties are `compatible`, `broken-usage-of-incorrect-compatible`. Important property contracts include: No top-level properties beyond the compatible matcher are declared.
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 0 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 1 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: I2C. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This schema integrates with the global devicetree validation pass as a negative/legacy compatibility list. Its compatible enums let schema tooling recognize names present in Linux drivers or immutable firmware while still documenting that new DTS usage is not approved. It is not tied to a single subsystem driver and should be treated as an exception list for ACPI PRP0001, old PowerPC/SPARC platforms, and other legacy cases.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/incomplete-devices.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/incomplete-devices.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/incomplete-devices.yaml -->
