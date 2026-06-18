# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg10-pmic.yaml

Purpose: Binding for the Samsung S2MPG10 main PMIC, which provides buck and LDO regulators, power meters, RTC clock outputs, GPIO interfaces, wakeup, and optional system power control.

Important schema surface and control flow: `compatible = "samsung,s2mpg10-pmic"`, `interrupts`, and `regulators` are required. Optional `clocks` references the Samsung S2MPS11 clock-provider schema, while `system-power-controller` and `wakeup-source` expose power-management roles. Pattern properties document supply phandles for `vinb1m` through `vinb10m` and `vinl1m` through `vinl15m`, including detailed rail sharing for LDO inputs. Regulators are validated by `/schemas/regulator/samsung,s2mpg10-regulator.yaml`.

State, dependencies, and integration: DT state describes main-PMIC interrupt wiring, regulator input supply topology, clock outputs, and PMIC ownership of system shutdown. Dependencies include Samsung clock and regulator schemas, GPIO/interrupt bindings, and S2MPG10 MFD/regulator/clock drivers. Risks include wrong main/sub PMIC rail suffixes, incomplete input supplies for shared LDO groups, and misuse of external-control regulator constants. Test signals are schema validation, referenced regulator and clock child validation, and runtime regulator/clock/wakeup registration.
