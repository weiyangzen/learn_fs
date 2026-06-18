# Group Research: group_1733_spdk_sources_virtualization_spdk_app_Makefile_sources_virtualizatio_cb2adf41f642

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/Makefile -->
# File Research: sources/virtualization/spdk/app/Makefile

## Purpose
Top-level SPDK application makefile. It selects which application subdirectories participate in `all` and `clean` builds and delegates recursive build behavior to SPDK's shared make infrastructure.

## Main Contents
- Sets `SPDK_ROOT_DIR` to the parent of `app`.
- Includes `mk/spdk.common.mk`.
- Adds app directories such as `trace`, `nvmf_tgt`, `iscsi_tgt`, `spdk_tgt`, `spdk_lspci`, NVMe tools, and optional apps.
- Omits `spdk_top` on Windows because curses is unsupported there.
- Adds `vhost` only when `CONFIG_VHOST` is enabled.
- Adds `spdk_dd` only on Linux.
- Adds `fio` only when `CONFIG_FIO_PLUGIN` is enabled.
- Includes `mk/spdk.subdirs.mk` for recursive targets.

## Dependencies
Depends on SPDK make variables from `spdk.common.mk`, especially `OS`, `CONFIG_VHOST`, and `CONFIG_FIO_PLUGIN`.

## Filesystem/Block Relevance
This makefile controls whether block-facing apps and tools such as NVMe-oF target, iSCSI target, fio plugins, `spdk_dd`, and NVMe inspection utilities are built.

## Risks and Notes
- Platform gating means some tools are intentionally absent from Windows or non-Linux builds.
- Actual compilation/link details live in each child makefile and SPDK shared make fragments.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/Makefile -->
# File Research: sources/virtualization/spdk/app/fio/Makefile

## Purpose
Recursive makefile for SPDK fio plugins. It builds both the direct NVMe fio plugin and the bdev fio plugin.

## Main Contents
- Sets `SPDK_ROOT_DIR` relative to `app/fio`.
- Includes `mk/spdk.common.mk`.
- Adds `nvme` and `bdev` subdirectories to `DIRS-y`.
- Delegates `all` and `clean` to `mk/spdk.subdirs.mk`.

## Dependencies
Uses SPDK's common and recursive subdirectory make infrastructure.

## Filesystem/Block Relevance
This file is the build entry point for fio engines used to benchmark SPDK block devices and SPDK NVMe paths.

## Risks and Notes
- It has no conditional logic itself; enablement is controlled by the parent `app/Makefile`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/Makefile -->
# File Research: sources/virtualization/spdk/app/fio/bdev/Makefile

## Purpose
Builds the `spdk_bdev` fio ioengine plugin from `fio_plugin.c`.

## Main Contents
- Includes SPDK common and module make fragments.
- Sets `FIO_PLUGIN := spdk_bdev`.
- Compiles `fio_plugin.c`.
- Links all SPDK bdev modules plus `event` and `event_bdev`.
- Includes `mk/spdk.fio.mk` for fio plugin build rules.

## Dependencies
Depends on `$(ALL_MODULES_LIST)`, SPDK event framework, event bdev support, and SPDK's fio plugin make fragment.

## Filesystem/Block Relevance
Produces the fio plugin that drives SPDK bdevs through the bdev layer, covering malloc, NVMe, file, zoned, and other configured bdev modules.

## Risks and Notes
- Linking `ALL_MODULES_LIST` makes the plugin broadly capable but dependent on configured module availability.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/bdev.json -->
# File Research: sources/virtualization/spdk/app/fio/bdev/bdev.json

## Purpose
Minimal SPDK JSON configuration for the bdev fio plugin.

## Main Contents
- Defines a single `bdev` subsystem configuration item.
- Creates malloc bdev `Malloc0`.
- Uses block size `512`.
- Uses `262144` blocks.

## Dependencies
Consumed by SPDK JSON/RPC configuration loading, specifically the `bdev_malloc_create` method.

## Filesystem/Block Relevance
Provides an in-memory block target for fio benchmarking without physical storage.

## Risks and Notes
- Capacity is fixed by the JSON values.
- It is suitable for testing plugin plumbing and memory-backed I/O, not persistence.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/bdev.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/bdev_zoned.json -->
# File Research: sources/virtualization/spdk/app/fio/bdev/bdev_zoned.json

## Purpose
SPDK JSON configuration for exercising fio against a zoned bdev stack.

## Main Contents
- Creates malloc bdev `Malloc0` with `2097152` blocks of size `512`.
- Creates zone block bdev `Zone0` on top of `Malloc0`.
- Sets `zone_capacity` to `262144`.
- Sets `optimal_open_zones` to `8`.

## Dependencies
Uses SPDK bdev RPC methods `bdev_malloc_create` and `bdev_zone_block_create`.

## Filesystem/Block Relevance
Provides a host-managed zoned block target for fio ZBD testing through the SPDK bdev fio plugin.

## Risks and Notes
- The zoned behavior is layered over volatile malloc storage.
- Zone geometry is static and intentionally small enough for local tests.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/bdev_zoned.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/fio_plugin.c -->
# File Research: sources/virtualization/spdk/app/fio/bdev/fio_plugin.c

## Purpose
Implements the `spdk_bdev` fio ioengine. It lets fio jobs issue read, write, trim, flush, zone append, zone report, and zone reset operations through SPDK's bdev layer.

## Main Entry Points
- `spdk_fio_setup()` validates fio thread mode, initializes SPDK once, expands `*` to all leaf bdevs, resolves file names to bdevs, and sets fio file sizes.
- `spdk_fio_init()` creates a per-fio-thread SPDK thread and opens bdev descriptors/channels.
- `spdk_fio_queue()` maps fio directions to `spdk_bdev_read()`, `spdk_bdev_write()`, `spdk_bdev_unmap()`, `spdk_bdev_flush()`, or `spdk_bdev_zone_append()`.
- `spdk_fio_getevents()` polls the SPDK thread until enough fio completions are available or timeout expires.
- `spdk_fio_report_zones()`, `spdk_fio_reset_wp()`, `spdk_fio_get_zoned_model()`, and `spdk_fio_get_max_open_zones()` provide fio ZBD integration when supported by the fio version.
- `spdk_fio_register()` and `spdk_fio_unregister()` register/unregister the fio engine.

## Internal Mechanics
A dedicated initialization/poll thread initializes SPDK env, loads JSON config, starts SPDK subsystems, optionally opens an RPC listener, and polls SPDK threads. Each fio worker gets a `spdk_fio_thread` with a SPDK thread, completion queue, and a list of opened bdev targets.

Synchronous calls that must run on the SPDK app thread use `spdk_fio_sync_run_oat()`, a condition-variable bridge that sends a message to the app thread and waits for completion. This is used for setup and some bdev capability queries.

I/O completion stores completed fio `io_u` pointers in the thread's `iocq`. `-ENOMEM` from bdev submission maps to `FIO_Q_BUSY`; other submission errors complete the fio I/O with an errno.

Zoned support converts SPDK bdev zone descriptors into fio `zbd_zone` structures, supports optional initial zone reset, and can replace writes with zone append when the target supports `SPDK_BDEV_IO_TYPE_ZONE_APPEND`.

## Options
Supports `spdk_conf`, `spdk_json_conf`, `spdk_mem`, `spdk_single_seg`, `log_flags`, `initial_zone_reset`, `zone_append`, `env_context`, and `spdk_rpc_listen_addr`.

## Dependencies
Depends on SPDK bdev, bdev zone, event/subsystem initialization, RPC, thread, env, DMA allocation, and fio plugin APIs. Conditional behavior depends on `FIO_IOOPS_VERSION`.

## Filesystem/Block Relevance
This is the primary fio bridge for benchmarking SPDK's generic block-device abstraction, including zoned bdevs and module-backed devices.

## Risks and Notes
- Requires fio `thread=1`.
- Fio daemon mode is rejected unless stdout/stderr are safely redirected to `/dev/null`.
- SPDK env is global and initialized once across fio jobs.
- The background poll loop is central to completions and app-thread message progress.
- Zoned callbacks are compiled only for sufficiently new fio versions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/bdev/fio_plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/nvme/Makefile -->
# File Research: sources/virtualization/spdk/app/fio/nvme/Makefile

## Purpose
Builds the direct SPDK NVMe fio plugin.

## Main Contents
- Sets `FIO_PLUGIN := spdk_nvme`.
- Compiles `fio_plugin.c`.
- Links socket modules, `nvme`, and `vmd`.
- Includes `mk/spdk.fio.mk`.

## Dependencies
Depends on SPDK socket modules, NVMe library, VMD library, common/module make fragments, and fio plugin make rules.

## Filesystem/Block Relevance
Builds the fio engine that bypasses SPDK bdev and drives NVMe namespaces directly.

## Risks and Notes
- Direct NVMe support differs from the bdev plugin: configuration is supplied through fio file names and plugin options rather than SPDK bdev JSON.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/nvme/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/fio/nvme/fio_plugin.c -->
# File Research: sources/virtualization/spdk/app/fio/nvme/fio_plugin.c

## Purpose
Implements fio's `spdk` ioengine for direct SPDK NVMe access. It parses fio file names as NVMe transport IDs, connects to controllers/namespaces, allocates I/O qpairs, and submits NVMe commands directly.

## Main Entry Points
- `spdk_fio_setup()` initializes SPDK env once, optionally initializes VMD/tracing, parses per-file transport IDs, probes/connects controllers, and discovers namespaces.
- `probe_cb()` applies host NQN, WRR, interrupt, and digest options to controller options.
- `attach_cb()` registers or reuses controllers, resolves namespace IDs, validates block sizes, configures PI and ZNS settings, and sets fio file size/type.
- `spdk_fio_open()` allocates an NVMe I/O qpair for a fio file.
- `spdk_fio_queue()` maps fio read/write/trim to NVMe read/write, SGL read/write, zone append, or dataset management commands.
- `spdk_fio_getevents()` round-robins qpairs and processes completions.
- ZNS callbacks implement fio zoned model, zone reporting, reset write pointer, and max-open-zone queries.
- FDP support exposes `fdp_fetch_ruhs()` for compatible fio versions.

## Internal Mechanics
Global controller state is shared under `g_mutex`, while each fio thread owns a list of `spdk_fio_qpair` objects and a completion queue. A separate pthread periodically processes admin completions for all connected controllers.

The plugin supports PCIe and NVMe-oF transport IDs. If a namespace is not specified, it uses the first active namespace. For PCIe addresses, it normalizes the PCI address string. For fabrics, it can derive or override host NQN.

I/O can use contiguous buffers or fio-provided SGL callbacks. The SGL path supports splitting by configured SGE size and optionally using bit bucket descriptors for read data. Trim maps to NVMe dataset management, with multi-range trim support when fio exposes it.

Protection information support configures NVMe PI flags, builds SPDK DIF/DIX contexts, generates PI for writes, verifies PI on reads, and supports both extended LBA and separate metadata modes.

ZNS support detects ZNS command-set namespaces, optionally resets all zones at initialization, maps fio zone reports from NVMe ZNS reports, and optionally converts writes to zone append.

## Options
Includes WRR, interrupt mode, queue priority/weights, memory size, shared memory ID, SGL settings, bit bucket length, host NQN, PI action/check settings, metadata buffer sizing, TCP digest settings, VMD enablement, initial zone reset, zone append, qid mapping print, tracing, log flags, and PCIe SGL merge control.

## Dependencies
Depends on SPDK NVMe, NVMe ZNS, VMD, env, DIF/DIX, tracing, endian/string/util helpers, and fio version-specific APIs for ZBD, FDP, and multi-range trim.

## Filesystem/Block Relevance
This plugin benchmarks raw NVMe hardware and NVMe-oF paths without the bdev layer, exposing controller, namespace, queue, metadata, and zoned behavior directly to fio.

## Risks and Notes
- Requires fio `thread=1`.
- Global plugin configuration is established by the first initialization path and shared across jobs.
- Admin completion polling is done by a cancellable pthread.
- PI buffer sizing must cover metadata needs; the code caps per-I/O metadata to configured allocation.
- ZNS report/reset paths allocate temporary qpairs before normal fio open.
- FDP directives require SGL writes.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/fio/nvme/fio_plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/iscsi_tgt/Makefile -->
# File Research: sources/virtualization/spdk/app/iscsi_tgt/Makefile

## Purpose
Builds the SPDK iSCSI target application `iscsi_tgt`.

## Main Contents
- Sets `APP = iscsi_tgt`.
- Adds `-I$(SPDK_ROOT_DIR)/lib` because iSCSI lacks a public API header.
- Compiles `iscsi_tgt.c`.
- Links all modules plus `event` and `event_iscsi`.
- Adds `env_dpdk_rpc` for DPDK env builds.
- Adds `event_nbd` on Linux.
- Provides install/uninstall targets.

## Dependencies
Depends on SPDK event framework, iSCSI event subsystem, all configured modules, optional DPDK RPC integration, and optional Linux NBD event support.

## Filesystem/Block Relevance
Builds the SPDK userspace iSCSI target, which exposes SPDK block devices over iSCSI.

## Risks and Notes
- The private include path is explicitly temporary.
- Link set varies by OS and env backend.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/iscsi_tgt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/iscsi_tgt/iscsi_tgt.c -->
# File Research: sources/virtualization/spdk/app/iscsi_tgt/iscsi_tgt.c

## Purpose
Minimal executable wrapper for the SPDK iSCSI target app.

## Main Entry Points
- `iscsi_parse_arg()` handles `-b` daemon mode.
- `iscsi_usage()` prints the iSCSI-specific option.
- `spdk_startup()` optionally dumps memzones when `MEMZONE_DUMP` is set.
- `main()` initializes app opts, parses SPDK and app arguments, optionally daemonizes, starts SPDK app framework, finalizes, and returns status.

## Internal Mechanics
The app name is `iscsi`. It relies on linked event subsystems to initialize the actual iSCSI target functionality. `daemon(1, 0)` is called after argument parsing and before `spdk_app_start()` when `-b` is supplied.

## Dependencies
Uses SPDK app/event/env/log APIs and includes `iscsi/iscsi.h` from SPDK's internal library path.

## Filesystem/Block Relevance
This is the process entry point for serving SPDK bdev-backed logical units through iSCSI.

## Risks and Notes
- No custom shutdown callback is installed.
- Failure to daemonize exits immediately.
- Most target behavior is in linked libraries, not this wrapper.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/iscsi_tgt/iscsi_tgt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/nvmf_tgt/Makefile -->
# File Research: sources/virtualization/spdk/app/nvmf_tgt/Makefile

## Purpose
Builds the SPDK NVMe-oF target application `nvmf_tgt`.

## Main Contents
- Sets `APP = nvmf_tgt`.
- Compiles `nvmf_main.c`.
- Links all modules plus `event` and `event_nvmf`.
- Adds `env_dpdk_rpc` for DPDK env builds.
- Adds `event_nbd` on Linux.
- Provides install/uninstall targets.

## Dependencies
Depends on SPDK event framework, NVMe-oF event subsystem, configured modules, optional DPDK RPC, and optional Linux NBD event support.

## Filesystem/Block Relevance
Builds the SPDK userspace NVMe-oF target, exposing SPDK bdevs as NVMe namespaces over fabrics transports.

## Risks and Notes
- Runtime target configuration is supplied through SPDK app/RPC mechanisms rather than this makefile.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/nvmf_tgt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/nvmf_tgt/nvmf_main.c -->
# File Research: sources/virtualization/spdk/app/nvmf_tgt/nvmf_main.c

## Purpose
Minimal executable wrapper for the SPDK NVMe-oF target app.

## Main Entry Points
- `nvmf_usage()` and `nvmf_parse_arg()` provide empty app-specific argument handling.
- `nvmf_tgt_started()` optionally dumps memzones when `MEMZONE_DUMP` is set.
- `main()` initializes SPDK app opts, parses args, starts the app framework, finalizes, and returns status.

## Internal Mechanics
The app name is `nvmf`. All meaningful target setup and runtime behavior come from linked event subsystems and configuration/RPC processing.

## Dependencies
Uses SPDK stdinc, env, and event APIs.

## Filesystem/Block Relevance
This is the process entry point for the NVMe-oF target that exports SPDK bdevs.

## Risks and Notes
- No custom app-specific CLI options are implemented.
- Startup blocks until the SPDK app exits.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/nvmf_tgt/nvmf_main.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_dd/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_dd/Makefile

## Purpose
Builds the `spdk_dd` copy utility.

## Main Contents
- Sets `APP = spdk_dd`.
- Compiles `spdk_dd.c`.
- Links all configured modules plus `event` and `event_bdev`.
- Uses SPDK app make rules and install/uninstall helpers.

## Dependencies
Depends on SPDK bdev/event libraries and all configured modules.

## Filesystem/Block Relevance
Builds a dd-like data mover for copying between files and SPDK bdevs.

## Risks and Notes
- Parent makefile restricts this app to Linux builds.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_dd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_dd/spdk_dd.c -->
# File Research: sources/virtualization/spdk/app/spdk_dd/spdk_dd.c

## Purpose
Implements `spdk_dd`, an asynchronous dd-like copy utility that copies between regular/block files and SPDK bdevs with configurable block size, queue depth, offsets, count, sparse handling, and file I/O backend selection.

## Main Entry Points
- `main()` parses SPDK/app arguments, validates input/output choices, starts the SPDK app, frees resources, and finalizes.
- `dd_run()` opens input/output targets, validates sizes/alignment, allocates DMA buffers, initializes file I/O pollers, starts progress reporting, and seeds the pipeline.
- `dd_target_seek()`, `dd_target_populate_buffer()`, `dd_target_read()`, and `dd_target_write()` form the copy pipeline.
- `dd_aio_poll()` and `dd_uring_poll()` reap file I/O completions.
- SPDK bdev callbacks `_dd_read_bdev_done()`, `_dd_write_bdev_done()`, `_dd_bdev_seek_data_done()`, and `_dd_bdev_seek_hole_done()` continue bdev operations.
- `dd_finish()` handles app shutdown by setting an interrupt flag.
- `dd_exit()` closes targets, unregisters pollers, and stops the app.

## Internal Mechanics
The utility models input and output as `dd_target` objects of type file or bdev. It maintains a fixed pool of `dd_io` objects sized by queue depth. Each object cycles through populate, read, write, and seek stages.

For normal copying, `dd_target_populate_buffer()` prepares a chunk and submits a read; read completion submits a write; write completion schedules the next chunk. If the final write is not aligned to the output block size, it first reads the destination block into the buffer so the partial update can be written as a full native block.

For sparse mode, file input uses `lseek(SEEK_DATA/SEEK_HOLE)`. Bdev input uses `spdk_bdev_seek_data()` and `spdk_bdev_seek_hole()` with a queue to serialize seek operations. Output files are finalized with `ftruncate()` when needed to preserve holes through the requested copy span.

File I/O uses io_uring when compiled and not forced to AIO, otherwise Linux libaio. io_uring registers files and fixed buffers; libaio submits `iocb`s and polls events through an SPDK poller. Bdev I/O uses SPDK bdev descriptors and I/O channels.

## Options
Supports `--if`, `--of`, `--ib`, `--ob`, `--iflag`, `--oflag`, `--skip`, `--seek`, `--bs`, `--qd`, `--count`, `--aio`, and `--sparse`.

## Dependencies
Depends on SPDK app, bdev, event, fd, util/string, optional VMD include, Linux libaio, and optional liburing.

## Filesystem/Block Relevance
This is a practical bridge between POSIX files/block devices and SPDK bdevs. It exercises read/write alignment, sparse extent discovery, bdev seek data/hole APIs, and async file I/O integration.

## Risks and Notes
- Requires exactly one input source and one output target.
- `--bs` must be at least both native block sizes and must align to input bdev block size.
- File targets are opened read/write; output files are created/truncated unless flags prevent it.
- Sparse behavior depends on target support for seek data/hole semantics.
- Progress accounting is global to the single copy job.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_dd/spdk_dd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_lspci/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_lspci/Makefile

## Purpose
Builds `spdk_lspci`, a small utility for listing PCI devices visible through SPDK's NVMe/VMD PCI drivers.

## Main Contents
- Sets `APP = spdk_lspci`.
- Compiles `spdk_lspci.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make rules and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, and common app build infrastructure.

## Filesystem/Block Relevance
Helps discover NVMe PCI devices usable by SPDK block/NVMe applications.

## Risks and Notes
- It is a standalone env utility, not an SPDK event app.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_lspci/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_lspci/spdk_lspci.c -->
# File Research: sources/virtualization/spdk/app/spdk_lspci/spdk_lspci.c

## Purpose
Lists SPDK-visible PCI devices supported by the NVMe driver, including devices behind VMD.

## Main Entry Points
- `usage()` prints help.
- `pci_enum_cb()` is a no-op enumeration callback used to populate SPDK's PCI list.
- `print_pci_dev()` formats PCI address, vendor/device IDs, and VMD annotations.
- `main()` parses `-h`, initializes SPDK env, initializes VMD, enumerates NVMe PCI devices, prints the device list, and finalizes.

## Internal Mechanics
The program initializes SPDK env with app name `spdk_lspci`, calls `spdk_vmd_init()`, enumerates the NVMe PCI driver, and then walks all SPDK PCI devices with `spdk_pci_for_each_device()`.

## Dependencies
Uses SPDK env, PCI, NVMe PCI driver access, and VMD APIs.

## Filesystem/Block Relevance
This utility helps identify NVMe hardware available to SPDK storage applications.

## Risks and Notes
- VMD initialization failure is non-fatal but may hide some NVMe devices.
- The enumeration callback intentionally does not claim or configure devices.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_lspci/spdk_lspci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_discover/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_discover/Makefile

## Purpose
Builds `spdk_nvme_discover`, an NVMe-oF discovery utility focused on discovery log changes/AERs.

## Main Contents
- Sets `APP = spdk_nvme_discover`.
- Compiles `discovery_aer.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, socket modules, VMD, and SPDK app make rules.

## Filesystem/Block Relevance
Builds a utility for discovering NVMe-oF subsystems that may expose remote block namespaces.

## Risks and Notes
- The source file is a standalone env-based utility, not a full SPDK event app.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_discover/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_discover/discovery_aer.c -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_discover/discovery_aer.c

## Purpose
Connects to an NVMe-oF discovery controller, prints the discovery log page, registers for discovery asynchronous event notifications, and reprints the log when discovery changes occur.

## Main Entry Points
- `parse_args()` handles transport ID, debug/log flags, and host NQN.
- `set_trid()` initializes and parses the NVMe transport ID, defaulting to the discovery NQN.
- `get_discovery_log_page()` submits a discovery log retrieval.
- `get_log_page_completion()` prints the discovery log and handles pending re-fetch requests.
- `aer_cb()` validates discovery AER completions and triggers another log fetch.
- `setup_sig_handlers()` installs SIGINT/SIGTERM handlers.
- `main()` initializes env, connects to the discovery controller, registers the AER callback, performs initial fetch, processes admin completions until shutdown, detaches, and finalizes.

## Internal Mechanics
The program tracks `g_discovery_in_progress` and `g_pending_discovery` so overlapping AER-triggered log requests are coalesced. The main loop only processes admin completions; all discovery log and AER activity completes through admin completion callbacks.

`print_discovery_log()` decodes generation counter, record count, record format, transport type, address family, subsystem type, port/controller IDs, service ID, subsystem NQN, and transport address.

## Dependencies
Uses SPDK env, NVMe, NVMe-oF discovery log structures, transport ID parsing, endian helpers, logging, signal handling, and admin completion processing.

## Filesystem/Block Relevance
Discovery records identify remote NVMe subsystems and endpoints that can later be used as block devices by SPDK NVMe-oF clients.

## Risks and Notes
- The transport ID is mandatory and must target an NVMe-oF discovery subsystem, not PCIe.
- Errors in AER or discovery-log commands terminate the process.
- Keep-alive/transport failure is represented by the main exit flag comment, but shutdown is primarily signal-driven in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_discover/discovery_aer.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_identify/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_identify/Makefile

## Purpose
Builds `spdk_nvme_identify`, SPDK's NVMe controller/namespace inspection utility.

## Main Contents
- Sets `APP = spdk_nvme_identify`.
- Compiles `identify.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, and common app build fragments.

## Filesystem/Block Relevance
Builds a utility used to inspect NVMe block namespace properties, capabilities, log pages, ZNS state, OCSSD geometry, and FDP data.

## Risks and Notes
- Feature availability depends on controller capabilities and transport.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_identify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_identify/identify.c -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_identify/identify.c

## Purpose
Implements `spdk_nvme_identify`, a comprehensive NVMe/NVMe-oF inspection utility. It discovers or connects to controllers, retrieves identify data, feature values, log pages, discovery records, OCSSD data, ZNS reports, FDP logs, and vendor-specific Intel logs, then prints decoded human-readable output.

## Main Entry Points
- `parse_args()` handles transport ID, hugepage/env settings, core selection, VMD, hex dump, socket backend, OCSSD verbosity, ZNS report limit, and log flags.
- `main()` initializes SPDK env, optionally initializes VMD, connects to a specific transport ID or probes controllers, prints controller data, detaches, and finalizes.
- `probe_cb()` applies host NQN to controller options.
- `attach_cb()` prints a discovered controller and queues async detach.
- `print_controller()` drives controller-level feature/log retrieval and prints controller, command set, log, health, power, ANA, discovery, vendor, and namespace data.
- `print_namespace()` prints active namespace metadata and dispatches OCSSD, ZNS, NVM, and FDP-specific detail paths.

## Internal Mechanics
The utility uses global buffers for log pages and a global `outstanding_commands` counter. Admin commands are submitted asynchronously but then drained by repeatedly calling `spdk_nvme_ctrlr_process_admin_completions()`.

Feature retrieval is serialized one feature at a time because some NVMe SSDs mishandle overlapping GET FEATURES commands. Controller features include arbitration, power management, temperature threshold, number of queues, and OCSSD media feedback. Namespace features include error recovery and FDP when supported.

Log collection includes error, health/SMART, firmware slot, ANA, command effects, discovery log, Intel SMART, Intel temperature, Intel marketing description, and FDP-specific logs. FDP configuration, reclaim unit usage, statistics, and events are fetched in header-then-full-buffer patterns when variable-sized.

ZNS handling prints ZNS namespace data and obtains zone reports through a temporary I/O qpair. OCSSD handling retrieves geometry and chunk information. NVM-specific data prints PI/storage-tag details.

The printer includes helpers for hex dumps, endian-safe field decoding, ASCII trimming, 128-bit counters, variable-width integers, opcode name mapping, CSI names, PI format names, and zone descriptor rendering.

## Dependencies
Depends on SPDK env, NVMe, NVMe-oF spec structures, NVMe ZNS, OCSSD, Intel NVMe extensions, VMD, socket backend selection, endian/string/util/UUID helpers, PCI IDs, and SPDK log flags.

## Filesystem/Block Relevance
This is a key diagnostic utility for NVMe-backed block storage. It exposes namespace size/capacity/utilization, LBA formats, metadata/PI format, deallocation/flush/write-zeroes/reservation support, ZNS geometry and zone state, FDP placement data, health counters, and discovery records for fabrics endpoints.

## Risks and Notes
- Many log buffers are dynamically allocated and freed in print paths; early exits can bypass cleanup.
- The tool exits on several command submission/allocation failures rather than attempting partial output.
- ZNS report count defaults to a limited number unless `-z` requests all zones or a specific limit.
- Discovery controllers skip most non-discovery log/feature retrieval.
- A specific `traddr` uses direct `spdk_nvme_connect()`; otherwise the tool probes matching controllers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_identify/identify.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_perf/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_perf/Makefile

## Purpose
Builds `spdk_nvme_perf`, SPDK's NVMe performance benchmark application.

## Main Contents
- Sets `APP = spdk_nvme_perf`.
- Compiles `perf.c`.
- Links socket modules, NVMe, VMD, keyring file support, trace, and event libraries.
- On Linux, links `-laio` and defines `HAVE_LIBAIO`.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, keyring file module, trace, event framework, and Linux libaio when built on Linux.

## Filesystem/Block Relevance
Builds SPDK's direct NVMe benchmark tool for measuring block I/O performance across PCIe and fabrics transports.

## Risks and Notes
- Linux builds gain libaio support through conditional flags.
- Actual benchmark behavior is implemented in `perf.c`, which is outside this grouped work item.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_perf/Makefile -->