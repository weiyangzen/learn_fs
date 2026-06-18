# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.h

Purpose: Defines the main Xe Linux tracepoint surface for TLB invalidation fences, execution queues, scheduler jobs/messages, hardware fences, MMIO register reads/writes, runtime/system PM transitions, EU stall reads, and max-job-count throttling. This header is consumed through the tracepoint framework and instantiated by the corresponding `CREATE_TRACE_POINTS` translation unit elsewhere in the Xe driver.

Important APIs/types/functions: It declares event classes `xe_tlb_inval_fence`, `xe_exec_queue`, `xe_exec_queue_multi_queue`, `xe_sched_job`, `xe_sched_msg`, `xe_hw_fence`, and `xe_pm_runtime`, then binds concrete events such as `xe_tlb_inval_fence_send/recv/signal/timeout`, `xe_exec_queue_create/submit/reset/kill/stop/resubmit`, `xe_sched_job_create/exec/run/free/timedout/set_error/ban`, `xe_sched_msg_add/recv`, `xe_hw_fence_create/signal/try_signal`, and PM get/put/resume/suspend variants. Standalone `TRACE_EVENT`s include `xe_reg_rw`, `xe_eu_stall_data_read`, and `xe_exec_queue_reach_max_job_count`.

Control flow: Trace calls made by other Xe subsystems expand into `TP_fast_assign` blocks that snapshot device names and selected fields from live structures, followed by `TP_printk` formatting for ftrace/perf consumers. The header ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` outside the include guard, matching Linux tracepoint generation rules.

State and persistence behavior: This file does not mutate persistent driver state. It records transient snapshots of object pointers, fence sequence numbers, GuC IDs/states, job fence errors, batch addresses, MMIO values, and caller symbols. Because events snapshot fields from live objects, call sites must pass valid objects with stable lifetime for the duration of the tracepoint.

Dependencies and integration points: Depends on Linux tracepoint macros plus Xe execution queue, scheduler job, GPU scheduler, GT, GuC execution queue, TLB invalidation, and VM headers. It integrates with call sites across queue scheduling, GuC submission, fence signaling, MMIO, and PM code. Device-name helpers use `dev_name()` through Xe device/tile/GT conversion helpers.

Risks: Tracepoint ABI changes can break userspace tooling that depends on field names or print formats. The event payloads dereference nested pointers such as `q->guc`, `job->q`, `job->fence`, and `mmio->tile`; unsafe or premature tracing around initialization/teardown could crash. Pointer logging is diagnostic-only and subject to kernel pointer formatting policy.

Test signals: Enable ftrace/perf tracepoints under `events/xe/*` and exercise queue creation/submission/reset, TLB invalidation, MMIO access, and runtime PM. KUnit or fault-injection tests around scheduler and GuC paths can assert tracepoints compile and remain available, but functional validation is primarily runtime tracing under real workloads.
