# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-mem-types.h

## Purpose
Defines memory-accounting IDs for the write-behind translator.

## Important APIs, Types, And Functions
`enum gf_wb_mem_types_` names allocation classes for legacy `wb_file_t`, `wb_request_t`, iovec arrays, `wb_conf_t`, `wb_inode_t`, and the end marker.

## Control Flow
`write-behind.c` initializes accounting with `gf_wb_mt_end` and uses these IDs for request, inode, and config allocations.

## State And Persistence
No runtime state; labels allocations for diagnostics.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is consumed by `write-behind.c`.

## Risks
`gf_wb_mt_wb_file_t` appears retained though the current code centers on `wb_inode_t`; stale allocation labels can confuse readers but preserve compatibility.

## Test Signals
Memory-accounting initialization and leak reports should show write-behind request, inode, and config allocation classes.
