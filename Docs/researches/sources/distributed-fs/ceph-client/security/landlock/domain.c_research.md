# sources/distributed-fs/ceph-client/security/landlock/domain.c

## Purpose

`domain.c` provides audit-specific domain metadata creation and helper logic to encode which domain layers denied optional access rights. It records details about the process that created a domain and assigns unique audit IDs.

## Important APIs, Types, and Functions

Under `CONFIG_AUDIT`, `get_current_exe()` captures the current executable path, `get_current_details()` allocates `struct landlock_details`, and `landlock_init_hierarchy_log()` initializes audit fields in a new hierarchy node. `get_layer_deny_mask()` encodes one optional access/layer pair into `deny_masks_t`. `landlock_get_deny_masks()` walks layer masks from newest to oldest and records the youngest layer denying each optional right. KUnit tests cover encoding and deny-mask extraction.

## Control Flow

When a new domain is created in `ruleset.c`, `landlock_init_hierarchy_log()` captures task PID, UID, command, executable path, assigns an ID with `landlock_get_id_range(1)`, marks logging pending, and initializes denial counters. When file open records optional access denials, `landlock_get_deny_masks()` receives the remaining layer masks and produces compact per-file state for later `ftruncate()` and ioctl audit records.

## State and Persistence Behavior

`struct landlock_details` is allocated once per domain hierarchy node and freed when the hierarchy is released. It pins the creator PID to avoid PID reuse ambiguity. Deny masks are compact transient or file-blob state, not global state.

## Dependencies and Integration Points

Dependencies include audit-enabled domain structures, path formatting through `d_path()`, executable file lookup, PID references, random ID generation, and optional access definitions from `access.h`.

## Risks and Test Signals

Executable path capture must tolerate missing `mm` or executable files. Deny-mask encoding depends on layer count and optional-access bit ordering. Test with `CONFIG_AUDIT=y`, domain creation by kernel threads or processes without exe, long paths, and KUnit suite `landlock_domain`.
