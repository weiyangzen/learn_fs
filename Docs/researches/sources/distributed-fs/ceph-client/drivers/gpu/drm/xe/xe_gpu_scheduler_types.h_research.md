<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h

## Purpose
`xe_gpu_scheduler_types.h` defines the Xe scheduler extension types layered on top of DRM GPU scheduler.

## Important APIs, types, and functions
`struct xe_sched_msg` is an in-band backend-defined message with list link, opaque private data, and opcode. `struct xe_sched_backend_ops` currently provides `process_msg()`, which may block and owns message cleanup policy. `struct xe_gpu_scheduler` embeds `struct drm_gpu_scheduler`, backend ops, message list, message spinlock, and work item. It aliases `xe_sched_entity` and `xe_sched_policy` to DRM scheduler types.

## Control flow and integration points
There is no executable code. `xe_gpu_scheduler.c` uses these structures to initialize scheduler state and process queued backend messages on the submit workqueue. GuC or other submission backends can embed or extend messages through private data/opcodes.

## State and persistence behavior
Scheduler objects persist for backend scheduler lifetime. Message nodes persist until `process_msg()` handles and frees or otherwise consumes them.

## Dependencies, risks, and test signals
Dependencies include DRM GPU scheduler and Linux list/work types via that include. Risks include backend-private message lifetime ambiguity, opcode namespace conflicts, and blocking `process_msg()` delaying GPU submission work. Test signals include backend message queue tests, scheduler init/fini under pending messages, and timeout/recovery paths using the embedded DRM scheduler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h -->
