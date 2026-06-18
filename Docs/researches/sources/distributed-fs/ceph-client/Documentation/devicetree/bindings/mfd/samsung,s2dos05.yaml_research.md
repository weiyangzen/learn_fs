# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2dos05.yaml

Purpose: Binding for the Samsung S2DOS05 PMIC, a panel/touchscreen companion PMIC with four LDOs, one buck, and ADC-related power measurement functions.

Important schema surface and control flow: `compatible = "samsung,s2dos05"`, `reg`, and `regulators` are required. The `regulators` object allows `buck` and `ldo1` through `ldo4`; each child must use the common regulator schema and include `regulator-name`. Additional top-level and regulator-child properties outside the schema are rejected.

State, dependencies, and integration: DT persists the I2C address and regulator constraints for panel and touchscreen rails consumed by the S2DOS05 MFD/regulator support. Dependencies include the common regulator schema and I2C bus binding. Risks include the loose regex shape for regulator names if future rail names are added, missing `regulator-name`, and voltage ranges that do not match attached display hardware. Test signals are `dt_binding_check`, example validation, and runtime regulator registration for `buck` and `ldo1-4`.
