# sources/distributed-fs/lustre-release/lnet/selftest/conctl.c

## Purpose
`conctl.c` is the kernel control plane for LNet selftest console operations. It handles legacy libcfs ioctl requests and generic netlink commands for sessions and groups, validates user-provided parameters, copies names and request payloads between user and kernel memory, serializes access to `console_session`, and dispatches to console/session/group/batch/test/stat helpers.

## Important APIs, Types, And Functions
- Legacy ioctl handlers include `lst_debug_ioctl`, `lst_group_add_ioctl`, `lst_group_del_ioctl`, `lst_group_update_ioctl`, `lst_nodes_add_ioctl`, `lst_batch_add_ioctl`, `lst_batch_run_ioctl`, `lst_batch_stop_ioctl`, `lst_batch_query_ioctl`, `lst_batch_list_ioctl`, `lst_batch_info_ioctl`, `lst_stat_query_ioctl`, and `lst_test_add_ioctl`.
- `lstcon_ioctl_entry` is the notifier entry for `IOC_LIBCFS_LNETST`.
- Generic netlink session handling uses `lst_session_keys`, `lst_sessions_show_dump`, and `lst_sessions_cmd`.
- Generic netlink group handling uses `lst_node_state2str`, `lst_node_str2state`, `struct lst_genl_group_prop`, `struct lst_genl_group_list`, `lst_groups_show_start`, `lst_groups_show_dump`, and `lst_groups_show_done`.
- Netlink registration uses `lst_genl_ops`, `lst_mcast_grps`, `lst_family`, `lstcon_init_netlink`, and `lstcon_fini_netlink`.

## Control Flow
Legacy ioctl entry first verifies the command, extracts the operation from `ioc_u32[0]`, rejects payloads larger than a page, allocates a kernel buffer, copies the user payload into it, and locks `console_session.ses_mutex`. It updates `ses_laststamp`, rejects shutdown sessions, expires old sessions, requires an active session for all operations except session creation, resets transaction stats, dispatches by opcode, copies `ses_trans_stat` to the second user buffer, unlocks, frees the temporary buffer, and returns a notifier-encoded errno.

Each ioctl helper performs focused validation. Session keys must match `console_session.ses_key`. Names must be present and within `LST_NAME_SIZE`; node/test arrays and result pointers must be non-null; indices and counts must be nonnegative or positive as appropriate; optional test parameter blobs must fit in one page minus `struct lstcon_test`. Helpers allocate NUL-terminated name buffers, copy from user, call `lstcon_*` operations, copy output fields such as features, test return codes, indexes, or counts back to user, and free temporary allocations.

Session generic netlink supports dumping active session state and creating or ending sessions. `lst_sessions_cmd` locks the session, handles shutdown/expiry, treats non-create requests as session end, parses scalar-list config for `name` and `timeout`, honors `NLM_F_REPLACE` as force, calls `lstcon_session_new`, and replies with a scalar key table plus session attributes. `lst_sessions_show_dump` reports an active session's name, key, timestamp, console NID, and node count.

Group netlink dump start allocates a dump context backed by `genradix`. Without request parameters it snapshots all session groups and takes refs. With parameters it enables verbose mode, parses requested group names and optional status filters, finds groups, and records refs. Dump emits the scalar key table once, then emits each group name and, in verbose mode, nested node entries filtered by state. Done releases group refs, frees the radix, and clears callback context.

## State And Persistence Behavior
The file does not persist data itself. It mutates the in-memory `console_session` and objects owned by the selftest console subsystem: sessions, groups, batches, nodes, tests, transaction stats, and timestamps. All legacy ioctl dispatch is serialized by `console_session.ses_mutex`; netlink session commands also take the mutex. Group dump contexts hold temporary references to groups across multipart netlink dump callbacks and release them in `.done`.

Allocated temporary buffers are short-lived per request. Name buffers are generally allocated with `nmlen + 1` and NUL-terminated before dispatch. Netlink replies are built in `sk_buff` objects and freed on error when ownership is not transferred.

## Dependencies And Integration Points
`conctl.c` depends on `console.h`, libcfs ioctl structures, LNet/libcfs helpers, Linux user-copy APIs, generic netlink, `lnet_genl_send_scalar_list`, `genradix`, and many selftest console functions such as `lstcon_group_add`, `lstcon_nodes_add`, `lstcon_batch_run`, `lstcon_test_add`, `lstcon_session_new`, and `lstcon_group_find`. The Makefile links it into `lnet_selftest.o`.

It is the bridge between user tools and in-kernel selftest orchestration. Legacy ioctl and generic netlink are parallel control surfaces; netlink currently covers sessions and groups, while many batch/test/stat operations remain ioctl-only in this file.

## Risks
- User-copy and allocation error paths are numerous. A few helpers free using sizes derived from args even after partial validation; most are safe with NULL but size consistency should be kept tight.
- `lst_stat_query_ioctl` copies a group name without explicitly appending a NUL before calling `lstcon_group_stat`, unlike most name helpers.
- In `lst_group_add_ioctl`, the `copy_from_user` failure path frees `args->lstio_grp_nmlen` bytes instead of `nmlen + 1`, which is a small accounting mismatch for the allocation macro.
- `lst_sessions_cmd` declares `char name[LST_NAME_SIZE]` without an obvious default initialization before parsing; a create request missing `name` could pass uninitialized stack data to `lstcon_session_new` unless higher-level netlink policy always provides it.
- Netlink dump code must preserve multipart message cursor state. If a message fills mid-group, the current implementation advances `lggl_index` only after the loop and may need careful validation for very large groups.
- Legacy ioctl returns transaction stats even when the operation failed late, so callers must interpret both ioctl rc and transaction fields.

## Test Signals
Tests should cover each ioctl opcode with valid and invalid session keys, missing names, overlong names, bad counts/pointers, session expiry/shutdown, batch/test lifecycle, transaction-stat copying, and fault-injected user-copy failures. Netlink tests should cover session create/end/dump, force create, invalid scalar-list types, group list dump, verbose group dump with status filters, missing groups, multipart dump cleanup, and registration/unregistration through `lstcon_init_netlink` and `lstcon_fini_netlink`.
