<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Allwinner A10 LRADC**. The file describes the devicetree contract for the Allwinner A10 LRADC. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `allwinner,sun4i-a10-lradc-keys`, `allwinner,sun8i-a83t-r-lradc`, `allwinner,suniv-f1c100s-lradc`, `allwinner,sun50i-a64-lradc`, `allwinner,sun50i-r329-lradc`, `allwinner,sun50i-h616-lradc`, `allwinner,sun20i-d1-lradc`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vref-supply`.
- Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.
- Top-level properties: `compatible`, `reg`, `clocks`, `resets`, `interrupts`, `vref-supply`, `wakeup-source`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `clocks`: maxItems 1.
- `resets`: maxItems 1.
- `vref-supply`: Regulator for the LRADC reference voltage.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^button-[0-9]+$` child nodes with required `label`, `linux,code`, `channel`, `voltage` and properties `label`, `linux,code`, `channel`, `voltage`
- Conditional validation: if `allwinner,sun50i-r329-lradc`: require `clocks`, `resets` / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clocks`, `resets`, `interrupts`, `vref-supply`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 120-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/allwinner,sun4i-a10-lradc-keys.yaml -->
