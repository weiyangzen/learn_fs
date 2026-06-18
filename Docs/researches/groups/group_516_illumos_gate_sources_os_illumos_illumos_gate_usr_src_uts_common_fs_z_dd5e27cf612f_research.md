# Group Research: group_516_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_dd5e27cf612f

Read completely under `Docs/research_subset_a.md` scope:
- `dmu_objset.c` 2990 lines
- `dmu_recv.c` 2961 lines
- `dmu_send.c` 1540 lines
- `dmu_traverse.c` 741 lines

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_objset.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_objset.c

This file implements ZFS DMU objset lifecycle and management: opening, holding, owning, creating, cloning, syncing, evicting, accounting, quota upgrades, statistics, snapshot/child enumeration, and small objset utility helpers.

Core responsibilities:
- Initializes and destroys global objset lock state with `dmu_objset_init()` / `dmu_objset_fini()`.
- Provides accessors for objset SPA, ZIL, DSL pool/dataset, type, name, id, dnode size, sync property, and logbias.
- Registers DSL property callbacks to keep live `objset_t` policy fields synchronized for checksum, compression, copies, dedup, cache policy, sync mode, logbias, redundant metadata, recordsize, dnodesize, and special small-block threshold.
- Opens on-disk `objset_phys_t` through ARC in `dmu_objset_open_impl()`, including encrypted/raw root block handling, block-size expansion for newer `objset_phys_t` layouts, ZIL allocation, special dnode opening, dirty-dnode multilist creation, and mutex setup.
- Converts DSL datasets to objsets with `dmu_objset_from_ds()`, serializing open through `ds_opening_lock`.
- Implements held and owned objset entry points: `dmu_objset_hold_flags()`, `dmu_objset_hold()`, `dmu_objset_own()`, `dmu_objset_own_obj()`, release/disown helpers, and ownership refresh for userspace upgrade flows.
- Handles objset eviction in two phases: unregister properties, tear down SA, evict dbufs, register with SPA eviction tracking, then close special dnodes/free ZIL/ARC buffer/mutexes when all dnodes are gone.
- Creates objsets and datasets via sync tasks: `dmu_objset_create_check()`, `dmu_objset_create_sync()`, and `dmu_objset_create()`. Encrypted creation forces immediate sync of encryption-dependent data before key mapping removal.
- Creates clones from snapshot origins through `dmu_objset_clone_check()`, `dmu_objset_clone_sync()`, and `dmu_objset_clone()`.
- Implements indirect remapping after device removal with `dmu_objset_remap_indirects()`, tracking last remap TXG in the DSL dir.
- Performs objset sync in `dmu_objset_sync()`: writes the root objset block, syncs meta/user/group/project special dnodes, parallel-syncs dirty regular dnodes, handles user accounting lists, updates ZIL header, and starts root block IO.
- Maintains user/group/project space accounting and object accounting through dirty dnode capture, AVL aggregation caches, ZAP increments, and deferred taskq processing.
- Provides upgrade machinery for userspace/userobj/projectquota accounting using `dmu_objset_upgrade()` background task dispatch and stoppable upgrade state.
- Lists snapshots and child dirs through ZAP cursors, and walks whole dataset trees with both path-based and DSL-pool/object based find routines.
- Exposes stats and state helpers such as `dmu_objset_space()`, `dmu_objset_fast_stat()`, `dmu_objset_stats()`, `dmu_objset_is_snapshot()`, encryption compatibility, user pointer accessors, `dmu_fsname()`, and dirty-space reservation.

Important control-flow notes:
- `dmu_objset_open_impl()` is the central constructor for in-memory `objset_t`; it wires together ARC, DSL properties, ZIL, special dnodes, dirty lists, and locks.
- `dmu_objset_sync()` is the central writeback path and assumes syncing context. It uses root block callbacks `dmu_objset_write_ready()` and `dmu_objset_write_done()` to update fill counts, root block pointers, and dataset block accounting.
- User accounting is skipped during encrypted receives and pool claiming, then completed later when keys/ownership make it safe.
- Raw receive state affects objset sync: encrypted objsets can write `os_phys_buf` raw when `os_raw_receive` or `os_next_write_raw` is set.
- `dmu_objset_find_dp()` can parallelize child enumeration with a taskq, unless serialization is requested or the pool config lock is write-held.
- Hidden `$` objsets are deliberately skipped during enumeration.

Key dependencies:
- DSL dataset/dir/pool APIs for ownership, creation, cloning, snapshotting, stats, and namespace traversal.
- ARC/dbuf/dnode/ZIL code for physical IO, dirty tracking, special dnodes, and intent-log syncing.
- ZAP for user accounting objects, snapshot/child listings, and upgrade metadata.
- SPA feature/version checks for userspace accounting, project quota, large dnodes, encryption, and remapping behavior.

Risk-sensitive invariants:
- Many paths require pool config lock or syncing context; assertions encode those contracts.
- Encrypted objset creation and raw receive handling are carefully ordered around key mappings and raw ARC buffers.
- Object accounting relies on dirty dnode ordering and per-TXG dirty links.
- Eviction uses `os_lock` as a barrier for `dnode_move()` safety.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_objset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_recv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_recv.c

This file implements the receive side of ZFS send/receive streams. It validates stream begin records, creates or resumes temporary receive datasets, reads stream records, applies them to the DMU, manages raw/encrypted receive state, finalizes snapshots, and cleans up failed receives.

Core responsibilities:
- Defines receive tunables and tags: `zfs_recv_queue_length`, `dmu_recv_tag`, and temporary clone name `%recv`.
- Validates begin records for existing targets, new targets, clone receives, resumable receives, raw/encrypted streams, feature compatibility, snapshot/filesystem limits, origin GUIDs, and force behavior.
- Creates receive targets in sync context:
  - Existing filesystem receives create a temporary `%recv` clone.
  - New filesystem receives create a new dataset.
  - Raw full receives defer objset physical creation until stream processing can consume raw encryption payload metadata.
  - Resumable receives store resume metadata in dataset ZAP fields.
- Supports resume begin by finding an inconsistent `%recv` or target dataset, validating saved resume fields, toguid/fromguid, ownership, and snapshot state, then re-owning it for receive.
- Reads stream records from a vnode, updates Fletcher checksums, supports byteswapped streams, validates record checksums, and allocates payload buffers or ARC buffers.
- Uses a two-thread pipeline in `dmu_recv_stream()`:
  - Reader thread reads records, validates payload/checksum, issues prefetches, and enqueues records.
  - Writer thread dequeues records and applies DMU changes.
- Applies all replay record types:
  - `DRR_OBJECT`: claim/reclaim dnodes, update bonus data, checksum/compress settings, raw dnode geometry, spill flags, and object-range crypto params.
  - `DRR_FREEOBJECTS`: frees object ranges.
  - `DRR_WRITE`: assigns loaned ARC buffers into object offsets.
  - `DRR_WRITE_BYREF`: handles dedup streams by copying from referenced datasets via GUID map.
  - `DRR_WRITE_EMBEDDED`: writes embedded blocks for non-raw streams.
  - `DRR_SPILL`: writes or ignores spill blocks depending on stream flags.
  - `DRR_FREE`: frees byte ranges.
  - `DRR_OBJECT_RANGE`: captures raw dnode-block crypto params.
  - `DRR_END`: verifies final stream checksum.
- Manages dedup receive GUID maps using AVL trees registered through `zfs_onexit`, with dataset ownership cleanup callbacks.
- Handles raw receive encryption payloads from the `DRR_BEGIN` nvlist through `dsl_crypto_recv_raw()` and delayed key updates for existing datasets.
- Maintains resumable receive progress by saving object, offset, and bytes-read fields during successful write records.
- Finalizes receives in sync context:
  - For existing targets, swaps the `%recv` clone into the origin head, optionally destroys newer snapshots when forced, snapshots the updated head, and destroys the temporary receive dataset.
  - For new targets, snapshots the received dataset and clears inconsistent/resume state.
  - Sets snapshot creation time, GUID, and raw IV set GUID where supplied.
- Cleans failed receives with `dmu_recv_cleanup_ds()`, preserving resumable inconsistent datasets when possible or destroying non-resumable partial receives.

Important control-flow notes:
- `dmu_recv_begin()` must be followed by `dmu_recv_stream()` on success, and `dmu_recv_stream()` must be followed by `dmu_recv_end()` on success.
- Receive datasets are intentionally marked `DS_FLAG_INCONSISTENT` during stream application and cleared only during successful end sync.
- The receive reader keeps an ordered object ignore list to avoid unsafe/useless prefetches when object allocation or blocksize changes.
- Resume correctness depends on ordered write records and validation of begin payload resume object/offset against dataset ZAP state.
- Raw receive path preserves on-disk encrypted bytes, dnode layout, byteorder, salt, IV, MAC, compression type, and maxblkid.

Key dependencies:
- DMU object, dnode, ARC buffer, dbuf, and transaction APIs for replaying stream records.
- DSL dataset/dir/snapshot/clone swap/destroy APIs for receive target lifecycle.
- SPA feature checks for embedded data, LZ4, large blocks, large dnodes, extensible dataset, and encryption.
- ZAP/NVList for resume metadata and raw encryption payloads.
- `zfs_onexit` for dedup stream GUID map lifetime.

Risk-sensitive invariants:
- Stream records must be ordered for resumable receive state.
- Raw receives cannot mix with embedded data and require spill-block stream flags.
- Existing encrypted filesystem replacement is restricted because old and new encryption key state cannot safely coexist during forced full replacement.
- Inconsistent datasets must not be exposed as normal mounted state before `dmu_recv_end_sync()` completes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_recv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_send.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_send.c

This file implements the send side of ZFS send/receive streams. It traverses datasets, converts changed blocks/dnodes into DMU replay records, writes the stream to a vnode, supports incremental/clone/raw/resume sends, and estimates send sizes.

Core responsibilities:
- Defines send tunables for corrupt-data substitution, queue length, free-record flags, unmodified spill blocks, and estimate recordsize override.
- Writes stream bytes with `dump_bytes()` and maintains stream offset under the dataset sendstream lock.
- Builds checksummed replay records with `dump_record()`, updating Fletcher state and tracking BEGIN/END emission.
- Emits record types:
  - `DRR_FREE` with aggregation for adjacent byte ranges.
  - `DRR_WRITE` for normal, compressed, or raw blocks.
  - `DRR_WRITE_EMBEDDED` for eligible embedded payloads.
  - `DRR_SPILL` for spill blocks, including raw fields and unmodified spill markers.
  - `DRR_FREEOBJECTS` with aggregation.
  - `DRR_OBJECT` for dnode metadata and bonus payloads.
  - `DRR_OBJECT_RANGE` for raw dnode-block encryption metadata.
  - `DRR_BEGIN` / `DRR_END` in `dmu_send_impl()`.
- Handles feature flags for SA spill, large blocks, large dnodes, embedded data, compressed send, raw send, LZ4, and resumable sends.
- Uses `traverse_dataset_resume()` from `dmu_traverse.c` in a producer thread to enqueue block records into a `bqueue`; the main send thread dequeues records, reads data from ARC, and writes replay records.
- Implements block classification in `do_dump()`:
  - Skips special objects and indirect blocks.
  - Converts holes in meta-dnode space to freeobjects.
  - Converts data holes to free ranges.
  - Reads dnode blocks and emits object records.
  - Reads SA/spill blocks and emits spill records.
  - Emits embedded writes when stream features permit.
  - Reads regular blocks as raw, compressed, or normal payloads.
  - Splits large blocks when the receiver did not negotiate large-block support.
- Supports raw encrypted sends by not decrypting traversal data, authenticating objset phys for non-raw encrypted sends, and including encryption parameters in stream records and BEGIN payload.
- Supports resume sends by including resume object/offset in BEGIN payload and starting traversal from the corresponding bookmark.
- Provides public send entry points:
  - `dmu_send_obj()` sends by object IDs within a pool.
  - `dmu_send()` sends by dataset/bookmark names and can own live heads to freeze them during send.
- Provides size estimates:
  - `dmu_send_estimate()` uses dataset accounting or `dsl_dataset_space_written()`.
  - `dmu_send_estimate_from_txg()` traverses blocks born after a TXG.
  - `dmu_adjust_send_estimate_for_indirects()` adjusts data-space estimates for indirect blocks and replay record overhead.

Important control-flow notes:
- `dump_free()` and `dump_write()` enforce increasing object/offset order; receive depends on this for correctness and resumability.
- `dump_dnode()` sends an object record, then a free-to-end marker past maxblkid, and may send unmodified spill blocks for compatibility.
- Raw send implies compressed and large-block-capable stream behavior.
- Non-raw encrypted sends authenticate `os_phys_buf` before sending.
- Send cancellation is coordinated by queue draining and an EOS marker from the traversal thread.
- If `zfs_send_corrupt_data` is enabled, unreadable data blocks can be replaced by a fixed corrupt-data pattern instead of failing.

Key dependencies:
- Dataset traversal callbacks from `dmu_traverse.c`.
- ARC raw/compressed/normal reads for block payload acquisition.
- DSL dataset/bookmark logic for incremental ancestry and clone detection.
- DMU backup record formats in `dmu_send.h` / replay records.
- Crypto helpers for raw send key and block parameter serialization.

Risk-sensitive invariants:
- Feature flags must match the receiver’s capabilities; large blocks, embedded data, LZ4, raw, and compression alter record layout.
- Raw streams must preserve encrypted block metadata exactly.
- Resume sends must begin at the same object/offset expected by the receiver.
- The stream must emit valid BEGIN and END records or verification fails before cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_traverse.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_traverse.c

This file implements generic ZFS block tree traversal over datasets, destroyed dataset root blocks, and whole pools. It is used by send, scrub-like walkers, estimates, and other DMU consumers that need ordered visits to block pointers and dnodes.

Core responsibilities:
- Defines traversal state `traverse_data_t` and prefetch state `prefetch_data_t`.
- Traverses ZIL blocks/records for non-snapshot datasets when appropriate, visiting claimed but unreplayed log blocks and stable read-only log blocks.
- Implements resume-aware traversal using `zbookmark_phys_t`, with skip modes for already completed subtrees and post-order resume semantics.
- Performs metadata prefetch for indirect, dnode, objset, and spill metadata when `TRAVERSE_PREFETCH_METADATA` is enabled.
- Supports data prefetch through a background traversal thread when `TRAVERSE_PREFETCH_DATA` is enabled, throttled by `zfs_pd_bytes_max`.
- Visits block pointers in `traverse_visitbp()`:
  - Skips blocks born before or at `td_min_txg`, with special handling for holes without birth times.
  - Calls callbacks in pre-order or post-order depending on flags.
  - Reads indirect blocks and recursively visits children.
  - Reads dnode blocks and recursively traverses contained dnodes.
  - Reads objset blocks and traverses meta/user/group/project-used dnodes.
  - Handles `TRAVERSE_HARD` by ignoring `EIO`/`ECKSUM`.
  - Records resume bookmark when traversal stops on error.
- Traverses individual dnodes in `traverse_dnode()`, including normal blkptrs and spill blkptrs.
- Implements public traversal entry points:
  - `traverse_dataset_resume()`
  - `traverse_dataset()`
  - `traverse_dataset_destroyed()`
  - `traverse_pool()`

Important control-flow notes:
- `traverse_impl()` is the central setup/teardown function. It initializes traversal state, handles hole-birth feature TXG, optionally traverses ZIL, launches prefetch traversal, performs the main root traversal, cancels prefetch, and destroys synchronization primitives.
- Root traversal starts at bookmark `(objset, ZB_ROOT_OBJECT, ZB_ROOT_LEVEL, ZB_ROOT_BLKID)`.
- Resume logic intentionally resumes at level-0 bookmarks even if traversal stopped at an indirect block.
- Hole birth behavior depends on `SPA_FEATURE_HOLE_BIRTH`, `send_holes_without_birth_time`, and whether object ID reallocation is possible.
- Protected/encrypted blocks are read with `ZIO_FLAG_RAW` when `TRAVERSE_NO_DECRYPT` is set.
- `traverse_pool()` walks the MOS first, then scans MOS objects for DSL dataset bonus types and traverses each dataset after its previous snapshot TXG.

Key dependencies:
- ARC reads/prefetch for block contents.
- Dnode and objset physical formats for recursive descent.
- DSL dataset/pool APIs for pool-wide traversal.
- ZIL parser for intent-log traversal.
- SPA feature state for hole birth behavior and raw/protected block handling.

Risk-sensitive invariants:
- Dataset contents must not be changing on disk during traversal, except for documented syncing/read-only contexts.
- Pre and post traversal flags are mutually exclusive.
- Prefetch resume state is separated from main resume state so prefetch can track progress without mutating caller state.
- Whole-pool traversal assumes a stable pool, such as zdb or sync context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_traverse.c -->