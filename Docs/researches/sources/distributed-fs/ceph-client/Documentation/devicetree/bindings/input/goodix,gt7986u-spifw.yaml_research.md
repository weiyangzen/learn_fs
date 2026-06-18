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
