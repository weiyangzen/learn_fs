# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-mem-types.h

## Purpose
Defines memory-accounting IDs for allocations made by the read-ahead translator.

## Important APIs, Types, And Functions
`enum gf_ra_mem_types_` starts at `gf_common_mt_end + 1` and names allocation classes for `ra_file_t`, `ra_conf_t`, `ra_page_t`, `ra_waitq_t`, `ra_fill_t`, and iovec arrays, ending with `gf_ra_mt_end`.

## Control Flow
`read-ahead.c` passes `gf_ra_mt_end` to `xlator_mem_acct_init()`. Allocation sites in `page.c` and `read-ahead.c` use the individual enum values with `GF_CALLOC`.

## State And Persistence
No runtime state is stored here; the enum is part of Gluster's in-process memory accounting namespace.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is included by `read-ahead.h`, making these IDs available to all read-ahead implementation files.

## Risks
IDs must remain unique relative to common memory types and should be extended only before `gf_ra_mt_end`. Mislabeling allocations mainly affects diagnostics and leak attribution.

## Test Signals
Translator initialization should call memory accounting successfully. Leak/statedump tooling should attribute read-ahead file, page, wait queue, fill, and iovec allocations to these IDs.
