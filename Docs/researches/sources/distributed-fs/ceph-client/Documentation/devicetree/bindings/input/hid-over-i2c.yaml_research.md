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
