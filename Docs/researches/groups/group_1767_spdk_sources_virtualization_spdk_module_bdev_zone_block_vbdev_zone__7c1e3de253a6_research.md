# Group Research: group_1767_spdk_sources_virtualization_spdk_module_bdev_zone_block_vbdev_zone__7c1e3de253a6

Scope: `Docs/research_subset_a.md` / `sources/virtualization/spdk` subset A virtualization storage modules.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.c -->
# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.c

Implements the `bdev_zoned_block` virtual bdev module, which presents a regular block bdev as a zoned block device with in-memory zone metadata.

Key elements:
- Registers `bdev_zoned_block` with init/fini/config/examine callbacks.
- Maintains pending config entries in `g_bdev_configs` and registered virtual devices in `g_bdev_nodes`.
- Models each zone with `struct block_zone`, `spdk_bdev_zone_info`, and a per-zone spinlock.
- Supports zone info, zone management, read, write, and zone append I/O.
- Enforces sequential write pointer semantics for writes and appends.
- Resets zones by updating in-memory state and optionally issuing base-bdev unmap.
- Creates virtual bdevs when the base bdev appears during examine or RPC-driven creation.
- Handles base bdev hotremove by unregistering dependent virtual bdevs.

Dependencies:
- SPDK bdev module APIs, bdev zone API, UUID generation, JSON config output, IO channel APIs.
- `vbdev_zone_block.h` exposes create/delete entry points used by RPC code.

Research notes:
- The wrapper does not persist zone state; zones initialize as full with write pointer at zone end.
- Zone size is rounded up to a power of two from `zone_capacity`; indexing uses `zone_shift`.
- Some base-bdev capacity may be truncated when it does not align to virtual zone layout.
- `GET_ZONE_INFO` is handled internally, but `zone_block_io_type_supported()` does not advertise `SPDK_BDEV_IO_TYPE_GET_ZONE_INFO`, which is notable.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.h -->
# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.h

Declares the public interface for the zone block virtual bdev module.

Key elements:
- `vbdev_zone_block_create()` creates a zoned virtual bdev over a named base bdev with zone capacity and optimal open zone count.
- `vbdev_zone_block_delete()` unregisters a named virtual bdev asynchronously through an SPDK bdev unregister callback.

Dependencies:
- Includes SPDK bdev and bdev module headers for callback and bdev types.

Research notes:
- This header is intentionally narrow; RPC code is the primary local consumer.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block_rpc.c

Adds JSON-RPC control for the zone block virtual bdev.

Key elements:
- Registers runtime RPC `bdev_zone_block_create`.
- Decodes `name`, `base_bdev`, `zone_capacity`, and `optimal_open_zones`.
- Calls `vbdev_zone_block_create()` and returns the created name on success.
- Registers runtime RPC `bdev_zone_block_delete`.
- Decodes `name`, calls `vbdev_zone_block_delete()`, and completes the JSON-RPC request from the unregister callback.

Dependencies:
- Uses SPDK JSON-RPC, string/error helpers, generated RPC context free helpers, and `vbdev_zone_block.h`.

Research notes:
- Creation parameters mirror `zone_block_config_json()` output in the implementation file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/blob/Makefile -->
# File Research: sources/virtualization/spdk/module/blob/Makefile

Top-level build dispatcher for SPDK blob modules.

Key elements:
- Sets `SPDK_ROOT_DIR` two levels up.
- Includes `mk/spdk.common.mk`.
- Builds only the `bdev` subdirectory through `DIRS-y = bdev`.
- Uses `spdk.subdirs.mk` for `all` and `clean`.

Dependencies:
- Delegates actual library build to `module/blob/bdev/Makefile`.

Research notes:
- This file is directory orchestration only; no C sources are compiled here directly.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/blob/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/blob/bdev/Makefile -->
# File Research: sources/virtualization/spdk/module/blob/bdev/Makefile

Builds the blobstore bdev adapter library.

Key elements:
- Defines shared object version `SO_VER := 14`, `SO_MINOR := 0`.
- Compiles `blob_bdev.c`.
- Produces library `blob_bdev`.
- Uses `spdk_blob_bdev.map` as the export map.

Dependencies:
- Includes SPDK common and library make fragments.

Research notes:
- This is the build unit for `spdk_bdev_create_bs_dev()` and related blobstore block-device adapter functions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/blob/bdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/blob/bdev/blob_bdev.c -->
# File Research: sources/virtualization/spdk/module/blob/bdev/blob_bdev.c

Implements an `spdk_bs_dev` backend over an SPDK bdev.

Key elements:
- `struct blob_bdev` embeds `spdk_bs_dev` and tracks base bdev, descriptor, write mode, refs, and lock.
- Implements read/write, readv/writev, extended memory-domain I/O options, write zeroes, unmap, and copy.
- Queues failed `-ENOMEM` bdev submissions through `spdk_bdev_queue_io_wait()` and resubmits later.
- Handles bdev I/O completions by translating success to blobstore callback status.
- Implements channel creation/destruction using bdev I/O channels with refcounted lifetime.
- `spdk_bs_bdev_claim()` claims the bdev descriptor with read/write claim semantics.
- `spdk_bdev_create_bs_dev()` opens a named bdev and initializes the blobstore device wrapper.
- `spdk_bdev_update_bs_blockcnt()` refreshes blobstore-visible block count.

Dependencies:
- SPDK blobstore, bdev, bdev module, thread, endian, and logging APIs.

Research notes:
- Unmap is optional; if unsupported, it completes successfully because blobstore does not require unmap to zero data.
- Copy support is installed only when the base bdev supports `SPDK_BDEV_IO_TYPE_COPY`.
- Range validation asserts if CoW/esnap ranges exceed the underlying bdev.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/blob/bdev/blob_bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/env_dpdk/Makefile -->
# File Research: sources/virtualization/spdk/module/env_dpdk/Makefile

Builds the DPDK environment RPC helper library.

Key elements:
- Compiles `env_dpdk_rpc.c`.
- Produces `env_dpdk_rpc`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Links into SPDK module build infrastructure through `spdk.lib.mk`.

Research notes:
- This library exposes runtime diagnostics for DPDK environment memory stats.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/env_dpdk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/env_dpdk/env_dpdk_rpc.c -->
# File Research: sources/virtualization/spdk/module/env_dpdk/env_dpdk_rpc.c

Registers a runtime JSON-RPC method to dump DPDK memory statistics.

Key elements:
- `env_dpdk_get_mem_stats` rejects parameters.
- Writes memory stats to `/tmp/spdk_mem_dump.txt`.
- Calls `spdk_env_dpdk_dump_mem_stats()`.
- Returns a JSON object containing the dump filename.

Dependencies:
- SPDK JSON-RPC and DPDK environment wrapper APIs.

Research notes:
- The output path is fixed, so repeated calls overwrite the same file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/env_dpdk/env_dpdk_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/Makefile -->
# File Research: sources/virtualization/spdk/module/event/Makefile

Top-level build dispatcher for event subsystem modules.

Key elements:
- Builds only the `subsystems` directory.
- Uses SPDK common and subdirs make fragments.
- Defines `all` and `clean` phony targets.

Dependencies:
- Delegates subsystem library selection to `module/event/subsystems/Makefile`.

Research notes:
- This is directory orchestration, not a direct source build unit.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/Makefile

Selects and orders SPDK event subsystem module builds.

Key elements:
- Always includes bdev, accel, scheduler, iscsi, nvmf, scsi, vmd, sock, iobuf, and keyring.
- Adds Linux-only `nbd`, optional Linux `ublk`, optional vhost, optional vfio-user, and optional fsdev.
- Encodes subsystem build dependencies through `DEPDIRS-*`.
- Notes dependency ordering should mirror dependency declarations in C subsystem files.

Dependencies:
- Uses SPDK subdirectory build infrastructure.

Research notes:
- The declared `DEPDIRS-nvmf` omits keyring and sock even though `nvmf_tgt.c` declares those runtime subsystem dependencies.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/accel/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/accel/Makefile

Builds the event accel subsystem library.

Key elements:
- Compiles `accel.c`.
- Produces `event_accel`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Depends on SPDK common and library make fragments.

Research notes:
- Runtime dependency on iobuf is declared in the corresponding C file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/accel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/accel/accel.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/accel/accel.c

Registers the SPDK accel framework as an event subsystem.

Key elements:
- Initializes via `spdk_accel_initialize()`.
- Finishes asynchronously via `spdk_accel_finish()`.
- Exposes config JSON through `spdk_accel_write_config_json`.
- Registers subsystem name `accel`.

Dependencies:
- Depends on `iobuf` through `SPDK_SUBSYSTEM_DEPEND(accel, iobuf)`.

Research notes:
- The subsystem simply bridges framework lifecycle callbacks into the event subsystem init/fini chain.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/accel/accel.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/bdev/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/bdev/Makefile

Builds the event bdev subsystem library.

Key elements:
- Compiles `bdev.c`.
- Produces `event_bdev`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- This is the build wrapper for block device framework lifecycle integration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/bdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/bdev/bdev.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/bdev/bdev.c

Registers the SPDK bdev framework as an event subsystem.

Key elements:
- Initializes bdev through `spdk_bdev_initialize()` and completion callback.
- Finishes through `spdk_bdev_finish()`.
- Emits bdev subsystem config JSON through `spdk_bdev_subsystem_config_json()`.
- Registers subsystem name `bdev`.

Dependencies:
- Declares dependencies on accel, keyring, vmd, sock, and iobuf.

Research notes:
- Provides the central block-storage lifecycle dependency for NBD, NVMe-oF, ublk, vhost block, and SCSI consumers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/bdev/bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/fsdev/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/fsdev/Makefile

Builds the event fsdev subsystem library.

Key elements:
- Compiles `fsdev.c`.
- Produces `event_fsdev`.
- Uses shared object version `3.0`.
- Uses the blank SPDK map file.

Dependencies:
- Included only when `CONFIG_FSDEV` selects the fsdev subsystem from the parent Makefile.

Research notes:
- Provides event-framework lifecycle glue for filesystem devices.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/fsdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/fsdev/fsdev.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/fsdev/fsdev.c

Registers the SPDK fsdev framework as an event subsystem.

Key elements:
- Initializes through `spdk_fsdev_initialize()`.
- Finishes through `spdk_fsdev_finish()`.
- Emits fsdev config JSON through `spdk_fsdev_subsystem_config_json()`.
- Registers subsystem name `fsdev`.

Dependencies:
- Uses SPDK fsdev, env, thread, and init APIs.

Research notes:
- No explicit subsystem dependencies are declared in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/fsdev/fsdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/Makefile

Builds the event iobuf subsystem library.

Key elements:
- Compiles `iobuf.c` and `iobuf_rpc.c`.
- Produces `event_iobuf`.
- Uses shared object version `5.0`.
- Uses the blank SPDK map file.

Dependencies:
- Provides both lifecycle integration and RPC option/stat support.

Research notes:
- Many other event subsystems depend on iobuf for buffer-pool availability.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf.c

Registers SPDK iobuf as an event subsystem and writes iobuf config JSON.

Key elements:
- Initializes via `spdk_iobuf_initialize()`.
- Finishes asynchronously via `spdk_iobuf_finish()`.
- Writes `iobuf_set_options` config with small/large pool counts, buffer sizes, and NUMA option.
- Registers subsystem name `iobuf`.

Dependencies:
- Uses SPDK iobuf, bdev, thread, init, and JSON APIs.

Research notes:
- This subsystem has no declared dependencies but is a dependency for accel, bdev, nvmf, and ublk.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf_rpc.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf_rpc.c

Adds startup/runtime JSON-RPC support for iobuf options and stats.

Key elements:
- Registers startup RPC `iobuf_set_options`.
- Decodes optional pool counts, buffer sizes, and NUMA enable flag.
- Uses an X-macro field list shared between RPC context and `spdk_iobuf_opts`.
- Includes a static assert that `spdk_iobuf_opts` remains size 40.
- Registers runtime RPC `iobuf_get_stats`.
- Serializes per-module small and large pool cache/main/retry/cache-size stats.

Dependencies:
- SPDK iobuf option/stat APIs, JSON-RPC, string helpers, generated RPC context definitions.

Research notes:
- The static assert intentionally forces updates when `spdk_iobuf_opts` grows.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iscsi/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/iscsi/Makefile

Builds the event iSCSI subsystem library.

Key elements:
- Adds `-I$(SPDK_ROOT_DIR)/lib` to CFLAGS.
- Compiles `iscsi.c`.
- Produces `event_iscsi`.
- Uses shared object version `8.0`.

Dependencies:
- Uses blank SPDK map file and library make fragment.

Research notes:
- Runtime dependencies are declared in `iscsi.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iscsi/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iscsi/iscsi.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/iscsi/iscsi.c

Registers the SPDK iSCSI target as an event subsystem.

Key elements:
- Initializes via `spdk_iscsi_init()`.
- Finishes via `spdk_iscsi_fini()`.
- Writes config JSON through `spdk_iscsi_config_json()`.
- Registers subsystem name `iscsi`.

Dependencies:
- Declares dependencies on `scsi` and `sock`.

Research notes:
- Uses asynchronous init/fini completion callbacks to advance the subsystem chain.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/iscsi/iscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/keyring/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/keyring/Makefile

Builds the event keyring subsystem library.

Key elements:
- Compiles `keyring.c`.
- Produces `event_keyring`.
- Uses shared object version `3.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built via standard SPDK library make infrastructure.

Research notes:
- Separate backend keyring modules live under `module/keyring`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/keyring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/keyring/keyring.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/keyring/keyring.c

Registers the SPDK keyring framework as an event subsystem.

Key elements:
- Initializes through `spdk_keyring_init()`.
- Cleans up through `spdk_keyring_cleanup()`.
- Writes config JSON by wrapping `spdk_keyring_write_config()` in an array.
- Registers subsystem name `keyring`.

Dependencies:
- Uses SPDK keyring and init APIs.

Research notes:
- This subsystem is a dependency for bdev and nvmf when keys are needed for encrypted storage or authentication.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/keyring/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nbd/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nbd/Makefile

Builds the event NBD subsystem library.

Key elements:
- Compiles `nbd.c`.
- Produces `event_nbd`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Included only from the parent subsystem Makefile on Linux.

Research notes:
- Runtime dependency on bdev is declared in the C file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nbd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nbd/nbd.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nbd/nbd.c

Registers the SPDK NBD service as an event subsystem.

Key elements:
- Initializes through `spdk_nbd_init()`.
- Finishes asynchronously through `spdk_nbd_fini()`.
- Writes config JSON through `spdk_nbd_write_config_json()`.
- Registers subsystem name `nbd`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- Bridges SPDK block devices to Linux NBD lifecycle under the event framework.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nbd/nbd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/Makefile

Builds the event NVMe-oF subsystem library.

Key elements:
- Compiles `nvmf_rpc.c` and `nvmf_tgt.c`.
- Produces `event_nvmf`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Runtime dependencies are declared in `nvmf_tgt.c`.

Research notes:
- This build unit contains both startup RPC configuration and the target lifecycle state machine.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/event_nvmf.h -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/event_nvmf.h

Defines shared NVMe-oF event subsystem configuration types and globals.

Key elements:
- `struct spdk_nvmf_admin_passthru_conf` controls which admin commands may be passed through.
- `struct spdk_nvmf_tgt_conf` wraps target options plus admin passthrough config.
- Externs expose `g_spdk_nvmf_tgt_conf`, `g_spdk_nvmf_tgt`, and `g_poll_groups_mask`.

Dependencies:
- Includes SPDK nvmf, queue, init, and log headers.

Research notes:
- Shared by `nvmf_tgt.c` and `nvmf_rpc.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/event_nvmf.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_rpc.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_rpc.c

Implements startup JSON-RPC configuration for the NVMe-oF event target.

Key elements:
- Registers `nvmf_set_max_subsystems`, allowed only once when max is still zero.
- Decodes discovery filter strings such as `match_any`, `transport`, `address`, and `svcid`.
- Decodes and validates `poll_groups_mask` as a subset of the SPDK environment core mask.
- Registers `nvmf_set_config` for admin command passthrough, poll group mask, discovery filter, DHCHAP options, and duplicate host policy.
- Registers `nvmf_set_crdt` for CRDT values.

Dependencies:
- Uses shared globals from `event_nvmf.h`, SPDK cpuset, util, JSON-RPC, and generated RPC decoders.

Research notes:
- All three RPCs are startup RPCs, shaping target behavior before subsystem initialization.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_tgt.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_tgt.c

Implements the NVMe-oF event subsystem lifecycle and optional NVMe admin passthrough behavior.

Key elements:
- Defines a target state machine from create target through poll group creation, subsystem start, running, and shutdown cleanup.
- Initializes default target options, discovery filter, DHCHAP digest/group masks, duplicate host policy, and admin passthrough flags.
- Creates one poll group thread per enabled core or per configured poll-group mask.
- Creates the discovery subsystem and starts/stops/destroys all NVMe-oF subsystems.
- Stops listeners before destroying subsystems and poll groups during shutdown.
- Implements custom admin command handlers for identify, get log page, get/set features, sanitize, security send/receive, firmware update, NVMe-MI, and vendor-specific commands.
- Passes allowed admin commands to a single-namespace bdev that supports `SPDK_BDEV_IO_TYPE_NVME_ADMIN`.
- Fixes selected identify/log-page data by merging NVMe drive data with SPDK NVMe-oF controller data.
- Writes config JSON for `nvmf_set_config`, DHCHAP options, duplicate host policy, poll group mask, and target config.

Dependencies:
- SPDK nvmf target APIs, bdev, thread, NVMe command structures, subsystem init/fini, and USDT probes.
- Depends on bdev, keyring, sock, accel, and iobuf subsystems.

Research notes:
- Shutdown requested during initialization is deferred until the target reaches a stable state.
- Admin passthrough is deliberately limited to single-namespace subsystems and requires NVMe admin support on the namespace bdev.
- Security send/receive passthrough logs a warning about key exposure unless transport encryption is used.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_tgt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scheduler/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/scheduler/Makefile

Builds the event scheduler subsystem library.

Key elements:
- Compiles `scheduler.c`.
- Produces `event_scheduler`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- Separate scheduler implementations are under `module/scheduler`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scheduler/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scheduler/scheduler.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/scheduler/scheduler.c

Registers scheduler selection as an event subsystem.

Key elements:
- During init, defaults to the `static` scheduler if none is already selected.
- During fini, disables scheduler period and clears selected scheduler.
- Writes config JSON as `framework_set_scheduler` with scheduler name and optional period.
- Registers subsystem name `scheduler`.

Dependencies:
- SPDK scheduler APIs and internal event definitions.

Research notes:
- This file manages event-framework scheduler selection, not the balancing algorithm itself.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scheduler/scheduler.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scsi/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/scsi/Makefile

Builds the event SCSI subsystem library.

Key elements:
- Compiles `scsi.c`.
- Produces `event_scsi`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built via SPDK library make fragment.

Research notes:
- Runtime dependency on bdev is declared in the C source.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scsi/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scsi/scsi.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/scsi/scsi.c

Registers the SPDK SCSI layer as an event subsystem.

Key elements:
- Initializes through `spdk_scsi_init()`.
- Finishes through `spdk_scsi_fini()`.
- Registers subsystem name `scsi`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- This subsystem underpins iSCSI and vhost SCSI integration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/scsi/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/sock/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/sock/Makefile

Builds the event sock subsystem library.

Key elements:
- Compiles `sock.c`.
- Produces `event_sock`.
- Uses shared object version `7.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- Initializes socket implementations used by networked targets such as NVMe-oF and iSCSI.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/sock/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/sock/sock.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/sock/sock.c

Registers SPDK socket initialization as an event subsystem.

Key elements:
- Initializes socket implementations with interrupt mode status from `spdk_interrupt_mode_is_enabled()`.
- Allows default socket implementation override via `SPDK_SOCK_IMPL_DEFAULT`.
- Writes socket config JSON through `spdk_sock_write_config_json()`.
- Registers subsystem name `sock`.

Dependencies:
- SPDK sock module internals, init, thread, string, and log APIs.

Research notes:
- Fini immediately advances the subsystem chain; shutdown logic is owned by socket implementation modules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/sock/sock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/ublk/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/ublk/Makefile

Builds the event ublk subsystem library.

Key elements:
- Compiles `ublk.c`.
- Produces `event_ublk`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by the parent Makefile when Linux and `CONFIG_UBLK=y`.

Research notes:
- Runtime dependencies are bdev and iobuf.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/ublk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/ublk/ublk.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/ublk/ublk.c

Registers the SPDK ublk service as an event subsystem.

Key elements:
- Initializes through `spdk_ublk_init()`.
- Finishes asynchronously through `spdk_ublk_fini()`, with fallback completion if fini returns an error.
- Writes config JSON through `spdk_ublk_write_config_json()`.
- Registers subsystem name `ublk`.

Dependencies:
- Declares dependencies on `bdev` and `iobuf`.

Research notes:
- Provides Linux ublk integration for exposing SPDK bdevs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/ublk/ublk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/Makefile

Builds the vfio-user target event subsystem library.

Key elements:
- Compiles `vfu_tgt.c`.
- Produces `event_vfu_tgt`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by parent Makefile when `CONFIG_VFIO_USER` is enabled.

Research notes:
- Optional fsdev dependency is controlled in the C source by `SPDK_CONFIG_FSDEV`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/vfu_tgt.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/vfu_tgt.c

Registers the vfio-user target as an event subsystem.

Key elements:
- Initializes with `spdk_vfu_init()`.
- Finishes with `spdk_vfu_fini()`.
- Registers subsystem name `vfio_user_target`.

Dependencies:
- Declares dependencies on bdev and scsi.
- Adds dependency on fsdev when `SPDK_CONFIG_FSDEV` is defined.

Research notes:
- This subsystem exposes SPDK devices through vfio-user target infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/vfu_tgt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_blk/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_blk/Makefile

Builds the vhost block event subsystem library.

Key elements:
- Compiles `vhost_blk.c`.
- Produces `event_vhost_blk`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by the parent subsystem Makefile when vhost is enabled.

Research notes:
- Runtime dependency on bdev is declared in source.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_blk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_blk/vhost_blk.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_blk/vhost_blk.c

Registers SPDK vhost block as an event subsystem.

Key elements:
- Initializes through `spdk_vhost_blk_init()`.
- Finishes through `spdk_vhost_blk_fini()`.
- Writes config JSON through `spdk_vhost_blk_config_json()`.
- Registers subsystem name `vhost_blk`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- Provides block-device vhost target lifecycle integration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_blk/vhost_blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/Makefile

Builds the vhost SCSI event subsystem library.

Key elements:
- Compiles `vhost_scsi.c`.
- Produces `event_vhost_scsi`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by parent Makefile when vhost is enabled.

Research notes:
- Runtime dependency on SCSI is declared in the C source.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/vhost_scsi.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/vhost_scsi.c

Registers SPDK vhost SCSI as an event subsystem.

Key elements:
- Initializes through `spdk_vhost_scsi_init()`.
- Finishes through `spdk_vhost_scsi_fini()`.
- Writes config JSON through `spdk_vhost_scsi_config_json()`.
- Registers subsystem name `vhost_scsi`.

Dependencies:
- Declares dependency on `scsi`.

Research notes:
- Relies on the SCSI subsystem rather than directly on bdev.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/vhost_scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/Makefile -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/Makefile

Builds the VMD event subsystem library.

Key elements:
- Compiles `vmd.c` and `vmd_rpc.c`.
- Produces `event_vmd`.
- Uses shared object version `8.0`.
- Uses blank SPDK map file.

Dependencies:
- Provides both VMD lifecycle and RPC control.

Research notes:
- The VMD subsystem is disabled by default and enabled through startup RPC.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/event_vmd.h -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/event_vmd.h

Declares shared VMD event subsystem helpers.

Key elements:
- `vmd_subsystem_enable()` marks VMD enabled before subsystem init.
- `vmd_subsystem_is_enabled()` reports enable state.

Dependencies:
- Consumed by `vmd.c` and `vmd_rpc.c`.

Research notes:
- Minimal header for startup RPC to communicate enablement to subsystem init.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/event_vmd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/vmd.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/vmd.c

Registers VMD support as an event subsystem.

Key elements:
- Maintains global `g_enabled` and hotplug poller pointer.
- Initializes VMD only when enabled by startup RPC.
- Calls `spdk_vmd_init()` and registers a periodic hotplug monitor poller.
- Fini unregisters the poller, calls `spdk_vmd_fini()`, and advances fini chain.
- Writes config JSON containing `vmd_enable` when enabled.
- Registers subsystem name `vmd`.

Dependencies:
- SPDK VMD, poller, init, JSON, and logging APIs.

Research notes:
- Hotplug monitor runs every 1,000,000 microseconds when enabled.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/vmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/vmd_rpc.c -->
# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/vmd_rpc.c

Adds JSON-RPC control for VMD.

Key elements:
- Registers startup RPC `vmd_enable`.
- Registers runtime RPC `vmd_remove_device`, decoding a PCI address and calling `spdk_vmd_remove_device()`.
- Registers runtime RPC `vmd_rescan`, returning the number of devices found.
- Rejects remove/rescan requests when VMD is disabled.

Dependencies:
- Uses `event_vmd.h`, SPDK VMD, env, PCI address parsing, JSON-RPC, and generated RPC context helpers.

Research notes:
- Device removal and rescan require prior startup-time enablement.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/event/subsystems/vmd/vmd_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/Makefile -->
# File Research: sources/virtualization/spdk/module/fsdev/Makefile

Top-level build dispatcher for fsdev modules.

Key elements:
- Includes `aio` subdirectory only when `CONFIG_AIO_FSDEV=y`.
- Defines `all` and `clean` phony targets.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Delegates actual AIO fsdev library build to `module/fsdev/aio/Makefile`.

Research notes:
- fsdev module availability is compile-time configurable.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/Makefile -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/Makefile

Builds the AIO fsdev module.

Key elements:
- Compiles `fsdev_aio.c` and `fsdev_aio_rpc.c`.
- On Linux, compiles `linux_aio_mgr.c` and links `-laio`.
- On non-Linux, compiles POSIX `aio_mgr.c`.
- Produces `fsdev_aio`.
- Uses shared object version `3.0`.

Dependencies:
- Uses blank SPDK map file and standard SPDK library make infrastructure.

Research notes:
- Selects between Linux libaio and portable POSIX AIO manager implementations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.c -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.c

Implements the non-Linux/portable POSIX AIO manager used by fsdev AIO.

Key elements:
- Uses pools of `spdk_aio_mgr_io` and `spdk_aio_mgr_req`.
- Splits vector I/O into POSIX `aiocb` requests, with up to `REQS_PER_AIO` request objects per AIO.
- Submits with `aio_read()` or `aio_write()`.
- Supports cancellation through `aio_cancel()`.
- Polls in-flight requests with `aio_error()` and completes with `aio_return()`.
- Returns completed request and AIO objects to internal pools.
- Deletes only when no in-flight AIOs remain.

Dependencies:
- POSIX AIO, SPDK queue, util, and logging APIs.
- Interface declared in `aio_mgr.h`.

Research notes:
- Callback error values are positive errno-style values, later passed through fsdev completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.h -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.h

Declares the AIO manager abstraction for fsdev AIO.

Key elements:
- Forward declares `spdk_aio_mgr` and `spdk_aio_mgr_io`.
- Defines `fsdev_aio_done_cb`.
- Declares create, read, write, cancel, poll, and delete functions.

Dependencies:
- Includes SPDK stdinc and queue headers for shared types.

Research notes:
- Both POSIX AIO and Linux libaio implementations satisfy this interface.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.c -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.c

Implements an SPDK fsdev module backed by a local host filesystem.

Key elements:
- Defines file object and file handle structures wrapping file descriptors, directory state, parent/leaf relationships, refcounts, and locks.
- Creates an `aio_fsdev` rooted at a configured host path.
- Uses `O_PATH`, `openat`, `fstatat`, `linkat`, `renameat`, `unlinkat`, and `/proc/self/fd` to operate relative to tracked file descriptors.
- Provides fsdev handlers for mount, umount, lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, release, read, write, statfs, fsync, xattr operations, flush, directory operations, flock, create, abort, fallocate, and copy-file-range.
- Uses `spdk_aio_mgr` for asynchronous read/write and a poller per I/O channel.
- Has `skip_rw` mode that completes reads/writes without touching backing storage.
- Registers fsdev module `aio` with module init/fini and context size.
- Writes replayable config JSON through `fsdev_aio_create`.
- Exposes `spdk_fsdev_aio_get_default_opts()`, `spdk_fsdev_aio_create()`, and `spdk_fsdev_aio_delete()`.

Dependencies:
- SPDK fsdev module APIs, thread/poller APIs, AIO manager abstraction, POSIX filesystem APIs, xattr APIs, and generated config constants.

Research notes:
- Path traversal is constrained by safe single-component checks for mutating operations; lookup permits `.` and `..` for NFS-export behavior but maps root `..` to root.
- Creation temporarily switches effective uid/gid to request credentials.
- Extended attribute behavior is guarded by `xattr_enabled`; the create path logs that xattrs can only be enabled on Linux but returns the current `rc`, which is zero after prior setup, making that branch worth checking.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.h -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.h

Declares the public AIO fsdev module interface.

Key elements:
- `struct spdk_fsdev_aio_opts` contains xattr, writeback cache, max write, and skip read/write options.
- Defines async delete completion callback type.
- Declares default option population, create, and delete functions.

Dependencies:
- Includes SPDK fsdev module header.

Research notes:
- Used by RPC code and the module implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio_rpc.c -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio_rpc.c

Adds runtime JSON-RPC control for AIO fsdev instances.

Key elements:
- Registers `fsdev_aio_create`.
- Decodes `name`, `root_path`, optional xattr, writeback cache, max write, and skip read/write options.
- Seeds RPC defaults from `spdk_fsdev_aio_get_default_opts()`.
- Calls `spdk_fsdev_aio_create()` and returns the fsdev name.
- Registers `fsdev_aio_delete`.
- Calls `spdk_fsdev_aio_delete()` and completes via callback.

Dependencies:
- `fsdev_aio.h`, SPDK JSON-RPC, string helpers, and generated RPC context free helpers.

Research notes:
- RPC option names match config JSON emitted by `fsdev_aio_write_config_json()`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/linux_aio_mgr.c -->
# File Research: sources/virtualization/spdk/module/fsdev/aio/linux_aio_mgr.c

Implements the Linux libaio-backed AIO manager for fsdev AIO.

Key elements:
- Uses `io_context_t`, `iocb`, `io_submit`, `io_queue_run`, and `io_cancel`.
- Maintains a pool of `spdk_aio_mgr_io` objects and an in-flight list.
- Prepares `preadv` or `pwritev` requests and installs completion callback with `io_set_callback`.
- Completion removes AIO from in-flight, invokes fsdev callback, increments completion count, and returns object to pool.
- Poll returns busy when completions occurred.
- Delete asserts no in-flight operations and releases libaio context.

Dependencies:
- Linux libaio and SPDK queue/log/util APIs.
- Interface declared in `aio_mgr.h`.

Research notes:
- `io_submit()` success is treated as any nonzero result; libaio errors are negative, so callers should verify this handling against libaio conventions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/fsdev/aio/linux_aio_mgr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/Makefile -->
# File Research: sources/virtualization/spdk/module/keyring/Makefile

Top-level build dispatcher for keyring backends.

Key elements:
- Always builds `file`.
- Builds `linux` when `CONFIG_HAVE_KEYUTILS` is enabled.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Backend build files live under `module/keyring/file` and `module/keyring/linux`.

Research notes:
- Separates generic event keyring subsystem from concrete key storage providers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/Makefile -->
# File Research: sources/virtualization/spdk/module/keyring/file/Makefile

Builds the file-backed keyring module.

Key elements:
- Compiles `keyring.c` and `keyring_rpc.c`.
- Produces `keyring_file`.
- Uses shared object version `4.0`.
- Uses `spdk_keyring_file.map`.

Dependencies:
- Built via SPDK library make fragment.

Research notes:
- Provides persistent config JSON for file-backed keys.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/keyring.c -->
# File Research: sources/virtualization/spdk/module/keyring/file/keyring.c

Implements a keyring backend that reads key material from local files.

Key elements:
- Validates paths as absolute.
- Requires key files to have no group/other permission bits.
- Requires key files to be owned by the current user.
- Stores key context as the configured file path.
- Reads key material with `fopen()`/`fread()` after rechecking path metadata.
- Emits config JSON as `keyring_file_add_key` with name and path.
- Exposes `spdk_keyring_file_add_key()` and `spdk_keyring_file_remove_key()`.
- Registers keyring module `keyring_file`.

Dependencies:
- SPDK keyring module API, file key module header, logging, string, and util APIs.

Research notes:
- Key material is not cached by this backend; it is loaded from the file when requested.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/keyring_rpc.c -->
# File Research: sources/virtualization/spdk/module/keyring/file/keyring_rpc.c

Adds runtime JSON-RPC control for file-backed keyring keys.

Key elements:
- Registers `keyring_file_add_key`.
- Decodes `name` and `path`, calls `spdk_keyring_file_add_key()`, returns boolean success.
- Registers `keyring_file_remove_key`.
- Decodes `name`, calls `spdk_keyring_file_remove_key()`, returns boolean success.

Dependencies:
- SPDK JSON-RPC, string/util helpers, file keyring public API, generated RPC free helpers.

Research notes:
- Add uses relaxed JSON decode; remove uses standard object decode.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/file/keyring_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/Makefile -->
# File Research: sources/virtualization/spdk/module/keyring/linux/Makefile

Builds the Linux kernel keyring-backed module.

Key elements:
- Compiles `keyring.c` and `keyring_rpc.c`.
- Produces `keyring_linux`.
- Links `-lkeyutils`.
- Uses shared object version `3.0`.
- Uses blank SPDK map file.

Dependencies:
- Included only when keyutils support is configured.

Research notes:
- Provides integration with Linux session keyrings.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring.c -->
# File Research: sources/virtualization/spdk/module/keyring/linux/keyring.c

Implements a keyring backend over Linux kernel keyutils.

Key elements:
- Tracks enablement in `g_opts`.
- Finds keys with `request_key("user", name, NULL, KEY_SPEC_SESSION_KEYRING)`.
- Probes keys by adding SPDK keyring entries when Linux keys exist.
- Stores Linux key serial number in per-key context.
- Reads key material with `keyctl_read()`.
- Emits config JSON as `keyring_linux_set_options`.
- Initializes only when enabled; otherwise returns `-ENODEV`.
- Registers keyring module `linux`.

Dependencies:
- Linux keyutils, SPDK keyring, keyring module, logging, string, and util APIs.

Research notes:
- Removal is a no-op at the Linux keyutils level; SPDK removes the keyring registration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring_linux.h -->
# File Research: sources/virtualization/spdk/module/keyring/linux/keyring_linux.h

Declares Linux keyring module options and accessors.

Key elements:
- `struct keyring_linux_opts` contains `enable`.
- Declares `keyring_linux_set_opts()` and `keyring_linux_get_opts()`.

Dependencies:
- Includes SPDK stdinc for `bool`.

Research notes:
- Used by Linux keyring implementation and startup RPC code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring_linux.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring_rpc.c -->
# File Research: sources/virtualization/spdk/module/keyring/linux/keyring_rpc.c

Adds startup JSON-RPC control for Linux keyring backend options.

Key elements:
- Registers `keyring_linux_set_options`.
- Decodes optional `enable`.
- Seeds RPC request from current options.
- Calls `keyring_linux_set_opts()` and returns boolean success.

Dependencies:
- `keyring_linux.h`, SPDK JSON-RPC, string/util helpers, generated RPC context.

Research notes:
- Startup timing matters because backend initialization checks the enable option.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/keyring/linux/keyring_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/Makefile -->
# File Research: sources/virtualization/spdk/module/scheduler/Makefile

Top-level build dispatcher for scheduler modules.

Key elements:
- Always builds `dynamic`.
- Builds `dpdk_governor` and `gscheduler` only when `DPDK_POWER=y`.
- Emits a clean-time warning when DPDK power support is missing.
- Uses SPDK subdir build infrastructure.

Dependencies:
- DPDK power support gates frequency-governor-based scheduling modules.

Research notes:
- Dynamic scheduler can build without DPDK power; governor-dependent modules cannot.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dpdk_governor/Makefile -->
# File Research: sources/virtualization/spdk/module/scheduler/dpdk_governor/Makefile

Builds the DPDK power governor scheduler support library.

Key elements:
- Adds `$(ENV_CFLAGS)`.
- Compiles `dpdk_governor.c`.
- Produces `scheduler_dpdk_governor`.
- Uses shared object version `6.0`.

Dependencies:
- Requires DPDK power support as selected by parent Makefile.

Research notes:
- Provides frequency scaling operations consumed by schedulers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dpdk_governor/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dpdk_governor/dpdk_governor.c -->
# File Research: sources/virtualization/spdk/module/scheduler/dpdk_governor/dpdk_governor.c

Implements an SPDK governor backed by DPDK `rte_power`.

Key elements:
- Queries available and current core frequencies.
- Raises/lowers core frequency and sets min/max frequency.
- Reports core priority capabilities from DPDK power core capabilities.
- Dumps active DPDK power environment as JSON.
- Initializes by checking SMT coverage, selecting a supported DPDK power environment, initializing each core, and enabling turbo where supported.
- Deinitializes power management on all SPDK cores.
- Registers governor name `dpdk_governor`.

Dependencies:
- SPDK env/event/scheduler APIs and DPDK `rte_power` headers.

Research notes:
- Refuses initialization when the app core mask includes only part of an SMT sibling set.
- Handles DPDK header path differences around DPDK 24.11.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dpdk_governor/dpdk_governor.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dynamic/Makefile -->
# File Research: sources/virtualization/spdk/module/scheduler/dynamic/Makefile

Builds the dynamic scheduler module.

Key elements:
- Compiles `scheduler_dynamic.c`.
- Produces `scheduler_dynamic`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Always selected by parent scheduler Makefile.

Research notes:
- The scheduler can use the DPDK governor if available but is built independently.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dynamic/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dynamic/scheduler_dynamic.c -->
# File Research: sources/virtualization/spdk/module/scheduler/dynamic/scheduler_dynamic.c

Implements SPDK's dynamic thread scheduler.

Key elements:
- Tracks per-core busy/idle TSC, thread count, and isolation state.
- Uses configurable thresholds: `load_limit`, `core_limit`, and `core_busy`.
- Optionally selects `dpdk_governor` during init.
- Moves idle threads to the main scheduling core.
- Moves active threads to cores that can fit their load while respecting thread cpumasks and isolated cores.
- Switches unused cores to interrupt mode and wakes/sleeps cores through governor frequency controls.
- Adjusts main-core frequency based on whether busy threads remain elsewhere.
- Exposes JSON scheduler options through `set_opts()` and `get_opts()`.
- Registers scheduler name `dynamic`.

Dependencies:
- SPDK env, thread, scheduler, internal event, logging, JSON, and USDT probe APIs.

Research notes:
- The algorithm updates estimated core load as it virtually moves threads so later placement decisions see the adjusted state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/dynamic/scheduler_dynamic.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/gscheduler/Makefile -->
# File Research: sources/virtualization/spdk/module/scheduler/gscheduler/Makefile

Builds the governor-based scheduler module.

Key elements:
- Compiles `gscheduler.c`.
- Produces `scheduler_gscheduler`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Built only when parent Makefile detects DPDK power support.

Research notes:
- Depends on the `dpdk_governor` runtime selection path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/gscheduler/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/scheduler/gscheduler/gscheduler.c -->
# File Research: sources/virtualization/spdk/module/scheduler/gscheduler/gscheduler.c

Implements a simple governor-based scheduler that adjusts core frequency from load thresholds.

Key elements:
- Uses min, adjust, and max busy percentage thresholds.
- Selects `dpdk_governor` during init and clears governor on deinit.
- Calculates busy percentage from current busy/idle TSC.
- Considers SMT sibling busy percentage by taking the maximum among siblings.
- Sets core frequency min, down, up, or max based on load thresholds.
- Registers scheduler name `gscheduler`.

Dependencies:
- SPDK scheduler, governor, env, thread, and internal event APIs.

Research notes:
- This scheduler adjusts frequency only; it does not move threads between cores.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/scheduler/gscheduler/gscheduler.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/sock/Makefile -->
# File Research: sources/virtualization/spdk/module/sock/Makefile

Top-level build dispatcher for socket implementation modules.

Key elements:
- Always builds `posix`.
- On Linux, builds `uring` when `CONFIG_URING` is enabled.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Delegates implementation library builds to subdirectories.

Research notes:
- This file selects socket transport implementation modules, separate from the event sock subsystem.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/sock/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/sock/posix/Makefile -->
# File Research: sources/virtualization/spdk/module/sock/posix/Makefile

Builds the POSIX socket implementation module.

Key elements:
- Compiles `posix.c`.
- Produces `sock_posix`.
- Links `-lssl`.
- Uses shared object version `8.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- The listed group includes only this Makefile, not `posix.c`; it establishes POSIX socket module build metadata.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/sock/posix/Makefile -->