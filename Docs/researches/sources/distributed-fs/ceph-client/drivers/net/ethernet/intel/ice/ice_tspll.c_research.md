# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.c

Purpose: programs and validates the Clock Generation Unit TSPLL used by PTP and SyncE-capable Intel ice devices. It handles E82x style MACs and E825-C style MACs with different register layouts, lock-status registers, and recovered-clock controls.

Important APIs and functions: `ice_tspll_init()` is the exported initialization entry point. It reads firmware function capabilities, validates `time_ref` and `clk_src`, disables sticky lock bits, programs TSPLL, and retries with TCXO/default frequency on failure. `ice_tspll_cfg_pps_out_e825c()` controls 1PPS output amplitude/enable. `ice_tspll_bypass_mux_active_e825c()`, `ice_tspll_cfg_bypass_mux_e825c()`, and `ice_tspll_cfg_synce_ethdiv_e825c()` manage E825-C SyncE bypass mux and divider state. Static helpers provide frequency/source names, default frequency, parameter checking, per-MAC TSPLL programming, sticky-bit programming, and link-speed-to-divider mapping.

Control flow: initialization exits early for unsupported MACs. For supported MACs, firmware capability values are checked against valid ranges and MAC/source restrictions. E82x programming disables PLL, writes R9/R19/R22/R24 using table-driven divisors, reenables PLL, waits, and checks `ICE_CGU_RO_BWM_LF_TRUE_LOCK`. E825-C programming disables PLL and time sync, enables the selected input receiver, writes fixed E825 divisors and source selection, clears R24, reenables PLL, waits, and checks `ICE_CGU_RO_LOCK_TRUE_LOCK`.

State and persistence: state is hardware register state in the CGU, not heap state. The code persists selected clock source, frequency, divisors, enable bits, lock-status mode, 1PPS output, bypass mux source, and SyncE dividers in device registers. `hw->func_caps.ts_func_info`, `hw->mac_type`, `hw->ptp.ports_per_phy`, and current link speed guide programming.

Dependencies and integration: uses `ice_read_cgu_reg()` and `ice_write_cgu_reg()` from PTP hardware support, CGU register/mask definitions, `ice_hw_to_dev()` logging, firmware capabilities from `ice_type.h`, and link speed constants from AQ definitions. SyncE calls are documented as running under `pf->dplls.lock`.

Risks: incorrect frequency/source combinations can fail PLL lock or produce invalid PTP timing. Register sequences are MAC-specific and order-sensitive. E825-C mux selection uses `port_num + ICE_CGU_BYPASS_MUX_OFFSET_E825C`, so invalid port numbering would select the wrong recovered clock. Link speeds without a divider mapping return `-EOPNOTSUPP`.

Test signals: test on E82x/E825-C hardware with firmware-provided TIME_REF and TCXO configs, confirm lock success and fallback behavior, verify warnings on invalid capability values, check 1PPS output, recovered clock mux active reporting, divider programming across supported link speeds, and PTP/SyncE stability after reset or link changes.
