<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pfuze100.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pfuze100.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: PFUZE100 family of regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The valid names for regulators are: --PFUZE100 sw1ab,sw1c,sw2,sw3a,sw3b,sw4,swbst,vsnvs,vrefddr,vgen1~vgen6 --PFUZE200 sw1ab,sw2,sw3a,sw3b,swbst,vsnvs,vrefddr,vgen1~vgen6,coin --PFUZE3000 sw1a,sw1b,sw2,sw3,swbst,vsnvs,vrefddr,vldo1,vldo2,vccsd,v33,vldo3,vldo4 --PFUZE3001 sw1,sw2,sw3,vsnvs,vldo1,vldo2,vccsd,v33,vldo3,vldo4 Each regulator is defined using the standard binding for regulators.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/pfuze100.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Robin Gong <yibin.gong@nxp.com>.
- Compatible contract: `fsl,pfuze100`, `fsl,pfuze200`, `fsl,pfuze3000`, `fsl,pfuze3001`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (7): `$nodename`, `compatible`, `reg`, `interrupts`, `fsl,pfuze-support-disable-sw`, `fsl,pmic-stby-poweroff`, `regulators`
- Regulator/vendor integration properties: `fsl,pfuze-support-disable-sw`, `fsl,pmic-stby-poweroff`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `fsl,pfuze100`, `fsl,pfuze200`, `fsl,pfuze3000`, `fsl,pfuze3001`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `fsl,pfuze-support-disable-sw` (ref /schemas/types.yaml#/definitions/flag; Boolean, if present disable all unused switch regulators to save power consumption. Attention, ensure that all important...)
  - `fsl,pmic-stby-poweroff` (ref /schemas/types.yaml#/definitions/flag; if present, configure the PMIC to shutdown all power rails when PMIC_STBY_REQ line is asserted during the power off sequ...)
  - `regulators` (type object; list of regulators provided by this controller.)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/flag`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/pfuze100.yaml`; `/schemas/types.yaml#/definitions/flag`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pfuze100.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pfuze100.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@8 {; compatible = "fsl,pfuze100";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pfuze100.yaml -->
