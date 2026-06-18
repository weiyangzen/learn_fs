# sources/distributed-fs/ceph-client/include/trace/events/workqueue.h

Purpose: Defines workqueue tracepoints for queueing, activation, execution start, and execution end.

Important APIs/types/functions: Provides `workqueue_queue_work`, `workqueue_activate_work`, `workqueue_execute_start`, and `workqueue_execute_end`, capturing work struct pointer, function pointer, target CPU, workqueue pointer/name, and execution context.

Control flow: Workqueue core emits queue/activation events before execution and start/end events around worker callback invocation. Trace entries snapshot callback identity for latency and ordering analysis.

State/persistence: Workqueue state remains in core structures; traces persist lifecycle observations.

Dependencies/integration: Integrated with kernel workqueue core, ftrace, perf, and latency tools.

Risks: Workqueue paths are hot and highly concurrent. The work item may be reused quickly, so trace consumers must interpret pointer identity with timestamps.

Test signals: Enable `workqueue:*` during workqueue selftests or driver activity and verify queue/execute event correlation.
