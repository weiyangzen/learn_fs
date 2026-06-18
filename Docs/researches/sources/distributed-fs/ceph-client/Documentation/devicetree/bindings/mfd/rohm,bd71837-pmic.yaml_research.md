# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71837-pmic.yaml

Purpose: Schema for ROHM BD71837 PMICs used with NXP i.MX platforms, modeling regulator setup, interrupt wiring, external oscillator input, clock output, and reset/power-button timing options.

Important schema surface and control flow: `compatible = "rohm,bd71837"`, `reg`, `interrupts`, `#clock-cells`, and `regulators` are required. Optional clock input uses `clocks` and `clock-names = "osc"`, clock output naming is fixed to `pmic_clk`, and ROHM-specific properties describe SNVS reset power retention and short/long press timing using enumerated millisecond values. The regulator subtree is validated by the BD71837 regulator binding.

State, dependencies, and integration: board DT determines how the BD71837 MFD provides regulators and clock output and how reset and button-timing policy is programmed. Dependencies include the ROHM regulator schema, clock provider/consumer bindings, interrupt bindings, and PMIC MFD/regulator drivers. Risks include choosing unsupported press durations, mismatching external oscillator wiring, and relying on reset-SNVS behavior without matching board power topology. Test signals are binding checks, example validation, regulator child schema coverage, and boot-time confirmation of clock output and PMIC reset-button behavior.
