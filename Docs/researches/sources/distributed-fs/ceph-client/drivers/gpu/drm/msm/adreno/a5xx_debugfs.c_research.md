# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_debugfs.c

## Purpose
`a5xx_debugfs.c` provides debugfs inspection and reset controls for A5xx GPUs. It exposes CP PFP, ME, MEQ, and ROQ internal state dumps and a privileged reset path that releases firmware/firmware BOs and forces recovery.

## Important APIs, Types, And Functions
The exported function is `a5xx_debugfs_init`. Debug dump helpers are `pfp_print`, `me_print`, `meq_print`, and `roq_print`, all routed through the generic `show` callback in `a5xx_debugfs_list`. The writable debugfs path is `reset_set`, exposed through `reset_fops`.

## Control Flow
`a5xx_debugfs_init` creates the read-only DRM info files and a writable `reset` file under the DRM minor debugfs root. Read paths use `drm_seq_file_printer`, recover `priv->gpu`, and call the function pointer stored in the info entry. Each print helper writes an indexed debug address register and reads the corresponding data register repeatedly. `reset_set` requires `CAP_SYS_ADMIN`, locks `gpu->lock`, releases PM4/PFP firmware references, unpins and drops PM4/PFP BOs, marks `gpu->needs_hw_init`, runtime-resumes the device, invokes `gpu->funcs->recover`, runtime-suspends, and unlocks.

## State And Persistence
Read paths do not retain state, but they change indexed debug address registers while dumping. Reset mutates firmware pointers, firmware BO pointers, `needs_hw_init`, and hardware state through recovery. The reset file is intentionally privileged but writable by debugfs permissions.

## Dependencies And Integration Points
The file depends on Linux debugfs, DRM debugfs helpers, `drm_printer`, MSM device private data, and A5xx register definitions from `a5xx_gpu.h`. It integrates with A5xx teardown conventions by using the same unpin/put patterns for PM4/PFP BOs.

## Risks
Debug reads touch live indexed hardware registers and can race with GPU activity if used during workload execution. `reset_set` explicitly allows resetting an active GPU for debugging, so users can lose active submissions. Firmware/BO release must remain aligned with `a5xx_destroy` and `a5xx_ucode_load` or reset can leak or double-release resources.

## Test Signals
Signals include debugfs files appearing only when debugfs is enabled, PFP/ME/MEQ/ROQ dumps returning stable formatted rows, non-admin reset writes failing, admin reset forcing firmware reload and recovery without leaks, and no crashes when debugfs is absent or `minor` is NULL.
