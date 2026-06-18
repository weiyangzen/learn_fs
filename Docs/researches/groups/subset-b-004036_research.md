# subset-b-004036 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.c

## Purpose
`vdo.c` is the in-memory lifecycle and operating core for a VDO instance. It initializes the global VDO registry, constructs and tears down VDO objects, configures work queues and thread IDs, formats first-use devices, loads/saves geometry and component superblocks, coordinates read-only and recovery transitions, exposes statistics, and provides thread-affinity assertions used by the rest of dm-vdo.

## Important APIs, Types, and Functions
Key internal types include `sync_completion`, used to run a completion callback on a VDO work queue and wait from a caller thread, and `device_registry`, a small rwlock-protected list of live VDO instances. Public entry points include `vdo_initialize_device_registry_once()`, `vdo_find_matching()`, `vdo_make_thread()`, `vdo_make()`, `vdo_destroy()`, `vdo_load_super_block()`, `vdo_save_components()`, `vdo_enable_read_only_entry()`, `vdo_enter_read_only_mode()`, `vdo_set_compressing()`, `vdo_fetch_statistics()`, and `vdo_get_physical_zone()`.

## Control Flow
Creation starts in `vdo_make()`, which allocates a `struct vdo`, calls `initialize_vdo()`, assigns a thread-name prefix, allocates `vdo_thread` records, and constructs admin, flusher, packer, data-vio pool, I/O submitter, optional bio-ack queue, and CPU queues. `initialize_vdo()` reads the geometry block; a zeroed geometry block triggers `vdo_format()`, otherwise the geometry is decoded. Formatting creates a UUID/nonce, initializes geometry and component states, and marks `needs_formatting`. Destruction reverses construction through `finish_vdo()`, registry removal, component frees, listener frees, thread config cleanup, compression-context cleanup, and final object free.

## State and Persistence Behavior
Persistent layout state is represented by the geometry block and superblock. `record_vdo()` snapshots volatile component state into `vdo->states`; `vdo_save_super_block()` encodes it and writes it with preflush/FUA. Geometry saves are similarly encoded and written at `VDO_GEOMETRY_BLOCK_LOCATION`. A superblock write failure marks the superblock `unwritable` to avoid later persistence that could make recovery semantics inconsistent. `vdo_set_state()` and `vdo_get_state()` use atomic state plus explicit memory barriers.

## Dependencies and Integration Points
This file is the coordinator for most dm-vdo subsystems: block map, recovery journal, slab depot, logical/physical/hash zones, dedupe, packer, flusher, io-submitter, VIO metadata I/O, admin state, encodings, and statistics. It integrates with Linux block APIs for zeroout and flushes, device-mapper target naming, dm-kcopyd for layout copy support, work queues via `funnel-workqueue`, and LZ4 compression contexts for CPU queue work.

## Risks and Test Signals
Risk concentrates around lifecycle unwinding, thread-affinity assumptions, read-only transition races, and persistence ordering. Important tests should cover fresh format vs existing geometry load, partial construction failure cleanup, superblock write failure making the device read-only/unwritable, suspend/resume read-only notification gating, compression toggling from non-packer context, statistics consistency, and invalid physical block lookup paths. Fault injection around metadata reads/writes and flush errors is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.h

## Purpose
`vdo.h` declares the central VDO object model and public in-driver API used by the dm-vdo implementation. It defines thread topology, read-only notification infrastructure, persistent metadata wrappers, admin state fields, statistics counters, and the large `struct vdo` that ties component subsystems together.

## Important APIs, Types, and Functions
Important types include `enum notifier_state`, `struct read_only_listener`, `struct vdo_thread`, `struct atomic_bio_stats`, `struct atomic_statistics`, `struct read_only_notifier`, `struct thread_config`, `struct vdo_geometry_block`, `struct vdo_super_block`, `struct vdo_administrator`, and `struct vdo`. Function declarations cover construction/destruction, thread creation, superblock and geometry persistence, synchronous flush, admin-state access, compression, statistics, read-only/recovery mode, thread assertions, physical-zone lookup, and status dumping.

## Control Flow
The header establishes the contracts used by `vdo.c` and other VDO components. Callers construct a VDO through `vdo_make()`, create required work queues with `vdo_make_thread()` or `vdo_make_default_thread()`, transition the instance through load/save/admin operations, and eventually call `vdo_destroy()`. Read-only flow is exposed through listener registration, entry enablement, notification drain/re-enable, and forced entry APIs.

## State and Persistence Behavior
`struct vdo` holds both atomic current mode (`state`) and encoded component states (`states`) destined for the superblock. `vdo_geometry_block` and `vdo_super_block` pair VIOs with fixed buffers for on-disk metadata. `read_only_notifier` stores the first read-only error and notification state under a spinlock. Statistics are atomic because bios and metadata I/O complete from multiple contexts.

## Dependencies and Integration Points
The header includes Linux atomic, blk, completion, kcopyd, list, and spinlock types, plus VDO-specific admin-state, encodings, workqueue, packer, physical-zone, statistics, thread-registry, and type definitions. It is a high-fanout interface consumed by VIO, zones, admin paths, target code, and statistics reporting.

## Risks and Test Signals
The largest risk is struct contract drift: many subsystems assume fields are initialized in a specific order and accessed only from expected VDO threads. Tests should validate read-only listener registration restrictions, state access from arbitrary threads, correct bio-ack queue detection, and that stats counters remain coherent under concurrent bio submission/completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.c

## Purpose
`vio.c` implements VDO I/O object support. It allocates VDO-owned bios, initializes metadata VIOs, maps VIOs to backing-device bios, records metadata I/O errors, manages thread-affine VIO pools, and maintains bio statistics for VDO-generated and externally serviced I/O.

## Important APIs, Types, and Functions
The local `struct vio_pool` owns preallocated `pooled_vio` entries, a shared data buffer, available/busy lists, a wait queue, and the VDO thread on which it may be used. Important functions include `pbn_from_vio_bio()`, `vdo_create_bio()`, `allocate_vio_components()`, `create_multi_block_metadata_vio()`, `vio_reset_bio_with_size()`, `update_vio_error_stats()`, `vio_record_metadata_io_error()`, `make_vio_pool()`, `acquire_vio_from_pool()`, `return_vio_to_pool()`, and bio accounting helpers.

## Control Flow
Metadata VIO creation allocates a VIO-owned bio sized for one or more VDO blocks, initializes completion metadata, and attaches an optional parent and data buffer. Submission paths reset the bio, set device/operation/endio/sector properties, build inline bvecs from kernel or vmalloc memory, and later continue the VIO completion after endio. VIO pools synchronously hand an available entry to a waiter callback or enqueue the waiter until `return_vio_to_pool()` notifies the oldest waiter.

## State and Persistence Behavior
VIOs do not persist state directly, but they are the mechanism used by superblock, geometry, journal, and block-map metadata to reach storage. The pool tracks `busy_count`, busy and available lists, and waiters. Error handling increments read-only, no-space, and other error counters and rate-limits log output. `pbn_from_vio_bio()` reverses the bio sector mapping to report physical block numbers with geometry offset accounted for.

## Dependencies and Integration Points
The file depends on Linux bio/blkdev/page APIs, ratelimit logging, VDO memory allocation, assertions, constants, io-submitter, wait queues, and `vdo.h`. It integrates with completion scheduling via `continue_vio_after_io()`, and its statistics feed the VDO statistics reported by `vdo_fetch_statistics()`.

## Risks and Test Signals
Important risks are bvec construction for vmalloc vs direct memory, multi-block size bounds, thread-affine pool misuse, returning pooled VIOs while waiters exist, and accounting errors when endio paths are retried. Tests should cover unaligned buffer offsets, maximum block counts, pool starvation/wakeup order, metadata I/O failures, and statistic increments for reads, writes, discards, flushes, FUA, and empty flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.h

## Purpose
`vio.h` declares the VDO I/O abstraction used by metadata and data paths. It exposes helpers for converting completions to VIOs, mapping VIOs to bio-zone threads, initializing VIO objects, resetting bios, accounting completions, and using pooled VIO entries.

## Important APIs, Types, and Functions
`MAX_BLOCKS_PER_VIO` derives the maximum VDO blocks addressable by bio vec limits. `struct pooled_vio` embeds a `struct vio`, pool linkage, and pool context. Inline helpers include `as_vio()`, `get_vio_bio_zone_thread_id()`, `assert_vio_in_bio_zone()`, `initialize_vio()`, `is_data_vio()`, `get_metadata_priority()`, `continue_vio()`, `continue_vio_after_io()`, and `vio_as_pooled_vio()`. Declarations cover VIO allocation/free, bio reset/properties, error stats, and pool operations.

## Control Flow
Callers initialize a VIO around a preallocated bio and VDO completion, then reset the bio per I/O with a target PBN, operation flags, buffer, and endio callback. Endio paths call `continue_vio_after_io()` to count completed bios, install the next completion callback, translate block status, and enqueue the completion. Pooled VIO users acquire asynchronously via a `vdo_waiter` callback and return entries to either the next waiter or the available list.

## State and Persistence Behavior
The header defines VIO state needed for persistence I/O but does not itself persist data. It guarantees that data VIOs are single-block through a `BUG_ON()` in `initialize_vio()`, while metadata VIOs can span up to `MAX_BLOCKS_PER_VIO`. Bio-zone state determines which VDO bio thread should submit the operation.

## Dependencies and Integration Points
`vio.h` includes Linux bio/blkdev/list APIs and VDO completion, constants, types, and VDO declarations. It is used by metadata components, io-submitter, VDO superblock/geometry code, data-vio handling, and statistics collection.

## Risks and Test Signals
The interface is sensitive to callback-thread IDs, bio-zone calculation, completion type correctness, and error propagation. Useful tests assert that completion-to-VIO conversions reject wrong types, data VIOs cannot be multi-block, metadata priority maps to the expected work queue priority, and `continue_vio_after_io()` preserves the first non-success result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.c

## Purpose
`wait-queue.c` implements VDO's lightweight callback wait queue. It provides FIFO enqueue, dequeue, transfer, selective extraction, and notification operations for VDO resources such as VIO pools without using Linux wait queues.

## Important APIs, Types, and Functions
The file implements `vdo_waitq_enqueue_waiter()`, `vdo_waitq_transfer_all_waiters()`, `vdo_waitq_notify_all_waiters()`, `vdo_waitq_get_first_waiter()`, `vdo_waitq_dequeue_matching_waiters()`, `vdo_waitq_dequeue_waiter()`, and `vdo_waitq_notify_next_waiter()`. The underlying data structure is a circular singly linked FIFO represented by a tail pointer and a length.

## Control Flow
Enqueue checks that a waiter is not already linked, then either self-links it as the first entry or splices it after the tail and advances the tail pointer. Dequeue returns the oldest waiter, updates the circular link or empties the queue, clears the waiter's `next_waiter`, and decrements length. Notify operations dequeue entries then invoke either an explicit callback or the waiter's stored callback.

## State and Persistence Behavior
All state is volatile and in-memory. `transfer_all_waiters()` can splice two queues in constant time by swapping head links and moving length, then reinitializes the source. `notify_all_waiters()` first transfers to a local queue, preventing callbacks that re-enqueue waiters from creating an infinite loop over newly added entries.

## Dependencies and Integration Points
The implementation depends on VDO assertions and status codes plus the declarations in `wait-queue.h`. It is integrated by VIO pools and other VDO resource allocators that operate on specific VDO workqueue threads and therefore do not need kernel waitqueue locking semantics.

## Risks and Test Signals
Risks are list corruption from double enqueue, incorrect tail/head splicing, callbacks re-entering queue operations, and length drift. Tests should cover empty/single/multiple enqueue-dequeue sequences, transfer into empty and non-empty queues, notify-all with callbacks that enqueue new waiters, and matching extraction preserving relative order for matched and unmatched entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.h

## Purpose
`wait-queue.h` defines VDO's small, callback-oriented wait queue abstraction. It is intended for VDO's thread-based resource scheduling where callers need FIFO callbacks but not Linux waitqueue sleeping, locking, priorities, or timers.

## Important APIs, Types, and Functions
`struct vdo_wait_queue` stores a tail pointer and waiter count. `struct vdo_waiter` stores the next pointer and optional callback. Function pointer types `vdo_waiter_callback_fn` and `vdo_waiter_match_fn` define notification and filtering contracts. Inline helpers include `vdo_waiter_is_waiting()`, `vdo_waitq_init()`, `vdo_waitq_has_waiters()`, and `vdo_waitq_num_waiters()`.

## Control Flow
Clients initialize a queue, embed or allocate waiters, set each waiter's callback, and enqueue when a resource is unavailable. Resource return paths call `vdo_waitq_notify_next_waiter()` or `vdo_waitq_notify_all_waiters()` to resume queued operations. Matching extraction supports moving selected waiters to a separate queue for targeted wakeups.

## State and Persistence Behavior
The queue is in-memory only. The circular-list invariant is documented in detail: empty queues have a null tail, singleton queues self-link, and multi-entry queues have the tail link point to the oldest entry. `next_waiter == NULL` is both the unqueued sentinel and the predicate used by `vdo_waiter_is_waiting()`.

## Dependencies and Integration Points
The header uses only basic Linux compiler/types support and is included by VIO pool code and other VDO components that need simple asynchronous waiter callbacks. It intentionally avoids `linux/wait.h` because the VDO model already supplies serialized thread ownership.

## Risks and Test Signals
Callers must not enqueue a waiter already on any queue and must not assume thread-safe access without external serialization. Tests should validate queue initialization, waiter waiting predicates, length accounting, FIFO order, and behavior when callbacks are supplied either per waiter or as a notification override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.c

## Purpose
`dm-verity-fec.c` adds forward error correction to dm-verity. When data or hash verification fails, it uses Reed-Solomon parity data to reconstruct the target block, then revalidates the corrected bytes against the expected verity digest before allowing them to be used.

## Important APIs, Types, and Functions
Important functions include `fec_decode_bufs()`, `fec_read_bufs()`, `fec_decode()`, `verity_fec_decode()`, `__verity_fec_finish_io()`, `verity_fec_status_table()`, `verity_fec_dtr()`, `verity_is_fec_opt_arg()`, `verity_fec_parse_opt_args()`, `verity_fec_ctr_alloc()`, and `verity_fec_ctr()`. It uses `struct dm_verity_fec` for persistent configuration and pools, and `struct dm_verity_fec_io` for per-bio decode state.

## Control Flow
`verity_fec_decode()` is called from dm-verity metadata or data mismatch handling. It lazily allocates per-bio FEC state from mempools, maps metadata blocks into the FEC block namespace when needed, and tries decoding without erasure hints first. If that fails, it reads and hashes related blocks to locate erasures and retries. Decoding deinterleaves message bytes from data/hash regions, reads parity blocks through dm-bufio, calls `decode_rs8()`, writes corrected bytes to an output buffer, and finally hashes the output to prove it matches `want_digest`.

## State and Persistence Behavior
The FEC target state records the parity device, parity start, covered block count, region geometry, hash coverage, RS roots, `rs_k`, bufio clients, mempools, kmem cache, and corrected-block counter. No repaired data is persisted by this file; corrected bytes are copied into the caller's destination buffer for the current bio. Mempool-backed state is released in `__verity_fec_finish_io()`.

## Dependencies and Integration Points
The file depends on dm-verity hash APIs, dm-bufio, dm target parsing, Linux rslib, math helpers, mempools, and kmsg logging. Constructor integration happens through dm-verity optional arguments: `use_fec_from_device`, `fec_blocks`, `fec_start`, and `fec_roots`. Status integration appends the FEC table options and reports corrected counters through the main verity status path.

## Risks and Test Signals
Risks include off-by-one region math, parity reads spanning block boundaries, recursion during metadata recovery, low-memory buffer allocation, and accidentally accepting miscorrected data. Tests should include data-block and metadata-block correction, parity boundary crossing, missing/invalid constructor options, mismatched data/hash block sizes, undersized devices, erasure-assisted recovery, and digest mismatch after RS decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.h

## Purpose
`dm-verity-fec.h` declares the optional dm-verity forward-error-correction interface, its target-table option names, Reed-Solomon parameter bounds, persistent FEC configuration, and per-bio FEC state.

## Important APIs, Types, and Functions
The header defines `DM_VERITY_FEC_RS_N`, minimum/maximum roots, deinterleave buffer sizing, option strings, `struct dm_verity_fec`, and `struct dm_verity_fec_io`. When `CONFIG_DM_VERITY_FEC` is enabled it declares `verity_fec_decode()`, `verity_fec_status_table()`, `verity_fec_finish_io()`, `verity_fec_init_io()`, option parsing, destructor, and constructor helpers. When disabled it supplies stubs.

## Control Flow
The main dm-verity target calls `verity_fec_ctr_alloc()` early, lets optional argument parsing populate `v->fec`, calls `verity_fec_ctr()` after hash tree setup, initializes per-bio FEC state with `verity_fec_init_io()`, invokes `verity_fec_decode()` only after verification failures, and calls `verity_fec_finish_io()` when completing each bio.

## State and Persistence Behavior
FEC configuration is runtime state derived from the target table and parity device. `corrected` is an atomic runtime counter. Per-bio state stores Reed-Solomon control data, erasure indexes, output buffer, recursion level, number of allocated buffers, and flexible-array deinterleave buffers. The header does not define on-disk format; it describes how existing parity blocks are consumed.

## Dependencies and Integration Points
The header includes `dm-verity.h` and Linux rslib. It is tightly coupled to the dm-verity target's block geometry, hash validation, and per-IO data lifecycle. Compile-time stubs allow the main target to parse and build without FEC support.

## Risks and Test Signals
Tests should cover both configured and unconfigured builds. Enabled builds need option-count accounting, FEC-enabled predicate behavior, per-bio initialization/finish idempotence, and correct propagation of `-EOPNOTSUPP` or `-EINVAL` from disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-loadpin.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-loadpin.c

## Purpose
`dm-verity-loadpin.c` lets LoadPin decide whether a block device is backed by a trusted dm-verity target. It compares a live verity target's root digest against a global list of trusted root digests supplied through LoadPin integration.

## Important APIs, Types, and Functions
The file defines the global `dm_verity_loadpin_trusted_root_digests` list and implements `dm_verity_loadpin_is_bdev_trusted()`. The helper `is_trusted_verity_target()` validates that a target is dm-verity, checks that its corruption mode is one of EIO/restart/panic rather than logging-only, obtains a copy of the root digest through `dm_verity_get_root_digest()`, and compares it with trusted entries.

## Control Flow
`dm_verity_loadpin_is_bdev_trusted()` rejects null devices and empty trust lists, resolves the mapped device from `bd_dev`, obtains the live table under SRCU, requires a singleton table, fetches target 0, and delegates to `is_trusted_verity_target()`. It then releases the live table and mapped device references before returning the trust result.

## State and Persistence Behavior
This file stores no persistent state. Its only state is the global trusted digest list, which is inspected but not modified here. It allocates a temporary digest copy via `dm_verity_get_root_digest()` and frees it after comparison.

## Dependencies and Integration Points
It depends on device-mapper internals (`dm.h`, `dm-core.h`), public dm-verity query helpers, and `linux/dm-verity-loadpin.h` for trusted digest structures. It integrates with LoadPin's filesystem trust decisions by answering whether a superblock's block device sits on an approved verity root.

## Risks and Test Signals
Risks include races around table lifetime, rejecting valid multi-target stacks, and trusting logging-mode verity devices that allow corrupted reads. Tests should cover null/non-DM devices, empty trust list, non-verity target, multi-target table, mode filtering, digest mismatch, digest match, and cleanup of allocated root digest copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-loadpin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-target.c

## Purpose
`dm-verity-target.c` implements the `verity` device-mapper target for transparent read-only block integrity verification. It maps reads to a data device, verifies returned blocks against a Merkle hash tree stored on a hash device, handles corruption and I/O error policies, optionally repairs data via FEC, optionally verifies the root hash signature at table load, and exposes status/IMA/LSM metadata.

## Important APIs, Types, and Functions
Key functions include `verity_hash()`, `verity_hash_at_level()`, `verity_verify_level()`, `verity_hash_for_block()`, `verity_recheck()`, `verity_handle_data_hash_mismatch()`, `verity_verify_io()`, `verity_end_io()`, `verity_map()`, `verity_status()`, `verity_parse_opt_args()`, `verity_setup_hash_alg()`, `verity_setup_salt_and_hashstate()`, `verity_ctr()`, `verity_dtr()`, `dm_verity_get_mode()`, `dm_verity_get_root_digest()`, and `dm_is_verity_target()`. The file also defines module parameters for hash prefetch sizing and bottom-half verification thresholds.

## Control Flow
Constructor parsing validates the fixed arguments, opens data/hash devices read-only, initializes hashing and salt state, parses optional behavior/FEC/signature arguments, verifies the root hash signature if requested, computes hash-tree levels and block positions, creates dm-io, dm-bufio, mempool, and verification workqueue resources, and initializes FEC. `verity_map()` rejects writes and misaligned/out-of-range I/O, installs per-bio state, prefetches hash blocks, submits the read, and lets `verity_end_io()` schedule verification. Verification walks each data block, obtains expected digests through the hash tree, hashes mapped bio data, handles zero-block optimization, and finishes the original bio with success or error.

## State and Persistence Behavior
The target is read-only and does not update the data or hash devices. Persistent trust comes from immutable table parameters: root digest, salt, hash algorithm, block geometry, hash start, and optional FEC/signature inputs. Runtime state includes cached verified hash buffers in dm-bufio auxiliary data, optional `validated_blocks` for `check_at_most_once`, corruption counters, `hash_failed`, and workqueue/mempool state.

## Dependencies and Integration Points
The file integrates with device-mapper target registration, dm-bufio for hash block caching, dm-io for recheck reads, Linux crypto or optimized SHA-256 library paths, workqueues including optional `system_bh_wq`, audit logging, reboot/panic policies, security hooks for LSM integrity metadata, FEC helpers, and signature helpers. It exports query functions used by LoadPin and other kernel code.

## Risks and Test Signals
Critical risks are accepting corrupted data, deadlocking or sleeping in bottom-half verification, incorrect hash-tree level math, signature option parsing errors, and unsafe `check_at_most_once` use after underlying data changes. Tests should cover valid reads, metadata corruption, data corruption with each mode, I/O errors with error modes, FEC recovery and failure, zero-block substitution, root hash signature required/missing/invalid, tasklet fallback on `-EAGAIN`, status table round trips, and LSM preresume metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.c

## Purpose
`dm-verity-verify-sig.c` implements optional dm-verity root-hash signature verification. It parses the `root_hash_sig_key_desc` target option, fetches a PKCS#7 signature blob from a user key, verifies the root hash against trusted keyrings, and owns the dm-verity keyring lifecycle.

## Important APIs, Types, and Functions
Important functions are `verity_verify_is_sig_opt_arg()`, `verity_verify_get_sig_from_key()`, `verity_verify_sig_parse_opt_args()`, `verity_verify_root_hash()`, `verity_verify_sig_opts_cleanup()`, `dm_verity_verify_sig_init()`, and `dm_verity_verify_sig_exit()`. Module parameters include `keyring_unsealed` and `require_signatures`.

## Control Flow
During target option parsing, `verity_verify_sig_parse_opt_args()` rejects duplicate signature descriptors, consumes the key description argument, retrieves the user key payload into `dm_verity_sig_opts`, and records the descriptor on `struct dm_verity`. Later `verity_verify_root_hash()` validates the root hash and signature: missing signatures are accepted unless `require_signatures` is set; supplied signatures are checked against the secondary or platform keyring if configured, then against the `.dm-verity` keyring if it contains keys and is restricted.

## State and Persistence Behavior
The file maintains a module-global `.dm-verity` keyring and module parameters. Per-target signature bytes are temporary in `dm_verity_sig_opts` until the main target copies them into security-facing target state; cleanup frees the temporary buffer. The keyring is allocated at module init, optionally sealed with `keyring_restrict()`, revoked and put at module exit.

## Dependencies and Integration Points
It depends on device-mapper argument parsing, Linux key/user-key APIs, PKCS#7 verification, optional secondary/platform keyrings, module parameters, and `dm-verity.h`. The main target calls init/exit at module registration, parser hooks during optional argument parsing, and root hash verification before accepting the table.

## Risks and Test Signals
Risks include accepting unsigned roots when policy requires signatures, mishandling revoked user keys, leaking signature buffers on parse failure, and unexpected keyring fallback behavior. Tests should cover no signature with and without `require_signatures`, invalid key description, revoked key payload, valid signature in each configured keyring, duplicate option rejection, keyring sealing behavior, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.h

## Purpose
`dm-verity-verify-sig.h` declares the optional root-hash signature verification interface for dm-verity and supplies disabled-build stubs when signature verification support is not configured.

## Important APIs, Types, and Functions
The header defines the feature label, the `root_hash_sig_key_desc` option string, `struct dm_verity_sig_opts`, and `DM_VERITY_ROOT_HASH_VERIFICATION_OPTS`. Enabled builds declare root hash verification, option recognition/parsing, option cleanup, and module init/exit helpers. Disabled builds return neutral or rejecting stubs as appropriate.

## Control Flow
The main target uses `verity_verify_is_sig_opt_arg()` during optional argument parsing, `verity_verify_sig_parse_opt_args()` to consume the descriptor and fetch signature bytes, `verity_verify_root_hash()` after fixed arguments are parsed, and `verity_verify_sig_opts_cleanup()` on both success and error paths. Module init/exit are chained through the dm-verity target module lifecycle.

## State and Persistence Behavior
The header's only data type, `dm_verity_sig_opts`, stores a temporary signature buffer and size. Persistent or security-visible signature state lives in `struct dm_verity` under `CONFIG_SECURITY` in `dm-verity.h` and is populated by the target implementation.

## Dependencies and Integration Points
It integrates compile-time configuration with the main dm-verity target and `dm-verity-verify-sig.c`. The stubs keep the target code simple while ensuring signature options are unrecognized when verification is disabled.

## Risks and Test Signals
Tests should verify feature option count accounting, disabled-build behavior for signature options, cleanup after partial parse failure, and that enabled builds require exactly one argument for `root_hash_sig_key_desc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-verity.h

## Purpose
`dm-verity.h` is the shared internal interface for the dm-verity target, FEC helper, signature helper, and LoadPin integration. It defines the target's configuration/runtime state and per-bio verification state.

## Important APIs, Types, and Functions
Important definitions include `DM_VERITY_MAX_LEVELS`, `enum verity_mode`, `enum verity_block_type`, `struct dm_verity`, `struct pending_block`, and `struct dm_verity_io`. Exported helpers include `verity_hash()`, `verity_hash_for_block()`, `dm_is_verity_target()`, `dm_verity_get_mode()`, and `dm_verity_get_root_digest()`.

## Control Flow
The main target allocates and initializes `struct dm_verity` in its constructor and stores it in `ti->private`. Each mapped bio receives a `struct dm_verity_io` from device-mapper per-bio storage. Verification code fills `pending_block` entries with expected and actual digests, possibly batches two SHA-256 blocks, and uses the flexible hash context field at the end of `dm_verity_io`.

## State and Persistence Behavior
`struct dm_verity` contains immutable table-derived state such as data/hash devices, block sizes, hash levels, root digest, salt, algorithm, and hash tree layout, plus runtime state such as `hash_failed`, corruption counters, `validated_blocks`, workqueue, dm-io client, and recheck mempool. It does not write persistence; it describes how persistent hash metadata is interpreted.

## Dependencies and Integration Points
The header depends on dm-io, dm-bufio, device-mapper, interrupt support, crypto shash, and SHA-2. FEC, signature verification, the main target, and LoadPin trust checks all include it.

## Risks and Test Signals
Risks include per-IO data size miscalculation due to the variable-length hash context, digest-size assumptions exceeding `HASH_MAX_DIGESTSIZE`, and mode semantics consumed by external callers. Tests should validate constructor-calculated `per_io_data_size`, SHA-256 optimized vs generic crypto paths, root digest copy ownership, and target identity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-verity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-writecache.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-writecache.c

## Purpose
`dm-writecache.c` implements the `writecache` device-mapper target, a persistent write-back cache in front of an origin block device. It supports persistent-memory (`p`) mode and SSD (`s`) mode, tracks cached blocks by original sector, commits metadata with sequence counts, services read/write/flush/discard bios, and asynchronously writes cached data back to the origin.

## Important APIs, Types, and Functions
Important persistent structures are `wc_memory_superblock` and `wc_memory_entry`. Runtime structures include `wc_entry`, `dm_writecache`, `writeback_struct`, and `copy_struct`. Major functions include `persistent_memory_claim()`, metadata accessors, `writecache_flush()`, `writecache_resume()`, `writecache_map_read()`, `writecache_map_write()`, `writecache_map_flush()`, `writecache_map_discard()`, `writecache_map()`, `writecache_end_io()`, endio/writeback thread functions, `writecache_writeback()`, `init_memory()`, `writecache_ctr()`, `writecache_dtr()`, and `writecache_status()`.

## Control Flow
The constructor parses mode, origin/cache devices, block size, and optional watermarks, writeback limits, autocommit, max age, cleaner, FUA, metadata-only, and pause settings. It maps or allocates cache metadata, validates or initializes the persistent superblock, allocates entries, workqueues, threads, mempools, and I/O clients. `writecache_map()` handles flush first, translates sectors to target offsets, enforces cache-block alignment, and dispatches to read/write/discard handlers. Writes allocate or reuse entries, copy data into pmem or remap to SSD cache blocks, and schedule metadata commits. Writeback selects committed LRU entries, groups contiguous runs, submits bios or kcopyd copies, and frees entries after endio.

## State and Persistence Behavior
Persistence is driven by `original_sector` and `seq_count` in cache metadata. Entries with sequence counts older than the superblock sequence are committed; uncommitted entries are flushed then the superblock `seq_count` is advanced. SSD mode uses an in-memory metadata map plus dirty bitmap flushed to the SSD cache device; pmem mode uses cache-line flushes and memory barriers. Resume rebuilds the rbtree/free list, discards incomplete entries, resolves duplicate sectors by newest sequence, and may flush repaired metadata.

## Dependencies and Integration Points
The target depends on device-mapper target APIs, dm-io, dm-kcopyd, dm-io-tracker, workqueues, timers, kthreads, biosets, mempools, DAX/libnvdimm for pmem, copy-machine-check helpers, rbtrees, waitqueues, and block queue-limit stacking. It registers as `writecache` with map, end_io, suspend/resume, message, status, iterate_devices, and io_hints hooks.

## Risks and Test Signals
Risks include metadata commit ordering, data loss on power failure, duplicate-sector resolution, pmem hardware poison handling, writeback races with reads/writes/discards, freelist starvation, and constructor option validation. Tests should cover fresh initialization, resume after partial commits, flush/FUA semantics, cleaner mode, metadata-only mode, pmem and SSD write paths, discard invalidation, low-watermark writeback, max-age writeback, writeback error propagation, status output, and all messages (`flush`, `flush_on_suspend`, `cleaner`, `clear_stats`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-writecache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zero.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zero.c

## Purpose
`dm-zero.c` implements the simple `zero` device-mapper target. It behaves like a virtual block device that returns zeroes for reads and silently drops writes and discards.

## Important APIs, Types, and Functions
The implementation consists of `zero_ctr()`, `zero_map()`, `zero_io_hints()`, and the `zero_target` registration. `zero_ctr()` accepts no target arguments and enables discard support. `zero_map()` handles reads, writes, and discards. `zero_io_hints()` advertises broad discard capability.

## Control Flow
Target construction fails if any arguments are supplied. On mapped reads, readahead is killed because populating cache with zero pages is wasteful; non-readahead reads are satisfied by `zero_fill_bio()` and completed immediately. Writes and discards are accepted and completed without forwarding. Unknown operations are killed.

## State and Persistence Behavior
The target has no private state and no persistence. All accepted I/O is completed synchronously without issuing lower-level requests. Writes and discards have no lasting effect.

## Dependencies and Integration Points
The file uses device-mapper target registration, Linux bio helpers, and module metadata. It registers as `zero`, version 1.2.0, with `DM_TARGET_NOWAIT`, constructor, map, and I/O hints hooks.

## Risks and Test Signals
Risk is low, but behavior must remain exact because upper layers may use this target for tests or sparse mappings. Tests should cover argument rejection, read zero-fill, readahead kill, write/drop completion, discard/drop completion, unknown operation kill, and queue-limit discard hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zero.c -->
