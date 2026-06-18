<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c

## Purpose
`xe_execlist.c` implements the legacy execlist submission backend used when GuC submission is disabled. It provides port scheduling, LRC start/idle programming, interrupt/timer progress handling, DRM scheduler backend ops, and `xe_exec_queue_ops` for execlist queues.

## Important APIs, types, and functions
Key functions include `__start_lrc()`, `__xe_execlist_port_start()`, `_idle()`, `_start_next_active()`, `read_execlist_status()`, IRQ handler functions, `xe_execlist_make_active()`, fail timer, `xe_execlist_port_create()`, `xe_execlist_port_destroy()`, `execlist_run_job()`, `execlist_job_free()`, backend queue init/fini/destroy, and `xe_execlist_init()`.

## Control flow and integration points
Port creation allocates a kernel idle LRC, initializes priority lists and lock, installs the hardware engine IRQ handler, and starts a fallback timer. Job run emits ring commands, marks the queue active, and returns the job fence. The active selection scans priority lists high-to-low, drops idle queues, and starts the next non-idle LRC or submits the port idle LRC. Starting an LRC writes context tail, flushes memory, writes HWSP, configures ring mode/MSI-X, writes descriptor low/high, and loads execlist control. Destroy is asynchronous on `system_dfl_wq` and removes active links before common queue fini.

## State and persistence behavior
Port state persists per hardware engine with active lists, last software context id, current running queue, fail timer, and idle LRC. Queue backend state stores the DRM scheduler, entity, port pointer, active priority, active link, and destroy work.

## Dependencies, risks, and test signals
Dependencies include DRM scheduler, MMIO registers, LRC layout, ring ops, HWSP BOs, engine IRQ locking, MSI-X capability, and exec queue common code. Risks include NIY kill/suspend/reset/active ops, interrupt race noted by TODO, timer fallback behavior, context-id wrap, async destroy ordering, and missing GuC feature parity. Test signals include force-execlist boot, job submission/completion, priority ordering, timer fallback, queue destroy under load, MSI-X/non-MSI-X interrupts, compute RCU mode programming, and lockdep on port lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c -->
