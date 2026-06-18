# sources/distributed-fs/ceph-client/security/apparmor/resource.c

Purpose: mediates `setrlimit()` operations under AppArmor profiles and applies profile-defined resource limits during label transitions.

Important APIs, types, and functions: exports `aa_sfs_entry_rlimit`, `aa_map_resource()`, `aa_task_setrlimit()`, and `__aa_transition_rlimits()`. Internal helpers are `audit_cb()`, `audit_resource()`, and `profile_setrlimit()`. It uses generated `rlim_names.h` and architecture-specific `rlim_map[]`.

Control flow: `aa_task_setrlimit()` obtains the target task label, requires `CAP_SYS_RESOURCE` when setting another differently labeled task's limit, otherwise iterates confined profiles and denies hard-limit raises above policy maxima. `__aa_transition_rlimits()` first relaxes soft limits controlled by the old label back toward init-task soft limits, then clamps current hard/soft limits to the new label's maxima and updates CPU timers when needed.

State and persistence: mutates `current->signal->rlim[]` during profile transitions and emits audit records. Policy rlimit settings are read from `rules->rlimits`.

Dependencies and integration: tied to AppArmor rulesets, label iteration, capability checks, audit callbacks, Linux `struct rlimit`, and POSIX CPU timer update code.

Risks and test signals: architecture resource-number mapping must match the compiler's flattened policy order. Cross-label setrlimit behavior depends on a capability fallback. Test signals include hard-limit denial, peer-label audit output, transition clamping, old-policy soft-limit reset, and RLIMIT_CPU timer updates.
