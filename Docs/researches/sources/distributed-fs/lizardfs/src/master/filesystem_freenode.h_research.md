# sources/distributed-fs/lizardfs/src/master/filesystem_freenode.h

## Purpose
`filesystem_freenode.h` declares the inode allocation helper used by node creation and changelog replay.

## Important API
`fsnodes_get_next_id(uint32_t ts, uint32_t req_inode)` returns an allocated inode id. `req_inode == 0` asks for any free id; a nonzero request asks for a specific inode but may fall back to another id if that id is already acquired.

## State and persistence behavior
The function works against `gMetadata->inode_pool` and `gMetadata->maxnodeid`. The timestamp is passed into the inode pool so reuse delay and detainer behavior remain deterministic.

## Dependencies and integration points
The header includes node types and is consumed by `filesystem_node.cc`, `filesystem_dump.cc`, and filesystem load/apply paths.

## Risks and test signals
Callers that require exact replay ids must compare the requested id with the returned id and report mismatch, as `fs_apply_create` does. Tests should assert that behavior and verify the API returns nonzero or aborts on exhaustion.
