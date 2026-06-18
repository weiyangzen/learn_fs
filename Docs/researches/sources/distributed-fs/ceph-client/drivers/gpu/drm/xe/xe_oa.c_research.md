
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.c

## Purpose

`xe_oa.c` implements Xe Observability Architecture performance counter streams. It initializes OA units and formats, manages dynamic metric configurations, opens anon stream file descriptors, programs OA/OAR/OAC/OAM hardware through MMIO and command batches, reads OA circular buffers, and exposes config/status/info operations through stream ioctls.

## Important APIs, Types, and Functions

- Internal config/state: `struct xe_oa_config`, `struct xe_oa_open_param`, `struct xe_oa_config_bo`, `struct xe_oa_fence`, and static `oa_formats[]`.
- Public entry points: `xe_oa_init()`, `xe_oa_register()`, `xe_oa_stream_open_ioctl()`, `xe_oa_add_config_ioctl()`, `xe_oa_remove_config_ioctl()`, `xe_oa_timestamp_frequency()`, and `xe_oa_unit_id()`.
- Stream file operations: `xe_oa_read()`, `xe_oa_poll()`, `xe_oa_ioctl()`, `xe_oa_mmap()`, and `xe_oa_release()`.
- Stream lifecycle: `xe_oa_stream_init()`, `xe_oa_stream_open_ioctl_locked()`, `xe_oa_stream_enable()`, `xe_oa_stream_disable()`, `xe_oa_stream_destroy()`, and `xe_oa_destroy_locked()`.
- Hardware programming: `xe_oa_enable_metric_set()`, `xe_oa_disable_metric_set()`, `xe_oa_enable()`, `xe_oa_disable()`, `xe_oa_configure_oa_context()`, `xe_oa_emit_oa_config()`, and `xe_oa_submit_bb()`.
- Config validation: `decode_oa_format()`, `xe_oa_user_extensions()`, `xe_oa_alloc_regs()`, and address validators for flex, B-counter, and mux registers.

## Control Flow

Device initialization enables OA only for GuC submission, non-VF devices, and Gen12+ platforms. It initializes per-GT OA units, assigns engines to OA units, selects supported formats, and later registers a `metrics` sysfs directory. Userspace opens a stream through the observation ioctl by passing extension properties. The open path validates privileges, OA unit, format, exec queue, sampling mode, buffer size, syncs, and exclusivity, then allocates a stream, OA buffer, kernel exec queue, forcewake/runtime PM refs, and initial metric config.

When enabled, the stream initializes OA buffer registers, programs OA control/debug/context registers, emits metric register loads via MI LRI batches, optionally disables preemption/timeslicing for a target exec queue, and starts an hrtimer for sampling streams. Reads poll/check the hardware tail, avoid partially landed reports by checking report id/timestamp, copy reports to userspace, clear consumed report headers, and advance OAHEADPTR. Config ioctls can switch metric sets by emitting a new config batch and using a delayed software fence to signal when NOA programming is active.

## State and Persistence Behavior

`struct xe_oa` persists on the device and owns supported format bits, the dynamic metrics IDR, `metrics_kobj`, and monotonically assigned OA unit ids. Each GT owns OA units protected by `gt_lock`; each OA unit permits one `exclusive_stream`. Each stream owns PM/forcewake refs, OA buffer BO, cached head/tail pointers, poll timer, sync entries, active config ref, cached config BOs, last fence, optional exec queue ref, and anon FD lifetime. Dynamic configs persist in `metrics_idr` and sysfs until removed or device teardown.

## Dependencies and Integration Points

OA integrates with the top-level observation ioctl, Xe query OA-unit reporting, DRM syncobj/sync entries, anon inodes, scheduler jobs, GGTT-pinned BOs, forcewake/runtime PM, MMIO/MCR registers, GuC RC/workarounds, hardware engine topology, and sysfs metrics. It relies on UAPI format encodings in `xe_drm.h`.

## Risks and Edge Cases

- OA is privilege-sensitive; sampling and config changes are gated by `xe_observation_paranoid`/`perfmon_capable`, while query-only OAR/OAC can be less privileged.
- Tail processing assumes OA writes land in order; partial report handling is defensive but hardware-order dependent.
- OA unit access is exclusive; teardown must clear `exclusive_stream` under GT lock and restore preemption/timeslice settings.
- Config register validation must stay current with platform MMIO allowlists.
- `xe_oa_emit_oa_config()` has point-of-no-return behavior after creating a software fence and cleaning syncs.
- Buffer mmap is read-only/private and maps system-memory pages directly; permission flag mistakes could expose writable counter buffers.

## Test Signals

Signals include OA query enumeration, stream open/close with privilege matrix, invalid extension/property fuzzing, dynamic config add/remove/sysfs id tests, OA buffer read/poll/mmap behavior, overrun/status reporting, config switch sync signaling, forced job/allocation failures, engine/OA-unit assignment tests, and platform format/address allowlist validation.
