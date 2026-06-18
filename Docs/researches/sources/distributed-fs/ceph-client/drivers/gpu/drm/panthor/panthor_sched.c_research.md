# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.c

## Purpose
Implements Panthor CSF scheduling for firmware-managed Mali GPUs. It bridges DRM scheduler jobs to firmware command stream group/queue interfaces, handles group rotation across limited CSG slots, manages queue fences/timeouts/sync waits, responds to firmware events, coordinates resets/suspend, and gathers fdinfo profiling.

## Important APIs, Types, and Functions
Core types are `panthor_scheduler`, `panthor_csg_slot`, `panthor_group`, `panthor_queue`, `panthor_group_pool`, `panthor_job`, syncobj layouts, tick/update contexts, and job ringbuffer instruction builders. Exported APIs include group pool/create/destroy/state functions, `panthor_job_create()`, job ref/VM/reservation helpers, scheduler init/unplug/suspend/resume/reset hooks, MMU fault reporting, firmware event reporting, and fdinfo gatherers.

## Control Flow
Scheduler init reads firmware global/CSG/CS interface capabilities, clamps CSG slots to unique priorities, verifies non-MCU AS availability, initializes queues/lists/workqueues, and publishes CSIF counts. Group creation validates masks/priorities, gets the target VM, allocates suspend/protection buffers, per-queue syncobj BO, queues/ringbuffers/firmware interfaces/profiling slots, inserts the group into idle lists, and marks the xarray handle registered. Job creation validates queue submit arguments, references the group, allocates a done fence for non-empty streams, computes scheduler credits from profiling-enabled instruction count, and initializes a DRM scheduler job. `queue_run_job()` resumes the device, initializes the done fence, writes a kernel-generated CS instruction sequence into the queue ringbuffer, advances insert pointers, schedules or doorbells the group, starts timeouts, updates last fence, and records busy state. Tick work snapshots active groups, asks firmware for status updates, picks groups by priority/round-robin while respecting AS-slot limits, suspends/terminates evicted groups, binds and starts/resumes new groups, updates runtime PM/devfreq, and queues the next tick only when needed.

## State and Persistence
Long-lived state includes scheduler workqueues, tick timing, runnable/idle/waiting lists, CSG slot bindings, runtime PM reference state, reset stopped-groups list, per-group state/fault/timeout/idle/blocked masks, queue ringbuffer and interface BOs, per-queue sync wait state, fence contexts, in-flight job lists, last fences, profiling slots, and fdinfo counters. Hardware-visible state is persisted in firmware input/output interfaces and syncobj BOs mapped into the VM.

## Dependencies and Integration Points
Depends on DRM scheduler/fences/dma_resv, runtime PM, devfreq, Panthor firmware interface helpers, kernel BO/GEM/heap/MMU/GPU/device helpers, CSF register macros, and UAPI group/queue/job structs. Integrates with MMU via `panthor_vm_active()`, `panthor_vm_idle()`, `panthor_vm_get_bo_for_va()`, and MMU fault reports. Tiler OOM integrates with heap growth and queue firmware inputs.

## Risks and Edge Cases
High-risk areas are lock ordering between scheduler lock, reset lock, queue fence locks, and dma-signaling sections; firmware ack timeouts; reset while jobs/groups are active; sync-wait CPU mapping lifetime; tiler OOM allocation outside scheduler lock; empty command streams returning last fence; timeout suspension/resume accounting; and fault attribution from CS extract pointers. CSG priority uniqueness is used to avoid firmware deadlocks, so slot-count clamping is intentional.

## Test Signals
Signals include group create/destroy/state ioctl tests, multiple priorities and more groups than slots to exercise rotation, RT preemption, job submission with/without profiling, empty stream fences, sync wait unblock, tiler OOM growth and ENOMEM fallback, CS fault/fatal IRQ injection, progress timeout, MMU fault propagation, suspend/resume/reset recovery, fdinfo accounting, and lockdep under concurrent submit/destroy/reset.
