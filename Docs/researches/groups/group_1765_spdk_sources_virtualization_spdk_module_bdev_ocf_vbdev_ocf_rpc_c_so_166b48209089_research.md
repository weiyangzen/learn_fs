# Group Research: group_1765_spdk_sources_virtualization_spdk_module_bdev_ocf_vbdev_ocf_rpc_c_so_166b48209089

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf_rpc.c

This file implements JSON-RPC control surface for the SPDK OCF virtual bdev module. It registers runtime RPCs for creating and deleting OCF devices, listing OCF devices, retrieving and resetting OCF statistics, changing cache mode, setting sequential cutoff parameters, starting a cache flush, and querying flush status.

The create path decodes `name`, `mode`, optional `cache_line_size`, `cache_bdev_name`, and `core_bdev_name`, then calls `vbdev_ocf_construct()`. The asynchronous `construct_cb()` returns the created vbdev name on success or a JSON-RPC internal error on failure. Delete decodes a device name, resolves it with `vbdev_ocf_get_by_name()`, then calls `vbdev_ocf_delete_clean()` and returns a boolean from `delete_cb()`.

Statistics RPCs use a small `get_ocf_stats_ctx` containing the request and OCF core name. Both `bdev_ocf_get_stats` and `bdev_ocf_reset_stats` resolve the vbdev, take an OCF cache management read lock, operate on the named core through `vbdev_ocf_stats_get()` or `vbdev_ocf_stats_reset()`, unlock the cache, and finally either emit JSON stats or a boolean success. Error reporting converts negative OCF/SPDK-style values with `spdk_strerror(-error)`.

`bdev_ocf_get_bdevs` optionally filters by an OCF vbdev name or by cache/core base name. It emits an array of objects containing the OCF device name, started state, and nested cache/core objects with each base name and attached flag. The helper `bdev_get_bdevs_fn()` is passed to `vbdev_ocf_foreach()`.

Cache mode and sequential cutoff RPCs are thin validators around module operations. `bdev_ocf_set_cache_mode` decodes `name` and `mode`, resolves the vbdev, calls `vbdev_ocf_set_cache_mode()`, and returns the effective OCF cache mode string from `ocf_get_cache_modename(ocf_cache_get_mode())`. `bdev_ocf_set_seqcutoff` decodes policy plus optional `threshold` and `promotion_count`, then calls `vbdev_ocf_set_seqcutoff()`.

Flush handling is asynchronous and stateful on `vbdev->flush`. `bdev_ocf_flush_start` refuses detached devices, locks the OCF cache for management read, marks `flush.in_progress`, starts `ocf_mngt_cache_flush()`, and immediately returns true once the flush is submitted. The flush completion callback stores the final status and clears `in_progress`. `bdev_ocf_flush_status` returns `in_progress` and, when not in progress, the last stored status.

Important dependencies are the autogen RPC context/free helpers from `spdk_internal/rpc_autogen.h`, `vbdev_ocf` lifecycle APIs, OCF management cache locks, and the stats JSON writer. The file consistently frees decoded RPC request strings on all paths, but RPC handlers often report internal errors for decode/allocation failures rather than always using JSON-RPC invalid-params codes.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/volume.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/volume.c

This file adapts SPDK bdevs to OCF volume operations. It registers an OCF volume type named `SPDK_block_device` whose private data is a `struct vbdev_ocf_base *`, and whose forward operations translate OCF read/write/flush/discard requests into SPDK bdev I/O.

`vbdev_ocf_volume_open()` stores the base pointer in the OCF volume private area. It either uses an explicit `opts` pointer or resolves a base object by UUID data via `vbdev_ocf_get_base_by_name()`. Close is a no-op. `vbdev_ocf_volume_get_length()` returns `blocklen * blockcnt` from the resolved base bdev. `vbdev_ocf_volume_get_max_io_size()` currently returns a fixed 131072 byte maximum.

The central path is `vbdev_forward_io()`. It gets the base object from volume private data, gets the OCF data object from the forward token, selects an SPDK I/O channel with `vbdev_forward_get_channel()`, and submits `spdk_bdev_readv()` or `spdk_bdev_writev()`. Management queues use the base management channel; normal queues use the queue private `vbdev_ocf_qctx` and choose cache or core channel based on `base->is_cache`.

Partial data forwarding is handled by `get_starting_vec()` and `initialize_cpy_vector()`. When the requested byte count is smaller than the OCF data buffer, the code finds the starting iovec for the given offset, allocates a temporary iovec array with `env_malloc()`, and creates a trimmed view into the original iovecs. The completion callback frees this temporary iovec array when used. Submission failures manually call `ocf_forward_end()` because SPDK completion will not run.

Flush and discard are direct translations. `vbdev_forward_flush()` submits a full-device SPDK flush over `blockcnt * blocklen` bytes. `vbdev_forward_discard()` submits `spdk_bdev_unmap()` for the requested byte address and length. Both return `-OCF_ERR_NO_MEM` on `-ENOMEM` submission failure and `-OCF_ERR_IO` otherwise.

`vbdev_forward_io_simple()` exists for OCF contexts where no queue is available. It allocates a small context, obtains an I/O channel with `spdk_bdev_get_io_channel()`, submits read/write on the OCF data iovs, and releases the channel in `vbdev_forward_io_simple_cb()`.

`vbdev_ocf_volume_init()` registers the OCF volume type against `vbdev_ocf_ctx` and `SPDK_OBJECT`; cleanup unregisters it. The implementation assumes byte-addressed OCF requests are aligned well enough for the underlying bdev calls and relies on OCF/SPDK higher layers for lifecycle synchronization of the base descriptors and channels.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/volume.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/volume.h

This private OCF header declares the volume adapter entry points implemented by `volume.c`.

It includes OCF, OCF context, and OCF data headers, then exports `vbdev_ocf_volume_init()` and `vbdev_ocf_volume_cleanup()`. The include guard name is `VBDEV_OCF_DOBJ_H`, which is broader than the file name but only protects these two declarations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/volume.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/passthru/Makefile

This Makefile builds the SPDK passthru bdev module as library `bdev_passthru`.

It sets `SPDK_ROOT_DIR` relative to the module directory, includes `mk/spdk.common.mk`, sets shared object version `8.0`, adds `$(SPDK_ROOT_DIR)/lib/bdev/` to `CFLAGS`, and compiles `vbdev_passthru.c` plus `vbdev_passthru_rpc.c`. The module uses `mk/spdk_blank.map` as its map file and includes `mk/spdk.lib.mk` for the common SPDK library build rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.c -->
# File Research: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.c

This file implements the passthru virtual bdev module: a transparent SPDK bdev wrapper that claims a base bdev, mirrors most of its properties, and forwards I/O to it. It is structured as an example-style vbdev module but includes complete lifecycle, hot-remove, RPC-created configuration, memory-domain forwarding, and config JSON support.

The module registers `passthru_if` with init, fini, config JSON, examine, and per-I/O context size callbacks. `g_bdev_names` stores requested passthru mappings, allowing creation to be deferred until a base bdev appears. `g_pt_nodes` stores live passthru vbdevs. Each `vbdev_passthru` holds the base bdev pointer, base descriptor, wrapper `spdk_bdev`, list link, and the thread where the base descriptor was opened. Each I/O channel owns one base I/O channel.

Destruction follows SPDK vbdev ordering: remove the live node from `g_pt_nodes`, release the claim on the base bdev, close the base descriptor on its original thread when needed, unregister the I/O device, then free the wrapper name and node in `_device_unregister_cb()`. Hot-remove of the base bdev unregisters all passthru vbdevs using that base.

The I/O submit path initializes a small per-I/O context marker, then forwards based on `bdev_io->type`. Reads first obtain a buffer with `spdk_bdev_io_get_buf()` and continue in `pt_read_get_buf_cb()`. Writes use `spdk_bdev_writev_blocks_ext()`. Other supported operations are write zeroes, unmap, flush, reset, zcopy, abort, compare, and copy. Read/write extended options propagate memory domain, memory-domain context, metadata buffer, and inverted DIF exclude mask. On `-ENOMEM`, the original I/O is placed on the base bdev wait queue and later resubmitted; other submission errors complete the original I/O failed.

Completions translate base bdev I/O status back to the original I/O. `_pt_complete_io()` uses `spdk_bdev_io_complete_base_io_status()` to preserve detailed base status, then frees the child I/O. `_pt_complete_zcopy_io()` copies the populated zcopy buffer pointer/length back to the original I/O before completing it.

Registration is driven by `vbdev_passthru_register()`. It matches a base bdev name in `g_bdev_names`, allocates a node, opens the base bdev for write, chooses a UUID either from configuration or by UUIDv5/SHA1 over a module namespace UUID and the base bdev UUID, mirrors write cache, alignment, optimal I/O boundary, block geometry, metadata/DIF layout, and NUMA, registers an SPDK I/O device, claims the base bdev, and registers the wrapper bdev. Error paths close descriptors, unregister/free allocations, and remove the node from the list.

`bdev_passthru_create_disk()` inserts the requested mapping into `g_bdev_names` first, then attempts immediate registration. `-ENODEV` from registration is treated as deferred success. `bdev_passthru_delete_disk()` unregisters the named passthru bdev and removes its persistent mapping from `g_bdev_names` only when unregister submission succeeds.

The module reports support for whatever I/O types the base bdev supports, forwards memory-domain discovery to the base bdev, emits live passthru entries as `bdev_passthru_create` calls in module config JSON, and emits per-bdev info under a `passthru` object with wrapper and base names. A notable edge case is that several cleanup paths call `spdk_bdev_module_release_bdev(&pt_node->pt_bdev)` after failed registration; the normal claim was on the base bdev, so this path is worth checking when auditing failure handling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.h -->
# File Research: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.h

This public module header declares the passthru bdev management API used by the RPC file.

`bdev_passthru_create_disk()` creates or defers creation of a passthru bdev over a named base bdev, with an optional UUID. `bdev_passthru_delete_disk()` unregisters a passthru bdev by name and reports completion through an SPDK bdev unregister callback. The header includes SPDK bdev and bdev module interfaces but exposes no implementation structs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru_rpc.c

This file registers JSON-RPC methods for the passthru bdev module.

`bdev_passthru_create` decodes `base_bdev_name`, `name`, and optional `uuid`, calls `bdev_passthru_create_disk()`, and returns the passthru name as a JSON string on success. Decode failure is logged and returned as an internal JSON-RPC error; create failure uses the negative SPDK errno code directly and formats the message with `spdk_strerror(-rc)`.

`bdev_passthru_delete` decodes `name`, calls `bdev_passthru_delete_disk()`, and completes asynchronously through `rpc_bdev_passthru_delete_cb()`. The callback returns boolean true on zero bdev errno or a JSON-RPC error with the bdev errno and string.

Both handlers use autogen context cleanup helpers from `spdk_internal/rpc_autogen.h`; no persistent state is held in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/raid/Makefile

This Makefile builds the SPDK RAID bdev module as library `bdev_raid`.

It sets `SPDK_ROOT_DIR`, includes SPDK common make rules, sets shared object version `8.0`, adds `lib/bdev` to the include path, and compiles `bdev_raid.c`, `bdev_raid_rpc.c`, `bdev_raid_sb.c`, `raid0.c`, `raid1.c`, and `concat.c`. When `CONFIG_RAID5F=y`, it also includes `raid5f.c`. The module uses `mk/spdk_blank.map` and common SPDK library rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid.c

This file is the RAID bdev core. It owns the global RAID list, RAID-level module registry, generic SPDK bdev function table, base bdev claiming/configuration, state transitions, superblock-backed discovery, hot-remove/resize handling, DIX reference-tag remapping, and the shared background-process framework used for rebuild.

Global state includes `g_raid_bdev_list`, `g_raid_modules`, `g_shutdown_started`, and tunable process options. RAID levels are plugged in through `raid_bdev_module_list_add()` and `RAID_MODULE_REGISTER()`. The module table maps string names such as `raid0`, `raid1`, `raid5f`, and `concat` to SPDK RAID levels; state and process names are similarly mapped for JSON output.

Per-I/O-channel state maps RAID slots to base bdev I/O channels and optionally holds a RAID-level private channel. When a background process is active, channel state also has a `process` view: the target channel and a processed-range channel map that substitutes the rebuilt target for already processed LBA ranges. Channel create skips missing bases and process targets; channel destroy releases all base/module/process channels.

The generic I/O path initializes `struct raid_bdev_io` from an SPDK bdev I/O and dispatches reads/writes, reset, flush, and unmap. Reads obtain a buffer first. RAID-level modules handle read/write and null-payload layout. Reset is core-handled by submitting reset to every configured base channel. `raid_bdev_io_complete_part()` tracks multi-child completions and completes the parent when the expected count reaches zero. `raid_bdev_queue_io_wait()` wraps SPDK wait-queue resubmission and marks dependent unblock semantics.

Background process awareness can split front-end I/O around a processed/unprocessed boundary. If an I/O spans the current process offset, the core submits the higher, unprocessed portion first, then restores/slices iovecs and metadata and submits the lower processed portion through the processed channel view. If an I/O is wholly before the process offset, it uses the processed channel view immediately.

DIX helpers build an SPDK DIF context and call SPDK DIX utilities. `raid_bdev_remap_dix_reftag()` rewrites reference tags for writes to base devices with a physical offset including `data_offset`. `raid_bdev_verify_dix_reftag()` verifies read/write metadata against RAID logical offsets. Read completion remaps DIX reference tags back to logical offsets before completing to callers when reference-tag checking is enabled.

RAID creation is split between `_raid_bdev_create()` and `raid_bdev_create()`. The core validates name length, duplicate names, strip-size rules, module presence, minimum base count, and module operational constraints. It allocates `raid_bdev`, base slot array, initializes generic bdev fields, and inserts into the global list. The public create path assigns slot names, generates a UUID when superblocks require one, configures base bdevs asynchronously, tolerates missing bases during initial configuration, and deletes the partially created RAID on configuration failure.

Configuration of a base bdev opens the base for write, validates UUID/name, claims it for the RAID module, gets an app-thread channel, calculates or validates `data_offset` and `data_size`, rejects unsupported DIF for modules that do not support it, and enforces uniform block/metadata/DIF geometry across all bases. For new base devices, it reads any existing RAID superblock first to avoid accidentally consuming a member of another RAID. When enough operational bases are configured, `raid_bdev_configure()` converts strip size from KiB to blocks, calls the RAID-level `start()` hook, initializes/writes the superblock when enabled, registers the RAID I/O device and bdev, marks state online, and opens the RAID bdev internally to delay unregistering while processes stop.

Base removal handles explicit removal, hot-remove events, and failure-induced removal. The core finds the slot by base bdev, marks `remove_scheduled`, quiesces the RAID bdev when online and removal is tolerated, updates superblock slot state to missing or failed, resets the base before removal when possible, removes base channels across all RAID channels, releases/ closes the base descriptor, unquiesces the RAID bdev, decrements operational count, and deconfigures the RAID if it can no longer satisfy its module constraint. If a rebuild process is active, removal may stop the process first or continue if enough operational bases remain and the removed base is not the target.

Resize events locate the affected base, update its observed block count, call the level-specific `resize()` hook when present, notify front-end block count changes, update superblock base sizes and RAID size, and rewrite the superblock.

Deletion marks all bases removal-scheduled, optionally clears superblocks on all configured bases, then deconfigures/unregisters or frees the RAID if no bases remain. The destruct path runs on the app thread, stops any module-specific resources, closes bases during shutdown or scheduled removal, unregisters the I/O device, and frees the object once no configured bases remain.

The background process framework is generic but currently models rebuild. It allocates a process with a target base, a window size derived from `process_window_size_kb`, a pool of up to 16 DMA process requests, optional bandwidth throttling from `process_max_bandwidth_mb_sec`, and a dedicated SPDK thread. Starting a process installs process channel state across all existing RAID channels, then creates the process thread. The process repeatedly quiesces an LBA range, submits RAID-level process requests, waits for all blocks in the window to complete, advances the processed offset in every channel, unquiesces the window, and repeats. On success it writes superblock slot state back to configured. On failure it removes the target base. Finish actions let unregister/removal callbacks wait for the process to stop.

Superblock discovery is integrated with `examine_disk`. If a bdev has DIF enabled, the code skips superblock probing and only tries pending non-superblock configurations. Otherwise it opens the bdev read-only, reads/parses the superblock, creates a RAID from the newest valid superblock when needed, resolves base slots by UUID, configures this and other currently present member bdevs by UUID aliases, and handles newer/lower sequence numbers. If no valid superblock exists, it attempts to match the bdev against RAID objects configured without superblocks.

The file also emits config JSON for process options and for non-superblock RAID bdevs, detailed info JSON including process progress and base slot state, forwards memory-domain discovery when the RAID-level module supports it, registers tracepoints for RAID I/O start/done, and logs under `bdev_raid`. Key invariants are app-thread ownership for configuration/destruction, uniform base geometry, correct `num_base_bdevs_discovered` and operational counts, no front-end access to process target until rebuild completion, and consistent superblock sequence/state updates.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid.h -->
# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid.h

This internal header defines the RAID bdev core data model, RAID-level module interface, I/O helpers, superblock format, and process option API used by all files in `module/bdev/raid`.

`struct raid_base_bdev_info` is the per-slot state for a base device: owning RAID, configured name/UUID, descriptor, data offset/size, removal/configuration callbacks, observed block count, app-thread channel, configured/process-target/failed flags, and removal scheduling state. `struct raid_bdev` is the RAID object: generic `spdk_bdev`, self descriptor, global list link, base slot array, strip geometry, state, base counts, RAID level, module pointer/private data, superblock buffers, active background process, and configure/destroy callbacks.

`struct raid_bdev_io` is the per-front-end-I/O context stored in SPDK bdev I/O driver context. It tracks logical offset/length, iovs, type, memory domain, metadata, wait queue entry, RAID channel, child completion counters/status, module-private data, optional custom completion, and split-state used when an active process divides an I/O into processed and unprocessed ranges.

The RAID-level module contract is `struct raid_bdev_module`. Each module declares its RAID level, minimum base count, optional base-removal tolerance constraint, memory-domain and DIF support flags, and callbacks for `start`, optional asynchronous `stop`, read/write submission, optional null-payload submission, optional module I/O channel, optional resize, and process request submission. `RAID_MODULE_REGISTER()` installs a module at constructor time.

The header declares core lifecycle APIs for create/delete/add/remove/find, string conversions, info JSON writing, module registration, I/O completion and queue helpers, channel accessors, process request completion, I/O initialization, and base-failure signaling. Inline wrappers for read/write/unmap/flush add each base slot's `data_offset`; the write wrapper also remaps DIX reference tags when enabled.

The superblock layout is fixed-size-header plus variable base array. The signature is `SPDKRAID`, version is `1.0`, the base member record is statically asserted to 64 bytes, and the header to 256 bytes. The maximum superblock length is constrained to fit below the minimum 1 MiB RAID data offset. Base superblock states include missing, configured, failed, and spare. Public superblock helpers allocate/free/init/write/clear/read superblocks.

`struct spdk_raid_bdev_opts` exposes background process tunables: process window size in KiB and max bandwidth in MiB/sec. `raid_bdev_get_opts()` and `raid_bdev_set_opts()` are used by the RPC layer and config JSON.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid_rpc.c

This file implements JSON-RPC methods for managing RAID bdevs.

`bdev_raid_get_bdevs` decodes a required `category` state selector, iterates `g_raid_bdev_list`, and emits RAID objects whose state matches the requested category or `all`. Each object includes name, UUID, and the shared `raid_bdev_write_info_json()` output, which includes strip size, state, level, superblock flag, base counts, process progress, and base slot details.

`bdev_raid_create` decodes `name`, optional `strip_size_kb`, `raid_level`, `base_bdevs`, optional `uuid`, and optional `superblock`. It rejects empty base names, then calls `raid_bdev_create()`. Creation is asynchronous; `rpc_bdev_raid_create_cb()` returns boolean true or a formatted error and frees the heap-decoded autogen context.

`bdev_raid_delete` decodes `name` and optional `clear_sb`, resolves the RAID object by name, then calls `raid_bdev_delete()`. Completion is asynchronous through `bdev_raid_delete_done()`, which logs failures and returns JSON boolean true on success.

`bdev_raid_add_base_bdev` decodes a base bdev name and RAID bdev name, resolves the RAID object, and calls `raid_bdev_add_base_bdev()`. This is the RPC entry point for replacing/re-adding members, potentially triggering rebuild in the core. `bdev_raid_remove_base_bdev` decodes a base bdev name, opens it read-only long enough to get the `spdk_bdev *`, calls `raid_bdev_remove_base_bdev()`, closes the descriptor, and reports async completion through `rpc_bdev_raid_remove_base_bdev_done()`.

`bdev_raid_set_options` decodes optional background process tunables. It first loads current options, overlays any provided fields, calls `raid_bdev_set_opts()`, and returns a boolean. It is registered for both startup and runtime.

The file mostly delegates validation to the RAID core and autogen decoders. Error conventions use negative errno-style RPC codes for many domain errors and JSON-RPC parse/internal codes for decode failures depending on handler.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid_sb.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid_sb.c

This file implements RAID superblock allocation, initialization, CRC validation, loading, writing, and clearing.

`raid_bdev_alloc_superblock()` allocates a DMA-zeroed buffer large enough for the maximum superblock length aligned to the bdev block size. `raid_bdev_free_superblock()` frees the main superblock plus any separate I/O buffer or metadata buffer used for interleaved/separate metadata formats.

`raid_bdev_init_superblock()` fills signature, version, UUID, RAID name, RAID size, data block size, RAID level, strip size, number of base bdevs, and base descriptors. Each configured base record stores UUID, data offset, data size, configured state, and slot number. `raid_bdev_sb_update_crc()` zeroes and recalculates CRC32C over the declared length; `raid_bdev_sb_check_crc()` recalculates without permanently changing the stored CRC.

Read-side parsing starts by reading enough blocks for the fixed superblock header. `raid_bdev_parse_superblock()` validates signature, declared length, CRC, supported major version, warns on newer minor version, and verifies base slot numbers. If the declared length exceeds the current read buffer but is within maximum bounds, it returns `-EAGAIN`; `raid_bdev_read_sb_remainder()` reallocates and reads the remaining bytes. For interleaved metadata bdevs, the read callback compacts data portions out of full block+metadata records before parsing.

`raid_bdev_load_base_bdev_superblock()` allocates a read context, opens a DMA buffer sized to the fixed header in device block units, submits `spdk_bdev_read()`, and returns the parsed superblock pointer only for the lifetime of the callback. Invalid signature/CRC/version are reported as `-EINVAL`, which callers use as "no valid RAID superblock" in examine paths.

Write-side I/O uses `raid_bdev_write_sb_ctx` to fan out writes to all configured, non-removing base bdevs. `raid_bdev_alloc_sb_io_buf()` prepares a write buffer: interleaved metadata gets a separate full-block buffer with data packed at each block start; non-interleaved writes use `raid_bdev->sb` directly and allocate a separate metadata buffer when the bdev has separate metadata. `raid_bdev_write_superblock()` increments the sequence number, updates the CRC, packs interleaved buffers if necessary, and submits `spdk_bdev_write_blocks_with_md()` to each base. `-ENOMEM` queues on the base bdev wait queue and resumes from the saved submitted index.

`raid_bdev_clear_superblock()` zeroes the prepared superblock I/O buffers and writes zeros to the superblock area on all configured bases. All write/clear calls assert they run on the SPDK app thread and call the supplied completion after every base slot is accounted for. The code treats skipped unconfigured/removing bases as successful fanout entries.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/bdev_raid_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/concat.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/concat.c

This file implements the concatenated RAID level. It exposes multiple base bdev data regions as one logical bdev by laying each base range after the previous one, without striping or redundancy.

`concat_start()` allocates a `concat_block_range` array in `raid_bdev->module_private`. For each base slot it rounds data size down to a multiple of strip size, records the logical start and length, updates total block count, and stores the rounded size back into the base info. The resulting RAID block count is the sum of all rounded base sizes. The RAID bdev advertises `optimal_io_boundary = strip_size` and `split_on_optimal_io_boundary = true`, so normal read/write requests should not cross module-imposed boundaries.

`concat_submit_rw_request()` finds the base range containing `raid_io->offset_blocks`, computes the physical base LBA relative to that range, and submits a single `raid_bdev_readv_blocks_ext()` or `raid_bdev_writev_blocks_ext()` with memory domain and metadata options propagated. `-ENOMEM` queues the original RAID I/O for later resubmission on the selected base bdev; other submission errors complete the RAID I/O failed.

Flush and unmap can span multiple concatenated base ranges. `concat_submit_null_payload_request()` identifies the first and last affected base indices, initializes the expected child count, and submits range-specific flush/unmap operations across the involved bases. It tracks already submitted base I/Os for `-ENOMEM` resumption and uses `raid_bdev_io_complete_part()` to complete once all involved bases finish.

`concat_stop()` frees the range table synchronously. The registered module requires at least one base bdev, supports memory domains, and supplies start/stop/read-write/null-payload hooks. It has no redundancy and no resize hook in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/concat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid0.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/raid0.c

This file implements RAID0 striping for the SPDK RAID bdev core. It maps logical strips round-robin across base bdevs, supports DIF/DIX, forwards read/write I/O, handles flush/unmap ranges that touch multiple disks, and resizes when the smallest base data region changes.

`raid0_start()` finds the minimum base data size, rounds it down to a strip-size multiple, stores that rounded size into every base slot, and sets RAID block count to rounded per-base size times the number of bases. Multi-base RAID0 advertises strip size as the optimal I/O boundary and requests splitting on that boundary, so normal read/write requests are expected to fit within one strip. Single-base RAID0 disables split-on-boundary.

`raid0_submit_rw_request()` computes the logical start strip, verifies the request does not span a strip boundary when more than one base exists, maps to physical disk index and disk LBA, and submits a single read or write to the selected base. Extended I/O options propagate memory domain and metadata. Writes verify DIX reference tags against the RAID logical offset before remapping/writing; reads verify base metadata in completion and the core later remaps reference tags back for the parent. `-ENOMEM` queues for resubmission; unexpected submission failures assert and complete failed.

Null-payload range operations can cross stripes. `_raid0_get_io_range()` summarizes the affected strip range, start/end disk, offsets inside first/last strips, and number of disks involved. `_raid0_split_io_range()` calculates each disk-local offset and length. `raid0_submit_null_payload_request()` loops across involved disks from start disk, submits unmap or flush for each disk-local range, tracks submitted count for wait-queue resume, and completes the parent when all child I/Os finish.

`raid0_resize()` recomputes the rounded minimum data size from live base descriptors, calculates the new RAID block count, calls `spdk_bdev_notify_blockcnt_change()` when changed, and updates every base slot data size. The module registers minimum base count one, memory-domain support, DIF support, read/write and null-payload hooks, and resize support.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid0.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid1.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/raid1.c

This file implements RAID1 mirroring. It supports degraded operation with at least one operational base, read load balancing, mirrored writes/flushes/unmaps, read-error recovery by reading another mirror and rewriting the failed mirror, resize to the smallest live base size, and rebuild through the core background-process framework.

Module-private state is `raid1_info`, which owns the parent RAID pointer and is registered as a separate SPDK I/O device. Each RAID1 module channel has a flexible array of outstanding read-block counters, one per base. `raid1_channel_next_read_base_bdev()` chooses the configured base channel with the fewest outstanding read blocks, and read submit/completion increments/decrements that counter.

Read I/O is sent to one selected mirror. On read completion failure, `raid1_read_other_base_bdev()` tries remaining mirrors, skipping missing channels and the failed original. If another mirror succeeds, `raid1_correct_read_error()` writes the successfully read data back to the original failed mirror. If that corrective write fails, the original base is marked failed but the user read still completes successfully. If all mirrors fail, the original failed base is marked failed and the user read completes failed.

Write I/O is submitted to all configured mirror channels. Missing channels are counted as failed child completions, but the default status is set to failed and any successful child completion changes the aggregate status to success because it differs from the default. Failed writes call `raid_bdev_fail_base_bdev()` for the base that reported failure. The same fanout pattern is used for flush and unmap through `raid1_submit_null_payload_request()`.

`raid1_start()` allocates module-private state, sets every base data size to the smallest base data size, sets RAID block count to that minimum, stores module private data, and registers the RAID1 module I/O device with enough context space for all read counters. `raid1_stop()` unregisters that module I/O device asynchronously and calls `raid_bdev_module_stop_done()` from the unregister callback, so it returns false to the core.

Rebuild support is implemented via the module `submit_process_request` hook. `raid1_submit_process_request()` initializes an embedded RAID read I/O for the process window and sets a custom completion callback. The read uses normal RAID1 mirror selection over the processed channel map, and on success `raid1_process_submit_write()` writes the buffer to the process target channel. Completion reports block-window status back to the core with `raid_bdev_process_request_complete()`.

`raid1_resize()` computes the smallest live base capacity after data offset, notifies a RAID block count change if needed, and updates all slot data sizes. The module registers RAID level 1, minimum two bases, a constraint of at least one operational base, memory-domain support, start/stop, read/write/null-payload hooks, module I/O channel creation, process request support, and resize support. It does not declare DIF support, so the core rejects DIF-enabled base bdevs for RAID1.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid1.c -->