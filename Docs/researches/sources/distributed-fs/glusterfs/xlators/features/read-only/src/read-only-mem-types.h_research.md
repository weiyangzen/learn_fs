# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-mem-types.h

## Purpose
`read-only-mem-types.h` defines memory accounting IDs for the read-only and WORM translators.

## Important APIs and Types
- `enum gf_read_only_mem_types_` declares `gf_read_only_mt_priv_t` for `read_only_priv_t` allocations and `gf_read_only_mt_end` as the limit passed to `xlator_mem_acct_init()`.

## Control Flow
No executable flow exists. `read-only.c` and `worm.c` use the enum during memory accounting initialization and private allocation.

## State and Persistence
The enum values are compile-time memory accounting labels. They persist no runtime data.

## Dependencies and Integration Points
The header depends on `<glusterfs/mem-types.h>` and integrates with GlusterFS xlator memory accounting.

## Risks
Future allocations in these translators should add distinct IDs before `gf_read_only_mt_end`; otherwise memory diagnostics stay coarse.

## Test Signals
Build coverage and statedump/memory accounting checks showing private allocations under the read-only component.
