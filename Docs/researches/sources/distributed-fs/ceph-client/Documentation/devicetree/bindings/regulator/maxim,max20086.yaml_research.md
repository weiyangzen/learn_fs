<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20086.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20086.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim Integrated MAX20086-MAX20089 Camera Power Protector. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MAX20086-MAX20089 are dual/quad camera power protectors, designed to deliver power over coax for radar and camera modules. They support software-configurable output switching and monitoring. The output voltage and current limit are fixed by the hardware design.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max20086.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- Compatible contract: `maxim,max20086`, `maxim,max20087`, `maxim,max20088`, `maxim,max20089`
- Top-level required properties: `compatible`, `reg`, `in-supply`, `vdd-supply`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `in-supply`, `vdd-supply`, `regulators`
- Top-level declared properties (6): `compatible`, `reg`, `enable-gpios`, `in-supply`, `vdd-supply`, `regulators`
- Regulator/vendor integration properties: `enable-gpios`, `in-supply`, `vdd-supply`
- Property detail signals:
  - `compatible` (enum `maxim,max20086`, `maxim,max20087`, `maxim,max20088`, `maxim,max20089`)
  - `reg` (maxItems 1)
  - `enable-gpios` (maxItems 1; GPIO connected to the EN pin, active high)
  - `in-supply` (Input supply for the camera outputs (IN pin, 3.0V to 15.0V))
  - `vdd-supply` (Input supply for the device (VDD pin, 3.0V to 5.5V))
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 1 `if` block(s), 1 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max20086.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, in-supply, vdd-supply, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20086.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20086.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20086.yaml -->
