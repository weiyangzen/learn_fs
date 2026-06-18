# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mps11.yaml

Purpose: Family binding for Samsung S2MPS11/13/14/15 and S2MPU02/05 PMICs, covering regulators, RTC/clock outputs, interrupts, wakeup behavior, and variant-specific power-off quirks.

Important schema surface and control flow: `compatible`, `reg`, and `regulators` are required. Supported compatibles select variant-specific regulator schemas through `allOf` branches. Optional `clocks` references the S2MPS11 clock binding, `interrupts` wires PMIC events, and `wakeup-source` enables wake handling. `samsung,s2mps11-acokb-ground` and `samsung,s2mps11-wrstbi-ground` are quirk flags, but `allOf` disables them for incompatible variants.

State, dependencies, and integration: DT state selects the exact regulator child contract and provides PMIC clock and wake/interrupt integration for S2M/S5M drivers. Dependencies include multiple Samsung regulator schemas, the Samsung PMIC clock schema, and interrupt bindings. Risks include using S2MPS11-only quirk properties on other variants, wrong regulator child set for the selected compatible, and missing clock child cells when clock outputs are consumed. Test signals are schema branch validation per compatible, quirk rejection on nonmatching variants, delegated regulator checks, and runtime regulator/clock/RTC interrupt probe.
