# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core.c

## Purpose
`isst-core.c` is the backend-neutral core layer for Intel Speed Select operations. It selects the platform ops table, validates callback availability, exposes wrapper functions for the CLI and daemon, performs common feature validation, owns shared MSR helper operations, and assembles full processed `isst_pkg_ctdp` data by combining level, PBF, FACT, power, core-mask, bucket, and TRL information.

## Important APIs, Types, And Functions
The central state is the static `struct isst_platform_ops *isst_ops`. `isst_set_platform_ops()` selects mailbox ops for API version 1 and TPMI ops for API versions 2 and 3. `CHECK_CB()` enforces callback presence. Nearly every public `isst_*` function delegates to the selected backend: `isst_read_pm_config()`, `isst_get_ctdp_levels()`, `isst_get_ctdp_control()`, `isst_get_tdp_info()`, `isst_get_pwr_info()`, `isst_get_coremask_info()`, `isst_get_pbf_info()`, `isst_get_fact_info()`, CLOS helpers, and feature setters. Shared MSR operations include `isst_send_msr_command()`, `isst_get_trl()`, `isst_set_trl()`, `isst_set_trl_from_current_tdp()`, and `isst_get_config_tdp_lock_status()`.

## Control Flow
The CLI calls `isst_set_platform_ops()` during initialization. Subsequent commands use wrapper APIs, so command code is independent of mailbox versus TPMI details. `isst_get_process_ctdp()` is the primary aggregation flow: read package levels, validate the requested level, iterate each applicable TDP level, fetch control state, optionally fetch PBF and FACT details, apply SKX fallback when perf-profile is not enabled, otherwise fetch TDP, power, core mask, TRL bucket, and TRL ratio data. `isst_get_process_ctdp_complete()` frees cpumasks allocated during that aggregation.

## State And Persistence Behavior
Internal persistent process state is just the selected ops pointer. Host state changes are delegated to backends or the MSR helper. `isst_set_trl()` writes MSR 0x1AD, defaulting zero input to all-ones. `isst_set_trl_from_current_tdp()` can reconstruct MSR TRL values from the current TDP level and account for mailbox versus TPMI frequency units. `isst_get_config_tdp_lock_status()` reads MSR 0x64b bit 31.

## Dependencies And Integration Points
The file is the integration point between `isst-config.c` command flows and the backend implementations. It also uses display helpers for validation failures, topology/cpufreq helpers for fallback behavior, and `/dev/isst_interface` with `ISST_IF_MSR_COMMAND` for MSR access. Its data structures are declared in `isst.h`.

## Risks And Edge Cases
`CHECK_CB()` exits the process on invalid ops instead of returning an error, so initialization order matters. Some wrapper functions allocate cpumasks before backend calls; callers must free them on success paths, and some error paths can be hard to audit. `isst_get_process_ctdp()` continues past some level-control failures but returns immediately for later fetch failures, so partial data behavior differs by stage. The SKX fallback path uses cpufreq base frequency and MSR TRL when perf-profile is disabled. Frequency unit conversion for TRL writes is subtle because mailbox ratios use 100 MHz units while TPMI reports MHz.

## Test Signals
Tests should cover ops selection by API version, invalid API rejection, callback guard behavior, MSR command packing, PBF/FACT level validation, `isst_get_process_ctdp()` with all-level and single-level requests, SKX disabled-perf-profile fallback, cpumask allocation/free expectations, and TRL conversion in `isst_set_trl_from_current_tdp()`.
