# File Research: sources/cow-pools/nilfs2-kmod10/include/trace/events/nilfs2.h

## Summary
Defines NILFS2 tracepoints for segment construction stages, transaction transitions, segment usage allocation/free checks, and metadata block operations.

## Trace Events
- `nilfs2_collection_stage_transition`: logs `nilfs_sc_info` pointer and collection stage symbol.
- `nilfs2_transaction_transition`: logs superblock pointer, transaction info pointer, nesting count, flags, and transition state.
- `nilfs2_segment_usage_check`: logs sufile pointer, segment number, and allocation scan count.
- `nilfs2_segment_usage_allocated`: logs allocated segment number.
- `nilfs2_segment_usage_freed`: logs freed segment number.
- `nilfs2_mdt_insert_new_block`: logs metadata inode, inode number, and block.
- `nilfs2_mdt_submit_block`: logs metadata inode, inode number, block offset, and request op mode.

## Important Details
The collection stage symbolic names mirror the stage enum in `segment.c`, so enum changes there must stay aligned with this header. Transaction transition states are defined only outside `TRACE_HEADER_MULTI_READ`.

`nilfs2_mdt_submit_block` uses `__field_struct(enum req_op, mode)` to avoid signedness handling problems with the bitwise request-op enum.

## Risks
Tracepoint fields dereference `struct nilfs_sc_info` members, so this header depends on the concrete segment-constructor layout being visible at tracepoint instantiation. Stage enum drift between `segment.c` and this file would produce misleading traces.
