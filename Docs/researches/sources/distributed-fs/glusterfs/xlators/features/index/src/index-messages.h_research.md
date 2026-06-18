# sources/distributed-fs/glusterfs/xlators/features/index/src/index-messages.h

## Purpose
Declares stable log message IDs for the index translator.

## Important APIs, Types, and Functions
`GLFS_MSGID(INDEX, ...)` assigns message identifiers for directory creation, readdir, index add/delete, dict failures, inode ctx errors, worker creation, invalid args, fd failures, and invalid graph layout.

## Control Flow
No runtime control flow; `index.c` references these symbols in `gf_msg()` calls.

## State and Persistence
No runtime state. The file documents that IDs must be appended, not removed, to avoid reuse.

## Dependencies and Integration Points
Includes `<glusterfs/glfs-message-id.h>` and integrates with GlusterFS structured logging.

## Risks and Edge Cases
Removing or reordering IDs can break log analytics and documentation. New `gf_msg()` sites should append new IDs here instead of reusing unrelated IDs.

## Test Signals
Build should verify all message IDs referenced by `index.c` are declared.
