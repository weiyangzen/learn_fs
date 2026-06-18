# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.h

## Purpose
This header declares the BTC DPM helper interface and BTC-specific default constants used by Radeon dynamic power management code. It is the small public surface shared between `btc_dpm.c`, later Northern Islands/Southern Islands DPM implementations, and Radeon ASIC hook declarations.

## Important APIs, Types, and Functions
It includes `radeon.h` and `rv770_dpm.h` for the core device, power-state, and RV770 power-level types. Constants define default UVD activity thresholds (`BTC_RLP_UVD_DFLT`, `BTC_RMP_UVD_DFLT`, `BTC_LHP_UVD_DFLT`, `BTC_LMP_UVD_DFLT`), per-family MGCG control defaults for Barts, Turks, and Caicos, and CG ULV register defaults.

The exported data and helpers are `btc_valid_sclk`, `btc_read_arb_registers`, `btc_program_mgcg_hw_sequence`, `btc_skip_blacklist_clocks`, `btc_adjust_clock_combinations`, `btc_apply_voltage_dependency_rules`, `btc_get_max_clock_from_voltage_dependency_table`, `btc_apply_voltage_delta_rules`, `btc_dpm_enabled`, `btc_reset_to_default`, and `btc_notify_uvd_to_smc`.

## Control Flow
The header has no executable control flow. It lets BTC implementation code expose reusable policy helpers for clock validation, voltage dependency enforcement, hardware register-sequence programming, SMC status/reset, arbitration register capture, and UVD state notification.

## State and Persistence Behavior
The header itself stores no state, but it exposes `btc_valid_sclk` as a global valid clock table and declares functions that mutate hardware registers, SMC soft registers, memory arbitration snapshots, and `rdev->pm.dpm` power-state data. The constants are compile-time policy inputs used to initialize persistent runtime power-management state.

## Dependencies and Integration Points
This header is included by `btc_dpm.c` and `ni_dpm.h`; BTC helper declarations are also referenced by NI and SI DPM code for shared clock and voltage rules. Consumers must already use Radeon DPM structures from `radeon.h` and `rv770_dpm.h`.

## Risks
Any signature drift here breaks cross-family DPM builds. Because helpers declared here are shared with later ASICs, BTC-specific assumptions in clock or voltage rules can have broader impact. The global `btc_valid_sclk` table is mutable because it is declared as `u32[]`, so accidental writes by a consumer would affect all later clock validation.

## Test Signals
Build coverage across BTC, NI, and SI DPM code is the first signal. Runtime coverage should include clock/voltage adjustment paths, UVD enable/disable notification, SMC reset/default paths, and register-sequence programming on supported BTC hardware.
