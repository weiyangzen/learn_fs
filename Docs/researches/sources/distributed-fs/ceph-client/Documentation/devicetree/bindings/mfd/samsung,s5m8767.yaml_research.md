# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s5m8767.yaml

Purpose: Binding for the Samsung S5M8767 PMIC, describing regulators, clock outputs, interrupts, wakeup, input supplies, and buck DVS GPIO configuration.

Important schema surface and control flow: `compatible = "samsung,s5m8767-pmic"`, `reg`, and `regulators` are required. Optional `clocks` references the Samsung S2MPS11-style clock provider schema. The binding has detailed DVS properties for buck2, buck3, and buck4 voltage tables, DVS GPIOs, dynamic scaling enable flags, default DVS index, discharge GPIOs, and input supplies `vinb1-9` and `vinl1-9`. Dependency rules require DVS GPIOs when DVS voltage arrays or per-buck GPIO-DVS flags are present. Regulator details are delegated to the S5M8767 regulator schema.

State, dependencies, and integration: DT persists power-rail constraints and dynamic voltage scaling wiring used by Samsung PMIC regulator and clock drivers. Dependencies include the Samsung clock and regulator schemas, GPIO bindings, and interrupt bindings. Risks include incomplete DVS dependency sets, wrong default DVS index, GPIO polarity mistakes, and supply phandle omissions for enabled rails. Test signals are `dt_binding_check`, dependency failures for partial DVS descriptions, delegated regulator validation, and runtime DVS/regulator/clock behavior.
