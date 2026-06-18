# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.h

## Purpose
This header exposes the common marker inode-context helper to marker source files.

## Important APIs, Types, And Functions
It includes `marker.h` and declares `marker_force_inode_ctx_get(inode_t *, xlator_t *, marker_inode_ctx_t **)`.

## Control Flow, State, And Dependencies
The header contains no runtime logic or state. Its only integration point is sharing the inode context retrieval/creation contract implemented in `marker-common.c`.

## Risks And Test Signals
The declaration must stay synchronized with the implementation. Since it exposes only one helper, build success across marker quota files is the primary signal.
