<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6358-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6358-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6358 Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Regulator node of the PMIC. This node should under the PMIC's device node. All voltage regulators provided by the PMIC are described as sub-nodes of this node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6358-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Zhiyong Tao <zhiyong.tao@mediatek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (18): `compatible`, `vsys-ldo1-supply`, `vsys-ldo2-supply`, `vsys-ldo3-supply`, `vsys-vcore-supply`, `vsys-vdram1-supply`, `vsys-vgpu-supply`, `vsys-vmodem-supply`, `vsys-vpa-supply`, `vsys-vproc11-supply`, `vsys-vproc12-supply`, `vsys-vs1-supply`, `vsys-vs2-supply`, `vs1-ldo1-supply`, `vs2-ldo1-supply`, `vs2-ldo2-supply`, `vs2-ldo3-supply`, `vs2-ldo4-supply`
- Regulator/vendor integration properties: `vsys-ldo1-supply`, `vsys-ldo2-supply`, `vsys-ldo3-supply`, `vsys-vcore-supply`, `vsys-vdram1-supply`, `vsys-vgpu-supply`, `vsys-vmodem-supply`, `vsys-vpa-supply`, `vsys-vproc11-supply`, `vsys-vproc12-supply`, `vsys-vs1-supply`, `vsys-vs2-supply`, `vs1-ldo1-supply`, `vs2-ldo1-supply`, `vs2-ldo2-supply`, `vs2-ldo3-supply`, `vs2-ldo4-supply`
- Property detail signals:
  - `compatible`
  - `vsys-ldo1-supply` (Supply for LDOs vfe28, vxo22, vcn28, vaux18, vaud28, vsim1, vusb, vbif28)
  - `vsys-ldo2-supply` (Supply for LDOs vldo28 (MT6358 only), vio28, vmc, vmch, vsim2)
  - `vsys-ldo3-supply` (Supply for LDOs vcn33, vcama[12] (MT6358 only), vemc, vibr)
  - `vsys-vcore-supply` (Supply for buck regulator vcore)
  - `vsys-vdram1-supply` (Supply for buck regulator vdram1)
  - `vsys-vgpu-supply` (Supply for buck regulator vgpu)
  - `vsys-vmodem-supply` (Supply for buck regulator vmodem)
  - `vsys-vpa-supply` (Supply for buck regulator vpa)
  - `vsys-vproc11-supply` (Supply for buck regulator vproc11)
  - `vsys-vproc12-supply` (Supply for buck regulator vproc12)
  - `vsys-vs1-supply` (Supply for buck regulator vs1)
  - `vsys-vs2-supply` (Supply for buck regulator vs2)
  - `vs1-ldo1-supply` (Supply for LDOs vrf18, vefuse, vcn18, vcamio (MT6358 only), vio18, vm18 (MT6366 only))
  - `vs2-ldo1-supply` (Supply for LDOs vdram2, vmddr (MT6366 only))
  - `vs2-ldo2-supply` (Supply for LDOs vrf12, va12)
  - `vs2-ldo3-supply` (Supply for LDOs vsram-core (MT6366 only), vsram-gpu, vsram-others, vsram-proc11, vsram-proc12)
  - `vs2-ldo4-supply` (Supply for LDO vcamd)
- Child-node or pattern API:
  - pattern child/property `^(buck_)?v(core|dram1|gpu|modem|pa|proc1[12]|s[12])$`
  - pattern child/property `^(ldo_)?v(a|rf)12$`
  - pattern child/property `^(ldo_)?v((aux|cn|io|rf)18|camio)$`
  - pattern child/property `^(ldo_)?vxo22$`
  - pattern child/property `^(ldo_)?v(aud|bif|cn|fe|io)28$`
  - pattern child/property `^(ldo_)?vusb$`
  - pattern child/property `^(ldo_)?vsram[_-](core|gpu|others|proc1[12])$`
  - pattern child/property `^(ldo_)?v(cama[12]|camd|cn33|dram2|efuse|emc|ibr|ldo28|m18|mc|mch|mddr|sim[12])$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 2 `if` block(s), 2 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6358-regulator.yaml`
- Header/example integration: `dt-bindings/regulator/mediatek,mt6397-regulator.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6358-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6358-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/regulator/mediatek,mt6397-regulator.h>; regulator {; compatible = "mediatek,mt6358-regulator";; buck_vgpu {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6358-regulator.yaml -->
