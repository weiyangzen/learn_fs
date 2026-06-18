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
