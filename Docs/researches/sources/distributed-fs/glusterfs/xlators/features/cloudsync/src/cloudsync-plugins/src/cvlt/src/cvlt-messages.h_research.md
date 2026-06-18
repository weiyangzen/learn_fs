# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/cvlt-messages.h

## Purpose
Declares structured message IDs for the CVLT plugin.

## Important APIs, types, and functions
Uses `GLFS_MSGID(CVLT, ...)` to define IDs such as extraction failure, free, resource allocation failure, restore/read failures, no memory, and dlopen failure.

## Control flow
No executable control flow; IDs are consumed by `gf_msg()` calls in `libcvlt.c`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the CVLT component namespace.

## Risks and test signals
Message IDs should never be deleted or reused. Tests are compile-time plus log inspection for meaningful IDs on failure paths.
