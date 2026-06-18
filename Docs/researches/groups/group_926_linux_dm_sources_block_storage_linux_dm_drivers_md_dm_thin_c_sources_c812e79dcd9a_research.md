# Group Research: Linux device-mapper thin provisioning, uevents, unstripe, and verity/FEC sources

This group covers the Linux device-mapper thin-pool and thin targets, path uevent support, the unstriped target, and dm-verity integrity verification including Reed-Solomon FEC and optional root-hash signature verification.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin.c

## Purpose
Implements the device-mapper `thin-pool` and `thin` targets. The pool target owns metadata, data-device allocation, snapshots, commit policy, discard handling, space exhaustion behavior, and lifecycle coordination. The thin target maps read/write bios through pool metadata, provisions blocks on demand, breaks snapshot sharing, and exposes per-thin status and limits.

## Main Interfaces
- Pool target operations: `pool_ctr()`, `pool_dtr()`, `pool_map()`, `pool_preresume()`, `pool_resume()`, `pool_presuspend()`, `pool_postsuspend()`, `pool_message()`, `pool_status()`, `pool_iterate_devices()`, and `pool_io_hints()`.
- Thin target operations: `thin_ctr()`, `thin_dtr()`, `thin_map()`, `thin_endio()`, `thin_preresume()`, `thin_presuspend()`, `thin_postsuspend()`, `thin_status()`, `thin_iterate_devices()`, and `thin_io_hints()`.
- Core IO path: `thin_bio_map()`, `process_bio()`, `process_cell()`, `provision_block()`, `process_shared_bio()`, `break_sharing()`, `process_deferred_bios()`, and `do_worker()`.
- Metadata and allocation path: `commit()`, `alloc_data_block()`, `metadata_operation_failed()`, `abort_transaction()`, `maybe_resize_data_dev()`, and `maybe_resize_metadata_dev()`.
- Pool control messages: `create_thin`, `create_snap`, `delete`, `set_transaction_id`, `reserve_metadata_snap`, and `release_metadata_snap`.

## Control Flow
Thin bios are first normalized by `thin_map()` and sent to `thin_bio_map()`. Flushes and discards are deferred to the pool worker; normal bios try a nonblocking metadata lookup while holding a virtual bio-prison cell to avoid races with discard. If a block is mapped and unshared, the bio is remapped directly to the pool data device. If lookup blocks, the block is unmapped, or the mapping is shared, the cell is queued to the ordered pool workqueue.

The worker drains prepared mapping/discard lists, then processes deferred cells and bios for each active thin. Unmapped writes allocate a data block and either zero it, copy data from an external origin, or complete a full-block overwrite directly with a hooked endio. Shared writes allocate a new data block, quiesce shared reads through a deferred set, copy old data with kcopyd, insert the new mapping, and then release detained bios. Reads from unmapped thin blocks return zeroes or read from an external origin if configured.

Pool metadata commits are batched. Bios that require a commit, such as flush/FUA after metadata changes, are held in `deferred_flush_bios` or `deferred_flush_completions`; `process_deferred_bios()` commits once and then issues or completes the accumulated bios. A periodic delayed worker wakes the pool to limit uncommitted transaction age.

Discard handling is mode- and feature-dependent. Without passdown, mapped ranges are removed after all IO quiesces. With passdown, the code removes mappings, temporarily increments data-block references to prevent reallocation races, issues discard bios to unshared physical ranges, then decrements references after passdown completes.

## State And Synchronization
The global `dm_thin_pool_table` maps pool mapped devices and metadata devices to shared `struct pool` objects under a mutex. Each pool has an ordered workqueue, bio prison, kcopyd client, metadata handle, deferred sets for shared reads and all IO, prepared mapping/discard lists, active thin list, and callback function pointers selected by pool mode.

`struct thin_c` tracks its pool, opened thin metadata device, optional external origin, deferred bios, retry-on-resume bios, deferred prison cells, sorted bio tree, and an RCU-visible active-thin list node. Active thin iteration uses RCU plus a refcount/completion pair so destruction waits for worker iteration to finish.

The pool mode state machine controls write, out-of-data-space, out-of-metadata-space, read-only, and fail behavior. Mode transitions swap IO callbacks, adjust metadata read/write state, cancel or schedule no-space timeouts, and send table events. Metadata failures abort the current transaction, set `needs_check`, and degrade the pool to read-only or fail mode.

## Integration Points
The file depends heavily on `dm-thin-metadata.h` for persistent metadata operations, `dm-bio-prison-v1` for per-block serialization, `dm_deferred_set` for quiescing, and `dm-kcopyd` for zero/copy operations. It registers two DM targets, `thin-pool` and `thin`, with the device-mapper core and uses DM target messages/status/table events for user-space control.

## Notable Behaviors
- Thin snapshots are implemented by metadata tree sharing; data sharing is broken lazily on write using timestamp/shared-state metadata.
- Pool data block size must be between 64 KiB and 1 GiB, and thin device ids are limited to 24 bits.
- `error_if_no_space` controls whether out-of-data-space IO is failed immediately or queued until resume; queued IO can later be forced to `BLK_STS_NOSPC` by the no-space timeout.
- Metadata pre-commit flushes the data device before committing metadata so newly inserted mappings survive crashes.
- Read-only pool modes still service reads and may return zeroes or origin data for unmapped blocks, but writes that need provisioning are failed or queued according to mode.
- `check_at_most_once`-style behavior is not here; thin instead sorts deferred bios/cells by sector to improve locality before processing.

## Risks And Review Focus
- Bio-prison cell ownership is subtle; every path must release, defer, requeue, or error cells exactly once.
- Discard passdown depends on temporary reference increments and shared-status double checks to avoid discarding blocks still referenced by other thins.
- Mode transitions update many function pointers; inconsistent callback state would change IO semantics under error conditions.
- Metadata error handling deliberately aborts transactions and sets `needs_check`; recovery paths should preserve that conservative behavior.
- Suspend/resume ordering matters: pool resume requeues bios and resumes active thins before clearing the pool suspended flag.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-uevent.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-uevent.c

## Purpose
Provides device-mapper uevent support for path-related target events, currently path failure and path reinstatement. It packages DM-specific environment variables and queues events through the mapped device for later emission through the kobject uevent mechanism.

## Main Interfaces
- `dm_path_uevent()` builds and queues a path event for a target.
- `dm_send_uevents()` sends and frees all events on a supplied event list.
- `dm_uevent_init()` and `dm_uevent_exit()` create and destroy the event slab cache.
- Internal helpers include `dm_uevent_alloc()`, `dm_uevent_free()`, and `dm_build_path_uevent()`.

## Control Flow
`dm_path_uevent()` validates the event type, translates it to a kobject action and string name, builds the event with target name, DM action, sequence number, path, and valid-path count, then attaches the event to the mapped device via `dm_uevent_add()`. Later, `dm_send_uevents()` removes each event from the list, copies the current mapped-device name and UUID, appends them to the environment, calls `kobject_uevent_env()`, and frees the event.

## State And Synchronization
Events are allocated from the `_dm_event_cache` kmem cache using `GFP_ATOMIC`, making event creation usable from constrained contexts. Each `struct dm_uevent` stores a mapped-device pointer, kobject action, environment buffer, list node, and local name/UUID buffers.

## Integration Points
Used by DM targets that need to notify user space about path state changes, especially multipath-style target behavior. It relies on core DM helpers including `dm_next_uevent_seq()`, `dm_uevent_add()`, and `dm_copy_name_and_uuid()`, and exports `dm_send_uevents()` and `dm_path_uevent()` to GPL modules.

## Notable Behaviors
- Device name and UUID are copied at send time, not event-build time, so removal races can cause an unsent event to be skipped.
- Event payload includes `DM_TARGET`, `DM_ACTION`, `DM_SEQNUM`, `DM_PATH`, `DM_NR_VALID_PATHS`, `DM_NAME`, and `DM_UUID`.
- Invalid event type is logged and dropped.

## Risks And Review Focus
- Environment construction failure drops the event; new fields must account for limited `kobj_uevent_env` capacity.
- Mapped-device lifetime assumptions are shared with the DM core event queue; callers should only queue events through the supported DM path.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-uevent.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-uevent.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-uevent.h

## Purpose
Declares the device-mapper uevent API and event type enum, with no-op stubs when `CONFIG_DM_UEVENT` is disabled.

## Main Interfaces
- `enum dm_uevent_type` defines `DM_UEVENT_PATH_FAILED` and `DM_UEVENT_PATH_REINSTATED`.
- When enabled, declares `dm_uevent_init()`, `dm_uevent_exit()`, `dm_send_uevents()`, and `dm_path_uevent()`.
- When disabled, supplies inline stubs that either return success or do nothing.

## Control Flow
The header has no runtime control flow beyond compile-time selection. Callers can invoke the API unconditionally and receive either real uevent behavior or stubbed behavior depending on configuration.

## State And Synchronization
No state is defined in the header. The enabled implementation owns allocation and event-list state in `dm-uevent.c`.

## Integration Points
Included by DM core/target code that needs path event notifications. It requires `struct list_head`, `struct kobject`, `struct dm_target`, and related DM types from surrounding includes.

## Notable Behaviors
- Disabled builds still compile callers cleanly and make uevent initialization a successful no-op.
- The public API is intentionally narrow and path-event-specific.

## Risks And Review Focus
- Adding new event types requires keeping the enum aligned with the implementation's event-name table.
- Callers should not infer delivery when `CONFIG_DM_UEVENT` may be disabled.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-uevent.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-unstripe.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-unstripe.c

## Purpose
Implements the `unstriped` device-mapper target. It exposes one logical stripe from an already striped layout by remapping linear logical sectors onto the selected stripe's physical sectors.

## Main Interfaces
- Target lifecycle: `unstripe_ctr()` and `unstripe_dtr()`.
- IO mapping: `unstripe_map()` and `map_to_core()`.
- Reporting and limits: `unstripe_status()`, `unstripe_iterate_devices()`, and `unstripe_io_hints()`.
- Module registration: `dm_unstripe_init()` and `dm_unstripe_exit()`.

## Control Flow
The constructor parses five arguments: stripe count, chunk size, stripe number, backing device path, and physical offset. It validates nonzero stripe/chunk values, opens the backing striped device, records the selected stripe offset and row width, checks that target length is chunk-aligned, and sets maximum IO length to one chunk.

For each bio, `unstripe_map()` switches the bio to the backing device and computes the backing sector. `map_to_core()` calculates the row number by dividing the logical sector by chunk size, skips over the sectors belonging to the other stripes in previous rows, adds the selected stripe's offset inside the row, then adds the physical start.

## State And Synchronization
`struct unstripe_c` stores only immutable mapping parameters and a DM device reference. No locks are needed because target configuration is fixed after construction.

## Integration Points
Registered as the `unstriped` DM target with `DM_TARGET_NOWAIT`. It uses DM device acquisition/release, target max IO length, device iteration callbacks, queue limit hints, and standard DM status output.

## Notable Behaviors
- `chunk_shift` is cached for power-of-two chunk sizes to avoid division in the map path.
- The target emits the original table arguments in `STATUSTYPE_TABLE`; info status is empty and IMA status is an empty string.
- `limits->chunk_sectors` is set to the configured chunk size.

## Risks And Review Focus
- The stripe-number validation permits the edge case `unstripe == stripes` when `stripes <= 1`; callers should be checked if changing this validation.
- `iterate_devices()` reports the target length from the physical start, although the target maps over a sparse set of sectors in the striped device.
- All arithmetic is sector-based; overflow or off-by-one changes would directly corrupt remapping.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-unstripe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.c

## Purpose
Adds optional forward error correction for dm-verity using Reed-Solomon codes. When normal hash verification fails for data or metadata blocks, this code reads interleaved source blocks and parity bytes, reconstructs the corrupted block, and revalidates it against the expected verity digest.

## Main Interfaces
- Feature/lifecycle: `verity_fec_is_enabled()`, `verity_fec_ctr_alloc()`, `verity_fec_ctr()`, and `verity_fec_dtr()`.
- Per-bio lifecycle: `verity_fec_init_io()` and `verity_fec_finish_io()`.
- Recovery path: `verity_fec_decode()`.
- Optional-argument handling: `verity_is_fec_opt_arg()`, `verity_fec_parse_opt_args()`, and `verity_fec_status_table()`.
- Internal decode helpers include `fec_decode_rsb()`, `fec_read_bufs()`, `fec_decode_bufs()`, `fec_read_parity()`, and `fec_decode_rs8()`.

## Control Flow
FEC configuration is parsed from optional verity arguments: parity device, covered block count, parity start block, and number of RS roots. `verity_fec_ctr()` validates compatible data/hash block sizes, computes RS data size and interleaving rounds, checks hash/data/FEC device capacities, creates bufio clients, and preallocates RS state, deinterleave buffers, and output buffers through mempools.

During verification failure, `verity_fec_decode()` maps metadata blocks into the FEC-covered block space when needed, computes the base RS block for the corrupted block, and tries correction without erasure hints first. If that fails, it retries with erasure locations found by hashing readable data blocks. Successful correction copies the reconstructed block either to a destination buffer or back into the original bio vectors, then the corrected data is always hashed again and compared with the expected digest.

`fec_read_bufs()` reads each block contributing to an RS block, including data blocks from the data device and hash/metadata blocks from the hash device. It deinterleaves bytes into preallocated RS buffers and optionally records erasures for blocks that fail reads or fail verity hash checks. `fec_decode_bufs()` reads parity bytes and decodes each RS block, collecting the target byte for the corrected output block.

## State And Synchronization
`struct dm_verity_fec` owns the parity DM device, data and FEC bufio clients, FEC layout values, Reed-Solomon parameters, mempools, and buffer cache. Per-bio `struct dm_verity_fec_io` is appended after the variable-length dm-verity per-bio digest fields and tracks allocated RS state, buffer pointers, erasure indexes, output buffer, output position, and recursion level.

## Integration Points
Called from `dm-verity-target.c` when metadata or data verification fails. It uses `verity_hash()`, `verity_hash_for_block()`, `verity_for_bv_block()`, and `verity_io_*()` layout helpers from `dm-verity.h`, plus Linux `rslib`, `dm-bufio`, and DM optional-argument parsing.

## Notable Behaviors
- RS parameters are based on `RS(255, N)` with `N = 255 - fec_roots`; root count is constrained to the supported overhead range.
- Interleaving spreads bytes across rounds to improve recovery from burst corruption.
- Recovery recursion is capped by `DM_VERITY_FEC_MAX_RECURSION` because FEC may need verity hashes, and hash verification itself may require FEC.
- Extra decode buffers are best-effort; at least the preallocated buffer set is required.
- Corrected metadata is written into the dm-bufio buffer passed by the caller, while corrected data can be copied back into bio vectors.

## Risks And Review Focus
- The layout arithmetic connecting data blocks, hash blocks, metadata, parity start, RS block, and interleaving rounds is correctness-critical.
- Erasure detection hashes other blocks during recovery and must avoid uncontrolled recursion.
- Buffer and mempool cleanup must match partial-constructor failure paths through `verity_fec_dtr()`.
- FEC success is only trustworthy after the final verity digest recheck; changes must preserve that validation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.h

## Purpose
Defines dm-verity FEC constants, option names, configuration state, per-bio state, and enabled/disabled build interfaces.

## Main Interfaces
- FEC constants: RS parameters, buffer counts, recursion limit, and option-name strings.
- `struct dm_verity_fec` stores FEC device, bufio clients, RS layout, mempools, and buffer cache.
- `struct dm_verity_fec_io` stores per-bio Reed-Solomon state, erasures, buffers, output, and recursion depth.
- Enabled declarations cover FEC decode, status, per-IO init/finish, option parsing, constructor allocation, constructor validation, and destruction.
- Disabled stubs return false, `-EOPNOTSUPP`, `-EINVAL`, or no-op success as appropriate.

## Control Flow
There is no runtime control flow in the header. Compile-time `CONFIG_DM_VERITY_FEC` selects either the real API declarations and `DM_VERITY_OPTS_FEC == 8`, or stubs and `DM_VERITY_OPTS_FEC == 0`.

## State And Synchronization
The header defines state layout only. Runtime allocation, ownership, and synchronization are handled in `dm-verity-fec.c` and the parent dm-verity target.

## Integration Points
Included by `dm-verity-target.c` and `dm-verity-fec.c`. It includes `dm-verity.h` for parent types and Linux `rslib` for `struct rs_control`.

## Notable Behaviors
- `DM_VERITY_FEC_BUF_MAX` is derived from `PAGE_SHIFT` and the number of RS blocks per buffer.
- Disabled builds keep dm-verity optional-argument accounting consistent by setting FEC option count to zero.
- FEC option names are part of the dm-verity table ABI: `use_fec_from_device`, `fec_blocks`, `fec_start`, and `fec_roots`.

## Risks And Review Focus
- Per-bio data layout depends on `struct dm_verity_fec_io` being appended after dm-verity's variable-length fields.
- Changing constants affects memory pressure, correction capacity, and table ABI validation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-target.c

## Purpose
Implements the `verity` device-mapper target for transparent read-only block integrity verification. It maps reads to a data device, verifies each data block against a Merkle hash tree stored on a hash device, optionally corrects corruption through FEC, optionally validates the root hash signature, and exposes corruption status.

## Main Interfaces
- Target lifecycle and DM hooks: `verity_ctr()`, `verity_dtr()`, `verity_map()`, `verity_status()`, `verity_prepare_ioctl()`, `verity_iterate_devices()`, and `verity_io_hints()`.
- Hash helpers exported to FEC: `verity_hash()`, `verity_hash_for_block()`, and `verity_for_bv_block()`.
- Verification path: `verity_end_io()`, `verity_work()`, `verity_verify_io()`, `verity_verify_level()`, and `verity_handle_err()`.
- Prefetch path: `verity_submit_prefetch()` and `verity_prefetch_io()`.
- Optional argument handling: `verity_parse_opt_args()`, `verity_parse_verity_mode()`, `verity_alloc_zero_digest()`, and `verity_alloc_most_once()`.

## Control Flow
The constructor parses the fixed dm-verity table fields: version, data device, hash device, data and hash block sizes, number of data blocks, hash start, hash algorithm, root digest, and salt. It validates read-only mode, block-size constraints, device sizes, digest size, and hash-tree level count; initializes the crypto ahash transform, hash bufio client, verification workqueue, per-bio data size, optional FEC, optional zero-block digest, optional at-most-once bitset, and optional root-hash signature verification.

`verity_map()` rejects writes, unaligned IO, and out-of-range IO. Valid reads are remapped to the data device, equipped with a `dm_verity_io` per-bio context, hooked with `verity_end_io()`, optionally prefetched, and submitted. Completion either returns an underlying IO error immediately when FEC is unavailable or the system is shutting down, or queues CPU-intensive verification work.

`verity_verify_io()` walks each data block in the bio. It obtains the expected digest through `verity_hash_for_block()`, which verifies hash-tree metadata from the root down unless a cached bufio hash block is already marked verified. It then hashes the data block and compares the digest. Mismatches try FEC recovery first; if recovery fails, `verity_handle_err()` records corruption, emits a uevent with block information, and applies the configured error mode: return EIO, log only, restart, or panic.

## State And Synchronization
`struct dm_verity` stores opened devices, bufio client, crypto transform, digest/salt state, tree geometry, corruption status, workqueue, per-level hash-block starts, optional FEC state, optional validated-block bitset, and optional signature key description. Hash-block verification state is stored in bufio auxiliary data as `struct buffer_aux::hash_verified`; it is intentionally lockless because duplicate verification races are harmless.

Per-bio state is held in `struct dm_verity_io`, followed in memory by variable-sized ahash request storage, real digest, wanted digest, and possibly FEC per-bio state. Verification work runs on an unbound CPU-intensive workqueue named `kverityd`.

## Integration Points
Uses Linux crypto ahash, dm-bufio, DM target registration, kobject uevents, reboot/panic APIs, FEC helpers from `dm-verity-fec.c`, and root-hash signature helpers from `dm-verity-verify-sig.c`. It registers the `verity` target with version `{1, 8, 0}`.

## Notable Behaviors
- Hash salt placement depends on verity version: version 1 salts before data; version 0 salts during finalization.
- Hash-tree metadata buffers are cached as verified and never reset to unverified.
- `ignore_zero_blocks` replaces expected zero blocks with zero-filled output rather than reading/validating data content.
- `check_at_most_once` records successfully validated data blocks in a bitset and skips later checks for those blocks.
- Prefetching skips root-level blocks and clusters level-0 hash reads according to the `prefetch_cluster` module parameter.
- Status info is `V` or `C`; table status reconstructs all configured options, while IMA status emits a semicolon-terminated measurement string.

## Risks And Review Focus
- Per-bio memory layout must stay aligned with `dm_verity_io`, digest helpers, and appended FEC state.
- `check_at_most_once` trades repeated verification for performance and should be evaluated carefully for mutable or unreliable lower layers.
- Error modes can restart or panic the system; option parsing must prevent conflicting modes.
- Hash-tree offset and level arithmetic must prevent overflow and keep the root-to-leaf chain exact.
- FEC and zero-block handling must not bypass the final digest comparison for nonzero corrected data.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.c

## Purpose
Implements optional dm-verity root-hash signature verification. It retrieves a PKCS#7 signature from a user key, verifies the root hash against trusted kernel keyrings, and supports a module parameter requiring signatures.

## Main Interfaces
- `verity_verify_is_sig_opt_arg()` recognizes the `root_hash_sig_key_desc` option.
- `verity_verify_sig_parse_opt_args()` parses the key description, loads signature bytes from the keyring, and stores the key description on `struct dm_verity`.
- `verity_verify_root_hash()` verifies a root hash and signature with `verify_pkcs7_signature()`.
- `verity_verify_sig_opts_cleanup()` frees temporary parsed signature data.

## Control Flow
Optional argument parsing consumes the key description following `root_hash_sig_key_desc`, requests a user key by that description, reads the user-key payload under the key semaphore, copies the signature into temporary constructor options, and records the key description in the verity target state. After all table arguments are parsed, `verity_verify_root_hash()` validates the root digest bytes against the signature. If no signature is supplied, verification succeeds unless the `require_signatures` module parameter is set.

## State And Synchronization
The file has a read-only module parameter `require_signatures`. Key payload access is protected by `down_read(&key->sem)` and released with `up_read()`. Temporary signature memory is held in `struct dm_verity_sig_opts` until constructor cleanup.

## Integration Points
Used by `dm-verity-target.c` during constructor option parsing and root hash validation. It depends on the Linux key retention service, user key type, and PKCS#7 verification API. Depending on configuration, verification uses the secondary trusted keyring or the default verification keyring argument.

## Notable Behaviors
- The root hash passed to signature verification is the hex-string table argument, not the decoded digest buffer.
- Missing signature returns success by default but `-ENOKEY` when signatures are forced.
- Invalid or revoked keys surface as constructor errors through `ti->error`.

## Risks And Review Focus
- Signature bytes are copied from user-key payloads; payload lifetime and key revocation handling depend on correct key semaphore use.
- `signature_key_desc` allocation happens even after signature retrieval errors unless allocation itself fails; constructor cleanup must free it.
- Callers should understand whether their trust policy requires `require_signatures` or explicit table signature options.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.h

## Purpose
Declares dm-verity root-hash signature verification constants, temporary option storage, and enabled/disabled build interfaces.

## Main Interfaces
- Defines `DM_VERITY_ROOT_HASH_VERIFICATION` and the option name `root_hash_sig_key_desc`.
- Defines `struct dm_verity_sig_opts` with signature size and signature bytes.
- When enabled, declares root-hash verification, signature option recognition/parsing, and option cleanup.
- When disabled, provides no-op or rejecting stubs and sets signature option count to zero.

## Control Flow
The header only selects real declarations or stubs through `CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG`. Disabled builds make root-hash verification always succeed and make signature option parsing unavailable.

## State And Synchronization
No runtime state is owned by this header. Temporary signature memory is described by `struct dm_verity_sig_opts` and owned by constructor parsing code.

## Integration Points
Included by the verity target and signature implementation. The option count feeds into dm-verity's maximum optional argument calculation.

## Notable Behaviors
- Enabled builds reserve two optional table arguments: option name plus key descriptor.
- Disabled builds reject the signature option as unrecognized via the parser path.

## Risks And Review Focus
- Option count must remain consistent with the parser consuming exactly one value after the option name.
- Stub behavior means table compatibility differs across kernel configurations.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity.h

## Purpose
Defines the shared dm-verity data structures, constants, enums, per-bio memory layout helpers, and helper prototypes used by the verity target and FEC implementation.

## Main Interfaces
- Constants and enums: `DM_VERITY_MAX_LEVELS`, `enum verity_mode`, and `enum verity_block_type`.
- Target state: `struct dm_verity`.
- Per-bio state: `struct dm_verity_io`.
- Variable-length per-bio accessors: `verity_io_hash_req()`, `verity_io_real_digest()`, `verity_io_want_digest()`, and `verity_io_digest_end()`.
- Helper prototypes: `verity_for_bv_block()`, `verity_hash()`, and `verity_hash_for_block()`.

## Control Flow
The header has no standalone runtime control flow. Its inline functions calculate addresses of variable-length fields stored immediately after `struct dm_verity_io`: ahash request, real digest, wanted digest, and the end pointer used by FEC to append its own per-bio state.

## State And Synchronization
`struct dm_verity` centralizes opened data/hash devices, dm-bufio state, crypto transform, root digest and salt, optional zero digest, block geometry, tree levels, corruption counters, error mode, verification workqueue, hash-level starts, optional FEC pointer, optional validated-block bitset, and optional signature key description.

`struct dm_verity_io` stores the parent target pointer, original bio endio, starting block, number of blocks, current bio iterator, and verification work item. Synchronization is handled by the implementation workqueue and lower-level APIs.

## Integration Points
Shared by `dm-verity-target.c`, `dm-verity-fec.c`, and signature/FEC headers. It pulls in dm-bufio, device-mapper, and crypto hash types.

## Notable Behaviors
- Per-bio layout is manual and depends on `ti->per_io_data_size` being computed by the constructor.
- `verity_io_digest_end()` is the extension point used by FEC for additional per-bio data.
- `DM_VERITY_MAX_LEVELS` is 63, matching the 64-bit hash-tree level arithmetic in the target.

## Risks And Review Focus
- Any change to `struct dm_verity_io` or the inline layout helpers must be coordinated with per-bio size and alignment calculations.
- `struct dm_verity` fields are read across IO completion/workqueue paths; lifecycle teardown must only occur after DM has stopped IO.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-verity.h -->