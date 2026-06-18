# sources/distributed-fs/orangefs/src/server/check.c

## Purpose
Implements server-side permission utilities. It converts Unix mode bits and POSIX-style ACLs into OrangeFS capability masks, validates that an incoming capability covers the handle being operated on, and delegates the final operation-specific permission decision to the state-machine metadata registered for the request.

## Important APIs, Types, And Functions
`PINT_get_capabilities` computes `PINT_CAP_READ`, `PINT_CAP_WRITE`, `PINT_CAP_EXEC`, `PINT_CAP_SETATTR`, `PINT_CAP_CREATE`, and `PINT_CAP_REMOVE` for a user, group list, object attributes, and optional ACL buffer. `PINT_perm_check` is the main operation guard used by server state machines. Local helpers are `check_mode`, `check_acls`, and `check_seteattr_dir_hint`. `enum access_type` maps internal read/write/execute checks to mode-bit tests.

## Control Flow
`PINT_get_capabilities` grants UID 0 all capabilities, then removes directory-only capabilities for non-directory objects. For non-root users it first attempts ACL grants for read, write, and execute; then it validates that group data and object GID are present, selects the object's active group from the caller group list, evaluates Unix mode bits through `check_mode`, adds `SETATTR` for the owner, and adds create/remove when a directory has both write and execute capability.

`PINT_perm_check` looks up the request's permission function through `PINT_server_req_get_perm_fun`. If the request carries a non-null capability, it chooses the handle that must be covered: remove/tree-remove and I/O/small-I/O use the handle stored in hints, special directory-hint `seteattr` may use the parent hint, and most operations use `s_op->target_handle`. It then scans `cap->handle_array` for that handle and returns `-PVFS_EACCES` if missing. Finally it calls the op-specific permission function and returns that result.

`check_acls` validates the ACL buffer shape, byte-swaps ACL entries from LEBF/network order, scans user/group entries, applies an ACL mask where needed, and returns `0`, `-PVFS_EACCES`, or `-PVFS_EINVAL`. `check_mode` validates the attr mask and checks owner, group, or other bits for the requested access.

## State And Persistence
The file stores no persistent state. It reads request state (`PINT_server_op`, `PVFS_server_req`, hints, capabilities), object attributes, ACL buffers, and caller credential/group arrays. `PINT_get_capabilities` writes only the caller-supplied `op_mask`; `PINT_perm_check` logs diagnostic information and returns permission status.

## Dependencies And Integration Points
The implementation depends on `pvfs2-server.h`, `pvfs2-attr.h`, server configuration/Trove headers, `pint-perf-counter.h`, `bmi-byteswap.h`, `security-util.h`, capability helpers, hints, and request metadata from `pvfs2-server-req.c`. It is part of the authorization path for generated server state machines and relies on each operation's `PINT_server_req_params` to supply the correct permission function.

## Risks And Test Signals
Permission bugs here have direct security impact. `check_seteattr_dir_hint` appears suspicious: it returns false if a key differs from any one of the three accepted hint names, which means ordinary single-name strings cannot satisfy the "all keys are dir hints" intent. That may force `seteattr` to validate the target handle instead of the parent for directory hint attributes. ACL scanning assumes canonical ACL ordering and treats some orderings as invalid. Tests should cover root/non-root capability generation, owner/group/other mode bits, ACL user/group/mask/other combinations, missing attr mask fields, missing hint handles for remove/I/O/seteattr, capability handle-array rejection, and the special `user.pvfs2.num_dfiles`, `user.pvfs2.dist_name`, and `user.pvfs2.dist_params` seteattr path.
