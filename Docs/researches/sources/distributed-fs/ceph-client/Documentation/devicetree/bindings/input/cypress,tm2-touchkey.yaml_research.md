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
