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
