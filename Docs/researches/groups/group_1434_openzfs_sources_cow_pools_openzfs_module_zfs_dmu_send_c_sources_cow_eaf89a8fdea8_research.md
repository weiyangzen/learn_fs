# Group Research: group_1434_openzfs_sources_cow_pools_openzfs_module_zfs_dmu_send_c_sources_cow_eaf89a8fdea8

Scope: `Docs/research_subset_a.md`, specifically `sources/cow-pools/openzfs`. I read all 4 listed source files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers core OpenZFS DMU send/traversal/transaction/prefetch machinery: send stream generation, block-tree traversal, transaction reservation and txg assignment, and adaptive predictive read-ahead.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_send.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_send.c

Implements `zfs send` stream construction for full, incremental, raw, compressed, resumable, saved, and redacted sends.

Key points:
- Defines send tunables for corrupt-data substitution, queue sizing/fill fractions, estimate record size override, free-record emission, and unmodified spill block handling.
- Builds DMU replay records through `dump_record()`, maintaining the send stream Fletcher checksum and stream offset.
- Aggregates adjacent `DRR_FREE`, `DRR_FREEOBJECTS`, and `DRR_REDACT` records via `dsc_pending_op` to reduce stream record count.
- Emits `DRR_OBJECT`, `DRR_WRITE`, `DRR_WRITE_EMBEDDED`, `DRR_SPILL`, `DRR_OBJECT_RANGE`, `DRR_FREE`, `DRR_FREEOBJECTS`, `DRR_REDACT`, `DRR_BEGIN`, and `DRR_END`.
- Handles stream feature negotiation in `setup_featureflags()`: SA spill, large blocks, embedded data, compression, raw encrypted streams, LZ4, ZSTD, resuming, redaction, large dnodes, long names, and large microzap constraints.
- `send_do_embed()` gates embedded block emission on stream feature compatibility and compression support.
- Raw send paths preserve encrypted block parameters: byteswap state, salt, IV, MAC, compression type, compressed size, dnode raw bonus data, object range encryption metadata, and crypt keydata in the BEGIN nvlist.
- Non-raw encrypted sends authenticate the objset physical buffer before sending if needed.
- Large blocks are split to `SPA_OLD_MAXBLOCKSIZE` when the stream lacks large-block support.
- Corrupt blocks can either abort with `EIO` or be replaced by a recognizable bad-block fill pattern when `zfs_send_corrupt_data` is enabled.

Pipeline and threading:
- Represents work as `struct send_range`, covering data, holes, objects, object ranges, redaction ranges, previously redacted ranges, and EOS markers.
- `send_traverse_thread()` runs `traverse_dataset_resume()` with `send_cb()` to turn changed blocks/dnodes into ordered ranges.
- `redact_list_thread()` traverses redaction lists and emits either `REDACT` or `PREVIOUSLY_REDACTED` ranges.
- `send_merge_thread()` merges ranges from the target traversal, ancestor redaction list, and optional redact-book list, using priority rules so redaction metadata overrides lower-priority data where appropriate.
- `find_next_range()` slices overlapping ranges at change points, preserving sorted object/block order and selecting the highest-priority metadata for each interval.
- `send_reader_thread()` issues ARC/zio reads after redaction decisions are known, resolves `PREVIOUSLY_REDACTED` ranges against the target dnode, skips deleted objects, expands large holes efficiently via `dnode_next_offset()`, and piggybacks unmodified spill blocks on object records.
- The main thread dequeues prefetched ranges and calls `do_dump()` to serialize replay records.

Entry points:
- `dmu_send_obj()` sends by dataset object IDs and validates from-snapshot ancestry.
- `dmu_send()` sends by dataset/bookmark names, supports live filesystem or volume ownership, saved `%recv` streams, redaction bookmarks, resume object/offset, and clone detection.
- `dmu_send_impl()` is the central implementation: holds objsets/redaction lists, creates BEGIN payload nvlist fields, starts worker threads, drains the reader queue, emits END when appropriate, and cleans up holds/queues/status.
- `dmu_send_estimate_fast()` estimates stream size from dataset space accounting or bookmark deltas, with adjustment for indirect blocks and replay-record overhead.

Dependencies and interactions:
- Uses `dmu_traverse.c` via `traverse_dataset_resume()` for txg-filtered tree walking.
- Uses DSL dataset/bookmark/redaction-list APIs for ancestry, redacted dataset metadata, saved stream state, and redaction bookkeeping.
- Uses ARC/zio read paths for cached and direct data reads, including raw/compressed reads.
- Cooperates with receive-side stream compatibility through feature flags, record layout, payload padding, and checksum sequencing.

Research relevance:
- This is the main source for OpenZFS replication stream semantics. It ties together COW block birth times, dataset ancestry, encryption metadata, redaction, resumability, record ordering, and bounded prefetching into the on-wire `zfs send` format.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_send.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_traverse.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_traverse.c

Implements generic block-pointer tree traversal for datasets, destroyed objsets, and pools.

Key points:
- `traverse_impl()` is the shared walker behind `traverse_dataset_resume()`, `traverse_dataset()`, `traverse_dataset_destroyed()`, and `traverse_pool()`.
- Traversal is txg-filtered: blocks at or below `td_min_txg` are skipped, using logical birth time when `TRAVERSE_LOGICAL` is set and physical birth otherwise.
- Handles resumable traversal with `resume_skip_check()`, avoiding already-completed subtrees and converting indirect-block failures to level-0 resume bookmarks.
- Traverses ZIL blocks/records for mutable datasets when appropriate, including claimed-but-not-replayed log blocks.
- Supports pre-order and post-order callbacks with `TRAVERSE_PRE` and `TRAVERSE_POST`; callbacks may return `TRAVERSE_VISIT_NO_CHILDREN`.
- Distinguishes holes, redacted blocks, indirect blocks, dnode blocks, objset blocks, spill blocks, and ZIL blocks.
- Applies hole-birth logic so zero-birth holes are visited or skipped depending on feature state, possible object ID reuse, and `send_holes_without_birth_time`.
- `TRAVERSE_HARD` suppresses `EIO`/`ECKSUM` traversal failures after callback/resume handling.
- `TRAVERSE_NO_DECRYPT` causes protected metadata reads to use raw zio flags where needed.
- Metadata prefetch is issued by `traverse_prefetch_metadata()` and capped for indirect fanout by `zfs_traverse_indirect_prefetch_limit`.
- Optional data prefetch runs in `traverse_prefetch_thread()`, bounded by `zfs_pd_bytes_max` and coordinated through `prefetch_data_t`.

Important routines:
- `traverse_visitbp()` is the recursive block visitor and central control-flow point.
- `traverse_dnode()` invokes callbacks for dnodes and walks all block pointers plus spill block pointers.
- `prefetch_dnode_metadata()` schedules metadata prefetch for dnode block pointers and spills.
- `traverse_pool()` walks the MOS and each DSL dataset object, adjusting each dataset’s start txg by previous-snapshot txg.

Dependencies and interactions:
- Used by `dmu_send.c` to enumerate changed logical blocks in canonical order.
- Uses ARC reads for metadata traversal, ZIL parsing for intent-log blocks, dnode/object-set structures for recursion, and spa feature state for hole-birth decisions.
- Exports `traverse_dataset` and `traverse_pool`.

Research relevance:
- This file is the reusable block-tree scanner that makes send, scrub-like tools, and pool-level scans possible without each caller reimplementing dnode/indirect/ZIL traversal.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_traverse.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_tx.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_tx.c

Implements DMU transaction creation, hold declaration, space/memory reservation, txg assignment, throttling, callbacks, commit, and abort.

Key points:
- `dmu_tx_create_dd()`, `dmu_tx_create()`, and `dmu_tx_create_assigned()` initialize transactions, hold lists, callback lists, pool references, and start timestamps.
- Holds describe intended modifications before txg assignment: writes, appends, frees, clones, ZAP updates, bonus buffers, generic space, spill blocks, and SA attribute updates.
- `dmu_tx_hold_dnode_impl()` and `dmu_tx_hold_object_impl()` attach dnode references and create `dmu_tx_hold_t` records with refcounted space and memory estimates.
- `dmu_tx_check_ioerr()` proactively reads existing blocks needed by a future modification, surfacing I/O errors before DMU state is dirtied.
- Write/append/free accounting reads partial edge blocks and needed indirects, respecting block alignment and avoiding full-free level-0 dbuf instantiation assumptions.
- Clone accounting reserves BRT-entry memory and relevant indirect-block write space.
- ZAP accounting uses worst-case microzap/fatzap space and performs lookup-based leaf error checks where a name is known.
- SA helpers reserve layout registry ZAP updates, bonus space, and spill space depending on attribute registration, growth, and spill state.
- Debug-only `dmu_tx_dirty_buf()` verifies that dirty buffers match declared holds.

Assignment and throttling:
- `dmu_tx_try_assign()` rejects transactions with prior I/O errors, suspended pools, dirty-data pressure, or write-log pressure before taking an open txg.
- Uses `txg_hold_open()` and dnode `dn_assigned_txg` / `dn_tx_holds` to prevent conflicting assignment across adjacent txgs.
- Computes worst-case allocation size with `spa_get_worst_case_asize()` and reserves memory/asize through `dsl_dir_tempreserve_space()`.
- `dmu_tx_delay()` imposes a nonlinear delay based on dirty-data and TX_WRITE log pressure, capped by `zfs_delay_max_ns`.
- `dmu_tx_assign()` implements blocking/nonblocking retry semantics for `DMU_TX_WAIT`, `DMU_TX_NOTHROTTLE`, and `DMU_TX_SUSPEND`.
- `dmu_tx_wait()` waits for dirty space, pool resume, specific dnode assignment release, or next synced txg.

Lifecycle:
- `dmu_tx_commit()` releases dnode tx holds, clears temporary reservations, registers txg callbacks, releases txg sync holds, and destroys the transaction.
- `dmu_tx_abort()` is for unassigned transactions, clears any temporary reservation, runs callbacks with `ECANCELED`, and destroys the transaction.
- `dmu_tx_callback_register()` and `dmu_tx_do_callbacks()` provide end-of-txg callback support.
- `dmu_tx_init()` / `dmu_tx_fini()` install/remove `dmu_tx` kstats.

Dependencies and interactions:
- Coordinates with dbuf/dnode locking, txg machinery, DSL directory quotas/reservations, dirty-data throttling, ZAP/SA code, and spa suspension/failmode policy.
- Exports the public kernel DMU transaction API when built in-kernel.

Research relevance:
- This is the write-side admission-control layer for DMU mutations. It encodes the contract that callers must declare what they may dirty before assignment, enabling safe txg grouping, quota checks, error preflight, and backpressure.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_tx.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_zfetch.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_zfetch.c

Implements adaptive predictive prefetch for DMU dnode data and indirect blocks.

Key points:
- Maintains per-dnode `zfetch_t` state containing a bounded list of active `zstream_t` streams.
- Tunables control global disable, maximum streams, stream reap times, minimum/maximum data prefetch distance, maximum indirect prefetch distance, reorder tolerance, and tolerated hole fraction.
- Kstats track hits, future accesses, stride detections, past accesses, misses, max-stream pressure, issued I/O, and active I/O.
- `dmu_zfetch_init()` / `dmu_zfetch_fini()` initialize and tear down per-dnode stream state.
- `dmu_zfetch_stream_create()` creates, reuses, or reaps streams based on age, reference count, file size, and `zfetch_max_streams`.
- Streams record current expected block, recent future ranges, data prefetch distance, indirect prefetch distance, prefetch windows, missed status, and whether more prefetched blocks were consumed.
- `dmu_zfetch_hit()` advances a stream on sequential hits and folds future ranges into the current progress.
- `dmu_zfetch_future()` records bounded out-of-order future reads and converts them into stream progress when the filled fraction is high enough.
- `dmu_zfetch_prime()` seeds a stream for callers that already know an upcoming sequential range.
- `dmu_zfetch_prepare()` classifies accesses as hits, near hits, future ranges, past accesses, or misses, then calculates data and indirect prefetch windows.
- `dmu_zfetch_run()` issues the actual data and indirect `dbuf_prefetch_impl()` calls, batching concurrent callers so the last caller performs the stream’s prefetch work.
- `dmu_zfetch()` is the simple wrapper that prepares and immediately runs a prefetch.

Behavioral details:
- Predictive prefetch is skipped when disabled, when the objset requests no prefetch, or when indirect vdev mappings are not loaded.
- Metadata-only objset mode disables data prefetch while still allowing indirect prefetch.
- Small files and first-block reads have fast paths to avoid unnecessary stream creation.
- Prefetch distance ramps quickly up to the minimum distance, grows more slowly after that, and is capped by configured maximums.
- Active prefetch pressure against ARC size limits aggressive doubling.
- Completion callback `dmu_zfetch_done()` updates stream state and active-I/O accounting.

Dependencies and interactions:
- Uses dnode structure locks, dbuf prefetch APIs, ARC flags, spa indirect-vdev readiness, refcounts, weighted sums, aggregate sums, and kstats.
- Complements prescient prefetch paths used by traversal/send; the global disable only disables predictive prefetch, not prescient prefetch.

Research relevance:
- This file is OpenZFS’s adaptive sequential/reordered read predictor. It reduces demand-read latency for regular file and volume access while bounding misprediction cost through stream limits, distance caps, stale-stream reap, and ARC pressure checks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_zfetch.c -->