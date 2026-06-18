# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/spacemit,p1.yaml

Purpose: Binding for the SpacemiT P1 PMIC, defining the I2C PMIC node, interrupt line, regulator input supplies, and regulator child tree.

Important schema surface and control flow: `compatible = "spacemit,p1"`, `reg`, `interrupts`, and `regulators` are required. The top-level supply properties identify six VIN inputs plus analog and digital LDO input groups (`aldoin`, `dldoin1`, `dldoin2`). The `regulators` object delegates valid rail names and properties to the SpacemiT P1 regulator schema and closes unevaluated properties.

State, dependencies, and integration: persistent DT records PMIC address, IRQ, input-supply topology, and regulator constraints for the P1 MFD/regulator driver. Dependencies include the SpacemiT regulator binding, common regulator/interrupt/I2C bindings, and board-level supply providers. Risks include missing parent supply phandles for enabled rails, using regulator child names outside the delegated schema, and interrupt polarity mistakes. Test signals are `dt_binding_check`, referenced regulator schema validation, and runtime regulator probe with input supply resolution.
