# Group Research: group_227_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_data_reconcile_wo_6cdec0b6a422

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.c

## Role

Implements the bcachefs background reconcile worker. Reconcile is the state-driven system that scans data, metadata, devices, stripes, and per-inode ranges for mismatches between current extent layout and configured IO path options, then schedules data moves or pointer changes to repair those mismatches.

## Main Responsibilities

- Encodes and decodes reconcile scan requests into `BTREE_ID_reconcile_scan` cookie keys.
- Maintains refcounted in-flight option-change registrations so a reconcile pass cannot clear a scan cookie while an option update is only half applied.
- Buffers reconcile work keys from logical and physical reconcile btrees to reduce contention with write-buffer flushing.
- Derives `data_update_opts` from `bch_extent_reconcile` records, including replica changes, target migration, checksum/compression rewrites, EC enable/disable, and bad/evacuating-device pointer removal.
- Moves direct data, btree nodes, and stripe work through `bch2_move_extent()` and `bch2_stripe_repair()`.
- Performs scan propagation for whole filesystem, metadata-only, device, stripe, and inode-scoped scans.
- Runs the reconcile kthread, phase scheduling, throttling, pending-work handling, copygc waits, and power-supply pause/resume.
- Exposes status and pending-scan text helpers for user-facing diagnostics.

## Scan Cookie Model

`reconcile_scan_encode()` maps structured scan requests to durable cookie positions. Reserved cookies cover filesystem-wide, metadata, pending, and stripes scans; device scans are encoded as `RECONCILE_SCAN_COOKIE_device + dev`; inode scans use the inode number directly when it is at or above `BCACHEFS_ROOT_INO`.

`bch2_set_reconcile_needs_scan_trans()` increments a cookie key in the reconcile scan btree. `bch2_clear_reconcile_needs_scan()` deletes the cookie only if the value still equals the value observed when the scan started, preventing concurrent scan requests from being lost.

## Option Change Guarding

The file defines `struct reconcile_scan_in_flight` and an rhashtable keyed by scan cookie. `bch2_set_reconcile_needs_scan_pre()` registers the cookie and increments it before an option change; `bch2_set_reconcile_needs_scan_post()` increments it again and wakes the worker after the option has settled. `opt_change_scope` cleanup unregisters cookies on both success and error paths.

This prevents a pass that scanned intermediate option state from deleting the only cookie that would cause a correct later pass.

## Reconcile Work Processing

Reconcile uses several btrees and phases:

- `BTREE_ID_reconcile_scan` for scan cookies and btree-node work buckets keyed by reconcile priority.
- `BTREE_ID_reconcile_hipri` and `BTREE_ID_reconcile_work` for logical data-order work.
- `BTREE_ID_reconcile_hipri_phys` and `BTREE_ID_reconcile_work_phys` for physical LBA-order work on rotational devices.
- `BTREE_ID_reconcile_pending` for work that cannot progress until devices/space/configuration change.

`next_reconcile_entry()` returns the next key for a phase. Non-scan work is buffered in a `darray_reconcile_work` of 1024 keys and then popped in order, reducing repeated btree walks and write-buffer contention.

## Data Option Derivation

`reconcile_set_data_opts()` is the central policy function. It inspects the extent's reconcile entry and produces a `struct data_update_opts`:

- Sets update type to `BCH_DATA_UPDATE_reconcile`.
- Chooses target and `BCH_WRITE_only_specified_devs` for non-hipri non-btree work.
- Drops bad, evacuating, offline, extra, wrongly targeted, wrongly checksummed, or wrongly compressed pointers.
- Handles erasure-code enablement by checking whether a stripe can form, avoiding endless retries when EC is impossible.
- Handles erasure-code disablement by setting `ptrs_kill_ec`.
- Marks work pending when no safe action can be taken, especially when replica reduction cannot happen without lowering required durability.

## Stripe Handling

`do_reconcile_stripe()` repairs stripe keys with `bch2_stripe_repair()`. If a stripe needs block evacuation, the stripe index and the current move IO sequence are stored in a retry list. `do_retry_stripes()` retries only after earlier data updates have drained, so stripe repair does not race data movement that it depends on.

`do_reconcile_scan_stripes()` recalculates whether stripes can widen after device/topology changes using a `widen_cache`.

## Scan Propagation

Filesystem and metadata scans walk root keys and btree levels with `do_reconcile_scan_btree()`. Leaf scanning is limited to extent and reflink btrees for full data scans; metadata scans skip leaves. Device scans walk backpointers for the selected device and update affected extents. Inode scans walk the logical extents for a single inode range.

When a scan sees a `KEY_TYPE_reflink_p` with `REFLINK_P_MAY_UPDATE_OPTIONS`, it follows the referenced reflink btree range and updates indirect extents with the referencing inode's IO options.

## Worker Lifecycle

`bch2_reconcile_thread()` waits until snapshot checking has completed, initializes a `moving_context` tied to the reconcile write point, then repeatedly runs `do_reconcile()`.

`do_reconcile()` advances through `reconcile_phases` in priority order: scan cookies, hipri btree work, hipri physical work, hipri logical work, normal btree work, normal physical work, normal logical work, and pending work. It flushes pending move IO between phases, waits on copygc when needed, and idles on the write IO clock when there is no visible work.

`bch2_reconcile_start()` creates the kthread unless mounted with `nochanges`; `bch2_reconcile_stop()` clears the RCU task pointer, synchronizes wakeups, stops the thread, and drops the task reference.

## Diagnostics and Initialization

`bch2_reconcile_status_to_text()` reports idle/running state, IO-clock wait timing, current phase/progress, and a reconcile thread backtrace. `bch2_reconcile_scan_pending_to_text()` reports whether scan work is pending once the filesystem may go read-write.

`bch2_fs_reconcile_init()` initializes the in-flight scan rhashtable and optional power-supply notifier. `bch2_fs_reconcile_exit()` destroys these resources and warns if in-flight scan entries remain.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.h

## Role

Public interface for the reconcile worker implemented in `work.c`. It defines scan request types, option-change bracketing state, wakeup helpers, pending-work helpers, status output, and lifecycle entry points.

## Key Definitions

- `RECONCILE_SCAN_TYPES()` enumerates scan classes: `fs`, `metadata`, `pending`, `stripes`, `device`, and `inum`.
- `struct reconcile_scan` stores the scan type plus either a device index or inode number.
- `BCH_OPT_CHANGE_SCANS_MAX` is currently 4, with a comment noting no option change touches more than one bracketed scan today.
- `struct opt_change_scope` holds the filesystem pointer and scan cookies registered during an option change.

## API Surface

- `bch2_set_reconcile_needs_scan_trans()`, `bch2_set_reconcile_needs_scan()`: set/increment durable scan cookies.
- `bch2_set_reconcile_needs_scan_pre()` and `_post()`: bracket option changes so reconcile does not clear an in-progress scan.
- `bch2_set_fs_needs_reconcile()`: queue a full filesystem reconcile scan.
- `bch2_reconcile_scan_cookie_is_set()`: test whether a scan cookie key exists.
- `bch2_extent_reconcile_pending_mod()`: add or remove an extent from the pending reconcile class.
- `bch2_reconcile_status_to_text()` and `bch2_reconcile_scan_pending_to_text()`: diagnostic printers.
- `bch2_reconcile_start()`, `bch2_reconcile_stop()`, `bch2_fs_reconcile_init()`, `bch2_fs_reconcile_exit()`: runtime and filesystem lifecycle.

## Wakeup Behavior

`bch2_reconcile_wakeup()` increments `c->reconcile.kick`, RCU-loads the reconcile task pointer, and wakes it if present. The kick counter is used by the worker to restart passes when new work arrives.

`bch2_reconcile_pending_wakeup()` queues the pending scan cookie and wakes the worker.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink.c

## Role

Implements bcachefs reflink and indirect extent mechanics. It validates and prints reflink keys, follows reflink pointers into the reflink btree, maintains indirect refcounts through triggers, converts extents to indirect extents, remaps source ranges into destination files, and repairs/refcounts indirect extents during GC/fsck.

## Key Types Handled

- `KEY_TYPE_reflink_p`: pointer stored in the extents btree, containing an indirect index plus front/back pad and flags.
- `KEY_TYPE_reflink_v`: indirect extent stored in the reflink btree, containing refcount plus normal extent entries.
- `KEY_TYPE_indirect_inline_data`: indirect refcounted inline data.

## Validation and Printing

`bch2_reflink_p_validate()` checks that `REFLINK_P_IDX` is not before `front_pad`. `bch2_reflink_v_validate()` rejects indirect extent positions above `REFLINK_P_IDX_MAX` and delegates pointer validation to `bch2_bkey_ptrs_validate()`. Inline indirect data validation is currently a no-op.

Text printers show pointer index, pads, `error`, `may_update_opts`, indirect refcounts, extent pointers, and inline data bytes.

## Lookup and Missing-Extent Repair

`bch2_lookup_indirect_extent()` maps a reflink pointer plus offset to the corresponding key in `BTREE_ID_reflink`. If the target data is missing, `bch2_indirect_extent_missing_error()` reports an fsck error and either adjusts pads for gaps outside the live range or cuts/marks the pointer with `REFLINK_P_ERROR` for live missing data. If a previously errored pointer now resolves correctly, `bch2_indirect_extent_not_missing()` clears the error flag.

The lookup is used both by the read path and by triggers, so it accepts a `should_commit` flag to control whether it may commit repairs directly.

## Refcount Triggers

`bch2_trigger_reflink_p()` resets pads for newly inserted pointers, then runs overwrite-before-insert trigger logic. Transactional trigger handling walks every indirect segment covered by the pointer including pads, increments refcounts on insert, decrements on overwrite/delete, and expands pointer pads when the indirect extent is larger than the nominal reference.

GC trigger handling uses `c->reflink_gc_table`, a sorted genradix table of indirect extents prepared by `bch2_gc_reflink_start()`, to accumulate expected refcounts. `bch2_reflink_p_check_repair()` uses the same machinery with repair enabled.

`bch2_trigger_reflink_v()` and `bch2_trigger_indirect_inline_data()` delete indirect keys when their refcount reaches zero. `reflink_v` then delegates to the normal extent trigger so underlying pointer accounting is updated.

## Making Extents Indirect

`bch2_make_extent_indirect()` converts a direct extent or inline data extent into an indirect extent:

- Ensures the relevant reflink feature bit is set.
- Captures inode IO options into the new indirect extent's reconcile entry so a reflinked extent does not later reconcile against filesystem defaults.
- Allocates the new key at the end of `BTREE_ID_reflink`, subject to the 56-bit `REFLINK_P_IDX_MAX` limit.
- Copies the original value after a zero refcount.
- Inserts the indirect key, then mutates the original key into a `reflink_p` pointing at it.
- Optionally sets `REFLINK_P_MAY_UPDATE_OPTIONS`.

## Range Remapping

`bch2_remap_range()` is the reflink clone/remap operation. It obtains a write reference, sets the reflink feature, resolves source and destination snapshots, walks source data extents, punches destination holes for source gaps, converts direct source extents to indirect extents as needed, creates destination `reflink_p` keys, and inserts them through `bch2_extent_update()`.

After the remap loop it updates the destination inode size when necessary. It returns the number of destination sectors completed, or an error if no progress was made.

## GC/FSCK Refcount Repair

`bch2_gc_reflink_start()` walks `BTREE_ID_reflink` and builds a genradix table containing every refcounted indirect extent with zero observed references. Reflink pointer GC triggers add/subtract to those observed counts. `bch2_gc_reflink_done()` walks the reflink btree again, compares stored refcounts to observed counts, fixes mismatches, and deletes indirect keys whose observed refcount is zero.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink.h

## Role

Declares reflink key operations and helpers for indirect extent management.

## Bkey Operation Bundles

- `bch2_bkey_ops_reflink_p` provides validation, text printing, merge hook, trigger, fsck check/repair hook, and a minimum value size of 16 bytes.
- `bch2_bkey_ops_reflink_v` provides validation, text printing, pointer byte-swapping, extent trigger integration, pointer repair through `bch2_check_fix_ptrs`, and a minimum value size of 8 bytes.
- `bch2_bkey_ops_indirect_inline_data` provides validation, text printing, trigger, and a minimum value size of 8 bytes.

## Helper Semantics

`bkey_is_indirect()` identifies `reflink_v` and `indirect_inline_data`. `bkey_refcount_c()` and `bkey_refcount()` return a const or mutable refcount pointer for those indirect types and `NULL` otherwise.

## Exported Operations

The header exports indirect lookup, direct-to-indirect conversion, range remapping, and GC start/done helpers:

- `bch2_lookup_indirect_extent()`
- `bch2_make_extent_indirect()`
- `bch2_remap_range()`
- `bch2_gc_reflink_start()`
- `bch2_gc_reflink_done()`
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink_format.h

## Role

Defines the on-disk value formats for bcachefs reflink pointers and indirect data.

## Structures

`struct bch_reflink_p` contains:

- Base `struct bch_val`.
- `idx_flags`, a 64-bit field split into a 56-bit indirect index plus flags.
- `front_pad` and `back_pad`, used to remember the full indirect range referenced when a pointer covers only part of an indirect extent that may later be split.

`struct bch_reflink_v` contains:

- Base value.
- 64-bit little-endian refcount.
- Flexible extent-entry storage beginning at `start[0]`.

`struct bch_indirect_inline_data` contains:

- Base value.
- 64-bit little-endian refcount.
- Inline data bytes.

## Bitfields

`REFLINK_P_IDX` covers bits 0-55. `REFLINK_P_ERROR` is bit 56 and marks a pointer whose live indirect data is missing. `REFLINK_P_MAY_UPDATE_OPTIONS` is bit 57 and allows reconcile to propagate IO path options from the referencing inode to indirect data.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reflink_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/update.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/update.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/update.h

## Role

Declares the data update types, option struct, runtime state struct, promote wrapper, and public update APIs.

## Update Types

`BCH_DATA_UPDATE_TYPES()` includes `other`, `copygc`, `reconcile`, `promote`, `self_heal`, `scrub`, and `scrub_no_repair`.

## `struct data_update_opts`

Carries update policy:

- Pointer masks for IO errors, pointer removal, and EC removal.
- Extra replica count and target.
- Booleans for `no_devs_have` and checksum paranoia.
- Preferred read device and read/write flags.
- Transaction commit flags.

## `struct data_update`

Owns the full move/update operation:

- Original key, btree id, options, and in-flight hash position.
- `cas[]` device references parallel to original pointers.
- Move-context list hooks and IO sequence.
- Embedded `bch_read_bio` and `bch_write_op`.
- Allocated bvec array for read/write bios.

## Promote Integration

`struct promote_op` wraps a `data_update` with promote accounting, optional async-object list index, CPU for promote limiting, and work struct.

## Exported APIs

The header exports formatting, in-flight lookup, index update, read completion, feasibility check, EC allocation failure handling, lifecycle cleanup/init, pointer-mask remapping, and filesystem table init/exit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/write.c

## Role

Implements the bcachefs data write path. It covers normal COW writes, encoded writes for move/update operations, compression, encryption, checksumming, inline data, nocow overwrites, replica submission, write-point queueing, btree index updates, and filesystem write-path initialization.

The top of the file also contains extensive bcachefs documentation for data write/read paths, encoded extents, encryption, erasure coding, reflink, move, reconcile, copygc, and scrub.

## Write Path Overview

`bch2_write()` is the closure entry point. It validates alignment and write permissions, obtains a filesystem write reference for normal writes, increments the write IO clock, optionally writes small tail data as inline data, then enters `__bch2_write()`.

Normal COW writes allocate new storage, transform data if needed, submit writes to replicas, then update the extent btree atomically. Move/data-update writes reuse the same IO pipeline but call `bch2_data_update_index_update()` instead of the default logical extent insert path.

## Extent and Inode Updates

`bch2_sum_sector_overwrites()` computes inode-sector and disk-sector deltas for a new extent over existing keys and determines whether usage is increasing.

`bch2_extent_update()` is the shared logical extent update helper. It traverses and trims the new extent, adjusts disk reservation, updates inode size/sectors through `bch2_extent_update_i_size_sectors()`, marks reconcile needs, inserts the extent, commits, updates caller totals, and advances the iterator.

`bch2_write_index_default()` inserts normal user writes into `BTREE_ID_extents`, resolving the subvolume snapshot and repeatedly calling `bch2_extent_update()` for keylist entries.

## Replica Submission and Completion

`bch2_submit_wbio_replicas()` clones a write bio for each extent pointer, obtains IO references for non-nocow writes or consumes caller-held refs for nocow writes, sets device/sector fields, records IO accounting, and submits each bio. Invalid or unavailable devices complete with an error.

`bch2_write_endio()` records device completion/error status, tracks failed devices, unlocks nocow buckets, records nocow devices needing flush, drops IO refs, frees bounce buffers, releases clone bios, and decrements the parent closure.

`bch2_write_drop_io_error_ptrs()` removes failed pointers from inserted keys after degraded writes; if no dirty pointers remain it returns a data-write error.

## Write Point Queueing

Write ops are associated with allocator write points. `bch2_write_queue()` attaches an op to a write point. `bch2_write_index()` queues the op for btree index update after IO completion. `bch2_write_point_do_index_updates()` drains a write point's completed operations, performs index updates, and either continues allocation/writing or finishes the op.

`__wp_update_state()` and `wp_update_state()` maintain write-point state and timing for stopped, waiting-for-IO, waiting-for-work, and runnable states.

## Encoding Pipeline

`bch2_write_extent()` prepares one writable extent segment:

- Reuses encoded data directly when it already satisfies geometry, checksum/encryption class, compression state, and write-point free space.
- Otherwise decompresses compressed encoded data when needed.
- Rechecks/recomputes checksums with `bch2_write_rechecksum()`.
- Decrypts when compression or checksum conversion requires plaintext.
- Allocates bounce bios when compression, encryption, checksum stability, EC buffering, or debug corruption injection require owned pages.
- Compresses, encrypts, checksums, and appends extent keys through `init_append_extent()`.
- Splits bios when the source remains only partially consumed.

`bch2_write_prep_encoded_data()` handles the special move/update case where the input bio already represents an encoded extent and may be rewritten whole, trimmed, decompressed, decrypted, or rechecksummed.

## Normal COW Allocation Loop

`__bch2_write()` repeatedly requests sectors from the foreground allocator with target, EC, replica, watermark, and flag constraints. It handles allocator blocking differently for sync and async callers, writes all possible data into the current write point, marks internal move writes `REQ_FUA`, submits replicas, and then either synchronously waits/indexes or queues async completion.

Allocator errors on normal writes are logged with detailed write-op text.

## Nocow Path

`bch2_nocow_write()` attempts in-place writes when the operation is not a move, the file/options request nocow, and existing extents are writable:

- Resolves the current snapshot and inode size.
- Requires direct non-encoded extents with enough durable replicas.
- Avoids splitting bios at unaligned extent ends.
- Takes IO refs before dropping btree locks.
- Locks nocow buckets and verifies bucket generations to avoid stale pointers.
- Splits bios by extent boundaries and submits writes directly to existing pointers.
- Converts unwritten extents after IO if needed.
- Falls back to normal COW if requirements are not met.

`bch2_nocow_write_convert_unwritten()` clears unwritten flags in successfully written extents and updates inode size/reconcile state. `bch2_nocow_write_done()` performs final nocow error/convert handling.

## Inline Data

`bch2_write_data_inline()` stores small writes as `KEY_TYPE_inline_data` when inline data is enabled and the data length is at most `min(block_size / 2, 1024)`. It copies data from the bio into the key, pads to 8-byte value alignment, inserts through the index path, and finishes the write without device IO.

## Error Handling and Diagnostics

`bch2_write_op_error()` logs file-position-aware write errors. `__bch2_write_index()` handles IO errors, degraded writes, index-update errors, open bucket cleanup, and final error propagation.

`__bch2_write_op_to_text()` and `bch2_write_op_to_text()` print position, age, flags, watermark, replicas, devices already held, inode options, open buckets, closure refs, error, and data-update state for move writes.

## Initialization

`bch2_fs_io_write_init()` initializes the write bioset and replica clone bioset. `bch2_fs_io_write_exit()` releases them.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/write.h

## Role

Public declarations and small helpers for the write path.

## Key Exports

- `to_wbio()` maps an embedded `struct bio` to `struct bch_write_bio`.
- Bounce-page pool helpers: `bch2_bio_free_pages_pool()` and `bch2_bio_alloc_pages_pool()`.
- Replica submission: `bch2_submit_wbio_replicas()`.
- Error logging: `bch2_write_op_error()`.
- Extent accounting/update helpers: `bch2_sum_sector_overwrites()` and `bch2_extent_update()`.
- Write closure entry point: `bch2_write`.
- Write-point index update worker: `bch2_write_point_do_index_updates()`.
- Formatting and filesystem init/exit helpers.

## `bch2_write_op_init()`

Initializes a `bch_write_op` with filesystem pointer, zeroed state, checksum/compression defaults from inode options, normal watermark, empty open-bucket and device lists, max position defaults, zero version, empty disk reservation, unlimited new file size, and no flush-device mask.

## Workqueue Selection

`index_update_wq()` routes copygc-watermark writes to `c->copygc.wq`; all other index updates use `c->btree_update_wq`.

## Bio Initialization

`wbio_init()` zeroes the write-bio private prefix while preserving the embedded bio object.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/write_types.h

## Role

Defines write flags and the core in-memory write operation structures used by `write.c`, data update, and debug code.

## Write Flags

`BCH_WRITE_FLAGS()` defines flags for allocation behavior, cached writes, pre-encoded data, page stability/ownership, specified-device allocation, mandatory EC, inline data, ENOSPC checking, sync mode, move/update writes, worker context, submitted state, and unwritten conversion.

The file defines both internal bit indices (`enum __bch_write_flags`) and public bit masks (`enum bch_write_flags`).

## `struct bch_write_bio`

Wraps a bio with bcachefs write metadata:

- Filesystem, parent split bio, and pinned device pointer.
- Submit time, logical inode offset, and nocow bucket.
- Failure list and target device id.
- Bitfields for split, bounce, bio ownership, nocow, mempool use, and first-btree-write state.
- Embedded `struct bio`.

The stored `bch_dev *ca` avoids re-looking up a device after removal has cleared `c->devs[]`.

## `struct bch_write_op`

Represents a complete write operation:

- Closure, filesystem, end callback, start time, optional async-object list index.
- Written sector count, flags, error, and IO-error state.
- Compression/checksum/replica/watermark settings and EC stripe wait state.
- Existing device list, target, nonce, inode options, subvolume, position, and version.
- Encoded-input CRC for move/data-update writes.
- Write point, disk reservation, open buckets, new file size, sector delta, insert keylist, inline key storage, nocow flush mask, and final embedded write bio.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/write_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.c

## Role

Implements optional debugfs exposure of live asynchronous bcachefs objects when `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled.

## Object Printers

The file maps async object list types to text printers:

- Promote operations via `bch2_promote_op_to_text()`.
- Read bios via `bch2_read_bio_to_text()`.
- Write ops via `bch2_write_op_to_text()`.
- Btree read bios via `bch2_btree_read_bio_to_text()`.
- Btree write bios via `bch2_bio_to_text()`.

## Debugfs Read Path

`bch2_async_obj_list_open()` allocates a `dump_iter`, finds the owning `bch_fs` from the `async_obj_list`, initializes iteration state, and creates a print buffer.

`bch2_async_obj_list_read()` repeatedly flushes buffered text to userspace, RCU-walks the `fast_list`, prints each object, advances the genradix iterator, and returns copied bytes or `-ENOMEM`/copy errors.

## Lifecycle

`bch2_fs_async_obj_debugfs_init()` creates an `async_objs` directory under the filesystem debug directory and one read-only debugfs file per async object list.

`bch2_fs_async_obj_init()` initializes each fast list, stores its list index, and assigns printer callbacks. `bch2_fs_async_obj_exit()` releases every fast list.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.h

## Role

Header for optional async-object debug tracking.

## Enabled Configuration

When `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled:

- `__async_object_list_add()` inserts an object into a `fast_list`, stores a positive index, and returns zero or an error.
- `__async_object_list_del()` removes the stored index and resets it to zero.
- `async_object_list_add()` and `async_object_list_del()` select the appropriate `c->async_objs[]` list using `BCH_ASYNC_OBJ_LIST_*`.
- Filesystem debugfs/init/exit functions are declared.

## Disabled Configuration

When disabled, add/delete macros compile to no-ops, `__async_object_list_add()` returns success, and the init/debugfs/exit helpers are inline stubs.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs_types.h

## Role

Defines the async-object list identifiers and list metadata structure used by the optional debug object registry.

## List Types

`BCH_ASYNC_OBJ_LISTS()` enumerates:

- `promote`
- `rbio`
- `write_op`
- `btree_read_bio`
- `btree_write_bio`

The enum adds `BCH_ASYNC_OBJ_NR` as the array size.

## `struct async_obj_list`

Stores the backing `fast_list`, a polymorphic `obj_to_text()` printer callback, and the list index used to recover the containing `bch_fs` in debugfs open.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/async_objs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/debug.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/debug.c

## Role

Implements assorted bcachefs debug and debugfs support. It can dump on-disk btree nodes, expose live btree keys and formats, show cached btree nodes, active transactions, journal pins, pending btree updates, transaction stats, deadlock diagnostics, btree node-scan results, write-point state, and async object lists.

## On-Disk Btree Node Dumping

`bch2_btree_node_ondisk_to_text()` selects a readable device for a btree node, obtains a read IO reference, reads the node directly from disk, verifies bset checksum(s), decrypts bsets in place via `bset_encrypt()`, and prints each packed key after disassembly. It reports invalid devices, offline devices, allocation failures, IO errors, unknown checksum types, and checksum failures.

## Shared Debugfs Iteration

`struct dump_iter` is allocated by open helpers and carries filesystem/list/btree identity, iterator positions, user buffer, size, copied byte count, and a `printbuf`.

`bch2_debugfs_flush_buf()` copies buffered text to userspace, updates `dump_iter` state, shifts remaining buffer contents down, fixes printbuf newline/field offsets, and returns either more-room status or bytes copied.

`bch2_dump_release()` frees the printbuf and iterator.

## Btree Debug Files

Per-btree debugfs directories contain:

- `keys`: `bch2_read_btree()` walks btree keys with prefetch and all snapshots, prints each key, advances `from`, and flushes as it goes.
- `formats`: `bch2_read_btree_formats()` walks btree nodes by level and prints node formatting/state text.
- `bfloat-failed`: `bch2_read_bfloat_failed()` prints nodes and failed bfloat conversion details.

All btree readers return no content until `BCH_FS_may_go_rw` is set, avoiding unsafe concurrent btree access during early recovery/journal gap-buffer mutation.

## Cache and Transaction Diagnostics

`bch2_cached_btree_nodes_read()` RCU-walks the btree cache rhashtable bucket by bucket and prints cached node address, btree id/level, key, flags, read-lock state, write-blocked state, reachability state, journal pins, and open buckets.

`bch2_btree_transactions_read()` SRCU/seqmutex-walks active btree transactions, sorts the transaction list by pointer, safely obtains transaction refs, prints transaction state and task backtrace, and handles relock restarts.

`btree_transaction_stats_read()` prints per-transaction-function memory, duration, optional kmalloc traces, lock hold/wait time stats, and max allocated path text.

`btree_deadlock_to_text()` walks live transactions until `bch2_check_for_deadlock()` finds and prints a deadlock.

## Journal, Updates, Node Scan, and Write Points

- `bch2_journal_pins_read()` streams journal sequence pin information.
- `bch2_btree_updates_read()` prints current btree update state once per open iterator.
- `bch2_btree_node_scan_read()` prints found btree nodes from the node-scan structure in inorder-to-Eytzinger order under the node-scan mutex.
- `bch2_write_points_read()` prints allocator write-point state via `bch2_write_points_to_text()`.

## Debugfs Tree Lifecycle

`bch2_debug_init()` creates the global `/sys/kernel/debug/bcachefs` root. `bch2_debug_exit()` removes it.

`bch2_fs_debug_init()` creates a per-filesystem directory named by UUID for multidevice filesystems or by filesystem name otherwise. It creates top-level files for cached nodes, transactions, journal pins, btree updates, transaction stats, deadlock, node scan, write points, and async objects. It then creates a `btrees` directory and per-btree debug subdirectories.

`bch2_fs_debug_exit()` removes the per-filesystem debugfs tree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/debug.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/debug.h

## Role

Declares core debugfs helpers and the shared dump iterator structure.

## Public API

`bch2_btree_node_ondisk_to_text()` is always declared and formats a btree node as read from disk.

When `CONFIG_DEBUG_FS` is enabled, the header declares:

- `struct dump_iter`
- `bch2_debugfs_flush_buf()`
- `bch2_dump_release()`
- Filesystem/global debug init and exit helpers.

When debugfs is disabled, filesystem and global debug init/exit functions are inline no-ops returning success where applicable.

## `struct dump_iter`

Carries the state common to debugfs streaming readers: filesystem pointer, optional async object list, btree id and level, current position, previous node, generic iterator cursor, print buffer, userspace destination buffer, requested size, and copied-byte count.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/debug.h -->