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
