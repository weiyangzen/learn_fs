# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71847-pmic.yaml

Purpose: Binding for ROHM BD71847 and BD71850 PMICs, primarily capturing regulator topology, reset/button timing, optional external clock input, and clock output behavior.

Important schema surface and control flow: `compatible` is either `rohm,bd71847` or `rohm,bd71850`; `reg`, `interrupts`, `#clock-cells`, and `regulators` are required. Optional `clocks` may feed the PMIC oscillator, `clock-output-names` names the PMIC clock output, and dependency rules tie `#clock-cells` and `clocks` together. ROHM properties describe SNVS retention on reset and enumerated short/long power-button press times. Regulators are delegated to the BD71847 regulator schema and top-level additional properties are rejected.

State, dependencies, and integration: persistent DT configures the PMIC MFD, regulators, interrupt line, and optional clock provider/consumer relationship. Dependencies include the ROHM regulator binding, clock bindings, interrupt bindings, and PMIC drivers. Risks include incompatible clock-cell/clock combinations, wrong variant compatible for board silicon, and unsupported button timing values. Test signals are `dt_binding_check`, regulator child validation, dependency-rule failures for incomplete clock descriptions, and runtime regulator/clock probe success.
