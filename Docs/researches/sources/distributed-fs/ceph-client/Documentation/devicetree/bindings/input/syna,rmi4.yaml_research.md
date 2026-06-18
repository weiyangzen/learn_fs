<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Synaptics RMI4 compliant devices**. The Synaptics RMI4 (Register Mapped Interface 4) core is able to support RMI4 devices using different transports (I2C, SPI) and different functions (e.g. Function 1, 2D sensors using Function 11 or 12). It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `syna,rmi4-i2c`, `syna,rmi4-spi`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Jason A. Donenfeld <Jason@zx2c4.com>, Matthias Schiffer <matthias.schiffer@ew.tq-group.com>, Vincent Huang <vincent.huang@tw.synaptics.com>.
- Top-level properties: `compatible`, `reg`, `#address-cells`, `#size-cells`, `interrupts`, `reset-gpios`, `spi-cpha`, `spi-cpol`, `syna,reset-delay-ms`, `syna,startup-delay-ms`, `vdd-supply`, `vio-supply`, `rmi4-f01@1`, `rmi4-f1a@1a`.
- `compatible`: enum `syna,rmi4-i2c`, `syna,rmi4-spi`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1; Active low signal.
- `vdd-supply`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `spi-cpha`.
- `spi-cpol`.
- `syna,reset-delay-ms`: Delay to wait after resetting the device..
- `syna,startup-delay-ms`: Delay to wait after powering on the device..
- `vio-supply`.
- `rmi4-f01@1`: type `object`; Function 1.
- `rmi4-f1a@1a`: ref `input.yaml#`; type `object`; RMI4 Function 1A is for capacitive keys..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `input.yaml#`, `/schemas/input/touchscreen/touchscreen.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^rmi4-f1[12]@1[12]$` child nodes with required `reg` and properties `reg`, `syna,clip-x-low`, `syna,clip-y-low`, `syna,clip-x-high`, `syna,clip-y-high`, `syna,offset-x`, `syna,offset-y`, `syna,delta-x-threshold`, `syna,delta-y-threshold`, `syna,sensor-type`, `syna,disable-report-mask`, `syna,rezero-wait-ms`; `^rmi4-f[0-9a-f]+@[0-9a-f]+$` child nodes with required `reg` and properties `reg`; `rmi4-f01@1` object node with required `reg` and properties `reg`, `syna,nosleep-mode`, `syna,wakeup-threshold`, `syna,doze-holdoff-ms`, `syna,doze-interval-ms`; `rmi4-f1a@1a` object node with required `reg` and properties `reg`, `linux,keycodes`
- Conditional validation: if `syna,rmi4-i2c`: require none / constrain `spi-rx-delay-us`, `spi-tx-delay-us`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `reset-gpios`, `syna,reset-delay-ms`, `vdd-supply`, `vio-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/syna,rmi4.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 293-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/syna,rmi4.yaml -->
