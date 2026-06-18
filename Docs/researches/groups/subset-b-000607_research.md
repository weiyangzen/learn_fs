# subset-b-000607 Research

Grouped source research for subset B work item `subset-b-000607`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,da9211.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,da9211.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Dialog Semiconductor DA9211-9215, DA9223-9225 Voltage Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/dlg,da9211.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Ariel D'Alessandro <ariel.dalessandro@collabora.com>.
- Compatible contract: `dlg,da9211`, `dlg,da9212`, `dlg,da9213`, `dlg,da9214`, `dlg,da9215`, `dlg,da9223`, `dlg,da9224`, `dlg,da9225`
- Top-level required properties: `compatible`, `reg`, `interrupts`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `interrupts`, `regulators`
- Top-level declared properties (4): `compatible`, `reg`, `interrupts`, `regulators`
- Property detail signals:
  - `compatible` (enum `dlg,da9211`, `dlg,da9212`, `dlg,da9213`, `dlg,da9214`, `dlg,da9215`, `dlg,da9223`, `dlg,da9224`, `dlg,da9225`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `regulators` (type object; List of regulators provided by the device)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/dlg,da9211.yaml`
- Header/example integration: `dt-bindings/regulator/dlg,da9211-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, interrupts, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,da9211.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,da9211.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/regulator/dlg,da9211-regulator.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/dlg,da9211.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fcs,fan53555.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fcs,fan53555.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Fairchild FAN53555 regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/fcs,fan53555.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Heiko Stuebner <heiko@sntech.de>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (5): `compatible`, `reg`, `fcs,suspend-voltage-selector`, `vin-supply`, `vsel-gpios`
- Regulator/vendor integration properties: `fcs,suspend-voltage-selector`, `vin-supply`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1)
  - `fcs,suspend-voltage-selector` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Declares which of the two available voltage selector registers should be used for the suspend voltage. The other one is ...)
  - `vin-supply` (Supply for the vin pin)
  - `vsel-gpios` (maxItems 1; Voltage Select. When this pin is LOW, VOUT is set by the VSEL0 register. When this pin is HIGH, VOUT is set by the VSEL1...)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/fcs,fan53555.yaml`; `/schemas/types.yaml#/definitions/uint32`

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fcs,fan53555.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fcs,fan53555.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@40 {; compatible = "fcs,fan53555";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fcs,fan53555.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Fixed Voltage regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.yaml, can also be used. However a fixed voltage regulator is expected to have the regulator-min-microvolt and regulator-max-microvolt to be the same.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/fixed-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>.
- Compatible contract: `regulator-fixed`, `regulator-fixed-clock`, `regulator-fixed-domain`
- Top-level required properties: `compatible`, `regulator-name`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`, `clocks`, `power-domains`, `required-opps`, `gpio`, `gpios`
- Top-level declared properties (15): `$nodename`, `compatible`, `regulator-name`, `gpio`, `gpios`, `clocks`, `power-domains`, `required-opps`, `startup-delay-us`, `off-on-delay-us`, `enable-active-high`, `gpio-open-drain`, `vin-supply`, `interrupts`, `system-critical-regulator`
- Regulator/vendor integration properties: `regulator-name`, `gpios`, `startup-delay-us`, `off-on-delay-us`, `vin-supply`, `system-critical-regulator`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `regulator-fixed`, `regulator-fixed-clock`, `regulator-fixed-domain`)
  - `regulator-name` (boolean schema True)
  - `gpio` (maxItems 1; gpio to use for enable control)
  - `gpios` (maxItems 1)
  - `clocks` (maxItems 1; clock to use for enable control. This binding is only available if the compatible is chosen to regulator-fixed-clock. Th...)
  - `power-domains` (maxItems 1; Power domain to use for enable control. This binding is only available if the compatible is chosen to regulator-fixed-do...)
  - `required-opps` (maxItems 1; Performance state to use for enable control. This binding is only available if the compatible is chosen to regulator-fix...)
  - `startup-delay-us` (startup time in microseconds)
  - `off-on-delay-us` (off delay time in microseconds)
  - `enable-active-high` (type boolean; Polarity of GPIO is Active high. If this property is missing, the default assumed is Active low.)
  - `gpio-open-drain` (type boolean; GPIO is open drain type. If this property is missing then default assumption is false.)
  - `vin-supply` (Input supply phandle.)
  - `interrupts` (maxItems 1; Interrupt signaling a critical under-voltage event.)
  - `system-critical-regulator` (boolean schema True)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 2 `if` block(s), 2 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/fixed-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulator-name) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `reg_1v8: regulator-1v8 {; compatible = "regulator-fixed";; regulator-name = "1v8";; regulator-min-microvolt = <1800000>;; regulator-max-microvolt = <1800000>;; gpio = <&gpio1 16 0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: ChromeOS EC controlled voltage regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.yaml, can also be used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/google,cros-ec-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Pi-Hsun Shih <pihsun@chromium.org>.
- Compatible contract: `google,cros-ec-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (3): `compatible`, `reg`, `vin-supply`
- Regulator/vendor integration properties: `vin-supply`
- Property detail signals:
  - `compatible` (const `google,cros-ec-regulator`)
  - `reg` (maxItems 1; Identifier for the voltage regulator to ChromeOS EC.)
  - `vin-supply` (Input supply phandle)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/google,cros-ec-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `spi {; #address-cells = <1>;; #size-cells = <0>;; cros_ec: ec@0 {; compatible = "google,cros-ec-spi";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: GPIO controlled regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.txt, can also be used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/gpio-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>.
- Compatible contract: `regulator-gpio`
- Top-level required properties: `compatible`, `regulator-name`, `gpios`, `states`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`, `gpios`, `states`
- Top-level declared properties (11): `compatible`, `regulator-name`, `enable-gpios`, `gpios`, `gpios-states`, `states`, `startup-delay-us`, `enable-active-high`, `gpio-open-drain`, `regulator-type`, `vin-supply`
- Regulator/vendor integration properties: `regulator-name`, `enable-gpios`, `gpios`, `states`, `startup-delay-us`, `regulator-type`, `vin-supply`
- Property detail signals:
  - `compatible` (const `regulator-gpio`)
  - `regulator-name` (boolean schema True)
  - `enable-gpios` (maxItems 1; GPIO to use to enable/disable the regulator. Warning, the GPIO phandle flags are ignored and the GPIO polarity is contro...)
  - `gpios` (minItems 1; maxItems 8; Array of one or more GPIO pins used to select the regulator voltage/current listed in "states".)
  - `gpios-states` (ref /schemas/types.yaml#/definitions/uint32-array; items enum 2 values; minItems 1; maxItems 8)
  - `states` (ref /schemas/types.yaml#/definitions/uint32-matrix; minItems 2; maxItems 256; Selection of available voltages/currents provided by this regulator and matching GPIO configurations to achieve them. If...)
  - `startup-delay-us` (startup time in microseconds)
  - `enable-active-high` (type boolean; Polarity of "enable-gpio" GPIO is active HIGH. Default is active LOW.)
  - `gpio-open-drain` (type boolean; GPIO is open drain type. If this property is missing then default assumption is false.)
  - `regulator-type` (ref /schemas/types.yaml#/definitions/string; enum `voltage`, `current`; default voltage; Specifies what is being regulated.)
  - `vin-supply` (Input supply phandle.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`; `/schemas/types.yaml#/definitions/string`
- Textual schema references: `/schemas/regulator/gpio-regulator.yaml`; `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulator-name, gpios, states) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `gpio-regulator {; compatible = "regulator-gpio";; regulator-name = "mmci-gpio-supply";; regulator-min-microvolt = <1800000>;; regulator-max-microvolt = <2600000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/infineon,ir38060.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/infineon,ir38060.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Infineon Buck Regulators with PMBUS interfaces. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/infineon,ir38060.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Guenter Roeck <linux@roeck-us.net>.
- Compatible contract: `infineon,ir38060`, `infineon,ir38064`, `infineon,ir38164`, `infineon,ir38263`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible` (enum `infineon,ir38060`, `infineon,ir38064`, `infineon,ir38164`, `infineon,ir38263`)
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/infineon,ir38060.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/infineon,ir38060.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/infineon,ir38060.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@34 {; compatible = "infineon,ir38060";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/infineon,ir38060.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/lltc,ltc3676.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/lltc,ltc3676.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Linear Technology LTC3676 8-output regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: LTC3676 contains eight regulators, 4 switching SW1..SW4 and four LDO1..4 .

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/lltc,ltc3676.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Tim Harvey <tharvey@gateworks.com>.
- Compatible contract: `lltc,ltc3676`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`, `lltc,fb-voltage-divider`, `regulator-always-on`
- Top-level declared properties (4): `compatible`, `reg`, `interrupts`, `regulators`
- Property detail signals:
  - `compatible` (const `lltc,ltc3676`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `regulators` (type object; List of regulators provided by this controller, must be named after their hardware counterparts (SW|LDO)[1-4].)
- Child-node or pattern API:
  - `regulators` child object with properties ldo1, ldo3

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-array`
- Textual schema references: `/schemas/regulator/lltc,ltc3676.yaml`; `/schemas/types.yaml#/definitions/uint32-array`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/lltc,ltc3676.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/lltc,ltc3676.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@3c {; compatible = "lltc,ltc3676";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/lltc,ltc3676.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max77650-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max77650-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Regulator driver for MAX77650 PMIC from Maxim Integrated.. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This module is part of the MAX77650 MFD device. For more details see Documentation/devicetree/bindings/mfd/max77650.yaml. The regulator controller is represented as a sub-node of the PMIC node on the device tree. The device has a single LDO regulator and a SIMO buck-boost regulator with three independent power rails.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/max77650-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bartosz Golaszewski <bgolaszewski@baylibre.com>.
- Compatible contract: `maxim,max77650-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (const `maxim,max77650-regulator`)
- Child-node or pattern API:
  - pattern child/property `^regulator-(ldo|sbb[0-2])$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/max77650-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max77650-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max77650-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max77650-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8660.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8660.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8660 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/max8660.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Daniel Mack <zonque@gmail.com>.
- Compatible contract: `maxim,max8660`, `maxim,max8661`
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `maxim,max8660`, `maxim,max8661`)
  - `reg` (maxItems 1)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/max8660.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8660.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8660.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@34 {; compatible = "maxim,max8660";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8660.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8893.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8893.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Regulator driver for MAX8893 PMIC from Maxim Integrated.. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The device has 5 LDO regulators and a single BUCK regulator. Programming is done through I2C bus.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/max8893.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Sergey Larin <cerg2010cerg2010@mail.ru>.
- Compatible contract: `maxim,max8893`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (3): `compatible`, `reg`, `regulators`
- Property detail signals:
  - `compatible` (const `maxim,max8893`)
  - `reg` (maxItems 1)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/max8893.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8893.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8893.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@3e {; compatible = "maxim,max8893";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/max8893.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max14577.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max14577.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX14577/MAX77836 MicroUSB and Companion Power Management IC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This is a part of device tree bindings for Maxim MAX14577/MAX77836 MicroUSB Integrated Circuit (MUIC). See also Documentation/devicetree/bindings/mfd/maxim,max14577.yaml for additional information and example.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max14577.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max14577-regulator`, `maxim,max77836-regulator`
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (3): `compatible`, `CHARGER`, `SAFEOUT`
- Property detail signals:
  - `compatible` (enum `maxim,max14577-regulator`, `maxim,max77836-regulator`)
  - `CHARGER` (ref regulator.yaml#; type object; Current regulator.)
  - `SAFEOUT` (ref regulator.yaml#; type object; Safeout LDO regulator (fixed voltage).)
- Child-node or pattern API:
  - `CHARGER` child object with properties regulator-min-microvolt, regulator-max-microvolt
  - `SAFEOUT` child object with properties regulator-min-microamp, regulator-max-microamp, regulator-min-microvolt, regulator-max-microvolt
  - pattern child/property `^LDO[12]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 1 `if` block(s), 1 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max14577.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max14577.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max14577.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max14577.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20411.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20411.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim Integrated MAX20411 Step-Down DC-DC Converter. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MAX20411 is a high-efficiency, DC-DC step-down converter. It provides configurable output voltage in the range of 0.5V to 1.275V, configurable over I2C.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max20411.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bjorn Andersson <andersson@kernel.org>.
- Compatible contract: `maxim,max20411`
- Top-level required properties: `compatible`, `reg`, `enable-gpios`
- Required keys across top-level and child schemas: `compatible`, `reg`, `enable-gpios`
- Top-level declared properties (4): `compatible`, `reg`, `enable-gpios`, `vdd-supply`
- Regulator/vendor integration properties: `enable-gpios`, `vdd-supply`
- Property detail signals:
  - `compatible` (const `maxim,max20411`)
  - `reg` (maxItems 1)
  - `enable-gpios` (GPIO connected to the EN pin, active high)
  - `vdd-supply` (Input supply for the device (VDD pin, 3.0V to 5.5V))
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max20411.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, enable-gpios) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20411.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20411.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max20411.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77620-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77620-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Regulator for MAX77620 Power management IC from Maxim Semiconductor.. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Device has multiple DCDC(sd[0-3]) and LDOs(ldo[0-8]). The input supply of these regulators are defined under parent device node. Details of regulator properties are defined as child node under sub-node "regulators" which is child node of device node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77620-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Svyatoslav Ryhel <clamor95@gmail.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^in-(sd[0-3]|ldo(0-1|2|3-5|4-6|7-8))-supply$`
  - pattern child/property `^(sd[0-3]|ldo[0-8])$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle`; `/schemas/regulator/regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/maxim,max77620-regulator.yaml`; `/schemas/regulator/regulator.yaml`; `/schemas/types.yaml#/definitions/phandle`; `/schemas/types.yaml#/definitions/uint32`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77620-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77620-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77620-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77686.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77686.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX77686 Power Management IC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This is a part of device tree bindings for Maxim MAX77686 Power Management Integrated Circuit (PMIC). The Maxim MAX77686 provides high-efficiency Buck and 26 Low-DropOut (LDO) regulators. See also Documentation/devicetree/bindings/mfd/maxim,max77686.yaml for additional information and example.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77686.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Chanwoo Choi <cw00.choi@samsung.com>, Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^LDO([1-9]|1[0-9]|2[3-6])$`
  - pattern child/property `^LDO2[0-2]$`
  - pattern child/property `^BUCK[1-7]$`
  - pattern child/property `^BUCK[89]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77686.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77686.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77686.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77686.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77693.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77693.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX77693 MicroUSB and Companion Power Management IC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This is a part of device tree bindings for Maxim MAX77693 MicroUSB Integrated Circuit (MUIC). See also Documentation/devicetree/bindings/mfd/maxim,max77693.yaml for additional information and example.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77693.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Chanwoo Choi <cw00.choi@samsung.com>, Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`
- Top-level declared properties (1): `CHARGER`
- Property detail signals:
  - `CHARGER` (ref regulator.yaml#; type object; Current regulator.)
- Child-node or pattern API:
  - `CHARGER` child object requiring regulator-name with properties regulator-name, regulator-always-on, regulator-boot-on, regulator-min-microamp, regulator-max-microamp
  - pattern child/property `^ESAFEOUT[12]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77693.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77693.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77693.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77693.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77802.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77802.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX77802 Power Management IC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This is a part of device tree bindings for Maxim MAX77802 Power Management Integrated Circuit (PMIC). The Maxim MAX77686 provides 10 high-efficiency Buck and 32 Low-DropOut (LDO) regulators. See also Documentation/devicetree/bindings/mfd/maxim,max77802.yaml for additional information and example. Certain regulators support "regulator-initial-mode" and "regulator-mode". The valid modes list is defined in the dt-bindings/regulator/maxim,max77802.h and their meaning is:: 1 - Normal regulator voltage output mode. 3 - Low Power which reduces the quiescent current down to only 1uA The standard "regulator-mode" property can only be used for regulators that support changing their mode to Low Power M...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77802.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Javier Martinez Canillas <javier@dowhile0.org>, Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^LDO([13]|2[01])$`
  - pattern child/property `^LDO([24-9]|1[0-5789]|2[3-9]|3[02345])$`
  - pattern child/property `^BUCK[2-4]$`
  - pattern child/property `^BUCK([15-9]|10)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77802.yaml`
- Header/example integration: `dt-bindings/regulator/maxim,max77802.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77802.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77802.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77802.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77826.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77826.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim Integrated MAX77826 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77826.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Iskren Chernev <iskren.chernev@gmail.com>.
- Compatible contract: `maxim,max77826`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `maxim,max77826`)
  - `reg` (maxItems 1)
  - `regulators` (ref regulator.yaml#; type object; list of regulators provided by this controller, must be named after their hardware counterparts LDO[1-15], BUCK and BUCK...)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77826.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77826.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77826.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@69 {; compatible = "maxim,max77826";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77826.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77838.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77838.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim Integrated MAX77838 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77838.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Ivaylo Ivanov <ivo.ivanov.ivanov1@gmail.com>.
- Compatible contract: `maxim,max77838`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `maxim,max77838`)
  - `reg` (maxItems 1)
  - `regulators` (ref regulator.yaml#; type object; list of regulators provided by this controller, must be named after their hardware counterparts ldo[1-4] and buck)
- Child-node or pattern API:
  - `regulators` child object with properties buck

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77838.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77838.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77838.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@60 {; compatible = "maxim,max77838";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77838.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77843.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77843.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX77843 MicroUSB and Companion Power Management IC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This is a part of device tree bindings for Maxim MAX77843 MicroUSB Integrated Circuit (MUIC). See also Documentation/devicetree/bindings/mfd/maxim,max77843.yaml for additional information and example.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max77843.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max77843-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`
- Top-level declared properties (2): `compatible`, `CHARGER`
- Property detail signals:
  - `compatible` (const `maxim,max77843-regulator`)
  - `CHARGER` (ref regulator.yaml#; type object; Current regulator.)
- Child-node or pattern API:
  - `CHARGER` child object requiring regulator-name with properties regulator-name, regulator-always-on, regulator-boot-on, regulator-min-microamp, regulator-max-microamp
  - pattern child/property `^SAFEOUT[12]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max77843.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77843.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77843.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max77843.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8973/MAX77621 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max8973.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max8973`, `maxim,max77621`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (15): `compatible`, `junction-warn-millicelsius`, `maxim,dvs-gpio`, `maxim,dvs-default-state`, `maxim,externally-enable`, `maxim,enable-gpio`, `maxim,enable-remote-sense`, `maxim,enable-falling-slew-rate`, `maxim,enable-active-discharge`, `maxim,enable-frequency-shift`, `maxim,enable-bias-control`, `maxim,enable-etr`, `maxim,enable-high-etr-sensitivity`, `reg`, `interrupts`
- Regulator/vendor integration properties: `maxim,dvs-gpio`, `maxim,dvs-default-state`, `maxim,externally-enable`, `maxim,enable-gpio`, `maxim,enable-remote-sense`, `maxim,enable-falling-slew-rate`, `maxim,enable-active-discharge`, `maxim,enable-frequency-shift`, `maxim,enable-bias-control`, `maxim,enable-etr`, `maxim,enable-high-etr-sensitivity`
- Property detail signals:
  - `compatible` (enum `maxim,max8973`, `maxim,max77621`)
  - `junction-warn-millicelsius` (Junction warning temperature threshold in millicelsius. If die temperature crosses this level then device generates the ...)
  - `maxim,dvs-gpio` (maxItems 1; GPIO which is connected to DVS pin of device.)
  - `maxim,dvs-default-state` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Default state of GPIO during initialisation. 1 for HIGH and 0 for LOW.)
  - `maxim,externally-enable` (type boolean; Externally control the regulator output enable/disable.)
  - `maxim,enable-gpio` (maxItems 1; GPIO for enable control. If the valid GPIO is provided then externally enable control will be considered.)
  - `maxim,enable-remote-sense` (type boolean; Enable remote sense.)
  - `maxim,enable-falling-slew-rate` (type boolean; Enable falling slew rate.)
  - `maxim,enable-active-discharge` (type boolean; Eable active discharge.)
  - `maxim,enable-frequency-shift` (type boolean; Enable 9% frequency shift.)
  - `maxim,enable-bias-control` (type boolean; Enable bias control which can reduce the startup delay to 20us from 220us.)
  - `maxim,enable-etr` (type boolean; Enable Enhanced Transient Response.)
  - `maxim,enable-high-etr-sensitivity` (type boolean; Enhanced transient response circuit is enabled and set for high sensitivity. If this property is available then etr will...)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/maxim,max8973.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@1b {; compatible = "maxim,max8973";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8997 Power Management IC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Maxim MAX8997 is a Power Management IC which includes voltage and current regulators, charger controller with fuel gauge, RTC, clock outputs, haptic motor driver, flash LED driver and Micro-USB Interface Controller. The binding here is not complete and describes only regulator and charger controller parts.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max8997.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max8997-pmic`
- Top-level required properties: `compatible`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `reg`, `regulators`, `regulator-name`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`
- Top-level declared properties (14): `compatible`, `charger-supply`, `interrupts`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck125-dvs-gpios`, `max8997,pmic-ignore-gpiodvs-side-effect`, `reg`, `regulators`
- Regulator/vendor integration properties: `charger-supply`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck125-dvs-gpios`, `max8997,pmic-ignore-gpiodvs-side-effect`
- Property detail signals:
  - `compatible` (const `maxim,max8997-pmic`)
  - `charger-supply` (Regulator node for charging current.)
  - `interrupts` (2 fixed item schema(s))
  - `max8997,pmic-buck1-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck1 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck2-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck2 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck5-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck5 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck1-uses-gpio-dvs` (type boolean; buck1 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck2-uses-gpio-dvs` (type boolean; buck2 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck5-uses-gpio-dvs` (type boolean; buck5 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck125-default-dvs-idx` (ref /schemas/types.yaml#/definitions/uint32; minimum 0; maximum 7; default 0)
  - `max8997,pmic-buck125-dvs-gpios` (minItems 3; maxItems 3; GPIO specifiers for three host gpio's used for DVS.)
  - `max8997,pmic-ignore-gpiodvs-side-effect` (type boolean; When GPIO-DVS mode is used for multiple bucks, changing the voltage value of one of the bucks may affect that of another...)
  - `reg` (maxItems 1)
  - `regulators` (type object; List of child nodes that specify the regulators.)
- Child-node or pattern API:
  - `regulators` child object with properties CHARGER, CHARGER_CV, CHARGER_TOPOFF, ENVICHG, ESAFEOUT1, ESAFEOUT2

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 1 `if` block(s), 1 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max8997.yaml`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`
- Header/example integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, max8997,pmic-buck1-dvs-voltage, max8997,pmic-buck2-dvs-voltage, max8997,pmic-buck5-dvs-voltage, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; #include <dt-bindings/interrupt-controller/irq.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316b-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316b-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6316 BP/VP SPMI PMIC Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MediaTek MT6316BP/VP PMICs are fully controlled by SPMI interface, both feature four step-down DC/DC (buck) converters, and provides 2+2 Phases, joining Buck 1+2 for the first phase, and Buck 3+4 for the second phase.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6316b-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6316b-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible` (const `mediatek,mt6316b-regulator`)
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - pattern child/property `^vbuck(12|34)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6316b-regulator.yaml`
- Header/example integration: `dt-bindings/spmi/spmi.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316b-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316b-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/spmi/spmi.h>; spmi {; #address-cells = <2>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316b-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316c-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316c-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6316 CP/HP/KP SPMI PMIC Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MediaTek MT6316CP/HP/KP PMICs are fully controlled by SPMI interface, features four step-down DC/DC (buck) converters, and provides 3+1 Phases, joining Buck 1+2+4 for the first phase, and uses Buck 3 for the second.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6316c-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6316c-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible` (const `mediatek,mt6316c-regulator`)
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - pattern child/property `^vbuck(124|3)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6316c-regulator.yaml`
- Header/example integration: `dt-bindings/spmi/spmi.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316c-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316c-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/spmi/spmi.h>; spmi {; #address-cells = <2>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316c-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316d-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316d-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6316 DP/TP SPMI PMIC Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MediaTek MT6316DP/TP PMICs are fully controlled by SPMI interface, both feature four step-down DC/DC (buck) converters, and provides a single Phase, joining Buck 1+2+3+4.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6316d-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6316d-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (3): `compatible`, `reg`, `vbuck1234`
- Property detail signals:
  - `compatible` (const `mediatek,mt6316d-regulator`)
  - `reg` (maxItems 1)
  - `vbuck1234` (ref regulator.yaml#; type object)
- Child-node or pattern API:
  - `vbuck1234` child object with properties regulator-allowed-modes

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6316d-regulator.yaml`
- Header/example integration: `dt-bindings/spmi/spmi.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316d-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316d-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/spmi/spmi.h>; spmi {; #address-cells = <2>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6316d-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6331-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6331-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MT6331 Regulator from MediaTek Integrated. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6331 PMIC provides 6 BUCK and 21 LDO (Low Dropout) regulators and nodes are named according to the regulator type: buck-<name> and ldo-<name>. MT6331 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6331-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6331-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (const `mediatek,mt6331-regulator`)
- Child-node or pattern API:
  - pattern child/property `^buck-v(core2|io18|dvfs11|dvfs12|dvfs13|dvfs14)$`
  - pattern child/property `^ldo-(avdd32aud|vauxa32)$`
  - pattern child/property `^ldo-v(dig18|emc33|ibr|io28|mc|mch|mipi|rtc|sim1|sim2|sram|usb10)$`
  - pattern child/property `^ldo-vcam(a|af|d|io)$`
  - pattern child/property `^ldo-vtcxo[12]$`
  - pattern child/property `^ldo-vgp[1234]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6331-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6331-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6331-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6331_vdvfs11_reg: buck-vdvfs11 {; regulator-name = "vdvfs11";; regulator-min-microvolt = <700000>;; regulator-max-microvolt = <1493750>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6331-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6332-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6332-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MT6332 Regulator from MediaTek Integrated. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6332 Companion PMIC provides 6 BUCK and 4 LDO (Low Dropout) regulators and nodes are named according to the regulator type: buck-<name> and ldo-<name>. MT6332 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6332-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6332-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (const `mediatek,mt6332-regulator`)
- Child-node or pattern API:
  - pattern child/property `^buck-v(dram|dvfs2|pa|rf18a|rf18b|sbst)$`
  - pattern child/property `^ldo-v(bif28|dig18|sram|usb33)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6332-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6332-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6332-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6332_vdram_reg: buck-vdram {; regulator-name = "vdram";; regulator-min-microvolt = <700000>;; regulator-max-microvolt = <1493750>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6332-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6357 Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6357 PMIC provides 5 BUCK and 29 LDO. Regulators and nodes are named according to the regulator type: - buck-<name> - ldo-<name>. MT6357 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6357-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Chen Zhong <chen.zhong@mediatek.com>, Fabien Parent <fabien.parent@linaro.org>, Alexandre Mergnat <amergnat@baylibre.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`, `regulator-min-microvolt`, `regulator-max-microvolt`
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^buck-v(core|modem|pa|proc|s1)$`
  - pattern child/property `^ldo-v(camio18|aud28|aux18|io18|io28|rf12|rf18|cn18|cn28|fe28)$`
  - pattern child/property `^ldo-v(efuse|ibr|ldo28|mch|cama|camd|cn33-bt|cn33-wifi)$`
  - pattern child/property `^ldo-v(xo22|emc|mc|sim1|sim2|sram-others|sram-proc|dram|usb33)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6357-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6357_vproc_reg: buck-vproc {; regulator-name = "vproc";; regulator-min-microvolt = <518750>;; regulator-max-microvolt = <1312500>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6397-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6397-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6397 Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Regulator node of the PMIC. This node should under the PMIC's device node. All voltage regulators provided by the PMIC are described as sub-nodes of this node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6397-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Sen Chu <sen.chu@mediatek.com>, Macpaul Lin <macpaul.lin@mediatek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (1 fixed item schema(s))
- Child-node or pattern API:
  - pattern child/property `^(buck_)?v(core|drm|gpu|io18|pca(7|15)|sramca(7|15))$`
  - pattern child/property `^(ldo_)?v(tcxo|(a|io)28)$`
  - pattern child/property `^(ldo_)?vusb$`
  - pattern child/property `^(ldo_)?v(cama|emc3v3|gp[123456]|ibr|mc|mch)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6397-regulator.yaml`
- Header/example integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/regulator/mediatek,mt6397-regulator.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6397-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6397-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/interrupt-controller/arm-gic.h>; mt6397_regulators: regulators {; compatible = "mediatek,mt6397-regulator";; mt6397_vpca15_reg: buck_vpca15 {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6397-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek DVFSRC-controlled Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Dynamic Voltage and Frequency Scaling Resource Collector Regulators are controlled with votes to the DVFSRC hardware.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6873-dvfsrc-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6873-dvfsrc-regulator`, `mediatek,mt6893-dvfsrc-regulator`, `mediatek,mt8183-dvfsrc-regulator`, `mediatek,mt8192-dvfsrc-regulator`, `mediatek,mt8195-dvfsrc-regulator`, `mediatek,mt8196-dvfsrc-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `dvfsrc-vcore`, `dvfsrc-vscp`
- Top-level declared properties (3): `compatible`, `dvfsrc-vcore`, `dvfsrc-vscp`
- Property detail signals:
  - `compatible` (enum `mediatek,mt6873-dvfsrc-regulator`, `mediatek,mt6893-dvfsrc-regulator`, `mediatek,mt8183-dvfsrc-regulator`, `mediatek,mt8192-dvfsrc-regulator`, `mediatek,mt8195-dvfsrc-regulator`, `mediatek,mt8196-dvfsrc-regulator`)
  - `dvfsrc-vcore` (ref regulator.yaml#; DVFSRC-controlled SoC Vcore regulator)
  - `dvfsrc-vscp` (ref regulator.yaml#; DVFSRC-controlled System Control Processor regulator)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6873-dvfsrc-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MCP16502 - High-Performance PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MCP16502 is an optimally integrated PMIC compatible with Microchip's eMPUs(Embedded Microprocessor Units), requiring Dynamic Voltage Scaling (DVS) with the use of High-Performance mode (HPM).

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/microchip,mcp16502.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Andrei Simion <andrei.simion@microchip.com>.
- Compatible contract: `microchip,mcp16502`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (9): `compatible`, `lpm-gpios`, `reg`, `lvin-supply`, `pvin1-supply`, `pvin2-supply`, `pvin3-supply`, `pvin4-supply`, `regulators`
- Regulator/vendor integration properties: `lvin-supply`, `pvin1-supply`, `pvin2-supply`, `pvin3-supply`, `pvin4-supply`
- Property detail signals:
  - `compatible` (const `microchip,mcp16502`)
  - `lpm-gpios` (maxItems 1; GPIO for LPM pin. Note that this GPIO must remain high during suspend-to-ram, keeping the PMIC into HIBERNATE mode.)
  - `reg` (maxItems 1)
  - `lvin-supply` (Input supply phandle for LDO1 and LDO2)
  - `pvin1-supply` (Input supply phandle for VDD_IO (BUCK1))
  - `pvin2-supply` (Input supply phandle for VDD_DDR (BUCK2))
  - `pvin3-supply` (Input supply phandle for VDD_CORE (BUCK3))
  - `pvin4-supply` (Input supply phandle for VDD_OTHER (BUCK4))
  - `regulators` (type object; List of regulators and its properties.)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/microchip,mcp16502.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@5b {; compatible = "microchip,mcp16502";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/motorola,cpcap-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/motorola,cpcap-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Motorola CPCAP PMIC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This module is part of the Motorola CPCAP MFD device. For more details see Documentation/devicetree/bindings/mfd/motorola,cpcap.yaml. The regulator controller is represented as a sub-node of the PMIC node on the device tree.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/motorola,cpcap-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Svyatoslav Ryhel <clamor95@gmail.com>.
- Compatible contract: `motorola,cpcap-regulator`, `motorola,mapphone-cpcap-regulator`, `motorola,mot-cpcap-regulator`, `motorola,xoom-cpcap-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`, `regulator-enable-ramp-delay`, `regulator-min-microvolt`, `regulator-max-microvolt`
- Top-level declared properties (2): `compatible`, `regulators`
- Property detail signals:
  - `compatible` (enum `motorola,cpcap-regulator`, `motorola,mapphone-cpcap-regulator`, `motorola,mot-cpcap-regulator`, `motorola,xoom-cpcap-regulator`)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/regulator/regulator.yaml#`
- Textual schema references: `/schemas/regulator/motorola,cpcap-regulator.yaml`; `/schemas/regulator/regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/motorola,cpcap-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/motorola,cpcap-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/motorola,cpcap-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp5416.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp5416.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power System MP5416 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mp5416.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Saravanan Sekar <sravanhome@gmail.com>.
- Compatible contract: `mps,mp5416`, `mps,mp5496`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `mps,mp5416`, `mps,mp5496`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller, must be named after their hardware counterparts BUCK[1-4] and LDO[1-4])
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mp5416.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp5416.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp5416.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@69 {; compatible = "mps,mp5416";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp5416.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp8859.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp8859.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power Systems MP8859 Voltage Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MP8859 is a synchronous, 4-switch, integrated buck-boost converter capable of regulating the output voltage from 2.8V to 22V wide input voltage range with high efficiency.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mp8859.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Markus Reichl <reichl@t-online.de>.
- Compatible contract: `mps,mp8859`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (3): `compatible`, `reg`, `mp8859_dcdc`
- Property detail signals:
  - `compatible` (const `mps,mp8859`)
  - `reg` (maxItems 1)
  - `mp8859_dcdc` (ref /schemas/regulator/regulator.yaml#; type object; DCDC regulator subnode)
- Child-node or pattern API:
  - `mp8859_dcdc` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/regulator/regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mp8859.yaml`; `/schemas/regulator/regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp8859.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp8859.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@66 {; compatible = "mps,mp8859";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp8859.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power Systems MP8867/MP8869 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mp886x.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Jisheng Zhang <jszhang@kernel.org>.
- Compatible contract: `mps,mp8867`, `mps,mp8869`
- Top-level required properties: `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`
- Required keys across top-level and child schemas: `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`
- Top-level declared properties (5): `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`, `mps,switch-frequency-hz`
- Regulator/vendor integration properties: `enable-gpios`, `mps,fb-voltage-divider`, `mps,switch-frequency-hz`
- Property detail signals:
  - `compatible` (enum `mps,mp8867`, `mps,mp8869`)
  - `reg` (maxItems 1)
  - `enable-gpios` (maxItems 1; GPIO to enable/disable the regulator.)
  - `mps,fb-voltage-divider` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems 2; An array of two integers containing the resistor values R1 and R2 of the feedback voltage divider in kilo ohms.)
  - `mps,switch-frequency-hz` (enum `500000`, `750000`, `1000000`, `1250000`, `1500000`; The valid switch frequency in Hertz.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-array`
- Textual schema references: `/schemas/regulator/mps,mp886x.yaml`; `/schemas/types.yaml#/definitions/uint32-array`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, enable-gpios, mps,fb-voltage-divider) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@62 {; compatible = "mps,mp8869";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq2286.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq2286.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power System MPQ2286 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mpq2286.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Saravanan Sekar <saravanan@linumiz.com>.
- Compatible contract: `mps,mpq2286`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (3): `compatible`, `reg`, `regulators`
- Property detail signals:
  - `compatible` (enum `mps,mpq2286`)
  - `reg` (maxItems 1)
  - `regulators` (type object)
- Child-node or pattern API:
  - `regulators` child object with properties buck

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mpq2286.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq2286.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq2286.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@3 {; compatible = "mps,mpq2286";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq2286.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power System MPQ7920 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mpq7920.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Saravanan Sekar <sravanhome@gmail.com>.
- Compatible contract: `mps,mpq7920`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `mps,mpq7920`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller, must be named after their hardware counterparts BUCK[1-4], one LDORTC, a...)
- Child-node or pattern API:
  - `regulators` child object with properties mps,switch-freq, ldortc

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint8`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mpq7920.yaml`; `/schemas/types.yaml#/definitions/uint8`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@69 {; compatible = "mps,mpq7920";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7932.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7932.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power System MPQ7932 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mpq7932.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Saravanan Sekar <saravanan@linumiz.com>.
- Compatible contract: `mps,mpq7932`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (3): `compatible`, `reg`, `regulators`
- Property detail signals:
  - `compatible` (enum `mps,mpq7932`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller, must be named after their hardware counterparts BUCK[1-6])
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mpq7932.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7932.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7932.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@3 {; compatible = "mps,mpq7932";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7932.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6315-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6315-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Mediatek MT6315 Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6315 is a power management IC (PMIC) configurable with SPMI. that contains 4 BUCKs output which can combine with each other by different efuse settings.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mt6315-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Hsin-Hsiung Wang <hsin-hsiung.wang@mediatek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (7): `compatible`, `reg`, `pvdd1-supply`, `pvdd2-supply`, `pvdd3-supply`, `pvdd4-supply`, `regulators`
- Regulator/vendor integration properties: `pvdd1-supply`, `pvdd2-supply`, `pvdd3-supply`, `pvdd4-supply`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1)
  - `pvdd1-supply` (Supply for regulator vbuck1)
  - `pvdd2-supply` (Supply for regulator vbuck2)
  - `pvdd3-supply` (Supply for regulator vbuck3)
  - `pvdd4-supply` (Supply for regulator vbuck4)
  - `regulators` (type object; List of regulators and its properties)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mt6315-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6315-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6315-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic@6 {; compatible = "mediatek,mt6315-regulator";; reg = <0x6 0>;; pvdd1-supply = <&pp4200_z2>;; pvdd3-supply = <&pp4200_z2>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6315-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MT6359 Regulator from MediaTek Integrated. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: List of regulators provided by this controller. It is named according to its regulator type, buck_<name> and ldo_<name>. MT6359 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mt6359-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Hsin-Hsiung Wang <hsin-hsiung.wang@mediatek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^buck_v(s1|gpu11|modem|pu|core|s2|pa|proc2|proc1|core_sshub)$`
  - pattern child/property `^ldo_v(ibr|rf12|usb|camio|efuse|xo22)$`
  - pattern child/property `^ldo_v(rfck|emc|a12|a09|ufs|bbck)$`
  - pattern child/property `^ldo_vcn(18|13|33_1_bt|13_1_wifi|33_2_bt|33_2_wifi)$`
  - pattern child/property `^ldo_vsram_(proc2|others|md|proc1|others_sshub)$`
  - pattern child/property `^ldo_v(fe|bif|io)28$`
  - pattern child/property `^ldo_v(aud|io|aux|rf|m)18$`
  - pattern child/property `^ldo_vsim[12]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mt6359-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6359_vs1_buck_reg: buck_vs1 {; regulator-name = "vs1";; regulator-min-microvolt = <800000>;; regulator-max-microvolt = <2200000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6360-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6360-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MT6360 Regulator from MediaTek Integrated. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: list of regulators provided by this controller, must be named after their hardware counterparts buck1/2 or ldo1/2/3/5/6/7

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mt6360-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Gene Chen <gene_chen@richtek.com>.
- Compatible contract: `mediatek,mt6360-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (4): `compatible`, `LDO_VIN1-supply`, `LDO_VIN2-supply`, `LDO_VIN3-supply`
- Regulator/vendor integration properties: `LDO_VIN1-supply`, `LDO_VIN2-supply`, `LDO_VIN3-supply`
- Property detail signals:
  - `compatible` (const `mediatek,mt6360-regulator`)
  - `LDO_VIN1-supply` (Input supply phandle(s) for LDO1/2/3)
  - `LDO_VIN2-supply` (Input supply phandle(s) for LDO5)
  - `LDO_VIN3-supply` (Input supply phandle(s) for LDO6/7)
- Child-node or pattern API:
  - pattern child/property `^buck[12]$`
  - pattern child/property `^ldo[123567]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mt6360-regulator.yaml`
- Header/example integration: `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/regulator/mediatek,mt6360-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6360-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6360-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/regulator/mediatek,mt6360-regulator.h>; regulator {; compatible = "mediatek,mt6360-regulator";; LDO_VIN3-supply = <&BUCK2>;; buck1 {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6360-regulator.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf0900.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf0900.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: NXP PF0900 Power Management Integrated Circuit regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The PF0900 is a power management integrated circuit (PMIC) optimized for high performance i.MX9x based applications. It features five high efficiency buck converters, three linear and one vaon regulators. It provides low quiescent current in Standby and low power off Modes.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/nxp,pf0900.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Joy Zou <joy.zou@nxp.com>.
- Compatible contract: `nxp,pf0900`
- Top-level required properties: `compatible`, `reg`, `interrupts`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `interrupts`, `regulators`
- Top-level declared properties (5): `compatible`, `reg`, `interrupts`, `regulators`, `nxp,i2c-crc-enable`
- Regulator/vendor integration properties: `nxp,i2c-crc-enable`
- Property detail signals:
  - `compatible` (enum `nxp,pf0900`)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
  - `regulators` (type object)
  - `nxp,i2c-crc-enable` (type boolean; The CRC enabled during register read/write. Controlled by customer unviewable fuse bits OTP_I2C_CRC_EN. Check chip part ...)
- Child-node or pattern API:
  - `regulators` child object with properties vaon

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/nxp,pf0900.yaml`
- Header/example integration: `dt-bindings/interrupt-controller/irq.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, interrupts, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf0900.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf0900.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/interrupt-controller/irq.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf0900.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf5300.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf5300.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: NXP PF5300/PF5301/PF5302 PMIC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The PF5300, PF5301, and PF5302 integrate high-performance buck converters, 12 A, 8 A, and 15 A, respectively, to power high-end automotive and industrial processors. With adaptive voltage positioning and a high-bandwidth loop, they offer transient regulation to minimize capacitor requirements.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/nxp,pf5300.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Woodrow Douglass <wdouglass@carnegierobotics.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/nxp,pf5300.yaml`

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf5300.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf5300.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@28 {; compatible = "nxp,pf5302", "nxp,pf5300";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf5300.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: NXP PF8100/PF8121A/PF8200 PMIC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: PF8100/PF8121A/PF8200 is a PMIC designed for highperformance consumer applications. It features seven high efficiency buck converters, four linear and one vsnvs regulators. It has built-in one time programmable fuse bank for device configurations.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/nxp,pf8x00-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Jagan Teki <jagan@amarulasolutions.com>, Troy Kisky <troy.kisky@boundarydevices.com>.
- Compatible contract: `nxp,pf8100`, `nxp,pf8121a`, `nxp,pf8200`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (3): `compatible`, `reg`, `regulators`
- Property detail signals:
  - `compatible` (enum `nxp,pf8100`, `nxp,pf8121a`, `nxp,pf8200`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller)
- Child-node or pattern API:
  - `regulators` child object with properties vsnvs

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/nxp,pf8x00-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@8 {; compatible = "nxp,pf8100";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/onnn,fan53880.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/onnn,fan53880.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Onsemi FAN53880 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The FAN53880 is an I2C porgrammable power management IC (PMIC) that contains a BUCK (step-down converter), four low dropouts (LDO) and one BOOST (step-up converter) output. It is designed for mobile power applications.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/onnn,fan53880.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Christoph Fritz <chf.fritz@googlemail.com>.
- Compatible contract: `onnn,fan53880`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (8): `$nodename`, `compatible`, `reg`, `VIN12-supply`, `VIN3-supply`, `VIN4-supply`, `PVIN-supply`, `regulators`
- Regulator/vendor integration properties: `VIN12-supply`, `VIN3-supply`, `VIN4-supply`, `PVIN-supply`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `onnn,fan53880`)
  - `reg` (maxItems 1)
  - `VIN12-supply` (Input supply phandle(s) for LDO1 and LDO2)
  - `VIN3-supply` (Input supply phandle(s) for LDO3)
  - `VIN4-supply` (Input supply phandle(s) for LDO4)
  - `PVIN-supply` (Input supply phandle(s) for BUCK and BOOST)
  - `regulators` (ref regulator.yaml#; type object; list of regulators provided by this controller, must be named after their hardware counterparts LDO[1-4], BUCK and BOOST)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/onnn,fan53880.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/onnn,fan53880.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/onnn,fan53880.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@35 {; compatible = "onnn,fan53880";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/onnn,fan53880.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Generic PWM Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Currently supports 2 modes of operation: Voltage Table: When in this mode, a voltage table (See below) of predefined voltage <=> duty-cycle values must be provided via DT. Limitations are that the regulator can only operate at the voltages supplied in the table. Intermediary duty-cycle values which would normally allow finer grained voltage selection are ignored and rendered useless. Although more control is given to the user if the assumptions made in continuous-voltage mode do not reign true. Continuous Voltage: This mode uses the regulator's maximum and minimum supplied voltages specified in the regulator-{min,max}-microvolt properties to calculate appropriate duty-cycle values. This allo...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/pwm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Brian Norris <briannorris@chromium.org>, Lee Jones <lee@kernel.org>, Alexandre Courbot <acourbot@nvidia.com>.
- Compatible contract: `pwm-regulator`
- Top-level required properties: `compatible`, `pwms`
- Required keys across top-level and child schemas: `compatible`, `pwms`
- Top-level declared properties (6): `compatible`, `pwms`, `voltage-table`, `enable-gpios`, `pwm-dutycycle-unit`, `pwm-dutycycle-range`
- Regulator/vendor integration properties: `enable-gpios`
- Property detail signals:
  - `compatible` (const `pwm-regulator`)
  - `pwms` (maxItems 1)
  - `voltage-table` (ref /schemas/types.yaml#/definitions/uint32-matrix; Voltage and Duty-Cycle table.)
  - `enable-gpios` (maxItems 1; Regulator enable GPIO)
  - `pwm-dutycycle-unit` (ref /schemas/types.yaml#/definitions/uint32; default 100; Integer value encoding the duty cycle unit. If not defined, <100> is assumed, meaning that pwm-dutycycle-range contains ...)
  - `pwm-dutycycle-range` (ref /schemas/types.yaml#/definitions/uint32-array; 2 fixed item schema(s); default ['0 100']; Should contain 2 entries. The first entry is encoding the dutycycle for regulator-min-microvolt and the second one the d...)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-matrix`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`
- Textual schema references: `/schemas/regulator/pwm-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.
- PWM integration is explicit; the PWM provider and voltage table/state mapping control the regulator output model.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, pwms) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; // Continuous Voltage With Enable GPIO Example:; regulator {; compatible = "pwm-regulator";; pwms = <&pwm1 0 8448 0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. QCA6390 PMU Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The QCA6390 package contains discrete modules for WLAN and Bluetooth. They are powered by the Power Management Unit (PMU) that takes inputs from the host and provides LDO outputs. This document describes this module.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,qca6390-pmu.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bartosz Golaszewski <bartosz.golaszewski@linaro.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `regulators`, `vddaon-supply`, `vddpmu-supply`, `vddrfa0p95-supply`, `vddrfa1p3-supply`, `vddrfa1p9-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`, `vddasd-supply`, `vddrfa0p8-supply`, `vddrfa1p2-supply`, `vddrfa1p7-supply`, `vddrfa2p2-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vdd-supply`, `vdddig-supply`, `vddrfa1p8-supply`
- Top-level declared properties (26): `compatible`, `vdd-supply`, `vddaon-supply`, `vddasd-supply`, `vdddig-supply`, `vddpmu-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vddio1p2-supply`, `vddrfa0p8-supply`, `vddrfa0p95-supply`, `vddrfa1p2-supply`, `vddrfa1p3-supply`, `vddrfa1p7-supply`, `vddrfa1p8-supply`, `vddrfa1p9-supply`, `vddrfa2p2-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`, `wlan-enable-gpios`, `bt-enable-gpios`, `swctrl-gpios`, `xo-clk-gpios`, ... (26 total)
- Regulator/vendor integration properties: `vdd-supply`, `vddaon-supply`, `vddasd-supply`, `vdddig-supply`, `vddpmu-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vddio1p2-supply`, `vddrfa0p8-supply`, `vddrfa0p95-supply`, `vddrfa1p2-supply`, `vddrfa1p3-supply`, `vddrfa1p7-supply`, `vddrfa1p8-supply`, `vddrfa1p9-supply`, `vddrfa2p2-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`
- Property detail signals:
  - `compatible`
  - `vdd-supply` (VDD supply regulator handle)
  - `vddaon-supply` (VDD_AON supply regulator handle)
  - `vddasd-supply` (VDD_ASD supply regulator handle)
  - `vdddig-supply` (VDD_DIG supply regulator handle)
  - `vddpmu-supply` (VDD_PMU supply regulator handle)
  - `vddpmumx-supply` (VDD_PMU_MX supply regulator handle)
  - `vddpmucx-supply` (VDD_PMU_CX supply regulator handle)
  - `vddio1p2-supply` (VDD_IO_1P2 supply regulator handle)
  - `vddrfa0p8-supply` (VDD_RFA_0P8 supply regulator handle)
  - `vddrfa0p95-supply` (VDD_RFA_0P95 supply regulator handle)
  - `vddrfa1p2-supply` (VDD_RFA_1P2 supply regulator handle)
  - `vddrfa1p3-supply` (VDD_RFA_1P3 supply regulator handle)
  - `vddrfa1p7-supply` (VDD_RFA_1P7 supply regulator handle)
  - `vddrfa1p8-supply` (VDD_RFA_1P8 supply regulator handle)
  - `vddrfa1p9-supply` (VDD_RFA_1P9 supply regulator handle)
  - `vddrfa2p2-supply` (VDD_RFA_2P2 supply regulator handle)
  - `vddpcie1p3-supply` (VDD_PCIE_1P3 supply regulator handle)
  - ... plus 8 more top-level declared propertie(s).
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 4 `if` block(s), 4 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,qca6390-pmu.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; pmu {; compatible = "qcom,qca6390-pmu";; pinctrl-names = "default";; pinctrl-0 = <&bt_en_state>, <&wlan_en_state>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm RPM regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Qualcomm RPM regulator is modelled as a subdevice of the RPM. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,rpm.yaml for information regarding the RPM node. The regulator node houses sub-nodes for each regulator within the device. Each sub-node is identified using the node's name, with valid values listed for each of the pmics below. For pm8058 l0, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14, l15, l16, l17, l18, l19, l20, l21, l22, l23, l24, l25, s0, s1, s2, s3, s4, lvs0, lvs1, ncp For pm8901 l0, l1, l2, l3, l4, l5, l6, s0, s1, s2, s3, s4, lvs0, lvs1, lvs2, lvs3, mvs For pm8921 s1, s2, s3, s4, s7, s8, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l1...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,rpm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bjorn Andersson <andersson@kernel.org>.
- Compatible contract: `qcom,rpm-pm8058-regulators`, `qcom,rpm-pm8901-regulators`, `qcom,rpm-pm8921-regulators`, `qcom,rpm-pm8018-regulators`, `qcom,rpm-smb208-regulators`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (enum `qcom,rpm-pm8058-regulators`, `qcom,rpm-pm8901-regulators`, `qcom,rpm-pm8921-regulators`, `qcom,rpm-pm8018-regulators`, `qcom,rpm-smb208-regulators`)
- Child-node or pattern API:
  - pattern child/property `.*-supply$`
  - pattern child/property `^((s|l|lvs)[0-9]*|s[1-2][a-b]|ncp|mvs|usb-switch|hdmi-switch)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/qcom,rpm-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/mfd/qcom-rpm.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/mfd/qcom-rpm.h>; regulators {; compatible = "qcom,rpm-pm8921-regulators";; vdd_l1_l2_l12_l18-supply = <&pm8921_s4>;; s1 {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. RPMh Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: rpmh-regulator devices support PMIC regulator management via the Voltage Regulator Manager (VRM) and Oscillator Buffer (XOB) RPMh accelerators. The APPS processor communicates with these hardware blocks via a Resource State Coordinator (RSC) using command packets. The VRM allows changing three parameters for a given regulator, enable state, output voltage, and operating mode. The XOB allows changing only a single parameter for a given regulator, its enable state. Despite its name, the XOB is capable of controlling the enable state of any PMIC peripheral. It is used for clock buffers, low-voltage switches, and LDO/SMPS regulators which have a fixed voltage and mode. ======================= Re...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,rpmh-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bjorn Andersson <bjorn.andersson@linaro.org>, Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `qcom,pm6150-rpmh-regulators`, `qcom,pm6150l-rpmh-regulators`, `qcom,pm6350-rpmh-regulators`, `qcom,pm660-rpmh-regulators`, `qcom,pm660l-rpmh-regulators`, `qcom,pm7325-rpmh-regulators`, `qcom,pm7550-rpmh-regulators`, `qcom,pm8005-rpmh-regulators`, `qcom,pm8009-rpmh-regulators`, `qcom,pm8009-1-rpmh-regulators`, `qcom,pm8010-rpmh-regulators`, `qcom,pm8150-rpmh-regulators`, ... (37 total)
- Top-level required properties: `compatible`, `qcom,pmic-id`
- Required keys across top-level and child schemas: `compatible`, `qcom,pmic-id`
- Top-level declared properties (6): `compatible`, `qcom,pmic-id`, `qcom,always-wait-for-ack`, `vdd-flash-supply`, `vdd-rgb-supply`, `bob`
- Regulator/vendor integration properties: `qcom,pmic-id`, `qcom,always-wait-for-ack`, `vdd-flash-supply`, `vdd-rgb-supply`
- Property detail signals:
  - `compatible` (enum `qcom,pm6150-rpmh-regulators`, `qcom,pm6150l-rpmh-regulators`, `qcom,pm6350-rpmh-regulators`, `qcom,pm660-rpmh-regulators`, `qcom,pm660l-rpmh-regulators`, `qcom,pm7325-rpmh-regulators`, `qcom,pm7550-rpmh-regulators`, `qcom,pm8005-rpmh-regulators`, ... (37 total))
  - `qcom,pmic-id` (ref /schemas/types.yaml#/definitions/string; RPMh resource name suffix used for the regulators found on this PMIC.)
  - `qcom,always-wait-for-ack` (ref /schemas/types.yaml#/definitions/flag; Boolean flag which indicates that the application processor must wait for an ACK or a NACK from RPMh for every request s...)
  - `vdd-flash-supply` (Input supply phandle of flash.)
  - `vdd-rgb-supply` (Input supply phandle of rgb.)
  - `bob` (ref regulator.yaml#; type object; BOB regulator node.)
- Child-node or pattern API:
  - `bob` child object
  - pattern child/property `^(smps|ldo|lvs|bob)[0-9]+$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 28 `if` block(s), 28 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/flag`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,rpmh-regulator.yaml`; `/schemas/types.yaml#/definitions/flag`; `/schemas/types.yaml#/definitions/string`
- Header/example integration: `dt-bindings/regulator/qcom,rpmh-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, qcom,pmic-id) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/regulator/qcom,rpmh-regulator.h>; pm8998-rpmh-regulators {; compatible = "qcom,pm8998-rpmh-regulators";; qcom,pmic-id = "a";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,sdm845-refgen-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,sdm845-refgen-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. REFGEN Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The REFGEN (reference voltage generator) regulator provides reference voltage for on-chip IPs (like PHYs) on some Qualcomm SoCs.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,sdm845-refgen-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Konrad Dybcio <konradybcio@kernel.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,sdm845-refgen-regulator.yaml`

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,sdm845-refgen-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,sdm845-refgen-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `regulator@162f000 {; compatible = "qcom,sm8250-refgen-regulator";; reg = <0x0162f000 0x84>;; };`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,sdm845-refgen-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: QCOM SMD RPM REGULATOR. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Qualcomm RPM over SMD regulator is modelled as a subdevice of the RPM. Because SMD is used as the communication transport mechanism, the RPM resides as a subnode of the SMD. As such, the SMD-RPM regulator requires that the SMD and RPM nodes be present. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,smd.yaml for information pertaining to the SMD node. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,smd-rpm.yaml for information regarding the RPM node. The regulator node houses sub-nodes for each regulator within the device. Each sub-node is identified using the node's name, with valid values listed for each of the pmics below. For mp5496, s1, s2, l2, l5 For...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,smd-rpm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Andy Gross <agross@kernel.org>, Bjorn Andersson <bjorn.andersson@linaro.org>.
- Compatible contract: `qcom,rpm-mp5496-regulators`, `qcom,rpm-pm2250-regulators`, `qcom,rpm-pm6125-regulators`, `qcom,rpm-pm660-regulators`, `qcom,rpm-pm660l-regulators`, `qcom,rpm-pm8226-regulators`, `qcom,rpm-pm8841-regulators`, `qcom,rpm-pm8909-regulators`, `qcom,rpm-pm8916-regulators`, `qcom,rpm-pm8937-regulators`, `qcom,rpm-pm8941-regulators`, `qcom,rpm-pm8950-regulators`, ... (20 total)
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (enum `qcom,rpm-mp5496-regulators`, `qcom,rpm-pm2250-regulators`, `qcom,rpm-pm6125-regulators`, `qcom,rpm-pm660-regulators`, `qcom,rpm-pm660l-regulators`, `qcom,rpm-pm8226-regulators`, `qcom,rpm-pm8841-regulators`, `qcom,rpm-pm8909-regulators`, ... (20 total))
- Child-node or pattern API:
  - pattern child/property `.*-supply$`
  - pattern child/property `^((s|l|lvs|5vs)[0-9]*)|(boost-bypass)|(bob)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,smd-rpm-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pm8941-regulators {; compatible = "qcom,rpm-pm8941-regulators";; vdd_l13_l20_l23_l24-supply = <&pm8941_boost>;; pm8941_s3: s3 {; regulator-min-microvolt = <1800000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,spmi-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,spmi-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm SPMI Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,spmi-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Robert Marko <robimarko@gmail.com>.
- Compatible contract: `qcom,pm6125-regulators`, `qcom,pm660-regulators`, `qcom,pm660l-regulators`, `qcom,pm8004-regulators`, `qcom,pm8005-regulators`, `qcom,pm8019-regulators`, `qcom,pm8226-regulators`, `qcom,pm8841-regulators`, `qcom,pm8909-regulators`, `qcom,pm8916-regulators`, `qcom,pm8937-regulators`, `qcom,pm8941-regulators`, ... (18 total)
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (2): `compatible`, `qcom,saw-reg`
- Regulator/vendor integration properties: `qcom,saw-reg`
- Property detail signals:
  - `compatible` (enum `qcom,pm6125-regulators`, `qcom,pm660-regulators`, `qcom,pm660l-regulators`, `qcom,pm8004-regulators`, `qcom,pm8005-regulators`, `qcom,pm8019-regulators`, `qcom,pm8226-regulators`, `qcom,pm8841-regulators`, ... (18 total))
  - `qcom,saw-reg` (ref /schemas/types.yaml#/definitions/phandle; Reference to syscon node defining the SAW registers)
- Child-node or pattern API:
  - pattern child/property `^(5vs[1-2]|(l|s)[1-9][0-9]?|lvs[1-4])$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 18 `if` block(s), 18 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle`; `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/qcom,spmi-regulator.yaml`; `/schemas/types.yaml#/definitions/phandle`; `/schemas/types.yaml#/definitions/uint32`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,spmi-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,spmi-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `regulators {; compatible = "qcom,pm8941-regulators";; vdd_l1_l3-supply = <&s1>;; s1: s1 {; regulator-min-microvolt = <1300000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,spmi-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,usb-vbus-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,usb-vbus-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: The Qualcomm PMIC VBUS output regulator driver. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This regulator driver controls the VBUS output by the Qualcomm PMIC. This regulator will be enabled in situations where the device is required to provide power to the connected peripheral.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,usb-vbus-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Wesley Cheng <quic_wcheng@quicinc.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `reg`, `regulator-min-microamp`, `regulator-max-microamp`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulator-min-microamp`, `regulator-max-microamp`
- Top-level declared properties (2): `compatible`, `reg`
- Property detail signals:
  - `compatible`
  - `reg` (maxItems 1; VBUS output base address)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,usb-vbus-regulator.yaml`

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulator-min-microamp, regulator-max-microamp) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,usb-vbus-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,usb-vbus-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; #address-cells = <1>;; #size-cells = <0>;; usb-vbus-regulator@1100 {; compatible = "qcom,pm8150b-vbus-reg";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,usb-vbus-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. WCN3990 PMU Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The WCN3990 package contains discrete modules for WLAN and Bluetooth. They are powered by the Power Management Unit (PMU) that takes inputs from the host and provides LDO outputs. This document describes this module.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,wcn3990-pmu.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bartosz Golaszewski <bartosz.golaszewski@oss.qualcomm.com>.
- Compatible contract: `qcom,wcn3950-pmu`, `qcom,wcn3988-pmu`, `qcom,wcn3990-pmu`, `qcom,wcn3991-pmu`, `qcom,wcn3998-pmu`
- Top-level required properties: `compatible`, `regulators`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`
- Required keys across top-level and child schemas: `compatible`, `regulators`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`
- Top-level declared properties (9): `compatible`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`, `vddch1-supply`, `swctrl-gpios`, `clocks`, `regulators`
- Regulator/vendor integration properties: `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`, `vddch1-supply`
- Property detail signals:
  - `compatible` (enum `qcom,wcn3950-pmu`, `qcom,wcn3988-pmu`, `qcom,wcn3990-pmu`, `qcom,wcn3991-pmu`, `qcom,wcn3998-pmu`)
  - `vddio-supply` (VDD_IO supply regulator handle)
  - `vddxo-supply` (VDD_XTAL supply regulator handle)
  - `vddrf-supply` (VDD_RF supply regulator handle)
  - `vddch0-supply` (chain 0 supply regulator handle)
  - `vddch1-supply` (chain 1 supply regulator handle)
  - `swctrl-gpios` (maxItems 1; GPIO line indicating the state of the clock supply to the BT module)
  - `clocks` (maxItems 1; Reference clock handle)
  - `regulators` (type object; LDO outputs of the PMU)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,wcn3990-pmu.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulators, vddio-supply, vddxo-supply, vddrf-supply, vddch0-supply) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; pmu {; compatible = "qcom,wcn3990-pmu";; vddio-supply = <&vreg_io>;; vddxo-supply = <&vreg_xo>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom-labibb-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom-labibb-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm's LAB(LCD AMOLED Boost)/IBB(Inverting Buck Boost) Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: LAB can be used as a positive boost power supply and IBB can be used as a negative boost power supply for display panels. Currently implemented for pmi8998.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom-labibb-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Sumit Semwal <sumit.semwal@linaro.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `interrupts`, `interrupt-names`
- Top-level declared properties (3): `compatible`, `lab`, `ibb`
- Property detail signals:
  - `compatible`
  - `lab` (ref regulator.yaml#; type object)
  - `ibb` (ref regulator.yaml#; type object)
- Child-node or pattern API:
  - `lab` child object requiring interrupts, interrupt-names with properties qcom,soft-start-us, interrupts, interrupt-names
  - `ibb` child object requiring interrupts, interrupt-names with properties qcom,discharge-resistor-kohms, interrupts, interrupt-names

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/qcom-labibb-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/interrupt-controller/irq.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom-labibb-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom-labibb-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/interrupt-controller/irq.h>; labibb {; compatible = "qcom,pmi8998-lab-ibb";; lab {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom-labibb-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: RaspberryPi 5" and 7" display V2 MCU-based regulator/backlight controller. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The RaspberryPi 5" and 7" display 2 has an MCU-based regulator, PWM backlight and GPIO controller on the PCB, which is used to turn the display unit on/off and control the backlight.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Marek Vasut <marek.vasut+renesas@mailbox.org>.
- Compatible contract: `raspberrypi,touchscreen-panel-regulator-v2`
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `#pwm-cells`
- Required keys across top-level and child schemas: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `#pwm-cells`
- Top-level declared properties (5): `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `#pwm-cells`
- Property detail signals:
  - `compatible` (const `raspberrypi,touchscreen-panel-regulator-v2`)
  - `reg` (maxItems 1)
  - `gpio-controller` (boolean schema True)
  - `#gpio-cells` (const `2`; The first cell is the pin number, and the second cell is used to specify the gpio polarity (GPIO_ACTIVE_HIGH or GPIO_ACT...)
  - `#pwm-cells` (const `3`; See ../../pwm/pwm.yaml for description of the cell formats.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, gpio-controller, #gpio-cells, #pwm-cells) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@45 {; compatible = "raspberrypi,touchscreen-panel-regulator-v2";; reg = <0x45>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator-v2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: RaspberryPi 7" display ATTINY88-based regulator/backlight controller. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The RaspberryPi 7" display has an ATTINY88-based regulator/backlight controller on the PCB, which is used to turn the display unit on/off and control the backlight.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Marek Vasut <marex@denx.de>.
- Compatible contract: `raspberrypi,7inch-touchscreen-panel-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (4): `compatible`, `reg`, `gpio-controller`, `#gpio-cells`
- Property detail signals:
  - `compatible` (const `raspberrypi,7inch-touchscreen-panel-regulator`)
  - `reg` (maxItems 1)
  - `gpio-controller` (boolean schema True)
  - `#gpio-cells` (const `2`)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@45 {; compatible = "raspberrypi,7inch-touchscreen-panel-regulator";; reg = <0x45>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/raspberrypi,7inch-touchscreen-panel-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator-output.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator-output.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Regulator output connector. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: This describes a power output connector supplied by a regulator, such as a power outlet on a power distribution unit (PDU). The connector may be standalone or merely one channel or set of pins within a ganged physical connector carrying multiple independent power outputs.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/regulator-output.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Zev Weiss <zev@bewilderbeest.net>.
- Compatible contract: `regulator-output`
- Top-level required properties: `compatible`, `vout-supply`
- Required keys across top-level and child schemas: `compatible`, `vout-supply`
- Top-level declared properties (2): `compatible`, `vout-supply`
- Regulator/vendor integration properties: `vout-supply`
- Property detail signals:
  - `compatible` (const `regulator-output`)
  - `vout-supply` (Phandle of the regulator supplying the output.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found.
- Textual schema references: `/schemas/regulator/regulator-output.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, vout-supply) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator-output.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator-output.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `output {; compatible = "regulator-output";; vout-supply = <&output_reg>;; };`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/regulator-output.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/renesas,raa215300.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/renesas,raa215300.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Renesas RAA215300 Power Management Integrated Circuit (PMIC). It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The RAA215300 is a high-performance, low-cost 9-channel PMIC designed for 32-bit and 64-bit MCU and MPU applications. It supports DDR3, DDR3L, DDR4, and LPDDR4 memory power requirements. The internally compensated regulators, built-in Real-Time Clock (RTC), 32kHz crystal oscillator, and coin cell battery charger provide a highly integrated, small footprint power solution ideal for System-On-Module (SOM) applications. A spread spectrum feature provides an ease-of-use solution for noise-sensitive audio or RF applications. This device exposes two devices via I2C. One for the integrated RTC IP, and one for everything else. Link to datasheet: https://www.renesas.com/in/en/products/power-power-man...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/renesas,raa215300.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Biju Das <biju.das.jz@bp.renesas.com>.
- Compatible contract: `renesas,raa215300`
- Top-level required properties: `compatible`, `reg`, `reg-names`
- Required keys across top-level and child schemas: `compatible`, `reg`, `reg-names`
- Top-level declared properties (6): `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`
- Property detail signals:
  - `compatible` (enum `renesas,raa215300`)
  - `reg` (maxItems 2)
  - `reg-names` (2 fixed item schema(s))
  - `interrupts` (maxItems 1)
  - `clocks` (maxItems 1; The clocks are optional. The RTC is disabled, if no clocks are provided(either xin or clkin).)
  - `clock-names` (enum `xin`, `clkin`; Use xin, if connected to an external crystal. Use clkin, if connected to an external clock signal.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found.
- Textual schema references: `/schemas/regulator/renesas,raa215300.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, reg-names) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/renesas,raa215300.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/renesas,raa215300.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `/* 32.768kHz crystal */; x2: x2-clock {; compatible = "fixed-clock";; #clock-cells = <0>;; clock-frequency = <32768>;; };`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/renesas,raa215300.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4801-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4801-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Richtek RT4801 Display Bias regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Regulator nodes should be named to DSVP and DSVN. The definition for each of these nodes is defined using the standard binding for regulators at Documentation/devicetree/bindings/regulator/regulator.txt. Datasheet is available at https://www.richtek.com/assets/product_file/RT4801H/DS4801H-00.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/richtek,rt4801-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: ChiYuan Huang <cy_huang@richtek.com>.
- Compatible contract: `richtek,rt4801`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (3): `compatible`, `reg`, `enable-gpios`
- Regulator/vendor integration properties: `enable-gpios`
- Property detail signals:
  - `compatible` (enum `richtek,rt4801`)
  - `reg` (maxItems 1)
  - `enable-gpios` (minItems 1; maxItems 2; GPIOs to use to enable DSVP/DSVN regulator. The first one is ENP to enable DSVP, and second one is ENM to enable DSVN. N...)
- Child-node or pattern API:
  - pattern child/property `^DSV(P|N)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/richtek,rt4801-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4801-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4801-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; rt4801@73 {; compatible = "richtek,rt4801";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4801-regulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Richtek RT4803 Boost Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: RT4803 is a boost regulator that's designed to provide the minimum output voltage, even if the input voltage is lower than the required voltage. It supports boost and auto bypass mode that depends on the difference between the input and output voltage. If the input is lower than the output, mode will transform to boost mode. Otherwise, turn on bypass switch to enter bypass mode. Datasheet is available at https://www.richtek.com/assets/product_file/RT4803/DS4803-03.pdf https://www.richtek.com/assets/product_file/RT4803A/DS4803A-06.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/richtek,rt4803.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: ChiYuan Huang <cy_huang@richtek.com>.
- Compatible contract: `richtek,rt4803`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (4): `compatible`, `reg`, `richtek,vsel-active-high`, `regulator-allowed-modes`
- Regulator/vendor integration properties: `richtek,vsel-active-high`, `regulator-allowed-modes`
- Property detail signals:
  - `compatible` (enum `richtek,rt4803`)
  - `reg` (maxItems 1)
  - `richtek,vsel-active-high` (type boolean; Specify the VSEL register group is using when system is active)
  - `regulator-allowed-modes` (items enum 2 values; Available operating mode 1: Auto PFM/PWM 2: Force PWM)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/richtek,rt4803.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@75 {; compatible = "richtek,rt4803";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4831-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4831-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Richtek RT4831 Display Bias Voltage Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: RT4831 is a multifunctional device that can provide power to the LCD display and LCD backlight. For Display Bias Voltage DSVP and DSVN, the output range is about 4V to 6.5V. It is sufficient to meet the current LCD power requirement. DSVLCM is a boost regulator in IC internal as DSVP and DSVN input power. Its voltage should be configured above 0.15V to 0.2V gap larger than the voltage needed for DSVP and DSVN. Too much voltage gap could improve the voltage drop from the heavy loading scenario. But it also make the power efficiency worse. It's a trade-off. Datasheet is available at https://www.richtek.com/assets/product_file/RT4831A/DS4831A-05.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/richtek,rt4831-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: ChiYuan Huang <cy_huang@richtek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: No required arrays were found.
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^DSV(LCM|P|N)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/richtek,rt4831-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4831-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4831-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4831-regulator.yaml -->
