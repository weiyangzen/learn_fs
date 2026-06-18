<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c

## Purpose
Initializes and tears down the Lima hardware device: clocks, reset, regulator, VM address space, MMIO, IP block discovery, GP/PP scheduler pipes, error-dump state, and runtime suspend/resume.

## Important APIs, types, and functions
`struct lima_ip_desc` describes each IP block's name, IRQ, required status, offset, and lifecycle callbacks. Public entry points are `lima_device_init()`, `lima_device_fini()`, `lima_device_resume()`, `lima_device_suspend()`, and `lima_ip_name()`. Helpers cover clock/regulator init, IP init/fini/resume/suspend, and GP/PP pipe init/fini.

## Control flow
Device init sets DMA constraints, enables bus/core clocks and optional reset, enables optional regulator, creates an empty VM, reserves VA/DLBU memory depending on Mali400 versus Mali450, maps MMIO, probes every IP descriptor, initializes the GP scheduler pipe, initializes the PP pipe by pairing present PP, PP MMU, and L2 cache blocks, initializes error-dump bookkeeping, and logs rates. Fini reverses scheduler pipes, IPs, DLBU memory, VM, regulator, and clocks. Resume enables clocks/regulator, resumes all present IPs, then resumes devfreq. Suspend refuses if scheduler credits indicate running tasks, suspends devfreq, suspends IPs in reverse order, disables regulator, and disables clocks.

## State and persistence
`struct lima_device` stores GPU id, versions, PP count, MMIO, clocks, reset, regulator, IP array, scheduler pipes, empty VM, VA range, DLBU page, devfreq state, and error-task list. IP descriptors are static. Hardware state is rebuilt on resume by each IP callback.

## Dependencies and integration points
Depends on platform resource 0, clock names `bus` and `core`, optional reset array, optional `mali` regulator, DMA mapping, VM code, GP/PP/MMU/PMU/L2/DLBU/BCAST modules, and DRM scheduler pipe setup. Called by `lima_drv.c` probe/remove and PM ops.

## Risks
IP discovery order matters: optional IPs can depend on earlier PP presence, and L2 cache selection differs between Mali400 and Mali450. Suspend can fail with `-EBUSY` if jobs are running. Error unwinding must match the partial init state. Mali450 reserves a VA region for DLBU; wrong VA bounds would collide with user BO mappings.

## Test signals
Probe/remove on Mali400 and Mali450, optional regulator/reset absence, missing optional PP cores, multiple L2 layouts, runtime suspend while idle and busy, resume after suspend, and failure injection during IP init validate this file. Logs expose IP versions and clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c -->
