# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_hwmgr.c

## Purpose

`goya_hwmgr.c` implements Goya power/clock management sysfs attributes and PLL profile programming. It exposes current and target MME/TPC/IC clocks, high PLL setting, automatic/manual PM mode, and Infineon VRM firmware version attributes through device attribute groups.

## Important APIs, Types, And Data

- `goya_set_pll_profile()` programs MME, TPC, and IC PLLs to `PLL_HIGH`, `PLL_LOW`, or saved `PLL_LAST` values through `hl_fw_set_frequency()`.
- Per-clock sysfs show/store handlers exist for `mme_clk`, `tpc_clk`, and `ic_clk`; current-frequency read-only handlers use `hl_fw_get_frequency(..., true)`.
- `pm_mng_profile_show()` and `pm_mng_profile_store()` expose `auto` and `manual` PM modes.
- `high_pll_show()` and `high_pll_store()` expose `hdev->high_pll`.
- `infineon_ver_show()` reports the CPU-CP-provided `cpucp_info.infineon_version`.
- `goya_add_device_attr()` assigns Goya clock and VRM attribute arrays into caller-provided `attribute_group` objects.

## Control Flow

Clock show handlers first call `hl_device_operational()` and then read firmware PLL frequency; negative firmware return values are forwarded as errors. Clock store handlers require an operational device, reject changes while `goya->pm_mng_profile == PM_AUTO`, parse the input with `kstrtoul()`, call `hl_fw_set_frequency()`, and cache the requested value in `goya->mme_clk`, `goya->tpc_clk`, or `goya->ic_clk`.

PM mode switching is guarded by `hdev->fpriv_list_lock`. The store path rejects profile changes while a compute context is active. Switching from manual to auto forces low PLL by setting `curr_pll_profile` to high, setting PM mode to auto, and calling `goya_set_frequency(PLL_LOW)`. Switching from auto to manual sets PM mode under the lock, releases the lock, flushes the delayed frequency work if it exists, and returns so the caller knows auto work is no longer racing frequency changes. Unknown values return `-EINVAL`.

`goya_set_pll_profile()` itself is a direct firmware-programming helper and intentionally returns early if `hdev->pdev` is missing. `PLL_LAST` restores saved per-domain clock values from `struct goya_device`.

## State And Persistence Behavior

Stored target clock values persist in `struct goya_device` fields and are used by `PLL_LAST`. `hdev->high_pll` is mutable through sysfs and used by high-profile programming. `goya->pm_mng_profile` controls whether users may directly write clock attributes, and `goya->curr_pll_profile` tracks the last auto profile to avoid redundant changes in `goya_set_frequency()`. The PM mode transition explicitly synchronizes with delayed PLL work to avoid background auto downshift after entering manual mode.

## Dependencies And Integration Points

This file depends on `goyaP.h`, the common firmware frequency helpers `hl_fw_set_frequency()` and `hl_fw_get_frequency()`, operational-state checks, `dev_get_drvdata()`, sysfs `DEVICE_ATTR_*` macros, `kstrtoul()`, `hdev->fpriv_list_lock`, `hdev->is_compute_ctx_active`, and CPU-CP info populated by `goya_cpucp_info_get()`. The attribute groups are installed by the generic driver through `goya_funcs.add_device_attr`.

## Risks And Edge Cases

- Store handlers ignore return status from `hl_fw_set_frequency()`, so firmware programming failures can still update cached clock values and return the original byte count.
- `kstrtoul()` writes into a `long value` variable despite expecting an `unsigned long *`-style destination; this relies on compatible representation and should be treated carefully in type-cleanup work.
- `strncmp("auto", buf, strlen("auto"))` and equivalent manual parsing accept prefixed values such as `automatic`; this may be intentional sysfs leniency but is not strict.
- PM mode switching must avoid deadlock with the delayed work item, hence the manual-mode path releases `fpriv_list_lock` before flushing delayed work.
- The clock write path is blocked in auto mode but not otherwise range-checked; firmware must reject unsupported PLL values.

## Test Signals

Tests should exercise operational and non-operational sysfs reads/writes, invalid numeric input, manual-vs-auto write permission, PM mode changes with and without active compute context, delayed work flushing on auto-to-manual transition, `PLL_HIGH`/`PLL_LOW`/`PLL_LAST` programming calls, high PLL mutation, and Infineon version formatting after CPU-CP info is fetched.
