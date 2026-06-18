# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.c

Purpose: sends IOSM modem state notifications to userspace as environment-bearing `KOBJ_CHANGE` uevents from process context.

Important APIs/functions: `ipc_uevent_send()` allocates `struct ipc_uevent_info` with `GFP_ATOMIC`, initializes a work item, stores the target device, formats `IOSM_EVENT=<event>` into a fixed buffer, and schedules the work. `ipc_uevent_work()` builds the `envp` array, calls `kobject_uevent_env()`, logs failure, and frees the work object.

Control flow and state: no persistent state is kept. Each event is a self-contained work item, making the function safe to call from atomic contexts and deferring uevent emission to the system workqueue.

Dependencies and integration points: depends on device/kobject infrastructure, slab allocation, workqueues, and event-string constants from `iosm_ipc_uevent.h`. It is used by IOSM modem state code to notify userspace about readiness, crash, coredump, and timeout states.

Risks and test signals: allocation failure silently drops events; long event strings are truncated to `MAX_UEVENT_LEN`; there is no device lifetime reference beyond the raw pointer stored in work. Tests should trigger each event string, monitor udev/netlink delivery, and exercise teardown-adjacent event sends.
