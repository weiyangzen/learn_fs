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
