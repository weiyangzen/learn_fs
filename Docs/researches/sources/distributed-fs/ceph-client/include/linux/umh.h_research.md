<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/umh.h -->
# sources/distributed-fs/ceph-client/include/linux/umh.h

Purpose: declares the kernel usermode-helper API for launching userspace programs from kernel context and for globally disabling helper execution during freezer/shutdown-sensitive periods.

Important APIs and types: wait flags `UMH_NO_WAIT`, `UMH_WAIT_EXEC`, `UMH_WAIT_PROC`, `UMH_KILLABLE`, and `UMH_FREEZABLE` control synchronization and signal/freezer behavior. `struct subprocess_info` carries work item, completion, executable path, argv/envp, wait mode, return value, credential-init hook, cleanup hook, and caller data. APIs include `call_usermodehelper()`, setup/exec split helpers, `usermodehelper_disable()/enable()`, lower-level disable-depth setters, and read-lock APIs for callers that need to serialize against disable.

Control flow: callers either invoke `call_usermodehelper()` directly or allocate a `subprocess_info`, customize credentials with `init`, and execute it with a selected wait mode. System suspend/freezer paths can raise disable depth and wait for readers so helpers are not launched in unsafe phases.

State and persistence: each helper request is transient workqueue state with completion/result fields. Global disable depth and read-lock state live in the implementation; no persistent user data is stored.

Dependencies and integration points: depends on GFP allocation, workqueues, completions, credentials, errno, and sysctl integration. It is used by firmware loading, hotplug/modprobe paths, core dumps, request-key, and other kernel-to-userspace escape hatches.

Risks and test signals: risks include deadlocks while waiting for userspace from reclaim/freezer paths, wrong credentials/environment, helper launch while disabled, leaked argv/envp buffers, and unbounded helper spawning. Test wait modes, killable/freezable waits, disable/enable during suspend, credential init failure cleanup, and helper failure return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/umh.h -->
