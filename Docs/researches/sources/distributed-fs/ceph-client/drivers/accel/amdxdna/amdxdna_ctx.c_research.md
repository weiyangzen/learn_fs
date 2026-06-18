# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.c

Purpose: implements generic AMD XDNA DRM hardware-context and command-submission ioctl plumbing, leaving device-specific hardware scheduling to `amdxdna_dev_ops`.

Important APIs/functions: context ioctls `amdxdna_drm_create_hwctx_ioctl()`, `amdxdna_drm_destroy_hwctx_ioctl()`, and `amdxdna_drm_config_hwctx_ioctl()` allocate, publish, configure, and destroy `struct amdxdna_hwctx` objects in a per-client xarray. `amdxdna_cmd_submit()` builds `amdxdna_sched_job`, pins/holds command and argument BOs, resumes runtime PM, protects the context lookup with SRCU, creates an output fence, and calls the device `cmd_submit` callback. Command helpers parse ERT headers, payloads, CU masks, and error state. `amdxdna_hwctx_walk()` provides SRCU-safe enumeration for query code.

Control flow: users create a context with QoS, create BOs, then submit an execbuf with one command BO and argument BO handles. Destroy removes the xarray entry first, synchronizes SRCU, and then calls device finalization so new submissions cannot race destroyed state.

State and persistence: per-client `hwctx_xa`, `next_hwctxid`, hardware-context fields, scheduler job references, BO references, fences, and atomic submit/free counters are in-memory only. `amdxdna_hwctx_remove_all()` cleans remaining contexts on file close/remove.

Dependencies: DRM GEM, DRM scheduler/fences, xarray, SRCU, tracepoints, runtime PM, AMD XDNA GEM and PCI driver ops.

Risks: error unwinds must drop PM, BO, fence, and job refs exactly once. `cmd_bo` may be absent for driver commands, so cleanup paths must tolerate NULL where expected. Config buffer handling caps CU config to one page; new config types need explicit validation.

Test signals: create/destroy/config ioctls, invalid handles, context ID wrap, concurrent submit/destroy, BO pin failures, PM resume failures, ERT payload bounds, and close/remove cleanup with live jobs.
