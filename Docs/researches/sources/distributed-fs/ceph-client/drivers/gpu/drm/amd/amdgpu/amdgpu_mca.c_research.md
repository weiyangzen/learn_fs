## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c

Purpose: implements Machine Check Architecture/RAS helpers for querying, caching, dumping, and accounting MCA error banks through SMU callbacks. It registers MCA RAS blocks, parses CE/UE/DE counts, prevents duplicate UE counting during recovery, and exposes debugfs dump/debug mode controls.

Important APIs/functions: simple UMC status helpers query/reset CE/UE counts from PCIe MCA status registers. `amdgpu_mca_mp0/mp1/mpio_ras_sw_init()` register RAS block objects. `amdgpu_mca_init/fini/reset()` initialize and free MCA bank caches. `amdgpu_mca_smu_init_funcs()` installs SMU callback table; `amdgpu_mca_smu_set_debug_mode()` delegates debug mode. `amdgpu_mca_smu_log_ras_error()` collects MCA banks, dispatches parsed counts into `ras_err_data`, caches unconsumed banks, and re-dispatches cached data. Debugfs adds `mca_debug_mode`, `mca_ue_dump`, and `mca_ce_dump`.

Control flow: SMU-backed collection asks for valid count by error type, reads each MCA entry within max count bounds, adds it to a temporary bank set, and logs selected register dumps. UE updates are suppressed after the first recovery-stage update using `ue_update_flag`; CE entries are dumped only when deferred-error logic says so. Dispatch parses a count per bank for the requested RAS block; nonzero counts are accumulated per socket/die as UE, CE, or deferred. Entries that could not be attributed remain cached for later attempts.

State and persistence: `adev->mca` holds RAS block interfaces, SMU funcs, per-error-type caches (`mca_caches`), mutexes, and the UE update atomic. MCA bank sets are in-memory linked lists. Debugfs reads can also populate caches. No persistent storage exists.

Dependencies/integration: depends on AMDGPU RAS framework, SMUIO MCM config, UMC status field macros, SMU MCA callbacks, debugfs, and RAS event logging. It feeds global RAS error accounting and recovery flows.

Risks: cache merging ignores allocation failures from `amdgpu_mca_bank_set_add_entry()` in some loops, so memory pressure may silently drop MCA entries. MCA bank list operations require correct lock usage around caches. UE duplicate suppression relies on `amdgpu_ras_intr_triggered()` state. Debugfs dump paths both inspect and cache MCA banks, so diagnostic reads can affect later accounting.

Test signals: RAS injection/fault tests for CE/UE/DE, recovery-stage duplicate UE suppression, SMU callback `-EOPNOTSUPP` behavior, debugfs dump and debug-mode controls, cache carryover across unmatched banks, and per-socket/die error statistics.
