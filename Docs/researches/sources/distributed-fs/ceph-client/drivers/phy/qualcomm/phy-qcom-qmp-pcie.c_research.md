# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c

## Purpose
This Linux kernel platform driver implements the Qualcomm QMP PCIe PHY provider. It binds many Qualcomm SoC-compatible strings to data-driven PHY configuration records, maps QSERDES/PCS register windows, controls regulators, resets, and clocks, registers generated pipe and optional PHY AUX clock outputs, and exposes a single `struct phy` through the generic PHY framework for PCIe root-complex or endpoint use.

## Important APIs, Types, And Data
- `enum qphy_reg_layout` indexes the per-generation PCS control/status offsets used by generic lifecycle code: software reset, start control, PCS status, and power-down control.
- `struct qmp_pcie_offsets` describes each hardware layout's relative SERDES, PCS, PCS_MISC, PCS_LANE1, TX/RX, secondary lane, TXZ/RXZ, and lane-shared windows.
- `struct qmp_phy_cfg_tbls` groups init tables for SERDES, TX/RX, TXZ/RXZ, PCS, PCS_MISC, PCS_LANE1, and lane-shared blocks.
- `struct qmp_phy_cfg` is the per-compatible contract: lane count, offsets, base init table set, optional RC/EP overrides, optional four-lane SERDES patch table, reset and regulator lists, register layout, power-down mask, PHYSTATUS bit mask, start-delay policy, and generated clock rates.
- `struct qmp_pcie` is runtime state: mapped MMIO bases, clock/reset/regulator handles, optional `phy_nocsr` reset, selected PCIe submode, fixed-rate clock providers, and the optional TCSR four-lane-selection result.
- Static `qmp_phy_init_tbl` families provide SoC and generation-specific register programming for MSM8998, IPQ6018/IPQ8074/IPQ9574, QCS615/QCS8300, SDM845 QMP/QHP, SC8180X/SC8280XP, SDX55/SDX65, SM8250/SM8350/SM8450/SM8550/SM8650/SM8750, SA8775P, SAR2130P, X1E80100/X1P42100, Glymur, and Kaanapali.
- `qmp_pcie_of_match_table` is the external binding surface. Each compatible maps directly to one `qmp_phy_cfg`.

## Control Flow
Probe allocates `qmp_pcie`, loads match data, obtains optional bulk clocks (`aux`, `cfg_ahb`, `ref`, `refgen`, `rchng`, `phy_aux`), reset controls, optional regulators, then parses either legacy child-node resources or the modern single resource window. Modern parsing applies `qmp_pcie_offsets` to derive all sub-block bases, reads optional `qcom,4ln-config-sel` through syscon/regmap, maps a second resource for port B when a four-lane split is selected, and obtains `pipe` plus optional `pipediv2` clocks. Legacy parsing maps child resources by index and carries special handling for SDM845 QHP and IPQ6018 PCS_MISC.

Power-on is split across generic PHY callbacks. `qmp_pcie_enable()` calls `qmp_pcie_init()` and then `qmp_pcie_power_on()`. Init may skip table programming when an optional `phy_nocsr` reset exists and boot firmware already left `SERDES_START | PCS_START` plus the expected power-down bits set. Otherwise it enables regulators, asserts/deasserts BCR resets around `phy_nocsr`, and enables the required bulk clocks. Power-on sets power-down bits, applies the common tables followed by RC or EP mode tables selected by `qmp_pcie_set_mode()`, enables pipe clocks, deasserts `phy_nocsr`, clears software reset, starts SERDES/PCS, optionally waits 1 ms, then polls PCS status until the configured `PHYSTATUS` bit clears or `PHY_INIT_COMPLETE_TIMEOUT` expires.

Four-lane handling is conditional: for configurations with at least four lanes and a true TCSR four-lane select bit, `qmp_pcie_init_registers()` applies the four-lane SERDES patch and calls `qmp_pcie_init_port_b()` to program lanes 3 and 4 through the second port's windows. Lane-specific table entries use `qmp_configure_lane()`, so lane masks embedded in `QMP_PHY_INIT_CFG_LANE()` determine which writes apply to each lane.

Power-off disables pipe clocks and, when there is no no-CSR reset preservation path, asserts SW reset, clears start bits, and clears power-down bits. Exit asserts `phy_nocsr` if present, otherwise asserts the bulk resets, then disables bulk clocks and regulators.

## State And Persistence
The driver persists no data outside device-managed kernel resources and hardware registers. Runtime state is held in `struct qmp_pcie` and is recreated on probe. Hardware state may persist across power cycles or bootloader handoff when `phy_nocsr` is present; the `skip_init` path intentionally preserves PHY programming across power-off/on cycles by avoiding register deinitialization when no-CSR reset support exists. The selected `mode` defaults to `PHY_MODE_PCIE_RC` and is updated only through `.set_mode`.

## Dependencies And Integration Points
The file integrates with the platform driver bus, device tree match data, generic PHY APIs, Linux clock provider APIs, bulk regulator/reset/clock frameworks, `syscon_regmap_lookup_by_phandle_args()` for four-lane routing, and shared Qualcomm QMP helpers from `phy-qcom-qmp-common.h` and `phy-qcom-qmp.h`. It depends heavily on versioned QSERDES/PCS register header macros, including the PCIe PCS headers in this subset. Downstream PCIe controller drivers consume the PHY through OF PHY lookup and pipe/aux clocks through the registered clock provider.

## Risks
The primary risk is table correctness: a wrong register macro, value, lane mask, or compatible-to-config mapping can cause silent link instability or PHY init timeouts. Resource-layout drift between legacy and modern device-tree bindings can map PCS_MISC, PCS_LANE1, or secondary lanes incorrectly. The bootloader handoff path is sensitive because `skip_init` trusts a small set of status bits as evidence that all required analog programming is valid. RC/EP overrides are sparse and may leave unset table families intentionally; a new SoC must ensure the base plus mode-specific tables compose correctly. Four-lane TCSR routing must match board wiring, or the driver may program the wrong port topology. Generated clock rates default to 125 MHz pipe unless overridden, with 20 MHz aux used only by selected configs.

## Test Signals
Useful signals include successful probe with all named clocks/resets/regulators resolved, clock provider registration from `clock-output-names`, successful `set_mode` for both RC and EP where supported, no `Init sequence not available` errors, no reset/regulator enable failures, and no `phy initialization timed-out` messages. Hardware validation should include PCIe link training at supported generations and lane widths, suspend/resume or repeated power-cycle tests to cover the `phy_nocsr` skip path, endpoint-mode boards for configs with `tbls_ep`, and four-lane designs that exercise `qcom,4ln-config-sel` and port B programming.
