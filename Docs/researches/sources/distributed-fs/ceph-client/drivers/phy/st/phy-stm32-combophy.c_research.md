# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c

Purpose: STM32MP25 ComboPHY provider for USB3 or PCIe, configuring syscfg mode, PLL/refclock source, optional PCIe impedance/vswing, RX equalizer, runtime PM, and wake IRQ support.

Important APIs, types, and functions: `struct stm32_combophy` stores PHY, syscfg regmap, MMIO base, reset, bulk clocks (`apb`, `ker`, optional `pad`), type, init state, and wake IRQ. `stm32_combophy_xlate()` accepts one type cell (`PHY_TYPE_USB3` or `PHY_TYPE_PCIE`) and rejects pad clock use with USB3. `stm32_combophy_pll_init()` computes register fields for supported reference rates, deisolates the PHY, asserts/deasserts reset, polls PLL status, and applies PCIe-specific programming. `stm32_impedance_tune()` maps DT micro-ohm and microvolt values to discrete syscfg fields.

Control flow: probe maps MMIO, obtains clocks, reset, global syscfg regmap by compatible, creates the PHY, optionally requests wake IRQ, enables runtime PM, and registers custom xlate. Init increments runtime PM, enables clocks, sets mode, initializes PLL, marks active, and refreshes PM state. Exit clears mode-specific enable bits, isolates the PHY, disables clocks, and drops runtime PM. Noirq suspend/resume disables/re-enables clocks when initialized and toggles wake IRQ.

State and persistence: selected type and `is_init` persist in the driver object. Hardware state persists in syscfg CR registers and local analog loop control. Optional DT properties (`st,ssc-on`, output impedance, vswing, RX equalizer) shape configuration.

Dependencies and integration points: generic PHY, PM runtime, syscon/regmap, clock/reset frameworks, wake IRQ, USB3/PCIe consumers using dt-bindings PHY type cells.

Risks: only specific input clock rates are accepted; unsupported board clocks fail init. RX equalizer validation compares raw value to a bit mask rather than maximum field value, allowing values up to mask numeric value. `type` is mutable and single-consumer oriented. Wake IRQ handler only acknowledges, relying on system wake plumbing.

Test signals: USB3 and PCIe xlate modes, pad-clock rejection for USB3, PLL lock for each supported refclock, impedance/vswing DT bounds, suspend/resume wake behavior, and syscfg readback after init/exit.
