# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg11-pmic.yaml

Purpose: Schema for the Samsung S2MPG11 sub-PMIC, complementing S2MPG10 with buck, buck-boost, LDO, NTC, power meter, GPIO, and wakeup-related resources.

Important schema surface and control flow: required properties are `compatible = "samsung,s2mpg11-pmic"`, `interrupts`, and `regulators`. `wakeup-source` is optional. Pattern properties define buck input supplies for numbered `vinbNs`, special `vinba`, `vinbb`, and `vinbd`, plus `vinl1s` through `vinl6s` shared LDO supplies. Regulators are delegated to `/schemas/regulator/samsung,s2mpg11-regulator.yaml`.

State, dependencies, and integration: DT persists the sub-PMIC IRQ, rail input topology, and regulator constraints consumed by the S2MPG11 MFD/regulator code. Dependencies include the Samsung regulator schema, GPIO/interrupt bindings, and shared Samsung PMIC infrastructure. Risks include confusing `m` and `s` suffixes between main and sub PMIC rails, incomplete shared-LDO supply descriptions, and external-control constants that must match regulator child capabilities. Test signals are `dt_binding_check`, regulator child schema validation, and runtime probe of regulators and wake-capable interrupt handling.
