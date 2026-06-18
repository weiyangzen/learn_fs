# Group Research: group_1647_qemu_sources_virtualization_qemu_block_ssh_c_sources_virtualization_24f895174266

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/virtualization/qemu`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/ssh.c -->
# File Research: sources/virtualization/qemu/block/ssh.c

`ssh.c` implements QEMU's `ssh` block protocol driver on top of libssh/libssh SFTP. It registers `bdrv_ssh` as both `format_name` and `protocol_name` `"ssh"` and provides URI parsing, remote connection setup, image creation, read/write/flush/truncate, filename refresh, and cleanup.

Core state is `BDRVSSHState`: a coroutine mutex serializes libssh/SFTP access; `sock`, `ssh_session`, `sftp_session`, and `sftp_file` hold the transport; `sftp_attributes attrs` caches remote file size/type; `InetSocketAddress *inet` and `char *user` are retained for error messages and `ssh_refresh_filename()`; `unsafe_flush_warning` suppresses repeated fsync capability warnings. `ssh_state_init()` zeros state, sets `sock = -1`, and initializes the mutex. `ssh_state_free()` frees user, attributes, SFTP file/session, disconnects SSH, and frees the libssh session, which owns the socket after `SSH_OPTIONS_FD`.

Option handling supports both URI and structured QAPI forms. `parse_uri()` accepts only `ssh://`, requires host and path, defaults port to 22, maps user/host/port/path into QDict options, and recognizes only the `host_key_check` query parameter. `ssh_has_filename_options_conflict()` rejects explicit option keys that conflict with a filename. `ssh_process_legacy_options()` translates legacy `host`, `port`, and `host_key_check` strings into modern QAPI keys such as `server.host` and `host-key-check.mode/type/hash`. `ssh_parse_options()` absorbs legacy runtime options, runs the translator, then builds `BlockdevOptionsSsh` with a flat QAPI visitor and clears processed options.

Host identity checking is explicit and central. Default mode is `known_hosts`. `check_host_key_knownhosts()` uses `ssh_session_is_known_server()` and fails on changed, missing, unknown, or wrong-type keys, including SHA256 fingerprint details when available. Hash mode goes through `check_host_key_hash()`, which obtains the server public key, computes MD5/SHA1/SHA256 as requested, and compares with `compare_fingerprint()`. Mode `none` skips validation. Authentication tries `ssh_userauth_none()` first, then `ssh_userauth_publickey_auto()` using normal identities/agent; password authentication is not implemented.

`connect_to_ssh()` is the main open helper. It selects the requested or system user, takes ownership of the QAPI `server` address into `s->inet`, parses a numeric port, opens a socket with `inet_connect_saddr()`, tries `TCP_NODELAY`, creates and configures a blocking libssh session, reads `~/.ssh/config`, binds the existing socket into libssh, connects, verifies the host key, authenticates, initializes SFTP, opens the remote path with caller-supplied `ssh_flags` and optional `creat_mode`, forces the SFTP file handle into blocking mode, and reads initial attributes. On errors it unwinds every partially initialized object and closes any socket not yet owned by libssh.

Create/open behavior is split between `ssh_open()`, `ssh_co_create()`, and `ssh_co_create_opts()`. `ssh_open()` maps `BDRV_O_RDWR` to `O_RDWR` or `O_RDONLY`, parses options, connects, and advertises `BDRV_REQ_ZERO_WRITE` truncation support for regular files. `ssh_co_create()` connects with `O_RDWR | O_CREAT | O_TRUNC` and uses `ssh_grow_file()` to size the file by writing one zero byte at `size - 1`. Legacy create options parse `size`, round to sector size, parse the URI, and call the QAPI create path.

I/O is coroutine-based but libssh calls are serialized by `s->lock`. `ssh_read()` seeks, then iterates over QEMU iovecs, limiting SFTP read requests to 16 KiB, yielding with `co_yield()` on `SSH_AGAIN`, zero-filling short EOF reads, and returning `-EIO` on SFTP errors. `ssh_write()` similarly seeks and writes iovec slices, limiting individual writes to 128 KiB, yielding on `SSH_AGAIN`, and updating cached size when writes extend the file. `co_yield()` registers AIO read/write handlers based on `ssh_get_poll_flags()` and wakes the coroutine through `restart_coroutine()`.

Flush uses OpenSSH's `fsync@openssh.com` extension. If unsupported, `ssh_flush()` warns once and returns success, which preserves compatibility but is not durable. If supported, it calls `sftp_fsync()` and yields on `SSH_AGAIN`. `ssh_co_getlength()` returns cached `attrs->size` without a libssh call. `ssh_co_truncate()` supports only growth and no preallocation; shrinking returns `-ENOTSUP`.

Filename helpers regenerate exact `ssh://user@host:port/path?host_key_check=...` names only when the stored `InetSocketAddress` can be represented simply. `ssh_bdrv_dirname()` refuses to synthesize a base directory if `host_key_check` requires a query string or no exact filename is available.

Important risks and invariants:
- All SFTP operations depend on serialized access through `CoMutex`; direct libssh calls outside this discipline could corrupt shared state.
- Cached length can become stale if another client mutates the remote file.
- Unsupported fsync returns success after warning, so management layers must understand durability is best-effort for servers lacking the extension.
- Only public-key/agent authentication is available.
- Host key hash comparison parses hex manually and accepts colon separators; malformed input fails by mismatch.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/stream.c -->
# File Research: sources/virtualization/qemu/block/stream.c

`stream.c` implements QEMU image streaming as a `BlockJob`. Streaming copies data from backing/intermediate images into the active top image, then adjusts the backing chain so the streamed range no longer depends on the old base.

`StreamBlockJob` extends `BlockJob` with a `BlockBackend *blk` for I/O through a temporary copy-on-read filter, pointers for `base_overlay`, `above_base`, `cor_filter_bs`, and `target_bs`, error policy, optional replacement backing string, protocol-masking flag, and whether the original target was read-only. `STREAM_CHUNK` is 512 KiB, the maximum chunk fed to copy-on-read prefetch.

`stream_start()` is the public entry point. It accepts either the older `base` interface or newer `bottom` interface, locates the overlay above the base, reopens the target read-write if necessary, inserts a `copy-on-read` filter above the target with `bottom` set to `base_overlay`, creates a block job on that filter, creates a `BlockBackend` with consistent read/write permissions, disables backend request queuing to avoid drain deadlocks, and blocks graph-changing or write/resize permissions on the active and intermediate nodes. It records all job state and starts the job.

`stream_run()` performs the main copy loop. It obtains the unfiltered target and length under graph lock, exits early if already at `base_overlay`, initializes progress, then scans offsets until the virtual length. For each chunk it yields via `block_job_ratelimit_sleep()`, honors cancellation, checks whether the top image already has data with `bdrv_co_is_allocated()`, and if not, checks whether data exists above the base using `bdrv_co_is_allocated_above()`. When data needs copying, it calls `stream_populate()`, which performs a prefetch read through the copy-on-read filter so the filter writes missing data into the target. Errors are routed through `block_job_error_action()` according to `on_error`, with STOP causing a retryable pause and REPORT ending the loop.

`stream_prepare()` runs at job completion. It drops the copy-on-read filter, drains all block nodes to stabilize the graph, finds the current base relationship, switches the unfiltered target backing child to the selected base with `bdrv_set_backing_hd()`, and updates the on-disk backing file string/format through `bdrv_change_backing_file()`. It handles protocol masking by using `"raw"` when the base is a protocol node and masking was requested.

`stream_clean()` removes any remaining copy-on-read filter, unreferences the job backend, restores read-only state if the job had reopened the image, and frees the backing file string.

Key invariants:
- `base` and `bottom` are mutually exclusive, and `backing_file_str` cannot be used with `bottom`.
- The copy-on-read filter is both the data-copy mechanism and a chain-freezing guard; it is dropped only when the job is ready to change backing.
- Graph locks and drain boundaries are critical because other jobs may mutate the chain while streaming.
- Intermediate nodes are protected because stream assumes each block is read once and remains unchanged.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/stream.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/throttle-groups.c -->
# File Research: sources/virtualization/qemu/block/throttle-groups.c

`throttle-groups.c` implements shared I/O throttling groups. Multiple `ThrottleGroupMember` instances can share one `ThrottleState`, while each member has its own AIO context, timers, pending queues, and round-robin position. It also exposes QOM `throttle-group` objects for monitor/QAPI configuration.

The private `ThrottleGroup` object contains the QOM parent, initialized flag, immutable name, a mutex protecting shared throttling state, `ThrottleState ts`, a list of members, per-direction round-robin tokens, per-direction `any_timer_armed` flags, and the clock type. All group objects are tracked in a global `throttle_groups` tail queue protected by the global QEMU mutex.

Lifetime helpers are name-based. `throttle_group_by_name()` searches the global list. `throttle_group_exists()` reports presence. `throttle_group_incref()` returns the group's `ThrottleState`, creating and completing a new `TYPE_THROTTLE_GROUP` object if absent. `throttle_group_unref()` drops the object reference. `throttle_group_get_name()` recovers the group name from a member's `ThrottleState`.

Scheduling is round-robin and per direction (`THROTTLE_READ`, `THROTTLE_WRITE`). `next_throttle_token()` advances from the current token to the next member with pending requests, with a special path for members whose `io_limits_disabled` is set during drain. `throttle_group_schedule_timer()` checks whether limits require waiting; if no group timer is armed, it calls `throttle_schedule_timer()` and records the member as the token. `schedule_next_request()` selects the next pending member, schedules a timer if needed, or immediately restarts a coroutine queue/timer.

`throttle_group_co_io_limits_intercept()` is the runtime interception point used by the throttle filter. It locks the group, decides whether the request must wait, queues the current coroutine on the member's `throttled_reqs[direction]` if a timer or prior pending request exists, accounts the bytes with `throttle_account()`, schedules the next request, and unlocks. This makes the shared `ThrottleState` enforce aggregate limits across all members while preserving fairness.

Restart machinery uses `RestartData` and a coroutine entry point. `throttle_group_restart_queue()` creates a coroutine in the member's AIO context and increments `restart_pending`. The coroutine clears `any_timer_armed` if appropriate, wakes one queued request, schedules another if the queue was empty, decrements `restart_pending`, and kicks `aio_wait`. `throttle_group_restart_tgm()` forces all directions of one member to progress, handling three cases: this member owns a pending timer, another member owns a pending timer, or no timer exists.

Configuration functions wrap the throttle library under the group mutex. `throttle_group_config()` atomically applies a `ThrottleConfig` and restarts queues. `throttle_group_get_config()` reads it. QOM property setters/getters map `x-iops-*`, `x-bps-*`, burst lengths, and `x-iops-size` into `ThrottleConfig`; individual property changes are only allowed before initialization because valid combinations require transactional validation. The `limits` property accepts/returns a full `ThrottleLimits` QAPI object.

Member registration and removal are careful around timers and AIO contexts. `throttle_group_register_tgm()` increfs/creates the group, initializes member queues, installs initial tokens if needed, inserts the member, and initializes timers with read/write callbacks. `throttle_group_unregister_tgm()` waits for pending restart coroutines, asserts no pending throttled requests or timers remain, updates tokens if removing the current token, removes the member, destroys timers, unreferences the group, and nulls the state pointer. Attach/detach functions move timers between AIO contexts and, on detach, reschedule any pending group work before destroying timer bindings.

The QOM type defaults to realtime clock, but qtest uses virtual clock for deterministic throttling tests. `complete` validates config and inserts the group into the global list; `finalize` removes initialized groups and frees resources; `can_be_deleted` allows deletion only when the object refcount is one.

Important risks and invariants:
- The group mutex protects both shared `ThrottleState` and cross-member fields; callers outside this file should not touch those internals.
- `throttle_timers` may be temporarily invalid during AIO context changes, so cross-member timer access is guarded by pending-request checks and detach assertions.
- Unregister requires the caller to drain first.
- `io_limits_disabled` is atomic because drain paths bypass normal throttling and can interact with scheduling.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/throttle-groups.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/throttle.c -->
# File Research: sources/virtualization/qemu/block/throttle.c

`throttle.c` implements the QEMU block filter driver named `"throttle"`. It attaches a block node to an existing throttle group and intercepts I/O requests to enforce the group's shared limits.

The only driver-specific open option is `throttle-group`. `throttle_parse_options()` absorbs options through `throttle_opts`, requires a group name, and verifies that the named group already exists with `throttle_group_exists()`. On success it returns a duplicated group name. `throttle_open()` opens the `"file"` child, inherits supported write/zero flags from the child while adding `BDRV_REQ_WRITE_UNCHANGED`, parses the group, and registers the node's `ThrottleGroupMember` with `throttle_group_register_tgm()` using the block node's AIO context.

The filter forwards data operations after interception. `throttle_co_preadv()` calls `throttle_group_co_io_limits_intercept(tgm, bytes, THROTTLE_READ)` before forwarding to `bdrv_co_preadv()`. `throttle_co_pwritev()`, `throttle_co_pwrite_zeroes()`, and `throttle_co_pdiscard()` intercept as `THROTTLE_WRITE` before forwarding. Compressed writes reuse `throttle_co_pwritev()` with `BDRV_REQ_WRITE_COMPRESSED`. Flush and getlength forward directly to the child.

AIO context hooks delegate to the group layer: `throttle_detach_aio_context()` detaches timers, and `throttle_attach_aio_context()` reattaches them in the new context. Reopen support reparses the target group in prepare, then on commit unregisters/reregisters the member if the group name changed; abort frees the prepared group string.

Drain handling disables limits while draining. `throttle_drain_begin()` atomically increments `io_limits_disabled` and restarts the member if this is the first disable. `throttle_drain_end()` decrements and asserts the disable count was nonzero. This prevents drain from waiting behind throttled requests.

`bdrv_throttle` is marked `is_filter = true`, uses default child permissions, has `instance_size = sizeof(ThrottleGroupMember)`, and declares `throttle-group` as a strong runtime option. Close unregisters the member from its group.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/throttle.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/trace.h -->
# File Research: sources/virtualization/qemu/block/trace.h

`trace.h` is a one-line local include shim:

```c
#include "trace/trace-block.h"
```

It lets block-layer C files include `"trace.h"` locally while resolving to the generated block trace header. It contains no state, declarations, or logic of its own.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vdi.c -->
# File Research: sources/virtualization/qemu/block/vdi.c

`vdi.c` implements QEMU's VirtualBox VDI image format driver. It supports probing, opening, checking, reading, writing, creating dynamic/static images, block status, zero-init reporting, and migration blocking. Snapshots, backing files, shrinking, and deallocation are explicitly absent or TODO.

The on-disk format is represented by `VdiHeader`, a packed 512-byte structure with signature/version/type, block map/data offsets, disk geometry, sector size, disk size, block size, block counts, and UUIDs. `BDRVVdiState` stores the little-endian block map in memory, block size, first block-map sector, host-endian header, a coroutine rwlock for bmap access, and a migration blocker. Constants define VDI signature/version, dynamic/static image types, default 1 MiB clusters, unallocated/discarded block markers, maximum block-map entries, and maximum supported disk size.

Endian helpers convert the header between disk little-endian and host order, including UUID byte swapping. `vdi_header_print()` is debug-only logging. `vdi_probe()` returns high confidence when the header signature matches. `vdi_open()` opens the `"file"` child, reads and validates the header, rounds odd disk sizes up to 512 bytes for compatibility, rejects unsupported signatures, versions, unaligned map/data offsets, non-512 sector sizes, non-default block sizes, impossible disk sizes, non-null link/parent UUIDs, and excessive block counts. It sets `bs->total_sectors`, allocates an aligned in-memory block map, reads it, installs a live-migration blocker, and initializes the bmap lock.

`vdi_co_check()` validates the block map and allocated count. It rejects repair mode, builds a temporary map to detect duplicate physical block indices, reports entries outside range, and compares counted allocated blocks with `header.blocks_allocated`. `vdi_co_get_info()` reports cluster size. `vdi_make_empty()` is a stub returning success as required by block-layer expectations.

Block status maps one cluster at a time. `vdi_co_block_status()` looks up the block-map entry, returns `BDRV_BLOCK_ZERO` for unallocated/discarded entries, otherwise maps to `offset_data + bmap_entry * block_size + index_in_block`, returns the child file, and adds `BDRV_BLOCK_RECURSE` for static images.

Reads iterate by VDI block boundaries. `vdi_co_preadv()` uses the bmap rwlock to read each block-map entry, zero-fills unallocated/discarded ranges, or reads from the child at the mapped physical offset. It uses a local concatenated `QEMUIOVector` per chunk.

Writes allocate on demand. `vdi_co_pwritev()` walks block boundaries, checks the bmap under read lock, upgrades to write lock for unallocated blocks, assigns the next physical block index from `header.blocks_allocated`, increments the header count, builds a full cluster buffer with unwritten parts zeroed, writes the entire new cluster while holding write-side bmap protection, and records the first/last modified bmap entries. Existing blocks are written directly as subranges. After successful data writes that allocated blocks, it writes the updated header and the affected aligned sectors of the block map. On data-write failure it returns before persisting header/map changes, leaving the in-memory map changed only for the failed open instance.

Creation is handled by `vdi_co_do_create()`. It validates size, preallocation mode, static-image support, optional cluster-size support, and maximum disk size; opens the protocol file through a `BlockBackend`; calculates block count and sector-aligned bmap size; writes a QEMU VDI header with generated image and snapshot UUIDs; writes a bmap filled with physical indices for static images or `VDI_UNALLOCATED` for dynamic images; and truncates static images to include all data blocks. Legacy create options create/open the file layer, translate `static` to QAPI `preallocation=metadata`, silently round size to sector size, and call the QAPI create path.

`vdi_close()` frees the bmap and removes the migration blocker. `vdi_has_zero_init()` returns the child zero-init status for static images and true for dynamic images because unallocated blocks read as zero.

Important risks and invariants:
- Only 512-byte sectors and 1 MiB VDI blocks are supported in the default build.
- Parent/link UUIDs are rejected, so VDI snapshots/backing chains are unsupported.
- Live migration is blocked for any VDI node.
- The code uses `CoRwlock` for block-map changes; header and bmap persistence must remain ordered after new cluster writes.
- Static images can report recursive block status because all payload blocks are mapped.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vdi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vhdx-endian.c -->
# File Research: sources/virtualization/qemu/block/vhdx-endian.c

`vhdx-endian.c` contains import/export helpers for VHDX on-disk little-endian structures. VHDX files store all multi-byte fields little-endian, but Microsoft GUID fields require mixed treatment where `data1`, `data2`, and `data3` are endian-converted while `data4` remains byte-array data.

The file provides conversions for:
- `VHDXHeader`: signature, checksum, sequence, GUIDs, log version, version, log length, and log offset.
- `VHDXLogDescriptor`: descriptor signature, file offset, sequence number, and export of union payload fields (`trailing_bytes`/`leading_bytes`).
- `VHDXLogDataSector`: data signature and split sequence high/low.
- `VHDXLogEntryHeader`: log header signature, checksum, entry length, tail, sequence, descriptor count, log GUID, flushed file offset, and last file offset.
- `VHDXRegionTableHeader` and `VHDXRegionTableEntry`.
- `VHDXMetadataTableHeader` and `VHDXMetadataTableEntry`.

The helpers assert non-null pointers and mostly convert in place, except `vhdx_header_le_export()` copies from a host-order source header into a separate little-endian destination. These functions are used by `vhdx.c` and `vhdx-log.c` before validating, checksumming, writing headers, building logs, and parsing metadata.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vhdx-endian.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vhdx-log.c -->
# File Research: sources/virtualization/qemu/block/vhdx-log.c

`vhdx-log.c` implements VHDX metadata log parsing, validation, replay, writing, and immediate flushing. The VHDX log is a circular buffer of 4 KiB sectors located at the offset/length from the active VHDX header. It journals metadata changes such as BAT entry updates so a dirty image can be recovered on open.

Internal helper structs are `VHDXLogSequence`, representing a contiguous valid sequence of log entries, and `VHDXLogDescEntries`, a log entry header followed by flexible-array descriptors. `zero_guid` marks an empty log. Indexing uses `vhdx_log_inc_idx()` to advance one 4 KiB sector with wraparound.

Read-side primitives include `vhdx_log_peek_hdr()`, which reads but does not advance the current header; `vhdx_log_read_sectors()`, which reads sectors from the circular log and optionally advances `read`; and `vhdx_log_reset()`, which clears read/write pointers and updates headers with a zero log GUID. `vhdx_log_write_sectors()` writes sectors to the circular log, after calling `vhdx_user_visible_write()`, and stops before colliding with the read pointer.

Validation checks are layered. `vhdx_log_hdr_is_valid()` verifies signature, entry length bounds/alignment, nonzero sequence number, matching active header log GUID, and descriptor-count bounds. `vhdx_log_desc_is_valid()` checks descriptor sequence, 4 KiB file-offset alignment, and valid `zero` or `desc` signatures; zero descriptors must have 4 KiB-aligned lengths. `vhdx_log_read_desc()` reads descriptor sectors, converts descriptors to host order when requested, and validates each descriptor. `vhdx_validate_log_entry()` verifies a full entry, sequence continuity, descriptor validity, data sector reads, and CRC32C across descriptor and data sectors.

Replay uses `vhdx_log_search()` to scan the circular buffer for the highest-sequence valid active log sequence. `vhdx_parse_log()` initializes log offset/length from the active header, rejects bad log offsets/version/length, exits if GUID or length says no log is present, searches for a valid sequence, refuses read-only open if replay is required, and otherwise flushes the sequence into the image. The read-only failure message points users to `qemu-img check -r all`.

`vhdx_log_flush()` replays a validated sequence. For each entry it re-peeks the header, rejects logs whose flushed-file offset exceeds current file length, reads descriptors, reads data sectors for data descriptors, converts data sector endian fields, applies each descriptor via `vhdx_log_flush_desc()`, extends the file to `last_file_offset` rounded to MiB if needed, flushes the block node, and resets the log. `vhdx_log_flush_desc()` reconstructs full 4 KiB data sectors from descriptor leading/trailing bytes plus the data-sector payload, or writes explicit zero sectors for zero descriptors.

Write-side logging is intentionally simple: `vhdx_log_write_and_flush()` flushes existing data, calls `vhdx_log_write()`, flushes the log, then immediately replays the just-written log. `vhdx_log_write()` creates a new log GUID if the header currently has zero log GUID; otherwise it returns `-ENOTSUP` because this implementation requires flushing after every write. It computes sector coverage for possibly unaligned writes, merges partial leading/trailing sectors with existing file contents, builds descriptors and data sectors in little-endian form through `vhdx_log_raw_to_le_sector()`, computes the entry checksum, writes all sectors to the circular log, increments sequence, and updates tail.

Important risks and invariants:
- Log writes are immediately flushed, simplifying consistency but limiting batching.
- Read-only open refuses dirty logs because replay must modify the image.
- Partial-sector journal writes depend on reading destination file contents before logging.
- `flushed_file_offset` protects against replaying a log into a truncated image.
- All checksum and endian handling must occur on the correct disk-order buffers.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vhdx-log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vhdx.c -->
# File Research: sources/virtualization/qemu/block/vhdx.c

`vhdx.c` is QEMU's main Hyper-V VHDX image format driver. It handles probing, header/region/metadata/BAT parsing, log replay integration, read/write, image creation, checking, zero-init reporting, and driver registration. Differencing VHDX files are recognized through metadata but not supported.

The file defines known VHDX region and metadata GUIDs, create options (`log_size`, `block_size`, `block_state_zero`, subformat), `VHDXImageType`, metadata-present flags, and `VHDXSectorInfo`, which carries BAT index, available sectors/bytes, payload file offset, and block offset for translated I/O.

Checksum helpers use CRC32C. `vhdx_update_checksum()` zeroes the checksum field, calculates CRC over a disk-order buffer, stores little-endian CRC, and returns it. `vhdx_checksum_calc()` supports incremental calculation while temporarily zeroing a CRC field. `vhdx_checksum_is_valid()` compares a stored little-endian CRC with a recalculated one. `vhdx_guid_generate()` creates a QEMU UUID and stores it as an MS GUID-compatible struct.

Region overlap tracking is used for safety. `vhdx_region_register()` records file regions, `vhdx_region_check()` rejects overlaps, and `vhdx_region_unregister_all()` frees the list. The header/log/region/BAT areas are checked so payload BAT entries cannot point into metadata/log/header regions.

Open flow starts in `vhdx_open()`. It opens the `"file"` child, initializes mutex/region list, validates the `vhdxfile` signature, creates a per-session GUID for future header updates, parses the two redundant headers with `vhdx_parse_header()`, replays a dirty log with `vhdx_parse_log()`, opens region tables, parses metadata, sets total sectors, calculates BAT entry count and BAT offset, reads and endian-converts the BAT, optionally checks BAT entries unless opening for check, and installs a live-migration blocker.

`vhdx_parse_header()` reads both 64 KiB header blocks, validates the 4 KiB header checksum, imports little-endian fields, accepts version 1 headers with `head` signature, and chooses the highest sequence number. Equal sequence numbers are accepted only if both headers are byte-identical, matching a Disk2VHD compatibility case. The active header's log region is registered. Header updates use `vhdx_update_header()` and `vhdx_update_headers()`, writing the inactive header with a higher sequence number and then doing the process twice so both headers converge.

`vhdx_open_region_tables()` reads the primary region table block, validates its checksum/signature and entry count, imports entries, rejects overlaps, records the BAT and metadata regions by GUID, rejects duplicate required known regions, and fails on unknown required regions. Both BAT and metadata regions are mandatory.

`vhdx_parse_metadata()` reads the metadata table, identifies required entries for file parameters, virtual disk size, page 83 data, logical sector size, and physical sector size, rejects unknown required metadata, rejects duplicate required entries, reads file parameters and sizes, rejects differencing files with parent locators as unsupported, supports only 512-byte logical sectors, validates block size and power-of-two derived values, computes sectors per block and chunk ratio, and caches shift counts.

BAT layout is calculated by `vhdx_calc_bat_entries()`, including sector bitmap entries interleaved by chunk ratio. `vhdx_check_bat_entries()` validates fully-present payload BAT entries against file length, overflow, truncation, and registered regions. `vhdx_block_translate()` maps logical sector ranges to BAT index and file offsets, adjusting for interleaved sector bitmap BAT entries.

Reads are serialized by `s->lock`. `vhdx_co_readv()` loops across payload block boundaries, rejects differencing files, translates sectors, and branches on BAT state. Not-present, undefined, unmapped, v0.95 unmapped, and zero states read as zero. Fully present blocks read from the child file at the translated payload offset. Partially present blocks and unknown states return errors because differencing support is absent.

Writes are also serialized. `vhdx_user_visible_write()` updates data-write GUID in the headers on the first guest-visible write. `vhdx_co_writev()` translates each block, allocates a new payload block for not-present/unmapped/undefined/zero states with `vhdx_allocate_block()`, optionally zero-fills the rest of a newly allocated block when truncation cannot guarantee zeroes, writes user data to the payload, updates the in-memory BAT entry to fully present, and persists the BAT entry through `vhdx_log_write_and_flush()`. On write error after a BAT update, it restores the in-memory BAT state. Fully present blocks are overwritten directly. Partially present/differencing paths return unsupported/error.

Creation writes the full VHDX layout. `vhdx_co_create()` validates maximum 64 TiB image size, log size multiple/minimum, subformat dynamic/fixed, zero-block option, and block size. It opens the target protocol node through a `BlockBackend`, writes the file identifier and UTF-16 creator string, creates two headers with `vhdx_create_new_headers()`, creates region tables and BAT with `vhdx_create_new_region_table()`/`vhdx_create_bat()`, then writes required metadata with `vhdx_create_new_metadata()`. Dynamic images can use zero-state BAT entries; fixed images preallocate data and mark payload blocks fully present. Legacy create options rename old option keys to QAPI keys, create/open the protocol layer, round size/log/block values, and call the QAPI create function.

`vhdx_co_check()` reports a fixed corruption if the log was replayed during open, then validates BAT entries. `vhdx_has_zero_init()` distinguishes fixed images, which inherit child zero-init status, from dynamic images, which read unallocated data as zero. `vhdx_close()` frees headers, BAT, parent entries, log header, migration blocker, and registered regions.

Important risks and invariants:
- Live migration is blocked for VHDX nodes.
- Differencing files and non-512 logical sector sizes are unsupported.
- Metadata/BAT updates rely on the log path for consistency; direct BAT persistence would bypass recovery semantics.
- Header update sequencing and GUID updates are spec-sensitive.
- BAT entries use 1 MiB-aligned file offsets plus low state bits; incorrect masking can point payload data into metadata regions.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vhdx.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vhdx.h -->
# File Research: sources/virtualization/qemu/block/vhdx.h

`vhdx.h` defines the VHDX on-disk structures, constants, shared driver state, and cross-file function prototypes used by `vhdx.c`, `vhdx-log.c`, and `vhdx-endian.c`.

Header-section constants describe the fixed first MiB: file identifier at offset 0, two 64 KiB header blocks, two region table blocks, and `VHDX_HEADER_SECTION_END`. `VHDXFileIdentifier`, `MSGUID`, `VHDXHeader`, `VHDXRegionTableHeader`, and `VHDXRegionTableEntry` model the file signature, Microsoft GUID layout, redundant headers, and region table records. The header uses CRC32C over a 4 KiB header area even though the packed header struct is smaller.

Log constants and structs define 1 MiB minimum log size, 4 KiB log sectors, log entry headers, descriptors, and data sectors. Log descriptors can be zero descriptors or data descriptors; data descriptors store the first 8 and last 4 bytes of a 4 KiB sector in the descriptor while the middle 4084 bytes live in a `VHDXLogDataSector`.

BAT constants define payload and sector-bitmap states, maximum sectors per block, bit masks for state and file offset, and `VHDXBatEntry`. Payload states include not present, undefined, zero, unmapped, fully present, and partially present. File offsets occupy the upper bits in 1 MiB units/alignment semantics.

Metadata structs define the metadata table header/entries and required metadata payloads: file parameters, virtual disk size, page 83 data, logical/physical sector sizes, and parent locator structures. Flags distinguish user metadata, virtual-disk metadata, and required metadata. VHDX supports up to 64 TiB virtual disk size and block sizes from 1 MiB to 256 MiB.

`VHDXMetadataEntries` stores recognized metadata table entries and a bitmask of presence. `VHDXLogEntries` stores circular-log runtime state: offset, length, write/read indexes, allocated header buffer, descriptor buffer, sequence, and tail. `VHDXRegionEntry` is an in-memory overlap-check list node. `BDRVVHDXState` is the main per-node state: coroutine mutex, active header index and two headers, region table entries, metadata, file parameters, block/sector/chunk sizing and shift caches, BAT entries and offset, first-visible-write flag, session GUID, log state, parent locator state, migration blocker, log-replayed flag, and registered regions.

The header also declares shared functions:
- GUID, checksum, and header update helpers from `vhdx.c`.
- Log parse/write/flush helpers from `vhdx-log.c`.
- Endian import/export helpers from `vhdx-endian.c`.
- `vhdx_user_visible_write()` for log code to trigger first-write header updates.

Inline GUID conversion helpers convert only `data1`, `data2`, and `data3`, preserving `data4` byte order. This is essential because MS GUIDs are not just raw 16-byte little-endian integers.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vhdx.h -->