# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-messages.h

## Purpose
This header defines stable log/message IDs for the shard translator.

## Important APIs
`GLFS_MSGID(SHARD, ...)` declares IDs for lookup failures, dictionary failures, missing `.shard` directory, fd/inode context errors, internal xattr issues, invalid volfiles and FOPs, stat/truncate/file-size update failures, memory allocation failure, generic FOP failure, shard deletion failure, and shard deletion completion. The header comments require appending IDs rather than removing or reusing them.

## Dependencies and integration
It includes `glusterfs/glfs-message-id.h` and is consumed by the shard implementation for structured logging. These IDs are part of operator-facing diagnostics and compatibility expectations.

## Risks and test signals
Reordering or deleting IDs can break message stability. New diagnostics should append IDs after `SHARD_MSG_SHARD_DELETION_COMPLETED`. Compile tests should include all users of the message constants, and behavioral tests should force representative shard errors such as missing `.shard`, lookup failure, invalid FOP, and deletion failure to validate logging paths.
