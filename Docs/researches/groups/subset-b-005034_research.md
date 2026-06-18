# Research Group subset-b-005034

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c

### Purpose
This Linux kernel platform driver implements the Qualcomm QMP PCIe PHY provider. It binds many Qualcomm SoC-compatible strings to data-driven PHY configuration records, maps QSERDES/PCS register windows, controls regulators, resets, and clocks, registers generated pipe and optional PHY AUX clock outputs, and exposes a single `struct phy` through the generic PHY framework for PCIe root-complex or endpoint use.

### Important APIs, Types, And Data
- `enum qphy_reg_layout` indexes the per-generation PCS control/status offsets used by generic lifecycle code: software reset, start control, PCS status, and power-down control.
- `struct qmp_pcie_offsets` describes each hardware layout's relative SERDES, PCS, PCS_MISC, PCS_LANE1, TX/RX, secondary lane, TXZ/RXZ, and lane-shared windows.
- `struct qmp_phy_cfg_tbls` groups init tables for SERDES, TX/RX, TXZ/RXZ, PCS, PCS_MISC, PCS_LANE1, and lane-shared blocks.
- `struct qmp_phy_cfg` is the per-compatible contract: lane count, offsets, base init table set, optional RC/EP overrides, optional four-lane SERDES patch table, reset and regulator lists, register layout, power-down mask, PHYSTATUS bit mask, start-delay policy, and generated clock rates.
- `struct qmp_pcie` is runtime state: mapped MMIO bases, clock/reset/regulator handles, optional `phy_nocsr` reset, selected PCIe submode, fixed-rate clock providers, and the optional TCSR four-lane-selection result.
- The large static `qmp_phy_init_tbl` families provide SoC and generation-specific register programming for MSM8998, IPQ6018/IPQ8074/IPQ9574, QCS615/QCS8300, SDM845 QMP/QHP, SC8180X/SC8280XP, SDX55/SDX65, SM8250/SM8350/SM8450/SM8550/SM8650/SM8750, SA8775P, SAR2130P, X1E80100/X1P42100, Glymur, and Kaanapali.
- `qmp_pcie_of_match_table` is the external binding surface. Each compatible maps directly to one `qmp_phy_cfg`.

### Control Flow
Probe allocates `qmp_pcie`, loads match data, obtains optional bulk clocks (`aux`, `cfg_ahb`, `ref`, `refgen`, `rchng`, `phy_aux`), reset controls, optional regulators, then parses either legacy child-node resources or the modern single resource window. Modern parsing applies `qmp_pcie_offsets` to derive all sub-block bases, reads optional `qcom,4ln-config-sel` through syscon/regmap, maps a second resource for port B when a four-lane split is selected, and obtains `pipe` plus optional `pipediv2` clocks. Legacy parsing maps child resources by index and carries special handling for SDM845 QHP and IPQ6018 PCS_MISC.

Power-on is split across generic PHY callbacks. `qmp_pcie_enable()` calls `qmp_pcie_init()` and then `qmp_pcie_power_on()`. Init may skip table programming when an optional `phy_nocsr` reset exists and boot firmware already left `SERDES_START | PCS_START` plus the expected power-down bits set. Otherwise it enables regulators, asserts/deasserts BCR resets around `phy_nocsr`, and enables the required bulk clocks. Power-on sets power-down bits, applies the common tables followed by RC or EP mode tables selected by `qmp_pcie_set_mode()`, enables pipe clocks, deasserts `phy_nocsr`, clears software reset, starts SERDES/PCS, optionally waits 1 ms, then polls PCS status until the configured `PHYSTATUS` bit clears or `PHY_INIT_COMPLETE_TIMEOUT` expires.

Four-lane handling is conditional: for configurations with at least four lanes and a true TCSR four-lane select bit, `qmp_pcie_init_registers()` applies the four-lane SERDES patch and calls `qmp_pcie_init_port_b()` to program lanes 3 and 4 through the second port's windows. Lane-specific table entries use `qmp_configure_lane()`, so lane masks embedded in `QMP_PHY_INIT_CFG_LANE()` determine which writes apply to each lane.

Power-off disables pipe clocks and, when there is no no-CSR reset preservation path, asserts SW reset, clears start bits, and clears power-down bits. Exit asserts `phy_nocsr` if present, otherwise asserts the bulk resets, then disables bulk clocks and regulators.

### State And Persistence
The driver persists no data outside device-managed kernel resources and hardware registers. Runtime state is held in `struct qmp_pcie` and is recreated on probe. Hardware state may persist across power cycles or bootloader handoff when `phy_nocsr` is present; the `skip_init` path intentionally preserves PHY programming across power-off/on cycles by avoiding register deinitialization when no-CSR reset support exists. The selected `mode` defaults to `PHY_MODE_PCIE_RC` and is updated only through `.set_mode`.

### Dependencies And Integration Points
The file integrates with the platform driver bus, device tree match data, generic PHY APIs, Linux clock provider APIs, bulk regulator/reset/clock frameworks, `syscon_regmap_lookup_by_phandle_args()` for four-lane routing, and shared Qualcomm QMP helpers from `phy-qcom-qmp-common.h` and `phy-qcom-qmp.h`. It depends heavily on versioned QSERDES/PCS register header macros, including the PCIe PCS headers in this subset. Downstream PCIe controller drivers consume the PHY through OF PHY lookup and pipe/aux clocks through the registered clock provider.

### Risks
The primary risk is table correctness: a wrong register macro, value, lane mask, or compatible-to-config mapping can cause silent link instability or PHY init timeouts. Resource-layout drift between legacy and modern device-tree bindings can map PCS_MISC, PCS_LANE1, or secondary lanes incorrectly. The bootloader handoff path is sensitive because `skip_init` trusts a small set of status bits as evidence that all required analog programming is valid. RC/EP overrides are sparse and may leave unset table families intentionally; a new SoC must ensure the base plus mode-specific tables compose correctly. Four-lane TCSR routing must match board wiring, or the driver may program the wrong port topology. Generated clock rates default to 125 MHz pipe unless overridden, with 20 MHz aux used only by selected configs.

### Test Signals
Useful signals include successful probe with all named clocks/resets/regulators resolved, clock provider registration from `clock-output-names`, successful `set_mode` for both RC and EP where supported, no `Init sequence not available` errors, no reset/regulator enable failures, and no `phy initialization timed-out` messages. Hardware validation should include PCIe link training at supported generations and lane widths, suspend/resume or repeated power-cycle tests to cover the `phy_nocsr` skip path, endpoint-mode boards for configs with `tbls_ep`, and four-lane designs that exercise `qcom,4ln-config-sel` and port B programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v6.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v6.h

This header defines the QMP V6 PCS_AON register offset surface. It exports one guarded macro, `QPHY_V6_PCS_AON_CLAMP_ENABLE` at `0x00`, for always-on PCS clamp control. There are no functions, runtime control flow, or persisted software state; integration is by inclusion from PHY drivers that need to write or read the V6 always-on PCS block through an MMIO base. Its dependencies are limited to C preprocessing, include guards, and the GPL-2.0 license marker. The risk is offset accuracy: a wrong clamp offset can break low-power isolation or retention behavior on hardware using the AON block. Test signals are compile coverage from including drivers and hardware suspend/resume or power-collapse tests that exercise clamp enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v8.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v8.h

This header maps QMP V8 PCS_AON offsets for multi-protocol always-on control. It defines USB3 and USB4 clamp registers, USB3/USB4/DP toggle-enable registers, and a dummy status register from `0x00` through `0x14`. There are no functions or mutable software state; the important API is the macro namespace `QPHY_V8_PCS_AON_*`, consumed by QMP PHY drivers that calculate register addresses from a PCS_AON base. Dependencies are only include guards and the shared Qualcomm register-naming convention. Integration risk is protocol mix-up: using the USB4 or DP toggle offset for USB3, or vice versa, could leave the wrong lane island clamped or toggled. Test signals include successful compilation of users and hardware validation of USB3, USB4, DisplayPort, and low-power transitions on V8 PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-aon-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v3.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v3.h

This header defines QMP V3 PCS_MISC offsets used by PCIe-oriented PCS programming. Its macro API covers clamp enable, oscillator-detect configuration, PCIe internal AUX clock configuration, and mode-2 oscillator-detect configuration registers. It has no functions, branching, persistence, or direct hardware access; it is a stable register map consumed by init tables such as the SDM845 QMP PCIe PCS_MISC table in `phy-qcom-qmp-pcie.c`. Dependencies are the include guard and convention that drivers add these offsets to a mapped PCS_MISC base. Risks are stale offsets or naming mismatches that make table entries write the wrong V3 PCS_MISC location, affecting oscillator detection, AUX-clock behavior, and clamp control. Test signals include build coverage plus link bring-up and low-power-state entry/exit on V3 PCIe PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v4.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v4.h

This header provides QMP V4 PCS_MISC offsets for Type-C control/status, generic PCS_MISC config, clamp enable, and placeholder status registers. It is a macro-only register map with no runtime code or software-owned state. Drivers integrate it by including the header and using `QPHY_V4_PCS_MISC_*` macros in init tables or direct MMIO operations against a PCS_MISC base. The file depends only on C preprocessor include guards. The main risk is offset collision between Type-C control and clamp/config registers, because incorrect writes may alter connector orientation, power-down, or clamp behavior. Test signals are compile coverage and hardware tests that exercise Type-C orientation, PHY low-power entry, and wake from clamped states on V4 designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v5.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v5.h

This compact header exports the QMP V5 PCS_MISC clamp-enable offset, `QPHY_V5_PCS_MISC_CLAMP_ENABLE` at `0x0c`. It contains no functions, state, or control flow. Its integration point is any QMP V5 PHY driver that controls PCS_MISC clamp behavior by adding this macro to a mapped PCS_MISC base. Dependencies are limited to include guards and register naming conventions. The risk is narrow but hardware-visible: incorrect clamp-enable addressing could break isolation during power collapse or resume. Test signals include compilation of any V5 PCS_MISC user and suspend/resume or PHY power-cycle validation where clamp control is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v8.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v8.h

This header defines a QMP V8 PCS_MISC config offset, `QPHY_V8_PCS_MISC_PCS_MISC_CONFIG1` at `0x08`. It is macro-only and contains no runtime behavior, state, or persistence. It integrates with V8 QMP PHY drivers that program a PCS_MISC base as part of init or mode switching. The only dependency is inclusion by C code that understands the V8 PCS_MISC block. The risk is that a single bad offset can silently program the wrong PCS_MISC register on V8 hardware. Test signals are successful builds and hardware bring-up paths that apply V8 PCS_MISC configuration, especially mode changes and low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-misc-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4.h

This header is the QMP V4 PCIe PCS register map. It exports offsets for power-state configuration, TX/RX PCS configuration, endpoint refclk drive/control, EP clock delays, idle detect and signal detect control, L1.1/L1.2 wake timing, internal AUX clock and oscillator-detect configuration, local FS/LF values, equalization configuration, preset pre/post cursor values, and RX equalization evaluation time. It has no functions or software state; its APIs are the `QPHY_V4_PCS_PCIE_*` macros used by PCIe PHY init tables such as IPQ6018, IPQ8074 Gen3, SDM845, SC8180X, and SM8250 entries in the PCIe driver. Dependencies are the mapped PCS_MISC/PCIe PCS base and the shared QMP init-table writer. Risks include register layout confusion with later V4.20/V5 variants, especially around EQ and preset offsets. Test signals include Gen1-Gen3 link training, L1 substate wake latency, endpoint refclk behavior, and no PHY init timeout after tables using these macros are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4_20.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4_20.h

This header defines the QMP V4.20 PCIe PCS offsets used by SDX55-era style PHY layouts. Its macro API includes endpoint refclk drive, oscillator-detect actions, EQ config, Gen3 and Gen4 RXEQ evaluation times, Gen4 EQ configuration, and lane1 INSIG software/mux controls. There is no executable code or persisted state. It integrates with the PCIe driver's V4.20 init tables and optional endpoint lane1 table, where the macros are consumed by `qmp_configure()` and `qmp_configure_lane()`. The main risks are variant drift from base V4 offsets and the `PCS_LANE1` window relationship under legacy bindings. Test signals include SDX55 link training, Gen4 equalization, endpoint-mode lane1 behavior, and successful PCS status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v4_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5.h

This header is the base QMP V5 PCIe PCS offset map. It defines power-state, endpoint refclk, L1.1/L1.2 wake, AUX clock, oscillator-detect, EQ, and preset P10 pre/post offsets. It contains no functions, no branching, and no software persistence. The macros are used by PCIe PHY tables for IPQ9574, SC8280XP, SM8350/SM8450 Gen3, and related V5 configurations. Integration depends on drivers selecting the correct `qmp_pcie_offsets` layout and adding these offsets to PCS_MISC/PCIe PCS bases. Risks are mostly variant confusion with V5.20 and later V6 offsets; incorrect power-state or EQ offsets can produce link instability or failed low-power states. Test signals include successful Gen3 link training, L1 substate behavior, and no timeout in `qmp_pcie_power_on()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5_20.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5_20.h

This header maps QMP V5.20 PCIe PCS registers, including power-state config, endpoint refclk, oscillator-detect actions, EQ config, P10 post preset, Gen3/Gen4 RXEQ evaluation times, Gen4 EQ/pre-gain, RX margining, and lane1 INSIG controls. It is a macro-only API with no runtime state. The PCIe driver uses these offsets for SDX65, SM8450/SM8550 Gen4, SA8775P, QCS8300, and other V5.20-style PHYs. Dependencies are the shared QMP init-table macros and correct PCS/PCS_LANE1 base mapping. Risks include the `QPHY_PCIE_V5_20_PCS_*` naming mix alongside `QPHY_V5_20_PCS_PCIE_*`, which can make table review error-prone, and variant drift from V6.20. Test signals include Gen4 equalization, RX margining capability, endpoint/refclk behavior, and lane1 INSIG programming on two-lane endpoint designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v5_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6.h

This header defines QMP V6 PCIe PCS offsets for EQ config, RXEQ evaluation, power-state config, endpoint refclk drive, oscillator-detect actions, and lane1 INSIG controls. It has no functions or persistence. The macros are consumed by V6 PCIe init tables, notably SM8550/SM8750 Gen3-style PCS_MISC programming and SAR2130P lane1 control. Dependencies are the QMP PCIe driver's selected PCS base and shared table writer. Risks include mixing this base V6 header with V6.20/V6.30 layouts; the same semantic register names may live at different offsets. Test signals are Gen3 link-up, lane1 endpoint behavior where used, and stable power-state transitions with no PHY init timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_20.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_20.h

This header provides QMP V6.20 PCIe PCS offsets for power-state, TX/RX config, endpoint refclk, oscillator-detect actions, EQ, Gen3/Gen4 RXEQ timing, Gen4 EQ/pre-gain, RX margining, and Gen3/Gen4 figure-of-merit EQ controls. It is macro-only and has no runtime state. It integrates with SM8550/SM8650 and X1E80100 Gen4x2/x4 tables in the PCIe driver. One notable risk is the macro spelling `QPHY_PCIE_V6_20_PCS_OSC_DTCT_ATCIONS`, which is consistently used by the driver but is typo-prone for new code. Other risks are offset drift from V5.20 and V6.30. Test signals include Gen4 equalization, RX margining, FOM programming, and successful repeated power-on polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_30.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_30.h

This header maps QMP V6.30 PCIe PCS offsets. It covers power-state, TX/RX config, endpoint refclk drive, oscillator-detect actions, EQ config, Gen3/Gen4 RXEQ timing, Gen4 EQ/pre-gain, RX margining, and Gen3/Gen4 FOM EQ controls. There are no functions, branches, or persisted values. It integrates with X1E80100 Gen4x8-style tables that use the V6.30 PCS and PCS_MISC layout with TXZ/RXZ and lane-shared blocks. Risks are high-impact because V6.30 offsets differ from V6.20; applying the wrong variant can corrupt unrelated PCS registers. Test signals include x8 lane bring-up, Gen4 equalization across all active lanes, RX margining, and correct behavior when `txz`/`rxz` tables are applied before regular TX/RX overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v6_30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v8.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v8.h

This header defines QMP V8 PCIe PCS offsets for power-state, TX/RX config, endpoint refclk, oscillator-detect, EQ, Gen3/Gen4 RXEQ timing, Gen4 pre-gain, TX de-emphasis, RX margining, signal detect, electrical-idle delay, power-state config6, and extended EQ config. It has no executable logic or software state. It is used by the Kaanapali V8 Gen3x2 PCIe tables in the PCIe driver and by any future V8 PCIe PHY users. Dependencies are the QMP table writer and correct V8 PCS base mapping. Risks include formatting/naming inconsistency that can obscure review and variant confusion with V8.50, whose generic PCS layout omits several offsets. Test signals include V8 link training, RX margining, electrical idle behavior, and successful PHY status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-pcie-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-sgmii.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-sgmii.h

This header defines QMP PCS offsets for SGMII PHY use. The macro API covers PHY start, power-down, software reset, line reset timing, TX large/small amplitude levels, PCS ready status, mid-term TX controls, and SGMII misc control. It has no functions, state, or control flow. It integrates with SGMII-specific Qualcomm QMP PHY drivers rather than the PCIe driver in this subset. Dependencies are only the preprocessor guard and consumers that add these offsets to a PCS base. Risks are wrong-ready-status or reset offsets, which can cause false bring-up success or stuck reset. Test signals include SGMII link establishment, PCS ready polling, reset sequencing, and amplitude tuning validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-sgmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v2.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v2.h

This header maps QMP V2 UFS PCS offsets. It defines PHY start, power-down control, TX amplitude and post-emphasis levels, RX stall/resync/min-Hibern8/signal-detect/PWM gear controls, and ready status. It contains no functions or software-managed state. UFS QMP PHY drivers integrate it through register init tables and readiness polling against a mapped PCS base. Dependencies are the include guard and shared register naming conventions. Risks include breaking UFS Hibern8 timing, PWM/HS gear behavior, or ready-status polling if offsets are wrong. Test signals include UFS PHY init, link startup, gear negotiation, Hibern8 entry/exit, and ready-status timeout absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v3.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v3.h

This header defines QMP V3 UFS PCS offsets for PHY start, power-down, TX amplitudes, RX symbol resync, min-Hibern8, signal-detect controls, ready status, TX mid-term control, and multi-lane control. It has no runtime behavior or persisted state. UFS PHY drivers consume these macros in init tables or direct register sequences. Dependencies are only compile-time inclusion and the mapped PCS base. Risks focus on Hibern8 timing, signal-detect setup, and multi-lane enablement. Test signals include UFS link startup, multi-lane operation, Hibern8 cycles, and successful ready-status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v4.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v4.h

This header is the QMP V4 UFS PCS register map. It exports offsets for start, power-down, software reset, 20 us core-clock timers, PLL control, TX amplitude, BIST fixed pattern control, TX/RX HS gear capability, debug bus clock select, linecfg disable, min-Hibern8, signal detect, PWM/HS gear band, ready status, TX mid-term control, and multi-lane control. It contains no functions or persistent software state. Integration is through UFS QMP PHY init tables and status polling. Risks include wrong timer or gear capability offsets, which can create subtle UFS link and power-management failures. Test signals include UFS gear negotiation, BIST where supported, Hibern8, line configuration, and ready-status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v5.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v5.h

This header provides QMP V5 UFS PCS offsets. Its macro API mirrors the V4-era UFS control surface with start, power-down, reset, timers, PLL control, TX amplitudes, BIST, HS gear capability, debug bus, RX min-Hibern8 and signal detect, gear band controls, ready status, TX mid-term control, and multi-lane control. There is no executable logic or state. UFS PHY drivers integrate it by selecting V5 macros in generation-specific init tables. Risks are variant drift from V4 and V6, especially around RX signal-detect and gear-band offsets. Test signals include UFS link startup at supported gears, Hibern8 cycles, multi-lane behavior, and ready-status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v6.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v6.h

This header maps QMP V6 UFS PCS registers. In addition to start, power-down, reset, timers, PLL, amplitudes, BIST, gear capability, debug bus, linecfg, Hibern8, signal detect, gear band, ready status, TX mid-term, and multi-lane control, it adds UFS HS-G5 capability/sync wait and TX post-emphasis level S4-S7 offsets. It is macro-only and has no software persistence. Integration is through newer UFS QMP PHY drivers that support V6 and UFS 4.x/HS-G5 features. Risks include incorrect HS-G5 sync/post-emphasis offsets causing high-speed-only failures while lower gears appear stable. Test signals include HS-G5 negotiation where supported, Hibern8, multi-lane operation, post-emphasis tuning, and ready-status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-ufs-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v4.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v4.h

This header defines QMP V4 USB3 PCS offsets. It covers power-state config, autonomous mode status/control, LFPS RX termination IRQ status/clear, LFPS timing and TX values, RX equalization training timing, receiver-detect delays, arc receiver detect timing, TX ones/zeros run length, ALFPS deglitch, signal-detect startup timer, and test control. It has no runtime code or state. USB QMP PHY drivers consume these macros in init sequences and low-power/autonomous-mode management. Risks include broken LFPS, receiver detect, or RXEQ timing if offsets are wrong. Test signals include USB3 connect/disconnect, U1/U2/U3 transitions, LFPS wake, RXEQ training, and test-mode coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v5.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v5.h

This header maps QMP V5 USB3 PCS offsets. It is similar to the V4 USB map but shifts several registers and adds LFPS config1 plus RX termination delay select. The macro API covers autonomous mode, LFPS IRQ/timing, RXEQ training, receiver detect, ALFPS deglitch, signal-detect startup, test control, and termination delay. There is no executable logic or persisted state. Integration is through USB QMP PHY init and power-management sequences. Risks are variant confusion with V4/V6 because the same semantic controls move by small offsets. Test signals include USB3 link bring-up, LFPS wake, receiver detection, RXEQ training, termination timing, and low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v6.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v6.h

This header exports a reduced QMP V6 USB3 PCS offset set for power-state config, autonomous mode control, LFPS RX termination IRQ clear, LFPS high-count value, RXEQ DFE time, and receiver-detect delay low/high registers. It is macro-only with no state or control flow. USB PHY drivers include it when their V6 tables need these PCS controls. Risks are missing or wrong offsets for low-power wake and receiver-detect timing. Test signals include USB3 attach/detach, LFPS wake handling, RXEQ training, receiver detect timing, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v7.h -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v7.h

This header defines the QMP V7 USB3 PCS offsets for the same compact control set as V6: power-state config, autonomous mode control, LFPS RX termination IRQ clear, LFPS high-count value, RXEQ DFE time, and receiver-detect delay low/high registers. It has no runtime behavior, persistence, or direct dependencies beyond the include guard and consumer drivers. Integration is through V7 USB QMP PHY tables. Risks are variant confusion with V6 because the exported names and offsets currently align closely, making copy-paste changes easy to miss when hardware diverges. Test signals include USB3 bring-up, LFPS wake, RXEQ training, receiver detection, and suspend/resume on V7 PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v7.h -->
