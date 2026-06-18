# sources/distributed-fs/ceph-client/security/tomoyo/tomoyo.c

## Purpose

This is TOMOYO's LSM registration and hook dispatch file. It maps kernel security hooks for exec, file, path, mount, socket, and task lifecycle operations into TOMOYO policy-checking helpers, and initializes TOMOYO task security blobs.

## Important APIs, types, and functions

Public state includes `tomoyo_blob_sizes`, `tomoyo_ss`, and `tomoyo_enabled`. `tomoyo_domain()` returns the current thread's domain and clears stale exec rollback state. Hook implementations include `tomoyo_cred_prepare`, `tomoyo_bprm_committed_creds`, `tomoyo_bprm_creds_for_exec`, `tomoyo_bprm_check_security`, many `tomoyo_path_*` wrappers, `tomoyo_file_open`, `tomoyo_file_fcntl`, `tomoyo_file_ioctl`, mount hooks, socket hook wrappers, `tomoyo_task_alloc`, and `tomoyo_task_free`.

## Control Flow

Initialization registers `tomoyo_hooks`, sets the initial task to `tomoyo_kernel_domain`, initializes memory management, and requests securityfs initialization through `initcall_fs`. Exec handling first loads policy when userspace loader support is enabled, then `tomoyo_bprm_check_security()` either finds the next domain for the initial exec check or checks interpreter read permission in the next domain. Path and file hooks build `struct path` wrappers around VFS arguments and call TOMOYO path, path-number, path2, mkdev, mount, or open helpers. Task allocation inherits the parent's domain and increments references; task free decrements active and saved exec domain references.

## State and Persistence

The task security blob stores `domain_info` and `old_domain_info`. `old_domain_info` persists across exec credential transitions so failed execs can roll back, then is cleared after committed credentials. The global SRCU `tomoyo_ss` protects policy traversal and GC. `tomoyo_enabled` is `__ro_after_init` and controlled by LSM setup.

## Dependencies and Integration Points

It integrates with the Linux LSM framework, task blob allocation, binprm lifecycle, VFS path hooks, socket hooks, mount hooks, TOMOYO policy helpers, and securityfs initialization. Network checks are delegated to `network.c`.

## Risks and Test Signals

Risks include reference count leaks around exec rollback, missing hook coverage for a sensitive operation, path construction using the wrong mount for link/rename, bypassing file-open checks for `__FMODE_EXEC`, and policy loader ordering. Tests should include exec success/failure/interpreter paths, domain inheritance through fork, path operation denial coverage, mount and pivotroot checks, socket hook dispatch, and module boot with TOMOYO enabled/disabled.
