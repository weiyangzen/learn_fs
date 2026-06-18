# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mem-types.h

## Purpose
`glusterd-mem-types.h` assigns GlusterD-specific memory accounting type IDs. These IDs are passed to `GF_MALLOC`, `GF_CALLOC`, and related allocation helpers so memory usage can be attributed to management subsystem structures.

## Important APIs, Types, And Functions
The file defines `gf_gld_mem_types_t`, starting at `gf_common_mt_end + 1` and ending at `gf_gld_mt_end`. Entries cover GlusterD configuration, peers, friend/op state machine contexts, lock/stage/commit contexts, probe contexts, volume and brick info, defrag info, pending node lists, brick response contexts, line buffers, mount specs, geo-replication specs, hooks stubs/private state, snapshot structures, service and brick process structures, pmap registry entries, and generic char/int/hostname helpers.

## Control Flow
There is no runtime control flow. The enum is included by GlusterD source files and referenced at allocation sites. For this subset, `glusterd-hooks.c` uses `gf_gld_mt_hooks_stub_t`, `gf_gld_mt_hooks_priv_t`, and `gf_gld_mt_charptr`, while management handlers use context memory types such as `gf_gld_mt_op_lock_ctx_t`.

## State And Persistence Behavior
The enum contributes to process memory accounting and diagnostics only. It does not persist state. Numeric stability matters because IDs are consumed by allocator/accounting code after compilation.

## Dependencies And Integration Points
It depends on `<glusterfs/mem-types.h>` for the common memory type range and is integrated throughout GlusterD's allocation paths. Adding a new memory type should happen before `gf_gld_mt_end` and must not collide with common types.

## Risks
Removing or reordering enum values can confuse diagnostics and any code assuming stable allocation categories. Using an overly generic type for new allocations makes leak accounting less useful. Forgetting to add a GlusterD-specific type for a long-lived allocation can obscure subsystem memory growth.

## Test Signals
Build tests catch missing enum names. Runtime leak/accounting tests should verify high-volume paths, especially hook queue and mgmt lock contexts, are attributed to meaningful GlusterD memory types. Review allocation changes for correct type selection and no use beyond `gf_gld_mt_end`.
