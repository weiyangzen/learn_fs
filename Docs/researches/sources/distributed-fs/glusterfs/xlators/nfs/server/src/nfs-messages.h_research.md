# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-messages.h

## Purpose

`nfs-messages.h` defines the stable message ID catalog for the Gluster NFS component. Every `gf_msg()` call in the NFS, mount, NFSv3, NLM, ACL, auth, and helper code uses these IDs for structured logging.

## Important APIs, types, and functions

The `GLFS_MSGID(NFS, ...)` macro expands a long ordered list of `NFS_MSG_*` identifiers. The list covers decode failures, FOP failures, protocol registration, option parsing, subvolume startup, auth/export parsing, file-handle resolution, ACL/NLM events, statd/rpcbind behavior, and inode context errors. `NFS_MSG_UNUSED_*` placeholders preserve numeric stability.

## Control flow

There is no runtime control flow. The important operational rule is in the file comment: append new IDs, never delete or reuse old IDs. That preserves log ABI compatibility across releases and tools.

## State and persistence behavior

Message IDs become part of durable logs and external diagnostics. They do not store process state, but their numeric values are consumed after the process exits by log analysis and support tooling.

## Dependencies and integration points

The header depends on `<glusterfs/glfs-message-id.h>`. It is included across NFS server source files, including `nfs.c`, `nfs-inodes.c`, `nfs3-fh.c`, and `nfs3-helpers.c`. It also holds IDs used by adjacent NLM/mount/auth modules, so changes affect more than the ten files in this group.

## Risks and edge cases

- Removing or reordering IDs can corrupt the meaning of old and new logs.
- A generic ID such as `NFS_MSG_STAT_ERROR` is reused by many protocol result logs; excessive consolidation can make automated diagnosis less precise.
- New code should use the closest existing ID only when the semantic match is real.

## Test signals

Compile coverage verifies symbol availability. Logging tests and support tooling should confirm that expected NFS error paths emit the right component and message ID.
