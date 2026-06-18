# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9571mwv.yaml

Purpose: Devicetree binding for ROHM BD9571MWV and BD9574MWF PMICs, describing their I2C node, interrupt and GPIO controllers, DDR backup power mask, reset-button mode, and regulator children.

Important schema surface and control flow: compatible is `rohm,bd9571mwv` or `rohm,bd9574mwf`; `reg`, `interrupts`, interrupt-controller cells, GPIO controller cells, and one reset-mode property are required. `rohm,ddr-backup-power` is a 4-bit mask for DDR rails kept alive in backup mode. `oneOf` requires exactly a level-mode or pulse-mode RSTB description. `regulators` accepts only `vd09`, `vd18`, `vd25`, `vd33`, and `dvfs`, each using the common regulator schema and a matching `regulator-name` pattern.

State, dependencies, and integration: DT persists PMIC reset-mode straps, backup rail policy, regulator constraints, and provider roles for GPIO and interrupts. Dependencies include common regulator, GPIO, interrupt, and types schemas plus the BD957x MFD/regulator/GPIO drivers. Risks include specifying both or neither reset mode, using regulator names that do not match hardware rails, and setting an incorrect DDR backup mask. Test signals are `dt_binding_check`, `oneOf` validation, regulator-name pattern failures, and runtime interrupt/GPIO/regulator provider registration.
