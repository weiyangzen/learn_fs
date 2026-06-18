# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_types.h

## Purpose

`i915_perf_types.h` defines the shared state model for i915 OA performance streams, metric configurations, platform operation callbacks, OA register groups, and per-GT performance groups. It is included from `i915_drv.h`, so it provides the embedded `struct i915_perf` layout used across the driver.

## Important APIs, types, and functions

Important definitions include perf group IDs (`PERF_GROUP_OAG`, `PERF_GROUP_OAM_SAMEDIA_0`), `enum report_header`, `enum oa_type`, `struct i915_perf_regs`, `struct i915_oa_format`, `struct i915_oa_reg`, `struct i915_oa_config`, `struct i915_perf_stream_ops`, `struct i915_perf_stream`, `struct i915_oa_ops`, `struct i915_perf_group`, `struct i915_perf_gt`, and `struct i915_perf`. There are no functions.

`struct i915_perf_stream` is the central per-fd state: it links to `perf`, uncore, engine, optional context, stream lock, sample flags/size, enable/preemption state, OA config, cached config BOs, pinned context, specific context ID/mask, poll hrtimer/wait queue, periodic sampling settings, OA buffer VMA/vaddr/head/tail/format, NOA wait VMA, and polling period. `struct i915_perf` stores global metric sysfs/IDR state, rate limiters, cached context-image offsets, valid context bit, operation callbacks, supported format mask, and NOA programming delay.

## Control flow

The header does not execute code, but it encodes callback-driven control flow. `i915_perf.c` fills `struct i915_oa_ops` at init based on platform, then stream operations call `enable_metric_set`, `oa_enable`, `read`, `oa_disable`, and validation callbacks. `struct i915_perf_stream_ops` abstracts stream fd operations so future stream types could share open/read/poll/ioctl/release plumbing.

## State and persistence behavior

The structs describe both persistent device-level state and transient stream state. `metrics_idr` and sysfs metric groups persist for the device lifetime or until removed by ioctl. `exclusive_stream` persists while an OA group is claimed and prevents concurrent incompatible streams. The OA buffer state tracks driver-owned head and verified tail instead of trusting hardware head updates. Krefs and RCU in `i915_oa_config` allow configs to outlive removal while streams or query calls still use them.

## Dependencies

The header depends on Linux atomic, hrtimer, llist, poll, sysfs, UUID, waitqueue, and uAPI types; GT engine/SSEU types; register definitions; uncore; and wakeref types. It is intentionally broad because `struct drm_i915_private` embeds `struct i915_perf`.

## Integration points

`i915_perf.c` is the primary implementation user. `i915_drv.h` embeds `struct i915_perf`, GT and engine structures reference `i915_perf_gt` and OA groups, `i915_query.c` reads `metrics_idr` and `i915_oa_config` register arrays, and debugfs touches `noa_programming_delay`.

## Risks

Changing these layouts has wide blast radius because they are embedded in core device/GT objects. Locking comments are part of the contract: `metrics_lock`, per-GT `perf.lock`, `stream->lock`, and `oa_buffer.ptr_lock` cover different concurrency domains. Adding fields without clear ownership can introduce stream teardown races, hrtimer use-after-free, or config lifetime bugs. Format metadata must match report parsing assumptions, including header width and report size.

## Test signals

Build all i915 objects that include `i915_drv.h`, run OA stream open/read/reconfigure tests, dynamic config add/remove/query tests, context filtering tests, and lockdep-enabled stress tests around stream close while polling or reading. ABI-sensitive changes should be checked against Mesa/tool expectations for report sizes and formats.
