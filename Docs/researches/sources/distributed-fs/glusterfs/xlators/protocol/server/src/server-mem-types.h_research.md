# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-mem-types.h

## Purpose

`server-mem-types.h` reserves protocol/server-specific memory accounting type IDs.

## Important APIs, types, and functions

The enum `gf_server_mem_types_` starts at `gf_common_mt_end + 1` and defines accounting buckets for `server_conf_t`, `server_state_t`, dirent responses, setvolume responses, lock migration records, child status records, and the terminating `gf_server_mt_end`.

## Control flow

Server allocations pass these enum values to GlusterFS allocation macros such as `GF_CALLOC()` and `GF_MALLOC()` so memory usage can be categorized.

## State and persistence behavior

There is no runtime state in this header. It affects memory accounting labels for process-lifetime allocations.

## Dependencies and integration points

It includes `<glusterfs/mem-types.h>` and must stay numerically after common memory types. It is used by server source files that allocate typed memory.

## Risks and test signals

The main risk is enum collision or failing to update the end marker when adding buckets. Memory-accounting initialization and statedump/mem-leak diagnostics are the relevant test signals.
