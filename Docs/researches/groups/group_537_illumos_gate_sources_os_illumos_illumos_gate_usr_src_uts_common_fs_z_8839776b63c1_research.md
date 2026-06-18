# Group Research: group_537_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_8839776b63c1

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All seven listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio.c

## Purpose

`zio.c` is the central ZFS I/O pipeline implementation. It creates, schedules, transforms, verifies, retries, completes, and destroys `zio_t` operations for logical block reads/writes, physical vdev I/O, frees, claims, trims, cache flushes, dedup paths, gang blocks, encryption, checksums, and error recovery.

## Major Responsibilities

- Initializes and destroys ZIO object/link/buffer kmem caches through `zio_init()` and `zio_fini()`.
- Provides metadata/data buffer allocation helpers:
  - `zio_buf_alloc()`, `zio_buf_free()`
  - `zio_data_buf_alloc()`, `zio_data_buf_free()`
- Maintains transform stacks used for compression, decompression, encryption, decryption, subblock expansion, and embedded/physical buffer conversions.
- Manages parent/child relationships, wait states, child error propagation, and pipeline stalls.
- Constructs public ZIO types:
  - `zio_root()`, `zio_null()`
  - `zio_read()`, `zio_write()`, `zio_rewrite()`
  - `zio_free()`, `zio_free_sync()`
  - `zio_claim()`
  - `zio_ioctl()`, `zio_trim()`
  - `zio_read_phys()`, `zio_write_phys()`
  - `zio_vdev_child_io()`, `zio_vdev_delegated_io()`
- Implements the staged pipeline executor `zio_execute()`, synchronous wait path `zio_wait()`, and async submission path `zio_nowait()`.
- Handles retry, suspend, resume, reexecution, failure-mode escalation, and FMA ereport posting.
- Implements gang block assembly/issue/write/failure rollback.
- Implements dedup table read/write/free coordination.
- Allocates, frees, claims, unallocates, and throttles DVAs.
- Issues I/O into vdev queues and handles completion/assessment.
- Calls encryption, checksum generation, checksum verification, and completion callbacks.
- Provides bookmark ordering helpers used by scan/traversal logic.

## Pipeline Model

`zio_execute()` advances `zio->io_stage` through `zio->io_pipeline` until the operation completes, blocks on children, is dispatched to another taskq, waits for device interrupt, is queued/delegated, or reaches `zio_done()`.

The pipeline table is:

- `zio_read_bp_init`
- `zio_write_bp_init`
- `zio_free_bp_init`
- `zio_issue_async`
- `zio_write_compress`
- `zio_encrypt`
- `zio_checksum_generate`
- `zio_nop_write`
- `zio_ddt_read_start`
- `zio_ddt_read_done`
- `zio_ddt_write`
- `zio_ddt_free`
- `zio_gang_assemble`
- `zio_gang_issue`
- `zio_dva_throttle`
- `zio_dva_allocate`
- `zio_dva_free`
- `zio_dva_claim`
- `zio_ready`
- `zio_vdev_io_start`
- `zio_vdev_io_done`
- `zio_vdev_io_assess`
- `zio_checksum_verify`
- `zio_done`

Pipeline interlocks are explicit: `zio_wait_for_children()` rewinds the stage and stores a stall pointer to a child counter. When the last child reaches the waited state, `zio_notify_parent()` redispatches the parent on the appropriate taskq.

## Transform Handling

`zio_push_transform()` replaces `io_abd` and `io_size` with transformed data while saving the original ABD/size and an optional callback. `zio_pop_transforms()` unwinds in LIFO order, optionally calls the transform callback, frees temporary ABDs, and restores original data.

Important transform callbacks:

- `zio_subblock()` copies read data out of a larger physical block.
- `zio_decompress()` expands compressed data after successful reads.
- `zio_decrypt()` authenticates/decrypts protected reads and logs authentication failures.

This stack lets write stages compress/encrypt before vdev I/O while restoring the caller-facing buffer at completion.

## Read Path

`zio_read()` verifies the block pointer and creates a logical read pipeline. `zio_read_bp_init()` configures transforms and special cases:

- Compressed logical reads push a decompression transform unless `ZIO_FLAG_RAW_COMPRESS` is set.
- Protected logical reads push a decryption/authentication transform unless `ZIO_FLAG_RAW_ENCRYPT` is set.
- Embedded data block pointers are decoded directly and switch to the interlock pipeline.
- Metadata/user-data cache flags are adjusted.
- Dedup blocks switch to the DDT read pipeline.
- Gang blocks add gang stages.

Checksum verification occurs near the vdev side. For vdev child reads with a block pointer, `zio_vdev_child_io()` can move checksum verification down to children, closer to leaf devices.

## Write Path

`zio_write()` validates `zio_prop_t`, creates a logical write, stores callbacks, and disables dedup when required data is unavailable for dedup verification or encrypted dedup.

`zio_write_bp_init()` handles override block pointers, nopwrite state, and DDT eligibility.

`zio_write_compress()` waits for logical/gang children, runs `io_children_ready`, compresses unless disabled by sync convergence policy, handles embedded data blocks, rounds compressed physical size to ashift, checks zero blocks, chooses rewrite vs allocate pipeline, and fills `blkptr_t` fields. It can switch to DDT or nopwrite paths.

`zio_encrypt()` handles protected writes after compression and before checksum generation. It supports raw encrypted writes, authenticated-only block types, indirect MAC checksums, objset MACs, ZIL MAC handling, and full data encryption through SPA crypto helpers.

`zio_checksum_generate()` computes the final checksum or embedded checksum after encryption.

## Free and Claim Paths

`zio_free()` validates the block pointer and either ignores embedded frees, defers frees to a bplist, or immediately waits on `zio_free_sync()`. Deferral depends on gang/dedup status, syncing txg, sync pass, and log spacemap feature state.

`zio_free_sync()` creates free pipeline work and may add async issue when gang or dedup blocks require reads.

`zio_claim()` is used during intent log replay/import to claim already-written blocks before new allocations can collide. Embedded blocks become null ZIOs. Dedup claims are only asserted for non-writable/zdb contexts.

## Parent/Child Accounting

`zio_add_child()` links parent and child with `zio_link_t`, increments per-child-type wait counters for all states the child has not reached, and enforces child-type hierarchy.

`zio_notify_parent()` propagates worst child error unless suppressed, propagates reexecute intent, decrements wait counters, and redispatches stalled parents when counters reach zero.

Errors are inherited by child class in `zio_done()` through `zio_inherit_child_errors()` in a controlled order.

## Gang Blocks

Gang blocks are represented as an in-core `zio_gang_node_t` tree of gang headers. The code uses a two-phase model:

- `zio_gang_assemble()` recursively reads gang headers into `io_gang_tree`.
- `zio_gang_issue()` walks the assembled tree and issues read/rewrite/free/claim children.

This avoids partial free/claim/write operations before all headers are known. If a gang write fails, `zio_dva_unallocate()` walks the gang tree and frees allocations immediately.

`zio_write_gang_block()` allocates a gang header, writes it, splits the data into up to `SPA_GBH_NBLKPTRS` members, and recursively creates gang child writes. Encrypted gang headers reserve DVA space for crypto metadata and cannot use all three copies.

## Dedup

DDT logic is embedded in staged handlers:

- `zio_ddt_read_start()` reads dedup blocks or starts repair reads from alternate DDT phys entries.
- `zio_ddt_read_done()` waits for repair children, copies repaired data if found, and closes the DDT repair state.
- `zio_ddt_collision()` verifies dedup collisions by comparing in-flight lead writes or existing on-disk data.
- `zio_ddt_write()` inserts or references DDT entries, creates lead writes, handles ditto copies, and downgrades to normal writes or stronger checksums on verified collision.
- `zio_ddt_free()` decrements DDT refcounts.

Dedup write children share transformed data through pushed transforms rather than recomputing compression/encryption.

## DVA Allocation and Throttling

`zio_dva_throttle()` chooses an allocation class with `spa_preferred_class()`, hashes the bookmark to an allocator lane, queues async writes in per-allocator AVL trees, and reserves allocation slots through metaslab throttle logic.

`zio_dva_allocate()` performs metaslab allocation, falls back from special allocation class to normal class on `ENOSPC`, and falls back to gang block allocation when large allocations fail.

`zio_dva_free()` and `zio_dva_claim()` call metaslab free/claim helpers.

`zio_alloc_zil()` separately allocates ZIL blocks, preferring log class and falling back to normal class. It fills block pointer fields and pre-generates encryption salt/IV for encrypted ZIL blocks.

## Vdev I/O

`zio_vdev_io_start()` handles top-level mirror dispatch when no concrete vdev is set, alignment expansion for logical I/O, repair bypass for non-dirty DTL regions, vdev cache reads/writes, vdev queueing, accessibility checks, delay timing, and dispatch to `vdev_op_io_start`.

`zio_vdev_io_done()` waits for vdev children, completes vdev queue accounting, updates vdev cache for writes, applies device/label fault injection, converts inaccessible-device errors to `ENXIO`, calls `vdev_op_io_done`, and probes unexpected leaf errors.

`zio_vdev_io_assess()` releases config locks, frees vdev-specific data, applies logical fault injection, retries eligible top-level failures, marks non-leaf vdevs unable to write on `ENXIO`, remembers unsupported write-cache flushes, invokes physical done callbacks, and short-circuits on errors.

## Completion and Error Recovery

`zio_ready()` marks the ready state, calls ready callbacks, updates block pointer copies, releases allocation throttle reservations on early failure, notifies ready-waiting parents, handles nodata gang exceptions, and can invoke ignored-write injection.

`zio_done()` is the main finalizer. It waits for all children, updates allocation throttle accounting, validates block pointer invariants, inherits child errors, finishes checksum reports, pops transforms, updates vdev stats, posts slow I/O and error ereports, decides reexecution/suspend policy, rolls back failed allocations, frees gang trees, calls done callbacks, notifies parents, wakes synchronous waiters, or destroys async ZIOs.

Reexecution is top-down. Failed logical roots can reexecute immediately on a taskq or suspend under `spa_suspend_zio_root` until `zio_resume()` reruns them.

## Bookmark Helpers

`zio_bookmark_compare()` orders live ZIOs by bookmark and pointer address.

`zbookmark_compare()` canonicalizes meta-dnode bookmarks so traversal ordering works across meta-dnode and normal-object references.

`zbookmark_subtree_completed()` checks whether a level-0 last-visited bookmark implies completion of a subtree.

## Key Dependencies

- ABD buffer API for scatter/gather data movement.
- ARC for reads and freed-block notification.
- SPA/vdev/metaslab layers for config, taskqs, allocation, device I/O, and stats.
- DDT for dedup.
- ZIO checksum, compression, and crypt modules.
- FMA/ZFS ereport helpers.
- Fault injection from `zio_inject.c`.

## Notes for Future Readers

- `io_pipeline`, `io_stage`, and child wait counters are tightly coupled. Any new stage must preserve stall/redispatch semantics.
- Transform callbacks may set `io_error` while unwinding in `zio_done()`.
- Encryption, checksum, and compression order is deliberate: write path compresses, encrypts, then checksums ciphertext; read path verifies then decrypts/decompresses through transforms.
- Gang and dedup children intentionally alter normal parent/child propagation rules.
- `ZIO_FLAG_DONT_PROPAGATE`, `ZIO_FLAG_IO_RETRY`, `ZIO_FLAG_CANFAIL`, and `ZIO_FLAG_SPECULATIVE` materially change visible error behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_checksum.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_checksum.c

## Purpose

`zio_checksum.c` implements ZFS checksum selection, checksum generation, checksum verification, checksum context-template management, and special handling for embedded checksums, gang headers, labels, dedup, nopwrite, salted checksums, and encrypted block MAC truncation.

## Major Responsibilities

- Defines `zio_checksum_table[]`, the table of supported checksum algorithms and flags.
- Provides ABD-based Fletcher-2 and Fletcher-4 implementations.
- Maps checksum algorithms to feature flags through `zio_checksum_to_feature()`.
- Resolves inherited/on checksum values through `zio_checksum_select()`.
- Resolves dedup checksum settings through `zio_checksum_dedup_select()`.
- Computes checksums through `zio_checksum_compute()`.
- Verifies checksums through `zio_checksum_error_impl()` and `zio_checksum_error()`.
- Frees per-SPA checksum templates through `zio_checksum_templates_free()`.

## Checksum Table

The table includes:

- `inherit`, `on`, `off`
- `label`
- `gang_header`
- `zilog`
- `fletcher2`
- `fletcher4`
- `sha256`
- `zilog2`
- `noparity`
- `sha512`
- `skein`
- `edonr`

Each entry stores native/byteswap functions, optional template init/free callbacks, flags, and display name.

Important flags include:

- `ZCHECKSUM_FLAG_METADATA`
- `ZCHECKSUM_FLAG_EMBEDDED`
- `ZCHECKSUM_FLAG_DEDUP`
- `ZCHECKSUM_FLAG_SALTED`
- `ZCHECKSUM_FLAG_NOPWRITE`

## ABD Checksum Functions

`abd_checksum_off()` writes a zero checksum.

`abd_fletcher_2_native()` and `abd_fletcher_2_byteswap()` iterate an ABD with Fletcher-2 native or byteswap increment functions.

`abd_fletcher_4_native()` and `abd_fletcher_4_byteswap()` use the active Fletcher-4 ABD ops structure, allowing platform-specific optimized implementations.

## Selection Logic

`zio_checksum_select()` treats child `inherit` as parent and child `on` as `ZIO_CHECKSUM_ON_VALUE`.

`zio_checksum_dedup_select()` is similar but maps `on` to `spa_dedup_checksum(spa)` and preserves `ZIO_CHECKSUM_VERIFY` when requested. It asserts that dedup checksums are either dedup-capable, verification-only, or off.

## Embedded Checksum Handling

For embedded checksum algorithms, the checksum is stored in a `zio_eck_t` embedded in the block data rather than only in the block pointer.

Special verifiers:

- Gang header checksum verifier is based on `<vdev, offset, txg>`.
- Label checksum verifier is based on label offset.
- ZILOG2 uses `zil_chain_t.zc_nused` to determine the effective checksum length.

`zio_checksum_compute()` temporarily writes the verifier into the embedded checksum field, computes the checksum, then writes the actual checksum back into the embedded field.

`zio_checksum_error_impl()` temporarily replaces the embedded expected checksum with the verifier, recomputes, restores the expected checksum, and compares.

## Encryption Interaction

Encrypted blocks store a MAC in the upper half of `blk_cksum`, leaving only a truncated regular checksum. `zio_checksum_handle_crypt()` preserves MAC words and, for weaker non-dedup checksums, XORs high checksum words into low words before truncation to retain more entropy.

Verification mirrors that behavior by zeroing MAC words before comparing actual and expected checksums for protected non-objset blocks.

## Context Templates

Some salted or expensive checksum algorithms can initialize a context template per SPA. `zio_checksum_template_init()` lazily initializes templates under `spa_cksum_tmpls_lock`. `zio_checksum_templates_free()` tears them down during SPA destruction.

## Fault Injection

`zio_checksum_error()` calls `zio_checksum_error_impl()` and then, if fault injection is enabled, can inject `ECKSUM` through `zio_handle_fault_injection()`. The bad checksum report records whether an error was injected.

## Key Dependencies

- `zio_checksum_table` is consumed by `zio.c`.
- Fletcher implementations come from `zfs_fletcher`.
- SHA/Skein/EdonR checksum functions are referenced through the table.
- SPA stores checksum salt and initialized templates.
- ABD iteration provides data traversal without requiring linear buffers.

## Notes for Future Readers

- Embedded checksum algorithms destructively modify the checked buffer during compute/verify, but verification restores the expected checksum field.
- `ZIO_CHECKSUM_MASK` must be used before feature lookup when dedup verify bits may be set.
- Gang-header checksums intentionally differ from data checksums so gang metadata can be verified independently.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_compress.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_compress.c

## Purpose

`zio_compress.c` provides table-driven compression selection, compression execution, decompression execution, and test hooks for simulated decompression failure.

## Major Responsibilities

- Defines `zio_compress_table[]`, mapping compression IDs to names, levels, compressor functions, and decompressor functions.
- Resolves inherited/on compression settings through `zio_compress_select()`.
- Compresses ABD data through `zio_compress_data()`.
- Decompresses linear buffers through `zio_decompress_data_buf()`.
- Decompresses ABD data through `zio_decompress_data()`.

## Compression Table

Supported entries are:

- `inherit`
- `on`
- `uncompressed`
- `lzjb`
- `empty`
- `gzip-1` through `gzip-9`
- `zle`
- `lz4`

`on` maps to LZ4 when `SPA_FEATURE_LZ4_COMPRESS` is active, otherwise to the legacy default.

## Compression Behavior

`zio_compress_data()` first checks whether the entire source ABD is zero. If so, it returns `0`, signaling that no block allocation is needed.

For nonzero data:

- `ZIO_COMPRESS_EMPTY` returns the source length.
- Other compressors are given a target length of 87.5% of the source length.
- Compression functions require linear input, so the source ABD is borrowed into a temporary linear buffer.
- If compressed output does not beat the target length, the original source length is returned, meaning compression is not worthwhile.

## Decompression Behavior

`zio_decompress_data_buf()` validates the compression function and calls the table decompressor.

`zio_decompress_data()` borrows compressed ABD data into a temporary linear buffer, decompresses it, and returns the ABD buffer. Unexpected decompression failure after checksum verification is treated as severe: it saves a copy of the failed compressed buffer and panics. A tunable fault hook can then force an `EINVAL` return after decompression for testing.

## Fault/Test Hooks

- `zio_decompress_fail_fraction` can probabilistically force decompression failure returns.
- `zio_decompress_failed_buf` stores a copy of data that caused an unexpected decompression panic.

## Key Dependencies

- Compressor implementations from `sys/compress.h`.
- ABD borrow/return helpers.
- SPA feature detection for LZ4 default behavior.
- Used heavily by `zio_write_compress()` and read-side `zio_decompress()` in `zio.c`.

## Notes for Future Readers

- Returning `0` from compression means “all-zero block,” not a compressed byte count.
- Compression functions never consume ABDs directly in this implementation.
- Decompression failure is considered evidence of memory corruption or an internal fault because checksum verification should already have passed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_crypt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_crypt.c

## Purpose

`zio_crypt.c` implements ZFS block encryption and authentication mechanics: key initialization, key wrapping/unwrapping, salt/IV generation, MAC generation, block pointer parameter encoding, ZIL/dnode/object-set special handling, indirect MAC checksums, and ABD wrappers around crypto operations.

## Major Responsibilities

- Defines supported encryption suites in `zio_crypt_table[]`.
- Initializes, destroys, wraps, and unwraps `zio_crypt_key_t`.
- Rotates salts after a configured number of uses.
- Generates random IVs and dedup-derived IV/salt values.
- Performs AES-GCM/AES-CCM encryption and decryption through `zio_do_crypt_uio()`.
- Performs SHA512-HMAC operations.
- Encodes and decodes encryption salt/IV/MAC fields in block pointers and ZIL blocks.
- Authenticates indirect block MAC trees.
- Authenticates objset physical blocks with portable and local MACs.
- Builds UIO layouts for normal blocks, ZIL blocks, and dnode blocks.
- Provides ABD-level crypto wrappers.

## On-Disk Crypt Layout

The file documents where encryption metadata lives:

- Salt: 64 bits in `DVA[2].dva_word[0]`.
- IV: first 64 bits in `DVA[2].dva_word[1]`, remaining 32 bits in the upper `blk_fill` IV field.
- MAC: usually stored in the second half of `blk_cksum`.
- ZIL MAC: stored in the embedded checksum inside `zil_chain_t`.
- Objset blocks: store two 256-bit MACs in `objset_phys_t`.
- Indirect blocks: store checksum-of-child-MACs rather than requiring keys to verify the tree shape.

Encrypted blocks reserve DVA space, which affects copy count decisions elsewhere in the ZIO pipeline.

## Supported Crypt Suites

`zio_crypt_table[]` includes:

- inherit/on/off placeholders
- AES-128/192/256 CCM
- AES-128/192/256 GCM

Authentication uses SHA512-HMAC for object authentication and key-related derivations.

## Key Lifecycle

`zio_crypt_key_init()` creates a new key with random GUID, master key material, HMAC key material, and salt. It derives the current encryption key with HKDF-SHA512 and initializes ICP key structures and optional crypto context templates.

`zio_crypt_key_destroy()` destroys locks/templates and zeroes key memory.

`zio_crypt_key_wrap()` encrypts master/HMAC key material with a wrapping key and authenticates AAD containing GUID, crypt suite, and key version for current-format keys.

`zio_crypt_key_unwrap()` decrypts wrapped key material, generates a fresh runtime salt, derives the current key, initializes key structures/templates, and records crypt metadata.

`zio_crypt_key_get_salt()` returns the current salt and increments usage count. If the count reaches `ZFS_CURRENT_MAX_SALT_USES`, `zio_crypt_key_change_salt()` rotates the salt and current derived key.

## IV and Salt Generation

`zio_crypt_generate_iv()` creates a random 96-bit IV.

`zio_crypt_generate_iv_salt_dedup()` derives salt and IV from an HMAC of plaintext. This allows encrypted dedup to produce identical ciphertext for identical plaintext within a clone family, while not exposing a plaintext hash directly.

## Core Crypto

`zio_do_crypt_uio()` is the low-level encryption/decryption function. It configures AES-CCM or AES-GCM parameters, passes AAD, uses the MAC as the final cipher UIO vector, and returns `ECKSUM` on invalid MAC during decrypt.

`zio_do_crypt_data()` builds UIOs, selects the correct derived key for the provided salt, calls `zio_do_crypt_uio()`, cleans temporary buffers, and stores failed decrypt buffers for debugging.

`zio_do_crypt_abd()` adapts ABD data to linear buffers and calls `zio_do_crypt_data()`.

## Block Pointer Encoding

`zio_crypt_encode_params_bp()` and `zio_crypt_decode_params_bp()` store/recover salt and IV from block pointers, accounting for block pointer byte order.

`zio_crypt_encode_mac_bp()` and `zio_crypt_decode_mac_bp()` store/recover MAC bytes from `blk_cksum` words 2 and 3. Objset blocks are special and return zero MAC here because their MACs are inside the objset payload.

`zio_crypt_encode_mac_zil()` and `zio_crypt_decode_mac_zil()` handle MACs in ZIL embedded checksum fields.

## Authentication Helpers

`zio_crypt_bp_zero_nonportable_blkprop()` masks block pointer fields before authentication so raw send/receive portability works. Version 0 compatibility is preserved for read-only import of old-format pools.

`zio_crypt_bp_auth_init()` constructs a portable authentication buffer containing selected `blk_prop` fields and MAC bytes.

`zio_crypt_bp_do_hmac_updates()`, `zio_crypt_bp_do_indrect_checksum_updates()`, and `zio_crypt_bp_do_aad_updates()` feed that portable block pointer representation into HMAC/SHA/AAD contexts.

## Objset Authentication

`zio_crypt_do_objset_hmacs()` computes two MACs:

- Portable MAC: protects `os_type`, portable `os_flags`, and metadnode fields. This is suitable for raw sends.
- Local MAC: protects non-portable accounting-related state when user/group/project accounting objects are present.

Objset MAC calculations always normalize values to little-endian representation rather than simply using on-disk byte order.

## Indirect MAC Checksums

`zio_crypt_do_indirect_mac_checksum_impl()` computes a SHA512 digest over portable fields and child MACs for all block pointers in an indirect block.

`zio_crypt_do_indirect_mac_checksum()` verifies current format first and falls back to version 0 on checksum mismatch. This allows verification without loading the encryption key.

`zio_crypt_do_indirect_mac_checksum_abd()` adapts ABD buffers.

## ZIL Special Handling

`zio_crypt_init_uios_zil()` encrypts sensitive log-record payloads but leaves `zil_chain_t`, common log record headers, and embedded block pointers in plaintext. Plaintext portions are authenticated as AAD. It parses records up to `zc_nused`, handles byteswapped headers, and creates UIO vectors only for encrypted spans.

## Dnode Special Handling

`zio_crypt_init_uios_dnode()` leaves dnode core fields and block pointers plaintext for scrub/claim visibility while encrypting eligible bonus buffers. It authenticates portable dnode fields, block pointer MAC/properties, spill block pointers, and unencrypted bonus buffers as AAD.

`zio_crypt_copy_dnode_bonus()` copies encrypted bonus-buffer data from an ABD into a destination buffer at matching dnode offsets.

## Normal Block Handling

`zio_crypt_init_uios_normal()` creates a simple plaintext vector and ciphertext vector plus MAC vector. It is used for most encrypted object types.

`zio_crypt_init_uios()` dispatches to ZIL, dnode, or normal UIO construction, then appends the MAC vector to the cipher UIO.

## Fault/Test Hooks

- `zfs_key_max_salt_uses` controls salt rotation threshold.
- `zio_decrypt_fail_fraction` can probabilistically force decrypt MAC failures.
- `failed_decrypt_buf` and `failed_decrypt_size` retain failed ciphertext for debugging.

## Key Dependencies

- ICP crypto framework.
- HKDF-SHA512.
- SHA2 and SHA512-HMAC.
- ZFS object type definitions, dnode layout, ZIL layout, block pointer macros, ABD API.
- Called by `zio_encrypt()`/`zio_decrypt()` in `zio.c` and SPA crypto wrappers.

## Notes for Future Readers

- Raw sends drive much of the “portable fields only” authentication design.
- ZIL and dnode blocks are not fully opaque ciphertext; they preserve selected structural metadata in plaintext but authenticate it.
- Indirect block MAC checksums are keyless-verifiable by design.
- Salt rotation reduces IV collision risk for random-IV modes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_inject.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_inject.c

## Purpose

`zio_inject.c` implements ZFS fault injection support used by `zinject` and test code. It registers fault handlers, matches them against logical or device I/O, injects errors/delays/panics/ignored writes, translates byte ranges to block ranges, lists/clears handlers, and initializes/finalizes global injection state.

## Major Responsibilities

- Maintains a global list of `inject_handler_t` records.
- Tracks whether injection is enabled with `zio_injection_enabled`.
- Supports data, device, label, decrypt, delay, panic, and ignored-write injection commands.
- Matches logical block bookmarks, object types, DVA masks, vdev GUIDs, I/O types, and error classes.
- Converts user byte ranges into block IDs through dnode metadata.
- Keeps an injection reference on the target SPA while a handler exists.
- Provides listing and clearing APIs for registered handlers.
- Flushes ARC when requested so reads reach the ZIO layer.

## Data Structures

`inject_handler_t` stores:

- Unique handler ID.
- Held `spa_t`.
- `zinject_record_t` rule.
- Optional delay lanes array.
- Next delay lane index.
- List node.

Global state:

- `inject_handlers`: all active handlers.
- `inject_lock`: protects handler list and delay handler count.
- `inject_delay_count`: count of active delay handlers.
- `inject_delay_mtx`: serializes delay lane assignment.
- `inject_next_id`: monotonic handler ID source.

## Matching

`freq_triggered()` implements probabilistic injection. Frequency `0` means always. Legacy 0-100 percentages and scaled `ZI_PERCENTAGE_MAX` values are both supported.

`zio_match_handler()` matches either MOS metadata by object type or exact bookmark ranges by objset, object, level, block ID range, DVA mask, and error.

`zio_match_dva()` identifies which DVA a vdev child I/O corresponds to by matching top vdev and offset, compensating for leaf label offset.

## Injection Paths

`zio_handle_panic_injection()` panics when a matching SPA, function tag, and type are found.

`zio_handle_decrypt_injection()` injects decrypt/authentication failures for matching bookmarks and object types.

`zio_handle_fault_injection()` injects logical data faults, currently only for reads with logical data.

`zio_handle_label_injection()` injects faults into vdev label regions, translating relative label offsets into physical label offsets.

`zio_handle_device_injection()` injects device-level faults by vdev GUID. It can skip label regions, respect failfast semantics, filter by I/O type, set `VDEV_AUX_OPEN_FAILED` for `ENXIO`, and mark retried I/O for statistics/FMA behavior.

`zio_handle_ignored_writes()` simulates hardware ignoring writes by removing vdev I/O stages from some syncing txg writes for a configured duration.

`spa_handle_ignored_writes()` validates ignored-write injection duration during spa sync.

`zio_handle_io_delay()` computes a target completion time for delayed I/O using per-handler lanes, frequency, vdev GUID, and configured latency.

## Delay Injection

Delay handlers have a fixed latency and lane count. Each lane records when it becomes idle. `zio_handle_io_delay()` chooses the handler/lane that can complete soonest, updates that lane atomically under `inject_delay_mtx`, and returns the target timestamp. `zio_delay_interrupt()` in `zio.c` uses this timestamp to delay completion.

The code rejects zero delay, zero lanes, and very large lane counts at registration.

## Registration and Clearing

`zio_inject_fault()` optionally unloads the SPA, optionally translates byte ranges, obtains an injection SPA reference, allocates a handler, allocates delay lanes if needed, inserts the handler under writer lock, increments enabled counters, and optionally flushes ARC.

`zio_inject_list_next()` returns the first handler with ID greater than the supplied ID and copies the pool name and record.

`zio_clear_fault()` removes a handler by ID, updates delay counts, frees delay lanes, releases the SPA injection reference, frees the handler, and decrements `zio_injection_enabled`.

`zio_inject_init()` initializes locks and the handler list. `zio_inject_fini()` destroys them.

## Key Dependencies

- `zio.c` calls injection hooks from checksum verification, vdev completion, vdev assessment, decryption, and ready stages.
- SPA namespace/injection references prevent disappearing pools while handlers exist.
- ARC flush is used to force subsequent reads through the ZIO layer.
- Dnode/dataset APIs translate byte ranges to block ranges.

## Notes for Future Readers

- The handler list is intentionally simple because few active faults are expected.
- Delay lane assignment requires both reader lock on the handler list and a mutex for per-lane atomicity.
- Device injection treats `ENXIO` specially and may convert it to `EIO` for active I/O.
- Logical data injection only applies to reads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_inject.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zle.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zle.c

## Purpose

`zle.c` implements ZFS zero-length encoding, a simple compression algorithm optimized for runs of zero bytes.

## Compression Format

Each compressed chunk begins with a length byte `b`.

- If `b < n`, the next `b + 1` bytes are literal data.
- If `b >= n`, the chunk represents `256 - b + 1` zero bytes.

The compression parameter `n` comes from the compression table. In `zio_compress.c`, ZLE uses level `64`.

## Functions

`zle_compress()` scans the source and emits either zero-run descriptors or literal-run descriptors.

For zero runs:

- It can encode up to `256 - n` zero bytes in one chunk.
- It emits only the length/control byte.

For literal runs:

- It can encode up to `n` literal bytes.
- It stops before a pair where both current and next byte are zero, allowing the next iteration to encode a zero run.
- It checks destination capacity before emitting a literal run.

If compression cannot consume all source bytes within the destination limit, it returns the original source length, signaling ineffective compression.

`zle_decompress()` reads chunk descriptors, copies literal bytes or emits zero bytes, and succeeds only if it exactly fills the destination buffer.

## Key Dependencies

- Used through `zio_compress_table[]` as the `zle` compressor/decompressor.
- Only depends on basic illumos types/macros.

## Notes for Future Readers

- This is not a general-purpose entropy compressor; it targets sparse/zero-heavy data.
- The compressor’s failure convention matches the ZIO compression layer: returning `s_len` means “store uncompressed.”
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zrlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zrlock.c

## Purpose

`zrlock.c` implements the Zero Reference Lock, a synchronization primitive that acts like a reference count with a non-blocking writer lock available only when the reference count is zero.

## Concept

A ZRL permits multiple concurrent references through `zrl_add()`/`zrl_remove()`. A writer-like user can acquire the lock only with `zrl_tryenter()`, and only when the count is zero. There is no blocking writer enter path, so writer priority and writer-waiter state are intentionally absent.

Special refcount values:

- `ZRL_LOCKED == -1`
- `ZRL_DESTROYED == -2`

`ZRL_LOCKED` is treated as zero references for refcount query purposes.

## Functions

`zrl_init()` initializes the mutex, condition variable, refcount, and debug owner fields.

`zrl_destroy()` asserts zero references, destroys synchronization primitives, and marks the lock destroyed.

`zrl_add_impl()` repeatedly attempts to atomically increment the refcount while it is not locked. If locked, it waits on the condition variable until unlocked. Reader acquisition is reentrant because ownership is not exclusive for readers.

`zrl_remove()` atomically decrements the refcount and asserts it remains nonnegative.

`zrl_tryenter()` atomically changes refcount from `0` to `ZRL_LOCKED`. It returns `1` on success and `0` otherwise.

`zrl_exit()` releases the locked state by setting refcount to `0` under the mutex and broadcasting to waiters.

`zrl_refcount()` returns positive references or zero for locked/zero states.

`zrl_is_zero()` returns true for zero or locked states.

`zrl_is_locked()` returns true only for `ZRL_LOCKED`.

Under `ZFS_DEBUG`, `zrl_owner()` returns the debug owner thread, and add/enter/exit maintain owner/caller tracking.

## Synchronization Design

Fast-path reference acquisition uses `atomic_cas_32()` without taking the mutex. Only the locked state causes waiters to take `zr_mtx` and sleep on `zr_cv`.

Unlock uses the mutex and broadcasts after storing zero, ensuring blocked adders wake and retry.

## Key Dependencies

- Uses illumos mutexes, condition variables, atomics, DTrace debug probe, and thread identity.
- The public wrapper macro/function for `zrl_add()` likely passes caller information into `zrl_add_impl()`.

## Notes for Future Readers

- ZRL is suitable when code needs to prevent new references only at moments where existing references are already zero.
- There is no writer wait path; callers that need blocking writer acquisition should use a different primitive.
- Reader reentry is allowed and explicitly useful for reference-state checks across call chains.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zrlock.c -->