# sources/distributed-fs/ceph-client/security/apparmor/include/resource.h

Purpose: declares AppArmor mediation and transition handling for POSIX resource limits.

Important APIs/types: `struct aa_rlimit` contains a mask of controlled hard limits and `limits[RLIM_NLIMITS]`. `aa_map_resource()` maps kernel resource indices to AppArmor policy indices. `aa_task_setrlimit()` mediates `setrlimit` against a subject label and target task. `__aa_transition_rlimits()` applies profile rlimit changes across exec/profile transitions. `aa_sfs_entry_rlimit[]` exports supported rlimit names to apparmorfs.

Control flow: LSM `task_setrlimit` obtains the current label and calls `aa_task_setrlimit()` for confined labels. Exec commit invokes `__aa_transition_rlimits(old, new)` after label change is committed to reset soft limits and enforce new hard limits.

State and persistence: rules live in profile rulesets; the running process state is the kernel rlimit table. `aa_free_rlimit_rules()` is a no-op because this structure has no dynamic allocations.

Dependencies and integration: depends on Linux `resource.h`, task credentials, profile rulesets, and apparmorfs feature reporting. Risks include inconsistent resource index mapping and surprise persistence because removing policy does not restore earlier rlimits. Test with profile transitions, per-resource allow/deny, inherited limits after exec, and policy removal after confinement.
