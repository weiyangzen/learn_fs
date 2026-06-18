# sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.h

## Purpose
`localalloc.h` declares the per-node local allocation API used by mount, recovery, and allocation paths.

## Important APIs, types, and functions
The header exposes load/shutdown, sizing, default-size calculation, recovery begin/complete, local-allocation eligibility, reservation/claim/free operations, free-bit observation, and delayed enable worker entry points. It forward declares `struct ocfs2_alloc_context` for allocator interactions.

## Control flow
Mount code sets sizes and loads the local alloc. Allocation code calls the eligibility check, reserves bits into an allocation context, then claims or frees bits inside a transaction. Recovery code calls begin recovery while handling a crashed slot and complete recovery later from journal completion work.

## State and persistence behavior
The header itself is stateless. Declared functions manipulate the local alloc dinode, global bitmap, OCFS2 superblock local alloc fields, reservation maps, and delayed enable work.

## Dependencies and integration points
It is used by allocator paths and `journal.c` recovery. It depends on OCFS2 superblock, dinode, allocation context, JBD2 `handle_t`, and workqueue types supplied by including files.

## Risks and edge cases
Callers must respect locking and lifetime rules: reserve returns an allocation context holding references/locks, claim/free require an active transaction, and recovery begin returns a copied dinode that completion must eventually free or consume.

## Test signals
Build coverage should ensure allocator and recovery users agree on prototypes. Runtime signals are covered by localalloc mount, allocation, shutdown, and recovery tests.
