<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **GPIO matrix keypad**. GPIO driven matrix keypad is used to interface a SoC with a matrix keypad. The matrix keypad supports multiple row and column lines, a key can be placed at each intersection of a unique row and a unique column. The matrix keypad can sense a key-press and... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `row-gpios`, `col-gpios`, `linux,keymap`.
- Maintainers: Marek Vasut <marek.vasut@gmail.com>.
- Top-level properties: `compatible`, `row-gpios`, `col-gpios`, `linux,keymap`, `linux,no-autorepeat`, `gpio-activelow`, `debounce-delay-ms`, `col-scan-delay-us`, `all-cols-on-delay-us`, `drive-inactive-cols`, `wakeup-source`.
- `compatible`: const `gpio-matrix-keypad`.
- `linux,keymap`.
- `wakeup-source`.
- `row-gpios`: List of GPIOs used as row lines. The gpio specifier for this property depends on the gpio controller to which these row lines are connected..
- `col-gpios`: List of GPIOs used as column lines. The gpio specifier for this property depends on the gpio controller to which these column lines are connected..
- `linux,no-autorepeat`: type `boolean`; Do not enable autorepeat feature..
- `gpio-activelow`: type `boolean`; Force GPIO polarity to active low. In the absence of this property GPIOs are treated as active high..
- `debounce-delay-ms`.
- `col-scan-delay-us`: Delay, measured in microseconds, that is needed before we can scan keypad after activating column gpio..
- `all-cols-on-delay-us`: Delay, measured in microseconds, that is needed after activating all column gpios..
- `drive-inactive-cols`: type `boolean`; Drive inactive columns during scan, default is to turn inactive columns into inputs..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `row-gpios`, `col-gpios`, `gpio-activelow`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 102-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-matrix-keypad.yaml -->
