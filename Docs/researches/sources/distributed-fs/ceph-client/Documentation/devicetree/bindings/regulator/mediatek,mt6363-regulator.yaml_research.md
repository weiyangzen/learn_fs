<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6363-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6363-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6363 PMIC Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6363 SPMI PMIC provides 10 BUCK and 25 LDO (Low DropOut) regulators and can optionally provide overcurrent warnings with one ocp interrupt for each voltage regulator.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6363-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6363-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (19): `compatible`, `reg`, `vsys-vbuck1-supply`, `vsys-vbuck2-supply`, `vsys-vbuck3-supply`, `vsys-vbuck4-supply`, `vsys-vbuck5-supply`, `vsys-vbuck6-supply`, `vsys-vbuck7-supply`, `vsys-vs1-supply`, `vsys-vs2-supply`, `vsys-vs3-supply`, `vs1-ldo1-supply`, `vs1-ldo2-supply`, `vs2-ldo1-supply`, `vs2-ldo2-supply`, `vs3-ldo1-supply`, `vs3-ldo2-supply`, `vsys-ldo1-supply`
- Regulator/vendor integration properties: `vsys-vbuck1-supply`, `vsys-vbuck2-supply`, `vsys-vbuck3-supply`, `vsys-vbuck4-supply`, `vsys-vbuck5-supply`, `vsys-vbuck6-supply`, `vsys-vbuck7-supply`, `vsys-vs1-supply`, `vsys-vs2-supply`, `vsys-vs3-supply`, `vs1-ldo1-supply`, `vs1-ldo2-supply`, `vs2-ldo1-supply`, `vs2-ldo2-supply`, `vs3-ldo1-supply`, `vs3-ldo2-supply`, `vsys-ldo1-supply`
- Property detail signals:
  - `compatible` (const `mediatek,mt6363-regulator`)
  - `reg` (maxItems 1)
  - `vsys-vbuck1-supply` (Input supply for vbuck1)
  - `vsys-vbuck2-supply` (Input supply for vbuck2)
  - `vsys-vbuck3-supply` (Input supply for vbuck3)
  - `vsys-vbuck4-supply` (Input supply for vbuck4)
  - `vsys-vbuck5-supply` (Input supply for vbuck5)
  - `vsys-vbuck6-supply` (Input supply for vbuck6)
  - `vsys-vbuck7-supply` (Input supply for vbuck7)
  - `vsys-vs1-supply` (Input supply for vs1)
  - `vsys-vs2-supply` (Input supply for vs2)
  - `vsys-vs3-supply` (Input supply for vs3)
  - `vs1-ldo1-supply` (Input supply for va15, vio0p75, vm18, vrf18, vrf-io18)
  - `vs1-ldo2-supply` (Input supply for vcn15, vio18, vufs18)
  - `vs2-ldo1-supply` (Input supply for vsram-cpub, vsram-cpum, vrf12, vrf13, vufs12)
  - `vs2-ldo2-supply` (Input supply for va12-1, va12-2, vcn13, vsram-cpul)
  - `vs3-ldo1-supply` (Input supply for vsram-apu, vsram-digrf, vsram-mdfe)
  - `vs3-ldo2-supply` (Input supply for vsram-modem, vrf0p9)
  - ... plus 1 more top-level declared propertie(s).
- Child-node or pattern API:
  - pattern child/property `^v(buck[1-7]|s[1-3])$`
  - pattern child/property `^va(12-1|12-2|15)$`
  - pattern child/property `^v(aux|m|rf-io|tref)18$`
  - pattern child/property `^v(cn13|cn15|emc)$`
  - pattern child/property `^vio(0p75|18)$`
  - pattern child/property `^vrf(0p9|12|13|18)$`
  - pattern child/property `^vsram-(apu|cpub|cpum|cpul|digrf|mdfe|modem)$`
  - pattern child/property `^vufs(12|18)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `#/$defs/ldo-common`
- Textual schema references: `/schemas/regulator/mediatek,mt6363-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6363-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6363-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6363-regulator.yaml -->
