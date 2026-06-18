<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc

## Purpose
Implements `lizardfs-admin manage-locks`, a privileged command for listing or unlocking flock/POSIX file locks.

## Important APIs, Types, and Functions
Defines `parseType`, `lockTypeToString`, `processUnlock`, `processListType`, `processList`, and command methods. Options include `--active`, `--pending`, `--inode=`, `--owner=`, `--sessionid=`, `--start=`, and `--end=`.

## Control Flow, State, and Persistence
`run` requires four positional arguments: host, port, `list|unlock`, and `flock|posix|all`; it creates an authenticated `RegisteredAdminConnection`. Unlock requires `--inode`, and either both owner/sessionid or neither. It sends a broad inode unlock or a single lock-range unlock. Listing pages through `LIZ_CLTOMA_MANAGE_LOCKS_LIST_LIMIT` chunks for active and/or pending flock/POSIX locks, optionally filtered by inode, until fewer than the limit are returned. Unlock mutates master lock state; list is read-only.

## Dependencies and Integration Points
Depends on admin authentication, `master/locks.h`, `protocol/lock_info.h`, `cltoma::manageLocks*`, `matocl::manageLocks*`, and LizardFS error strings.

## Risks and Test Signals
Risks include porcelain mode still printing section headers, direct `exit(1)` on EPERM or oversized list responses, `--active` and `--pending` both set producing both categories, type parsing depending on fourth argument, and destructive broad unlock by inode when owner/sessionid are omitted. Test signals are list active/pending for flock/POSIX/all, pagination at exact limit, inode filtering, single and broad unlock, mismatched owner/session arguments, range boundaries, bad password, EPERM messaging, and porcelain parseability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc -->
