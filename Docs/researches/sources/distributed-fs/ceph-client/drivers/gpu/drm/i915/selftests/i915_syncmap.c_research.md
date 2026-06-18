# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_syncmap.c

## Purpose
This file tests `i915_syncmap`, a compressed radix-style map from 64-bit context IDs to sequence numbers. It validates initialization, single-leaf insertion, tree growth above and below existing leaves, neighbour packing, branch compaction, random insertion, and sequence-number freshness checks.

## Important APIs, Types, And Functions
- `i915_syncmap_mock_selftests()` registers the suite.
- `i915_syncmap_print_to_buf()` and `dump_syncmap()` format the internal tree for failure diagnostics.
- `check_syncmap_free()`, `check_seqno()`, `check_one()`, and `check_leaf()` are invariant helpers.
- Test functions are `igt_syncmap_init()`, `igt_syncmap_one()`, `igt_syncmap_join_above()`, `igt_syncmap_join_below()`, `igt_syncmap_neighbours()`, `igt_syncmap_compact()`, and `igt_syncmap_random()`.

## Control Flow
Each test initializes a syncmap pointer, performs controlled `i915_syncmap_set()` insertions, checks returned leaf/parent topology, and uses `i915_syncmap_is_later()` to validate lookups. Join-above tests insert IDs with shrinking common prefixes. Join-below and compaction tests force branch replacement and skipped single-child branch behavior. Random tests first populate random contexts for a short phase, then replay a deterministic context stream across changing seqnos and compare expected `seqno_later()` outcomes.

## State And Persistence
The syncmap tree is heap-backed and transient. Tests mutate `*sync` as insertions may return the active leaf, not always the root; diagnostic printing climbs to the root through `parent` links. Every path calls `i915_syncmap_free()` and verifies the pointer is cleared.

## Dependencies And Integration Points
It depends on the internal syncmap layout (`height`, `prefix`, `bitmap`, `__sync_child`, `__sync_seqno`, `KSYNCMAP`, `SHIFT`, `MASK`) and selftest random helpers. It is registered in the mock selftest list.

## Risks
The tests inspect internal representation, so legitimate implementation changes to compression or layout require updates. Failure diagnostics allocate a page-sized buffer and may skip tree printing if allocation fails. Random tests depend on seed reproducibility.

## Test Signals
Signals include exact bitmap population, leaf height zero where expected, parent/child placement, root compaction shape, correct absence for neighbouring but uninserted IDs, correct seqno freshness results, and pointer clearing after free.
