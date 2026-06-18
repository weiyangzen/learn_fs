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
