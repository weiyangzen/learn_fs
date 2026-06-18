# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_trace.h

## Purpose
Defines MSM GPU tracepoints for submit lifecycle, frequency changes, GEM reclaim, suspend/resume, preemption, MMU preallocation cleanup, and register access. These tracepoints provide low-overhead observability for performance, power, memory pressure, and fault debugging.

## Important APIs, Types, and Functions
Trace events include `msm_gpu_submit`, `msm_gpu_submit_flush`, `msm_gpu_submit_retired`, `msm_gpu_freq_change`, `msm_gmu_freq_change`, `msm_gem_shrink`, `msm_gem_purge_vmaps`, `msm_gpu_suspend`, `msm_gpu_resume`, `msm_gpu_preemption_trigger`, `msm_gpu_preemption_irq`, `msm_mmu_prealloc_cleanup`, and `msm_gpu_regaccess`. The header sets `TRACE_SYSTEM drm_msm_gpu`, `TRACE_INCLUDE_FILE msm_gpu_trace`, and includes `trace/define_trace.h`.

## Control Flow
There is no runtime control flow beyond tracepoint expansion. Producers call generated `trace_msm_*` helpers from submit, retire, devfreq, shrinker, PM, preemption, IOMMU prealloc cleanup, and register access paths. Tracepoint payloads capture submit ids, pid, ring, seqno, timing, frequency, reclaim counts, preemption ring ids, preallocation counts, and register offsets.

## State and Persistence
Tracepoints do not persist driver state. They expose snapshots to ftrace/perf/tracefs consumers. Event fields are typed and formatted through `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

## Dependencies and Integration Points
Depends on Linux tracepoint infrastructure and types from `msm_gem_submit`/ringbuffer headers at inclusion sites. It is instantiated by `msm_gpu_tracepoints.c`. Register helpers in `msm_gpu.h` call `trace_msm_gpu_regaccess`, and several core modules call the other generated helpers.

## Risks
Risks are mostly build and trace ABI issues: changing field types or print formats can break tooling, missing include dependencies can fail trace generation, and high-frequency register access tracing can be noisy when enabled. Tracepoints must remain safe when passed partially initialized submit fields.

## Test Signals
Build with tracepoints enabled, inspect `/sys/kernel/tracing/events/drm_msm_gpu`, enable individual events, submit workloads, trigger devfreq and shrinker activity, and verify events carry expected ring, fence, frequency, and reclaim values.
