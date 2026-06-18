<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Voltage/Current Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (41): `regulator-name`, `regulator-min-microvolt`, `regulator-max-microvolt`, `regulator-microvolt-offset`, `regulator-min-microamp`, `regulator-max-microamp`, `regulator-input-current-limit-microamp`, `regulator-power-budget-milliwatt`, `regulator-always-on`, `regulator-boot-on`, `regulator-allow-bypass`, `regulator-allow-set-load`, `regulator-ramp-delay`, `regulator-enable-ramp-delay`, `regulator-settling-time-us`, `regulator-settling-time-up-us`, `regulator-settling-time-down-us`, `regulator-soft-start`, `regulator-initial-mode`, `regulator-allowed-modes`, `regulator-system-load`, `regulator-pull-down`, `system-critical-regulator`, `regulator-over-current-protection`, ... (41 total)
- Regulator/vendor integration properties: `regulator-name`, `regulator-min-microvolt`, `regulator-max-microvolt`, `regulator-microvolt-offset`, `regulator-min-microamp`, `regulator-max-microamp`, `regulator-input-current-limit-microamp`, `regulator-power-budget-milliwatt`, `regulator-always-on`, `regulator-boot-on`, `regulator-allow-bypass`, `regulator-allow-set-load`, `regulator-ramp-delay`, `regulator-enable-ramp-delay`, `regulator-settling-time-us`, `regulator-settling-time-up-us`, `regulator-settling-time-down-us`, `regulator-soft-start`, `regulator-initial-mode`, `regulator-allowed-modes`, `regulator-system-load`, `regulator-pull-down`, `system-critical-regulator`, `regulator-over-current-protection`, ... (41 total)
- Property detail signals:
  - `regulator-name` (ref /schemas/types.yaml#/definitions/string; A string used as a descriptive name for regulator outputs)
  - `regulator-min-microvolt` (smallest voltage consumers may set)
  - `regulator-max-microvolt` (largest voltage consumers may set)
  - `regulator-microvolt-offset` (ref /schemas/types.yaml#/definitions/uint32; Offset applied to voltages to compensate for voltage drops)
  - `regulator-min-microamp` (smallest current consumers may set)
  - `regulator-max-microamp` (largest current consumers may set)
  - `regulator-input-current-limit-microamp` (maximum input current regulator allows)
  - `regulator-power-budget-milliwatt` (power budget of the regulator)
  - `regulator-always-on` (type boolean; boolean, regulator should never be disabled)
  - `regulator-boot-on` (type boolean; bootloader/firmware enabled regulator. It's expected that this regulator was left on by the bootloader. If the bootloade...)
  - `regulator-allow-bypass` (type boolean; allow the regulator to go into bypass mode)
  - `regulator-allow-set-load` (type boolean; allow the regulator performance level to be configured)
  - `regulator-ramp-delay` (ref /schemas/types.yaml#/definitions/uint32; ramp delay for regulator(in uV/us) For hardware which supports disabling ramp rate, it should be explicitly initialised ...)
  - `regulator-enable-ramp-delay` (ref /schemas/types.yaml#/definitions/uint32; The time taken, in microseconds, for the supply rail to reach the target voltage, plus/minus whatever tolerance the boar...)
  - `regulator-settling-time-us` (Settling time, in microseconds, for voltage change if regulator have the constant time for any level voltage change. Thi...)
  - `regulator-settling-time-up-us` (Settling time, in microseconds, for voltage increase if the regulator needs a constant time to settle after voltage incr...)
  - `regulator-settling-time-down-us` (Settling time, in microseconds, for voltage decrease if the regulator needs a constant time to settle after voltage decr...)
  - `regulator-soft-start` (type boolean; Enable soft start so that voltage ramps slowly)
  - ... plus 23 more top-level declared propertie(s).
- Child-node or pattern API:
  - pattern child/property `.*-supply$`
  - pattern child/property `^regulator-state-(standby|mem|disk)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: True`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/phandle-array`
- Textual schema references: `/schemas/regulator/regulator.yaml`; `/schemas/types.yaml#/definitions/phandle-array`; `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `xyzreg: regulator {; regulator-min-microvolt = <1000000>;; regulator-max-microvolt = <2500000>;; regulator-always-on;; vin-supply = <&vin>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator.yaml -->
