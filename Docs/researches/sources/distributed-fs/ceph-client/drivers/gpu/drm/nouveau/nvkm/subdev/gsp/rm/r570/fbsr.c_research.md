# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fbsr.c

Purpose: implements R570 framebuffer suspend/resume callbacks. It preserves BAR/instance-memory state around GSP suspend, disables active channel scheduling through a new internal FIFO control, allocates system backing for RM's VRAM state, and delegates common cleanup to R535 helpers where compatible.

Important APIs: `r570_fbsr_suspend_channels()` writes `NV2080_CTRL_INTERNAL_FIFO_TOGGLE_ACTIVE_CHANNEL_SCHEDULING`. `r570_fbsr_init()` creates a host memory-list object with `r535_fbsr_memlist()`, sends `NV2080_CTRL_INTERNAL_FBSR_INIT`, and passes `gsp->sr.meta.addr` as `sysmemAddrOfSuspendResumeData`. `r570_fbsr_suspend()` stops scheduling, saves preserved and boot instmem objects, disables BAR2, sizes and allocates `gsp->sr.fbsr`, and initializes RM FBSR. `r570_fbsr_resume()` restores boot BAR2 page tables via BAR0, re-enables BAR2, flushes BAR2 VMM, restores remaining instmem objects, flushes BAR1 VMM, resumes scheduling, and calls `r535_fbsr_resume()`.

Control flow and state: suspend saves state from `device->imem->list` and `imem->boot`, marks `device->bar->bar2 = false`, and allocates `gsp->sr.fbsr` sized from `gsp->fb.heap.size`, `gsp->fb.rsvd_size`, and VGA workspace size. Resume reverses BAR accessibility in stages so page tables are available before normal BAR2-backed restore.

Dependencies and integration: depends on instmem private APIs, BAR helpers, GSP, VMM, R570 FBSR/FIFO headers, and R535 FBSR memory-list/resume helpers. It is invoked from `r535_gsp_fini()`/`r535_gsp_init()` through the selected RM API's `.fbsr` callbacks.

Risks: errors after scheduling is disabled or BAR2 is disabled must be unwound by higher-level failure handling; this file does not re-enable scheduling on all suspend failure paths. FBSR size calculation must include all RM VRAM allocations or resume may lose state. Resume order is critical because BAR2 page tables themselves need restoring before BAR2 can be used.

Test signals: runtime and system suspend/resume should preserve channels and instmem allocations, BAR1/BAR2 VMM flushes should occur without faults, active channel scheduling should stop and resume, and post-resume workloads should not see unexpected channel resets.
