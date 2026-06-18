# sources/distributed-fs/ceph-client/drivers/clk/qcom/common.c

## Purpose
Provides shared helper code for Qualcomm clock-controller drivers. It supplies frequency-table lookup helpers, parent-map lookup helpers, MMIO-to-regmap mapping, PLL FSM configuration, board clock compatibility registration, protected-clock filtering, interconnect clock registration, PLL/CBCR preconfiguration, reset/GDSC registration, common-clock registration, and generic probe wrappers used by many qcom clock controllers.

## Important APIs, Types, And Functions
- `struct qcom_cc` is the runtime container for reset controller state, registered `clk_regmap` array, clock count, and attached power-domain list.
- `qcom_find_freq`, `qcom_find_freq_multi`, and `qcom_find_freq_floor` select frequency table entries at or above a requested rate, multi-table equivalent, or floor entry.
- `qcom_find_src_index` and `qcom_find_cfg_index` map between hardware parent source/config values and common-clock parent indexes.
- `qcom_cc_map`, `qcom_cc_probe`, and `qcom_cc_probe_by_index` create an MMIO regmap and call `qcom_cc_really_probe`.
- `qcom_cc_really_probe` is the central controller-registration path for resets, GDSCs, DFS RCGs, hardware clocks, regmap clocks, OF provider, interconnect clocks, RPM runtime-PM, protected clocks, and optional driver-data initialization.
- `qcom_cc_register_board_clk` and `qcom_cc_register_sleep_clk` preserve compatibility with old DTs by creating fixed-rate and fixed-factor board clocks.

## Control Flow
A SoC-specific driver builds a `qcom_cc_desc` and calls `qcom_cc_probe`. The common path maps registers, allocates `qcom_cc`, attaches optional PM domains, resumes RPM-backed devices if requested, configures PLLs and critical CBCRs from `qcom_cc_driver_data`, registers the reset controller, registers GDSCs with cleanup, registers DFS RCGs, drops clocks listed in `protected-clocks`, registers standalone `clk_hw`s and `clk_regmap`s, adds the OF clock provider, and optionally registers interconnect clock nodes. On errors after RPM runtime get, the `put_rpm` path releases the runtime-PM reference.

## State And Persistence
Runtime state persists in devm-managed `qcom_cc`, reset controller registration, GDSC registrations, OF provider data, and optional interconnect clock data. Hardware state is changed by PLL configuration, CBCR enable writes, reset operations, GDSC power-domain operations, and optional driver-specific register configuration. Protected clocks are represented by setting entries in the runtime `rclks` table to NULL so the provider hides them.

## Dependencies And Integration Points
The file depends on regmap, platform MMIO resources, common clock framework, reset-controller core, Qualcomm reset/GDSC/branch/RCG/alpha PLL helpers, interconnect-clk support, PM runtime, OF properties, and generic device-managed cleanup. It is the integration point for most qcomcc SoC driver files, including the display controllers in this subset.

## Risks And Edge Cases
`protected-clocks` silently nulls entries, so downstream consumers must tolerate provider NULLs for firmware-owned clocks. PLL driver data requires both config and register layout; missing fields abort probe. RPM runtime handling must balance resume-and-get with put on every path. Interconnect clock registration depends on valid clock IDs in `icc_hws`. Board-clock compatibility code can create synthetic clock names only when old DT nodes are absent. Registration order matters because GDSCs and resets share the same regmap and reset controller.

## Test Signals
Test signals include frequency helpers selecting first/fastest/floor entries correctly, invalid parent lookups returning `-ENOENT`, failed MMIO/regmap mapping propagating errors, protected clocks disappearing from OF lookup, reset and GDSC registration succeeding, PLL/CBCR initialization writes occurring before clock registration, RPM runtime refs balanced on probe failure, and interconnect clock registration guarded by `CONFIG_INTERCONNECT_CLK`.
