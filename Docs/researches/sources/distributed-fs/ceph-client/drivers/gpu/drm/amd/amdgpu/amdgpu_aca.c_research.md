<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c

## Purpose
`amdgpu_aca.c` implements Accelerator Check Architecture support for amdgpu RAS. It collects valid ACA banks from SMU firmware, filters them by hardware IP, dispatches them to registered ACA handles, parses and caches error counts, emits RAS event logs, optionally generates CPER records, exposes per-handle sysfs reads under the RAS group, and provides debugfs dump/debug-mode controls.

The code is a bridge between SMU-reported machine-check-style bank registers and amdgpu RAS accounting. It supports UE, CE, and deferred error flows and lets hardware-specific handle owners provide validation and parser callbacks.

## Important APIs, types, and functions
- `amdgpu_aca_init()`, `amdgpu_aca_fini()`, and `amdgpu_aca_reset()` initialize, clean up, and reset ACA manager state.
- `amdgpu_aca_set_smu_funcs()` installs the SMU callback table used to count banks, fetch banks, parse error codes, and set debug mode.
- `amdgpu_aca_add_handle()` and `amdgpu_aca_remove_handle()` register per-IP `struct aca_handle` objects, initialize their error caches, and add/remove `ras/aca_<name>` sysfs files.
- `amdgpu_aca_get_error_data()` is the main RAS query entry point. It updates banks from SMU, logs deferred errors where appropriate, drains the selected handle's error cache into `struct ras_err_data`, and clears cached bank errors after reporting.
- Bank collection helpers include `aca_smu_get_valid_aca_count()`, `aca_smu_get_valid_aca_banks()`, `aca_banks_add_bank()`, and `aca_banks_release()`.
- Dispatch and cache helpers include `aca_bank_is_valid()`, `aca_dispatch_banks()`, `aca_bank_parser()`, `aca_error_cache_log_bank_error()`, `aca_log_aca_error()`, and `aca_log_aca_error_data()`.
- `aca_bank_info_decode()` decodes IPID fields into hwid, mcatype, die id, and socket id.
- `aca_bank_check_error_codes()` delegates to SMU `parse_error_code()` and checks against an allowed list.
- Debug helpers create `aca_debug_mode`, `aca_ue_dump`, and `aca_ce_dump` when debugfs is enabled.

## Control flow
ACA starts with `amdgpu_aca_init()`, which initializes the handle manager and UE update flag. Hardware-specific RAS blocks call `amdgpu_aca_add_handle()` with an `aca_info` descriptor. If ACA is enabled through runtime state or `debug_enable_ras_aca`, the handle is added to the manager list, gets error-cache lists and locks, and receives a sysfs attribute.

When RAS queries errors, `amdgpu_aca_get_error_data()` checks the handle, validates the requested error type against the handle mask, maps UE to `ACA_SMU_TYPE_UE` and CE/deferred to `ACA_SMU_TYPE_CE`, then calls `aca_banks_update()`. That function checks whether UE banks should be updated, asks SMU for a valid bank count, fetches each bank, dumps registers to RAS event logs, filters out non-UMC poison UEs, appends banks to a temporary list, dispatches banks to matching handles, and generates CPER records. Dispatch invokes each handle's parser when the bank matches its hardware IP or is a deferred bank routed to UMC.

After update, `__aca_get_error_data()` drains deferred error cache unless the user explicitly asked for deferred only, then drains the requested error cache. Draining adds CE/UE/DE counts to `ras_err_data` per decoded socket/die and removes cache entries so the sysfs query is effectively read-and-clear.

Debugfs dump flows call the same update path with a handler that prints decoded bank info and register values before logging them into the normal error cache.

## State and persistence behavior
ACA runtime state lives under `adev->aca`. It owns the handle manager list, SMU function table, UE update atomic flag, and enable state. Each registered handle owns an error cache with per-error-type lists protected by mutexes. Cache entries accumulate counts by socket and die, not by every decoded field; `find_bank_error()` only keys on `socket_id` and `die_id`.

The cache is transient. It is cleared when RAS/sysfs reads drain entries, when handles are removed, or when ACA is finalized. `amdgpu_aca_reset()` clears the UE update flag. UE updates are throttled during RAS interrupt recovery through `ue_update_flag` so the same UE bank is not counted repeatedly before reset clears the SMU valid MCA count.

## Dependencies and integration points
The implementation depends on Linux list/mutex/sysfs/debugfs/seq_file helpers, amdgpu RAS accounting and event logging, CPER generation, SMU ACA callbacks supplied by ASIC-specific power-management code, UMC/GFX/SDMA RAS blocks that register handles, and `struct ras_query_context` event ids.

It integrates with `amdgpu_ras_aca_sysfs_read()` for sysfs reads, `amdgpu_ras_set_aca_debug_mode()` for debug mode writes, and `amdgpu_cper_generate_*_record()` when CPER output is enabled.

## Risks and edge cases
The cache key only uses socket and die, so multiple banks on the same socket/die are aggregated. That is useful for RAS counts but loses bank-specific detail after logs are emitted. Deferred errors are routed to UMC handles regardless of IP match; incorrect deferred classification can shift ownership.

UE update suppression depends on `amdgpu_ras_intr_triggered()` and the atomic flag. A missed reset of the flag can undercount later UEs; missing suppression can double count persistent valid banks. `aca_smu_get_valid_aca_banks()` filters poison UEs for non-UMC banks, so changes in SMU semantics could hide real non-UMC poison reports.

Sysfs attributes are only removed if `adev->dev->kobj.sd` exists. The code must handle teardown ordering where the RAS sysfs group is already gone. Debugfs dump paths both print and mutate caches by calling the normal parser, so reads can affect later query results.

## Test signals
Useful signals include successful handle registration/removal, presence and removal of `ras/aca_<name>` sysfs files, correct CE/UE/DE counts in RAS queries, read-and-clear cache behavior, CPER records generated when enabled, debugfs dumps showing expected bank registers, debug-mode toggling through SMU, and no duplicate UE counts across a single recovery. Fault-injection tests should cover missing SMU callbacks, invalid bank counts, non-matching hwid/mcatype, deferred banks, and parser failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c -->
