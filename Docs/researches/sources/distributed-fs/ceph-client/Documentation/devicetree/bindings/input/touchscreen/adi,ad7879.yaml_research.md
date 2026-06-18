<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Analog Devices AD7879(-1)/AD7889(-1) touchscreen interface (SPI/I2C)**. The file describes the devicetree contract for the Analog Devices AD7879(-1)/AD7889(-1) touchscreen interface (SPI/I2C). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `adi,ad7879`, `adi,ad7879-1`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `touchscreen-max-pressure`, `adi,resistance-plate-x`, `touchscreen-swapped-x-y`, `adi,first-conversion-delay`, `adi,acquisition-time`, `adi,median-filter-size`, `adi,averaging`, `adi,conversion-interval`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `adi,ad7879`, `adi,ad7879-1`; for SPI slave, use "adi,ad7879" for I2C slave, use "adi,ad7879-1".
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `touchscreen-max-pressure`: ref `/schemas/types.yaml#/definitions/uint32`; maximum reported pressure.
- `adi,resistance-plate-x`: ref `/schemas/types.yaml#/definitions/uint32`; total resistance of X-plate (for pressure calculation).
- `touchscreen-swapped-x-y`: ref `/schemas/types.yaml#/definitions/flag`; X and Y axis are swapped (boolean).
- `adi,first-conversion-delay`: ref `/schemas/types.yaml#/definitions/uint8`; 0-12: In 128us steps (starting with 128us) 13 : 2.560ms 14 : 3.584ms 15 : 4.096ms This property has to be a '/bits/ 8' value.
- `adi,acquisition-time`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: 2us 1: 4us 2: 8us 3: 16us This property has to be a '/bits/ 8' value.
- `adi,median-filter-size`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: disabled 1: 4 measurements 2: 8 measurements 3: 16 measurements This property has to be a '/bits/ 8' value.
- `adi,averaging`: ref `/schemas/types.yaml#/definitions/uint8`; enum `0`, `1`, `2`, `3`; 0: 2 middle values (1 if median disabled) 1: 4 middle values 2: 8 middle values 3: 16 values This property has to be a '/bits/ 8' value.
- `adi,conversion-interval`: ref `/schemas/types.yaml#/definitions/uint8`; 0 : convert one time only 1-255: 515us + val * 35us (up to 9.440ms) This property has to be a '/bits/ 8' value.
- `gpio-controller`.
- `#gpio-cells`: const `1`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/spi/spi-peripheral-props.yaml`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 150-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/adi,ad7879.yaml -->
