# Group Research: group_1638_qemu_sources_virtualization_qemu_block_cloop_c_sources_virtualizati_3befcb40d5cd

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/qemu`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/cloop.c -->
# File Research: sources/virtualization/qemu/block/cloop.c

Implements QEMU's read-only CLOOP image format driver. It probes for the CLOOP shell-script magic, opens a file child, parses the 128-byte header area, reads big-endian block size and block count, validates block size, validates and loads the compressed-block offset table, allocates compressed/uncompressed buffers, and initializes a zlib stream.

Runtime reads are sector-aligned only. `cloop_co_preadv()` serializes access with a coroutine mutex, maps each requested sector to a compressed block, calls `cloop_read_block()` to lazily decompress the current block if needed, and copies 512-byte sectors into the caller qiov. Only one decompressed block is cached (`current_block`).

Important safety checks include: block size must be nonzero, 512-byte aligned, and <= 64 MiB; `n_blocks` and offset table sizing are bounded; offsets must be monotonic; compressed block size is capped at twice `MAX_BLOCK_SIZE`. The driver registers as format `cloop`, exposes `.bdrv_co_preadv`, default child permissions, 512-byte request alignment, and no write path.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/cloop.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/commit.c -->
# File Research: sources/virtualization/qemu/block/commit.c

Implements block commit, both the modern live block job path (`commit_start()`) and the older synchronous `bdrv_commit()` helper. The live job copies allocated data from an overlay chain into a base image, then drops intermediate nodes from the backing chain.

`CommitBlockJob` tracks the temporary `commit_top` filter, top/base `BlockBackend`s, base node, base overlay, on-error policy, backing-file replacement string, and whether the backing chain is frozen. `commit_iteration()` queries allocation status above the base, writes zero extents with `blk_co_pwrite_zeroes()`, copies allocated data via an aligned 512 KiB buffer, rate-limits progress, and maps I/O errors through block job error policy. `commit_run()` sizes/truncates the base if needed, allocates the buffer, loops through the image, sleeps for rate limiting, and stops on cancellation.

`commit_start()` validates distinct top/base, adjusts base writability, inserts a `commit_top` filter above top, freezes the chain down to base, adds blocker permissions for intermediate nodes, creates top/base block backends, and starts the job. `commit_prepare()` unfreezes the chain and calls `bdrv_drop_intermediate()`. `commit_abort()` removes blockers, replaces the commit filter with its backing node, and notes the consistency risk if partial writes already reached the base.

The `commit_top` filter is a dummy consistent-read provider that forwards reads to backing while allowing writes in the backing chain. The synchronous `bdrv_commit()` drains all nodes, temporarily inserts `commit_top` above the backing file, copies allocated regions, attempts to empty the source, flushes both sides, and restores read-only/backing state on cleanup.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/commit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/copy-before-write.c -->
# File Research: sources/virtualization/qemu/block/copy-before-write.c

Implements the `copy-before-write` block filter used by backup/fleecing flows. It sits above a source node and copies old data into a target before guest writes, discards, or write-zeroes modify the source.

`BDRVCopyBeforeWriteState` owns a `BlockCopyState`, target child, CBW error policy, timeout, discard-source flag, a coroutine mutex, an access bitmap for snapshot reads, a done bitmap for already copied areas, a request list for frozen snapshot reads, and `snapshot_error`. `cbw_do_copy_before_write()` aligns writes to the block-copy cluster size, starts `block_copy()`, handles timeout/error policy, marks copied clusters in `done_bitmap`, and waits for overlapping frozen snapshot read requests before allowing the guest write to proceed.

Normal reads pass through to `bs->file`; writes/discards/zeroes first call copy-before-write and then forward to the source. Snapshot reads use `cbw_snapshot_read_lock()` to verify requested areas are in `access_bitmap`, choose either `target` for already copied ranges or `bs->file` for protected source ranges, and block overlapping guest writes via `frozen_read_reqs`. Snapshot discard clears access bits, resets block-copy state, and discards from target.

`cbw_open()` parses QAPI-style options, opens `file` and `target`, optionally looks up a bitmap, creates `BlockCopyState`, creates disabled done/access bitmaps, initializes access from block-copy's dirty bitmap, and sets supported write/zero flags. `cbw_child_perm()` gives target write permission while controlling resize and source write/consistent-read permissions. `bdrv_cbw_append()` constructs options and inserts the filter; `bdrv_cbw_drop()` removes it. The driver registers as filter `copy-before-write`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/copy-before-write.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/copy-before-write.h -->
# File Research: sources/virtualization/qemu/block/copy-before-write.h

Declares the global-state API for the copy-before-write filter. It includes block internals and block-copy definitions, then exposes `bdrv_cbw_append()` and `bdrv_cbw_drop()`.

`bdrv_cbw_append()` takes source and target nodes, optional filter node name, discard-source behavior, minimum cluster size, an output `BlockCopyState **`, CBW error policy, and error target. `bdrv_cbw_drop()` removes a CBW filter and unreferences it. The header is intentionally small and only exports lifecycle operations.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/copy-before-write.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/copy-on-read.c -->
# File Research: sources/virtualization/qemu/block/copy-on-read.c

Implements the `copy-on-read` filter. It forwards most operations to its file child, but reads may set `BDRV_REQ_COPY_ON_READ` so data read from backing layers is materialized into the top node.

`cor_open()` opens the file child, sets supported flags, and optionally accepts a `bottom` node name. If `bottom` is provided, it validates that the node exists, is open, is not a filter, freezes the backing chain from this filter down to bottom, and holds a reference. Reads without a bottom simply forward with `BDRV_REQ_COPY_ON_READ`. Reads with a bottom iterate through allocation status, decide where copy-on-read is needed for ranges below the active layer, skip pure prefetch ranges that do not need read/write work, and forward partial requests.

Writes, zeroes, discards, compressed writes, eject, lock-medium, and getlength are pass-through operations. `cor_child_perm()` passes through consistent-read/write/resize permissions and requests `BLK_PERM_WRITE_UNCHANGED` unless inactive. `cor_close()` and `bdrv_cor_filter_drop()` unfreeze the backing chain and unref/drop the filter. The driver registers as filter `copy-on-read`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/copy-on-read.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/copy-on-read.h -->
# File Research: sources/virtualization/qemu/block/copy-on-read.h

Declares the global-state helper `bdrv_cor_filter_drop()`, which removes and unreferences a copy-on-read filter. The header includes `block/block_int.h` and documents the filter as performing copy-on-read operations.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/copy-on-read.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/coroutines.h -->
# File Research: sources/virtualization/qemu/block/coroutines.h

Internal block-layer coroutine declarations. It groups thread-safe I/O API functions and mixed I/O/global-state wrappers used by generated block code and block drivers.

Declared coroutine/read-lock functions include `bdrv_co_check()`, `bdrv_co_invalidate_cache()`, `bdrv_co_common_block_status_above()`, VMState read/write helpers, and NBD connection establishment. Mixed wrapper declarations expose `bdrv_common_block_status_above()` and `nbd_do_establish_connection()` with generated coroutine wrapper annotations.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/coroutines.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/create.c -->
# File Research: sources/virtualization/qemu/block/create.c

Implements the QMP `blockdev-create` command as a QEMU job. `BlockdevCreateJob` stores the target `BlockDriver` and cloned `BlockdevCreateOptions`.

`qmp_blockdev_create()` resolves the driver from the QAPI enum, enforces whitelist policy, checks that `.bdrv_co_create` exists, creates a manual-dismiss `JOB_TYPE_CREATE` job in the main AioContext, clones the options, and starts it. `blockdev_create_run()` sets one unit of progress, calls the driver's `bdrv_co_create()`, marks progress complete, frees the cloned options, and returns the driver result.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/create.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/crypto.c -->
# File Research: sources/virtualization/qemu/block/crypto.c

Implements QEMU's LUKS block format driver on top of `QCryptoBlock`. `BlockCrypto` stores the crypto object, an `updating_keys` permission state, and optional detached header child.

The driver provides crypto header read/write callbacks that work both in coroutine and non-coroutine contexts and choose the detached header child when present. Creation helpers support normal and detached-header LUKS creation, payload formatting, preallocation/truncate handling, legacy create-opts parsing, and `blockdev-create` QAPI options. Option conversion functions parse open/create/amend QDicts through QAPI visitors.

Open flow creates `file` and optional `header` children, parses runtime options, sets detached/no-I/O crypto flags, opens the `QCryptoBlock`, and marks the BDS encrypted. I/O paths use a 1 MiB aligned bounce buffer so guest qiovs never expose ciphertext: reads fetch ciphertext at payload offset and decrypt into caller qiov; writes copy caller data to the bounce buffer, encrypt, and write ciphertext. Request alignment is set to the crypto sector size, length subtracts payload offset, and truncate adds payload offset with overflow checks.

The LUKS-specific sections implement probing, measuring required/fully allocated size, image-specific info reporting, keyslot amend options, permission tightening during key updates, and child permission compatibility behavior. The registered format driver is `luks`, with create, create-opts, truncate, measure, get-info, amend, reopen, read/write, and strong runtime option support.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/crypto.h -->
# File Research: sources/virtualization/qemu/block/crypto.h

Defines crypto block option names and `QemuOptDesc` helper macros for QCOW and LUKS encryption options. LUKS options include key secret, cipher algorithm/mode, IV generator and hash, hash algorithm, PBKDF iteration time, detached-header flag, keyslot, state, old secret, and new secret.

The header also declares the three QDict-to-QAPI parser helpers: `block_crypto_create_opts_init()`, `block_crypto_amend_opts_init()`, and `block_crypto_open_opts_init()`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/curl.c -->
# File Research: sources/virtualization/qemu/block/curl.c

Implements read-only HTTP, HTTPS, FTP, and FTPS protocol block drivers using libcurl multi/socket integration. It supports URL, readahead, SSL verification, timeout, cookies or cookie secret, username/password secret, proxy credentials, and force-range options.

`BDRVCURLState` owns the libcurl multi handle, timer, known length, up to eight `CURLState` transfer slots, socket table, URL/options, AioContext, mutex, free-state queue, and credentials. Each `CURLState` has an easy handle, cached read buffer, range string, error buffer, in-use flag, and waiting request slots. The code restricts allowed protocols to HTTP/HTTPS/FTP/FTPS, with separate handling for libcurl 7.85 string protocol APIs.

Open enforces read-only, initializes libcurl globally, parses options, validates readahead alignment and timeout, resolves secrets, verifies URL scheme matches the driver, initializes a curl state, performs a HEAD or forced `0-0` GET to determine size and byte-range support, rejects unknown size or HTTP(S) without range support, then attaches the multi handle to the BDS AioContext. Read requests first search cached/readahead buffers, can wait on overlapping active transfers, otherwise allocate a transfer state, allocate a readahead buffer, set a byte range, add the easy handle to the multi handle, kick curl, and yield until completion.

Completion handlers copy data into waiting qiovs, zero-fill beyond EOF, wake coroutines, and clean the transfer state. Aio attach/detach configures socket handlers and timers, cleans easy handles and buffers, and handles context migration. Four `BlockDriver`s register the same implementation under `http`, `https`, `ftp`, and `ftps`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/curl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/dirty-bitmap.c -->
# File Research: sources/virtualization/qemu/block/dirty-bitmap.c

Implements block dirty bitmap management around `HBitmap`. `BdrvDirtyBitmap` tracks owner BDS, bitmap storage, busy state, successor bitmap, optional name, size, disabled/readonly/persistent/inconsistent/skip-store flags, active iterators, and list linkage.

The file provides lock wrappers for `bs->dirty_bitmap_mutex`, named lookup, bitmap creation with granularity/name validation and device length sizing, lifecycle release, named bitmap release, truncate across all bitmaps, persistent bitmap driver hooks, and persistence capability checks. Successor support lets operations create an anonymous child bitmap, disable and mark the parent busy, later abdicate the name/persistence to the successor or reclaim by merging child bits back into the parent.

State APIs include enable/disable, busy, readonly, persistence, inconsistent, skip-store, query info for QMP, first/next iteration, SHA256, dirty count, granularity, and default granularity selection from cluster size clamped to 4K..64K. Iterator APIs wrap `HBitmapIter`. Dirty mutation APIs set/reset/clear/restore bits, merge bitmaps with public validation or internal unchecked paths, mark all enabled bitmaps dirty on writes, and serialize/deserialize bitmap chunks for persistence/migration.

The important invariants are: readonly bitmaps reject mutation; inconsistent persistent bitmaps are disabled and mostly unusable; active iterators prevent release; successor/busy state protects transactional replacement; cross-BDS merges lock both bitmap owners.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/dirty-bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/dmg-bz2.c -->
# File Research: sources/virtualization/qemu/block/dmg-bz2.c

Optional DMG bzip2 decompression module. It defines `dmg_uncompress_bz2_do()`, initializes a `bz_stream`, decompresses one complete chunk, checks for `BZ_STREAM_END` and exact output length, then tears down the bzip2 stream.

A constructor registers the function by assigning the global `dmg_uncompress_bz2` pointer declared in `dmg.h`. The main DMG driver can operate without this module loaded, but bzip2-compressed chunks will fail when accessed.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/dmg-bz2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/dmg-lzfse.c -->
# File Research: sources/virtualization/qemu/block/dmg-lzfse.c

Optional DMG LZFSE decompression module. It includes the LZFSE header with a diagnostic workaround for strict-prototypes warnings, then defines `dmg_uncompress_lzfse_do()` using `lzfse_decode_buffer()`.

Unlike the bzip2 helper, it returns the decoded output size on success and `-1` on failure. A constructor registers the helper through the global `dmg_uncompress_lzfse` function pointer. The main DMG driver detects whether this optional module is available before treating ULFO chunks as readable.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/dmg-lzfse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/dmg.c -->
# File Research: sources/virtualization/qemu/block/dmg.c

Implements QEMU's read-only Apple DMG/UDIF image format driver. It supports zero, raw, ignored, zlib, optional bzip2, and optional LZFSE chunk types. It probes weakly by `.dmg` filename suffix.

Open flow applies auto read-only, opens the file child, loads optional `dmg-bz2` and `dmg-lzfse` modules, locates the `koly` trailer near EOF, validates data/resource/plist offsets against the trailer location, reads total sectors, then parses either the resource fork or XML property list to build chunk tables. MISH block parsing recognizes chunk entries, ignores comments/end markers, warns for unsupported types, validates sector counts and compressed lengths with 64 MiB caps, and records per-chunk type, file offset, compressed length, guest sector start, and sector count. It also tracks maximum compressed and uncompressed chunk sizes for buffer allocation.

Runtime reads are 512-byte aligned and serialized by a coroutine mutex. `dmg_read_chunk()` binary-searches the chunk containing a sector, lazily decompresses or reads the whole chunk into a single cached buffer, and handles zero/ignore chunks specially without large zero buffers. Zlib chunks use the file's persistent zstream; bzip2/LZFSE chunks call optional function pointers; raw chunks read directly. `dmg_co_preadv()` copies requested sectors from the current chunk buffer or zero-fills them.

Close frees all chunk arrays, aligned buffers, and the zlib stream. The driver registers as format `dmg`, with default child permissions, 512-byte request alignment, and read-only semantics.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/dmg.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/dmg.h -->
# File Research: sources/virtualization/qemu/block/dmg.h

Shared DMG driver header. `BDRVDMGState` contains the coroutine lock, chunk table arrays (`types`, `offsets`, `lengths`, `sectors`, `sectorcounts`), current cached chunk index, compressed/uncompressed buffers, and zlib stream.

It defines `BdrvDmgUncompressFunc` and declares the optional global function pointers `dmg_uncompress_bz2` and `dmg_uncompress_lzfse`, which are installed by the optional decompressor modules.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/dmg.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/export.c -->
# File Research: sources/virtualization/qemu/block/export/export.c

Common block export registry and QMP plumbing. It collects available export drivers (`nbd`, optional vhost-user-blk, optional FUSE, optional VDUSE) and maintains a main-thread-only global list of active `BlockExport`s.

`blk_exp_add()` validates export ID uniqueness and syntax, resolves the driver and node, rejects writable exports of read-only nodes, optionally moves the node to a single requested iothread or collects multiple iothread contexts, activates the node unless inactive exports are explicitly allowed and supported, creates a `BlockBackend` with consistent-read and optional write permission, configures write cache/writethrough behavior, allocates the driver-specific export object, calls the driver's create method, and inserts the export into the global list.

Reference counting is atomic; final deletion is scheduled as a bottom half in the main AioContext, where the export is removed from the list, driver delete is called, block backend dev ops are cleared, the backend is unrefed, and a `BLOCK_EXPORT_DELETED` event is emitted. Shutdown drops user ownership, calls driver request-shutdown, and unreferences. QMP handlers add/delete/query exports, with safe deletion rejecting exports still in use unless hard mode is requested. `blk_exp_close_all_type()` requests shutdown for matching exports and waits until none remain.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/export.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/fuse.c -->
# File Research: sources/virtualization/qemu/block/export/fuse.c

Implements the FUSE block export driver, presenting a block node as a single raw regular file mounted at a chosen path. It uses FUSE protocol 7.x low-level device handling directly, while libfuse is used for session setup/mount/unmount.

`FuseExport` extends `BlockExport` with a FUSE session, in-flight counter, mount/handler/halted state, one or more `FuseQueue`s, mountpoint, writable/growable/allow-other flags, and atomic stat metadata. Each queue has an AioContext, FUSE FD, and cached aligned write-data buffer. Multi-iothread export creates one queue per supplied AioContext and clones `/dev/fuse` FDs with `FUSE_DEV_IOC_CLONE`; otherwise a single queue follows the block backend's AioContext.

Creation checks mountpoint uniqueness, verifies the mountpoint is a regular file, sets permissions and ownership defaults, optionally tries `allow_other` automatically, mounts with `rw/ro,nosuid,nodev,noatime,max_read,default_permissions`, makes the FUSE FD nonblocking, clones extra queue FDs, installs fd handlers, and configures block dev ops for draining. Draining detaches handlers, waits for atomic in-flight requests, refreshes AioContext on end, and reattaches handlers unless halted.

Request intake uses `readv()` so FUSE WRITE payloads land directly in an aligned data buffer. It validates header size, request length, supported opcode header lengths, old/new `fuse_init_in` layout differences, truncated requests, and writes immediate `-ENOSYS`/`-EINVAL` errors where needed. Requests run in coroutines with a graph read lock.

Supported operations include INIT, STATFS, OPEN, GETATTR, SETATTR, READ, WRITE, FALLOCATE, FSYNC, FLUSH, optional LSEEK, DESTROY/RELEASE no-ops, and LOOKUP returning `ENOENT` for anything besides the root. Reads short-read at EOF and allocate aligned response buffers. Writes enforce writability, handle fixed-size short writes or growable truncation, guard offset overflow, and use `blk_co_pwrite()`. Fallocate supports EOF preallocation, optional punch-hole, and optional zero-range by truncating/zero-writing in chunks. LSEEK maps `SEEK_DATA`/`SEEK_HOLE` through block status and handles EOF visibility.

Responses are written either as a single `FuseRequestOutHeader` or header-plus-buffer for read data. Shutdown detaches handlers and removes the mountpoint from the global export table; delete closes cloned FDs, frees cached buffers/queues, unmounts/destroys the session, and frees the mountpoint. The exported driver is `blk_exp_fuse`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/fuse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/meson.build -->
# File Research: sources/virtualization/qemu/block/export/meson.build

Build manifest for block export sources. It always adds `export.c`, conditionally adds `vhost-user-blk-server.c` and `virtio-blk-handler.c` when vhost-user block server support is enabled, conditionally adds `fuse.c` when FUSE support is available, and conditionally adds VDUSE export sources plus `libvduse`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/meson.build -->