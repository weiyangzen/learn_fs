<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8952.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8952.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8952 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max8952.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max8952`
- Top-level required properties: `compatible`, `max8952,dvs-mode-microvolt`, `reg`
- Required keys across top-level and child schemas: `compatible`, `max8952,dvs-mode-microvolt`, `reg`
- Top-level declared properties (8): `compatible`, `max8952,default-mode`, `max8952,dvs-mode-microvolt`, `max8952,en-gpio`, `max8952,ramp-speed`, `max8952,sync-freq`, `max8952,vid-gpios`, `reg`
- Regulator/vendor integration properties: `max8952,default-mode`, `max8952,dvs-mode-microvolt`, `max8952,en-gpio`, `max8952,ramp-speed`, `max8952,sync-freq`, `max8952,vid-gpios`
- Property detail signals:
  - `compatible` (const `maxim,max8952`)
  - `max8952,default-mode` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`; index of default DVS voltage)
  - `max8952,dvs-mode-microvolt` (minItems 4; maxItems 4; Array of 4 integer values defining DVS voltages in microvolts. All values must be from range <770000, 1400000>.)
  - `max8952,en-gpio` (maxItems 1; GPIO used to control enable status of regulator)
  - `max8952,ramp-speed` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`; default 0; Voltage ramp speed, values map to: - 0: 32mV/us - 1: 16mV/us - 2: 8mV/us - 3: 4mV/us - 4: 2mV/us - 5: 1mV/us - 6: 0.5mV/...)
  - `max8952,sync-freq` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`, `2`; default 0; Sync frequency, values map to: - 0: 26 MHz - 1: 13 MHz - 2: 19.2 MHz Defaults to 26 MHz if not specified.)
  - `max8952,vid-gpios` (minItems 2; maxItems 2; Array of two GPIO pins used for DVS voltage selection)
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/maxim,max8952.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, max8952,dvs-mode-microvolt, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8952.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8952.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8952.yaml -->
