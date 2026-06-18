# File Research: sources/cow-pools/bcachefs-tools/fs/data/update.c

## Role

Implements the data update/move engine used by copygc, reconcile, promote, self-heal, and scrub. A data update reads an existing extent, optionally rewrites selected pointers or adds replicas, then atomically updates the btree while preserving durability and reconcile invariants.

## In-Flight Tracking

The file defines an `rhltable` keyed by `struct bbpos`. `bch2_data_update_in_flight()` prevents conflicting updates at the same extent position. Non-copygc updates are excluded by any update; copygc only conflicts with another copygc so promotions and reconcile do not unnecessarily block bucket evacuation.

## Device Reference Handling

`bkey_get_dev_refs()` and `bkey_put_dev_refs()` maintain `bch_dev` references parallel to extent pointer positions. The code deliberately stores device pointers in `data_update.cas[]` so exit and nocow lock paths do not re-derive devices from `c->devs[]`, which may have been cleared by device removal while references are still held.

## Index Update After Rewrite

`data_update_index_update_key()` merges newly written extents into the current btree state. It:

- Copies the current key, the written key, and an insert candidate.
- Cuts keys to the overlapping range.
- Verifies the current extent still matches the original.
- Remaps old pointer masks to the current key.
- Prevents replacing durable non-cached replicas with cached replicas.
- Drops explicit conflicts, useless writes, requested EC durability, requested old replicas, and excess durability.
- Propagates incompressible state.
- Accounts `i_sectors` and disk-sector deltas.
- Logs the update type and old key to the transaction.
- Inserts snapshot whiteouts where needed.
- Runs `bch2_bkey_set_needs_reconcile()` both on the just-written data for verification and on the final inserted key for the real reconcile state.
- Emergency-remounts read-only if an option-change race would reduce durability below required levels.

`bch2_data_update_index_update()` wraps this over all pending keys in the write op.

## No-Write and EC Failure Paths

`data_update_index_update_nowrite()` handles cases where a read found IO errors but no new replicas remain to write. It drops failed pointers from matching extents and marks reconcile state without issuing data IO.

`bch2_data_update_ec_alloc_failed()` marks matching extents pending when EC allocation failed before a write happened, so reconcile retries from the pending list instead of continuously re-reading data.

## Read Completion

`bch2_data_update_read_done()` transitions from read phase to write phase:

- Treats checksum errors on poisoned extents as movable by recomputing a checksum and preserving poisoned semantics.
- Records scrub-no-repair journal repair entries for IO-error pointers.
- Ends scrub reads that do not need repair.
- Adds IO-error pointers to `ptrs_kill`, adjusts `devs_have`, and may take the no-write path if nothing remains to rewrite.
- Sets the write op CRC and compressed bio size, then calls `bch2_write`.

## Lifecycle and Diagnostics

`bch2_data_update_exit()` traces the result, removes the update from the in-flight table, releases move-context accounting, wakes waiters, frees bounce pages and bvecs, unlocks nocow buckets, drops device references, and returns disk reservations.

`bch2_data_update_opts_to_text()`, `bch2_data_update_to_text()`, and `bch2_data_update_inflight_to_text()` format update state for tracing/debugfs.

## Feasibility Checks

`bch2_can_do_data_update()` computes durability that will remain after requested pointer removals, builds the `devs_have` list, and asks whether enough durability can be written to the target. For EC-mandatory updates it also probes EC stripe-head allocation to avoid expensive reads when stripe creation is impossible.

`durability_available_on_target()` inspects eligible target devices, allocator availability, write flags, cached mode, and copygc pressure.

## Initialization

`bch2_data_update_init()` constructs a `data_update`:

- Copies the original key and update options.
- Initializes the embedded write op as a move/data-encoded write.
- Checks snapshot validity unless scrub-no-repair is running.
- Reserves extra replica space.
- Handles mixed checksummed/non-checksummed extents by preferring a specific read device and limiting rewrites.
- Computes retained durability, desired new replica count, and existing devices.
- Performs allocation feasibility checks, in-flight insertion, nocow locking, and unwritten-extent conversion.
- Allocates read/write bios sized for the largest encoded representation.

`bch2_fs_data_update_init()` initializes the in-flight rhltable; `bch2_fs_data_update_exit()` destroys it.
