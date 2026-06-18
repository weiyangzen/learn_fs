<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pca9450-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pca9450-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: NXP PCA9450A/B/C Power Management Integrated Circuit regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Regulator nodes should be named to BUCK_<number> and LDO_<number>. The definition for each of these nodes is defined using the standard binding for regulators at Documentation/devicetree/bindings/regulator/regulator.txt. Datasheet is available at https://www.nxp.com/docs/en/data-sheet/PCA9450DS.pdf Support PF9453, Datasheet is available at https://www.nxp.com/docs/en/data-sheet/PF9453_SDS.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/nxp,pca9450-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Robin Gong <yibin.gong@nxp.com>.
- Compatible contract: `nxp,pca9450a`, `nxp,pca9450b`, `nxp,pca9450c`, `nxp,pca9451a`, `nxp,pca9452`, `nxp,pf9453`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (16): `compatible`, `reg`, `interrupts`, `inl1-supply`, `inb13-supply`, `inb26-supply`, `inb45-supply`, `regulators`, `nxp,i2c-lt-enable`, `nxp,wdog_b-warm-reset`, `nxp,pmic-on-req-on-debounce-us`, `nxp,pmic-on-req-off-debounce-us`, `nxp,power-on-step-ms`, `nxp,power-down-step-ms`, `nxp,restart-ms`, `npx,pmic-rst-b-debounce-ms`
- Regulator/vendor integration properties: `inl1-supply`, `inb13-supply`, `inb26-supply`, `inb45-supply`, `nxp,i2c-lt-enable`, `nxp,wdog_b-warm-reset`, `nxp,pmic-on-req-on-debounce-us`, `nxp,pmic-on-req-off-debounce-us`, `nxp,power-on-step-ms`, `nxp,power-down-step-ms`, `nxp,restart-ms`, `npx,pmic-rst-b-debounce-ms`
- Property detail signals:
  - `compatible` (enum `nxp,pca9450a`, `nxp,pca9450b`, `nxp,pca9450c`, `nxp,pca9451a`, `nxp,pca9452`, `nxp,pf9453`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `inl1-supply` (Regulator supply for the INL1 pin group, powering LDOx)
  - `inb13-supply` (Regulator supply for the INB13 pin group, powering BUCK1 and BUCK3.)
  - `inb26-supply` (Regulator supply for the INB26 pin group, powering BUCK2 and BUCK6.)
  - `inb45-supply` (Regulator supply for the INB45 pin group, powering BUCK4 and BUCK5.)
  - `regulators` (type object; list of regulators provided by this controller)
  - `nxp,i2c-lt-enable` (type boolean; Indicates that the I2C Level Translator is used.)
  - `nxp,wdog_b-warm-reset` (type boolean; When WDOG_B signal is asserted a warm reset will be done instead of cold reset.)
  - `nxp,pmic-on-req-on-debounce-us` (enum `120`, `20000`, `100000`, `750000`; Debounce time for PMIC_ON_REQ high.)
  - `nxp,pmic-on-req-off-debounce-us` (enum `120`, `2000`; Debounce time for PMIC_ON_REQ is asserted low)
  - `nxp,power-on-step-ms` (enum `1`, `2`, `4`, `8`; Time step configuration during power on sequence)
  - `nxp,power-down-step-ms` (enum `2`, `4`, `8`, `16`; Time step configuration during power down sequence)
  - `nxp,restart-ms` (enum `250`, `500`; Time to stay off regulators during Cold reset)
  - `npx,pmic-rst-b-debounce-ms` (enum `10`, `50`, `100`, `500`, `1000`, `2000`, `4000`, `8000`; PMIC_RST_B debounce time)
- Child-node or pattern API:
  - `regulators` child object with properties LDO5

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 1 `if` block(s), 1 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/nxp,pca9450-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/regulator/nxp,pca9450-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pca9450-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pca9450-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/regulator/nxp,pca9450-regulator.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pca9450-regulator.yaml -->
