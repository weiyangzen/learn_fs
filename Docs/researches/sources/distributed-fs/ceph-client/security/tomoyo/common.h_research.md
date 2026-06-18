# sources/distributed-fs/ceph-client/security/tomoyo/common.h

## Purpose

`common.h` is the shared TOMOYO internal contract. It defines constants, enumerations, policy object layouts, request payloads, namespace/profile/domain state, securityfs I/O cursors, exported globals, function prototypes, reference helpers, and SRCU lock helpers used by all TOMOYO source files in this directory.

## Important APIs, types, and functions

The main enums define condition operands, path stat slots, profile modes, policy IDs, domain flags, group IDs, ACL entry types, path/network/mount operations, MAC indexes, MAC categories, policy stats, and preference indexes. `struct tomoyo_request_info` is the per-check object passed from LSM hooks into checkers and audit logic; its union carries operation-specific parameters for path, path2, mkdev, path-number, env, inet, unix, mount, and task checks. `struct tomoyo_path_info`, `tomoyo_name_union`, `tomoyo_number_union`, and `tomoyo_ipaddr_union` are the reusable pattern/range/group operands.

Persistent policy layouts include `tomoyo_domain_info`, `tomoyo_policy_namespace`, `tomoyo_profile`, `tomoyo_acl_info`, `tomoyo_path_acl`, `tomoyo_path_number_acl`, `tomoyo_mkdev_acl`, `tomoyo_path2_acl`, `tomoyo_mount_acl`, `tomoyo_env_acl`, network ACLs, `tomoyo_group`, transition controls, aggregators, managers, and packed `tomoyo_condition`. Runtime-only support types include `tomoyo_execve`, `tomoyo_page_dump`, `tomoyo_obj_info`, and `tomoyo_io_buffer`. Inline helpers include `tomoyo_read_lock()`, `tomoyo_read_unlock()`, PID helpers, `tomoyo_pathcmp()`, reference drops for names/conditions/groups, `tomoyo_task()`, union equality helpers, `tomoyo_current_namespace()`, and `list_for_each_cookie()`.

## Control flow

The header does not implement policy decisions, but it shapes all control flow. Checkers initialize `tomoyo_request_info`, fill the operation-specific union, set `param_type`, call `tomoyo_check_acl()`, and audit through `tomoyo_supervisor()`. Writers fill `tomoyo_acl_param` with a mutable policy line, target list, namespace, and delete flag, then call parser/update functions. Readers store resumable list cursors in `tomoyo_io_buffer::r` and rely on `list_for_each_cookie()` with SRCU dereference to survive partial reads.

## State and persistence behavior

The header declares global policy state: `tomoyo_policy_loaded`, `tomoyo_enabled`, condition/domain/name/namespace lists, `tomoyo_policy_lock`, `tomoyo_ss`, kernel domain/namespace objects, memory quotas/usage, and LSM blob sizes. It models lifecycle with `tomoyo_acl_head::is_deleted`, `TOMOYO_GC_IN_PROGRESS`, and shared-object reference counts. Names, groups, and conditions are interned/shared by reference count; domain objects are also referenced from task security blobs.

## Dependencies and integration points

`common.h` includes Linux filesystem, credential, binfmt, networking, mount, list, poll, LSM, and socket headers. It is included by TOMOYO implementation files and is the bridge to LSM hooks in `tomoyo.c`, audit/securityfs helpers, realpath utilities, and network/file/mount/env/domain enforcement. The `tomoyo_task()` inline depends on `tomoyo_blob_sizes.lbs_task` matching LSM blob registration.

## Risks

Because this file fixes enum ordering and packed object layout, changes can break policy text compatibility, profile index mapping, condition binary layout, GC cleanup, and audit rendering. The variable-size `tomoyo_condition` tail layout is especially sensitive to count and alignment mistakes. Request union fields are reused by many checkers; a wrong `param_type` or uninitialized union member can produce incorrect access decisions. Inline reference drops must stay paired with parser/update ownership rules.

## Test signals

Compile coverage across all TOMOYO files is the first signal because most contracts are type-level. Runtime tests should exercise every ACL type, condition operand, profile mode, namespace, group type, securityfs interface, task-domain transition, and GC deletion path. Static analysis should focus on packed struct access, reference ownership, SRCU annotations, and `tomoyo_task()` blob offset assumptions.
