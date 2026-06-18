<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **PWM vibrator**. Registers a PWM device as vibrator. It is expected, that the vibrator's strength increases based on the duty cycle of the enable PWM channel (100% duty cycle meaning strongest vibration, 0% meaning no vibration). The binding supports an optional direction... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `pwm-names`, `pwms`.
- Maintainers: Sebastian Reichel <sre@kernel.org>.
- Top-level properties: `compatible`, `pwm-names`, `pwms`, `enable-gpios`, `vcc-supply`, `direction-duty-cycle-ns`.
- `compatible`: const `pwm-vibrator`.
- `pwms`: maxItems 2; minItems 1.
- `vcc-supply`.
- `pwm-names`: minItems 1.
- `enable-gpios`.
- `direction-duty-cycle-ns`: Duty cycle of the direction PWM channel in nanoseconds, defaults to 50% of the channel's period..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `pwm-names`, `pwms`, `enable-gpios`, `vcc-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/pwm-vibrator.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 59-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pwm-vibrator.yaml -->
