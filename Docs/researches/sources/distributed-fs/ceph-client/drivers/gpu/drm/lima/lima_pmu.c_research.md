<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c

## Purpose
Controls the Mali PMU power domains used by Lima, powering GPU IP blocks up during init/resume and down during fini/suspend.

## Important APIs, types, and functions
Exports `lima_pmu_init()`, `lima_pmu_fini()`, `lima_pmu_resume()`, and `lima_pmu_suspend()`. Helpers are `lima_pmu_wait_cmd()`, `lima_pmu_get_ip_mask()`, `lima_pmu_hw_init()`, and `lima_pmu_hw_fini()`.

## Control flow
Hardware init masks PMU interrupts, writes a conservative software delay, reads power status, and powers up any off domains while waiting for command completion. Fini computes a domain mask from GPU type and present PP cores, powers down currently-on domains in that mask, and handles the Mali400 quirk where all-domain powerdown may not generate an interrupt.

## State and persistence
`ip->data.mask` caches the PMU domain mask. Hardware state persists as PMU power status, interrupt clear/mask, software delay, and command state.

## Dependencies and integration points
Depends on Lima device GPU ID, IP presence, and PMU register constants. Called by device IP lifecycle and PM suspend/resume ordering.

## Risks
Wrong masks can power down active or required domains. PMU command timeout prevents reliable power sequencing. The Mali400 interrupt quirk must remain preserved.

## Test signals
Probe/resume power-up, suspend/remove power-down, Mali400 and Mali450 PP topology masks, PMU timeout injection, and clock-frequency stress validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c -->
