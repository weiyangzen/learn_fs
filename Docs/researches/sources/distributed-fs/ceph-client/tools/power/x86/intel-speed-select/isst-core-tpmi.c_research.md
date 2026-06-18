# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-tpmi.c

## Purpose
`isst-core-tpmi.c` implements the `struct isst_platform_ops` backend for TPMI-based Intel Speed Select platforms, used by API versions 2 and 3. It maps generic SST operations onto typed `linux/isst_if.h` ioctl payloads for performance levels, base frequency, turbo frequency, core-power state, CLOS parameters, CLOS association, and TPMI instance discovery.

## Important APIs, Types, And Functions
The exported entry point is `tpmi_get_platform_ops()`, returning `tpmi_ops`. `tpmi_process_ioctl()` is the common ioctl helper and debug printer. Feature readers include `tpmi_read_pm_config()`, `tpmi_get_config_levels()`, `tpmi_get_ctdp_control()`, `tpmi_get_tdp_info()`, `tpmi_get_pwr_info()`, `tpmi_get_coremask_info()`, `tpmi_get_get_trls()`, `tpmi_get_trl_bucket_info()`, `tpmi_get_pbf_info()`, `tpmi_get_fact_info()`, `tpmi_get_clos_information()`, `tpmi_pm_get_clos()`, and `tpmi_clos_get_assoc_status()`. Mutators include `tpmi_set_tdp_level()`, `tpmi_set_pbf_fact_status()`, `tpmi_adjust_uncore_freq()`, `tpmi_pm_qos_config()`, `tpmi_set_clos()`, and `tpmi_clos_associate()`.

## Control Flow
Every public operation fills a kernel ABI structure with `socket_id` and `power_domain_id` from `struct isst_id`, then calls `tpmi_process_ioctl()`. Performance-level reads start with `ISST_IF_PERF_LEVELS` to populate package-level state and then use `ISST_IF_GET_PERF_LEVEL_INFO` and related mask/fabric ioctls for level details. Feature enable/disable writes call `ISST_IF_PERF_SET_FEATURE`, then poll `isst_get_ctdp_control()` up to five times to confirm the requested PBF or FACT state. Core-power and CLOS setters intentionally loop across all valid punit instances in the package because the code treats those settings as package-scoped.

## State And Persistence Behavior
This file has little internal state; `tpmi_update_platform_param()` is currently a no-op. Hardware state changes occur through TPMI ioctl set operations for performance level, feature state, core-power enable/type, CLOS parameters, and CLOS associations. `tpmi_adjust_uncore_freq()` reads TPMI fabric frequencies, then `_set_uncore_min_max()` scans `/sys/devices/system/cpu/intel_uncore_frequency/` for entries with matching `domain_id` and `package_id` and writes min/max frequency files.

## Dependencies And Integration Points
The file depends on `/dev/isst_interface`, the TPMI-capable `linux/isst_if.h` ABI, topology helpers from `isst-config.c`, common validation and wrapper logic from `isst-core.c`, and display/error helpers. Unlike the mailbox backend, frequency values are exposed in MHz and `tpmi_get_disp_freq_multiplier()` returns 1. TRL levels are named `level-0` through `level-7`.

## Risks And Edge Cases
The backend returns `-1` for many ioctl failures without detailed errno propagation, so callers generally get generic command failure. `tpmi_get_get_trl()` has a `FIX ME` and always returns level 0 ratios, which can hide requested-level differences. `tpmi_get_pwr_info()` is a stub that reports zero min/max power. API version differences affect how PBF/FACT support bits are interpreted. Package-wide loops temporarily mutate `id->punit` and must restore it on all paths. Uncore sysfs discovery skips entries whose metadata cannot be read, and failures are mostly silent.

## Test Signals
Important tests include ioctl payload construction for each operation, API v2 versus v3 support-mask handling, valid-mask filtering in `tpmi_is_punit_valid()`, package-wide CLOS/core-power loops, feature enable polling success and timeout, punit CPU mask conversion, and uncore sysfs matching by package/domain ids. Regression tests should pin the known `tpmi_get_get_trl()` level-0 behavior until fixed.
