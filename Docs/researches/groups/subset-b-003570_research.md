# Research: subset-b-003570

Grouped research for DRM vblank core helpers and the etnaviv DRM driver files listed in work item `subset-b-003570`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank.c

## Purpose
Implements the DRM core vblank subsystem: per-CRTC vblank interrupt/timer accounting, timestamp interpolation, reference-counted enable/disable, userspace vblank wait and sequence ioctls, event delivery, and integration with vblank work. It is the central code drivers rely on after `drm_vblank_init()` and `drm_crtc_handle_vblank()`.

## Important APIs, Types, and Functions
Exports include `drm_vblank_init`, `drm_dev_has_vblank`, `drm_crtc_vblank_get/put`, `drm_crtc_vblank_on/off/reset/restore`, count/time accessors, event helpers, wait/sequence ioctls, vblank timer start/cancel/timeout helpers, and timestamp helpers. State is held in `struct drm_vblank_crtc` entries under `dev->vblank`, including atomic `count`, hardware `last`, `time`, `seqlock`, waitqueue, `refcount`, `enabled`, `inmodeset`, config, mode timing, hrtimer, and pending work list. Module parameters `vblankoffdelay` and `timestamp_precision_usec` tune IRQ disable delay and timestamp precision.

## Control Flow
Initialization allocates per-CRTC vblank state, initializes locks/timers/seqlocks/workers, and registers managed cleanup. `drm_vblank_get()` increments the refcount under `vbl_lock`; the 0-to-1 transition enables hardware vblank through CRTC funcs and reconciles missed counts via `drm_update_vblank_count()`. `drm_vblank_put()` schedules immediate, delayed, or no disable depending on `offdelay_ms` and `disable_immediate`. Interrupt handlers call `drm_handle_vblank()`, which locks `event_lock` and `vblank_time_lock`, updates count/time, wakes waiters, delivers queued events, runs vblank work, and possibly disables instant-off IRQs. Userspace waits convert relative/absolute requests to 64-bit sequences, optionally queue events, or block on the vblank waitqueue. Timer-backed vblank calls use an hrtimer to synthesize `drm_crtc_handle_vblank()`.

## State and Persistence
Counters are in-memory software counters that survive IRQ disable intervals by estimating missed vblanks using hardware counters or timestamps. Count/time snapshots are protected by a seqlock; enable/disable state and modeset gating are protected by `vbl_lock` and `vblank_time_lock`. Events persist on `dev->vblank_event_list` until delivered or prematurely flushed on CRTC disable. No on-disk persistence exists.

## Dependencies and Integration Points
Depends on DRM CRTC funcs (`enable_vblank`, `disable_vblank`, `get_vblank_counter`, `get_vblank_timestamp`), helper funcs (`get_scanout_position`, timer timeout handlers), atomic/modeset state, DRM leases, DRM event infrastructure, hrtimers, timers, waitqueues, and `drm_vblank_work.c`. Drivers must call `drm_crtc_handle_vblank()` from IRQs or use vblank timers.

## Risks
The risky areas are reference balancing between queued events/work and vblank IRQ refs, races around modeset disable/enable, hardware counter wrap/reset handling, timestamp precision failures, and hrtimer cancellation deadlocks. Incorrect driver hooks can create stale counts, duplicate events, or missed page-flip completion. `disable_immediate` requires race-free timestamping.

## Test Signals
Useful signals include vblank wait ioctl behavior, sequence ioctl event ordering, page-flip event timestamps, suspend/resume and modeset counter continuity, timer-backed virtual vblank operation, debug `DRM_UT_VBL` traces, lockdep, WARNs for invalid pipe/refcount state, and stress tests with rapid enable/disable plus queued events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_helper.c

## Purpose
Provides small helper implementations for drivers that need generic vblank behavior, especially timer-backed vblank support for hardware without real vblank interrupts.

## Important APIs, Types, and Functions
Exports `drm_crtc_vblank_atomic_flush`, `drm_crtc_vblank_atomic_enable`, `drm_crtc_vblank_atomic_disable`, `drm_crtc_vblank_helper_enable_vblank_timer`, `drm_crtc_vblank_helper_disable_vblank_timer`, and `drm_crtc_vblank_helper_get_vblank_timestamp_from_timer`. These functions are intended for `drm_crtc_helper_funcs` and `drm_crtc_funcs` wiring, often through helper macros.

## Control Flow
`atomic_flush` consumes `crtc_state->event` under `event_lock`, tries to acquire a vblank ref, arms the event for the next vblank on success, or sends immediately on failure. Enable/disable call `drm_crtc_vblank_on/off`. Timer helpers simply start/cancel the vblank timer and source timestamps from the timer timeout helper.

## State and Persistence
The file owns no persistent state. It mutates CRTC state event pointers and delegates all vblank state to `drm_vblank.c`.

## Dependencies and Integration Points
Depends on DRM atomic state, event locking, `drm_crtc_arm_vblank_event`, `drm_crtc_send_vblank_event`, and vblank timer APIs. Integrates with drivers that choose generic helper funcs instead of bespoke vblank IRQ handling.

## Risks
Drivers using `atomic_flush` must ensure event arming matches hardware commit timing; otherwise events may be one frame late or early. Timer-backed timestamps are synthetic and depend on correct mode-derived frame duration.

## Test Signals
Atomic commit tests should verify event delivery with and without available vblank refs. Timer-backed drivers need checks for stable event cadence, correct disable behavior, and absence of leaked `crtc_state->event` pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_work.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_work.c

## Purpose
Implements `drm_vblank_work`, a delayed work facility that queues work until a target vblank count and then runs it on a per-CRTC realtime-priority kthread worker.

## Important APIs, Types, and Functions
Internal vblank hooks are `drm_handle_vblank_works`, `drm_vblank_cancel_pending_works`, `drm_vblank_worker_init`, `drm_vblank_destroy_worker`, and `drm_vblank_flush_worker`. Exported APIs are `drm_vblank_work_schedule`, `drm_vblank_work_cancel_sync`, `drm_vblank_work_flush`, `drm_vblank_work_flush_all`, and `drm_vblank_work_init`. State resides in each `struct drm_vblank_work` and `struct drm_vblank_crtc` pending list, waitqueue, and kthread worker.

## Control Flow
Scheduling takes `event_lock`, rejects cancelling or modeset-disabled work, acquires a vblank ref for newly pending work, and either queues immediately if the target passed and `nextonmiss` is false or links the work onto `pending_work`. Each vblank calls `drm_handle_vblank_works()` under `event_lock`, moves due items to the kthread worker, drops their vblank refs, and wakes flush waiters. Cancellation removes pending list entries, drops refs, sets a cancellation guard, and synchronously cancels running kthread work.

## State and Persistence
All state is in-memory. Pending list membership tracks whether a vblank ref is held. `cancelling` prevents self-rearming races while cancellation is in progress. Worker lifetime is tied to per-CRTC vblank initialization and cleanup.

## Dependencies and Integration Points
Depends on DRM vblank count/ref APIs, `event_lock`, `vbl_lock`, kernel kthread workers, FIFO scheduler priority, and vblank off cleanup in `drm_vblank.c`.

## Risks
Primary risks are leaked vblank refs if pending list transitions are wrong, rearming races during cancellation, scheduling work while a CRTC is in modeset, and realtime worker latency failing strict scanout deadlines.

## Test Signals
Stress self-rearming work, cancel/flush while vblank interrupts are disabled, vblank-off cleanup, lockdep around event/vblank locks, and refcount WARNs in the vblank core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vma_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vma_manager.c

## Purpose
Provides DRM's page-based mmap offset manager for mapping driver memory objects into a single DRM device address space, plus per-open-file access control for mmap permission checks.

## Important APIs, Types, and Functions
Exports manager lifecycle (`drm_vma_offset_manager_init/destroy`), offset allocation (`drm_vma_offset_add/remove`), lookup (`drm_vma_offset_lookup_locked`), and access control (`drm_vma_node_allow`, `drm_vma_node_allow_once`, `drm_vma_node_revoke`, `drm_vma_node_is_allowed`). It uses `struct drm_mm` for allocation and rb-trees for both interval lookup and allowed-file tracking.

## Control Flow
Managers initialize a page-range-backed `drm_mm`. Adding a node inserts into `drm_mm` under write lock unless already allocated; removing deletes and zeroes the `drm_mm_node`. Lookup walks the interval tree for the best node with `start <= requested_start`, then verifies it spans the requested page range. Access allow preallocates a permission entry, inserts or increments by `struct drm_file *` tag under node lock, and revoke decrements/removes entries.

## State and Persistence
Offset allocations persist in memory until explicit removal. Allowed-file rb-tree entries persist across offset add/remove and must be balanced by revocation before node destruction. No disk persistence exists.

## Dependencies and Integration Points
Depends on `drm_mm`, Linux rb-tree APIs, DRM GEM mmap offset helpers, and callers holding lookup locks for weak-reference lookup patterns.

## Risks
Using multiple managers on one address_space breaks linear mmap teardown assumptions. Permission entries can leak if allow/revoke counts are unbalanced. Callers must keep nodes alive during locked lookup and remove all nodes before manager destruction.

## Test Signals
Test non-overlap allocation, lookup inside object ranges, mmap access denied/allowed/revoked, repeated allow/revoke reference counts, destruction with empty manager, and concurrent lookup/remove lock discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vma_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_writeback.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_writeback.c

## Purpose
Implements DRM writeback connector support: connector-specific properties, internal/custom encoder initialization, framebuffer-backed writeback jobs, out-fence creation/signaling, and deferred cleanup.

## Important APIs, Types, and Functions
Exports `drm_writeback_connector_init`, `drm_writeback_connector_init_with_encoder`, `drmm_writeback_connector_init`, `drm_writeback_prepare_job`, `drm_writeback_queue_job`, `drm_writeback_cleanup_job`, `drm_writeback_signal_completion`, and `drm_writeback_get_out_fence`. It creates properties `WRITEBACK_FB_ID`, `WRITEBACK_PIXEL_FORMATS`, and `WRITEBACK_OUT_FENCE_PTR`. `struct drm_writeback_connector` owns a job queue, job lock, fence lock/context/seqno, and pixel-format blob.

## Control Flow
Initialization creates shared writeback properties, initializes a writeback connector, attaches an encoder, creates the immutable formats blob, initializes job/fence state, and attaches properties. `drm_writeback_set_fb()` lazily allocates a connector-state job and references the framebuffer. Prepare invokes optional connector helper validation/setup and marks the job prepared. Queue transfers job ownership from connector state to FIFO queue. Completion pops the first job, signals and releases its out-fence, then schedules job cleanup on `system_long_wq` because framebuffer release can sleep.

## State and Persistence
State is in-memory DRM object state. Jobs persist in `job_queue` from commit queueing to hardware completion. Pixel format blobs are refcounted DRM blobs. Managed init registers cleanup that destroys properties/blob and drains queued jobs.

## Dependencies and Integration Points
Integrates with DRM connector/encoder/property frameworks, atomic connector state, connector helper callbacks (`prepare_writeback_job`, `cleanup_writeback_job`), `dma_fence`, `sync_file` userspace ABI, and driver hardware completion interrupts.

## Risks
Drivers must signal exactly one completion per queued job and preserve hardware FIFO order. Property deletion is device-global and must not break multiple connectors. Accessing a framebuffer after completion without a private reference is unsafe. Out-fence error propagation depends on drivers passing accurate status.

## Test Signals
Atomic writeback tests should check property presence, supported format blob contents, per-commit FB semantics, out-fence signaling/error, FIFO completion ordering, cleanup on connector teardown, and interrupt-context completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Kconfig

## Purpose
Defines kernel configuration options for the etnaviv DRM driver for Vivante GPU IP cores and optional thermal throttling support.

## Important APIs, Types, and Functions
The primary symbol is `DRM_ETNAVIV`, a tristate depending on `DRM` and `MMU`. It selects `SHMEM`, `SYNC_FILE`, `TMPFS`, `WANT_DEV_COREDUMP`, `DRM_SCHED`, and DMA/CMA support when available. `DRM_ETNAVIV_THERMAL` is a bool depending on `DRM_ETNAVIV`, defaulting to enabled.

## Control Flow
Kconfig controls whether `etnaviv.o` is built in, modular, or omitted. Thermal support selection additionally selects `THERMAL` when enabled.

## State and Persistence
No runtime state is present; this file persists build-time configuration.

## Dependencies and Integration Points
Integrates with the DRM subsystem, MMU requirement, GEM shmem/TMPFS backing, sync file fence export, devcoredump, DMA contiguous memory support, DRM scheduler, and kernel thermal framework.

## Risks
Disabling thermal throttling is explicitly warned as potentially unsafe for SoCs. Missing MMU or DRM dependencies excludes the driver. Configuration changes affect availability of runtime features assumed by source files in this directory.

## Test Signals
Validate allmodconfig/allyesconfig and minimal configs, module build/load with `CONFIG_DRM_ETNAVIV=m`, and thermal-enabled versus thermal-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Makefile

## Purpose
Lists the object files linked into the etnaviv DRM driver and connects them to `CONFIG_DRM_ETNAVIV`.

## Important APIs, Types, and Functions
The `etnaviv-y` aggregate includes buffer, command parser, command buffer, driver, dump, GEM/PRIME/submit, GPU, hardware DB, IOMMU v1/v2/MMU, perfmon, flop reset, and scheduler objects. `obj-$(CONFIG_DRM_ETNAVIV) += etnaviv.o` emits the final built-in or module object.

## Control Flow
Kbuild compiles all listed objects into the aggregate driver when the Kconfig symbol is enabled.

## State and Persistence
No runtime state; this is build metadata. Ordering matters only insofar as Kbuild aggregates the listed objects into one module.

## Dependencies and Integration Points
Integrates this subset with adjacent etnaviv files not in this work item, including GPU, scheduler, MMU, submit, hardware DB, and perfmon implementations.

## Risks
Missing an object can produce unresolved symbols or disabled functionality. Adding generated headers alone is insufficient without corresponding object inclusion.

## Test Signals
Run kernel build targets for built-in and module configurations, and inspect `modinfo etnaviv`/link errors for aggregate consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/cmdstream.xml.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/cmdstream.xml.h

## Purpose
Generated Vivante FE command stream opcode and bitfield definitions used to construct and validate GPU command buffers.

## Important APIs, Types, and Functions
Defines `FE_OPCODE_*` values, primitive types, and `VIV_FE_*` command packet fields for LOAD_STATE, END, NOP, DRAW variants, WAIT, LINK, STALL, CALL/RETURN, CHIP_SELECT, WAIT_FENCE, DRAW_INDIRECT, and SNAP_PAGES. Macros provide masks, shifts, and field encoders such as `VIV_FE_LOAD_STATE_HEADER_COUNT(x)` and `VIV_FE_LINK_HEADER_PREFETCH(x)`.

## Control Flow
No executable control flow. Consumers combine the macros to emit 32-bit command words; `etnaviv_buffer.h` wraps common emit patterns, while `etnaviv_cmd_parser.c` decodes opcodes and LOAD_STATE fields for validation.

## State and Persistence
No mutable state. The header is generated from rules-ng-ng XML inputs and must stay synchronized with hardware definitions.

## Dependencies and Integration Points
Used by etnaviv command generation, parser validation, and low-level GPU ring manipulation. It pairs with state register headers such as `state.xml.h` and common enum definitions.

## Risks
Incorrect generated constants can corrupt command streams or weaken validation. Manual edits would be fragile because the source of truth is the XML generator.

## Test Signals
Build coverage catches missing macros. Runtime command submission, parser rejection tests, and GPU hang diagnostics indicate whether packet encodings match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/cmdstream.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/common.xml.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/common.xml.h

## Purpose
Generated common Vivante GPU constants for pipes, sync recipients, endian modes, chip model IDs, feature bits, and minor feature flags.

## Important APIs, Types, and Functions
Defines `PIPE_ID_PIPE_3D/2D`, `SYNC_RECIPIENT_*`, `ENDIAN_MODE_*`, many `chipModel_*` IDs, `chipFeatures_*`, and `chipMinorFeatures0..12_*` feature bits. These flags drive capability checks throughout etnaviv.

## Control Flow
No executable flow. Runtime code reads `struct etnaviv_chip_identity` feature fields and tests these macros to choose command sequences, cache flush behavior, MMU setup, and workarounds.

## State and Persistence
No mutable state. Like the command stream header, it is generated from XML and should be regenerated rather than manually changed.

## Dependencies and Integration Points
Used by `etnaviv_buffer.c`, `etnaviv_flop_reset.c`, GPU feature probing, perfmon, MMU and scheduler paths. It provides stable names for hardware capability checks.

## Risks
Feature bit mismatches can enable unsupported paths or skip required workarounds. Because many flags are hardware-errata oriented, subtle mistakes may only appear on specific SoC revisions.

## Test Signals
Hardware probing logs, feature-specific GPU tests, build coverage across etnaviv files, and regression testing on multiple Vivante chip models are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/common.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.c

## Purpose
Builds and mutates the kernel-side etnaviv GPU ring command buffer, including pipe switching, MMU flushes/context switches, user command buffer linking, event emission, cache flushes, sync points, and GPU stop/end handling.

## Important APIs, Types, and Functions
Key functions are `etnaviv_buffer_init`, `etnaviv_buffer_config_mmuv2`, `etnaviv_buffer_config_pta`, `etnaviv_buffer_end`, `etnaviv_sync_point_queue`, and `etnaviv_buffer_queue`. Important helpers include `etnaviv_cmd_select_pipe`, `etnaviv_buffer_reserve`, `etnaviv_buffer_replace_wait`, and `etnaviv_buffer_dump`. It uses `struct etnaviv_gpu`, `struct etnaviv_cmdbuf`, IOMMU mappings, chip identity flags, and command macros.

## Control Flow
The ring is initialized with a WAIT/LINK loop, optionally preceded by PPU flop reset commands. New submissions reserve space, optionally switch MMU context and flush MMU, optionally switch 2D/3D pipe with cache maintenance, link into the submitted cmdbuf, append a return sequence with cache flushes, event, WAIT/LINK loop, then atomically replaces the previous WAIT with a LINK to start execution. End and sync-point paths similarly replace a waitlink with END or a short event/END sequence.

## State and Persistence
Mutates `gpu->buffer.user_size`, `gpu->exec_state`, `gpu->mmu_context`, and `gpu->flush_seq`. Command buffer memory is persistent for the bound GPU and suballocated in DMA memory. `etnaviv_buffer_replace_wait()` uses barriers because the GPU may be reading the same WAIT while the CPU patches it.

## Dependencies and Integration Points
Depends on generated command/state headers, MMU context APIs, cmdbuf VA translation, GPU locks, BLT feature flags, PPU flop reset support, and event IDs consumed by GPU IRQ handling. Called from GPU initialization and submit execution paths.

## Risks
Incorrect prefetch dword counts, waitlink offsets, memory barriers, or context-switch ordering can jump the FE to bad addresses or hang the GPU. MMU context switches must occur only after old-context ring targets are computed. Feature-specific BLT/cache flush paths are hardware sensitive.

## Test Signals
GPU submit tests, hang recovery traces, ring debugfs dumps, command hex dumps under `DRM_UT_DRIVER`, MMU context switch stress, 2D/3D mixed workloads, and BLT-capable chip coverage are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.h

## Purpose
Provides inline command emission primitives for etnaviv command buffers.

## Important APIs, Types, and Functions
Defines `OUT`, `CMD_LOAD_STATE`, `CMD_LOAD_STATES_START`, `CMD_END`, `CMD_WAIT`, `CMD_LINK`, `CMD_STALL`, and `CMD_SEM`. These operate on `struct etnaviv_cmdbuf` and generated command/register macros.

## Control Flow
Each helper aligns `user_size` as required, writes command words into the buffer, and advances `user_size`. `CMD_SEM` emits a GL semaphore token through LOAD_STATE.

## State and Persistence
The only state changed is `cmdbuf->user_size` and the backing memory pointed at by `cmdbuf->vaddr`. `OUT` uses `BUG_ON` if writes exceed `cmdbuf->size`.

## Dependencies and Integration Points
Used heavily by `etnaviv_buffer.c` and `etnaviv_flop_reset.c`. Depends on generated `cmdstream.xml.h`, state register headers, and `struct etnaviv_cmdbuf`.

## Risks
These helpers assume callers reserve enough space and provide valid register/opcode values. Buffer overflow triggers a kernel BUG, so callers must compute sizes correctly.

## Test Signals
Command buffer construction tests, runtime GPU submissions, debug hex dumps, and KASAN/BUG reports from oversized emissions are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmd_parser.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmd_parser.c

## Purpose
Validates userspace etnaviv command streams, rejecting forbidden opcodes and writes to sensitive hardware state unless backed by expected relocations.

## Important APIs, Types, and Functions
Exports `etnaviv_validate_init` and `etnaviv_cmd_validate_one`. Internal state includes `struct etna_validation_state`, the `etnaviv_sensitive_states` table, a bitmap of sensitive state offsets, and `cmd_length` for allowed fixed-length opcodes. The `EXTRACT` macro decodes generated bitfields.

## Control Flow
Initialization populates a bitmap of sensitive state register ranges. Validation walks the command dwords, decodes opcode, computes packet length, and for LOAD_STATE checks whether the written register range intersects sensitive states. Sensitive state writes require a relocation at the matching submit offset; non-sensitive relocations are warned and skipped. Only a small allowlist of draw/NOP/stall/load-state packet types is permitted.

## State and Persistence
The sensitive-state bitmap is initialized once at module init. Per-submit validation is stateless except for advancing through the relocation array.

## Dependencies and Integration Points
Called from `etnaviv_gem_submit.c` before submission. Depends on generated command stream bitfields, relocation records from the UAPI submit path, and GPU device logging.

## Risks
Parser length bugs can under- or over-scan command buffers. Missing sensitive registers weakens isolation; overly broad ranges reject valid workloads. Relocations must be sorted consistently with command offsets for the advancing pointer logic.

## Test Signals
Submit tests with valid/invalid LOAD_STATE relocations, forbidden opcode rejection, truncated packet rejection, fuzzed command streams, and rate-limited warning coverage are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmd_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.c

## Purpose
Implements a write-combined DMA command buffer suballocator used by etnaviv kernel ring buffers and submitted command buffers.

## Important APIs, Types, and Functions
Defines private `struct etnaviv_cmdbuf_suballoc` with DMA address, CPU mapping, granule bitmap, mutex, waitqueue, and free-space flag. Exports allocation/lifetime (`etnaviv_cmdbuf_suballoc_new/destroy`), IOMMU map/unmap, per-cmdbuf allocation/free, and VA/PA translation helpers.

## Control Flow
The suballocator allocates a 512 KiB DMA WC region split into 4 KiB granules. `etnaviv_cmdbuf_init()` computes a power-of-two region order, finds a free bitmap region, waits up to 10 seconds if none is available, and returns a CPU pointer at the suballocation offset. Free releases the bitmap region and wakes waiters. Mapping delegates to etnaviv IOMMU suballoc VA helpers.

## State and Persistence
The DMA WC allocation persists for the DRM device lifetime. Individual cmdbufs persist until `etnaviv_cmdbuf_free`. Bitmap state tracks granule ownership; `free_space` is a wakeup hint.

## Dependencies and Integration Points
Created in `etnaviv_bind`, mapped into IOMMU contexts, used by GPU ring setup, submit path, and flop reset payload allocation. Depends on DMA mapping APIs and etnaviv MMU helpers.

## Risks
Power-of-two bitmap allocation can fragment capacity. Timeout waiting for space indicates leaked or long-lived command buffers. Missing free causes submit stalls. DMA mask assumptions are enforced in platform probe.

## Test Signals
High-concurrency submit stress, timeout logs, IOMMU mapping validation, command buffer VA/PA debug output, and leak checks around submit completion are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.h

## Purpose
Declares etnaviv command buffer structures and suballocator APIs.

## Important APIs, Types, and Functions
Defines `struct etnaviv_cmdbuf` with suballocator pointer, suballocation offset, CPU address, total size, and used size. Declares suballocator lifecycle, map/unmap, cmdbuf init/free, and address translation functions.

## Control Flow
No executable flow beyond declarations; callers allocate cmdbufs, emit commands through `etnaviv_buffer.h`, translate to GPU VA with a mapping, and free when complete.

## State and Persistence
Documents the state fields maintained by `etnaviv_cmdbuf.c` and command emitters.

## Dependencies and Integration Points
Included by buffer, driver, dump, GEM submit, GPU, MMU, and flop reset code.

## Risks
Consumers must keep `user_size <= size`, use the correct IOMMU mapping for VA translation, and free suballocations once hardware is done.

## Test Signals
Build coverage and submit/ring buffer runtime tests exercise this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.c

## Purpose
Implements the top-level etnaviv DRM driver: module/platform registration, component master binding, DRM device setup, per-open context lifecycle, debugfs, ioctl dispatch, and GEM/PRIME integration.

## Important APIs, Types, and Functions
Important functions include `etnaviv_open`, `etnaviv_postclose`, ioctl handlers for params/GEM CPU prep/fini/info/userptr/waits/perfmon, debugfs show functions, `etnaviv_bind/unbind`, `etnaviv_pdev_probe/remove`, and module init/exit. The `drm_driver` advertises `DRIVER_GEM | DRIVER_RENDER`, ioctl table, PRIME import, fdinfo, debugfs, fops, and version metadata.

## Control Flow
Module init initializes command validation, registers GPU and master platform drivers, and creates a virtual etnaviv platform device when DT has an available Vivante GPU. Probe sets DMA masks/configuration and registers a component master. Bind allocates `drm_device` and private state, initializes xarray/GEM list/cmdbuf suballocator, binds GPU components, initializes available GPUs, and registers the DRM device. Open allocates a file-private context, assigns an xarray ID, creates an IOMMU context, and initializes scheduler entities per GPU. Postclose destroys scheduler entities, drops the MMU context, erases the xarray entry, and frees the context.

## State and Persistence
Driver-private state tracks GPU pointers, command buffer suballocator, global MMU, active contexts xarray, GEM object list, shared-memory GFP mask, and optional flop-reset cmdbuf. State exists while the DRM device is bound.

## Dependencies and Integration Points
Integrates Linux component framework, platform driver/DT matching (`vivante,gc`), DMA masks, DRM core, DRM scheduler, GEM helpers, PRIME, debugfs, etnaviv GPU/MMU/perfmon/GEM submit implementations, and generated validation init.

## Risks
Partial bind failures must unwind suballocator/private/device state correctly. Open error paths must release xarray IDs and MMU contexts; this file currently frees ctx on MMU init failure but the xarray allocation path requires scrutiny. DMA mask assumptions affect command buffer reachability. Device-tree component matching must include all active GPU cores.

## Test Signals
Module load/unload, bind/unbind with multiple GPUs, render-node open/close stress, ioctl validation tests, DMA mask probe failures, debugfs reads, and scheduler entity leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.h

## Purpose
Declares shared top-level etnaviv driver data structures, exported cross-file function prototypes, debug macros, and utility helpers.

## Important APIs, Types, and Functions
Defines `ETNAVIV_SOFTPIN_START_ADDRESS`, `struct etnaviv_file_private`, and `struct etnaviv_drm_private`. Declares GEM, PRIME, buffer, submit, validation, and debugfs functions. Inline helpers include `size_vstruct()` for overflow-safe variable-struct sizing and `etnaviv_timeout_to_jiffies()` for monotonic UAPI timeout conversion.

## Control Flow
No primary runtime flow; inline helpers are used by submit and wait paths. Timeout conversion returns zero for expired absolute monotonic deadlines.

## State and Persistence
Documents per-file context state, global driver-private state, active contexts xarray, GEM list, command buffer suballocator, global MMU, GPU array, and flop reset payload pointer.

## Dependencies and Integration Points
Included across the etnaviv driver. Depends on DRM GEM/UAPI headers, DRM scheduler, xarray, Linux time APIs, and etnaviv MMU/GPU forward declarations.

## Risks
The flexible submit sizing helper must be used consistently to avoid allocation overflow. Timeout semantics are absolute monotonic, so userspace and kernel must agree on clock domain.

## Test Signals
Build coverage, ioctl timeout tests, large submit allocation validation, and context lifecycle tests exercise this header’s contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.c

## Purpose
Creates etnaviv devcoredump files on GPU hangs, collecting registers, MMU state, ring buffer, submitted command buffer, buffer-object physical map, and BO contents.

## Important APIs, Types, and Functions
Module parameter `dump_core` gates one-shot dumping. Internal helpers are `etnaviv_core_dump_header`, register/MMU/memory dump emitters, and `struct core_dump_iterator`. Exported `etnaviv_core_dump()` consumes `struct etnaviv_gem_submit`.

## Control Flow
On first enabled dump, it locks the submit MMU context, computes dump size and object count, allocates vmalloc memory, writes zeroed headers followed by data sections, dumps registers/MMU/ring/cmd, unlocks MMU, optionally writes a BO physical page map, copies each submitted BO, writes an end marker, and hands the buffer to `dev_coredumpv()`.

## State and Persistence
`etnaviv_dump_core` is set false after the first dump unless rearmed through the module parameter. Dump contents persist through the kernel devcoredump mechanism for userspace collection.

## Dependencies and Integration Points
Called by scheduler hang handling. Depends on GPU register accessors, MMU dump helpers, GEM page/vmap helpers, cmdbuf VA translation, devcoredump, and generated state register constants.

## Risks
Large dumps can fail `GFP_NOWAIT` allocation. BO copying races are mitigated by submit ownership but page/vmap failures may leave sparse sections. Register reads must account for power-register address fixups.

## Test Signals
Induced GPU hangs, devcoredump file format parsing, register/MMU/ring/cmd section presence, BO map consistency, and rearming `dump_core` are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.h

## Purpose
Defines the etnaviv devcoredump file section format and declares the core dump entry point.

## Important APIs, Types, and Functions
Defines magic `ETDUMP_MAGIC`, section type enum values (`REG`, `MMU`, `RING`, `CMD`, `BOMAP`, `BO`, `END`), `struct etnaviv_dump_object_header`, `struct etnaviv_dump_registers`, and `etnaviv_core_dump()`.

## Control Flow
No executable flow. `etnaviv_dump.c` writes arrays of these headers and data sections for userspace tools to decode.

## State and Persistence
The structures define persistent dump binary layout exposed through devcoredump.

## Dependencies and Integration Points
Included by dump implementation and scheduler hang handling. Consumers outside the kernel can parse these records.

## Risks
Changing header layout or enum values can break existing dump parsers. Endianness fields are explicitly little-endian and must be populated correctly.

## Test Signals
Compile-time layout usage, devcoredump parser compatibility, and generated dump inspection validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.c

## Purpose
Implements a PPU flop-reset workaround for selected Vivante GPU identities by preparing a small compute payload and emitting command stream state to run it.

## Important APIs, Types, and Functions
Exports `etnaviv_flop_reset_ppu_require`, `etnaviv_flop_reset_ppu_init`, and `etnaviv_flop_reset_ppu_run`. Internal helpers fill input image data, copy a fixed shader instruction sequence, and emit OpenCL/PPU state through command macros. Module parameter `force_flop_reset` can force the workaround when 3D pipe support exists.

## Control Flow
Requirement checking matches chip model/revision against a small database or the force parameter. Init allocates a cmdbuf from the shared suballocator, fills input data and shader bytes, and keeps it for driver lifetime. Run computes the GPU VA of the payload in the active MMU context and emits state that loads uniforms, shader ranges, workgroup configuration, kicker, and shader cache flushes into the GPU ring.

## State and Persistence
Persistent state is `priv->flop_reset_data_ppu`, a suballocated cmdbuf containing input/output image regions and shader code. It is freed on driver unbind.

## Dependencies and Integration Points
Called from GPU initialization/ring setup when chip identity requires it. Depends on command emission helpers, cmdbuf suballocation, active MMU context mapping, generated state headers, and chip feature flags.

## Risks
Hard-coded shader/state values are highly hardware-specific. Running on a chip without required 3D/PPU support can hang; force mode guards only the 3D feature. Init failure or missing payload causes run to skip with an error.

## Test Signals
Boot/init logs on affected model `0x8000` revision `0x6205`, forced-workaround tests, GPU initialization success, ring dumps showing emitted reset commands, and absence of early hangs on affected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.h

## Purpose
Declares the etnaviv PPU flop-reset workaround interface.

## Important APIs, Types, and Functions
Forward-declares `struct etnaviv_chip_identity`, `struct etnaviv_drm_private`, and `struct etnaviv_gpu`; declares `etnaviv_flop_reset_ppu_require`, `etnaviv_flop_reset_ppu_init`, and `etnaviv_flop_reset_ppu_run`.

## Control Flow
No executable flow. GPU initialization uses `require`/`init`; ring initialization uses `run`.

## State and Persistence
The header exposes no state directly; implementation stores payload state in `etnaviv_drm_private`.

## Dependencies and Integration Points
Included by buffer/GPU paths and the implementation. It isolates the workaround from generic command buffer code.

## Risks
Callers must initialize the payload before running the workaround and only run when identity checks require or force it.

## Test Signals
Build coverage and affected-chip initialization paths validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.c

## Purpose
Implements etnaviv GEM buffer object allocation, page pinning, scatter-gather mapping, mmap/fault handling, CPU synchronization, IOMMU VRAM mapping references, debugfs object reporting, object release, and userptr support.

## Important APIs, Types, and Functions
Key functions include `etnaviv_gem_get_pages`, `etnaviv_gem_mmap_offset`, `etnaviv_gem_mapping_get/unreference`, `etnaviv_gem_vmap`, `etnaviv_gem_cpu_prep/fini`, `etnaviv_gem_wait_bo`, `etnaviv_gem_free_object`, `etnaviv_gem_obj_add`, `etnaviv_gem_new_handle`, `etnaviv_gem_new_private`, and `etnaviv_gem_new_userptr`. Important ops tables are shmem and userptr `etnaviv_gem_ops`, VM ops, and DRM GEM object funcs.

## Control Flow
Shmem objects are allocated, initialized with DRM GEM, assigned cache flags, added to the driver GEM list, and exposed as handles. Pages and sg tables are allocated lazily under object lock; cached buffers use DMA map/sync for CPU/device coherency. mmap either sets PFNMAP protections for WC/uncached or redirects cached mappings to shmem. Faults pin/get pages and insert PFNs. IOMMU mapping lookup reuses active or reaped mappings, maps pages when needed, increments use counts, and takes object refs. CPU prep waits or tests reservation fences, then syncs caches; fini syncs back to device. Free removes GEM list entries, unmaps all VRAM mappings, releases ops-specific resources, and destroys the GEM object.

## State and Persistence
Each object tracks flags, visible GPU size, pages, sg table, vmap address, GPU-active count, VRAM mapping list, last CPU prep op, and optional userptr metadata. The driver private GEM list persists objects for debugfs until object release.

## Dependencies and Integration Points
Depends on DRM GEM/shmem/PRIME helpers, dma-resv fences, DMA mapping APIs, VM fault APIs, etnaviv IOMMU, GPU wait helpers, and UAPI flags. Userptr uses long-term GUP and current mm ownership checks.

## Risks
Coherency is delicate: DMA API warnings note possible corruption with concurrent CPU/device access. Mapping reuse races require object and MMU locks in the documented order. Userptr pins are restricted to the creating mm. `last_cpu_prep_op` misuse warns on fini without prep. Object free requires inactive GPU state.

## Test Signals
GEM create/mmap/fault tests for cached/WC/uncached, CPU prep/fini coherency tests, userptr permission and lifetime tests, IOMMU mapping stress with reuse/reap, PRIME interactions, dma-resv wait timeouts, and debugfs object accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.h

## Purpose
Defines etnaviv GEM object, VRAM mapping, userptr, submit, and GEM operation structures shared by memory management and submission code.

## Important APIs, Types, and Functions
Defines `struct etnaviv_gem_userptr`, `struct etnaviv_vram_mapping`, `struct etnaviv_gem_object`, `struct etnaviv_gem_ops`, `struct etnaviv_gem_submit_bo`, and `struct etnaviv_gem_submit`. Inline helpers are `to_etnaviv_bo()` and `is_active()`. Declares submit put, GEM wait/private allocation/object list/pages/mapping APIs.

## Control Flow
No main control flow; the structures are populated by GEM creation, submit ioctl parsing, IOMMU mapping, scheduler jobs, and hang dump paths.

## State and Persistence
The header defines persistent per-object state, per-mapping state, per-submit variable-length BO arrays, scheduler job embedding, MMU contexts, fences, pid, exec state, perfmon requests, and command buffer.

## Dependencies and Integration Points
Included by driver, GEM, PRIME, submit, GPU, MMU, dump, and command parser code. Depends on DRM GEM, dma-resv, DRM scheduler, etnaviv cmdbuf and UAPI headers.

## Risks
`struct etnaviv_gem_submit` ends with a flexible array and must not gain fields after `bos[]`. Mapping `use` counts and object refs must stay balanced. `gpu_active` must reflect scheduler/hardware ownership to avoid freeing active objects.

## Test Signals
Build coverage, submit allocation sizing, BO mapping lifetime tests, hang recovery dumps, and lockdep/refcount checks exercise this header’s contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_prime.c

## Purpose
Implements etnaviv PRIME/dma-buf sharing hooks for sg-table export/import, vmap, pin/unpin, mmap, and imported object release.

## Important APIs, Types, and Functions
Exports `etnaviv_gem_prime_get_sg_table`, `etnaviv_gem_prime_vmap`, `etnaviv_gem_prime_pin`, `etnaviv_gem_prime_unpin`, and `etnaviv_gem_prime_import_sg_table`. Internal ops include `etnaviv_gem_prime_release`, `etnaviv_gem_prime_vmap_impl`, `etnaviv_gem_prime_mmap_obj`, and the imported-object `etnaviv_gem_prime_ops`. Imports the `DMA_BUF` namespace.

## Control Flow
Export sg-table requires local pages already pinned. PRIME pin pins local pages for non-imported objects; unpin currently delegates to the placeholder put-pages path. Import creates a private WC GEM object with PRIME ops, stores the provided sg table, allocates a page array, fills it from the sg table, lockdep-tags the object, and adds it to the GEM list. Vmap maps imported dma-bufs through `dma_buf_vmap`; mmap delegates to `dma_buf_mmap` and drops the reference acquired by generic GEM mmap.

## State and Persistence
Imported objects own a page pointer array but not the pages themselves; release frees the array, unmaps any dma-buf vmap, and calls `drm_prime_gem_destroy` with the sg table.

## Dependencies and Integration Points
Integrated through `drm_driver.gem_prime_import_sg_table` and GEM object funcs in `etnaviv_gem.c`. Depends on DRM PRIME helpers, dma-buf vmap/mmap APIs, and etnaviv GEM private allocation.

## Risks
`get_sg_table` assumes pinning has already happened. Imported pages are borrowed, so release must not unpin them. Vmap lifetime must pair with dma-buf vunmap. Mmap reference dropping must match DRM GEM mmap behavior.

## Test Signals
DMA-buf import/export tests, PRIME mmap/vmap tests, cross-device sharing workloads, object release leak checks, and lockdep class separation for imported GEM locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_prime.c -->
