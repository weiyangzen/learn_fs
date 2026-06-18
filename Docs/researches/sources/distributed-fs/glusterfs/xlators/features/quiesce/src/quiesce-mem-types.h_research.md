# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-mem-types.h

## Purpose

`quiesce-mem-types.h` registers memory accounting categories for the quiesce translator.

## Important APIs, Types, and Functions

The enum `gf_quiesce_mem_types_` defines `gf_quiesce_mt_priv_t`, `gf_quiesce_mt_failover_hosts`, and `gf_quiesce_mt_end`, starting after `gf_common_mt_end`.

## Control Flow

There is no runtime control flow; `quiesce.c` passes `gf_quiesce_mt_end` to `xlator_mem_acct_init` and uses the specific types in allocations.

## State and Persistence Behavior

No state is persisted. The enum enables memory accounting for private state and failover host records.

## Dependencies and Integration Points

It includes Gluster common memory type definitions and must stay synchronized with allocation sites in `quiesce.c`.

## Risks and Edge Cases

Adding allocations without memory types reduces accounting visibility. Renumbering can collide with other components if not based on `gf_common_mt_end`.

## Test Signals

Memory accounting initialization and leak reports should categorize quiesce private and failover host allocations correctly.
