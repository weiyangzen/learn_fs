## sources/distributed-fs/ceph-client/arch/x86/events/amd/brs.c

Purpose: implements AMD Family 19h Branch Sampling (BRS), a branch-stack sampling mechanism using debug-extension MSRs.

Important APIs/types: `union amd_debug_extn_cfg`, `amd_brs_hw_config()`, `amd_brs_reset()`, `amd_brs_init()`, `amd_brs_enable/disable[_all]()`, `amd_brs_drain()`, `amd_pmu_brs_sched_task()`, `perf_amd_brs_lopwr_cb()`, and `amd_brs_lopwr_init()`. It uses `BRS_POISON` to mark stale branch records.

Control flow: init detects `X86_FEATURE_BRS` on supported AMD family, sets `x86_pmu.lbr_nr` to 16, and disables hardware filtering. Event config permits only sampling, retired-taken-branch BRS events, non-frequency periods larger than BRS depth, and branch-stack type without fine filtering. Runtime enable toggles `brsmen`; interrupt handling disables/drains BRS, reads saturated branch records from `MSR_AMD_SAMP_BR_*`, sign-extends targets, applies PLM filtering, and fills `cpuc->lbr_entries`.

State/persistence: per-CPU `brs_active`, `lbr_users`, branch entries, MSR `MSR_AMD_DBG_EXTN_CFG`, and poisoned MSR entries protect against cross-task reuse.

Integration points: AMD core PMU static calls, perf branch stack sampling, context switch hooks, ACPI low-power callbacks, and sysfs event exposure from `core.c`.

Risks: BRS records are not PID-tagged, so poisoning on context switch is critical. Low-power states can hold NMIs too long unless BRS is disabled. Test signals include `perf record -j any -e branch-brs`, context-switch leakage tests, low-power idle tests, NMI handling, and branch-stack PLM filtering checks.
