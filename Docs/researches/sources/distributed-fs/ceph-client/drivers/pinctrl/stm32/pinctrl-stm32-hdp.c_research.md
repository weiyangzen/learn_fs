# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32-hdp.c

## Purpose
This driver controls the STM32 Hardware Debug Port, a small pinctrl/GPIO device that routes internal debug/observation signals to up to eight HDP pins and exposes output-only GPIO control for the HDP GPO value bits.

## Important APIs, types, and functions
`struct stm32_hdp` stores device state, MMIO base, clock, pinctrl device, optional firewall grants, generic gpiochip, cached mux/GPO state, function-name table, and firewall count. `stm32_hdp_pins[]` defines HDP0-7. `func_name_mp13`, `func_name_mp15`, and `func_name_mp25` provide 16 function names per HDP pin. Pinctrl callbacks expose one group per pin and use generic DT map/free helpers. Pinmux callbacks report `HDP_FUNC_TOTAL`, return function names, map each function to one HDP group, and write `HDP_MUX`. `stm32_hdp_probe()` maps resources, obtains firewall access, enables the clock, registers pinctrl, initializes a generic output-only gpiochip, and enables the HDP block. PM callbacks save/restore GPO and mux state.

## Control flow
Probe allocates state, optionally requests firewall access for all entries, maps resource 0, selects the function-name table from OF match data, enables the clock, registers and enables pinctrl, configures the generic gpiochip with data/set/clear registers, registers the gpiochip, writes `HDP_CTRL_ENABLE`, and logs hardware version. Pinmux `set_mux` computes the selected HDP line from `group_selector`, reduces the function selector modulo 16, updates that line's 4-bit field in `HDP_MUX`, and caches the full mux register. Suspend saves `HDP_GPOSET`, selects pinctrl sleep state, and disables the clock. Resume re-enables the clock, enables HDP, restores GPO set and mux state, and selects default state. Remove disables HDP and releases firewall grants.

## State and persistence behavior
The driver caches `mux_conf` on each mux update and `gposet_conf` on suspend. Hardware state lives in HDP control, mux, GPO set/clear/value, and version registers. The generic gpiochip is output-only (`GPIO_GENERIC_NO_INPUT`) and `get_direction` always reports output. Firewall grants are acquired at probe and explicitly released at remove.

## Dependencies and integration points
It depends on platform MMIO, clocks, pinctrl core, generic pinconf DT mapping, generic GPIO helpers, optional STM32 firewall APIs, and OF compatibles `st,stm32mp131-hdp`, `st,stm32mp151-hdp`, and `st,stm32mp251-hdp`. It does not use the common STM32 pinctrl core.

## Risks
Function selector space is flattened as 8*16 entries; wrong DT function indexes can select a valid but unintended signal. `set_mux` uses `func_selector %= HDP_FUNC`, so out-of-group function selectors wrap rather than fail. `gposet_conf` saves only the set register, not the clear/value register, so restored GPIO output state depends on hardware semantics. Firewall release is manual in remove; errors after partial firewall acquisition before drvdata lifetime ends need review against firewall helper semantics.

## Test signals
Tests should cover all three compatible function tables, pinmux selection on each HDP line, wrap behavior for selector values, output-only GPIO set/clear/value behavior, suspend/resume restoration of mux and GPO state, firewall-enabled and firewall-disabled builds, and removal disabling `HDP_CTRL`.
