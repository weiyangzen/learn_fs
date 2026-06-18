# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96802-pmic.yaml

Purpose: Binding for ROHM BD96802 and BD96806 configurable automotive PMICs, describing their I2C node, safety interrupt lines, and regulator child tree.

Important schema surface and control flow: compatible is `rohm,bd96802` or `rohm,bd96806`; `reg`, one or two interrupts, matching `interrupt-names`, and `regulators` are required. The interrupt model mirrors BD96801: `intb` is the normal interrupt, optional `errb` reports fatal faults that can shut down power outputs. The regulator subtree references `../regulator/rohm,bd96802-regulator.yaml`, and additional top-level properties are rejected.

State, dependencies, and integration: DT state sets PMIC address, IRQ wiring, and regulator safety/voltage constraints for the BD96802 MFD and regulator drivers. Dependencies include the ROHM BD96802 regulator schema and common interrupt/regulator infrastructure. Risks include not connecting `errb` on systems that need fatal fault capture, misspelled interrupt names, and regulator child properties accepted only by the delegated schema. Test signals are binding validation, example validation, regulator child validation, and runtime IRQ/regulator registration.
