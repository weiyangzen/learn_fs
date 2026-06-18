<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fitipower,fp9931.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fitipower,fp9931.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: FitiPower FP9931/JD9930 Power Management Integrated Circuit. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: FP9931 is a Power Management IC to provide Power for EPDs with one 3.3V switch, 2 symmetric LDOs behind 2 DC/DC converters, and one unsymmetric regulator for a compensation voltage. JD9930 has in addition some kind of night mode.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/fitipower,fp9931.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Andreas Kemnade <andreas@kemnade.info>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`, `vin-supply`, `pg-gpios`, `enable-gpios`
- Required keys across top-level and child schemas: `compatible`, `reg`, `vin-supply`, `pg-gpios`, `enable-gpios`
- Top-level declared properties (9): `compatible`, `reg`, `enable-gpios`, `pg-gpios`, `en-ts-gpios`, `xon-gpios`, `vin-supply`, `fitipower,tdly-ms`, `regulators`
- Regulator/vendor integration properties: `enable-gpios`, `vin-supply`, `fitipower,tdly-ms`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1)
  - `enable-gpios` (maxItems 1)
  - `pg-gpios` (maxItems 1)
  - `en-ts-gpios` (maxItems 1)
  - `xon-gpios` (maxItems 1)
  - `vin-supply` (Supply for the whole chip. Some vendor kernels and devicetrees declare this as a non-existing GPIO named "pwrall".)
  - `fitipower,tdly-ms` (4 fixed item schema(s); Power up soft start delay settings tDLY1-4 bitfields in the POWERON_DELAY register)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/regulator/regulator.yaml`
- Textual schema references: `/schemas/regulator/fitipower,fp9931.yaml`; `/schemas/regulator/regulator.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, vin-supply, pg-gpios, enable-gpios) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fitipower,fp9931.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fitipower,fp9931.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@18 {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fitipower,fp9931.yaml -->
