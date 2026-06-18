# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpa01.yaml

Purpose: Schema for the Samsung S2MPA01 PMIC, part of the S2M/S5M family with regulators, RTC, clock outputs, interrupts, and wakeup capability.

Important schema surface and control flow: the required properties are `compatible = "samsung,s2mpa01-pmic"`, `reg`, and `regulators`; `interrupts` and `wakeup-source` are optional. The regulator subtree is delegated to `/schemas/regulator/samsung,s2mpa01.yaml`, which owns the valid LDO/BUCK child names and regulator-specific constraints. Additional top-level properties are closed.

State, dependencies, and integration: persistent DT sets the PMIC I2C address and regulator initialization data and may wire an interrupt for RTC, power, or fault events. Dependencies include the Samsung S2MPA01 regulator schema, common interrupt and regulator infrastructure, and the S2M/S5M MFD drivers. Risks include omitting an interrupt when wake events are expected, using regulator names not covered by the referenced schema, and confusing S2MPA01 with adjacent S2MPS variants. Test signals are binding validation, delegated regulator validation, and boot-time registration of regulators and optional wake IRQs.
