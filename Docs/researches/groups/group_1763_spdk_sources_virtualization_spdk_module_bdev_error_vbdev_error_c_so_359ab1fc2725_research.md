# Group Research: group_1763_spdk_sources_virtualization_spdk_module_bdev_error_vbdev_error_c_so_359ab1fc2725

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error.c -->
# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error.c

## Purpose
Implements SPDK's test-oriented error-injection virtual bdev. It wraps an existing bdev as `EE_<base>` and can inject failures, NVMe status failures, NOMEM, pending I/O, or data corruption for selected I/O types.

## Main Entry Points
- `vbdev_error_create()` records requested configuration and attempts to construct an error partition over the base bdev.
- `vbdev_error_delete()` unregisters the named error bdev.
- `vbdev_error_inject_error()` updates per-I/O-type injection rules.
- `vbdev_error_resume_pending()` clears pending injection counts and resubmits held I/O.
- `vbdev_error_examine()` creates configured error bdevs when their base bdevs are examined.
- `vbdev_error_config_json()` emits replayable `bdev_error_create` RPC config.

## Internal Mechanics
Each `error_disk` is a `spdk_bdev_part` with an `error_vector` indexed by bdev I/O type up to RESET. Each `error_channel` tracks in-flight I/O and a queue of pending injected I/O. `vbdev_error_get_error_type()` only injects READ, WRITE, UNMAP, and FLUSH, waits until `io_inflight >= error_qd`, and atomically decrements `error_num`.

The request path handles RESET specially by iterating all channels and aborting `pending_ios`. Failure injection completes immediately with normal bdev, NVMe, or NOMEM status. Pending injection queues the bdev I/O context without submitting to the base. Corrupt-data injection XORs one byte at `corrupt_offset`: writes are corrupted before forwarding, while reads are corrupted after successful base completion. Normal and corrupt I/O are forwarded through `spdk_bdev_part_submit_request_ext()`.

Configuration is maintained separately in `g_error_config` so create requests can survive base-bdev absence and be replayed during examine. Hotremove delegates to `spdk_bdev_part_base_hotremove()`.

## Dependencies
Uses SPDK bdev module and partition helpers, JSON config writers, UUID handling, pthread mutexes, atomics, and SPDK TAILQ/channel iteration utilities.

## Risks and Notes
`opts->io_type` is used as an array index for the targeted case; callers must pass either the special all/reset values or a valid bdev I/O type. Pending I/O lifetime depends on reset/resume paths removing the stored driver context exactly once. `vbdev_error_resume_pending()` sends resubmit messages to `spdk_get_thread()` from the channel-iteration callback, so thread context matters when reasoning about resubmission ordering.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error.h -->
# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error.h

## Purpose
Declares the private/public interface for the error-injection bdev module.

## Main Contents
- `spdk_delete_error_complete`, the async delete callback type.
- `vbdev_error_create()` and `vbdev_error_delete()` for lifecycle management.
- `struct vbdev_error_inject_opts`, carrying I/O type, error type, NVMe status fields, injection count, queue-depth threshold, and corruption settings.
- `vbdev_error_inject_error()` for configuring injection behavior.
- `vbdev_error_resume_pending()` for releasing I/O held by pending injection.

## Dependencies
Includes SPDK standard headers, bdev API, public error module definitions, and UUID definitions.

## Risks and Notes
The header exposes raw numeric fields matching RPC-generated decode values, so validation is mostly in callers and the implementation. `vbdev_error_inject_error()` takes a mutable `char *name` even though it treats the name as read-only.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error_rpc.c

## Purpose
Exposes JSON-RPC methods for creating, deleting, configuring, and resuming SPDK error-injection bdevs.

## Main Entry Points
- `bdev_error_create` decodes `base_name` and optional `uuid`, then calls `vbdev_error_create()`.
- `bdev_error_delete` decodes `name`, calls `vbdev_error_delete()`, and completes asynchronously.
- `bdev_error_inject_error` decodes the injection target and behavior, validates NVMe status parameters, builds `vbdev_error_inject_opts`, and calls `vbdev_error_inject_error()`.
- `bdev_error_resume_pending` resolves the named bdev and calls `vbdev_error_resume_pending()`.

## Internal Mechanics
The RPC layer relies on generated autogen context structs and decode helpers for error I/O type and error type strings. The default injection count is one. NVMe status code type/status code must be specified only for NVMe failure injection; non-NVMe injection rejects nonzero NVMe status fields.

## Dependencies
Uses SPDK JSON-RPC, string/error helpers, logging, `vbdev_error.h`, and `spdk_internal/rpc_autogen.h`.

## Risks and Notes
Resume uses `spdk_bdev_get_by_name()` and passes the resulting bdev pointer to the module; it does not open a descriptor. Error responses mix SPDK JSON-RPC internal errors for decode failures with errno-style module errors for operational failures.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/error/vbdev_error_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/ftl/Makefile

## Purpose
Builds the SPDK FTL bdev module library.

## Main Contents
The makefile sets `SPDK_ROOT_DIR`, includes SPDK common/lib make fragments, declares shared-object version `8.0`, adds `lib/ftl` to include paths, compiles `bdev_ftl.c` and `bdev_ftl_rpc.c`, names the library `bdev_ftl`, and uses `spdk_blank.map`.

## Dependencies
Depends on the SPDK make infrastructure and the FTL library headers.

## Risks and Notes
This is a thin build declaration; source membership and the extra FTL include path are the main maintenance points.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.c -->
# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.c

## Purpose
Wraps `spdk_ftl_dev` as an SPDK bdev. It handles FTL module initialization, bdev creation/deletion, deferred creation when base devices are absent, I/O dispatch, stats/properties helpers, and JSON configuration.

## Main Entry Points
- `bdev_ftl_create_bdev()` opens base/cache bdevs, allocates an `ftl_bdev`, and starts `spdk_ftl_dev_init()`.
- `bdev_ftl_delete_bdev()` validates the named bdev belongs to the FTL module, configures fast shutdown, and unregisters it.
- `bdev_ftl_defer_init()` stores a copied FTL config for later examine-time creation.
- `bdev_ftl_unmap()`, `bdev_ftl_get_stats()`, `bdev_ftl_get_properties()`, and `bdev_ftl_set_property()` run management actions on an existing FTL bdev.
- Module callbacks initialize/finalize the FTL library and examine deferred init entries.

## Internal Mechanics
I/O support is limited to READ, WRITE, UNMAP, and FLUSH. Reads first acquire a bdev buffer, then call `spdk_ftl_readv()`. Writes and unmaps call the matching FTL vector APIs. Flush completes successfully without forwarding. FTL completion return codes map `0` to success, `-EAGAIN`/`-ENOMEM` to bdev NOMEM, and other errors to failed.

Creation keeps descriptors for both base and cache bdevs so the underlying devices stay open. `bdev_ftl_create_cb()` queries FTL attributes/config, fills bdev geometry, UUID, optimal I/O boundary, and registers the bdev. On partial failure after FTL device creation, it disables fast shutdown and frees the FTL device asynchronously before reporting the original error.

Management actions share `struct bdev_ftl_action`, which opens the named bdev, verifies module ownership, stores callback state, and closes the descriptor on completion.

## Dependencies
Uses SPDK bdev, thread/env/JSON/string utilities, `spdk/ftl.h`, and internal FTL stats structures from `ftl_core.h`.

## Risks and Notes
`bdev_ftl_create_bdev()` unconditionally opens `conf->cache_bdev`; callers/config defaults must provide a usable cache bdev string. Deferred init iterates one entry per examine callback and removes an entry once creation is attempted on a present base. The generic action helper invokes the callback synchronously on setup failure, so RPC callers must tolerate immediate completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.h -->
# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.h

## Purpose
Declares the internal FTL bdev control interface shared by the core FTL bdev module and its RPC implementation.

## Main Contents
- `struct ftl_bdev_info` returns the created bdev name and UUID.
- `struct rpc_ftl_stats_ctx` carries an open FTL descriptor, JSON-RPC request, and `struct ftl_stats`.
- `ftl_bdev_init_fn` is the async create callback type.
- Prototypes cover create, delete, deferred init, unmap, get stats, get properties, and set property.

## Dependencies
Includes SPDK bdev module and FTL APIs plus `ftl_core.h` for stats.

## Risks and Notes
The header couples RPC context directly to core module declarations through `rpc_ftl_stats_ctx`, so changes to stats reporting affect both layers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl_rpc.c

## Purpose
Provides JSON-RPC methods for FTL bdev lifecycle, unmap, statistics, and runtime properties.

## Main Entry Points
- `bdev_ftl_create` decodes FTL config, applies defaults, sets create mode when UUID is null, checks name conflicts, and starts or defers creation.
- `bdev_ftl_delete` unregisters an FTL bdev with optional fast shutdown.
- `bdev_ftl_unmap` submits an FTL management unmap range.
- `bdev_ftl_get_stats` returns per-stat-type read/write/error counters.
- `bdev_ftl_get_properties` delegates JSON property output to the FTL library.
- `bdev_ftl_set_property` sets a named property value.

## Internal Mechanics
Create initializes `spdk_ftl_conf` from defaults, then overlays RPC parameters. Successful create returns an object containing `name` and `uuid`; deferred create returns a string noting deferred creation. Stats output iterates all `FTL_STATS_TYPE_MAX` entries and emits named objects for user, compaction, GC, metadata base, metadata cache, and L2P counters.

## Dependencies
Uses SPDK JSON-RPC, bdev module utilities, string/log helpers, generated RPC autogen contexts, and `bdev_ftl.h`.

## Risks and Notes
Create treats `-ENODEV` specially as deferrable but reports most other failures as JSON-RPC internal errors. Stats context owns dynamically allocated memory and an FTL bdev descriptor that is closed by the shared action helper.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/gpt/Makefile

## Purpose
Builds the SPDK GPT bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `gpt.c` and `vbdev_gpt.c`, sets `LIBNAME = bdev_gpt`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends only on the SPDK make system and source-local GPT module files.

## Risks and Notes
This file is purely build glue; adding RPC support or additional GPT helpers would require updating `C_SRCS`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/gpt.c -->
# File Research: sources/virtualization/spdk/module/bdev/gpt/gpt.c

## Purpose
Parses and validates GPT metadata from a bdev-read buffer, including the protective MBR, GPT header, partition-entry array location, and CRC checks.

## Main Entry Points
- `gpt_parse_mbr()` validates the protective MBR at LBA 0.
- `gpt_parse_partition_table()` validates the current primary or secondary GPT header and partition table.

## Internal Mechanics
Parsing is controlled by `gpt->parse_phase`. Primary parsing expects the header at LBA 1 and partition entries at the header-provided LBA within the front buffer. Secondary parsing expects the header at the last LBA and maps the partition array relative to the end of the loaded tail buffer.

Header validation checks header size bounds, header CRC with the CRC field zeroed, GPT signature, expected `my_lba`, and usable-LBA range. Partition validation limits entries to 128, requires SPDK's expected partition-entry struct size, locates the array, and validates the array CRC.

Protective MBR validation requires the MBR signature, a GPT protective partition entry, start LBA 1, and size either total sectors minus one or `0xFFFFFFFF`.

## Dependencies
Uses `spdk/gpt_spec.h`, SPDK endian helpers, CRC32, event/log headers, and `gpt.h`.

## Risks and Notes
The parser intentionally supports at most 128 GPT entries and one exact entry size. It mutates the in-buffer header CRC field while computing the checksum and restores it. Many validation failures are logged at debug level for probe-style use.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/gpt.h -->
# File Research: sources/virtualization/spdk/module/bdev/gpt/gpt.h

## Purpose
Defines the GPT module's internal data model, constants, GUIDs, parse phases, and parser prototypes.

## Main Contents
The header defines the current SPDK GPT partition type GUID, the deprecated old GUID that preserves an off-by-one sizing behavior, a 32 KiB GPT read buffer size, GUID comparison macro, parse-phase enum, and `struct spdk_gpt` fields for buffer state, LBA geometry, parsed header, and partition entries.

## Dependencies
Includes SPDK GPT spec and logging headers.

## Risks and Notes
`REGISTER_GUID_DEPRECATION` conditionally registers the old GUID deprecation in exactly one compilation unit. Consumers of `struct spdk_gpt` must set `parse_phase`, buffer, sector size, and total sector fields before parsing.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/vbdev_gpt.c -->
# File Research: sources/virtualization/spdk/module/bdev/gpt/vbdev_gpt.c

## Purpose
Implements the GPT virtual bdev module. It examines bdevs for SPDK GPT partitions and exposes each matching partition as a `spdk_bdev_part`.

## Main Entry Points
- `vbdev_gpt_examine()` screens bdev geometry and starts GPT reads.
- `vbdev_gpt_read_gpt()` creates base context and reads the primary GPT window.
- `gpt_bdev_complete()` parses MBR/primary GPT and falls back to secondary GPT if needed.
- `gpt_read_secondary_table_complete()` parses secondary GPT and creates partition bdevs.
- `vbdev_gpt_submit_request()` forwards partition I/O to the base bdev, acquiring buffers for reads.

## Internal Mechanics
`gpt_base` owns the parser buffer, a bdev part base, the partition list, and a temporary channel used only during table reads. Created GPT partition bdevs are named `<base>p<N>` with one-based partition indices, carry the partition unique GUID as bdev UUID, and expose JSON info containing base name, offset, table GUID, partition type GUID, unique GUID, and UTF-16LE partition name.

Only partitions with SPDK's current type GUID or deprecated old type GUID are exposed. The old GUID deliberately subtracts one block from the partition size to preserve compatibility with historical layouts. Partitions outside the GPT usable LBA range are ignored.

I/O forwarding uses `spdk_bdev_part_submit_request()`. On `-ENOMEM`, the request is queued with `spdk_bdev_queue_io_wait()` and resubmitted later. Memory domain support is forwarded from the base bdev unless DIF reference-tag checking is enabled, because bdev_part must touch metadata in that case.

## Dependencies
Uses SPDK bdev module/partition helpers, env/thread/RPC/string utilities, endian helpers, and parser functions from `gpt.c`.

## Risks and Notes
The module only examines bdevs with at least two blocks and block size divisible by 512. If no partitions are created, it frees the part-base context after examine completion. Secondary GPT fallback reads the last `gpt->buf_size` bytes; unusual layouts must fit the module's buffer assumptions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/gpt/vbdev_gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/iscsi/Makefile

## Purpose
Builds the SPDK iSCSI bdev module library.

## Main Contents
Declares shared-object version `8.0`, adds `lib/bdev` to include paths, suppresses warning-as-error behavior for CentOS 7 libiscsi inline declarations, compiles `bdev_iscsi.c` and `bdev_iscsi_rpc.c`, names the library `bdev_iscsi`, and uses `spdk_blank.map`.

## Dependencies
Depends on SPDK make infrastructure and external libiscsi headers/libraries supplied elsewhere in the build.

## Risks and Notes
The `-Wno-error` is an environment compatibility workaround and should not hide module-specific warnings unintentionally.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.c -->
# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.c

## Purpose
Implements an SPDK bdev backed by a remote iSCSI LUN using libiscsi. It manages asynchronous connection setup, SCSI inquiry/capacity discovery, I/O translation, polling, timeout service, resize detection, and bdev lifecycle.

## Main Entry Points
- `create_iscsi_disk()` parses the iSCSI URL, creates a libiscsi context, starts async login, and queues a connection request.
- `delete_iscsi_disk()` unregisters an iSCSI bdev.
- `bdev_iscsi_get_opts()` and `bdev_iscsi_set_opts()` manage global timeout settings.
- `bdev_iscsi_submit_request()` routes bdev I/O to the owning iSCSI service thread.
- Module init/fini register config JSON behavior and clear outstanding connection requests.

## Internal Mechanics
Connection setup is a staged state machine driven by `iscsi_bdev_conn_poll()`: async connect, logical block provisioning inquiry, optional block limits inquiry, READ CAPACITY(16), then `create_iscsi_lun()`. Successful creation registers an SPDK bdev with geometry from READ CAPACITY and UNMAP capabilities from inquiry pages.

The first I/O channel establishes `lun->main_td` and starts pollers for libiscsi fd service and timeout checks. Later I/O submitted from other SPDK threads is sent to `main_td`; completion is sent back to the original submitting thread if needed. A no-main-channel poller keeps servicing the libiscsi context while no regular I/O channel exists.

READ maps to READ(16), WRITE to WRITE(16), FLUSH to SYNCHRONIZE CACHE(16), UNMAP to SCSI UNMAP with at most one descriptor, and RESET to an async LUN reset task management function. Command callbacks complete with SCSI status and sense data. Unit attention for capacity change triggers READ CAPACITY(16), notifies block-count growth if larger, and retries the failed I/O.

## Dependencies
Uses SPDK bdev/thread/fd/env/JSON/string utilities, libiscsi (`iscsi/iscsi.h`, `iscsi/scsi-lowlevel.h`), POSIX poll, pthread mutexes, and SCSI/iSCSI protocol constants.

## Risks and Notes
Thread affinity is central: libiscsi service and request submission are serialized on `main_td`, with mutex-protected channel-count transitions. `bdev_iscsi_resize()` only accepts growth, not shrink. UNMAP supports only one descriptor, so requests larger than `max_unmap` are rejected despite splitting calculations. Connection request cleanup is delayed until after `iscsi_service()` unwinds, using `req->status` as a lifecycle marker.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.h -->
# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.h

## Purpose
Declares the iSCSI bdev module control interface and option structure.

## Main Contents
- `struct spdk_bdev_iscsi_opts` stores timeout seconds and derived timeout poller period.
- Delete and create callback typedefs.
- `create_iscsi_disk()` starts creation of a bdev from a name, iSCSI URL, and initiator IQN.
- `delete_iscsi_disk()` unregisters a named iSCSI bdev.
- `bdev_iscsi_get_opts()` and `bdev_iscsi_set_opts()` manage global module options.

## Dependencies
Includes SPDK bdev declarations.

## Risks and Notes
The warning in the create API is important: credentials embedded in iSCSI URLs can appear in configuration dumps.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi_rpc.c

## Purpose
Exposes JSON-RPC methods for iSCSI bdev options, creation, and deletion.

## Main Entry Points
- `bdev_iscsi_set_options` updates timeout seconds at startup or runtime.
- `bdev_iscsi_create` decodes name, initiator IQN, and URL, then calls `create_iscsi_disk()`.
- `bdev_iscsi_delete` decodes name and calls `delete_iscsi_disk()`.

## Internal Mechanics
Create completion maps positive libiscsi/SCSI statuses to JSON-RPC invalid-params errors, negative errno values to stringified errors, and success to the created bdev name. Delete completion returns boolean true on success.

## Dependencies
Uses `bdev_iscsi.h`, SPDK JSON-RPC, string/log helpers, and generated RPC autogen contexts.

## Risks and Notes
The options setter contains a branch for `-EPERM`, but the current `bdev_iscsi_set_opts()` implementation always returns zero after updating derived timeout period. Decode failures are reported as JSON-RPC internal errors rather than invalid params.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/lvol/Makefile

## Purpose
Builds the SPDK logical-volume bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `vbdev_lvol.c` and `vbdev_lvol_rpc.c`, names the library `bdev_lvol`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on the SPDK make infrastructure and lvol/blob/bdev headers used by the sources.

## Risks and Notes
This build unit contains both core lvol logic and the RPC surface; no separate RPC library is declared.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.c -->
# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.c

## Purpose
Implements the SPDK logical-volume bdev module. It maps blobstore lvol stores and lvol blobs to bdevs, handles lvstore load/create/unload/destroy, lvol create/snapshot/clone/resize/delete/rename/read-only operations, I/O forwarding, external snapshot support, shallow copy, hotplug, and asynchronous module shutdown.

## Main Entry Points
- `vbdev_lvs_create_ext()` and `vbdev_lvs_create()` create lvstores on base bdevs.
- `vbdev_lvs_unload()` and `vbdev_lvs_destruct()` unload or destroy lvstores.
- `vbdev_lvol_create()`, `vbdev_lvol_create_snapshot()`, `vbdev_lvol_create_clone()`, and `vbdev_lvol_create_bdev_clone()` create lvol bdevs from blobs, snapshots, or external-snapshot bdevs.
- `vbdev_lvol_destroy()`, `vbdev_lvol_rename()`, `vbdev_lvol_resize()`, and `vbdev_lvol_set_read_only()` mutate existing lvols.
- `vbdev_lvs_examine_disk()` loads lvstores discovered on base bdevs.
- `vbdev_lvs_examine_config()` handles external snapshot hotplug.
- `vbdev_lvol_shallow_copy()` and `vbdev_lvol_set_external_parent()` implement external-copy/parent operations.

## Internal Mechanics
`g_spdk_lvol_pairs` tracks loaded `lvol_store_bdev` pairs. Lookup helpers refuse lvstores with `removal_in_progress`, preventing new operations while unload/destroy is active. Creating an lvstore builds a blobstore bdev over the base bdev, initializes `spdk_lvs_opts`, sets external snapshot creation callback, claims the base bdev for the lvol module, and inserts the pair.

Each lvol bdev is a `struct lvol_bdev` whose public bdev name is `lvol->unique_id` and whose alias is `<lvs_name>/<lvol_name>`. Geometry is derived from blob cluster count, blobstore cluster size, and I/O unit size. The module forwards reads, writes, unmaps, and write-zeroes through blob I/O APIs and supports seek-data/seek-hole from blob allocation state. Writes, unmaps, and write-zeroes are hidden for read-only blobs.

Destroy/unload paths are asynchronous. Lvstore destroy recursively deletes deletable lvols, checks for circular clone dependencies, unregisters lvol bdevs, closes blobs, and finally unloads or destroys the blobstore. During global fini, `g_shutdown_started` allows the last lvol close to unload its lvstore and remove the registry entry.

External snapshot support validates esnap IDs as lower-case UUID strings, opens and claims the referenced bdev as a blobstore device when present, and otherwise returns a degraded dummy `spdk_bs_dev` that reports degraded state and no usable I/O. Missing esnap devices are registered for later hotplug; when the external bdev appears, clone trees are walked and bdevs are created for no-longer-degraded lvols.

Memory domain reporting includes base bdev domains and, for external snapshot clones, domains from the esnap bdev when it is available. Shallow copy creates and claims a destination bs_dev, starts `spdk_lvol_shallow_copy()`, then destroys the external device wrapper on completion.

## Dependencies
Uses SPDK bdev module APIs, blob/blobstore/lvol APIs, blob_bdev, UUID/string/log helpers, and internal lvolstore declarations.

## Risks and Notes
Alias rename happens before `spdk_lvol_rename()` completes; if the lvol rename later fails, alias state may already have changed. Degraded lvols do not register bdevs until their external snapshot is available, so RPC deletion has fallback lookup paths by UUID and `lvs/lvol` name. Clone deletion prevents removing an lvol with more than one clone relation. The degraded dummy bs_dev contains assert-failing I/O callbacks by design and must not be used for real I/O.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.h -->
# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.h

## Purpose
Declares the lvol bdev module's internal control API and shared data structures for lvstore/lvol operations.

## Main Contents
- `struct lvol_store_bdev` links an `spdk_lvol_store` to its base bdev, current request, removal flag, and global list entry.
- `struct lvol_bdev` embeds the public bdev and links it to its lvol and lvstore pair.
- Prototypes cover lvstore create/destroy/unload/rename/lookup, lvol create/snapshot/clone/external clone/resize/read-only/rename/destroy, bdev-to-lvol lookup, external snapshot device creation, shallow copy, and setting an external parent.

## Dependencies
Includes SPDK lvol, bdev module, blob_bdev, and internal lvolstore headers.

## Risks and Notes
This header exposes many asynchronous operations with callback contracts but no explicit ownership annotations; callers must follow the implementation's callback/lifetime rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol_rpc.c

## Purpose
Implements the JSON-RPC surface for logical volume stores and logical volumes, including snapshots, clones, external parents, shallow-copy progress, resize, inflate/decouple, listing, and deletion.

## Main Entry Points
- Lvstore RPCs: `bdev_lvol_create_lvstore`, `bdev_lvol_rename_lvstore`, `bdev_lvol_delete_lvstore`, `bdev_lvol_get_lvstores`, and `bdev_lvol_grow_lvstore`.
- Lvol RPCs: `bdev_lvol_create`, `bdev_lvol_snapshot`, `bdev_lvol_clone`, `bdev_lvol_clone_bdev`, `bdev_lvol_rename`, `bdev_lvol_resize`, `bdev_lvol_set_read_only`, `bdev_lvol_delete`, and `bdev_lvol_get_lvols`.
- Parent/copy RPCs: `bdev_lvol_inflate`, `bdev_lvol_decouple_parent`, `bdev_lvol_start_shallow_copy`, `bdev_lvol_check_shallow_copy`, `bdev_lvol_set_parent`, and `bdev_lvol_set_parent_bdev`.

## Internal Mechanics
`vbdev_get_lvol_store_by_uuid_xor_name()` enforces that callers identify a lvstore by exactly one of UUID or name. Most lvol operations resolve a bdev by name, verify it belongs to the lvol module via `vbdev_lvol_get_from_bdev()`, and then invoke the core asynchronous helper.

Size arguments are exposed in MiB and converted to bytes before calling lvol APIs. Listing lvstores reports UUID, name, base bdev, total/free clusters, I/O unit size, cluster size, and max growable size. Listing lvols reports alias, UUID, name, thin/snapshot/clone/esnap/degraded flags, allocated clusters, and parent lvstore identity; only lvols with nonzero refcount are listed.

Shallow copy tracking uses a process-local incrementing operation ID and a linked list of status entries. Start returns the operation ID immediately. Check reports copied/total cluster counts and state; completed or errored entries are removed when checked.

Deletion has extra degraded-lvol lookup logic: it first tries normal bdev name/alias lookup, then UUID lookup, then splitting `lvs_name/lvol_name` in-place.

## Dependencies
Uses SPDK JSON-RPC, bdev lookup APIs, string/log helpers, generated RPC autogen contexts, and `vbdev_lvol.h`.

## Risks and Notes
Several decode failures are reported as JSON-RPC internal errors. Shallow-copy status is retained until checked after completion or error, so clients must poll to free status entries. `bdev_lvol_delete` mutates the decoded `name` string when parsing `lvs/lvol` degraded lookup.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/malloc/Makefile

## Purpose
Builds the SPDK malloc bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `bdev_malloc.c` and `bdev_malloc_rpc.c`, sets `LIBNAME = bdev_malloc`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on SPDK make infrastructure and malloc bdev source files.

## Risks and Notes
This makefile is straightforward build glue for an in-memory bdev module.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.c -->
# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.c

## Purpose
Implements SPDK's in-memory malloc bdev. It allocates DMA-capable backing memory, supports optional metadata and DIF/DIX protection information, uses the accel framework for data movement, and exposes read/write/flush/reset/unmap/write-zeroes/zcopy/abort/compare/copy operations.

## Main Entry Points
- `create_malloc_disk()` validates options, allocates backing memory and optional metadata memory, initializes PI if requested, registers the bdev, and inserts it into `g_malloc_disks`.
- `delete_malloc_disk()` unregisters a named malloc bdev.
- `bdev_malloc_submit_request()` dispatches each bdev I/O type.
- Module init/fini register/unregister the shared I/O device used for malloc channels.

## Internal Mechanics
Each `malloc_disk` owns the public bdev plus `malloc_buf` and optional separate metadata buffer. Each channel owns an accel I/O channel and a completion poller. Synchronous completions are queued in `completed_tasks` and drained by `malloc_completion_poller()`.

Reads, writes, compares, copies, unmaps, and write-zeroes are implemented with accel copy/compare/fill operations. Read with a null iov base maps the caller directly to the backing buffer and optional metadata buffer, then completes without copying. ZCOPY start similarly exposes the backing buffer. Abort always fails.

Protection information support verifies incoming data on writes when metadata is visible, verifies stored data before hidden-metadata reads, verifies read buffers after reads with visible metadata, and regenerates PI after unmap/write-zeroes. Initial PI is generated over the full disk when DIF is enabled. Supported metadata sizes are 0, 8, 16, 32, 64, and 128 bytes.

Config JSON emits replayable `bdev_malloc_create` entries with geometry, UUID, optimal boundary, metadata, DIF, PI format, and NUMA ID. Memory domain support is broad when DIF is disabled and disabled when DIF is enabled.

## Dependencies
Uses SPDK bdev module APIs, DMA allocation, accel framework, DIF/DIX helpers, endian/string/log utilities, memory domains, pollers, and NUMA enumeration.

## Risks and Notes
Large allocations are pinned DMA memory and can fail for size, alignment, NUMA, or hugepage availability. `physical_block_size` must be 512-byte aligned but is not defaulted in this file if callers pass zero. Accel sequence failure handling intentionally maps sequence `-ENOMEM` to `-EFAULT` at finish to prevent bdev-layer retry of an already failed sequence.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.h -->
# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.h

## Purpose
Declares the malloc bdev creation/deletion interface and option structure.

## Main Contents
- `spdk_delete_malloc_complete`, the async delete callback type.
- `struct malloc_bdev_opts`, carrying name, UUID, block count/size, physical block size, optimal I/O boundary, metadata size/layout, DIF type, DIF location, PI format, and NUMA ID.
- `create_malloc_disk()` and `delete_malloc_disk()` prototypes.

## Dependencies
Includes SPDK standard and bdev module declarations.

## Risks and Notes
The `name` field is a mutable `char *` but is duplicated during creation. Callers must fully initialize defaults such as physical block size and NUMA ID before calling `create_malloc_disk()`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc_rpc.c

## Purpose
Provides JSON-RPC methods to create and delete malloc bdevs.

## Main Entry Points
- `bdev_malloc_create` decodes geometry, metadata, DIF, UUID, optimal boundary, and NUMA options, calls `create_malloc_disk()`, and returns the created bdev name.
- `bdev_malloc_delete` decodes the bdev name and calls `delete_malloc_disk()`.

## Internal Mechanics
The RPC layer builds `struct malloc_bdev_opts` directly from the generated decode context. `numa_id` defaults to `SPDK_ENV_NUMA_ID_ANY`. The core create function duplicates the optional name, so the decoded string can be freed after the call.

## Dependencies
Uses `bdev_malloc.h`, SPDK JSON-RPC, string/log helpers, and generated RPC autogen contexts.

## Risks and Notes
`physical_block_size` is optional and defaults to zero in the decode context unless the generator provides another default; the core create path rejects non-512-aligned values but accepts zero alignment-wise, which can create a bdev with zero physical block size if not normalized elsewhere.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/null/Makefile

## Purpose
Builds the SPDK null bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `bdev_null.c` and `bdev_null_rpc.c`, sets `LIBNAME = bdev_null`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on SPDK make infrastructure and the null bdev source files that are outside this group's listed sources.

## Risks and Notes
Only the makefile is in this work item. The actual null bdev behavior is defined in `bdev_null.c` and `bdev_null_rpc.c`, which are referenced here but not part of this grouped file list.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/Makefile -->