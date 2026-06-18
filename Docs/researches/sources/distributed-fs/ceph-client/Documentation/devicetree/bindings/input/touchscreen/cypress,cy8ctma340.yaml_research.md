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
