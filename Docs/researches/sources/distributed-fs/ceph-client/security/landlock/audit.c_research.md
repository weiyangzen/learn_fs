# sources/distributed-fs/ceph-client/security/landlock/audit.c

## Purpose

`audit.c` emits audit records for Landlock domain allocation, access denials, and domain deallocation. It maps denied filesystem/network/scope requests to stable blocker strings and identifies the youngest domain layer responsible for a denial.

## Important APIs, Types, and Functions

`fs_access_strings[]` and `net_access_strings[]` map UAPI bits to audit names. `get_blocker()` and `log_blockers()` format denial causes. `log_domain()` logs domain allocation details once. `get_hierarchy()` maps a layer index to the corresponding hierarchy node. `get_denied_layer()` finds the youngest denying layer from full layer masks. `get_layer_from_deny_masks()` decodes compact optional-access deny masks. `landlock_log_denial()` is the main denial logger, and `landlock_log_drop_domain()` logs deallocation for previously recorded domains. KUnit tests cover hierarchy and layer selection helpers.

## Control Flow

When an enforcement hook denies an action, it builds `struct landlock_request` and calls `landlock_log_denial()`. The function validates the request shape, derives the missing access and youngest denied hierarchy, skips disabled logging, increments denial counters regardless of audit enablement, applies same-exec/new-exec logging policy, emits an `AUDIT_LANDLOCK_ACCESS` record with LSM audit data, then calls `log_domain()` to emit the related `AUDIT_LANDLOCK_DOMAIN` allocation record if needed. When a hierarchy is freed, `landlock_log_drop_domain()` emits a deallocation record only if allocation had been logged.

## State and Persistence Behavior

Audit state is stored in `struct landlock_hierarchy`: `log_status`, `num_denials`, ID, details, and log flags. The file does not persist records itself; audit subsystem storage handles that. Denial counters remain even if audit is disabled.

## Dependencies and Integration Points

Dependencies include Linux audit, LSM audit data, Landlock credentials, domains, rulesets, and access masks. It is compiled only with `CONFIG_AUDIT`.

## Risks and Test Signals

Incorrect layer attribution makes audit records misleading and can break user-space policy debugging. Request validation catches inconsistent caller state. Test with audit enabled/disabled, same-exec and new-exec log flags, optional truncate/ioctl denials, network denials, and KUnit suite `landlock_audit`.
