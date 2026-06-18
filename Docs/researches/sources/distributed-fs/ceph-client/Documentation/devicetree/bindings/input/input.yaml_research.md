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
