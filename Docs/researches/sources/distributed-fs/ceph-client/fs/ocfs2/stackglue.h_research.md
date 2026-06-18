# sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.h

Purpose: declares the public contract between OCFS2 filesystem code, the stackglue core, and cluster stack plugins. It hides stack-specific lock status block layouts behind common OCFS2 types and defines the callback surface a plugin must implement.

Important APIs and types: key definitions are `struct ocfs2_protocol_version`, `struct fsdlm_lksb_plus_lvb`, `struct ocfs2_dlm_lksb`, `struct ocfs2_locking_protocol`, `struct ocfs2_cluster_connection`, `struct ocfs2_stack_operations`, and `struct ocfs2_stack_plugin`. It also defines `DLM_LKF_LOCAL`, `GROUP_NAME_MAX`, and `CLUSTER_NAME_MAX`, and declares all cluster connect/disconnect, DLM lock, LVB, plock, protocol, and plugin registration functions.

Control flow: the header has no active control flow, but it establishes that filesystem code calls `ocfs2_cluster_connect`, then uses `ocfs2_dlm_lock` and related wrappers without inspecting stack-specific lksb internals. Stack plugins fill `ocfs2_stack_operations`; their connect callbacks must not return until recovery notifications and lock processing are operational.

State and persistence behavior: `ocfs2_cluster_connection` stores per-mount runtime state: group name, cluster name, negotiated protocol version, recovery callback and private data, plugin lockspace pointer, and plugin-private state. `ocfs2_dlm_lksb` embeds either o2dlm or fsdlm status storage plus the owning connection pointer. No on-disk state is represented directly.

Dependencies and integration points: includes Linux DLM public headers and OCFS2 DLM API definitions. It is included by filesystem lock glue, stack implementations, mount code, and sysfs setup. The `ocfs2_kset` export declared here links stackglue sysfs to per-device sysfs created by `super.c`.

Risks: the union size and embedded LVB padding must remain sufficient for every supported stack lock status block. Callback contracts are strong: disconnect must not return while a plugin can still reference the connection. The fake `DLM_LKF_LOCAL` flag must not collide with upstream DLM flags. Any protocol version mismatch is a mount-safety issue.

Test signals: build coverage for both o2cb and user stack plugins, lock/unlock/LVB operations through the opaque `ocfs2_dlm_lksb`, protocol negotiation with incompatible major/minor versions, stack plugins with NULL `.plock`, and module unload while no active connection exists.
