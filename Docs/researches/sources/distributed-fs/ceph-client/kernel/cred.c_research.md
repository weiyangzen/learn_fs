# sources/distributed-fs/ceph-client/kernel/cred.c

## Purpose
`cred.c` implements the kernel credential lifecycle: allocation, copying for fork/exec, committing changed credentials, aborting unused credentials, RCU-safe destruction, credential comparison for filesystem access, user-count tracking, kernel-service credentials, and LSM override helpers.

## Important APIs, types, and functions
The file owns the credential slab cache `cred_jar`. Public functions include `__put_cred()`, `exit_creds()`, `get_task_cred()`, `cred_alloc_blank()`, `prepare_creds()`, `prepare_exec_creds()`, `copy_creds()`, `commit_creds()`, `abort_creds()`, `cred_fscmp()`, `set_cred_ucounts()`, `cred_init()`, `prepare_kernel_cred()`, `set_security_override()`, and `set_create_files_as()`. Internal helpers include `put_cred_rcu()` and `cred_cap_issubset()`.

The relevant data is `struct cred` and its references to UID/GID values, user namespace, user and ucounts objects, group_info, keyrings, request-key auth, security blob, capability sets, and RCU head.

## Control flow
`prepare_creds()` allocates a new credential object, copies current credentials, resets use count to one, pins group/user/user_ns/keyring/ucount references, clears the security blob, and asks the LSM layer to prepare copied security state. Callers mutate the copy and either `commit_creds()` or `abort_creds()`.

`commit_creds()` verifies the task is not in subjective override state, takes an extra reference for subjective credentials, adjusts dumpability and parent-death signal if IDs/capabilities become less privileged, updates keyring fsuid/fsgid state, increments new user process counts if user or namespace changed, RCU-publishes `real_cred` and `cred`, decrements old process counts, switches credential namespace state, sends proc connector UID/GID events, and drops both old references.

`copy_creds()` shares credentials for new threads when possible. Otherwise it prepares a copy, optionally creates a new user namespace and ucounts for `CLONE_NEWUSER`, handles thread/process keyring inheritance, installs the new object as both objective and subjective credentials for the child, and accounts the process count. `exit_creds()` drops task credential references and cached requested keys. Destruction runs either immediately for `non_rcu` or through `call_rcu()`, then frees LSM, keyrings, group_info, user, ucounts, user namespace, and slab memory.

## State and persistence behavior
Credential objects are refcounted and RCU-published. Task pointers `task->real_cred` and `task->cred` are the authoritative runtime state; old objects remain valid to RCU readers until grace period completion. User process counts and namespace references are adjusted during fork, commit, and free. Keyring references and LSM security blobs are owned by each credential object. There is no filesystem persistence, but credential changes are observable through proc connector events and process access-control behavior.

## Dependencies and integration points
This file integrates with the LSM hooks (`security_prepare_creds()`, `security_cred_free()`, `security_kernel_act_as()`, `security_kernel_create_files_as()`), keyrings, user namespaces, ucounts and RLIMIT_NPROC accounting, proc connector, ptrace/dumpability rules, scheduler task lifecycle, RCU, slab accounting, and filesystem UID/GID access comparisons.

## Risks and edge cases
Credential mutation is security-critical. Callers must never modify published credentials directly and must not call `commit_creds()` while subjective credentials differ from objective credentials. The memory barrier before RCU publication is required so ptrace observes nondumpability before privilege changes. Reference balancing across keys, namespaces, group info, ucounts, and LSM security blobs is subtle, especially on error paths. `cred_cap_issubset()` handles nested user namespace capability semantics; mistakes can make dumpability too permissive or too restrictive. `prepare_kernel_cred()` rejects a NULL daemon and strips keyrings for kernel service credentials.

## Test signals
Test signals include fork thread sharing versus process copy behavior, `CLONE_NEWUSER` success and failure paths, exec credential reset of fs IDs and keyrings, UID/GID changes triggering proc connector events, dumpability changes under privilege drop and capability subset changes, ptrace races, keyring fsuid/fsgid changes, LSM allocation failure rollback, ucounts exhaustion, RCU delayed free behavior, and `cred_fscmp()` ordering across fsuid/fsgid/groups.
