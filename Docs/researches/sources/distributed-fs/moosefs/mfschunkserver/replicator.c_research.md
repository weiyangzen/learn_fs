# sources/distributed-fs/moosefs/mfschunkserver/replicator.c

## Purpose
`replicator.c` performs chunk copy and erasure-code transformations for the chunkserver. It supports full copy (`SIMPLE`), split (`SPLIT`), missing-part recovery (`RECOVER`), and join (`JOIN`) by reading from source chunkservers and writing a local chunk.

## Important APIs and control flow
The public API is `replicator_stats()` and `replicate()`. Internal `repsrc` objects track one remote source; `replication` tracks destination state and buffers. The operation creates a version-0 local chunk with `hdd_rep_create`, connects concurrently to sources, opens the local chunk, requests source block counts, then loops over destination block groups.

For each group it sends `CLTOCS_READ`, receives and validates `CSTOCL_READ_DATA`, checks final read statuses where required, and writes local blocks. `RECOVER` XORs source blocks and CRCs, skipping final all-zero reconstructed blocks. On success it calls `hdd_rep_setversion()` and `hdd_close(...,1)`; on failure cleanup deletes the version-0 chunk.

## Dependencies and risks
Dependencies include `hddspacemgr`, `sockets`, `crc`, `mfslog`, `datapack`, `mfsstrerr`, `clocks`, and protocol constants. It is called by background jobs scheduled from master commands.

Tests should cover all modes, EC parts 4/8, last partial groups, zero-tail recovery, wrong remote packet fields, source overload statuses, reconnect retries, total/progress timeouts, NOP keepalives, and cleanup after each failure stage.
