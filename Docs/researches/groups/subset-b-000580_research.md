# Research Group: subset-b-000580

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adafruit,seesaw-gamepad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adafruit,seesaw-gamepad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adafruit,seesaw-gamepad.yaml` is a Linux devicetree YAML schema for a input binding schema: **Adafruit Mini I2C Gamepad with seesaw**. Adafruit Mini I2C Gamepad +-----------------------------+ | ___ | | / \ (X) | | | S | __ __ (Y) (A) | | \___/ |ST| |SE| (B) | | | +-----------------------------+ S -> 10-bit precision bidirectional analog joystick ST -> Start SE -> Select X, A, B, Y ->... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `adafruit,seesaw-gamepad`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Anshul Dalal <anshulusr@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`.
- `compatible`: const `adafruit,seesaw-gamepad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1; The gamepad's IRQ pin triggers a rising edge if interrupts are enabled..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adafruit,seesaw-gamepad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 63-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adafruit,seesaw-gamepad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml` is a Linux devicetree YAML schema for a joystick binding: **ADC attached joystick**. Bindings for joystick devices connected to ADC controllers supporting the Industrial I/O subsystem. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `io-channels`, `#address-cells`, `#size-cells`.
- Maintainers: Artur Rojek <contact@artur-rojek.eu>.
- Top-level properties: `compatible`, `io-channels`, `poll-interval`, `#address-cells`, `#size-cells`.
- `compatible`: const `adc-joystick`.
- `io-channels`: maxItems 1024; minItems 1; List of phandle and IIO specifier pairs. Each pair defines one ADC channel to which a joystick axis is connected. See https://github.com/devicetree-org/dt-schema/blob/master/schemas/iio/iio-consumer.yaml for details..
- `poll-interval`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^axis@[0-9a-f]+$` child nodes with required `reg`, `linux,code`, `abs-range` and properties `reg`, `linux,code`, `abs-range`, `abs-fuzz`, `abs-flat`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `io-channels`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adc-joystick.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 127-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **ADC attached resistor ladder buttons**. The file describes the devicetree contract for the ADC attached resistor ladder buttons. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `io-channels`, `io-channel-names`, `keyup-threshold-microvolt`.
- Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>.
- Top-level properties: `compatible`, `io-channels`, `io-channel-names`, `keyup-threshold-microvolt`, `poll-interval`, `autorepeat`.
- `compatible`: const `adc-keys`.
- `io-channels`: maxItems 1.
- `poll-interval`.
- `io-channel-names`: const `buttons`.
- `keyup-threshold-microvolt`: Voltage above or equal to which all the keys are considered up..
- `autorepeat`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^button-` child nodes with required `linux,code`, `press-threshold-microvolt` and properties `label`, `linux,code`, `press-threshold-microvolt`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `io-channels`, `io-channel-names`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adc-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 103-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adi,adp5588.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adi,adp5588.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adi,adp5588.yaml` is a Linux devicetree YAML schema for a keypad binding: **Analog Devices ADP5588 Keypad Controller**. Analog Devices Mobile I/O Expander and QWERTY Keypad Controller https://www.analog.com/media/en/technical-documentation/data-sheets/ADP5588.pdf It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `adi,adp5587`, `adi,adp5588`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Nuno Sá <nuno.sa@analog.com>.
- Top-level properties: `compatible`, `reg`, `vcc-supply`, `reset-gpios`, `interrupts`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `adi,unlock-keys`.
- `compatible`: enum `adi,adp5587`, `adi,adp5588`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; If specified, it will be asserted during driver probe. As the line is active low, it should be marked GPIO_ACTIVE_LOW..
- `vcc-supply`: Supply Voltage Input.
- `gpio-controller`: This property applies if either keypad,num-rows lower than 8 or keypad,num-columns lower than 10..
- `#gpio-cells`: const `2`.
- `interrupt-controller`: This property applies if either keypad,num-rows lower than 8 or keypad,num-columns lower than 10. This property is optional if keypad,num-rows or keypad,num-columns are not specified as the device is then configured to be used purely for gpio during which....
- `#interrupt-cells`: const `2`.
- `adi,unlock-keys`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 2; minItems 1; Specifies a maximum of 2 keys that can be used to unlock the keypad. If this property is set, the keyboard will be locked and only unlocked after these keys are pressed. If only one key is set, a double click is needed to unlock the keypad. The value of....
- Shared-schema dependencies are pulled with `$ref`: `matrix-keymap.yaml#`, `input.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `vcc-supply`, `reset-gpios`, `interrupts`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adi,adp5588.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 139-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adi,adp5588.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Allwinner A10 LRADC**. The file describes the devicetree contract for the Allwinner A10 LRADC. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `allwinner,sun4i-a10-lradc-keys`, `allwinner,sun8i-a83t-r-lradc`, `allwinner,suniv-f1c100s-lradc`, `allwinner,sun50i-a64-lradc`, `allwinner,sun50i-r329-lradc`, `allwinner,sun50i-h616-lradc`, `allwinner,sun20i-d1-lradc`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vref-supply`.
- Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.
- Top-level properties: `compatible`, `reg`, `clocks`, `resets`, `interrupts`, `vref-supply`, `wakeup-source`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `clocks`: maxItems 1.
- `resets`: maxItems 1.
- `vref-supply`: Regulator for the LRADC reference voltage.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^button-[0-9]+$` child nodes with required `label`, `linux,code`, `channel`, `voltage` and properties `label`, `linux,code`, `channel`, `voltage`
- Conditional validation: if `allwinner,sun50i-r329-lradc`: require `clocks`, `resets` / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clocks`, `resets`, `interrupts`, `vref-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 120-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ariel-pwrbutton.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ariel-pwrbutton.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ariel-pwrbutton.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Dell Wyse 3020 a.k.a. "Ariel" Power Button**. The ENE Embedded Controller on the Ariel board has an interface to the SPI bus that is capable of sending keyboard and mouse data. A single power button is attached to it. This binding describes this configuration. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `dell,wyse-ariel-ec-input`, `ene,kb3930-input`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Lubomir Rintel <lkundrak@v3.sk>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `spi-max-frequency`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `spi-max-frequency`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ariel-pwrbutton.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 58-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ariel-pwrbutton.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,captouch.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,captouch.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,captouch.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Atmel capacitive touch device**. Atmel capacitive touch device, typically an Atmel touch sensor connected to AtmegaXX MCU running firmware based on Qtouch library. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `atmel,captouch`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `linux,keycodes`.
- Maintainers: Dharma balasubiramani <dharma.b@microchip.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `linux,keycodes`.
- `compatible`: const `atmel,captouch`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 8; minItems 1.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/atmel,captouch.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 59-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,captouch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,maxtouch.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,maxtouch.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,maxtouch.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Atmel maXTouch touchscreen/touchpad**. Atmel maXTouch touchscreen or touchpads such as the mXT244 and similar devices. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `atmel,maxtouch`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Nick Dyer <nick@shmanahar.org>, Linus Walleij <linusw@kernel.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `vdda-supply`, `vdd-supply`, `reset-gpios`, `wake-gpios`, `linux,gpio-keymap`, `linux,keycodes`, `atmel,wakeup-method`, `wakeup-source`.
- `compatible`: const `atmel,maxtouch`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; Optional GPIO specifier for the touchscreen's reset pin (active low). The line must be flagged with GPIO_ACTIVE_LOW..
- `linux,keycodes`: maxItems 8; minItems 1.
- `vdd-supply`: Optional regulator for the VDD digital voltage..
- `wakeup-source`: type `boolean`.
- `vdda-supply`: Optional regulator for the AVDD analog voltage..
- `wake-gpios`: maxItems 1; Optional GPIO specifier for the touchscreen's wake pin (active low). The line must be flagged with GPIO_ACTIVE_LOW..
- `linux,gpio-keymap`: ref `/schemas/types.yaml#/definitions/uint32-array`; When enabled, the SPT_GPIOPWN_T19 object sends messages on GPIO bit changes. An array of up to 8 entries can be provided indicating the Linux keycode mapped to each bit of the status byte, starting at the LSB. Linux keycodes are defined in....
- `atmel,wakeup-method`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`; The WAKE line is an active-low input that is used to wake up the touch controller from deep-sleep mode before communication with the controller could be started. This optional feature used to minimize current consumption when the controller is in deep....
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `touchscreen/touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vdda-supply`, `vdd-supply`, `reset-gpios`, `wake-gpios`, `linux,gpio-keymap`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/atmel,maxtouch.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 121-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/atmel,maxtouch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/awinic,aw86927.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/awinic,aw86927.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/awinic,aw86927.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Awinic AW86927 LRA Haptic IC**. The file describes the devicetree contract for the Awinic AW86927 LRA Haptic IC. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `awinic,aw86927`, `awinic,aw86938`.
- Required top-level fields: `compatible`, `reg`, `reset-gpios`, `interrupts`.
- Maintainers: Griffin Kroah-Hartman <griffin.kroah@fairphone.com>.
- Top-level properties: `compatible`, `reg`, `reset-gpios`, `interrupts`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `reset-gpios`, `interrupts`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/awinic,aw86927.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 53-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/awinic,aw86927.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS7222A/B/C/D Capacitive Touch Controller**. The Azoteq IQS7222A, IQS7222B, IQS7222C and IQS7222D are multichannel capacitive touch controllers that feature additional sensing capabilities. Link to datasheets: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`, `azoteq,iqs7222d`.
- Required top-level fields: `compatible`, `reg`, `irq-gpios`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `irq-gpios`, `reset-gpios`, `azoteq,max-counts`, `azoteq,auto-mode`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-select`, `azoteq,lta-beta-lp`, `azoteq,lta-beta-np`, `azoteq,counts-beta-lp`, `azoteq,counts-beta-np`, `azoteq,lta-fast-beta-lp`, `azoteq,lta-fast-beta-np`, `azoteq,timeout-ati-ms`, `azoteq,rate-ati-ms`, `azoteq,timeout-np-ms`, `azoteq,rate-np-ms`, `azoteq,timeout-lp-ms`, `azoteq,rate-lp-ms`, `azoteq,timeout-ulp-ms`, `azoteq,rate-ulp-ms`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, and 1 more.
- `compatible`: enum `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`, `azoteq,iqs7222d`.
- `reg`: maxItems 1.
- `irq-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low RDY output..
- `reset-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low MCLR input. The device is temporarily held in hardware reset prior to initialization if this property is present..
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `azoteq,max-counts`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the maximum number of conversion periods (counts) that can be reported as follows: 0: 1023 1: 2047 2: 4095 3: 16384.
- `azoteq,auto-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the number of conversions to occur before an interrupt is generated as follows: 0: 4 1: 8 2: 16 3: 32.
- `azoteq,ati-frac-div-fine`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI fine fractional divider..
- `azoteq,ati-frac-div-coarse`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI coarse fractional divider..
- `azoteq,ati-comp-select`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI compensation selection..
- `azoteq,lta-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter damping factor to be applied during low-power mode..
- `azoteq,lta-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter damping factor to be applied during normal-power mode..
- `azoteq,counts-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the counts filter damping factor to be applied during low-power mode..
- `azoteq,counts-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the counts filter damping factor to be applied during normal- power mode..
- `azoteq,lta-fast-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter fast damping factor to be applied during low-power mode..
- `azoteq,lta-fast-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter fast damping factor to be applied during normal-power mode..
- `azoteq,timeout-ati-ms`: Specifies the delay (in ms) before ATI is retried following an ATI error..
- additional schema properties: `azoteq,rate-ati-ms`, `azoteq,timeout-np-ms`, `azoteq,rate-np-ms`, `azoteq,timeout-lp-ms`, `azoteq,rate-lp-ms`, `azoteq,timeout-ulp-ms`, `azoteq,rate-ulp-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, `trackpad`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `input.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^cycle-[0-9]$` child nodes with required none and properties `azoteq,conv-period`, `azoteq,conv-frac`, `azoteq,tx-enable`, `azoteq,rx-float-inactive`, `azoteq,dead-time-enable`, `azoteq,tx-freq-fosc`, `azoteq,vbias-enable`, `azoteq,sense-mode`, `azoteq,iref-enable`, `azoteq,iref-level`, `azoteq,iref-trim`; `^channel-([0-9]|1[0-9])$` child nodes with required none and properties `azoteq,ulp-allow`, `azoteq,ref-select`, `azoteq,ref-weight`, `azoteq,use-prox`, `azoteq,counts-filt-enable`, `azoteq,ati-band`, `azoteq,global-halt`, `azoteq,invert-enable`, `azoteq,dual-direction`, `azoteq,rx-enable`, `azoteq,samp-cap-double`, `azoteq,vref-half`, and 11 more; `^slider-[0-1]$` child nodes with required `azoteq,channel-select` and properties `azoteq,channel-select`, `azoteq,slider-size`, `azoteq,lower-cal`, `azoteq,upper-cal`, `azoteq,top-speed`, `azoteq,bottom-speed`, `azoteq,bottom-beta`, `azoteq,static-beta`, `azoteq,use-prox`, `linux,axis`; `^gpio-[0-2]$` child nodes with required none and properties `drive-open-drain`; `trackpad` object node with required `azoteq,channel-select` and properties `azoteq,channel-select`, `azoteq,num-rows`, `azoteq,num-cols`, `azoteq,top-speed`, `azoteq,bottom-speed`, `azoteq,use-prox`
- Conditional validation: if `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`: require none / constrain `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, `trackpad`; if `azoteq,iqs7222b`, `azoteq,iqs7222c`: require none / constrain none; if `azoteq,iqs7222b`, `azoteq,iqs7222d`: require none / constrain none; if `azoteq,iqs7222b`: require none / constrain none; if `azoteq,iqs7222a`: require none / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `irq-gpios`, `reset-gpios`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 1148-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,cs40l50.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,cs40l50.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,cs40l50.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Cirrus Logic CS40L50 Advanced Haptic Driver**. CS40L50 is a haptic driver with waveform memory, integrated DSP, and closed-loop algorithms. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cirrus,cs40l50`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `reset-gpios`, `vdd-io-supply`.
- Maintainers: James Ogletree <jogletre@opensource.cirrus.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `reset-gpios`, `vdd-a-supply`, `vdd-p-supply`, `vdd-io-supply`, `vdd-b-supply`.
- `compatible`: enum `cirrus,cs40l50`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `vdd-a-supply`: Power supply for internal analog circuits..
- `vdd-p-supply`: Power supply for always-on circuits..
- `vdd-io-supply`: Power supply for digital input/output..
- `vdd-b-supply`: Power supply for the boost converter..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `vdd-a-supply`, `vdd-p-supply`, `vdd-io-supply`, `vdd-b-supply`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/cirrus,cs40l50.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 68-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,cs40l50.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,ep9307-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,ep9307-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,ep9307-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Cirrus ep93xx keypad**. The KPP is designed to interface with a keypad matrix with 2-point contact or 3-point contact keys. The KPP is designed to simplify the software task of scanning a keypad matrix. The KPP is capable of detecting, debouncing, and decoding one or multiple... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cirrus,ep9307-keypad`, `cirrus,ep9312-keypad`, `cirrus,ep9315-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `linux,keymap`.
- Maintainers: Alexander Sverdlin <alexander.sverdlin@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `debounce-delay-ms`, `cirrus,prescale`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `debounce-delay-ms`.
- `cirrus,prescale`: ref `/schemas/types.yaml#/definitions/uint16`; row/column counter pre-scaler load value.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/input/matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint16`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/cirrus,ep9307-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 86-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cirrus,ep9307-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,cyapa.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,cyapa.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,cyapa.yaml` is a Linux devicetree YAML schema for a input binding schema: **Cypress All Points Addressable (APA) I2C Touchpad / Trackpad**. The file describes the devicetree contract for the Cypress All Points Addressable (APA) I2C Touchpad / Trackpad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,cyapa`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wakeup-source`, `vcc-supply`.
- `compatible`: const `cypress,cyapa`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `vcc-supply`: 3.3V power.
- `wakeup-source`.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vcc-supply`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/cypress,cyapa.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 49-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,cyapa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,tm2-touchkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,tm2-touchkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,tm2-touchkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Samsung TM2 touch key controller**. Touch key controllers similar to the TM2 can be found in a wide range of Samsung devices. They are implemented using many different MCUs, but use a similar I2C protocol. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,tm2-touchkey`, `cypress,midas-touchkey`, `cypress,aries-touchkey`, `coreriver,tc360-touchkey`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Stephan Gerhold <stephan@gerhold.net>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `vdd-supply`, `vcc-supply`, `vddio-supply`, `linux,keycodes`.
- `compatible`: enum `cypress,tm2-touchkey`, `cypress,midas-touchkey`, `cypress,aries-touchkey`, `coreriver,tc360-touchkey`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 4; minItems 1.
- `vdd-supply`: Optional regulator for LED voltage, 3.3V..
- `vcc-supply`: Optional regulator for MCU, 1.8V-3.3V (depending on MCU)..
- `vddio-supply`: Optional regulator that provides digital I/O voltage, e.g. for pulling up the interrupt line or the I2C pins..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vdd-supply`, `vcc-supply`, `vddio-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/cypress,tm2-touchkey.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 73-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress,tm2-touchkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress-sf.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress-sf.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress-sf.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Cypress StreetFighter touchkey controller**. The file describes the devicetree contract for the Cypress StreetFighter touchkey controller. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,sf3155`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `avdd-supply`, `vdd-supply`.
- Maintainers: Yassine Oudjana <y.oudjana@protonmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `avdd-supply`, `vdd-supply`, `linux,keycodes`.
- `compatible`: const `cypress,sf3155`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 8; minItems 1.
- `vdd-supply`: Regulator for VDD digital voltage.
- `avdd-supply`: Regulator for AVDD analog voltage.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `avdd-supply`, `vdd-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/cypress-sf.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 61-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/cypress-sf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Dialog Semiconductor DA7280 Low Power High-Definition Haptic Driver**. The file describes the devicetree contract for the Dialog Semiconductor DA7280 Low Power High-Definition Haptic Driver. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `dlg,da7280`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `dlg,actuator-type`, `dlg,const-op-mode`, `dlg,periodic-op-mode`, `dlg,nom-microvolt`, `dlg,abs-max-microvolt`, `dlg,imax-microamp`, `dlg,impd-micro-ohms`.
- Maintainers: Roy Im <roy.im.opensource@diasemi.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `dlg,actuator-type`, `dlg,const-op-mode`, `dlg,periodic-op-mode`, `dlg,nom-microvolt`, `dlg,abs-max-microvolt`, `dlg,imax-microamp`, `dlg,impd-micro-ohms`, `pwms`, `dlg,ps-seq-id`, `dlg,ps-seq-loop`, `dlg,gpi0-seq-id`, `dlg,gpi1-seq-id`, `dlg,gpi2-seq-id`, `dlg,gpi0-mode`, `dlg,gpi1-mode`, `dlg,gpi2-mode`, `dlg,gpi0-polarity`, `dlg,gpi1-polarity`, `dlg,gpi2-polarity`, `dlg,resonant-freq-hz`, `dlg,bemf-sens-enable`, `dlg,freq-track-enable`, `dlg,acc-enable`, `dlg,rapid-stop-enable`, `dlg,amp-pid-enable`, and 1 more.
- `compatible`: const `dlg,da7280`.
- `reg`: maxItems 1; I2C address of the device..
- `interrupts`: maxItems 1.
- `pwms`: maxItems 1.
- `dlg,actuator-type`: enum `LRA`, `ERM-bar`, `ERM-coin`.
- `dlg,const-op-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; Haptic operation mode for FF_CONSTANT.
- `dlg,periodic-op-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; Haptic operation mode for FF_PERIODIC. The default value is 1 for both of the operation modes. For more details, please see the datasheet.
- `dlg,nom-microvolt`: Nominal actuator voltage rating.
- `dlg,abs-max-microvolt`: Absolute actuator maximum voltage rating.
- `dlg,imax-microamp`: Actuator max current rating.
- `dlg,impd-micro-ohms`: Impedance of the actuator.
- `dlg,ps-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; The PS_SEQ_ID(pattern ID in waveform memory inside chip) to play back when RTWM-MODE is enabled.
- `dlg,ps-seq-loop`: ref `/schemas/types.yaml#/definitions/uint32`; The PS_SEQ_LOOP, Number of times the pre-stored sequence pointed to by PS_SEQ_ID or GPI(N)_SEQUENCE_ID is repeated.
- `dlg,gpi0-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI0_SEQUENCE_ID, pattern to play when gpi0 is triggered.
- `dlg,gpi1-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI1_SEQUENCE_ID, pattern to play when gpi1 is triggered.
- `dlg,gpi2-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI2_SEQUENCE_ID, pattern to play when gpi2 is triggered.
- `dlg,gpi0-mode`: enum `Single-pattern`, `Multi-pattern`; Pattern mode for gpi0.
- `dlg,gpi1-mode`: enum `Single-pattern`, `Multi-pattern`; Pattern mode for gpi1.
- additional schema properties: `dlg,gpi2-mode`, `dlg,gpi0-polarity`, `dlg,gpi1-polarity`, `dlg,gpi2-polarity`, `dlg,resonant-freq-hz`, `dlg,bemf-sens-enable`, `dlg,freq-track-enable`, `dlg,acc-enable`, `dlg,rapid-stop-enable`, `dlg,amp-pid-enable`, `dlg,mem-array`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `pwms`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/dlg,da7280.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 248-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Dialog DA9061/62/63 OnKey Module**. This module is part of the DA9061/DA9062/DA9063. For more details about entire DA906{1,2,3} chips see Documentation/devicetree/bindings/mfd/dlg,da9063.yaml This module provides the KEY_POWER event. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `dlg,da9062-onkey`, `dlg,da9063-onkey`, `dlg,da9061-onkey`.
- Required top-level fields: `compatible`.
- Maintainers: Biju Das <biju.das.jz@bp.renesas.com>.
- Top-level properties: `compatible`, `dlg,disable-key-power`.
- `compatible`.
- `dlg,disable-key-power`: type `boolean`; Disable power-down using a long key-press. If this entry exists the OnKey driver will remove support for the KEY_POWER key press when triggered using a long press of the OnKey..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 38-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth3000.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth3000.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth3000.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Elantech I2C Touchpad**. The file describes the devicetree contract for the Elantech I2C Touchpad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `elan,ekth3000`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wakeup-source`, `vcc-supply`, `elan,trackpoint`, `elan,clickpad`, `elan,middle-button`, `elan,x_traces`, `elan,y_traces`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-x-mm`, `touchscreen-y-mm`.
- `compatible`: const `elan,ekth3000`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `vcc-supply`: a phandle for the regulator supplying 3.3V power.
- `wakeup-source`: type `boolean`; touchpad can be used as a wakeup source.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `elan,trackpoint`: type `boolean`; touchpad can support a trackpoint.
- `elan,clickpad`: type `boolean`; touchpad is a clickpad (the entire surface is a button).
- `elan,middle-button`: type `boolean`; touchpad has a physical middle button.
- `elan,x_traces`: ref `/schemas/types.yaml#/definitions/uint32`; number of antennas on the x axis.
- `elan,y_traces`: ref `/schemas/types.yaml#/definitions/uint32`; number of antennas on the y axis.
- `touchscreen-x-mm`.
- `touchscreen-y-mm`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen/touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vcc-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/elan,ekth3000.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 81-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth3000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth6915.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth6915.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth6915.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Elan I2C-HID touchscreen controllers**. Supports the Elan eKTH6915 and other I2C-HID touchscreen controllers. These touchscreen controller use the i2c-hid protocol with a reset GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `elan,ekth5015m`, `elan,ekth6915`, `elan,ekth8d18`, `elan,ekth6a12nay`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vcc33-supply`.
- Maintainers: Douglas Anderson <dianders@chromium.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `no-reset-on-power-off`, `vcc33-supply`, `vccio-supply`.
- `compatible`.
- `reg`.
- `interrupts`: maxItems 1.
- `reset-gpios`: Reset GPIO; not all touchscreens using eKTH6915 hook this up..
- `panel`.
- `no-reset-on-power-off`: type `boolean`; Reset line is wired so that it can (and should) be left deasserted when the power supply is off..
- `vcc33-supply`: The 3.3V supply to the touchscreen..
- `vccio-supply`: The IO supply to the touchscreen. Need not be specified if this is the same as the 3.3V supply..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `no-reset-on-power-off`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/elan,ekth6915.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 84-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/elan,ekth6915.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **FocalTech FT8112 touchscreen controller**. Supports the FocalTech FT8112 touchscreen controller. This touchscreen controller uses the i2c-hid protocol with a reset GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `focaltech,ft8112`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vcc33-supply`.
- Maintainers: Daniel Peng <Daniel_Peng@pegatron.corp-partner.google.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- `compatible`: enum `focaltech,ft8112`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `panel`.
- `vcc33-supply`.
- `vccio-supply`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/focaltech,ft8112.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 66-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,mpr121-touchkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,mpr121-touchkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,mpr121-touchkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Freescale MPR121 capacitive touch sensor controller**. The MPR121 supports up to 12 completely independent electrodes/capacitance sensing inputs in which 8 are multifunctional for LED driving and GPIO. https://www.nxp.com/docs/en/data-sheet/MPR121.pdf It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `fsl,mpr121-touchkey`.
- Required top-level fields: `compatible`, `reg`, `vdd-supply`, `linux,keycodes`.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `vdd-supply`, `linux,keycodes`, `wakeup-source`.
- `compatible`: const `fsl,mpr121-touchkey`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 12; minItems 1.
- `vdd-supply`.
- `wakeup-source`: type `boolean`; Use any event on keypad as wakeup event..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vdd-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/fsl,mpr121-touchkey.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 90-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,mpr121-touchkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,scu-key.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,scu-key.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,scu-key.yaml` is a Linux devicetree YAML schema for a key/button input binding: **i.MX SCU Client Device Node - SCU Key Based on SCU Message Protocol**. i.MX SCU Client Device Node Client nodes are maintained as children of the relevant IMX-SCU device node. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `fsl,imx8qxp-sc-key`, `fsl,imx-sc-key`.
- Required top-level fields: `compatible`, `linux,keycodes`.
- Maintainers: Dong Aisheng <aisheng.dong@nxp.com>.
- Top-level properties: `compatible`, `linux,keycodes`, `wakeup-source`.
- `compatible`.
- `linux,keycodes`: maxItems 1.
- `wakeup-source`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/fsl,scu-key.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 42-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/fsl,scu-key.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7375p.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7375p.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7375p.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Goodix GT7375P touchscreen**. Supports the Goodix GT7375P touchscreen. This touchscreen uses the i2c-hid protocol but has some non-standard power sequencing required. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `goodix,gt7375p`, `goodix,gt7986u`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `reset-gpios`, `vdd-supply`.
- Maintainers: Douglas Anderson <dianders@chromium.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `vdd-supply`, `mainboard-vddio-supply`, `goodix,no-reset-during-suspend`.
- `compatible`.
- `reg`: enum `93`, `20`.
- `interrupts`: maxItems 1.
- `reset-gpios`.
- `vdd-supply`: The 3.3V supply to the touchscreen..
- `panel`.
- `mainboard-vddio-supply`: The supply on the main board needed to power up IO signals going to the touchscreen. This supply need not go to the touchscreen itself as long as it allows the main board to make signals compatible with what the touchscreen is expecting for its IO rails..
- `goodix,no-reset-during-suspend`: type `boolean`; Set this to true to enforce the driver to not assert the reset GPIO during suspend. Due to potential touchscreen hardware flaw, back-powering could happen in suspend if the power supply is on and with active-low reset GPIO asserted. This property is used....
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `vdd-supply`, `mainboard-vddio-supply`, `goodix,no-reset-during-suspend`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/goodix,gt7375p.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 89-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7375p.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7986u-spifw.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7986u-spifw.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7986u-spifw.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Goodix GT7986U SPI HID Touchscreen**. Supports the Goodix GT7986U touchscreen. This touch controller reports data packaged according to the HID protocol over the SPI bus, but it is incompatible with Microsoft's HID-over-SPI protocol. NOTE: these bindings are distinct from the bindings used... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `goodix,gt7986u-spifw`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `reset-gpios`.
- Maintainers: Charles Wang <charles.goodix@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `reset-gpios`, `spi-max-frequency`.
- `compatible`: enum `goodix,gt7986u-spifw`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `spi-max-frequency`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/spi/spi-peripheral-props.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/goodix,gt7986u-spifw.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 69-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/goodix,gt7986u-spifw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml` is a Linux devicetree YAML schema for a keypad binding: **ChromeOS EC Keyboard**. Google's ChromeOS EC Keyboard is a simple matrix keyboard implemented on a separate EC (Embedded Controller) device. It provides a message for reading key scans from the EC. These are then converted into keycodes for processing by the kernel. This device... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `google,cros-ec-keyb-switches`, `google,cros-ec-keyb`.
- Required top-level fields: `compatible`.
- Maintainers: Simon Glass <sjg@chromium.org>, Benson Leung <bleung@chromium.org>.
- Top-level properties: `compatible`, `google,needs-ghost-filter`, `function-row-physmap`.
- `compatible`.
- `google,needs-ghost-filter`: type `boolean`; Enable a ghost filter for the matrix keyboard. This is recommended if the EC does not have its own logic or hardware for this..
- `function-row-physmap`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 15; minItems 1; An ordered u32 array describing the rows/columns (in the scan matrix) of top row keys from physical left (KEY_F1) to right. Each entry encodes the row/column as: (((row) & 0xFF) << 24) | (((column) & 0xFF) << 16) where the lower 16 bits are reserved. This....
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `google,cros-ec-keyb`: require `keypad,num-rows`, `keypad,num-columns`, `linux,keymap` / constrain none
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 140-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,goldfish-events-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,goldfish-events-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,goldfish-events-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Android Goldfish Events Keypad**. Android goldfish events keypad device generated by android emulator. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `google,goldfish-events-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Kuan-Wei Chiu <visitorckw@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`.
- `compatible`: const `google,goldfish-events-keypad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/google,goldfish-events-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 41-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,goldfish-events-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-beeper.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-beeper.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-beeper.yaml` is a Linux devicetree YAML schema for a beeper binding: **GPIO controlled beeper**. The file describes the devicetree contract for the GPIO controlled beeper. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `gpios`.
- Maintainers: Fabio Estevam <festevam@denx.de>.
- Top-level properties: `compatible`, `gpios`.
- `compatible`: const `gpio-beeper`.
- `gpios`: maxItems 1; GPIO that drives the beeper..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `gpios`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-beeper.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 33-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-beeper.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-charlieplex-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-charlieplex-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-charlieplex-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **GPIO charlieplex keypad**. The charlieplex keypad supports N^2)-N different key combinations (where N is the number of I/O lines). Key presses and releases are detected by configuring only one line as output at a time, and reading other line states. This process is repeated for each... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `line-gpios`, `linux,keymap`, `poll-interval`.
- Maintainers: Hugo Villeneuve <hvilleneuve@dimonoff.com>.
- Top-level properties: `compatible`, `autorepeat`, `debounce-delay-ms`, `line-gpios`, `linux,keymap`, `poll-interval`, `settling-time-us`, `wakeup-source`.
- `compatible`: const `gpio-charlieplex-keypad`.
- `linux,keymap`.
- `wakeup-source`.
- `poll-interval`.
- `autorepeat`.
- `debounce-delay-ms`.
- `line-gpios`: List of GPIOs used as lines. The gpio specifier for this property depends on the gpio controller to which these lines are connected..
- `settling-time-us`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `line-gpios`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-charlieplex-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 108-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-charlieplex-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **GPIO attached keys**. The file describes the devicetree contract for the GPIO attached keys. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: none.
- Maintainers: Rob Herring <robh@kernel.org>.
- Top-level properties: `compatible`, `autorepeat`, `label`, `poll-interval`.
- `compatible`: enum `gpio-keys`, `gpio-keys-polled`.
- `poll-interval`.
- `autorepeat`.
- `label`: Name of entire device.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^(button|event|key|switch|(button|event|key|switch)-[a-z0-9-]+|[a-z0-9-]+-(button|event|key|switch))$` child nodes with required `linux,code` and properties `gpios`, `interrupts`, `interrupt-names`, `label`, `linux,code`, `linux,input-type`, `linux,input-value`, `debounce-interval`, `wakeup-source`, `wakeup-event-action`, `linux,can-disable`
- Conditional validation: if `interrupts`: require `interrupt-names` / constrain `interrupt-names`; if `gpio-keys-polled`: require `poll-interval` / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 181-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **GPIO matrix keypad**. GPIO driven matrix keypad is used to interface a SoC with a matrix keypad. The matrix keypad supports multiple row and column lines, a key can be placed at each intersection of a unique row and a unique column. The matrix keypad can sense a key-press and... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `row-gpios`, `col-gpios`, `linux,keymap`.
- Maintainers: Marek Vasut <marek.vasut@gmail.com>.
- Top-level properties: `compatible`, `row-gpios`, `col-gpios`, `linux,keymap`, `linux,no-autorepeat`, `gpio-activelow`, `debounce-delay-ms`, `col-scan-delay-us`, `all-cols-on-delay-us`, `drive-inactive-cols`, `wakeup-source`.
- `compatible`: const `gpio-matrix-keypad`.
- `linux,keymap`.
- `wakeup-source`.
- `row-gpios`: List of GPIOs used as row lines. The gpio specifier for this property depends on the gpio controller to which these row lines are connected..
- `col-gpios`: List of GPIOs used as column lines. The gpio specifier for this property depends on the gpio controller to which these column lines are connected..
- `linux,no-autorepeat`: type `boolean`; Do not enable autorepeat feature..
- `gpio-activelow`: type `boolean`; Force GPIO polarity to active low. In the absence of this property GPIOs are treated as active high..
- `debounce-delay-ms`.
- `col-scan-delay-us`: Delay, measured in microseconds, that is needed before we can scan keypad after activating column gpio..
- `all-cols-on-delay-us`: Delay, measured in microseconds, that is needed after activating all column gpios..
- `drive-inactive-cols`: type `boolean`; Drive inactive columns during scan, default is to turn inactive columns into inputs..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `row-gpios`, `col-gpios`, `gpio-activelow`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 102-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-mouse.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-mouse.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-mouse.yaml` is a Linux devicetree YAML schema for a mouse binding: **GPIO attached mouse**. This simply uses standard GPIO handles to define a simple mouse connected to 5-7 GPIO lines. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `scan-interval-ms`, `up-gpios`, `down-gpios`, `left-gpios`, `right-gpios`.
- Maintainers: Anshul Dalal <anshulusr@gmail.com>.
- Top-level properties: `compatible`, `scan-interval-ms`, `up-gpios`, `down-gpios`, `left-gpios`, `right-gpios`, `button-left-gpios`, `button-middle-gpios`, `button-right-gpios`.
- `compatible`: const `gpio-mouse`.
- `scan-interval-ms`: maxItems 1.
- `up-gpios`: maxItems 1.
- `down-gpios`: maxItems 1.
- `left-gpios`: maxItems 1.
- `right-gpios`: maxItems 1.
- `button-left-gpios`: maxItems 1.
- `button-middle-gpios`: maxItems 1.
- `button-right-gpios`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `up-gpios`, `down-gpios`, `left-gpios`, `right-gpios`, `button-left-gpios`, `button-middle-gpios`, `button-right-gpios`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-mouse.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 68-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-mouse.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-vibrator.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-vibrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-vibrator.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **GPIO vibrator**. Registers a GPIO device as vibrator, where the on/off capability is controlled by a GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `enable-gpios`.
- Maintainers: Luca Weiss <luca@z3ntu.xyz>.
- Top-level properties: `compatible`, `enable-gpios`, `vcc-supply`.
- `compatible`: const `gpio-vibrator`.
- `vcc-supply`: Regulator that provides power.
- `enable-gpios`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `enable-gpios`, `vcc-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-vibrator.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 39-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-vibrator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/hid-over-i2c.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/hid-over-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/hid-over-i2c.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **HID over I2C Devices**. HID over I2C provides support for various Human Interface Devices over the I2C bus. These devices can be for example touchpads, keyboards, touch screens or sensors. The specification has been written by Microsoft and is currently available here:... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `wacom,w9013`, `hid-over-i2c`, `Just "hid-over-i2c" alone is allowed, but not recommended.`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Benjamin Tissoires <benjamin.tissoires@redhat.com>, Jiri Kosina <jkosina@suse.cz>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `hid-descr-addr`, `panel`, `post-power-on-delay-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `vdd-supply`, `vddl-supply`, `wakeup-source`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `vdd-supply`: 3.3V supply.
- `wakeup-source`.
- `hid-descr-addr`: ref `/schemas/types.yaml#/definitions/uint32`; HID descriptor address.
- `panel`.
- `post-power-on-delay-ms`: Time required by the device after enabling its regulators or powering it on, before it is ready for communication..
- `touchscreen-inverted-x`.
- `touchscreen-inverted-y`.
- `vddl-supply`: 1.8V supply.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `vdd-supply`, `vddl-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/hid-over-i2c.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 85-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/hid-over-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ibm,op-panel.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ibm,op-panel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ibm,op-panel.yaml` is a Linux devicetree YAML schema for a key/button input binding: **IBM Operation Panel**. The IBM Operation Panel provides a simple interface to control the connected server. It has a display and three buttons: two directional arrows and one 'Enter' button. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ibm,op-panel`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Eddie James <eajames@linux.ibm.com>.
- Top-level properties: `compatible`, `reg`, `linux,keycodes`.
- `compatible`: const `ibm,op-panel`.
- `reg`: maxItems 1.
- `linux,keycodes`: maxItems 3; minItems 1.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ibm,op-panel.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 50-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ibm,op-panel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili2901.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili2901.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili2901.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Ilitek ILI2901 touchscreen controller**. Supports the Ilitek ILI2901 touchscreen controller. This touchscreen controller uses the i2c-hid protocol with a reset GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ilitek,ili2901`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vcc33-supply`.
- Maintainers: Jiri Kosina <jkosina@suse.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- `compatible`: enum `ilitek,ili2901`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `panel`.
- `vcc33-supply`.
- `vccio-supply`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ilitek,ili2901.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 66-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili2901.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili9882t.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili9882t.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili9882t.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Ilitek ili9882t touchscreen controller**. Supports the Ilitek ili9882t touchscreen controller. This touchscreen controller uses the i2c-hid protocol with a reset GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ilitek,ili9882t`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `panel`, `vccio-supply`.
- Maintainers: Cong Yang <yangcong5@huaqin.corp-partner.google.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `vccio-supply`.
- `compatible`: const `ilitek,ili9882t`.
- `reg`: const `65`.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; Reset GPIO..
- `panel`.
- `vccio-supply`: The 1.8V supply to the touchscreen..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ilitek,ili9882t.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 67-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ilitek,ili9882t.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Freescale i.MX Keypad Port(KPP)**. The KPP is designed to interface with a keypad matrix with 2-point contact or 3-point contact keys. The KPP is designed to simplify the software task of scanning a keypad matrix. The KPP is capable of detecting, debouncing, and decoding one or multiple... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `fsl,imx21-kpp`, `fsl,imx25-kpp`, `fsl,imx27-kpp`, `fsl,imx31-kpp`, `fsl,imx35-kpp`, `fsl,imx51-kpp`, `fsl,imx53-kpp`, `fsl,imx50-kpp`, `fsl,imx6q-kpp`, `fsl,imx6sx-kpp`, `fsl,imx6sl-kpp`, `fsl,imx6sll-kpp`, `fsl,imx6ul-kpp`, `fsl,imx7d-kpp`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `linux,keymap`.
- Maintainers: Liu Ying <gnuiyl@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/imx-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 85-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/input.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/input.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/input.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Input Devices Common Properties**. This is the common base schema used by Linux input bindings for shared properties such as autorepeat, event codes, wakeup behavior, and input identification metadata. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: none.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `autorepeat`, `debounce-delay-ms`, `linux,keycodes`, `linux,code`, `linux,input-type`, `poll-interval`, `power-off-time-sec`, `reset-time-sec`, `settling-time-us`.
- `linux,keycodes`: ref `/schemas/types.yaml#/definitions/uint32-array`; Specifies an array of numeric keycode values to be used for reporting button presses..
- `linux,code`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies a single numeric keycode value to be used for reporting button/switch events. Specify KEY_RESERVED (0) to opt out of event reporting..
- `poll-interval`: ref `/schemas/types.yaml#/definitions/uint32`; Poll interval time in milliseconds..
- `autorepeat`: type `boolean`; Enable autorepeat when key is pressed and held down..
- `debounce-delay-ms`: Debounce delay in milliseconds. This is the time during which the key press or release signal must remain stable before it is considered valid..
- `linux,input-type`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `3`, `5`; Specifies whether the event is to be interpreted as a key, relative, absolute, or switch..
- `power-off-time-sec`: Duration in seconds which the key should be kept pressed for device to power off automatically. Device with key pressed shutdown feature can specify this property..
- `reset-time-sec`: Duration in seconds which the key should be kept pressed for device to reset automatically. Device with key pressed reset feature can specify this property..
- `settling-time-us`: Delay, in microseconds, when activating an output line/col/row before we can reliably read other input lines that maybe affected by this output. This can be the case for an output with a RC circuit that affects ramp-up/down times..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: True` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reset-time-sec`.

## Risks and Test Signals
- Primary risks: updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/input.yaml`; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 80-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/input.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Azoteq IQS269A Capacitive Touch Controller**. The Azoteq IQS269A is an 8-channel capacitive touch controller that features additional Hall-effect and inductive sensing capabilities. Link to datasheet: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs269a`, `azoteq,iqs269a-00`, `azoteq,iqs269a-d0`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `azoteq,hall-enable`, `azoteq,suspend-mode`, `azoteq,clk-div`, `azoteq,ulp-update`, `azoteq,reseed-offset`, `azoteq,filt-str-lp-lta`, `azoteq,filt-str-lp-cnt`, `azoteq,filt-str-np-lta`, `azoteq,filt-str-np-cnt`, `azoteq,rate-np-ms`, `azoteq,rate-lp-ms`, `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,ati-band-tighten`, `azoteq,filt-disable`, `azoteq,gpio3-select`, `azoteq,dual-direction`, `azoteq,tx-freq`, `azoteq,global-cap-increase`, `azoteq,reseed-select`, and 8 more.
- `compatible`: enum `azoteq,iqs269a`, `azoteq,iqs269a-00`, `azoteq,iqs269a-d0`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 8; minItems 1; Specifies the numeric keycodes associated with each available gesture in the following order (enter 0 for unused gestures): 0: Slider 0 tap 1: Slider 0 hold 2: Slider 0 positive flick or swipe 3: Slider 0 negative flick or swipe 4: Slider 1 tap 5: Slider 1....
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `azoteq,hall-enable`: type `boolean`; Enables Hall-effect sensing on channels 6 and 7. In this case, keycodes assigned to channel 6 are ignored and keycodes assigned to channel 7 are interpreted as switch codes. Refer to the datasheet for requirements im- posed on channels 6 and 7 by....
- `azoteq,suspend-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the power mode during suspend as follows: 0: Automatic (same as normal runtime, i.e. suspend/resume disabled) 1: Low power (all sensing at a reduced reporting rate) 2: Ultra-low power (channel 0 proximity sensing) 3: Halt (no sensing).
- `azoteq,clk-div`: type `boolean`; Divides the device's core clock by a factor of 4..
- `azoteq,ulp-update`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the ultra-low-power mode update rate..
- `azoteq,reseed-offset`: type `boolean`; Applies an 8-count offset to all long-term averages upon either ATI or reseed events..
- `azoteq,filt-str-lp-lta`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the long-term average filter strength during low-power mode..
- `azoteq,filt-str-lp-cnt`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the raw count filter strength during low-power mode..
- `azoteq,filt-str-np-lta`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the long-term average filter strength during normal-power mode..
- `azoteq,filt-str-np-cnt`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the raw count filter strength during normal-power mode..
- `azoteq,rate-np-ms`: Specifies the report rate (in ms) during normal-power mode..
- `azoteq,rate-lp-ms`: Specifies the report rate (in ms) during low-power mode..
- `azoteq,rate-ulp-ms`: Specifies the report rate (in ms) during ultra-low-power mode..
- additional schema properties: `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,ati-band-tighten`, `azoteq,filt-disable`, `azoteq,gpio3-select`, `azoteq,dual-direction`, `azoteq,tx-freq`, `azoteq,global-cap-increase`, `azoteq,reseed-select`, `azoteq,tracking-enable`, `azoteq,filt-str-slider`, `azoteq,touch-hold-ms`, `azoteq,gesture-swipe`, `azoteq,timeout-tap-ms`, `azoteq,timeout-swipe-ms`, `azoteq,thresh-swipe`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^channel@[0-7]$` child nodes with required `reg` and properties `reg`, `azoteq,reseed-disable`, `azoteq,blocking-enable`, `azoteq,slider0-select`, `azoteq,slider1-select`, `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,meas-cap-decrease`, `azoteq,rx-float-inactive`, `azoteq,local-cap-size`, `azoteq,invert-enable`, `azoteq,proj-bias`, and 8 more
- Conditional validation: if `azoteq,iqs269a-d0`: require none / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `azoteq,gpio3-select`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs269a.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 648-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS626A Capacitive Touch Controller**. The Azoteq IQS626A is a 14-channel capacitive touch controller that features additional Hall-effect and inductive sensing capabilities. Link to datasheet: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs626a`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `azoteq,suspend-mode`, `azoteq,clk-div`, `azoteq,ulp-enable`, `azoteq,ulp-update`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,gpio3-select`, `azoteq,reseed-select`, `azoteq,thresh-extend`, `azoteq,tracking-enable`, `azoteq,reseed-offset`, `azoteq,rate-np-ms`, `azoteq,rate-lp-ms`, `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- `compatible`: const `azoteq,iqs626a`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `azoteq,suspend-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the power mode during suspend as follows: 0: Automatic (same as normal runtime, i.e. suspend/resume disabled) 1: Low power (all sensing at a reduced reporting rate) 2: Ultra-low power (ULP channel proximity sensing) 3: Halt (no sensing).
- `azoteq,clk-div`: type `boolean`; Divides the device's core clock by a factor of 4..
- `azoteq,ulp-enable`: type `boolean`; Permits the device to automatically enter ultra-low-power mode from low- power mode..
- `azoteq,ulp-update`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`, `4`, and 3 more; Specifies the rate at which the trackpad, generic and Hall channels are updated during ultra-low-power mode as follows: 0: 8 1: 13 2: 28 3: 54 4: 89 5: 135 6: 190 7: 256.
- `azoteq,ati-band-disable`: type `boolean`; Disables the ATI band check..
- `azoteq,ati-lp-only`: type `boolean`; Limits automatic ATI to low-power mode..
- `azoteq,gpio3-select`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`, `4`, and 3 more; Selects the channel or group of channels for which the GPIO3 pin represents touch state as follows: 0: None 1: ULP channel 2: Trackpad 3: Trackpad 4: Generic channel 0 5: Generic channel 1 6: Generic channel 2 7: Hall channel.
- `azoteq,reseed-select`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the event(s) that prompt the device to reseed (i.e. reset the long-term average) of an associated channel as follows: 0: None 1: Proximity 2: Proximity or touch 3: Proximity, touch or deep touch.
- `azoteq,thresh-extend`: type `boolean`; Multiplies all touch and deep-touch thresholds by 4..
- `azoteq,tracking-enable`: type `boolean`; Enables all associated channels to track their respective reference channels..
- `azoteq,reseed-offset`: type `boolean`; Applies an 8-count offset to all long-term averages upon either ATI or reseed events..
- `azoteq,rate-np-ms`: Specifies the report rate (in ms) during normal-power mode..
- `azoteq,rate-lp-ms`: Specifies the report rate (in ms) during low-power mode..
- additional schema properties: `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen/touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/string-array`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^ulp-0|generic-[0-2]|hall$` child nodes with required none and properties `azoteq,ati-exclude`, `azoteq,reseed-disable`, `azoteq,meas-cap-decrease`, `azoteq,rx-inactive`, `azoteq,linearize`, `azoteq,dual-direction`, `azoteq,filt-disable`, `azoteq,ati-mode`, `azoteq,ati-base`, `azoteq,ati-target`, `azoteq,cct-increase`, `azoteq,proj-bias`, and 17 more; `^trackpad-3x[2-3]$` child nodes with required none and properties `azoteq,ati-exclude`, `azoteq,reseed-disable`, `azoteq,meas-cap-decrease`, `azoteq,rx-inactive`, `azoteq,linearize`, `azoteq,dual-direction`, `azoteq,filt-disable`, `azoteq,ati-mode`, `azoteq,ati-target`, `azoteq,cct-increase`, `azoteq,proj-bias`, `azoteq,sense-freq`, and 11 more
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `azoteq,gpio3-select`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs626a.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 878-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Azoteq IQS620A/621/622/624/625 Keys and Switches**. The Azoteq IQS620A, IQS621, IQS622, IQS624 and IQS625 multi-function sensors feature a variety of self-capacitive, mutual-inductive and Hall-effect sens- ing capabilities that can facilitate a variety of contactless key and switch applications. These... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs620a-keys`, `azoteq,iqs621-keys`, `azoteq,iqs622-keys`, `azoteq,iqs624-keys`, `azoteq,iqs625-keys`.
- Required top-level fields: `compatible`, `linux,keycodes`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `linux,keycodes`.
- `compatible`: enum `azoteq,iqs620a-keys`, `azoteq,iqs621-keys`, `azoteq,iqs622-keys`, `azoteq,iqs624-keys`, `azoteq,iqs625-keys`.
- `linux,keycodes`: maxItems 16; minItems 1; Specifies the numeric keycodes associated with each available touch or proximity event according to the following table. An 'x' indicates the event is supported for a given device. Specify 0 for unused events.....
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^hall-switch-(north|south)$` child nodes with required `linux,code` and properties `linux,code`, `azoteq,use-prox`
- Conditional validation: if `azoteq,iqs624-keys`, `azoteq,iqs625-keys`: require none / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs62x-keys.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 132-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml` is a Linux devicetree YAML schema for a keypad binding: **Common Key Matrices on Matrix-connected Keyboards**. This common schema defines matrix keypad keymap encoding and row/column dimension properties that concrete keypad controller bindings reference. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: none.
- Maintainers: Olof Johansson <olof@lixom.net>.
- Top-level properties: `linux,keymap`, `keypad,num-rows`, `keypad,num-columns`.
- `linux,keymap`: ref `/schemas/types.yaml#/definitions/uint32-array`; An array of packed 1-cell entries containing the equivalent of row, column and linux key-code. The 32-bit big endian cell is packed as: row << 24 | column << 16 | key-code.
- `keypad,num-rows`: ref `/schemas/types.yaml#/definitions/uint32`; Number of row lines connected to the keypad controller..
- `keypad,num-columns`: ref `/schemas/types.yaml#/definitions/uint32`; Number of column lines connected to the keypad controller..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: True` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.

## Risks and Test Signals
- Primary risks: updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/matrix-keymap.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 48-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Onkey driver for MAX77650 PMIC from Maxim Integrated.**. This module is part of the MAX77650 MFD device. For more details see Documentation/devicetree/bindings/mfd/max77650.yaml. The onkey controller is represented as a sub-node of the PMIC node on the device tree. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `maxim,max77650-onkey`.
- Required top-level fields: `compatible`.
- Maintainers: Bartosz Golaszewski <bgolaszewski@baylibre.com>.
- Top-level properties: `compatible`, `linux,code`, `maxim,onkey-slide`.
- `compatible`: const `maxim,max77650-onkey`.
- `linux,code`.
- `maxim,onkey-slide`: ref `/schemas/types.yaml#/definitions/flag`; The system's button is a slide switch, not the default push button..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/max77650-onkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 38-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,mt6779-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,mt6779-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,mt6779-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Mediatek's Keypad Controller**. Mediatek's Keypad controller is used to interface a SoC with a matrix-type keypad device. The keypad controller supports multiple row and column lines. A key can be placed at each intersection of a unique row and a unique column. The keypad controller can... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `mediatek,mt6779-keypad`, `mediatek,mt6873-keypad`, `mediatek,mt8183-keypad`, `mediatek,mt8365-keypad`, `mediatek,mt8516-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Maintainers: Mattijs Korpershoek <mkorpershoek@kernel.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `wakeup-source`, `debounce-delay-ms`, `mediatek,keys-per-group`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wakeup-source`: type `boolean`; use any event on keypad as wakeup event.
- `clocks`: maxItems 1.
- `clock-names`.
- `debounce-delay-ms`.
- `mediatek,keys-per-group`: ref `/schemas/types.yaml#/definitions/uint32`; each (row, column) group has multiple keys.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/input/matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`, `clock-names`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/mediatek,mt6779-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 87-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,mt6779-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **MediaTek PMIC Keys**. There are two key functions provided by MT6397, MT6323 and other MediaTek PMICs: pwrkey and homekey. The key functions are defined as the subnode of the function node provided by the PMIC that is defined as a Multi-Function Device (MFD). For MediaTek... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `mediatek,mt6323-keys`, `mediatek,mt6328-keys`, `mediatek,mt6331-keys`, `mediatek,mt6357-keys`, `mediatek,mt6358-keys`, `mediatek,mt6359-keys`, `mediatek,mt6397-keys`.
- Required top-level fields: `compatible`.
- Maintainers: Chen Zhong <chen.zhong@mediatek.com>.
- Top-level properties: `compatible`, `power-off-time-sec`, `mediatek,long-press-mode`.
- `compatible`: enum `mediatek,mt6323-keys`, `mediatek,mt6328-keys`, `mediatek,mt6331-keys`, `mediatek,mt6357-keys`, `mediatek,mt6358-keys`, and 2 more.
- `power-off-time-sec`.
- `mediatek,long-press-mode`: ref `/schemas/types.yaml#/definitions/uint32`; Key long-press force shutdown setting 0 - disabled 1 - pwrkey 2 - pwrkey+homekey.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^((power|home)|(key-[a-z0-9-]+|[a-z0-9-]+-key))$` child nodes with required `linux,keycodes` and properties `interrupts`, `interrupt-names`, `linux,keycodes`, `wakeup-source`
- Conditional validation: if `powerkey`: require none / constrain `interrupt-names`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 95-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/microchip,cap11xx.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/microchip,cap11xx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/microchip,cap11xx.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Microchip CAP11xx based capacitive touch sensors**. The Microchip CAP1xxx Family of RightTouchTM multiple-channel capacitive touch controllers and LED drivers. The device communication via I2C only. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `microchip,cap1106`, `microchip,cap1126`, `microchip,cap1188`, `microchip,cap1203`, `microchip,cap1206`, `microchip,cap1293`, `microchip,cap1298`.
- Required top-level fields: `compatible`, `interrupts`.
- Maintainers: Rob Herring <robh@kernel.org>.
- Top-level properties: `compatible`, `reg`, `#address-cells`, `#size-cells`, `interrupts`, `autorepeat`, `linux,keycodes`, `microchip,sensor-gain`, `microchip,irq-active-high`, `microchip,sensitivity-delta-sense`, `microchip,signal-guard`, `microchip,input-threshold`, `microchip,calib-sensitivity`.
- `compatible`: enum `microchip,cap1106`, `microchip,cap1126`, `microchip,cap1188`, `microchip,cap1203`, `microchip,cap1206`, and 2 more.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1; Property describing the interrupt line the device's ALERT#/CM_IRQ# pin is connected to. The device only has one interrupt source..
- `linux,keycodes`: maxItems 8; minItems 3; Specifies an array of numeric keycode values to be used for the channels. If this property is omitted, KEY_A, KEY_B, etc are used as defaults. The number of entries must correspond to the number of channels..
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `autorepeat`: Enables the Linux input system's autorepeat feature on the input device..
- `microchip,sensor-gain`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `4`, `8`; Defines the gain of the sensor circuitry. This effectively controls the sensitivity, as a smaller delta capacitance is required to generate the same delta count values..
- `microchip,irq-active-high`: type `boolean`; By default the interrupt pin is active low open drain. This property allows using the active high push-pull output..
- `microchip,sensitivity-delta-sense`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `4`, `8`, `16`, and 3 more; Controls the sensitivity multiplier of a touch detection. Higher value means more sensitive settings. At the more sensitive settings, touches are detected for a smaller delta capacitance corresponding to a "lighter" touch..
- `microchip,signal-guard`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 8; minItems 3; 0 - off 1 - on The signal guard isolates the signal from virtual grounds. If enabled then the behavior of the channel is changed to signal guard. The number of entries must correspond to the number of channels..
- `microchip,input-threshold`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 8; minItems 3; Specifies the delta threshold that is used to determine if a touch has been detected. A higher value means a larger difference in capacitance is required for a touch to be registered, making the touch sensor less sensitive. The number of entries must....
- `microchip,calib-sensitivity`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 8; minItems 3; Specifies an array of numeric values that controls the gain used by the calibration routine to enable sensor inputs to be more sensitive for proximity detection. Gain is based on touch pad capacitance range 1 - 5-50pF 2 - 0-25pF 4 - 0-12.5pF The number of....
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/leds/common.yaml#`, `input.yaml`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^led@[0-7]$` child nodes with required `reg` and properties `reg`, `label`, `linux,default-trigger`, `default-state`
- Conditional validation: if `microchip,cap1106`, `microchip,cap1203`, `microchip,cap1206`, `microchip,cap1293`, `microchip,cap1298`: require none / constrain none; if `microchip,cap1106`, `microchip,cap1126`, `microchip,cap1188`, `microchip,cap1203`, `microchip,cap1206`: require none / constrain `microchip,signal-guard`, `microchip,calib-sensitivity`
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/microchip,cap11xx.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 226-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/microchip,cap11xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/nxp,lpc3220-key.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/nxp,lpc3220-key.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/nxp,lpc3220-key.yaml` is a Linux devicetree YAML schema for a keypad binding: **NXP LPC32xx Key Scan Interface**. The file describes the devicetree contract for the NXP LPC32xx Key Scan Interface. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `nxp,lpc3220-key`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `nxp,debounce-delay-ms`, `nxp,scan-delay-ms`, `linux,keymap`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `nxp,debounce-delay-ms`, `nxp,scan-delay-ms`.
- `compatible`: const `nxp,lpc3220-key`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `nxp,debounce-delay-ms`: Debounce delay in ms.
- `nxp,scan-delay-ms`: Repeated scan period in ms.
- Shared-schema dependencies are pulled with `$ref`: `matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/nxp,lpc3220-key.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 61-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/nxp,lpc3220-key.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/parade,tc3408.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/parade,tc3408.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/parade,tc3408.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Parade TC3408 touchscreen controller**. Parade TC3408 is a touchscreen controller supporting the I2C-HID protocol. It requires a reset GPIO and two power supplies (3.3V and 1.8V). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `parade,tc3408`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Maintainers: Langyan Ye <yelangyan@huaqin.corp-partner.google.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- `compatible`: const `parade,tc3408`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `vcc33-supply`: The 3.3V supply to the touchscreen..
- `vccio-supply`: The 1.8V supply to the touchscreen..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/parade,tc3408.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 68-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/parade,tc3408.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Pine64 PinePhone keyboard**. A keyboard accessory is available for the Pine64 PinePhone and PinePhone Pro. It connects via I2C, providing a raw scan matrix, a flashing interface, and a subordinate I2C bus for communication with a battery charger IC. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `pine64,pinephone-keyboard`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Samuel Holland <samuel@sholland.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `vbat-supply`, `wakeup-source`, `i2c`.
- `compatible`: const `pine64,pinephone-keyboard`.
- `reg`: const `21`.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `vbat-supply`: Supply for the keyboard MCU.
- `i2c`: ref `/schemas/i2c/i2c-controller.yaml#`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/i2c/i2c-controller.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `i2c` object node with required none and properties none
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vbat-supply`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 66-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-beeper.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-beeper.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-beeper.yaml` is a Linux devicetree YAML schema for a beeper binding: **PWM beeper**. The file describes the devicetree contract for the PWM beeper. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `pwms`.
- Maintainers: Sascha Hauer <s.hauer@pengutronix.de>.
- Top-level properties: `compatible`, `pwms`, `amp-supply`, `beeper-hz`.
- `compatible`: const `pwm-beeper`.
- `pwms`: maxItems 1.
- `amp-supply`: an amplifier for the beeper.
- `beeper-hz`: bell frequency in Hz.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `pwms`, `amp-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/pwm-beeper.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 41-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-beeper.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **PWM vibrator**. Registers a PWM device as vibrator. It is expected, that the vibrator's strength increases based on the duty cycle of the enable PWM channel (100% duty cycle meaning strongest vibration, 0% meaning no vibration). The binding supports an optional direction... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `pwm-names`, `pwms`.
- Maintainers: Sebastian Reichel <sre@kernel.org>.
- Top-level properties: `compatible`, `pwm-names`, `pwms`, `enable-gpios`, `vcc-supply`, `direction-duty-cycle-ns`.
- `compatible`: const `pwm-vibrator`.
- `pwms`: maxItems 2; minItems 1.
- `vcc-supply`.
- `pwm-names`: minItems 1.
- `enable-gpios`.
- `direction-duty-cycle-ns`: Duty cycle of the direction PWM channel in nanoseconds, defaults to 50% of the channel's period..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `pwm-names`, `pwms`, `enable-gpios`, `vcc-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/pwm-vibrator.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 59-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Qualcomm PM8921 PMIC KeyPad**. The file describes the devicetree contract for the Qualcomm PM8921 PMIC KeyPad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8058-keypad`, `qcom,pm8921-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `linux,keymap`.
- Maintainers: Dmitry Baryshkov <dmitry.baryshkov@linaro.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wakeup-source`, `linux,keypad-wakeup`, `debounce`, `scan-delay`, `row-hold`.
- `compatible`: enum `qcom,pm8058-keypad`, `qcom,pm8921-keypad`.
- `reg`: maxItems 1.
- `interrupts`.
- `wakeup-source`: type `boolean`; use any event on keypad as wakeup event.
- `linux,keypad-wakeup`: type `boolean`; legacy version of the wakeup-source property.
- `debounce`: ref `/schemas/types.yaml#/definitions/uint32`; Time in microseconds that key must be pressed or released for state change interrupt to trigger..
- `scan-delay`: ref `/schemas/types.yaml#/definitions/uint32`; time in microseconds to pause between successive scans of the matrix array.
- `row-hold`: ref `/schemas/types.yaml#/definitions/uint32`; time in nanoseconds to pause between scans of each row in the matrix array..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 89-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-pwrkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-pwrkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-pwrkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Qualcomm PM8921 PMIC Power Key**. The file describes the devicetree contract for the Qualcomm PM8921 PMIC Power Key. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8921-pwrkey`, `qcom,pm8058-pwrkey`, `qcom,pm8018-pwrkey`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Bjorn Andersson <andersson@kernel.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `debounce`, `pull-up`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`.
- `debounce`: ref `/schemas/types.yaml#/definitions/uint32`; Time in microseconds that key must be pressed or released for state change interrupt to trigger..
- `pull-up`: ref `/schemas/types.yaml#/definitions/flag`; Presence of this property indicates that the KPDPWR_N pin should be configured for pull up..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8921-pwrkey.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 75-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-pwrkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Qualcomm PM8941 PMIC Power Key**. The file describes the devicetree contract for the Qualcomm PM8941 PMIC Power Key. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8941-pwrkey`, `qcom,pm8941-resin`, `qcom,pmk8350-pwrkey`, `qcom,pmk8350-resin`, `qcom,pmm8654au-pwrkey`, `qcom,pmm8654au-resin`.
- Required top-level fields: `compatible`, `interrupts`.
- Maintainers: Courtney Cavin <courtney.cavin@sonymobile.com>, Vinod Koul <vkoul@kernel.org>.
- Top-level properties: `compatible`, `interrupts`, `debounce`, `bias-pull-up`, `wakeup-source`, `linux,code`.
- `compatible`.
- `interrupts`: maxItems 1.
- `linux,code`: The input key-code associated with the power key. Use the linux event codes defined in include/dt-bindings/input/linux-event-codes.h. When property is omitted KEY_POWER is assumed..
- `wakeup-source`: Button can wake-up the system. Only applicable for 'resin', 'pwrkey' always wakes the system by default..
- `debounce`: ref `/schemas/types.yaml#/definitions/uint32`; Time in microseconds that key must be pressed or released for state change interrupt to trigger..
- `bias-pull-up`: ref `/schemas/types.yaml#/definitions/flag`; Presence of this property indicates that the KPDPWR_N pin should be configured for pull up..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `qcom,pm8941-pwrkey`, `qcom,pmk8350-pwrkey`: require none / constrain `wakeup-source`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 72-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8xxx-vib.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8xxx-vib.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8xxx-vib.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Qualcomm PM8xxx PMIC Vibrator**. The file describes the devicetree contract for the Qualcomm PM8xxx PMIC Vibrator. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8058-vib`, `qcom,pm8916-vib`, `qcom,pm8921-vib`, `qcom,pmi632-vib`, `qcom,pm6150-vib`, `qcom,pm7250b-vib`, `qcom,pm7325b-vib`, `qcom,pm7550ba-vib`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Bjorn Andersson <andersson@kernel.org>.
- Top-level properties: `compatible`, `reg`.
- `compatible`.
- `reg`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8xxx-vib.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 47-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8xxx-vib.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Regulator Haptic**. The file describes the devicetree contract for the Regulator Haptic. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `haptic-supply`, `max-microvolt`, `min-microvolt`.
- Maintainers: Jaewon Kim <jaewon02.kim@samsung.com>.
- Top-level properties: `compatible`, `haptic-supply`, `max-microvolt`, `min-microvolt`.
- `compatible`: const `regulator-haptic`.
- `haptic-supply`: Power supply to the haptic motor.
- `max-microvolt`: The maximum voltage value supplied to the haptic motor.
- `min-microvolt`: The minimum voltage value supplied to the haptic motor.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `haptic-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/regulator-haptic.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 43-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml` is a Linux devicetree YAML schema for a input binding schema: **Rotary encoder**. See Documentation/input/devices/rotary-encoder.rst for more information. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `gpios`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `gpios`, `linux,axis`, `rotary-encoder,steps`, `rotary-encoder,relative-axis`, `rotary-encoder,rollover`, `rotary-encoder,steps-per-period`, `wakeup-source`, `rotary-encoder,encoding`, `rotary-encoder,half-period`.
- `compatible`: const `rotary-encoder`.
- `gpios`: minItems 2.
- `wakeup-source`.
- `linux,axis`: the input subsystem axis to map to this rotary encoder. Defaults to 0 (ABS_X / REL_X).
- `rotary-encoder,steps`: ref `/schemas/types.yaml#/definitions/uint32`; Number of steps in a full turnaround of the encoder. Only relevant for absolute axis. Defaults to 24 which is a typical value for such devices..
- `rotary-encoder,relative-axis`: ref `/schemas/types.yaml#/definitions/flag`; register a relative axis rather than an absolute one. Relative axis will only generate +1/-1 events on the input device, hence no steps need to be passed..
- `rotary-encoder,rollover`: ref `/schemas/types.yaml#/definitions/flag`; Automatic rollover when the rotary value becomes greater than the specified steps or smaller than 0. For absolute axis only..
- `rotary-encoder,steps-per-period`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `4`; Number of steps (stable states) per period. The values have the following meaning: 1: Full-period mode (default) 2: Half-period mode 4: Quarter-period mode.
- `rotary-encoder,encoding`: ref `/schemas/types.yaml#/definitions/string`; enum `gray`, `binary`; the method used to encode steps..
- `rotary-encoder,half-period`: ref `/schemas/types.yaml#/definitions/flag`; Makes the driver work on half-period mode. This property is deprecated. Instead, a 'steps-per-period ' value should be used, such as "rotary-encoder,steps-per-period = <2>"..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `gpios`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/rotary-encoder.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 90-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Samsung SoC series Keypad Controller**. Samsung SoC Keypad controller is used to interface a SoC with a matrix-type keypad device. The keypad controller supports multiple row and column lines. A key can be placed at each intersection of a unique row and a unique column. The keypad controller can... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `samsung,s3c6410-keypad`, `samsung,s5pv210-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `samsung,keypad-num-columns`, `samsung,keypad-num-rows`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Top-level properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `wakeup-source`, `linux,input-no-autorepeat`, `linux,input-wakeup`, `samsung,keypad-num-columns`, `samsung,keypad-num-rows`.
- `compatible`: enum `samsung,s3c6410-keypad`, `samsung,s5pv210-keypad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `clocks`: maxItems 1.
- `clock-names`.
- `linux,input-no-autorepeat`: type `boolean`; Do no enable autorepeat feature..
- `linux,input-wakeup`: type `boolean`.
- `samsung,keypad-num-columns`: ref `/schemas/types.yaml#/definitions/uint32`; Number of column lines connected to the keypad controller..
- `samsung,keypad-num-rows`: ref `/schemas/types.yaml#/definitions/uint32`; Number of row lines connected to the keypad controller..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^key-[0-9a-z]+$` child nodes with required `keypad,column`, `keypad,row`, `linux,code` and properties `keypad,column`, `keypad,row`, `linux,code`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clocks`, `clock-names`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 121-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Spreadtrum SC27xx PMIC Vibrator**. The file describes the devicetree contract for the Spreadtrum SC27xx PMIC Vibrator. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, `sprd,sc2731-vibrator`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>.
- Top-level properties: `compatible`, `reg`.
- `compatible`: enum `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, `sprd,sc2731-vibrator`.
- `reg`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 31-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Synaptics RMI4 compliant devices**. The Synaptics RMI4 (Register Mapped Interface 4) core is able to support RMI4 devices using different transports (I2C, SPI) and different functions (e.g. Function 1, 2D sensors using Function 11 or 12). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `syna,rmi4-i2c`, `syna,rmi4-spi`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Jason A. Donenfeld <Jason@zx2c4.com>, Matthias Schiffer <matthias.schiffer@ew.tq-group.com>, Vincent Huang <vincent.huang@tw.synaptics.com>.
- Top-level properties: `compatible`, `reg`, `#address-cells`, `#size-cells`, `interrupts`, `reset-gpios`, `spi-cpha`, `spi-cpol`, `syna,reset-delay-ms`, `syna,startup-delay-ms`, `vdd-supply`, `vio-supply`, `rmi4-f01@1`, `rmi4-f1a@1a`.
- `compatible`: enum `syna,rmi4-i2c`, `syna,rmi4-spi`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; Active low signal.
- `vdd-supply`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `spi-cpha`.
- `spi-cpol`.
- `syna,reset-delay-ms`: Delay to wait after resetting the device..
- `syna,startup-delay-ms`: Delay to wait after powering on the device..
- `vio-supply`.
- `rmi4-f01@1`: type `object`; Function 1.
- `rmi4-f1a@1a`: ref `input.yaml#`; type `object`; RMI4 Function 1A is for capacitive keys..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `input.yaml#`, `/schemas/input/touchscreen/touchscreen.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^rmi4-f1[12]@1[12]$` child nodes with required `reg` and properties `reg`, `syna,clip-x-low`, `syna,clip-y-low`, `syna,clip-x-high`, `syna,clip-y-high`, `syna,offset-x`, `syna,offset-y`, `syna,delta-x-threshold`, `syna,delta-y-threshold`, `syna,sensor-type`, `syna,disable-report-mask`, `syna,rezero-wait-ms`; `^rmi4-f[0-9a-f]+@[0-9a-f]+$` child nodes with required `reg` and properties `reg`; `rmi4-f01@1` object node with required `reg` and properties `reg`, `syna,nosleep-mode`, `syna,wakeup-threshold`, `syna,doze-holdoff-ms`, `syna,doze-interval-ms`; `rmi4-f1a@1a` object node with required `reg` and properties `reg`, `linux,keycodes`
- Conditional validation: if `syna,rmi4-i2c`: require none / constrain `spi-rx-delay-us`, `spi-tx-delay-us`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `syna,reset-delay-ms`, `vdd-supply`, `vio-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/syna,rmi4.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 293-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv260x.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv260x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv260x.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Texas Instruments - drv260x Haptics driver family**. The file describes the devicetree contract for the Texas Instruments - drv260x Haptics driver family. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,drv2604`, `ti,drv2605`, `ti,drv2605l`.
- Required top-level fields: `compatible`, `reg`, `enable-gpios`, `mode`, `library-sel`.
- Maintainers: Andrew Davis <afd@ti.com>.
- Top-level properties: `compatible`, `reg`, `vbat-supply`, `mode`, `library-sel`, `enable-gpio`, `enable-gpios`, `vib-rated-mv`, `vib-overdrive-mv`.
- `compatible`: enum `ti,drv2604`, `ti,drv2605`, `ti,drv2605l`.
- `reg`: maxItems 1.
- `vbat-supply`: Power supply to the haptic motor.
- `mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`; Power up mode of the chip (defined in include/dt-bindings/input/ti-drv260x.h) DRV260X_LRA_MODE Linear Resonance Actuator mode (Piezoelectric) DRV260X_LRA_NO_CAL_MODE This is a LRA Mode but there is no calibration sequence during init. And the device is....
- `library-sel`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`, `4`, and 3 more; These are ROM based waveforms pre-programmed into the IC. This should be set to set the library to use at power up. (defined in include/dt-bindings/input/ti-drv260x.h) DRV260X_LIB_EMPTY - Do not use a pre-programmed library DRV260X_ERM_LIB_A -....
- `enable-gpio`: maxItems 1.
- `enable-gpios`: maxItems 1.
- `vib-rated-mv`: ref `/schemas/types.yaml#/definitions/uint32`; The rated voltage of the actuator in millivolts. If this is not set then the value will be defaulted to 3200 mV..
- `vib-overdrive-mv`: ref `/schemas/types.yaml#/definitions/uint32`; The overdrive voltage of the actuator in millivolts. If this is not set then the value will be defaulted to 3200 mV..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `vbat-supply`, `enable-gpio`, `enable-gpios`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,drv260x.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 109-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv260x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv266x.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv266x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv266x.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Texas Instruments - drv266x Haptics driver**. Product Page: http://www.ti.com/product/drv2665 http://www.ti.com/product/drv2667 It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,drv2665`, `ti,drv2667`.
- Required top-level fields: `compatible`, `reg`, `vbat-supply`.
- Maintainers: Anshul Dalal <anshulusr@gmail.com>.
- Top-level properties: `compatible`, `reg`, `vbat-supply`.
- `compatible`: enum `ti,drv2665`, `ti,drv2667`.
- `reg`: maxItems 1.
- `vbat-supply`: Required supply regulator.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `vbat-supply`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,drv266x.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 49-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,drv266x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **TI-NSPIRE Keypad**. The file describes the devicetree contract for the TI-NSPIRE Keypad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,nspire-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `scan-interval`, `row-delay`, `linux,keymap`.
- Maintainers: Andrew Davis <afd@ti.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `scan-interval`, `row-delay`, `active-low`.
- `compatible`: enum `ti,nspire-keypad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `scan-interval`: ref `/schemas/types.yaml#/definitions/uint32`; How often to scan in us. Based on a APB speed of 33MHz, the maximum and minimum delay time is ~2000us and ~500us respectively.
- `row-delay`: ref `/schemas/types.yaml#/definitions/uint32`; How long to wait between scanning each row in us..
- `active-low`: Specify that the keypad is active low..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 74-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,tca8418.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,tca8418.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,tca8418.yaml` is a Linux devicetree YAML schema for a keypad binding: **TI TCA8418 I2C/SMBus keypad scanner**. The file describes the devicetree contract for the TI TCA8418 I2C/SMBus keypad scanner. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,tca8418`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`.
- `compatible`: enum `ti,tca8418`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,tca8418.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 61-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,tca8418.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,twl4030-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,twl4030-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,twl4030-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Texas Instruments TWL4030-family Keypad Controller**. TWL4030's Keypad controller is used to interface a SoC with a matrix-type keypad device. The keypad controller supports multiple row and column lines. A key can be placed at each intersection of a unique row and a unique column. The keypad controller can... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,twl4030-keypad`.
- Required top-level fields: `compatible`, `interrupts`, `keypad,num-rows`, `keypad,num-columns`, `linux,keymap`.
- Maintainers: Peter Ujfalusi <peter.ujfalusi@gmail.com>.
- Top-level properties: `compatible`, `interrupts`.
- `compatible`: const `ti,twl4030-keypad`.
- `interrupts`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `interrupts`.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,twl4030-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 59-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,twl4030-keypad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Analog Devices AD7879(-1)/AD7889(-1) touchscreen interface (SPI/I2C)**. The file describes the devicetree contract for the Analog Devices AD7879(-1)/AD7889(-1) touchscreen interface (SPI/I2C). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `adi,ad7879`, `adi,ad7879-1`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `touchscreen-max-pressure`, `adi,resistance-plate-x`, `touchscreen-swapped-x-y`, `adi,first-conversion-delay`, `adi,acquisition-time`, `adi,median-filter-size`, `adi,averaging`, `adi,conversion-interval`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `adi,ad7879`, `adi,ad7879-1`; for SPI slave, use "adi,ad7879" for I2C slave, use "adi,ad7879-1".
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `touchscreen-max-pressure`: ref `/schemas/types.yaml#/definitions/uint32`; maximum reported pressure.
- `adi,resistance-plate-x`: ref `/schemas/types.yaml#/definitions/uint32`; total resistance of X-plate (for pressure calculation).
- `touchscreen-swapped-x-y`: ref `/schemas/types.yaml#/definitions/flag`; X and Y axis are swapped (boolean).
- `adi,first-conversion-delay`: ref `/schemas/types.yaml#/definitions/uint8`; 0-12: In 128us steps (starting with 128us) 13 : 2.560ms 14 : 3.584ms 15 : 4.096ms This property has to be a '/bits/ 8' value.
- `adi,acquisition-time`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: 2us 1: 4us 2: 8us 3: 16us This property has to be a '/bits/ 8' value.
- `adi,median-filter-size`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: disabled 1: 4 measurements 2: 8 measurements 3: 16 measurements This property has to be a '/bits/ 8' value.
- `adi,averaging`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: 2 middle values (1 if median disabled) 1: 4 middle values 2: 8 middle values 3: 16 values This property has to be a '/bits/ 8' value.
- `adi,conversion-interval`: ref `/schemas/types.yaml#/definitions/uint8`; 0 : convert one time only 1-255: 515us + val * 35us (up to 9.440ms) This property has to be a '/bits/ 8' value.
- `gpio-controller`.
- `#gpio-cells`: const `1`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/spi/spi-peripheral-props.yaml`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 150-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Apple touchscreens attached using the Z2 protocol**. A series of touschscreen controllers used in Apple products It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `apple,j293-touchbar`, `apple,j493-touchbar`.
- Required top-level fields: `compatible`, `interrupts`, `reset-gpios`, `firmware-name`, `touchscreen-size-x`, `touchscreen-size-y`.
- Maintainers: Sasha Finkelstein <k@chaosmail.tech>.
- Top-level properties: `compatible`, `interrupts`, `reset-gpios`, `firmware-name`, `apple,z2-cal-blob`.
- `compatible`: enum `apple,j293-touchbar`, `apple,j493-touchbar`.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `firmware-name`: maxItems 1.
- `apple,z2-cal-blob`: ref `/schemas/types.yaml#/definitions/uint8-array`; maxItems 4096; Calibration blob supplied by the bootloader.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint8-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `interrupts`, `reset-gpios`, `firmware-name`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 70-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS7210A/7211A/E Trackpad/Touchscreen Controller**. The Azoteq IQS7210A, IQS7211A and IQS7211E trackpad and touchscreen control- lers employ projected-capacitance sensing and can track two contacts. Link to datasheets: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs7210a`, `azoteq,iqs7211a`, `azoteq,iqs7211e`.
- Required top-level fields: `compatible`, `reg`, `irq-gpios`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `irq-gpios`, `reset-gpios`, `azoteq,forced-comms`, `azoteq,forced-comms-default`, `azoteq,rate-active-ms`, `azoteq,rate-touch-ms`, `azoteq,rate-idle-ms`, `azoteq,rate-lp1-ms`, `azoteq,rate-lp2-ms`, `azoteq,timeout-active-ms`, `azoteq,timeout-touch-ms`, `azoteq,timeout-idle-ms`, `azoteq,timeout-lp1-ms`, `azoteq,timeout-lp2-ms`, `azoteq,timeout-ati-ms`, `azoteq,timeout-comms-ms`, `azoteq,timeout-press-ms`, `azoteq,fosc-freq`, `azoteq,fosc-trim`, `azoteq,num-contacts`, `azoteq,contact-split`, `azoteq,trim-x`, `azoteq,trim-y`, `trackpad`, `alp`, `button`, and 6 more.
- `compatible`: enum `azoteq,iqs7210a`, `azoteq,iqs7211a`, `azoteq,iqs7211e`.
- `reg`: maxItems 1.
- `irq-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low RDY output. The pin doubles as the IQS7211E's active-low MCLR input, in which case this GPIO must be configured as open-drain..
- `reset-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low MCLR input. The device is temporarily held in hardware reset prior to initialization if this property is present..
- `wakeup-source`.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `azoteq,forced-comms`: type `boolean`; Enables forced communication; to be used with host adapters that cannot tolerate clock stretching..
- `azoteq,forced-comms-default`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`; Indicates if the device's OTP memory enables (1) or disables (0) forced communication by default. Specifying this property can expedite startup time if the default value is known. If this property is not specified, communication is not initiated until the....
- `azoteq,rate-active-ms`: Specifies the report rate (in ms) during active mode..
- `azoteq,rate-touch-ms`: Specifies the report rate (in ms) during idle-touch mode..
- `azoteq,rate-idle-ms`: Specifies the report rate (in ms) during idle mode..
- `azoteq,rate-lp1-ms`: Specifies the report rate (in ms) during low-power mode 1..
- `azoteq,rate-lp2-ms`: Specifies the report rate (in ms) during low-power mode 2..
- `azoteq,timeout-active-ms`: Specifies the length of time (in ms) to wait for an event before moving from active mode to idle or idle-touch modes..
- `azoteq,timeout-touch-ms`: Specifies the length of time (in ms) to wait for an event before moving from idle-touch mode to idle mode..
- `azoteq,timeout-idle-ms`: Specifies the length of time (in ms) to wait for an event before moving from idle mode to low-power mode 1..
- `azoteq,timeout-lp1-ms`: Specifies the length of time (in ms) to wait for an event before moving from low-power mode 1 to low-power mode 2..
- additional schema properties: `azoteq,timeout-lp2-ms`, `azoteq,timeout-ati-ms`, `azoteq,timeout-comms-ms`, `azoteq,timeout-press-ms`, `azoteq,fosc-freq`, `azoteq,fosc-trim`, `azoteq,num-contacts`, `azoteq,contact-split`, `azoteq,trim-x`, `azoteq,trim-y`, `trackpad`, `alp`, `button`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `../input.yaml#`, `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `trackpad` object node with required none and properties `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,channel-select`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,touch-enter`, `azoteq,touch-exit`, `azoteq,thresh`, `azoteq,conv-period`, and 1 more; `alp` object node with required none and properties `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,ati-base`, `azoteq,ati-mode`, `azoteq,sense-mode`, `azoteq,debounce-enter`, `azoteq,debounce-exit`, and 4 more; `button` object node with required none and properties `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,ati-base`, `azoteq,ati-mode`, `azoteq,sense-mode`, `azoteq,touch-enter`, `azoteq,touch-exit`, `azoteq,debounce-enter`, `azoteq,debounce-exit`, and 3 more
- Conditional validation: if `azoteq,iqs7210a`: require none / constrain `alp`; if `azoteq,iqs7211e`: require none / constrain `reset-gpios`, `trackpad`, `alp`
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `irq-gpios`, `reset-gpios`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 769-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/chipone,icn8318.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/chipone,icn8318.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/chipone,icn8318.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **ChipOne ICN8318 Touchscreen Controller**. The file describes the devicetree contract for the ChipOne ICN8318 Touchscreen Controller. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `chipone,icn8318`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `wake-gpios`, `touchscreen-size-x`, `touchscreen-size-y`.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wake-gpios`.
- `compatible`: const `chipone,icn8318`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wake-gpios`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `wake-gpios`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/chipone,icn8318.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 62-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/chipone,icn8318.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma140.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma140.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma140.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Cypress CY8CTMA140 series touchscreen controller**. The file describes the devicetree contract for the Cypress CY8CTMA140 series touchscreen controller. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,cy8ctma140`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-max-pressure`.
- Maintainers: Linus Walleij <linusw@kernel.org>.
- Top-level properties: `compatible`, `reg`, `clock-frequency`, `interrupts`, `vcpin-supply`, `vdd-supply`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-swapped-x-y`, `touchscreen-max-pressure`.
- `compatible`: const `cypress,cy8ctma140`.
- `reg`: const `32`.
- `interrupts`: maxItems 1.
- `vdd-supply`: Digital power supply regulator on VDD pin.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `clock-frequency`: I2C client clock frequency, defined for host.
- `vcpin-supply`: Analog power supply regulator on VCPIN pin.
- `touchscreen-inverted-x`.
- `touchscreen-inverted-y`.
- `touchscreen-swapped-x-y`.
- `touchscreen-max-pressure`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clock-frequency`, `interrupts`, `vcpin-supply`, `vdd-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma140.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 72-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma140.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma340.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma340.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma340.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Cypress CY8CTMA340 series touchscreen controller**. The Cypress CY8CTMA340 series (also known as "CYTTSP" after the marketing name Cypress TrueTouch Standard Product) touchscreens can be connected to either I2C or SPI buses. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,cy8ctma340`, `cypress,cy8ctst341`, `cypress,cyttsp-spi`, `cypress,cyttsp-i2c`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `bootloader-key`, `touchscreen-size-x`, `touchscreen-size-y`.
- Maintainers: Javier Martinez Canillas <javier@dowhile0.org>, Linus Walleij <linusw@kernel.org>.
- Top-level properties: `$nodename`, `compatible`, `reg`, `clock-frequency`, `spi-max-frequency`, `interrupts`, `vcpin-supply`, `vdd-supply`, `reset-gpios`, `bootloader-key`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-fuzz-x`, `touchscreen-fuzz-y`, `active-distance`, `active-interval-ms`, `lowpower-interval-ms`, `touch-timeout-ms`, `use-handshake`.
- `compatible`.
- `reg`: I2C address when used on the I2C bus, or the SPI chip select index when used on the SPI bus.
- `interrupts`: maxItems 1; Interrupt to host.
- `reset-gpios`: Reset line for the touchscreen, should be tagged as GPIO_ACTIVE_LOW.
- `vdd-supply`: Digital power supply regulator on VDD pin.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `$nodename`.
- `clock-frequency`: I2C client clock frequency, defined for host when using the device on the I2C bus.
- `spi-max-frequency`: SPI clock frequency, defined for host, defined when using the device on the SPI bus. The throughput is maximum 2 Mbps so the typical value is 2000000, if higher rates are used the total throughput needs to be restricted to 2 Mbps..
- `vcpin-supply`: Analog power supply regulator on VCPIN pin.
- `bootloader-key`: ref `/schemas/types.yaml#/definitions/uint8-array`; maxItems 8; minItems 8; the 8-byte bootloader key that is required to switch the chip from bootloader mode (default mode) to application mode.
- `touchscreen-fuzz-x`.
- `touchscreen-fuzz-y`.
- `active-distance`: ref `/schemas/types.yaml#/definitions/uint32`; the distance in pixels beyond which a touch must move before movement is detected and reported by the device.
- `active-interval-ms`: the minimum period in ms between consecutive scanning/processing cycles when the chip is in active mode.
- `lowpower-interval-ms`: the minimum period in ms between consecutive scanning/processing cycles when the chip is in low-power mode.
- `touch-timeout-ms`: minimum time in ms spent in the active power state while no touches are detected before entering low-power mode.
- additional schema properties: `use-handshake`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clock-frequency`, `interrupts`, `vcpin-supply`, `vdd-supply`, `reset-gpios`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma340.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 148-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,cy8ctma340.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,tt21000.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,tt21000.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,tt21000.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Cypress TT21000 touchscreen controller**. The Cypress TT21000 series (also known as "CYTTSP5" after the marketing name Cypress TrueTouch Standard Product series 5). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `cypress,tt21000`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vdd-supply`.
- Maintainers: Alistair Francis <alistair@alistair23.me>.
- Top-level properties: `compatible`, `reg`, `#address-cells`, `#size-cells`, `interrupts`, `vdd-supply`, `vddio-supply`, `reset-gpios`, `linux,keycodes`, `wakeup-source`.
- `compatible`: const `cypress,tt21000`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `linux,keycodes`: EV_ABS specific event code generated by the axis..
- `vdd-supply`: Regulator for voltage..
- `wakeup-source`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `vddio-supply`: Optional Regulator for I/O voltage..
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`, `../input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^button@[0-9]+$` child nodes with required `reg`, `linux,keycodes` and properties `reg`, `linux,keycodes`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vdd-supply`, `vddio-supply`, `reset-gpios`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/cypress,tt21000.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 111-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/cypress,tt21000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/edt-ft5x06.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/edt-ft5x06.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/edt-ft5x06.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **FocalTech EDT-FT5x06 Polytouch**. There are 5 variants of the chip for various touch panel sizes FT5206GE1 2.8" .. 3.8" FT5306DE4 4.3" .. 7" FT5406EE8 7" .. 8.9" FT5506EEG 7" .. 8.9" FT5726NEI 5.7” .. 11.6" It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `edt,edt-ft5206`, `edt,edt-ft5306`, `edt,edt-ft5406`, `edt,edt-ft5506`, `evervision,ev-ft5726`, `focaltech,ft3518`, `focaltech,ft5426`, `focaltech,ft5452`, `focaltech,ft6236`, `focaltech,ft8201`, `focaltech,ft8716`, `focaltech,ft8719`, `focaltech,ft3519`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `reset-gpios`, `wake-gpios`, `wakeup-source`, `vcc-supply`, `iovcc-supply`, `gain`, `offset`, `offset-x`, `offset-y`, `report-rate-hz`, `threshold`, `interrupt-controller`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `vcc-supply`.
- `wakeup-source`.
- `wake-gpios`: maxItems 1.
- `iovcc-supply`.
- `gain`: ref `/schemas/types.yaml#/definitions/uint32`; Allows setting the sensitivity in the range from 0 to 31. Note that lower values indicate higher sensitivity..
- `offset`: ref `/schemas/types.yaml#/definitions/uint32`; Allows setting the edge compensation in the range from 0 to 31..
- `offset-x`: ref `/schemas/types.yaml#/definitions/uint32`; Same as offset, but applies only to the horizontal position. Range from 0 to 80, only supported by evervision,ev-ft5726 devices..
- `offset-y`: ref `/schemas/types.yaml#/definitions/uint32`; Same as offset, but applies only to the vertical position. Range from 0 to 80, only supported by evervision,ev-ft5726 devices..
- `report-rate-hz`: Allows setting the scan rate in Hertz. M06 supports range from 30 to 140 Hz. M12 supports range from 1 to 255 Hz..
- `threshold`: ref `/schemas/types.yaml#/definitions/uint32`; Allows setting the "click"-threshold in the range from 0 to 255..
- `interrupt-controller`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `evervision,ev-ft5726`: require none / constrain `offset-x`, `offset-y`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `wake-gpios`, `vcc-supply`, `iovcc-supply`, `interrupt-controller`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/edt-ft5x06.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 138-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/edt-ft5x06.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/eeti,exc3000.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/eeti,exc3000.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/eeti,exc3000.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **EETI EXC3000 series touchscreen controller**. The file describes the devicetree contract for the EETI EXC3000 series touchscreen controller. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `eeti,exc3000`, `eeti,exc80h60`, `eeti,exc80h84`, `eeti,egalax_ts`, `eeti,exc3000-i2c`, `eeti,exc81w32`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Dmitry Torokhov <dmitry.torokhov@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `reset-gpios`, `wakeup-gpios`, `vdd-supply`, `attn-gpios`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- `compatible`.
- `reg`: enum `4`, `10`, `42`.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `vdd-supply`: Power supply regulator for the chip.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `wakeup-gpios`: maxItems 1.
- `attn-gpios`: maxItems 1; Phandle to a GPIO to check whether interrupt is still latched. This is necessary for platforms that lack support for level-triggered IRQs..
- `touchscreen-inverted-x`.
- `touchscreen-inverted-y`.
- `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `eeti,egalax_ts`, `eeti,exc3000-i2c`: require `touchscreen-size-x`, `touchscreen-size-y` / constrain `reg`, `wakeup-gpios`, `attn-gpios`
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `wakeup-gpios`, `vdd-supply`, `attn-gpios`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/eeti,exc3000.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 94-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/eeti,exc3000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,ektf2127.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,ektf2127.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,ektf2127.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Elan eKTF2127 I2C touchscreen controller**. The file describes the devicetree contract for the Elan eKTF2127 I2C touchscreen controller. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `elan,ektf2127`, `elan,ektf2132`, `elan,ektf2232`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `power-gpios`.
- Maintainers: Siebren Vroegindeweij <siebren.vroegindeweij@hotmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `power-gpios`.
- `compatible`: enum `elan,ektf2127`, `elan,ektf2132`, `elan,ektf2232`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `power-gpios`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `power-gpios`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/elan,ektf2127.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 58-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,ektf2127.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,elants_i2c.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,elants_i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,elants_i2c.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Elantech I2C Touchscreen**. The file describes the devicetree contract for the Elantech I2C Touchscreen. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `elan,ektf3624`, `elan,ekth3500`, `elan,ekth3915`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: David Heidelberg <david@ixit.cz>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wakeup-source`, `reset-gpios`, `vcc33-supply`, `vccio-supply`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-swapped-x-y`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; reset gpio the chip is connected to..
- `wakeup-source`: type `boolean`; touchscreen can be used as a wakeup source..
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `vcc33-supply`: a phandle for the regulator supplying 3.3V power..
- `vccio-supply`: a phandle for the regulator supplying IO power..
- `touchscreen-inverted-x`.
- `touchscreen-inverted-y`.
- `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/elan,elants_i2c.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 74-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/elan,elants_i2c.yaml -->
