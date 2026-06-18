# Research: subset-b-005546

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.c

Purpose: implements the mlx5 VFIO PCI vendor command layer for migration and dirty-page logging. It wraps mlx5 firmware commands for VHCA suspend/resume, migration-state query/save/load, protection-domain and mkey-backed DMA buffers, and the page-tracker object used by VFIO log ops.

Important APIs and functions: `mlx5vf_cmd_suspend_vhca()`, `mlx5vf_cmd_resume_vhca()`, `mlx5vf_cmd_query_vhca_migration_state()`, `mlx5vf_cmd_save_vhca_state()`, `mlx5vf_cmd_load_vhca_state()`, `mlx5vf_cmd_set_migratable()`, `mlx5vf_start_page_tracker()`, `mlx5vf_stop_page_tracker()`, and `mlx5vf_tracker_read_and_clear()`. Buffer helpers allocate pages, DMA map them with IOVA when possible, create mlx5 mkeys, and cache buffers on migration-file lists.

Control flow: initialization checks that the PCI function is a VF, obtains the mlx5 core device, validates migration capabilities, resolves VF id and VHCA id, registers an SR-IOV notifier, and installs migration/log callbacks. Save commands are asynchronous: they acquire `save_comp`, submit `SAVE_VHCA_STATE`, then the callback appends a migration header and data buffer to the readable stream or queues cleanup work on errors. Dirty logging builds a CQ plus host/FW RC QPs, creates a PAGE_TRACK object over VFIO IOVA ranges, modifies it to REPORTING on read-and-clear, drains CQEs into an `iova_bitmap`, and reposts receive WQEs.

State and persistence: state is in memory only in `mlx5vf_pci_core_device`, `mlx5_vf_migration_file`, buffer lists, completions, and tracker resources. Firmware state is serialized through the migration stream, where records use `mlx5_vf_migration_header` with mandatory FW data and optional stop-copy-size tags. Resources are freed on close, detach, stop logging, or reset.

Dependencies and integration: depends on mlx5 core command layouts, SR-IOV notifications, DMA/IOMMU APIs, VFIO migration/log ops, completion workqueues, and `iova_bitmap`. It integrates with `main.c` state transitions and exposes capability-dependent pre-copy, stop-copy, P2P, chunk-mode, and logging behavior.

Risks: concurrency is subtle around `state_mutex`, `save_comp`, async callbacks, and reset/detach paths. DMA mapping and mkey cleanup must stay balanced. Page-tracker error events, CQ poll errors, and firmware state errors must propagate to VFIO callers or migration can silently lose dirty pages. Chunk mode also relies on preserving buffer/header ownership across reads.

Test signals: exercise capability gating on supported and unsupported VFs, save/load migration streams including pre-copy cleanup and optional tags, async save failure paths, detach notifications, reset while migration/logging is active, dirty log start/read/stop, combined IOVA range fallback, and DMA mapping failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.h

Purpose: declares the shared mlx5 VFIO migration data model and command APIs used by `cmd.c` and `main.c`.

Important APIs and types: defines migration file states (`MLX5_MIGF_STATE_*`), resume stream parser states, migration record tags and flags, `mlx5_vf_migration_header`, `mlx5_vhca_data_buffer`, async save state, stop-copy work state, `mlx5_vf_migration_file`, CQ/QP/page-tracker structs, and the top-level `mlx5vf_pci_core_device`. It also declares VFIO command, migration-file, buffer, and page-tracker helpers.

Control flow and state: this header encodes the lifecycle shared across the driver: migration files own anonymous FDs, stream positions, record sizes, per-chunk buffers, poll wait queues, async command context, and buffer reuse lists. The device object embeds the VFIO core device, capability flags, current VFIO migration state, active save/restore files, reset coordination, tracker state, workqueue, notifier, and mlx5 core handle.

Dependencies and integration: includes VFIO PCI core, mlx5 driver, vport, CQ, and QP headers. Its prototypes are the internal contract between `main.c` state-machine/file operations and `cmd.c` firmware operations.

Risks: bitfield state flags and arrayed chunk buffers are shared across async and synchronous paths, so any API misuse can produce leaks or stale stream state. Locking assumptions are implicit in callers; several helpers require `state_mutex`.

Test signals: compile coverage across mlx5 capability options, lockdep paths for functions requiring `state_mutex`, chunk and non-chunk migration, and page-tracker start/stop/read cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/main.c

Purpose: implements the VFIO device operations and migration-file userspace ABI for mlx5 VFs. It converts VFIO migration state transitions into mlx5 firmware suspend/resume/save/load commands and exposes anonymous read/write FDs for migration data.

Important APIs and functions: save-side file ops (`mlx5vf_save_read()`, `mlx5vf_save_poll()`, `mlx5vf_precopy_ioctl()`), restore-side write parser (`mlx5vf_resume_write()` and helpers), migration transitions (`mlx5vf_pci_step_device_state_locked()` and `mlx5vf_pci_set_device_state()`), reset cleanup (`mlx5vf_state_mutex_unlock()`, AER reset handler), and VFIO ops/probe/remove glue.

Control flow: save setup allocates a migration file, PD, buffers, optional stop-copy chunk buffers, optional pre-copy tracking, and submits an initial save. Reads are stream based and consume queued header/data buffers; in pre-copy, temporary lack of data returns `-ENOMSG`, while final completion acts as EOF. Pre-copy ioctl reports initial/dirty bytes and can trigger new incremental saves. Restore writes parse headers, optional tag data, and FW image records, reallocating buffers as needed before invoking `LOAD_VHCA_STATE`.

State and persistence: no persistent disk state. Migration state lives in `mvdev->mig_state`, active `saving_migf`/`resuming_migf`, stream offsets, buffer lists, and firmware image records. `deferred_reset` ensures reset cleanup occurs after lock-sensitive paths complete.

Dependencies and integration: relies on `cmd.c` for mlx5 firmware commands and buffer cleanup, VFIO core for state arcs and common PCI ops, anon inodes for migration FDs, and pci driver override matching for Mellanox VF devices.

Risks: stream-position expectations are strict; out-of-order reads put the file into error. Reset and close paths must cancel async work and cleanup resources without deadlocking with VFIO/mm locks. Resume parser validates record size against `MAX_LOAD_SIZE` but optional unknown mandatory tags fail migration.

Test signals: migration arc tests for RUNNING/P2P/PRE_COPY/STOP_COPY/RESUMING, blocking and nonblocking reads, pre-copy `VFIO_DEVICE_FEATURE_MIG_PRECOPY_INFO`, optional stop-copy-size tag handling, reset during active migration, FD close while async save is inflight, and malformed restore streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Kconfig

Purpose: adds the `NVGRACE_GPU_VFIO_PCI` tristate for VFIO assignment support for NVIDIA Grace Hopper/Grace Blackwell GPU devices with coherent device memory.

Important configuration: it depends on `ARM64` or `COMPILE_TEST && 64BIT`, selects `VFIO_PCI_CORE`, and documents that the module is intended for assigning the GPU to userspace through KVM/QEMU-style VFIO flows.

Control flow and integration: selecting this config builds the `nvgrace-gpu-vfio-pci` module from the companion Makefile. It gates the specialized VFIO PCI driver that can expose ACPI-described GPU memory as fake VFIO BAR regions.

Risks: enabling on unsupported platforms is compile-test only; runtime behavior depends on ACPI/device properties and NVIDIA device IDs in `main.c`.

Test signals: Kconfig dependency resolution for ARM64 and compile-test builds, module selection, and ensuring `VFIO_PCI_CORE` is selected automatically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Makefile

Purpose: wires the NVGrace GPU VFIO PCI module into kbuild.

Important build behavior: `obj-$(CONFIG_NVGRACE_GPU_VFIO_PCI)` emits `nvgrace-gpu-vfio-pci.o`, and the module is built from `main.o`.

Dependencies and integration: this is the build companion to the Kconfig option and has no runtime logic. It follows normal single-object module composition.

Risks and test signals: build failures will surface through missing dependencies in `main.c`; useful tests are `allyesconfig`/`allmodconfig` and ARM64 compile-test coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/main.c

Purpose: provides a VFIO PCI driver for NVIDIA Grace Hopper/Blackwell GPU PFs whose coherent device memory is described outside normal BAR sizing. It exposes usable and reserved GPU memory to guests through emulated 64-bit BAR regions and custom mmap/read/write behavior.

Important APIs and types: `struct mem_region`, `struct nvgrace_gpu_pci_core_device`, VFIO ops for open/close/ioctl/read/write/mmap/get_region_info, config-space BAR emulation, pfn address-space registration, P2P dmabuf physical range reporting, ACPI property parsing, device-ready polling, and reset tracking.

Control flow: probe first waits for C2C/HBM readiness through BAR0, reads ACPI memory properties, selects either enhanced ops or core fallback ops, detects the MIG hardware bug via NVIDIA DVSEC, partitions memory into `usemem` and optional `resmem`, and registers the VFIO device. Open enables VFIO core, initializes fake BAR values, maps BAR0, and registers PFN address spaces. Mmap routes fake BAR offsets to PFNMAP VMAs whose faults insert PFNs after runtime power and readiness checks. Read/write either emulate config BAR registers or map device memory with `memremap()`/`ioremap_wc()` and copy data.

State and persistence: in-memory state records physical address, actual length, rounded BAR size, emulated BAR value, kernel mapping, pfn address space, reset-readiness flag, and whether the old MIG workaround is needed. Mappings are lazily created and freed on close.

Dependencies and integration: uses VFIO PCI core, iommufd physical attach ops, pfn address-space helpers, runtime PM, PCI P2PDMA provider APIs, ACPI device properties, PCI config-space emulation, and memory-failure PFN mapping support.

Risks: fake BAR sizes are rounded up while real memory may be smaller, so reads beyond real memory must return all ones and writes must be dropped. First access after reset must be serialized against readiness polling to avoid RAS noise. Incorrect `resmem` cache attributes or pfn offset translation can break guest mappings.

Test signals: probe with and without ACPI properties, GH MIG-bug and GB fixed paths, config BAR read/write emulation, sparse region info, mmap faults including huge PFNMAP if enabled, read/write past actual but within reported BAR size, reset-done followed by first access, and P2P dmabuf range queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Kconfig

Purpose: adds the `PDS_VFIO_PCI` tristate for AMD/Pensando PDS VFIO PCI support.

Important configuration: it depends on `PDS_CORE && PCI_IOV`, selects `VFIO_PCI_CORE` and `IOMMUFD_DRIVER`, and documents the module name `pds-vfio-pci` plus the related PDS VFIO documentation.

Control flow and integration: this config enables the PDS VF migration/logging driver built by the local Makefile. The dependencies ensure the PF-side PDS core and SR-IOV support are present.

Risks and test signals: build coverage should verify dependency gating and namespace imports. Runtime behavior is only meaningful for Pensando VF device IDs handled in `pci_drv.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Makefile

Purpose: composes the PDS VFIO PCI module.

Important build behavior: `pds-vfio-pci.o` is built when `CONFIG_PDS_VFIO_PCI` is set and includes `cmds.o`, `dirty.o`, `lm.o`, `pci_drv.o`, and `vfio_dev.o`.

Dependencies and integration: the object split mirrors the runtime architecture: PF admin commands, dirty tracking, live-migration files, PCI driver registration, and VFIO device operations.

Risks and test signals: stale object lists would omit migration or logging functionality; build tests should cover module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.c

Purpose: implements PDS firmware/admin-queue commands used by the VFIO migration and dirty logging layers.

Important APIs: client registration/unregistration, `pds_vfio_suspend_device_cmd()`, `pds_vfio_resume_device_cmd()`, migration state size/save/restore commands, host VF migration status notification, dirty status/enable/disable, and dirty sequence/ack commands.

Control flow: commands are wrapped as `PDS_AQ_CMD_CLIENT_CMD` and sent through the PF `pdsc_adminq_post()` path using the registered client id. Suspend is two-phase: send suspend, then poll suspend-status with fast polling until completion or timeout. Migration save/restore maps the anonymous migration file scatterlist for DMA, builds a PDS SGL, issues SAVE or RESTORE, and unmaps afterward. Dirty tracking commands exchange region descriptors and sequence/ack SGLs with firmware.

State and persistence: persistent state is firmware-side; driver state includes `client_id`, DMA-mapped SGL addresses, and file/dirty-region metadata owned elsewhere. Command functions balance DMA mappings around each request.

Dependencies and integration: depends on PDS core interfaces, PF lookup through `pdsc_get_pf_struct()`, adminq command layouts, DMA APIs, `lm.c` migration files, and `dirty.c` region tracking.

Risks: failures in adminq, DMA mapping, or firmware status polling abort VFIO state transitions. The dirty-status path currently requires SEQ_ACK bitmap support. Correct endian conversion and SGL length reporting are essential.

Test signals: client registration lifetime, suspend timeout, adminq `-EAGAIN` polling, save/restore DMA mapping failures, dirty capability absence, dirty disable returning nonzero regions, and seq/ack read/write command errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.h

Purpose: declares the PDS admin-command API consumed by migration, dirty tracking, and PCI driver code.

Important APIs: prototypes cover client lifecycle, suspend/resume, migration state size/save/restore, host-VF migration status, dirty status/enable/disable, and seq/ack bitmap exchange.

Control flow and integration: this header is the narrow boundary between high-level VFIO state code and low-level PDS PF firmware commands. It intentionally exposes no structures beyond the PDS VFIO device pointer and command parameters.

Risks and test signals: signature changes ripple across `lm.c`, `dirty.c`, and `pci_drv.c`; compile tests catch most integration drift, while runtime tests must validate command ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.c

Purpose: implements PDS VFIO dirty-page logging using firmware SEQ_ACK bitmaps.

Important APIs and functions: `pds_vfio_dma_logging_start()`, `pds_vfio_dma_logging_stop()`, `pds_vfio_dma_logging_report()`, bitmap allocation/free helpers, dirty region construction, `pds_vfio_dirty_seq_ack()`, and bitmap processing into VFIO `iova_bitmap`.

Control flow: start marks host VF migration in progress, confirms dirty logging is disabled and supported, combines IOVA ranges if firmware has fewer region slots, sends region descriptors to firmware, allocates per-region host sequence/ack bitmaps and DMA SGLs, and marks logging enabled. Report validates that the requested IOVA range is inside a tracked region, computes bitmap offset/length in 64-bit aligned chunks, reads device sequence bits, XORs with host ack bits, sets dirty IOVAs, copies seq to ack, and writes ack back. Stop disables firmware tracking, frees SGLs/bitmaps/regions, and clears host VF migration status.

State and persistence: `struct pds_vfio_dirty` owns an array of regions and enabled flag. Each region stores host bitmaps, device bitmap offset, SGL DMA address, start/size/page size, and region bitmap byte count. All state is in memory and cleaned on stop, close, reset error, or failed enable.

Dependencies and integration: depends on PDS admin commands, interval trees from VFIO ranges, DMA mapping through the PF device, vmalloc-backed bitmap pages, and VFIO log ops.

Risks: range math and bitmap offset alignment are critical; mistakes can miss or over-report dirtied pages. The code assumes requests fit a single tracked region. DMA direction differs for read_seq and write_ack and must be synchronized correctly.

Test signals: start with overlapping/many IOVA ranges, firmware max-region combining, unsupported dirty type, zero-length and out-of-region report rejection, 64-bit bitmap alignment, dirty XOR/ack correctness, stop idempotency, and failure cleanup after partial allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.h

Purpose: defines PDS dirty logging state and declares VFIO log-op entry points.

Important types: `struct pds_vfio_region` tracks per-region host sequence/ack bitmaps, bitmap bytes, IOVA start/size/page size, firmware SGL, DMA address, device bitmap byte offset, and SGE count. `struct pds_vfio_dirty` stores region array, count, and enabled flag.

Control flow and integration: higher layers call enable/disable helpers from migration state paths and expose VFIO log callbacks through `vfio_dev.c`. The structs are filled and freed in `dirty.c`.

Risks and test signals: consumers must hold `state_mutex` around dirty state changes. Tests should cover enabled flag transitions and cleanup after reset or close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.c

Purpose: implements PDS live-migration anonymous files and VFIO migration state transition actions.

Important APIs and functions: migration file allocation/free, save read file op, restore write file op, `pds_vfio_step_device_state_locked()`, `pds_vfio_put_save_file()`, and `pds_vfio_put_restore_file()`.

Control flow: save file creation queries firmware state size, allocates a vmalloc-backed page buffer, creates a scatterlist for DMA, then `pds_vfio_get_lm_state_cmd()` fills it. User reads sequentially through page lookup. Restore creates a fixed-size state file, accepts sequential writes into pages, and on RESUMING->STOP issues `pds_vfio_set_lm_state_cmd()`. State transitions also drive full/P2P suspend/resume and dirty-disable cleanup.

State and persistence: `struct pds_vfio_lm_file` stores the anon inode, lock, current valid size, allocated size, backing pages, SG table, DMA SGL, and sequential lookup cache. File disable zeroes size and resets offsets; final release destroys lock and frees the wrapper.

Dependencies and integration: depends on VFIO migration arcs from `vfio_dev.c`, firmware commands from `cmds.c`, PDS admin data structures, anon inodes, highmem mapping, and scatterlist/DMA APIs.

Risks: restore writes increment `size` and must not exceed allocated state length. File lifetime uses an extra reference; release and driver cleanup must not double free. Sequential page lookup caching must reset correctly for backward offsets.

Test signals: save and restore FD creation, short reads/writes, disabled FD behavior, invalid offsets, migration arc coverage, suspend/resume command failures, restore command failure, and close/reset cleanup while FDs are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.h

Purpose: declares PDS live-migration file state and transition helpers.

Important types and APIs: `struct pds_vfio_lm_file` captures anonymous file, lock, sizes, page memory, pages, SG table, firmware SGL, sequential lookup cache, and disabled flag. Prototypes expose the locked state-step function and save/restore file cleanup helpers.

Control flow and integration: this header connects `vfio_dev.c` migration ops to `lm.c`, and lets reset/close paths release active files.

Risks and test signals: the struct mixes file lifetime, DMA mapping metadata, and sequential read/write cache; tests should stress cleanup on partially initialized files and repeated state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.c

Purpose: registers the AMD/Pensando PDS VFIO PCI driver and handles PF-client registration and recovery notifications.

Important APIs and functions: `pds_vfio_pci_probe()`, `pds_vfio_pci_remove()`, PDS event notifier registration, reset/recovery handling, AER reset handler, and PCI driver table matching Pensando Ethernet VF override IDs.

Control flow: probe allocates the VFIO device, registers it with VFIO PCI core, registers as a PDS client, and subscribes to PDS reset notifications. On reset-complete notifications, if migration or dirty tracking is active, it moves the VFIO migration state to ERROR because kernel migration drivers must not asynchronously transition to a normal state outside user/VFIO reset control. Remove unregisters notifier, client, VFIO core device, and device reference.

State and persistence: stores notifier callback in `pds_vfio->nb` and the firmware client id through `cmds.c`. Recovery updates in-memory VFIO state and releases migration/dirty resources through `pds_vfio_reset()`.

Dependencies and integration: depends on PDS core notify APIs, VFIO allocation/register helpers, PDS command registration, and `vfio_dev.c` device ops.

Risks: notifier lifetime must be torn down before device release. Recovery must not silently resume migration after PF reset, or userspace could believe stale device state is valid. Probe unwinding must unregister in reverse order.

Test signals: probe failure at each stage, client unregister on remove, PDS reset notification while running, while stop-copy/resuming, and while dirty logging is enabled, plus AER reset-done path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.h

Purpose: minimal include guard for PDS PCI driver declarations.

Important content: includes `<linux/pci.h>` but currently declares no functions or types.

Integration: included by `pci_drv.c`, likely reserved for future PCI-driver shared declarations.

Risks and test signals: no runtime risk. Compile tests catch include guard or dependency issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.c

Purpose: implements the PDS VFIO device operations, migration ops, log ops, state storage, and shared helpers.

Important APIs and functions: device pointer helpers, `pds_vfio_reset()`, migration set/get/data-size ops, log ops binding to dirty tracking, init/release/open/close VFIO device ops, and `pds_vfio_ops_info()`.

Control flow: init resolves VF id, initializes VFIO PCI core and mutex, sets migration flags for stop-copy and P2P, and installs migration/log ops. Open enables the PCI device and sets migration state to RUNNING. Set-state loops through VFIO-approved next states and delegates each transition to `lm.c`. Close releases active migration files, disables dirty logging, and closes VFIO core.

State and persistence: top-level state is in `struct pds_vfio_pci_device`: active save/restore files, dirty logging state, state mutex, current migration state, notifier block, VF id, and PDS client id.

Dependencies and integration: integrates VFIO PCI core, iommufd ops, migration file logic, dirty logging, and PCI driver client/notification setup. `pds_vfio_reset()` is shared with recovery and AER paths.

Risks: state ERROR is sticky until VFIO reset; set-state avoids asking VFIO core for transitions out of ERROR. Close and reset must release files and dirty resources under `state_mutex`. Data-size is a fixed PDS device-state constant, not queried dynamically.

Test signals: open/close, state transition errors, ERROR handling, fixed data-size reporting, log op start/report/stop through VFIO, and reset cleanup from both AER and PF recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.h

Purpose: declares the PDS VFIO device object and shared helper APIs.

Important types and APIs: `struct pds_vfio_pci_device` embeds `vfio_pci_core_device`, active migration files, dirty state, state mutex, current VFIO migration state, notifier block, VF id, and PDS client id. It declares ops lookup, drvdata conversion, reset helper, and device/pci conversion helpers.

Control flow and integration: used by every PDS implementation file as the central state container. It ties together VFIO core, live migration, dirty logging, PDS notifications, and command client identity.

Risks and test signals: shared state must be protected consistently by `state_mutex`; compile tests catch cross-file API drift, and runtime tests should validate cleanup when any embedded subsystem is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Kconfig

Purpose: adds `QAT_VFIO_PCI`, a VFIO PCI migration driver for Intel QAT VFs.

Important configuration: selects `VFIO_PCI_CORE` and depends on one of the QAT PF drivers (`CRYPTO_DEV_QAT_4XXX`, `420XX`, or `6XXX`). Help text identifies the module name `qat_vfio_pci`.

Control flow and integration: this option enables the QAT VFIO PCI module built from `main.c`, relying on the QAT migration device API exported by the crypto QAT driver.

Risks and test signals: dependency coverage must prevent builds without QAT migration symbols. Build tests should include module and built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Makefile

Purpose: wires the QAT VFIO PCI migration module into kbuild.

Important build behavior: `obj-$(CONFIG_QAT_VFIO_PCI)` creates `qat_vfio_pci.o` from `main.o`.

Dependencies and integration: the module imports the `CRYPTO_QAT` namespace in `main.c`.

Risks and test signals: build tests should verify symbol namespace import and all QAT generation dependency combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/main.c

Purpose: implements VFIO PCI live migration support for Intel QAT virtual functions using the QAT PF migration-device API.

Important APIs and types: `struct qat_vf_migration_file`, `struct qat_vf_core_device`, save/read and resume/write file ops, pre-copy ioctl, state transition handler, reset handling, VFIO ops/probe/remove glue, and QAT migration calls such as `qat_vfmig_save_setup()`, `save_state()`, `load_setup()`, `load_state()`, `suspend()`, and `resume()`.

Control flow: init installs migration flags for stop-copy, P2P, and pre-copy, initializes VFIO core, finds the PF and VF id, creates and initializes a QAT migration device. Open enables VFIO core and opens QAT migration. Pre-copy saves setup data only and reports remaining setup bytes; stop-copy saves full device state. Restore writes into the QAT state buffer and repeatedly calls setup-load until enough data is available, then RESUMING->STOP loads final state. P2P arcs fully suspend/resume the VF because QAT cannot stop only P2P DMA.

State and persistence: migration data is held in the QAT migration device `state` buffer plus per-FD `filled_size` and disabled flags. Device migration state and active save/restore files are protected by `state_mutex`. There is no disk persistence.

Dependencies and integration: depends on VFIO PCI core, anon inodes, QAT migration API under `CRYPTO_QAT`, PCI VF/PF relationships, and VFIO migration arc helpers.

Risks: write bounds use `state_size`; bad size or repeated writes can fail restore. Pre-copy only carries setup data, so stop-copy must refresh full state. Reset must call QAT reset and disable FDs under the state lock. Errors from `qat_vfmig_load_setup()` other than `-EAGAIN` abort restore early.

Test signals: QAT generations in PCI id table, init failure unwinds, open/close QAT migration lifetime, pre-copy info/read behavior, stop-copy state refresh after pre-copy P2P, restore setup compatibility failures, final load failure, reset during active FDs, and P2P suspend/resume arcs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/trace.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/trace.h

Purpose: defines VFIO PCI tracepoints for mmap and mmap fault diagnostics.

Important APIs: trace events `vfio_pci_nvgpu_mmap_fault`, `vfio_pci_nvgpu_mmap`, and `vfio_pci_npu2_mmap` capture PCI device name, host physical address, user address, mapping size when applicable, and return status.

Control flow and integration: standard Linux tracepoint header pattern declares `TRACE_SYSTEM vfio_pci`, event payloads, print formats, and includes `trace/define_trace.h` outside the include guard. `TRACE_INCLUDE_PATH` points back to the driver source directory.

State and persistence: tracepoints persist only in tracing buffers when enabled; they do not change device state.

Dependencies and risks: depends on tracepoint infrastructure and `struct pci_dev`. Event names include older NVGPU/NPU2 mapping flows; userspace tooling may depend on field names. Incorrect include path breaks trace generation.

Test signals: compile with tracing enabled, validate trace event format files under tracefs, and exercise mmap fault paths in drivers that call these tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci.c

Purpose: implements the generic `vfio-pci` meta-driver that binds arbitrary PCI devices to VFIO using common VFIO PCI core operations.

Important APIs and functions: module parameters for dynamic IDs, INTx masking, VGA resource access, idle D3, SR-IOV, and denylist override; denylist checks for known unsafe Intel QAT/DSA/IAX devices; `vfio_pci_open_device()`, generic VFIO device ops, probe/remove, SR-IOV configure, dynamic id parser, init/exit.

Control flow: module init pushes parameters into VFIO PCI core, registers the PCI driver, and adds dynamic IDs from the `ids` module parameter. Probe rejects denylisted devices unless overridden, allocates a `vfio_pci_core_device`, attaches generic PCI ops including dmabuf physical lookup, and registers the VFIO device. Open enables VFIO core and optionally sets up Intel IGD-specific regions before finishing enable. SR-IOV configure is allowed only when the module parameter is enabled.

State and persistence: static module parameters govern runtime behavior. Per-device state is allocated in VFIO core and stored as driver data; no persistent storage is used.

Dependencies and integration: depends on VFIO PCI core/private helpers, PCI dynamic IDs, optional VGA/IGD support, iommufd attach/detach including PASID ops, and core error handlers.

Risks: disabling the denylist can expose devices with known stability/security errata to untrusted userspace. SR-IOV enablement without a PF userspace driver can create nonfunctional VFs. Dynamic ID parsing must reject malformed strings without corrupting the driver id table.

Test signals: module parameter matrix, denylist allow/block paths, dynamic id parsing, probe failure unwind, Intel IGD open path, SR-IOV configure with and without `enable_sriov`, iommufd attach/detach/PASID ops, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci.c -->
