<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,slg51000.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,slg51000.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Dialog Semiconductor SLG51000 Voltage Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/dlg,slg51000.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Eric Jeong <eric.jeong.opensource@diasemi.com>, Support Opensource <support.opensource@diasemi.com>.
- Compatible contract: `dlg,slg51000`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`, `regulator-name`
- Top-level declared properties (10): `compatible`, `reg`, `interrupts`, `dlg,cs-gpios`, `vin3-supply`, `vin4-supply`, `vin5-supply`, `vin6-supply`, `vin7-supply`, `regulators`
- Regulator/vendor integration properties: `dlg,cs-gpios`, `vin3-supply`, `vin4-supply`, `vin5-supply`, `vin6-supply`, `vin7-supply`
- Property detail signals:
  - `compatible` (const `dlg,slg51000`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `dlg,cs-gpios` (maxItems 1; GPIO for chip select)
  - `vin3-supply` (Input supply for ldo3, required if regulator is enabled)
  - `vin4-supply` (Input supply for ldo4, required if regulator is enabled)
  - `vin5-supply` (Input supply for ldo5, required if regulator is enabled)
  - `vin6-supply` (Input supply for ldo6, required if regulator is enabled)
  - `vin7-supply` (Input supply for ldo7, required if regulator is enabled)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/regulator/regulator.yaml#`
- Textual schema references: `/schemas/regulator/dlg,slg51000.yaml`; `/schemas/regulator/regulator.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/regulator/dlg,da9121-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,slg51000.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,slg51000.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/regulator/dlg,da9121-regulator.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,slg51000.yaml -->
