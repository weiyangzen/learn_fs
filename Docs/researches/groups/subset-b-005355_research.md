# subset-b-005355 Research

Grouped research for the listed Linux SCSI files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sg.c

## Purpose
Implements the Linux SCSI generic (`sg`) character driver, exposing SCSI command passthrough devices as `/dev/sgN` under major `SCSI_GENERIC_MAJOR`. It supports the legacy `struct sg_header` read/write ABI and the newer `sg_io_hdr_t` ABI used by `SG_IO`, plus polling, async notification, mmap-backed reserved buffers, direct I/O, blk tracing, sysfs class devices, and optional `/proc/scsi/sg` diagnostics.

## Important APIs, Types, And Functions
The central state types are `Sg_device`, `Sg_fd`, `Sg_request`, and `Sg_scatter_hold`. `Sg_device` tracks one SCSI device, its minor number, open/exclusive state, sysfs cdev, attached file descriptors, and detach state. `Sg_fd` is per-open state: request list, reserve buffer, timeout, command queue mode, orphan policy, fasync target, and refcount. `Sg_request` represents one queued SCSI command and contains the user header, sense buffer, block request, bio, scatter backing, and completion state. `Sg_scatter_hold` owns indirect I/O pages or references the reserved buffer.

The exported file operations are `sg_open`, `sg_release`, `sg_read`, `sg_write`, `sg_ioctl`, `sg_poll`, `sg_mmap`, and `sg_fasync`. Device lifecycle is handled by `sg_add_device`, `sg_remove_device`, `sg_alloc`, `sg_get_dev`, and `sg_device_destroy` through a `class_interface` registered with the SCSI midlayer. Request creation and completion flow through `sg_new_write`, `sg_common_write`, `sg_start_req`, `sg_rq_end_io`, `sg_new_read`, `sg_finish_rem_req`, and `sg_remove_request`.

The module parameters are `scatter_elem_sz`, `allow_dio`, and `def_reserved_size`. Procfs support, when enabled, adds `allow_dio`, `def_reserved_size`, `devices`, `device_strs`, `device_hdr`, `debug`, and `version` entries under `/proc/scsi/sg`.

## Control Flow
`init_sg` registers the character-device range, class, and SCSI interface. When a SCSI device appears, `sg_add_device` obtains the request queue, allocates a cdev and `Sg_device`, assigns an IDR minor, creates the sysfs device and `generic` backlink, and stores driver data on the class device.

`sg_open` resolves the minor through the IDR, takes a device reference, blocks or fails around `O_EXCL`, verifies error-recovery state unless nonblocking, initializes per-open `Sg_fd` state, reserves a buffer capped by queue limits, and increments open count. `sg_release` decrements open count, clears exclusive state when needed, wakes waiters, and drops the `Sg_fd` reference. Final per-fd cleanup runs in workqueue context in `sg_remove_sfp_usercontext`, which drains unread requests, unmaps bios, frees reserve pages, drops the SCSI device, and releases the module reference.

The write path accepts either old or v3 headers. Legacy writes parse `struct sg_header`, infer command length and transfer direction, copy the CDB, and populate an internal `sg_io_hdr_t`. New writes copy an `sg_io_hdr_t`, validate `interface_id == 'S'`, check mmap/direct-I/O compatibility, copy the user CDB, and optionally enforce read-only access restrictions through `sg_allow_access`. `sg_common_write` validates transfer size, builds and maps the block request in `sg_start_req`, stores `sg_rq_end_io` as completion, and submits with `blk_execute_rq_nowait`.

`sg_start_req` allocates a SCSI block request, copies the CDB into the `scsi_cmnd`, and maps data through direct I/O when allowed and aligned or through pages from the reserve/indirect allocator otherwise. The indirect allocator builds a page-pointer array, rounds buffers to 512-byte boundaries, tries the configured page order, and backs off to smaller orders on allocation failure.

On completion, `sg_rq_end_io` copies status, residual, sense, and duration from the SCSI command, updates removable-media change state for unit attention, frees the block request immediately, and either wakes readers/fasync subscribers or schedules user-context cleanup for dropped orphan requests. Reads locate a completed non-`SG_IO` request by pack id, mark it as being returned, copy legacy or v3 result fields and sense data to userspace, unmap user buffers, and remove the request.

`SG_IO` ioctl is synchronous on top of the same machinery: submit with `sg_new_write`, wait on `read_wait`, then call `sg_new_read`; if interrupted before completion, the request becomes an orphan. Other ioctls manage timeout, reserved size, command queueing, pack-id behavior, orphan retention, request-table introspection, SCSI identity, blk tracing, and delegation to `scsi_ioctl`.

## State And Persistence Behavior
Persistent kernel state is in the IDR minor map, per-device cdev/sysfs objects, per-open request arrays, per-open reserved buffer pages, module parameters, and optional procfs tunables. State is not persisted across module unload or reboot. Request state transitions are encoded in `Sg_request.done`: active (`0`), readable (`1`), and being returned (`2`). Detached devices are guarded by `atomic_t detaching`, which makes new opens fail, wakes waiters, emits `EPOLLHUP`, and allows final destruction only after references drain.

Concurrency is split across `sg_index_lock` for the global IDR, `sfd_lock` for open-file lists, `rq_list_lock` for request lists and completion flags, `open_rel_lock` for open/exclusive counters, and `f_mutex` for mutable per-fd buffer settings. Reference counts on `Sg_device` and `Sg_fd` bridge asynchronous request completion and release paths.

## Dependencies And Integration Points
The driver sits between user-space SCSI passthrough tools and the SCSI/block layers. It depends on SCSI core types and helpers (`scsi_device`, `scsi_cmnd`, `scsi_alloc_request`, `scsi_ioctl`, error handling, command permission checks), block request mapping/unmapping (`blk_rq_map_user_io`, `blk_rq_unmap_user`, blk trace), Linux char-device infrastructure, sysfs classes, IDR allocation, wait queues, fasync, procfs/seq-file support, and VM fault handling for mmap of reserve buffers.

## Risks
This is a security-sensitive raw device interface. The code explicitly restricts legacy read/write use to the opener credential context with `sg_check_file_access` because inherited file descriptors and splice-like paths have historically made this ABI dangerous. User-pointer handling is broad: headers, CDBs, sense buffers, iovecs, mmap buffers, and data buffers all cross the kernel boundary and must preserve exact ABI behavior.

The request lifecycle has several race-prone edges: detach vs open/read/write, `SG_IO` interrupted by a signal, orphan cleanup, request completion racing `release`, reserved-buffer reuse, and immediate block request freeing while user-buffer unmapping is deferred to user context. Buffer sizing is also delicate because it combines user lengths, queue limits, direct-I/O alignment, scatter table limits, and module/proc tunables. Compatibility behavior, including old header field reuse and odd return values such as `SG_GET_TIMEOUT`, should be considered ABI-stable even when surprising.

## Test Signals
Useful tests include `sg3_utils` passthrough smoke tests, `SG_IO` success/error/sense handling, legacy read/write command flow, nonblocking open/read/write behavior, `O_EXCL` open contention, command queue saturation, `poll`/`fasync`, forced pack-id reads, timeout and orphan behavior after signal interruption, reserved-buffer resize while idle vs busy, mmap I/O, direct-I/O enablement/alignment fallbacks, hot-unplug/detach while commands are pending, and `/proc/scsi/sg/debug` output with active and completed requests. Kernel build signals should include both `CONFIG_SCSI_PROC_FS` and compat syscall coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sgiwd93.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sgiwd93.c

## Purpose
Provides the SGI IP22 platform driver for WD33C93 SCSI controllers connected through the SGI HPC3 DMA engine. It adapts the shared `wd33c93` SCSI core to SGI hardware registers, interrupt delivery, and HPC descriptor-chain DMA.

## Important APIs, Types, And Functions
`struct ip22_hostdata` embeds `WD33C93_hostdata` and adds the DMA descriptor memory, DMA handle, and parent `device`. `struct hpc_chunk` wraps an `hpc_dma_desc` with padding to keep descriptors quadword-aligned. `sgiwd93_template` defines the SCSI host template using `wd33c93_queuecommand`, `wd33c93_abort`, and `wd33c93_host_reset`.

The important functions are `sgiwd93_probe`, `sgiwd93_remove`, `sgiwd93_intr`, `dma_setup`, `dma_stop`, `fill_hpc_entries`, `init_hpc_chain`, and exported `sgiwd93_reset`.

## Control Flow
The platform-driver init function registers a driver named `sgiwd93`. Probe obtains platform data containing WD register addresses, HPC register addresses, unit number, and IRQ. It allocates a `Scsi_Host` with `ip22_hostdata`, allocates one noncoherent page for HPC DMA descriptors, initializes the circular descriptor chain, points WD33C93 register access at SASR/SCMD offsets, configures sync/fast/burst DMA mode in the embedded WD hostdata, and calls `wd33c93_init` with `dma_setup` and `dma_stop` callbacks. It then requests the IRQ, registers the host with SCSI core, and scans the bus.

For interrupts, `sgiwd93_intr` takes the SCSI host lock and delegates to `wd33c93_intr`. For data movement, `dma_setup` records direction, rejects empty/bogus transfers as no-DMA, maps the current SCSI buffer with `dma_map_single`, fills the HPC descriptor list in chunks of at most 8192 bytes, appends an EOX descriptor, syncs descriptor memory for the device, writes the next-descriptor pointer, and starts HPC with direction-specific control bits. `dma_stop` stops or flushes HPC depending on direction, clears control, and unmaps the original DMA buffer.

Remove reverses probe: remove SCSI host, free IRQ, free noncoherent descriptor memory, and release the `Scsi_Host`.

## State And Persistence Behavior
All state is runtime-only and scoped to the platform device. The descriptor page is reused across commands; each DMA setup rewrites descriptors from the current `scsi_pointer`. The embedded `WD33C93_hostdata` persists controller settings and current DMA direction while the host exists. No state is stored on disk or across driver unload.

## Dependencies And Integration Points
This file depends on SGI MIPS platform headers (`hpc3`, `ip22`, `wd`), Linux platform-device and DMA APIs, SCSI host core, and the shared `wd33c93` driver. Hardware integration is through HPC3 SCSI registers and WD33C93 SASR/SCMD register windows supplied by platform data.

## Risks
The DMA path assumes the WD33C93 core uses `struct scsi_pointer` fields in the expected way. Descriptor limits and the 8192-byte chunking rule encode hardware behavior; changing them can create truncated or corrupt DMA. The file contains an explicit warning that abort/reset method signatures can be unsafe on 64-bit systems with memory outside compatible address spaces. Error handling in probe must preserve unwind order because IRQ registration, host registration, and descriptor allocation are independent resources.

## Test Signals
Signals are mainly platform/hardware tests: boot on SGI IP22 with the controller present, IRQ delivery under command load, DMA reads and writes over transfer sizes above and below 8192 bytes, abort and host-reset paths via SCSI error handling, remove/unbind cleanup, and DMA API debug checks for map/unmap balance. Build coverage requires the target architecture/platform headers that expose SGI HPC3 and WD platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sgiwd93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sim710.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sim710.c

## Purpose
Implements a simple NCR/Symbios 53C710 EISA SCSI driver by wiring EISA device discovery and board-specific configuration into the shared `53c700` SCSI core. It supports command-line/module configuration for per-slot SCSI IDs and EISA probing for known Compaq and HP board IDs.

## Important APIs, Types, And Functions
`sim710_driver_template` names the host and supplies the SCSI midlayer template used by `NCR_700_detect`. `sim710_probe_common` performs the shared host allocation and registration for a detected board. `sim710_eisa_probe` decodes EISA configuration registers for supported cards. `sim710_device_remove`, `sim710_init`, `sim710_exit`, and `param_setup` handle lifecycle and module/boot parameters.

The `id_array` stores optional SCSI initiator IDs indexed by slot, while `sim710` is a module parameter string parsed with `param_setup`.

## Control Flow
At boot/module load, optional `sim710=` parameters are parsed. Entries of the form `slot:<n>` followed by `id:<n>` update `id_array`; invalid slot or missing slot inputs produce warnings. With `CONFIG_EISA`, `sim710_init` registers an EISA driver with IDs `CPQ4410`, `CPQ4411`, and `HWP0C80`.

On EISA probe, HP boards use one IRQ table and read SCSI ID from an EISA register bitmask; other supported boards use the Compaq IRQ table. Invalid IRQ indexes fail probing. Valid configuration enters `sim710_probe_common`, which allocates and initializes `NCR_700_Host_Parameters`, reserves the 64-byte I/O region, maps it, sets differential/clock/chip/burst flags, calls `NCR_700_detect`, sets SCSI ID/base/IRQ on the returned host, requests a shared IRQ using `NCR_700_intr`, stores the host in driver data, and scans the host.

Remove unregisters the SCSI host, releases the shared `53c700` host, unmaps I/O, frees hostdata, frees the IRQ, and releases the I/O region.

## State And Persistence Behavior
State is runtime-only. `id_array` is initialized to target ID 7 and can be modified by boot/module parameters before probing. Each detected device stores its `Scsi_Host` in the device driver data and its `NCR_700_Host_Parameters` in host private data. Hardware resources are reserved only while the driver is bound.

## Dependencies And Integration Points
This file depends on EISA core when enabled, Linux I/O port reservation/mapping, interrupt handling, SCSI host registration, SPI transport headers, and the shared `53c700` implementation (`NCR_700_detect`, `NCR_700_intr`, `NCR_700_release`). It has no independent command execution engine; command handling is delegated to the core 53c700 driver.

## Risks
The parser is permissive and uses simple string scanning, so malformed command-line input mostly results in warnings or ignored settings rather than strict failure. EISA register decoding is board-specific and assumes the static IRQ tables match firmware encoding. Probe error paths must keep resource release paired with the point of failure. The code currently returns success from `sim710_init` even if no EISA devices were found because EISA registration does not report that distinction.

## Test Signals
Primary signals are kernel build coverage with and without `CONFIG_EISA`, module parameter parsing tests for slot/id combinations, EISA probe on the supported device IDs, successful SCSI scan, IRQ sharing behavior, remove/unbind resource cleanup, and I/O port conflict handling. Runtime validation depends on hardware or emulation that exposes compatible EISA 53C710 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sim710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Kconfig

## Purpose
Defines the kernel configuration option for the Microchip PQI storage controller driver. `SCSI_SMARTPQI` can be built in, built as module `smartpqi`, or disabled.

## Important APIs, Types, And Functions
The public interface is the Kconfig symbol `SCSI_SMARTPQI`, declared as `tristate "Microchip PQI Driver"`. It depends on `PCI`, `SCSI`, and `!S390`, and selects `SCSI_SAS_ATTRS` plus `RAID_ATTRS`.

## Control Flow
During kernel configuration, selecting this option enables compilation of the smartpqi driver objects through the companion Makefile. The help text identifies the supported controller family, module name, a Microchip URL, and a note that `aacraid` will not manage smartpqi controllers.

## State And Persistence Behavior
This file has no runtime state. Its selected value persists only in the kernel `.config` and determines whether the driver is included in the build or emitted as a loadable module.

## Dependencies And Integration Points
It integrates with the SCSI and PCI Kconfig menus and forces the SAS transport and RAID attribute support needed by the driver. Documentation integration is through `Documentation/scsi/smartpqi.rst`.

## Risks
Dependency mistakes can make the driver visible on unsupported architectures or hide it from valid PCI/SCSI builds. The `select` statements pull in support code automatically, so missing or excessive selects can affect minimal kernel configurations. The note about `aacraid` is operationally important because choosing the wrong driver can leave controllers unmanaged.

## Test Signals
Signals are Kconfig resolution tests (`y`, `m`, and `n` where allowed), build tests with PCI/SCSI enabled and on S390-disabled paths, module-name validation (`smartpqi.ko`), and menu/help rendering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Makefile

## Purpose
Defines how the smartpqi driver is built from its component objects when `CONFIG_SCSI_SMARTPQI` is enabled.

## Important APIs, Types, And Functions
The key Kbuild variables are `obj-$(CONFIG_SCSI_SMARTPQI) += smartpqi.o` and `smartpqi-objs := smartpqi_init.o smartpqi_sis.o smartpqi_sas_transport.o`.

## Control Flow
Kbuild includes this directory Makefile from the SCSI driver build. If `CONFIG_SCSI_SMARTPQI=y`, the objects are linked into the kernel; if `m`, they are linked into `smartpqi.ko`; if unset, no smartpqi objects are built.

## State And Persistence Behavior
No runtime state exists. Build output state is limited to generated object files and the final built-in or module artifact.

## Dependencies And Integration Points
This file ties the Kconfig symbol to three implementation units: initialization/core controller logic, SIS/PQI mode transition support, and SAS transport integration. It depends on Kbuild conventions for composite objects.

## Risks
Adding a new implementation source without updating `smartpqi-objs` silently omits functionality. Incorrect object ordering can matter if initialization sections or symbol dependencies change. The Makefile is small, so most risk is integration drift relative to source files.

## Test Signals
Build `CONFIG_SCSI_SMARTPQI=y` and `m`, confirm all three objects are compiled and linked, inspect `smartpqi.ko` symbols when modular, and run dependency-only builds after adding or removing smartpqi source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi.h

## Purpose
Defines the hardware protocol, firmware data structures, queue layout, controller state, device state, RAID-bypass metadata, SAS transport hooks, and helper declarations for the Microchip PQI SCSI driver. It is the shared contract consumed by `smartpqi_init.c`, `smartpqi_sis.c`, and `smartpqi_sas_transport.c`.

## Important APIs, Types, And Functions
The header starts with packed hardware register and IU definitions: `pqi_device_registers`, `pqi_ctrl_registers`, `pqi_iu_header`, admin requests/responses, RAID/AIO I/O requests, task management requests, event requests/responses, vendor general requests, host memory descriptors, and AIO/RAID error information. These structures use explicit endian types and packed layout because firmware consumes them directly.

Queue and controller runtime types include `pqi_admin_queues_aligned`, `pqi_admin_queues`, `pqi_queue_group`, `pqi_event_queue`, `pqi_io_request`, `pqi_event`, and the large `pqi_ctrl_info`. `pqi_ctrl_info` is the central HBA state: PCI device, MMIO register pointers, firmware identity, controller capabilities, queue memory, IRQ mode and vector counts, SCSI host pointer, scan/reset flags, firmware feature booleans, device list, SAS host data, request pool, event array, heartbeat/offline work, synchronous request semaphore, blocked-thread accounting, OFA/controller-log memory, and removal state.

Device-facing types include CISS report-lun formats, physical/logical LUN entries, `raid_map`, `pqi_scsi_dev_raid_map_data`, `pqi_scsi_dev`, stream detection state, per-device TMF work, SAS node/port/phy wrappers, and BMIC command payloads. `pqi_scsi_dev` records bus/target/lun identity, WWID and volume ID, physical/logical flags, offline/remove/reset state, inquiry strings, SAS topology, queue depth, AIO handle, RAID bypass map and counters, encryption limits, stream history, outstanding command counters, and TMF work items.

Constants enumerate PQI request/response IU types, admin functions, PQI and CISS status codes, event types, queue sizes, queue alignment requirements, reset types/actions, firmware feature bits, CISS/BMIC opcodes, logical volume states, bus IDs, RAID map limits, and default transfer/queue limits. The inline `shost_to_hba` retrieves `pqi_ctrl_info` from SCSI host private data. External declarations expose SAS/SMP integration functions and `pqi_sas_transport_functions`.

## Control Flow
This header does not execute control flow directly, but it shapes the driver lifecycle. Initialization code maps SIS and PQI registers through `pqi_ctrl_registers`, transitions to PQI mode, reports device capabilities, allocates aligned admin/operational/event queues, fills `pqi_ctrl_info`, and creates I/O request pools sized by firmware limits. I/O submission code chooses RAID, AIO, RAID1, RAID5, or RAID6 IU formats based on `pqi_scsi_dev` state and RAID map calculations, then posts to a `pqi_queue_group`. Completion code decodes response IU types and error buffers to update SCSI command results.

Discovery code uses CISS report logical/physical LUN structures, BMIC identify payloads, VPD status definitions, and RAID map structures to build and update `pqi_scsi_dev` entries. Event code uses `pqi_event_config`, `pqi_event_response`, and event acknowledgements to schedule rescans, AIO state changes, OFA memory handling, and controller logging. Reset/offline code uses heartbeat, soft-reset, reset-register, block-request flags, and controller removal state fields in `pqi_ctrl_info`.

## State And Persistence Behavior
All declared state is in-memory driver state or DMA-coherent memory shared with controller firmware. The hardware-facing structures persist only while allocated and mapped; firmware-visible queues and host-memory descriptors must obey the alignment and packing constants. `pqi_ctrl_info` persists for the PCI device lifetime, while `pqi_scsi_dev` entries persist while devices remain discovered or retained through rescan/delete handling. No file-backed persistence is defined here.

The header encodes several state machines: controller mode (`SIS_MODE`/`PQI_MODE`), controller removal state, reset status, per-device gone/new/keep/offline/reset flags, request reference counts, event pending flags, heartbeat counters, blocked request accounting, and OFA quiesce/memory allocation work.

## Dependencies And Integration Points
The header depends on Linux SCSI host APIs, BSG/SAS transport support, PCI-owned controller code, DMA address types, endian annotations, workqueues, timers, locks, semaphores, per-CPU stats, and firmware protocols PQI, CISS, BMIC, CSMI, and SAS SMP. It integrates with Kbuild through the smartpqi composite module and with the SCSI midlayer through `Scsi_Host`, `scsi_cmnd`, `scsi_device`, SAS rphys, BSG jobs, and RAID/SAS attributes selected by Kconfig.

## Risks
The highest risk is ABI/layout drift. Packed structures, bitfields, endian fields, array sizes, queue element lengths, and alignment constants must match firmware exactly. Changes to `pqi_ctrl_info` and `pqi_scsi_dev` can affect locking, lifecycle, hotplug, reset, and I/O fast paths across multiple implementation files. RAID bypass data has many derived fields; inconsistent interpretation of RAID maps can misroute I/O. Firmware feature bits and default transfer limits gate behavior for encryption, RAID writes, OFA, logging, soft reset, and multi-LUN devices, so a wrong constant can disable required handling or enable unsupported paths.

## Test Signals
Build tests should compile all smartpqi objects with sparse/endian checking and struct layout assumptions intact. Runtime signals include controller initialization in SIS-to-PQI transition, admin queue creation/deletion, operational queue interrupt delivery, logical/physical LUN discovery, SAS transport registration, SMP passthrough, RAID bypass reads/writes for RAID 0/1/5/6, encrypted transfer limit handling, hotplug and AIO state events, LUN reset/TMF completion, heartbeat/offline detection, soft reset, OFA and controller-log memory events, and removal paths for graceful and surprise unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi.h -->
