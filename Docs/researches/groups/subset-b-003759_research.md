# subset-b-003759 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sched.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sched.c

## Purpose

`v3d_sched.c` implements the Broadcom V3D driver's DRM GPU scheduler backends. It translates scheduler jobs into hardware register programming for binning, rendering, TFU, CSD, cache-clean, and CPU-side pseudo-jobs; maintains per-client and global queue runtime statistics; switches perfmons around hardware jobs; and performs scheduler-wide GPU reset handling on timeouts.

## Important APIs, Types, and Functions

- `v3d_stats_alloc`, `v3d_stats_release`, `v3d_job_start_stats`, and `v3d_job_update_stats`: allocate and update queue statistics protected by a `seqcount`.
- `v3d_bin_job_run`, `v3d_render_job_run`, `v3d_tfu_job_run`, and `v3d_csd_job_run`: scheduler `run_job` callbacks that create IRQ fences, record active jobs, emit tracepoints, update stats, optionally switch perfmon state, and kick hardware by writing queue registers.
- CPU job handlers: `v3d_rewrite_csd_job_wg_counts_from_indirect`, `v3d_timestamp_query`, `v3d_reset_timestamp_queries`, `v3d_copy_query_results`, `v3d_reset_performance_queries`, and `v3d_copy_performance_query` perform synchronous memory/query operations behind the scheduler.
- `v3d_gpu_reset_for_timeout`, `v3d_cl_job_timedout`, and queue-specific timeout callbacks coordinate `drm_sched_stop`, `v3d_reset`, karma accounting, job resubmission, and scheduler restart.
- `v3d_sched_init` and `v3d_sched_fini` initialize/finalize one `drm_gpu_scheduler` per enabled V3D queue with a credit limit of one and a 500 ms timeout.

## Control Flow

Initialization calls `v3d_queue_sched_init` for bin, render, TFU, CPU, and, when supported, CSD and cache-clean queues. Each scheduler entity later invokes the relevant `run_job` callback. Hardware jobs first check whether the finished fence already has an error, install themselves as `queue->active_job`, create an IRQ fence with `v3d_fence_create`, attach it to `job->irq_fence`, trace submission, start stats, and program registers. For CL queues, writing CT0/CT1 queue end addresses starts execution; for TFU, `ICFG` starts; for CSD, CFG0 starts.

CPU and cache-clean jobs are synchronous. They start stats, run local memory or perfmon work, update stats, and return `NULL` because no hardware fence is needed. Indirect CSD CPU jobs rewrite compute workgroup counts and uniform values before the dependent CSD job runs.

Timeout handling first tries to detect forward progress for CL and CSD queues by comparing current address/return address or batch counters. If progress occurred, it returns `DRM_GPU_SCHED_STAT_NO_HANG`; otherwise it locks `reset_lock`, stops all schedulers, resets the GPU, increments global and client reset counters, resubmits jobs, and restarts all schedulers.

## State and Persistence Behavior

Persistent state lives in `struct v3d_dev`: queue schedulers, `active_job` pointers, stats refs, active/global perfmons, reset counters, and reset/scheduler locks. Per-job state includes IRQ and done fences, BO references, perfmon refs, query arrays, and queue-specific arguments. Stats are updated with local-clock timestamps under seqcount while preemption is disabled, allowing sysfs/debug readers to sample them safely. CPU query jobs persist results by writing into mapped BO memory and by replacing syncobj fences.

## Dependencies and Integration Points

This file integrates with DRM GPU scheduler, DMA fences, DRM syncobjs, V3D register macros, perfmon helpers, cache maintenance helpers, BO vmap helpers, reset code, and tracepoints from `v3d_trace.h`. It is fed by `v3d_submit.c`, and completion is driven by IRQ/fence code elsewhere in the V3D driver.

## Risks and Edge Cases

- CPU job handlers assume submit-time validation guaranteed BO counts, offsets, and query array sizes; bad validation can become out-of-bounds BO writes.
- Indirect CSD workgroup multiplication can overflow before assignment to CFG4; only the all-ones result is warned.
- `v3d_switch_perfmon` stops the previous active perfmon and starts the new one around jobs; bad lifetime/ref handling in submit paths could lead to stale perfmon use.
- Timeout progress heuristics can defer reset for workloads that keep changing command pointers while still effectively hung.
- `drm_sched_init` failure after earlier queues requires `v3d_sched_fini`; the cleanup path relies on `sched.ready`.

## Test Signals

Useful signals include IGT submit/timeout/reset tests, perfmon switching tests across mixed queues, CPU query tests validating timestamp/performance BO writes and syncobj replacement, indirect CSD tests for uniform rewrite and CFG4 generation, sysfs stats monotonicity checks, and lockdep coverage for `reset_lock`, queue locks, and BO vmap lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_submit.c

## Purpose

`v3d_submit.c` is the V3D userspace submission front end. It implements the CL, TFU, CSD, and CPU job ioctls; copies and validates user extension payloads; resolves GEM BO handles; attaches reservation and syncobj dependencies; creates scheduler jobs; sequences dependent jobs; and returns completion fences through legacy single syncobjs or the multi-sync extension.

## Important APIs, Types, and Functions

- `v3d_lookup_bos` and `v3d_lock_bo_reservations`: build `job->bo[]`, reserve each BO, and add implicit reservation dependencies to the scheduler job.
- `v3d_job_init`, `v3d_push_job`, `v3d_job_cleanup`, and `v3d_job_put`: common lifetime machinery around `drm_sched_job_init`, krefs, done fences, stats refs, and scheduler push.
- `v3d_get_extensions`: walks the user-provided extension chain and dispatches to multi-sync and CPU-job extension parsers.
- Multi-sync helpers: `v3d_get_multisync_submit_deps`, `v3d_get_multisync_post_deps`, `v3d_put_multisync_post_deps`, and output handling in `v3d_attach_fences_and_unlock_reservation`.
- CPU extension parsers: indirect CSD, timestamp query/reset/copy, and performance query/reset/copy parsers populate `struct v3d_cpu_job`.
- Ioctl entry points: `v3d_submit_cl_ioctl`, `v3d_submit_tfu_ioctl`, `v3d_submit_csd_ioctl`, and `v3d_submit_cpu_ioctl`.

## Control Flow

For GPU work, each ioctl validates padding and flags, optionally parses the extension chain, allocates queue-specific job structures, initializes their scheduler jobs against the calling file's scheduler entity, copies hardware register or CL address arguments, resolves BOs, reserves them, and pushes jobs under `v3d->sched_lock`. CL submission can create a bin job, a render job, and optionally a cache-clean job, wiring bin-to-render and render-to-clean dependencies with `drm_sched_job_add_dependency`. CSD submission similarly pushes CSD then cache-clean. TFU is a single hardware job.

CPU submission first allocates a `v3d_cpu_job`, requires exactly one CPU job extension, checks the submitted BO count against `cpu_job_bo_handle_count`, initializes a CPU scheduler job, and pushes it. For indirect CSD, the CPU job is followed by a dependent CSD job and a dependent cache-clean job; output fences are attached to the cache-clean job rather than the CPU job. Other CPU jobs return the CPU job's done fence.

Error handling unwinds scheduler job init, krefs, BO refs, syncobj refs, and reservations. Success attaches the job fence to each reserved BO as a write fence, unlocks reservations, replaces output syncobjs, and drops local krefs so scheduler completion owns the final references.

## State and Persistence Behavior

Submit-time state is mostly transient, but it creates persistent scheduler/fence effects: BO reservation fences remain on GEM objects, syncobjs are replaced with done fences, and perfmon references persist until job cleanup. `struct v3d_job` owns BO refs, stats refs, perfmon refs, `irq_fence`, `done_fence`, and scheduler state. CPU job query arrays persist until `v3d_cpu_job_free` frees syncobj and perfmon-id storage. Multisync output syncobj refs are consumed after fence replacement.

## Dependencies and Integration Points

The file depends on DRM GEM lookup/reservation helpers, DMA reservation objects, DRM syncobj dependencies, DRM GPU scheduler entities, V3D perfmon lookup, V3D CSD feature detection, BO types from `v3d_drv.h`, tracepoints, and scheduler callbacks in `v3d_sched.c`. Its ioctls are exposed by the V3D DRM driver and are expected by Mesa/userspace.

## Risks and Edge Cases

- Several CPU query parsers do little offset/stride bounds checking in this file; scheduler CPU handlers later write into mapped BOs.
- `v3d_copy_query_info` allocates `kperfmon_ids` using `sizeof(struct v3d_performance_query *)` rather than `sizeof(u32)`, wasting memory and potentially hiding type mistakes.
- Some syncobj dependency errors ignore `-ENOENT`, with TODO comments; behavior should be kept compatible but reviewed for silent dependency loss.
- Extension chains are trusted to terminate; cyclic user `next` pointers can repeatedly copy from user memory until fault or soft lockup unless generic ioctl guards exist elsewhere.
- Failure after indirect CSD setup has two reservation contexts to unwind; null `clean_job` assumptions in generic failure paths need care.

## Test Signals

Exercise all four ioctls with valid and invalid flags, padding, BO counts, multisync counts, missing syncobjs, dependency chains, perfmon conflicts, and CSD-on-non-CSD hardware. CPU query tests should cover timestamp reset/copy, performance reset/copy, indirect CSD rewrite, partial-copy flags, 32/64-bit writes, syncobj replacement, and error unwinding under fault-injected `copy_from_user`, GEM lookup, reservation, and scheduler dependency failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sysfs.c

## Purpose

`v3d_sysfs.c` exposes a read-only `gpu_stats` sysfs attribute for V3D queue activity. It formats per-queue job counts and accumulated runtime so users and test tooling can inspect GPU scheduler utilization outside debugfs.

## Important APIs, Types, and Functions

- `gpu_stats_show`: sysfs show method that samples `local_clock`, iterates `V3D_MAX_QUEUES`, calls `v3d_get_stats`, and writes tab-separated lines with queue name, timestamp, completed jobs, and runtime.
- `DEVICE_ATTR_RO(gpu_stats)`: declares the read-only device attribute.
- `v3d_sysfs_init` and `v3d_sysfs_destroy`: create and remove the attribute group from the DRM device kobject.

## Control Flow

Driver setup calls `v3d_sysfs_init` with the device. Reads call `gpu_stats_show`, which obtains the DRM device from `dev_get_drvdata`, converts it to `struct v3d_dev`, emits a header, and emits one row per queue. Teardown calls `v3d_sysfs_destroy` to remove the group.

## State and Persistence Behavior

The file stores no independent state. It reads persistent queue stats maintained by scheduler code and reports a single timestamp for the whole sample. Runtime values include active in-flight time as of the sampled timestamp if `v3d_get_stats` accounts for active jobs.

## Dependencies and Integration Points

It depends on Linux sysfs, `local_clock`, `v3d_get_stats`, `v3d_queue_to_string`, and the V3D device model. It is an observability endpoint for the scheduler and complements tracepoints/debugfs.

## Risks and Edge Cases

- The fixed sysfs buffer is assumed large enough for all queue rows; adding many queues would require checking output length.
- Stats for uninitialized optional queues still rely on `v3d->queue[queue].stats` being valid.
- Timestamp is in local-clock nanoseconds, not wall time, which is correct for runtime correlation but may surprise scripts.

## Test Signals

Read `/sys/.../gpu_stats` after driver init, submit jobs to several queues, verify the header and queue names, confirm job counts/runtimes increase monotonically, and check that create/remove paths do not leave stale sysfs files across bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace.h

## Purpose

`v3d_trace.h` defines the V3D ftrace event schema used to observe submit ioctls, hardware queue submissions, IRQ completions, CPU jobs, cache cleans, and GPU resets.

## Important APIs, Types, and Functions

- Submit ioctl events: `v3d_submit_cl_ioctl`, `v3d_submit_tfu_ioctl`, `v3d_submit_csd_ioctl`, and `v3d_submit_cpu_ioctl`.
- Hardware submit events: `v3d_submit_cl`, `v3d_submit_tfu`, and `v3d_submit_csd`.
- Completion IRQ events: `v3d_bcl_irq`, `v3d_rcl_irq`, `v3d_tfu_irq`, and `v3d_csd_irq`.
- CPU and maintenance events: `v3d_cpu_job_begin`, `v3d_cpu_job_end`, `v3d_cache_clean_begin`, `v3d_cache_clean_end`, `v3d_reset_begin`, and `v3d_reset_end`.
- `TRACE_INCLUDE_FILE v3d_trace` and final `#include <trace/define_trace.h>` integrate with the kernel tracepoint generator.

## Control Flow

Normal includers get trace prototypes through the include guard. Exactly one C file defines `CREATE_TRACE_POINTS` before including this header to instantiate the tracepoint objects. Runtime callers in submit, scheduler, IRQ, cache, and reset code invoke `trace_v3d_*` helpers generated from these definitions.

## State and Persistence Behavior

Tracepoints persist as static kernel trace event descriptors and only record when enabled by ftrace/perf tooling. Each event stores a compact snapshot such as DRM minor index, fence sequence number, CL address range, CSD CFG fields, CPU job type, or reset device index.

## Dependencies and Integration Points

The header depends on Linux tracepoint infrastructure, DRM device minor indexing, V3D job type enums, and generated trace include path handling. It is consumed directly by `v3d_trace_points.c` and referenced by scheduler, submit, IRQ, reset, and cache code.

## Risks and Edge Cases

- Event fields such as `dev->primary->index` assume a registered primary minor exists at trace time.
- Format changes affect userspace tracing scripts and kernel test expectations.
- Adding a trace event requires updating both caller code and tracepoint instantiation coverage.

## Test Signals

Build with tracing enabled, verify tracepoint generation succeeds, enable `events/v3d/*`, run CL/TFU/CSD/CPU submissions and GPU reset paths, and confirm event payloads include expected sequence numbers, job types, queue labels, and command addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace_points.c

## Purpose

`v3d_trace_points.c` is the tracepoint instantiation unit for V3D. It includes the driver header and, outside sparse checking, defines `CREATE_TRACE_POINTS` before including `v3d_trace.h`.

## Important APIs, Types, and Functions

- `CREATE_TRACE_POINTS`: causes `TRACE_EVENT` declarations in `v3d_trace.h` to emit storage and registration code.
- `#ifndef __CHECKER__`: avoids confusing sparse with generated trace definitions.

## Control Flow

The build compiles this file once into the V3D driver. Other files include `v3d_trace.h` normally and get extern declarations; this file supplies the definitions required by the trace subsystem.

## State and Persistence Behavior

It creates the static tracepoint metadata for the module lifetime and has no runtime logic of its own.

## Dependencies and Integration Points

It depends entirely on `v3d_trace.h`, the Linux trace build system, and `v3d_drv.h` for type visibility. Removing it would leave tracepoint references unresolved.

## Risks and Edge Cases

The primary risk is duplicate or missing tracepoint instantiation. Only one translation unit may define `CREATE_TRACE_POINTS` for this trace header.

## Test Signals

Compile/link the V3D driver with tracing enabled and verify `trace_v3d_*` symbols resolve and ftrace exposes V3D event directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Kconfig

## Purpose

`vboxvideo/Kconfig` declares the VirtualBox DRM/KMS driver option `DRM_VBOXVIDEO`. It controls whether the virtual graphics card driver is built and records its architectural and helper-library dependencies.

## Important APIs, Types, and Functions

- `config DRM_VBOXVIDEO`: tristate option named "Virtual Box Graphics Card".
- Dependencies: `DRM`, `X86`, and `PCI`.
- Selected helpers: DRM client selection, KMS helper, VRAM helper, TTM, TTM helper, and generic allocator.

## Control Flow

When enabled, Kbuild compiles the `vboxvideo` object listed in the local Makefile. The help text recommends module builds so the VM graphics driver can be updated independently of the kernel.

## State and Persistence Behavior

This file has no runtime state. It persists build-time configuration in `.config`, determining whether the PCI module is available.

## Dependencies and Integration Points

It integrates with the DRM Kconfig tree, PCI/X86 platform selection, and helper libraries used by `vbox_drv.c`, `vbox_ttm.c`, and HGSMI/VBVA allocation code.

## Risks and Edge Cases

Missing selected helpers would surface as build failures. The X86 dependency excludes non-x86 VirtualBox graphics users even if the virtual device could theoretically appear elsewhere.

## Test Signals

Build `CONFIG_DRM_VBOXVIDEO=m` and `=y` in x86 DRM configs, verify helper symbols are selected, and confirm non-x86 configs do not offer the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Makefile

## Purpose

`vboxvideo/Makefile` lists the compilation units that form the VirtualBox DRM driver module and ties them to `CONFIG_DRM_VBOXVIDEO`.

## Important APIs, Types, and Functions

- `vboxvideo-y`: includes HGSMI helpers, modesetting protocol helpers, VBVA ring support, PCI driver glue, IRQ, hardware init, KMS mode code, and VRAM memory manager code.
- `obj-$(CONFIG_DRM_VBOXVIDEO) += vboxvideo.o`: builds the composite object when configured.

## Control Flow

Kbuild compiles each listed object and links them into `vboxvideo.o`. The resulting module registers the PCI DRM driver defined in `vbox_drv.c`.

## State and Persistence Behavior

No runtime state. Ordering here only affects link composition; init order is controlled by driver code.

## Dependencies and Integration Points

It must stay synchronized with function declarations in `vbox_drv.h` and Kconfig selections. Removing any object breaks driver paths such as HGSMI buffer allocation or atomic modesetting.

## Risks and Edge Cases

New source files need explicit addition. The list is small, so omissions become link-time undefined references.

## Test Signals

Build the module and verify all exported internal functions resolve, especially `hgsmi_*`, `vbva_*`, `vbox_mode_init`, `vbox_hw_init`, and `vbox_irq_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_base.c

## Purpose

`hgsmi_base.c` implements high-level guest-to-host HGSMI/VBVA commands for VirtualBox graphics: host flags location reporting, capability reporting, configuration queries, and cursor shape updates.

## Important APIs, Types, and Functions

- `hgsmi_report_flags_location`: tells the host where the guest-heap `hgsmi_host_flags` structure resides in VRAM.
- `hgsmi_send_caps_info`: sends VBVA capability bits and warns if the host reports failure.
- `hgsmi_test_query_conf`: probes query-config behavior by expecting a sentinel value round trip.
- `hgsmi_query_conf`: submits `VBVA_QUERY_CONF32` and returns the host-written value.
- `hgsmi_update_pointer_shape`: validates cursor image size, builds `vbva_mouse_pointer_shape`, submits it, and maps VirtualBox status codes to Linux errno.

## Control Flow

Each function allocates an HGSMI buffer from the guest heap with a channel and command id, fills the command structure, submits it through `hgsmi_buffer_submit`, reads back host-updated fields if needed, and frees the buffer. Cursor updates compute AND-mask plus XOR image length when a new shape is supplied and force the visible flag with shape uploads.

## State and Persistence Behavior

The file stores no local state. Persistent effects occur in the host and shared VRAM: capability flags, host flag location, cursor shape, and returned configuration values. Buffers are transient gen_pool allocations.

## Dependencies and Integration Points

It depends on `hgsmi_buffer_alloc/free/submit` from `vbox_hgsmi.c`, VirtualBox status codes from `linux/vbox_err.h`, HGSMI channels, setup commands, and VBVA protocol structures in `vboxvideo.h`. It is used by hardware init, connector mode probing, cursor plane updates, and IRQ setup.

## Risks and Edge Cases

- Host command failures are not always propagated; `hgsmi_send_caps_info` warns but returns success.
- Cursor size calculations must avoid overflow for invalid dimensions, though callers already restrict cursor size.
- `hgsmi_query_conf` returns success even if the host leaves an unsupported sentinel, leaving interpretation to callers.
- The cursor allocation keeps a historical four extra bytes for ABI compatibility; future changes should not remove it casually.

## Test Signals

Run under old and new VirtualBox hosts, verify mode-hint and cursor capability queries, test cursor shape upload with visibility-only and shape data paths, fault-inject HGSMI allocation failures, and confirm host flags location enables IRQ/hotplug processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_ch_setup.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_ch_setup.h

## Purpose

`hgsmi_ch_setup.h` defines HGSMI setup-channel command and host-flag structures used by the guest to tell the VirtualBox host where to write event flags.

## Important APIs, Types, and Functions

- `HGSMI_CC_HOST_FLAGS_LOCATION`: setup command id for host flags location reporting.
- `struct hgsmi_buffer_location`: guest VRAM offset and length pair sent to the host.
- `HGSMIHOSTFLAGS_*`: bits for pending commands, IRQ, VSYNC, hotplug, and cursor capability notifications.
- `struct hgsmi_host_flags`: 16-byte shared flag block written by the host.

## Control Flow

`hgsmi_report_flags_location` sends `struct hgsmi_buffer_location` on the HGSMI setup channel. IRQ code later reads `struct hgsmi_host_flags` at the configured guest-heap offset.

## State and Persistence Behavior

The definitions describe a persistent shared-memory contract. The host owns writes to `host_flags`; the guest reads and clears IRQ state through I/O ports.

## Dependencies and Integration Points

Used by `vbox_drv.h`, `hgsmi_base.c`, `vbox_irq.c`, and hardware init/mode probing. The offsets interact with `GUEST_HEAP_OFFSET` and `HOST_FLAGS_OFFSET` in `vbox_drv.h`.

## Risks and Edge Cases

Changing structure packing, size, or bit values would break the VirtualBox host ABI. IRQ handling also relies on historical behavior where some flags may not be cleared independently.

## Test Signals

Verify packed structure sizes, host flag offset reporting, hotplug/cursor capability IRQ delivery, and no regressions with older hosts that keep hotplug flags set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_ch_setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_channels.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_channels.h

## Purpose

`hgsmi_channels.h` defines numeric HGSMI channel ids for VirtualBox guest-host graphics communication.

## Important APIs, Types, and Functions

- Fixed channels: reserved, HGSMI setup/configuration, VBVA graphics, seamless display modes, and OpenGL.
- String-mapped channel range: `HGSMI_CH_STRING_FIRST` through `HGSMI_CH_STRING_LAST`.

## Control Flow

HGSMI buffer allocation records a channel byte in `hgsmi_buffer_header`. The host routes the submitted buffer based on that channel and the channel-specific command id.

## State and Persistence Behavior

No runtime state. The constants are ABI-stable identifiers in shared buffers.

## Dependencies and Integration Points

Used by all HGSMI command helpers, VBVA ring flushing, modesetting protocol helpers, and cursor/capability submissions.

## Risks and Edge Cases

Values are protocol ABI and must not change. Commands sent on the wrong channel will be ignored or misinterpreted by the host.

## Test Signals

Compile-time inclusion plus runtime smoke tests for HGSMI setup and VBVA commands on a VirtualBox host validate channel routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_channels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_defs.h

## Purpose

`hgsmi_defs.h` defines the generic HGSMI buffer header/tail layout and sequence flag constants used by the VirtualBox guest heap command transport.

## Important APIs, Types, and Functions

- `struct hgsmi_buffer_header`: data size, sequence flags, channel id, channel-specific info, and sequence metadata.
- `struct hgsmi_buffer_tail`: reserved word and checksum field.
- `HGSMI_BUFFER_HEADER_F_SEQ_*`: single/start/continue/end sequence markers.
- `HGSMI_NUMBER_OF_CHANNELS`: fixed 256-channel namespace.

## Control Flow

`hgsmi_buffer_alloc` prepends this header and appends the tail to every guest-heap command. `hgsmi_buffer_submit` writes the header offset to the host I/O port, where the host validates and consumes the buffer.

## State and Persistence Behavior

The structures exist in shared VRAM for the duration of each command allocation. The ABI and packing are persistent contracts with the VirtualBox host.

## Dependencies and Integration Points

Used by `vbox_hgsmi.c` for checksum generation, allocation, free size calculation, and submit offset reporting. Channel values come from `hgsmi_channels.h`.

## Risks and Edge Cases

Packed layout and sizes must remain stable. The current driver only emits single-buffer commands; adding sequences would need new allocation/submission logic and checksum coverage.

## Test Signals

Check structure sizes/offsets, checksum acceptance by the host, allocation/free round trips, and command submission under hosts that validate HGSMI headers strictly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/modesetting.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/modesetting.c

## Purpose

`modesetting.c` contains HGSMI protocol helpers for display mode state outside DRM object setup: reporting per-display screen info, updating absolute input mapping, and querying host-provided mode hints.

## Important APIs, Types, and Functions

- `hgsmi_process_display_info`: sends `VBVA_INFO_SCREEN` with display index, origin, framebuffer offset, pitch, dimensions, bpp, and screen flags.
- `hgsmi_update_input_mapping`: sends `VBVA_REPORT_INPUT_MAPPING` for host pointer/tablet coordinate mapping.
- `hgsmi_get_mode_hints`: sends `VBVA_QUERY_MODE_HINTS` and copies returned `vbva_modehint` entries.

## Control Flow

Each helper allocates a VBVA-channel HGSMI command buffer, fills the protocol structure, submits it, and frees it. Mode hints allocate one command large enough for the query header plus the returned hint array, then check the host return code before copying results.

## State and Persistence Behavior

Persistent state is on the host side: current virtual display layout, input mapping rectangle, and last mode hints. The guest copies hints into `vbox->last_mode_hints` through callers. Allocated command buffers are transient.

## Dependencies and Integration Points

Used by `vbox_mode.c` during atomic modesets and connector probing, and by `vbox_irq.c` hotplug work when host mode hints change. It depends on `hgsmi_buffer_alloc/free/submit`, VBVA structures, and VirtualBox status codes.

## Risks and Edge Cases

- `hgsmi_process_display_info` silently returns if allocation fails, potentially leaving host display state stale.
- Mode hint size is `screens * sizeof(struct vbva_modehint)`; callers clamp screen count to avoid unbounded allocation.
- Host-provided hints require validation before KMS uses positions.

## Test Signals

Validate display info updates during enable, disable, framebuffer offset changes, and disconnected screens; verify input mapping after multi-monitor layout changes; and test mode hint retrieval, unsupported-host failures, and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/modesetting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.c

## Purpose

`vbox_drv.c` is the VirtualBox DRM PCI driver entry point. It probes the VirtualBox graphics PCI device, allocates the DRM device, initializes hardware, VRAM, modesetting, IRQs, registers the DRM device, and implements suspend/resume hooks.

## Important APIs, Types, and Functions

- `vbox_pci_probe`, `vbox_pci_remove`, and `vbox_pci_shutdown`: PCI lifecycle handlers.
- `vbox_pm_suspend`, `vbox_pm_resume`, `vbox_pm_freeze`, `vbox_pm_thaw`, and `vbox_pm_poweroff`: DRM mode-config and PCI power management paths.
- `pciidlist`: matches vendor/device `0x80ee:0xbeef`.
- `driver`: `struct drm_driver` enabling modeset, GEM, atomic, cursor hotspot, GEM VRAM, and fbdev TTM helpers.
- `drm_module_pci_driver_if_modeset`: module registration controlled by the `modeset` parameter.

## Control Flow

Probe first verifies HGSMI support with `vbox_check_supported`, removes conflicting apertures, allocates `struct vbox_private` as a managed DRM device, enables PCI, then calls `vbox_hw_init`, `vbox_mm_init`, `vbox_mode_init`, and `vbox_irq_init`. After successful `drm_dev_register`, it starts generic DRM clients. Failure unwinds IRQ, mode, and hardware setup in reverse order. Remove unregisters DRM, performs atomic shutdown, and finalizes IRQ, mode, and hardware state.

## State and Persistence Behavior

`struct vbox_private` persists as the DRM device private object for the PCI device lifetime. It carries mapped VRAM/guest heap pointers, mode state, work items, locks, and protocol buffers initialized by other files. Suspend saves PCI state and moves to D3hot after DRM helper suspend; resume reenables PCI and restores DRM mode configuration.

## Dependencies and Integration Points

The file depends on PCI, aperture conflict removal, DRM managed allocation, atomic helpers, fbdev/TTM helpers, and internal setup functions from `vbox_main.c`, `vbox_ttm.c`, `vbox_mode.c`, and `vbox_irq.c`.

## Risks and Edge Cases

- `vbox_hw_init` returning `-ENOTSUPP` for missing host mode hints prevents binding to older hosts.
- Resume does not re-run `vbox_hw_init`; it relies on mapped resources and host state surviving PCI power transitions well enough for DRM helper resume.
- Failure paths share `err_hw_fini` for memory-manager and mode-init failures; `vbox_hw_fini` must tolerate partially initialized acceleration state.

## Test Signals

Probe/remove in VirtualBox VMs, suspend/resume, hibernate freeze/thaw, modeset module parameter behavior, fbdev setup, conflicting framebuffer removal, and bind failure on unsupported VBE/HGSMI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.h

## Purpose

`vbox_drv.h` is the central private header for the VirtualBox DRM driver. It declares driver identity, shared constants, `struct vbox_private`, DRM object wrappers, internal function prototypes, and the VBE I/O-port write helper.

## Important APIs, Types, and Functions

- Driver metadata: `DRIVER_NAME`, `DRIVER_DESC`, and version macros.
- VRAM layout macros: `GUEST_HEAP_OFFSET`, `GUEST_HEAP_SIZE`, `GUEST_HEAP_USABLE_SIZE`, and `HOST_FLAGS_OFFSET`.
- `struct vbox_private`: DRM device plus guest heap, VBVA buffer mappings, gen_pool, per-CRTC state, VRAM sizes, host mode hints, hardware lock, hotplug work, input mapping, and cursor data.
- `struct vbox_connector`, `struct vbox_crtc`, and `struct vbox_encoder`: wrappers over DRM connector/CRTC/encoder.
- Internal prototypes for hardware init, mode init, IRQ, memory manager, HGSMI buffer transport, and capability reporting.
- `vbox_write_ioport`: writes VBE index/data pairs with `outw`.

## Control Flow

All implementation files include this header to share the private object model. `vbox_private` is allocated by `devm_drm_dev_alloc`; mode, IRQ, HGSMI, and memory-manager code then fill and consume its fields.

## State and Persistence Behavior

The header defines the driver's long-lived state layout. `hw_mutex` protects mode and acceleration accesses; `hotplug_work` defers mode-hint processing; `cursor_data` caches formatted cursor images; CRTC fields cache last mode geometry for disabled CRTC updates and input mapping.

## Dependencies and Integration Points

It includes Linux genalloc/I/O/IRQ headers, DRM GEM/encoder/VRAM helpers, and VirtualBox protocol headers. It is the integration point between PCI driver glue, hardware setup, HGSMI/VBVA helpers, IRQ handling, and atomic modesetting.

## Risks and Edge Cases

- `struct vbox_private` embeds `struct drm_device` first; changing that requires custom release/container handling.
- VRAM layout macros depend on host protocol assumptions about the adapter information area at the end of VRAM.
- `vbox_write_ioport` performs raw port I/O and must only run on supported x86/PCI systems.
- Shared mutable fields require `hw_mutex` discipline; new callers should not update host mode/VBVA state unlocked.

## Test Signals

Build coverage across all driver objects, lockdep around `hw_mutex`, VRAM layout validation on hosts with different VRAM sizes, and compile checks for container macros and prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_hgsmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_hgsmi.c

## Purpose

`vbox_hgsmi.c` implements the low-level HGSMI guest-heap transport: command buffer allocation, checksum generation, buffer free, and host notification through the HGSMI guest I/O port.

## Important APIs, Types, and Functions

- `hgsmi_hash_process`, `hgsmi_hash_end`, and `hgsmi_checksum`: compute the VirtualBox one-at-a-time hash over command offset, header, and tail prefix.
- `hgsmi_buffer_alloc`: allocates header + payload + tail from the guest `gen_pool`, fills header/tail metadata, and returns the payload pointer.
- `hgsmi_buffer_free`: recovers the header from a payload pointer and frees the full allocation.
- `hgsmi_buffer_submit`: converts the header virtual address to a guest physical/VRAM offset, writes it to `VGA_PORT_HGSMI_GUEST`, and executes a memory barrier.

## Control Flow

Higher-level helpers request a payload buffer with a channel and command id. After payload fill, they submit it, allowing the host to process and possibly modify the buffer. They then read response fields and free the allocation.

## State and Persistence Behavior

The gen_pool owns guest-heap allocation state. Individual command buffers are short-lived shared VRAM records. Submission has persistent host-side effects depending on command type. The memory barrier after `outl` tells the compiler/CPU that the host may have modified shared memory.

## Dependencies and Integration Points

It depends on Linux generic allocator DMA APIs, VirtualBox VBE/HGSMI ports, and header/tail definitions. It is the transport for `hgsmi_base.c`, `modesetting.c`, and `vbva_base.c`.

## Risks and Edge Cases

- All callers must submit/free payload pointers returned by this allocator; arbitrary pointers corrupt gen_pool accounting.
- `total_size = size + header + tail` is not overflow-checked.
- Host processing is synchronous from the driver's perspective; if a host delays writes, response reads could be stale.
- Checksum must match host expectations exactly, including the command offset passed into the hash.

## Test Signals

Allocation/free stress in guest heap, checksum verification against known host implementation, command submission smoke tests, and fault injection for exhausted guest heap or invalid pool mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_hgsmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_irq.c

## Purpose

`vbox_irq.c` handles VirtualBox graphics IRQs and host mode-hint hotplug events. It reads host flags from the shared guest heap, schedules hotplug work, validates host-provided monitor positions, updates connector mode hints, and registers/frees the shared PCI IRQ.

## Important APIs, Types, and Functions

- `vbox_irq_handler`: shared IRQ handler that checks `HGSMIHOSTFLAGS_IRQ`, detects hotplug/cursor capability events, clears IRQs, and returns handled status.
- `vbox_report_hotplug`: schedules the deferred hotplug worker.
- `vbox_update_mode_hints`: queries host mode hints, validates positions, updates connector/CRTC hint fields, reports display blank/disable transitions, and emits KMS hotplug later through the worker.
- `validate_or_set_position_hints`: replaces overlapping or invalid enabled-screen positions with a left-to-right layout.
- `vbox_irq_init` and `vbox_irq_fini`: initialize hotplug work, perform an initial hint update, request/free the PCI IRQ, and flush work.

## Control Flow

Init sets up work, fetches current hints, then registers a shared IRQ. On interrupt, the handler reads host flags from `guest_heap + HOST_FLAGS_OFFSET`; if the IRQ bit is absent, it returns `IRQ_NONE`. Hotplug/cursor flags without VSYNC schedule work, then the handler clears host IRQ state by writing all ones to `VGA_PORT_HGSMI_HOST`. The worker refreshes hints and calls `drm_kms_helper_hotplug_event`.

## State and Persistence Behavior

Persistent guest state includes `vbox->last_mode_hints`, each connector's `mode_hint`, CRTC `x_hint`, `y_hint`, and `disconnected` fields. Host flags are shared memory written by the host and cleared through I/O. Workqueue state persists until flushed in teardown.

## Dependencies and Integration Points

It depends on PCI IRQs, DRM connector iteration/locking, KMS hotplug helpers, HGSMI mode-hint commands, and display-info reporting from `modesetting.c`. Connector mode probing in `vbox_mode.c` consumes the updated hints.

## Risks and Edge Cases

- Historical host bugs leave hotplug/cursor flags set; the VSYNC check is a compatibility workaround.
- `validate_or_set_position_hints` masks dimensions with `0x8fff`, which reflects protocol quirks and must be preserved carefully.
- Hint updates occur under the connection mutex but also send HGSMI display updates; avoid deadlocks with atomic modeset paths.
- `request_irq` uses a shared interrupt, so false positives must return `IRQ_NONE`.

## Test Signals

Hotplug monitor add/remove in a VM, cursor capability changes, invalid/overlapping host hints, IRQ sharing behavior, connector status updates, KMS hotplug uevents, and teardown with pending hotplug work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_main.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_main.c

## Purpose

`vbox_main.c` performs VirtualBox graphics hardware/protocol initialization and finalization. It discovers VRAM size and host capabilities, maps the guest heap and VBVA buffers, initializes the gen_pool transport, reports guest capabilities, and enables per-screen VBVA acceleration buffers.

## Important APIs, Types, and Functions

- `vbox_report_caps`: sends VBVA capability bits, first without and then with mode-hint support for host compatibility.
- `vbox_accel_init` and `vbox_accel_fini`: reserve per-CRTC VBVA buffers at the end of usable VRAM, map them, initialize buffer contexts, and enable/disable them.
- `have_hgsmi_mode_hints`: queries mode-hint and guest-cursor reporting support.
- `vbox_check_supported`: probes VBE/VBox interface IDs through I/O ports.
- `vbox_hw_init` and `vbox_hw_fini`: top-level hardware setup and teardown.

## Control Flow

`vbox_hw_init` reads full VRAM size from the VBE data port, checks ANYX support, reserves PCI BAR 0, maps the guest heap at the end of VRAM, creates a 16-byte-granularity gen_pool over the usable guest heap, verifies HGSMI query behavior, sets available VRAM below the guest heap, queries monitor count, clamps it, requires mode hints and guest cursor reporting, allocates `last_mode_hints`, and enables VBVA acceleration buffers. Finalization disables all VBVA buffers.

## State and Persistence Behavior

It initializes persistent fields in `struct vbox_private`: `full_vram_size`, `available_vram_size`, `any_pitch`, `guest_heap`, `guest_pool`, `num_crtcs`, `last_mode_hints`, `vbva_info`, and `vbva_buffers`. It also establishes host-side capability and VBVA enable state until finalization or VM/device reset.

## Dependencies and Integration Points

It depends on PCI BAR mapping, gen_pool allocation, VBE I/O ports, VirtualBox HGSMI/VBVA protocol helpers, and `vbox_drv.h` VRAM layout macros. Mode setup and IRQ code assume this initialization has completed successfully.

## Risks and Edge Cases

- The code reads `full_vram_size` from the data port after earlier ID probing; the port index state must match host expectations.
- Available VRAM is reduced by guest heap and VBVA buffers; small VRAM configurations could underflow if host reports too many CRTCs.
- Older hosts without 4.3 mode-hint/cursor reporting are rejected.
- `vbox_accel_fini` assumes `vbva_info` and `num_crtcs` were initialized; partial init failure tolerance matters.

## Test Signals

Probe on VirtualBox versions with different capability sets, multiple monitor counts, small/large VRAM sizes, VBVA enable failure paths, capability reporting acceptance, and bind/unbind leak checks for gen_pool and mapped ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_mode.c

## Purpose

`vbox_mode.c` implements the VirtualBox DRM atomic modesetting objects and host update paths. It creates CRTCs, primary/cursor planes, encoders, connectors, synthetic EDID/modes, and atomic callbacks that report modes, framebuffer views, damage rectangles, cursor images, and input mapping to the host through HGSMI/VBVA.

## Important APIs, Types, and Functions

- `vbox_do_modeset`: programs legacy VBE registers for CRTC 0 when possible and sends `VBVA_INFO_SCREEN`.
- `vbox_set_view`: sends `VBVA_INFO_VIEW` describing a CRTC's framebuffer/command-buffer view.
- `vbox_set_up_input_mapping`: decides whether outputs share one framebuffer and computes host pointer mapping dimensions.
- `vbox_crtc_set_base_and_mode`: central locked path that updates cached CRTC geometry, view, mode, and input mapping.
- Plane callbacks: `vbox_primary_atomic_check/update/disable` and `vbox_cursor_atomic_check/update/disable`.
- Object constructors: `vbox_create_plane`, `vbox_crtc_init`, `vbox_encoder_init`, and `vbox_connector_init`.
- Connector helpers: `vbox_get_modes`, `vbox_connector_detect`, and `vbox_fill_modes`.
- `vbox_mode_init` and `vbox_mode_fini`: initialize and clean up DRM mode configuration.

## Control Flow

Mode init configures DRM mode limits and creates one CRTC, encoder, and VGA connector per host-reported screen. Primary plane updates call `vbox_crtc_set_base_and_mode`, then send each damage clip as a VBVA command record in the CRTC's ring buffer. Cursor updates validate ARGB8888 size, copy pixels plus a one-bit alpha mask into `vbox->cursor_data`, and upload cursor shape to the host; cursor disable hides the host cursor when no CRTC still has it enabled. Connector probing reports host flags location, capabilities on CRTC 0, adds no-EDID modes plus a preferred CVT mode based on hints, updates synthetic EDID, and publishes suggested X/Y properties.

## State and Persistence Behavior

Persistent state includes CRTC cached dimensions, framebuffer offsets, cursor enabled flags, input mapping width/height, single-framebuffer mode, connector mode hints, and synthetic EDID properties. Host state is updated through VBE registers, `VBVA_INFO_SCREEN`, `VBVA_INFO_VIEW`, cursor shape commands, input mapping commands, and VBVA damage records.

## Dependencies and Integration Points

The file uses DRM atomic helpers, GEM VRAM and shadow plane helpers, framebuffer damage helpers, EDID/mode helpers, HGSMI/VBVA protocol helpers, and shared `vbox_private` state. It depends on `vbox_main.c` having initialized guest heap and VBVA buffers and on `vbox_irq.c` updating mode hints.

## Risks and Edge Cases

- `vbox_primary_atomic_update` assumes `new_state->fb` is non-null; disable uses a separate callback.
- Cursor image copy does not clear `cursor_data` before building the one-bit mask, so stale mask bits are possible if smaller cursors follow larger ones unless the buffer is otherwise overwritten.
- `vbox_create_plane` returns `ERR_PTR(-EINVAL)` even when `drm_universal_plane_init` failed with another error.
- Input mapping and cross-CRTC modesets rely on cached disabled-CRTC geometry; stale values can resize host windows unexpectedly.
- Host protocols are updated under `hw_mutex`; new callbacks must preserve locking.

## Test Signals

Atomic enable/disable/pageflip tests, multi-monitor layout changes, single large framebuffer vs per-output framebuffer behavior, dirty rectangle propagation, cursor size/hotspot validation, synthetic EDID preferred modes, connector hotplug hint updates, and lockdep around `hw_mutex` during KMS commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_ttm.c

## Purpose

`vbox_ttm.c` initializes the VirtualBox DRM VRAM memory manager over PCI BAR 0 and installs write-combining for better framebuffer performance.

## Important APIs, Types, and Functions

- `vbox_mm_init`: obtains BAR base/size, adds a write-combining MTRR/PAT mapping with `devm_arch_phys_wc_add`, and calls `drmm_vram_helper_init` over `vbox->available_vram_size`.

## Control Flow

Probe calls this after hardware init has reduced available VRAM for the guest heap and VBVA buffers. The DRM VRAM helper then manages GEM VRAM allocations for framebuffers and scanout.

## State and Persistence Behavior

The DRM managed VRAM helper stores memory-manager state in the DRM device for the device lifetime. The write-combining mapping is devm-managed. This file stores no independent state.

## Dependencies and Integration Points

It depends on PCI resources, architecture WC setup, DRM VRAM helpers, and `vbox->available_vram_size` from `vbox_hw_init`. `vbox_mode.c` later allocates/uses GEM VRAM objects from this manager.

## Risks and Edge Cases

- WC setup failure is intentionally ignored for correctness but can reduce performance.
- The VRAM helper must not cover the guest heap/VBVA command area; correctness depends on `available_vram_size` being accurate.
- BAR size smaller than reported available VRAM would make initialization fail or map invalid ranges.

## Test Signals

Probe with different VRAM sizes, framebuffer allocation and mmap tests, write-combining performance/attribute checks, and failure injection for `drmm_vram_helper_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo.h

## Purpose

`vboxvideo.h` is the main VirtualBox graphics protocol header. It documents VRAM layout and defines VBVA ring buffers, guest-to-host command ids, host-to-guest events, configuration indices, screen/mode/cursor/capability structures, mode hints, and input mapping payloads.

## Important APIs, Types, and Functions

- VRAM and adapter constants: `VBOX_VIDEO_MAX_SCREENS`, `VBVA_ADAPTER_INFORMATION_SIZE`, `VBVA_MIN_BUFFER_SIZE`, and interpret/disable command values.
- VBVA ring structures: `vbva_cmd_hdr`, `vbva_host_flags`, `vbva_record`, and `vbva_buffer`.
- Command ids: `VBVA_QUERY_CONF32`, `VBVA_INFO_VIEW`, `VBVA_FLUSH`, `VBVA_INFO_SCREEN`, `VBVA_ENABLE`, `VBVA_MOUSE_POINTER_SHAPE`, `VBVA_INFO_CAPS`, `VBVA_QUERY_MODE_HINTS`, `VBVA_REPORT_INPUT_MAPPING`, and cursor position commands.
- Config indices: monitor count, host heap size, mode hint reporting, guest cursor reporting, cursor capabilities, screen flags, and max record size.
- Payload structures: `vbva_conf32`, `vbva_infoview`, `vbva_infoscreen`, `vbva_enable_ex`, `vbva_mouse_pointer_shape`, `vbva_caps`, `vbva_query_mode_hints`, `vbva_modehint`, and `vbva_report_input_mapping`.

## Control Flow

Implementation files allocate HGSMI buffers containing these structures and submit them on the VBVA channel. The host interprets command ids and modifies result fields, mode hints, or shared ring-buffer offsets according to this ABI.

## State and Persistence Behavior

The header defines both transient command payloads and persistent shared VRAM structures. `vbva_buffer` maintains ring offsets and record queues shared between guest and host; mode hints and host flags persist across hotplug updates; capability and display info commands update host-side state.

## Dependencies and Integration Points

Used across all VirtualBox driver files, especially `vbva_base.c`, `modesetting.c`, `hgsmi_base.c`, `vbox_irq.c`, and `vbox_mode.c`. It is the bridge between DRM/KMS state and the VirtualBox host protocol.

## Risks and Edge Cases

- Packed structure layouts and numeric command values are ABI and must remain stable.
- Ring buffer fields are shared-memory concurrency points with one side updating `free_offset` and the other `data_offset`.
- Large record support depends on partial-record semantics and `VBVA_RING_BUFFER_THRESHOLD`.
- The protocol contains historical misspellings/quirks such as `partial_write_tresh`; renaming fields would break compatibility.

## Test Signals

Compile-time size/offset assertions, host interoperability tests for every command structure used by the driver, ring buffer wrap/partial-record tests, mode hint parsing, cursor shape upload, and multi-monitor display-info updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_guest.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_guest.h

## Purpose

`vboxvideo_guest.h` declares the guest-side helper API for VirtualBox HGSMI/VBVA operations and defines the per-screen VBVA buffer context.

## Important APIs, Types, and Functions

- `struct vbva_buf_ctx`: stores buffer VRAM offset/length, overflow flag, active record pointer, and mapped `vbva_buffer` pointer.
- HGSMI helper prototypes for flags location, capabilities, config queries, cursor shape, display info, input mapping, and mode hints.
- VBVA ring helper prototypes for enable/disable, begin/end update, write, and context setup.

## Control Flow

Mode, IRQ, and hardware setup code call these helpers without needing the low-level buffer header details. `vbva_buffer_begin_update`, `vbva_write`, and `vbva_buffer_end_update` form the record-writing sequence for dirty rectangles.

## State and Persistence Behavior

`vbva_buf_ctx` persists per CRTC while acceleration is enabled. It tracks whether a ring buffer is mapped/enabled, whether an update is active, and whether overflow occurred.

## Dependencies and Integration Points

The header includes Linux genalloc and `vboxvideo.h`, and is included by `vbox_drv.h` and most protocol implementation files. It is the internal API surface between KMS code and transport code.

## Risks and Edge Cases

Callers must pair begin/end update and must not write when `record` is null or overflowed. Buffer offsets and lengths must match host-visible VRAM layout established during hardware init.

## Test Signals

Build checks for prototypes, VBVA begin/write/end sequencing tests, buffer overflow handling, and integration tests from plane damage updates to host flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_guest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_vbe.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_vbe.h

## Purpose

`vboxvideo_vbe.h` defines the legacy VirtualBox/Bochs VBE DISPI I/O-port interface and capability IDs used by the driver for probing and initial mode programming.

## Important APIs, Types, and Functions

- I/O ports: `VBE_DISPI_IOPORT_INDEX`, `VBE_DISPI_IOPORT_DATA`, DAC ports, `VGA_PORT_HGSMI_HOST`, and `VGA_PORT_HGSMI_GUEST`.
- Register indices: ID, X/Y resolution, BPP, enable, bank, virtual width/height, X/Y offset, VBox video command, and framebuffer base high.
- Interface IDs: Bochs IDs, `VBE_DISPI_ID_VBOX_VIDEO`, `VBE_DISPI_ID_HGSMI`, and `VBE_DISPI_ID_ANYX`.
- Enable flags: disabled, enabled, get caps, and 8-bit DAC.

## Control Flow

Probe and feature checks write an ID/register index then read or write data. CRTC 0 modeset code writes resolution, pitch, bpp, enable, and offsets for compatibility with older hosts. HGSMI submission writes command offsets to `VGA_PORT_HGSMI_GUEST`, and IRQ clear writes to `VGA_PORT_HGSMI_HOST`.

## State and Persistence Behavior

The constants address host-emulated device registers. Writes persist in the virtual graphics adapter until changed or reset.

## Dependencies and Integration Points

Used by `vbox_drv.h`, `vbox_main.c`, `vbox_mode.c`, `vbox_hgsmi.c`, and `vbox_irq.c`. Kconfig limits this to X86/PCI where port I/O is valid.

## Risks and Edge Cases

Incorrect index/data ordering can read or write the wrong virtual register. Values are ABI constants shared with VirtualBox and Bochs-compatible hosts.

## Test Signals

Probe supported IDs, legacy first-screen modeset behavior, HGSMI port submission, IRQ clearing, and ANYX capability handling under multiple VirtualBox versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_vbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbva_base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbva_base.c

## Purpose

`vbva_base.c` implements the guest-side VBVA ring-buffer writer used to send graphics update records to the VirtualBox host.

## Important APIs, Types, and Functions

- `vbva_buffer_available`: computes free ring space from host `data_offset` and guest `free_offset`.
- `vbva_buffer_place_data_at`: copies data into the ring, handling wraparound.
- `vbva_buffer_flush`: submits `VBVA_FLUSH` to make the host process records.
- `vbva_write`: writes arbitrary-length record payloads, flushing and respecting partial-write threshold when space is low.
- `vbva_enable`, `vbva_disable`, and `vbva_inform_host`: initialize/reset the ring and send `VBVA_ENABLE`/disable commands.
- `vbva_buffer_begin_update` and `vbva_buffer_end_update`: reserve a record slot, mark it partial, and later mark it complete.
- `vbva_setup_buffer_context`: records each screen's ring offset and length.

## Control Flow

Hardware init sets up each buffer context and calls `vbva_enable`. During a plane damage update, KMS code calls begin, writes a `vbva_cmd_hdr`, and ends the update. Writes flush the host when record slots or data space are low, and set overflow state if progress is impossible.

## State and Persistence Behavior

Persistent shared state lives in `struct vbva_buffer`: ring offsets, record queue indices, host flags, data length, and record flags. The guest owns `free_offset` and record allocation; the host owns `data_offset` and processes completed records. `vbva_buf_ctx` tracks active record and overflow state.

## Dependencies and Integration Points

It depends on HGSMI buffer submission, VBVA channel constants, and protocol structures. `vbox_main.c` enables/disables buffers, and `vbox_mode.c` writes dirty rectangles through this API under `hw_mutex`.

## Risks and Edge Cases

- Pointer arithmetic on `const void *p` relies on compiler extensions; kernel builds allow it but changes should keep types explicit.
- Ring overflow sets `buffer_overflow` and prevents further writes until end/disable.
- Begin/end pairing is required; missing end leaves a partial record for the host.
- Space calculations assume the host updates `data_offset` coherently after flush.

## Test Signals

Unit or VM tests for ring wraparound, full record queue flushing, large writes near `partial_write_tresh`, overflow recovery, enable/disable result handling, and dirty rectangle delivery to the host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbva_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Kconfig

## Purpose

`vc4/Kconfig` declares the Broadcom VC4 DRM driver, HDMI CEC support, and VC4 KUnit tests. It captures platform dependencies and helper libraries needed by the display/audio/GEM driver.

## Important APIs, Types, and Functions

- `config DRM_VC4`: tristate Broadcom VC4 Graphics option for Raspberry Pi/Broadcom platforms or compile-test.
- Dependencies include DRM, firmware availability, common clock, PM, SND, and SND_SOC.
- Selected helpers include DRM client/KMS/display/HDMI/audio helpers, GEM DMA helpers, panel bridge, MIPI DSI, and ALSA HDMI codec pieces.
- `config DRM_VC4_HDMI_CEC`: optional CEC support.
- `config DRM_VC4_KUNIT_TEST`: KUnit test option depending on DRM_VC4 and KUnit.

## Control Flow

Configuration enables the VC4 composite object built by the Makefile. The KUnit option adds mock/test source files to the same object when enabled.

## State and Persistence Behavior

No runtime state. The file controls compiled feature availability in kernel configuration.

## Dependencies and Integration Points

It integrates VC4 with Broadcom/Raspberry Pi platform support, DRM helper subsystems, HDMI audio/CEC support, and KUnit.

## Risks and Edge Cases

The firmware dependency prevents built-in VC4 when Raspberry Pi firmware is a module, except under compile-test constraints. Missing selected helpers surface as build errors.

## Test Signals

Build coverage for platform, compile-test, CEC on/off, KUnit on/off, and `KUNIT_ALL_TESTS` default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Makefile

## Purpose

`vc4/Makefile` defines the VC4 driver object composition and conditionally includes debugfs and KUnit test files.

## Important APIs, Types, and Functions

- `vc4-y`: sorted list of core driver objects, including BO, CRTC, KMS, HDMI, HVS, IRQ, perfmon, plane, render validation, trace, TXP, V3D bridge, and validation code.
- `vc4-$(CONFIG_DRM_VC4_KUNIT_TEST)`: adds mock helpers and pixel-valve muxing tests.
- `vc4-$(CONFIG_DEBUG_FS)`: adds `vc4_debugfs.o`.
- `obj-$(CONFIG_DRM_VC4) += vc4.o`: builds the composite driver.

## Control Flow

Kbuild compiles the listed files into one module/built-in object according to configuration. KUnit tests become part of the driver object only when the test option is enabled.

## State and Persistence Behavior

No runtime state. Link composition determines which init/test symbols are present.

## Dependencies and Integration Points

The file must stay synchronized with Kconfig and internal symbol references. The test entries depend on production VC4 symbols and DRM KUnit helper availability.

## Risks and Edge Cases

Forgetting to add a new source file causes link failures or missing functionality. Since tests are linked into the main object, test-only code must remain guarded by Kconfig.

## Test Signals

Build `CONFIG_DRM_VC4` with and without debugfs and KUnit, verify object lists resolve, and run KUnit suites when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.c

## Purpose

`vc4_mock.c` builds synthetic VC4 and VC5 DRM devices for KUnit tests. It creates mock CRTCs, primary planes, encoders, connectors, HVS state, runs VC4 KMS load, registers the DRM device, and returns a ready `struct vc4_dev`.

## Important APIs, Types, and Functions

- Mock descriptors: `vc4_mock_output_desc`, `vc4_mock_pipe_desc`, and `vc4_mock_desc` describe pixel valves and their outputs.
- Static mock topologies: `vc4_mock` and `vc5_mock` model VC4/VC5 CRTC-output combinations.
- `__build_one_pipe` and `__build_mock`: create dummy primary plane, CRTC, and outputs for each pipe.
- `__mock_device`: allocates KUnit device/DRM device, sets generation, allocates HVS, builds topology, loads KMS, registers DRM, and registers cleanup action.
- Public helpers: `vc4_mock_device` and `vc5_mock_device`.

## Control Flow

Tests call a mock-device helper. The helper allocates managed test resources, constructs the topology from the generation-specific descriptor, invokes production `vc4_kms_load`, registers the device so atomic helpers behave normally, and arranges `drm_dev_unregister` as a KUnit cleanup action.

## State and Persistence Behavior

All state is test-scoped and mostly DRM-managed or KUnit-managed. The returned `vc4_dev` contains mock KMS objects, HVS state, generation marker, and a registered DRM device until test teardown.

## Dependencies and Integration Points

It depends on DRM KUnit helpers, VC4 production data objects (`bcm2835_*`, `bcm2711_*`), mock CRTC/output/plane helpers, `__vc4_hvs_alloc`, and `vc4_kms_load`.

## Risks and Edge Cases

- Mock descriptors must reflect production hardware mux constraints; stale topology reduces test value.
- Registering a DRM device inside KUnit requires reliable cleanup to avoid leakage across tests.
- Production KMS load may gain dependencies not modeled by the mock device.

## Test Signals

The PV muxing KUnit suites are the primary consumers. Build and run both VC4 and VC5 mock-device paths, verify all expected encoders/connectors exist, and ensure KUnit cleanup unregisters devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.h

## Purpose

`vc4_mock.h` declares the VC4 KUnit mock helpers and small wrapper structs used by mock CRTC/output construction and atomic-state manipulation.

## Important APIs, Types, and Functions

- `vc4_find_crtc_for_encoder`: inline helper that asserts a single possible CRTC and returns it.
- `struct vc4_dummy_crtc` and `struct vc4_dummy_output`: test wrappers around production `vc4_crtc`, `vc4_encoder`, and DRM connector.
- Constructors: `vc4_dummy_plane`, `vc4_mock_pv`, `vc4_dummy_output`, `vc4_mock_device`, and `vc5_mock_device`.
- Atomic helpers: `vc4_mock_atomic_add_output` and `vc4_mock_atomic_del_output`.

## Control Flow

KUnit tests include this header to build a mock device and manipulate outputs in atomic states without depending on physical hardware.

## State and Persistence Behavior

No state is stored in the header, but it defines test object layouts used for DRM-managed allocations and container conversions.

## Dependencies and Integration Points

It includes `vc4_drv.h` and is shared by all VC4 KUnit mock/test files.

## Risks and Edge Cases

The inline CRTC lookup asserts exactly one possible CRTC; tests for shared encoders would need a different helper. Wrapper layout must stay compatible with production `vc4_encoder` and `vc4_crtc` expectations.

## Test Signals

Compile all KUnit mock files, run PV muxing suites, and add coverage when production encoder/CRTC structures change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_crtc.c

## Purpose

`vc4_mock_crtc.c` constructs dummy VC4 CRTCs for KUnit by wrapping production CRTC state management and atomic check callbacks around `__vc4_crtc_init`.

## Important APIs, Types, and Functions

- `vc4_dummy_crtc_helper_funcs`: uses production `vc4_crtc_atomic_check`.
- `vc4_dummy_crtc_funcs`: uses production state reset/duplicate/destroy functions.
- `vc4_mock_pv`: allocates `vc4_dummy_crtc` with DRM managed memory and initializes it with supplied CRTC data and primary plane.

## Control Flow

Mock topology construction creates a primary plane, then calls `vc4_mock_pv` for each pixel valve. The resulting CRTC participates in production atomic checking while avoiding hardware register setup.

## State and Persistence Behavior

The dummy CRTC is DRM-managed for the mock device lifetime. Its state is production `vc4_crtc_state`, allowing tests to inspect assigned HVS channels.

## Dependencies and Integration Points

It depends on DRM atomic helper vtables, KUnit assertions, `__vc4_crtc_init`, and production VC4 CRTC data.

## Risks and Edge Cases

If production CRTC init gains mandatory hardware resources, the mock may need new stand-ins. The helper currently supplies no enable/disable callbacks, so tests should remain check-only unless extended.

## Test Signals

PV muxing tests should create all mock CRTCs successfully and exercise `vc4_crtc_atomic_check` through `drm_atomic_check_only`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_output.c

## Purpose

`vc4_mock_output.c` constructs dummy encoders/connectors for KUnit and provides helpers to add or remove outputs in DRM atomic state.

## Important APIs, Types, and Functions

- `vc4_dummy_output`: allocates a `vc4_dummy_output`, initializes a DRM encoder with a VC4 encoder type, initializes a DRM connector, and attaches them.
- `default_mode`: 640x480 mode used for test output enablement.
- `vc4_mock_atomic_add_output`: finds an encoder by VC4 type, gets its CRTC, attaches connector state, sets mode, and marks the CRTC active.
- `vc4_mock_atomic_del_output`: marks the CRTC inactive, clears mode, and detaches connector state.

## Control Flow

Mock device construction creates outputs. Tests allocate an atomic state, call add/del helpers for encoder combinations, then run `drm_atomic_check_only` to exercise production muxing logic.

## State and Persistence Behavior

Output objects are DRM-managed. Atomic helper calls mutate only the provided atomic state until tests call swap-state for bug-regression scenarios.

## Dependencies and Integration Points

It depends on DRM atomic/connector/encoder helpers, `vc4_find_encoder_by_type`, mock header utilities, and production VC4 encoder type values.

## Risks and Edge Cases

The helpers return `-EDEADLK` to let callers restart atomic acquisition; tests must handle backoff correctly. The default mode is simple and may not cover mode-dependent constraints.

## Test Signals

KUnit add/remove output paths for every encoder type, EDEADLK retry coverage, connector/CRTC state correctness, and muxing checks after `drm_atomic_check_only`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_plane.c

## Purpose

`vc4_mock_plane.c` creates dummy primary planes for VC4 KUnit mock devices.

## Important APIs, Types, and Functions

- `vc4_dummy_plane`: asserts the requested plane type is primary and delegates to `drm_kunit_helper_create_primary_plane`.

## Control Flow

Mock pipe construction calls this before creating the dummy CRTC. The returned DRM plane is attached to the CRTC by `vc4_mock_pv`.

## State and Persistence Behavior

The plane is KUnit/DRM-helper managed for the test lifetime. No file-local state exists.

## Dependencies and Integration Points

It depends on DRM KUnit helpers and the mock header. It intentionally only supports `DRM_PLANE_TYPE_PRIMARY` because the muxing tests do not need overlay/cursor planes.

## Risks and Edge Cases

Tests requesting non-primary planes will assert. Production code changes that require plane formats/modifiers in atomic checks may need richer mock plane setup.

## Test Signals

Build KUnit mocks and create every mock VC4/VC5 pipe; failures here surface as mock-device construction assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_test_pv_muxing.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_test_pv_muxing.c

## Purpose

`vc4_test_pv_muxing.c` is a KUnit test suite for VC4/VC5 HVS FIFO and pixel-valve muxing. It validates legal encoder-to-channel assignments, rejects illegal output combinations, and captures regressions around active FIFO stability and unnecessary CRTC state acquisition.

## Important APIs, Types, and Functions

- `check_fifo_conflict`: verifies no HVS FIFO channel is assigned twice in global state.
- Encoder constraint tables: `vc4_encoder_constraints` and `vc5_encoder_constraints`.
- `check_channel_for_encoder`: confirms an encoder's assigned channel is enabled and allowed by the generation-specific constraints.
- Parameter arrays: valid and invalid VC4/VC5 output combinations.
- Test bodies: `drm_vc4_test_pv_muxing`, `drm_vc4_test_pv_muxing_invalid`, and VC5 bug regression tests for subsequent CRTC enable, stable FIFO, and avoiding too many CRTC states.
- `kunit_test_suites`: registers VC4 valid/invalid, VC5 valid/invalid, and VC5 bug suites.

## Control Flow

Each parameterized test builds a mock VC4 or VC5 device, allocates a DRM atomic state with deadlock retry handling, enables or disables requested mock outputs, runs `drm_atomic_check_only`, and inspects VC4 global HVS/CRTC state. Valid cases expect success, no FIFO conflicts, and allowed channel assignments. Invalid cases expect atomic check failure. Bug tests perform staged atomic commits/checks to ensure enabling a second HDMI uses a different FIFO, disabling one output does not move the other active output, and enabling HDMI1 does not pull in HDMI0 CRTC state.

## State and Persistence Behavior

Most tests inspect transient atomic state. Bug regressions use `drm_atomic_helper_swap_state` to persist a first checked state before testing a subsequent transition. Test-private state stores the mock device pointer in `struct pv_muxing_priv`.

## Dependencies and Integration Points

The suite depends on mock device helpers, DRM KUnit/atomic helpers, production VC4 KMS/HVS state, `vc4_find_encoder_by_type`, `vc4_hvs_get_new_global_state`, and production muxing logic in VC4 atomic checks.

## Risks and Edge Cases

- The exhaustive-looking parameter lists are hand-maintained; new encoder types or muxing rules require updates.
- Some VC5 valid cases are duplicated, which increases runtime without adding coverage.
- Tests are check-focused and do not exercise hardware programming paths.
- Deadlock retry handling must clear atomic state correctly to avoid false failures.

## Test Signals

Run `vc4-pv-muxing-combinations`, `vc5-pv-muxing-combinations`, and `vc5-pv-muxing-bugs` through KUnit. Failures indicate regressions in HVS channel assignment, constraint enforcement, state reuse, or active FIFO stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_test_pv_muxing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_bo.c

## Purpose

`vc4_bo.c` implements VC4 GEM buffer-object management for the pre-VC5 VC4 driver. It allocates contiguous DMA-backed GEM objects, caches recently freed kernel BOs, tracks BO labels/statistics, supports userspace purgeable BOs, exposes create/mmap/shader/tiling/label ioctls, and defines GEM object operations.

## Important APIs, Types, and Functions

- BO stats/labels: `bo_type_names`, `vc4_bo_stats_print`, `vc4_get_user_label`, `vc4_bo_set_label`, and `vc4_label_bo_ioctl`.
- Kernel BO cache: `vc4_get_cache_list_for_size`, `vc4_bo_get_from_cache`, `vc4_free_object`, `vc4_bo_cache_free_old`, `vc4_bo_cache_purge`, timer/work callbacks, and `vc4_bo_cache_init/destroy`.
- Purgeable userspace cache: `vc4_bo_add_to_purgeable_pool`, `vc4_bo_remove_from_purgeable_pool`, `vc4_bo_userspace_cache_purge`, `vc4_bo_purge`, `vc4_bo_inc_usecnt`, and `vc4_bo_dec_usecnt`.
- Creation paths: `vc4_create_object`, `vc4_bo_create`, `vc4_bo_dumb_create`, `vc4_create_bo_ioctl`, and `vc4_create_shader_bo_ioctl`.
- Mapping/export operations: `vc4_prime_export`, `vc4_gem_object_mmap`, `vc4_fault`, and `vc4_gem_object_funcs`.
- User ioctls: mmap offset query, tiling set/get, shader BO creation, dumb create, generic BO create, and label assignment.

## Control Flow

Initialization creates label slots, initializes `bo_lock`, BO cache lists, timer/work, and managed destroy action. Allocation first rounds size to pages and tries a same-size cached BO; otherwise it allocates via `drm_gem_dma_create`, purging kernel then userspace caches on DMA allocation failure. User-visible BO ioctls set `madv = VC4_MADV_WILLNEED` and create GEM handles. Shader BO creation copies user code, zeroes padding, validates the shader before handle exposure, and disallows writable mmap/export of validated shader BOs.

On final GEM unref, `vc4_free_object` removes purgeable entries if needed, refuses to cache imported/named/purged objects, frees validated shader metadata, resets BO state, puts reusable DMA BOs into size/time cache, relabels them as kernel cache, and expires old cache entries. Purgeable logic moves `DONTNEED` BOs into a separate list when not in use and can free their DMA memory under pressure; later mmap faults on purged BOs return SIGBUS.

## State and Persistence Behavior

Persistent driver state includes dynamic `bo_labels`, allocation counters, kernel BO cache lists indexed by page count, cache timer/work, purgeable list counters, and per-BO `madv`, `usecnt`, `validated_shader`, tiling flag, label, free time, and DMA mapping. Exporting a BO increments use count and effectively makes it unpurgeable.

## Dependencies and Integration Points

The file depends on DRM GEM DMA helpers, dma-buf export, DRM vma mmap helpers, debugfs, VC4 shader validation, VC4 V3D bin BO acquisition, VC4 UAPI structs, DMA allocation, timers/workqueues, and driver generation checks. It is used by VC4 ioctl dispatch and KMS framebuffer paths.

## Risks and Edge Cases

- This code explicitly rejects `vc4->gen > VC4_GEN_4`; VC5 uses different memory management assumptions.
- Purgeable list removal deliberately drops/reacquires locks; races are mitigated with `list_del_init`, `madv_lock`, and `usecnt`, but changes here are high risk.
- Kernel BO cache can retain sensitive data; user BO creation avoids unzeroed cache reuse, while shader BO creation zeroes padding after copying.
- `bo_page_index(size)` assumes nonzero page-rounded size.
- Label slot management is linear and user labels are freed when counts drop to zero; stats updates require `bo_lock`.
- Purged BO mmap faults intentionally SIGBUS, so userspace must honor MADV results.

## Test Signals

Run VC4 GEM ioctl tests for BO create/mmap/dumb/shader/tiling/label, shader validation race tests, dma-buf export rejection for shader BOs, purgeable MADV pressure tests, SIGBUS on purged mmap access, BO cache reuse/expiry tests, debugfs `bo_stats`, fault injection for DMA allocation failure, and lockdep/KCSAN around `bo_lock`, `purgeable.lock`, and `madv_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_bo.c -->
