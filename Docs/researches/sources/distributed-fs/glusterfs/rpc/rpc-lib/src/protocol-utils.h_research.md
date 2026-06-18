## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/protocol-utils.h

Purpose: provides small inline helpers around protocol-common data.

Important APIs: `get_vol_type` adjusts a cluster type based on distribution and brick counts, preserving tier/invalid/non-distributed cases and offsetting distributed variants by `GF_CLUSTER_TYPE_MAX - 1`. `get_struct_variable` returns a pointer to one field in `gf_gsync_status_t` by numeric index.

Control flow: both helpers are straight-line inline functions. `get_struct_variable` uses a switch covering indexes 0 through 21 and returns NULL for unknown indexes.

State and persistence: no mutable state. It exposes pointers into caller-owned `gf_gsync_status_t` instances.

Dependencies and integration: includes `protocol-common.h` and depends on cluster type constants defined elsewhere. Consumers can use `get_struct_variable` for generic table/status formatting.

Risks: index-based access is brittle; callers must keep indexes synchronized with `gf_gsync_status_t` field order. `get_struct_variable` does not validate `sts_val` before dereferencing. `get_vol_type` depends on implicit numeric layout of cluster type enum values.

Test signals: unit tests for volume-type classification boundaries and every gsync field index, including NULL/default behavior.
