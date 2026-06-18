# subset-b-005587 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_mem.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_mem.c

## Purpose
`virtio_mem.c` is the Linux virtio-mem driver. It exposes hypervisor-controlled memory as Linux hotplug memory, reconciles the device `requested_size` with the guest's `plugged_size`, and makes unplugged ranges inaccessible or fake-offline so the kernel never allocates memory that the device has not actually plugged. It supports two operating models: sub-block mode (SBM), where a Linux memory block is tracked as multiple virtio-mem subblocks, and big-block mode (BBM), where each tracked unit spans one or more Linux memory blocks.

## Important APIs, types, and functions
- Module parameters `unplug_online`, `force_bbm`, and `bbm_block_size` influence unplug policy and block-mode selection.
- `struct virtio_mem` owns the virtio device, virtqueue, config cache, memory-hotplug state, retry timer, notifier blocks, parent resource, memory group id, kdump vmcore callback state, and either `sbm` or `bbm` tracking arrays.
- `enum virtio_mem_sbm_mb_state` and `enum virtio_mem_bbm_bb_state` model Linux memory-block and big-block lifecycle states.
- `virtio_mem_probe()`, `virtio_mem_init()`, `virtio_mem_init_hotplug()`, `virtio_mem_remove()`, and the `virtio_driver` table implement the virtio lifecycle.
- `virtio_mem_run_wq()` is the central reconciliation loop for config changes, cleanup, plug requests, unplug requests, retry backoff, and fatal error handling.
- `virtio_mem_send_request()`, `virtio_mem_send_plug_request()`, `virtio_mem_send_unplug_request()`, `virtio_mem_send_unplug_all_request()`, and kdump-only `virtio_mem_send_state_request()` are the guest-to-host request path over the single virtqueue.
- SBM helpers maintain `mb_states` and `sb_states`, prepare tracking arrays, plug/unplug subblocks, add/remove memory blocks, and react to online/offline notifications.
- BBM helpers maintain `bb_states`, plug/add big blocks, fake-offline online pages, remove Linux memory, and unplug whole big blocks.
- `virtio_mem_memory_notifier_cb()` and `virtio_mem_online_page_cb()` integrate with Linux memory hotplug and online-page handling.
- `virtio_mem_fake_offline()`, `virtio_mem_fake_online()`, `virtio_mem_set_fake_offline()`, and notifier helpers implement the PG_offline/page-ref choreography for unplugging online memory safely.

## Control flow
Probe allocates `struct virtio_mem`, initializes the virtqueue and synchronization objects, reads immutable config fields (`plugged_size`, `block_size`, NUMA node, address range), and either enters kdump mode or normal hotplug mode. Hotplug initialization chooses SBM when the virtio device block size and pageblock granularity allow subblocks inside a Linux memory block; otherwise it uses BBM with a power-of-two big block size. It reserves the device address range as a parent `System RAM` resource, registers a dynamic memory group, registers memory and PM notifiers, installs the shared online-page callback, marks the device ready, and queues initial work.

The workqueue cancels pending retry timers, refreshes device config when `config_changed` is set, cleans up previously half-failed plug/unplug state, then compares `requested_size` and `plugged_size`. If the host requests more memory, SBM first fills partially plugged online/offline memory blocks, then reuses unused blocks, then prepares new blocks; BBM reuses or prepares whole big blocks. If the host requests less memory, SBM prioritizes offline and partially plugged memory, then movable online memory, then kernel memory if `unplug_online` permits; BBM first removes offline blocks, then movable blocks, then any online block if allowed. Busy host/device states, busy guest pages, and allocation pressure map to retry behavior through an hrtimer with exponential backoff.

Memory online/offline callbacks serialize state changes with `hotplug_mutex`. Going online is rejected for unexpected SBM states. Onlining converts offline states to kernel or movable states based on the target zone, and the online-page callback only releases actually plugged subblocks while keeping unplugged ranges fake-offline. Offlining transitions online states back to offline and may schedule immediate work if unplugging offline-only memory. Device config changes only set an atomic flag and queue the workqueue; the main loop then rereads size and usable-range fields.

Kdump mode is special: hotplug is disabled, the device is marked ready, and `/proc/vmcore` callbacks query per-device-block state from the host so crash dump code can identify RAM without plugging or unplugging anything.

## State and persistence behavior
All persistent state is in memory and device config, not on disk. `plugged_size` is the driver's reflection of successful host plug/unplug requests, while `requested_size` and `usable_region_size` are refreshed from device config. SBM persists one byte per tracked Linux memory block plus a bitmap of plugged subblocks; counters summarize states and `have_unplugged_mb` records cleanup debt. BBM persists one byte per big block plus counters. `offline_size` throttles how much newly added but not-yet-onlined memory can accumulate. `parent_resource`, `resource_name`, and `mgid` tie device memory into the Linux resource and memory-group model.

Removal prevents new work, cancels work/timers, removes partially plugged offline SBM blocks, unregisters callbacks, and only releases the parent resource and memory group if no system RAM from the device remains. If memory is still added, the driver warns because Linux has no reliable way to remove all added memory during device removal. Suspend resets queues unless persistent suspend is supported and blocks unsafe suspend/hibernation with plugged memory.

## Dependencies and integration points
The file integrates the virtio core, virtqueue API, Linux memory hotplug, memory groups, resource management, NUMA/ACPI PXM translation, page allocator `alloc_contig_range()`, `generic_online_page()`, PM notifiers, kdump vmcore callbacks, RCU for the global device list, and the virtio-mem UAPI config/request structures. It relies on `VIRTIO_MEM_F_UNPLUGGED_INACCESSIBLE`, optional `VIRTIO_MEM_F_ACPI_PXM`, and optional `VIRTIO_MEM_F_PERSISTENT_SUSPEND`.

## Risks and test signals
Main risks are races with memory onlining/offlining, partially successful host plug/unplug requests, MM cleanup gaps after `add_memory_driver_managed()` failures, retry loops under host busy or guest memory pressure, unsafe forced module removal with memory still added, and PG_offline/page reference accounting mistakes. BBM also relies on section-sized fake-offline chunks and can be coarse. Test signals include probe on aligned and misaligned regions, SBM and BBM selection, requested-size grow/shrink, offline threshold behavior, online-page treatment of unplugged ranges, `unplug_online=0`, ZONE_MOVABLE unplug success, busy page retry, config-change during unplug, kdump `/proc/vmcore` RAM filtering, suspend/restore behavior, and clean remove after all memory is unplugged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_mmio.c

## Purpose
`virtio_mmio.c` implements the memory-mapped virtio transport for platform devices. It maps a virtio-mmio register window, exposes it as a `struct virtio_device`, provides virtio config operations, creates vrings, handles the single transport interrupt, and supports device instantiation via platform resources, Device Tree, ACPI, or a command-line/module parameter.

## Important APIs, types, and functions
- `struct virtio_mmio_device` embeds `struct virtio_device` and stores the platform device, MMIO base, and transport version.
- `vm_get_features()`, `vm_finalize_features()`, `vm_get()`, `vm_set()`, `vm_generation()`, `vm_get_status()`, `vm_set_status()`, and `vm_reset()` implement config access.
- `vm_notify()` and `vm_notify_with_data()` write queue notifications.
- `vm_interrupt()` acknowledges config and vring interrupts and fans out to `virtio_config_changed()` and `vring_interrupt()`.
- `vm_setup_vq()`, `vm_find_vqs()`, `vm_del_vq()`, `vm_del_vqs()`, and `vm_synchronize_cbs()` manage virtqueues and IRQ lifetime.
- `vm_get_shm_region()` reads shared-memory region descriptors.
- `virtio_mmio_probe()` validates magic/version/device id, configures DMA masks, maps resources, and registers the virtio device.
- Optional `vm_cmdline_set()` and related helpers create platform devices from `virtio_mmio.device=`.

## Control flow
Probe allocates the transport wrapper, maps BAR-like platform resource 0, checks the magic value and version, rejects dummy device id 0, records vendor/device ids, initializes legacy guest page size for version 1, sets DMA masks, stores driver data, and calls `register_virtio_device()`. Feature negotiation reads high and low feature words, lets vring code consume transport features, enforces that version 2 devices negotiate `VIRTIO_F_VERSION_1`, and writes selected features back.

Queue discovery requests the platform IRQ once, optionally enables wakeup for Device Tree `wakeup-source`, then creates each named virtqueue in order. `vm_setup_vq()` selects the queue, rejects unavailable or already-active queues, creates a split vring, writes queue size and descriptor addresses, and activates either legacy `QUEUE_PFN` or modern descriptor/avail/used address registers. Interrupt handling reads and acknowledges the interrupt status before dispatching config and vring events.

## State and persistence behavior
State lasts for the platform device lifetime: MMIO base, transport version, registered virtio device, active vrings, and IRQ registration. No persistent storage exists. Command-line devices persist only as platform devices created under `vm_cmdline_parent` until module exit, where they are unregistered. Freeze/restore delegates to virtio core and rewrites version-1 guest page size on restore.

## Dependencies and integration points
The driver depends on platform resources, IRQ APIs, OF/ACPI matching, DMA masks, virtio core, virtio ring, and UAPI `virtio_mmio.h`. It is the transport used by virtio device drivers above it, and it must match the MMIO register ABI for legacy v1 and modern v2 devices.

## Risks and test signals
Risk areas include legacy v1 32-bit PFN limits, non-atomic 64-bit device config reads/writes split into two 32-bit accesses, missing or shared IRQ handling, dummy devices, bad command-line parsing, and devices that violate version/feature requirements. Test signals include DT/ACPI/cmdline probe, invalid magic/version rejection, v1 high-memory vring failure, v2 feature negotiation requiring `VERSION_1`, queue creation/deletion, config-change interrupts, vring interrupts, wakeup-source behavior, shared-memory region discovery, and freeze/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_admin_legacy_io.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_admin_legacy_io.c

## Purpose
`virtio_pci_admin_legacy_io.c` exports helper APIs that let callers access a VF's legacy virtio common/device configuration and notification information through the PF's modern virtio admin virtqueue. It is used when a modern SR-IOV PF supports admin commands that proxy legacy I/O semantics for member devices.

## Important APIs, types, and functions
- `virtio_pci_admin_has_legacy_io()` checks that the PF virtio device exists, negotiated `VIRTIO_F_ADMIN_VQ`, and advertised all legacy admin command bits.
- `virtio_pci_admin_legacy_common_io_write()` and `virtio_pci_admin_legacy_device_io_write()` wrap `virtio_pci_admin_legacy_io_write()` for common and device config writes.
- `virtio_pci_admin_legacy_common_io_read()` and `virtio_pci_admin_legacy_device_io_read()` wrap `virtio_pci_admin_legacy_io_read()` for reads.
- `virtio_pci_admin_legacy_io_notify_info()` requests legacy queue notify BAR/offset information matching caller-specified BAR flags.
- All exported functions are `EXPORT_SYMBOL_GPL` APIs for other virtio PCI/SR-IOV code.

## Control flow
Each operation starts from a VF `struct pci_dev`, resolves the owning PF's `struct virtio_device` via `virtio_pci_vf_get_pf_dev()`, obtains the VF group member id with `pci_iov_vf_id() + 1`, builds a `struct virtio_admin_cmd`, attaches data and/or result scatterlists, and executes the command through `vp_modern_admin_cmd_exec()`. Read commands use a small data descriptor for offset and a caller-provided result buffer. Write commands allocate a variable-sized payload containing offset plus register bytes. Notify-info parses returned entries until an END flag or a matching flag entry is found.

## State and persistence behavior
This file owns no persistent state. It allocates temporary command payload/result structures per call and depends on the PF admin virtqueue state stored in `struct virtio_pci_device`. The caller is explicitly responsible for serializing access for a given member device, so these helpers do not add per-VF locking.

## Dependencies and integration points
It depends on `linux/virtio_pci_admin.h`, SR-IOV PCI helpers, `virtio_pci_common.h`, and the modern admin command executor in `virtio_pci_modern.c`. It integrates PF-controlled admin virtqueue functionality with VF-oriented legacy configuration access.

## Risks and test signals
Risks include missing caller serialization, PF/VF lifetime races, unsupported command bitmaps, invalid VF ids, result parsing that returns `-ENOENT` if flags do not match, and propagation of admin command status values as negative errors. Test signals include positive/negative `virtio_pci_admin_has_legacy_io()`, read/write round trips for common and device config offsets, invalid VF handling, notify-info lookup for each BAR flag, unsupported command rejection, and concurrent caller behavior under external locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_admin_legacy_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.c

## Purpose
`virtio_pci_common.c` is the shared PCI transport driver for legacy and modern virtio-pci devices. It owns PCI probing/removal, common interrupt and virtqueue dispatch, MSI-X/INTx vector allocation policy, queue affinity, power-management reset handling, SR-IOV enablement, and PCI error reset callbacks.

## Important APIs, types, and functions
- `vp_find_vqs()`, `vp_del_vqs()`, `vp_notify()`, `vp_synchronize_vectors()`, `vp_bus_name()`, `vp_set_vq_affinity()`, and `vp_get_vq_affinity()` are shared `virtio_config_ops` helpers used by legacy and modern transports.
- `vp_request_msix_vectors()`, `vp_find_vqs_msix()`, `vp_find_vqs_intx()`, and `vp_find_one_vq_msix()` implement the vector fallback ladder.
- Interrupt handlers `vp_interrupt()`, `vp_config_changed()`, `vp_vring_interrupt()`, and `vp_vring_slow_path_interrupt()` route INTx/MSI-X events.
- `virtio_pci_probe()` chooses modern vs legacy probing, with `force_legacy` as an optional override.
- `virtio_pci_remove()`, PM callbacks, `virtio_pci_sriov_configure()`, and PCI reset handlers manage lifecycle beyond initial registration.
- `virtio_pci_vf_get_pf_dev()` exposes the PF virtio device for VF admin-command helpers.

## Control flow
Probe allocates `struct virtio_pci_device`, enables the PCI device, attempts modern or legacy transport setup, sets bus mastering, and registers the embedded virtio device. Modern setup is preferred unless `force_legacy` requests legacy first; transitional devices can fall back either way depending on capabilities and BAR availability. Removal marks the virtio device broken on surprise removal, disables SR-IOV, unregisters the virtio device, removes the selected transport, disables PCI, and releases the virtio device reference.

Virtqueue discovery first tries MSI-X with one vector per queue, then MSI-X with slow-path queues sharing the config vector, then MSI-X with one shared queue vector, then INTx. MSI-X setup always reserves a config vector first, optionally allocates a shared queue vector, and then creates requested virtqueues plus an admin virtqueue when the modern transport reports one. Queue info objects are linked onto normal or slow-path lists under `vp_dev->lock`, allowing interrupt handlers to iterate active callback queues safely. Teardown frees per-vq IRQs, config/shared IRQs, affinity masks, MSI-X allocations, queue info arrays, and transport-specific queue resources.

## State and persistence behavior
Persistent state is the `struct virtio_pci_device` allocated for each PCI function. It records whether legacy or modern transport is active, MMIO/PIO transport state in the union, ISR pointer, virtqueue lists, queue info array, admin VQ state, MSI-X names/masks/vector counts, INTx/MSI-X flags, and transport callbacks. The module parameter `force_legacy` is read-only after load. No disk persistence exists.

## Dependencies and integration points
This file depends on Linux PCI, MSI-X/IRQ APIs, virtio core, virtio ring, SR-IOV helpers, PM, and the legacy/modern transport-specific files. It is the actual `pci_driver` registered for Red Hat/Qumranet virtio PCI IDs and provides symbols consumed by admin legacy I/O and modern admin device-parts support.

## Risks and test signals
Risks include complex MSI-X fallback cleanup, queue list races with interrupts and queue reset, slow-path/admin queue vector sharing, affinity mask indexing, surprise removal, PM paths that skip reset when PCI PM reports no soft reset, and SR-IOV enablement while the virtio driver is not ready. Test signals include modern and legacy probe fallback, all MSI-X policy fallbacks, INTx operation, per-vq affinity changes, admin VQ creation, queue teardown with interrupts in flight, suspend/resume/freeze/thaw, PCI function reset, SR-IOV enable/disable gates, and surprise removal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.h -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.h

## Purpose
`virtio_pci_common.h` defines the private shared contract for the virtio-pci transport. It centralizes the per-queue, admin-queue, and per-device data structures used by common, legacy, modern, and admin helper files, and declares the cross-file operations that back `virtio_config_ops`.

## Important APIs, types, and functions
- `struct virtio_pci_vq_info` stores a virtqueue pointer, list node, and MSI-X vector.
- `struct virtio_pci_admin_vq` stores admin virtqueue metadata, spinlock, supported command/capability bitmaps, device-parts object limits, ID allocator, name, and queue index.
- `struct virtio_pci_device` embeds `struct virtio_device`, the PCI device, legacy/modern transport union, ISR pointer, queue lists, queue info array, admin VQ, MSI-X bookkeeping, transport callbacks, and optional admin-VQ index callback.
- `to_vp_device()` converts a generic virtio device to the private PCI wrapper.
- Declarations expose shared queue operations, bus naming, affinity operations, legacy/modern probe/remove, VF-to-PF lookup, admin VQ helpers, and admin command execution.
- `VIRTIO_LEGACY_ADMIN_CMD_BITMAP`, `VIRTIO_DEV_PARTS_ADMIN_CMD_BITMAP`, and `VIRTIO_ADMIN_CMD_BITMAP` define the admin command set the driver can negotiate.

## Control flow
The header has no standalone runtime flow, but its callback fields define the dispatch model: common code calls `setup_vq`, `del_vq`, and `config_vector` through function pointers installed by legacy or modern probe. Modern probe may also install `avq_index`, which lets common queue discovery create the admin virtqueue after normal queues.

## State and persistence behavior
The structs declared here are the persistent in-memory state for each virtio-pci function. The header also encodes compile-time policy: legacy admin commands are included only when `CONFIG_VIRTIO_PCI_ADMIN_LEGACY` is enabled; otherwise only device-parts admin commands are negotiated.

## Dependencies and integration points
It depends on Linux PCI, interrupt, spinlock/mutex, virtio, virtio config, virtio ring, and public legacy/modern virtio PCI headers. It is included by all virtio-pci implementation files in this work item and forms their ABI boundary.

## Risks and test signals
Risks include stale struct contracts between common and transport-specific files, admin command bitmap mismatches with device capabilities, MSI-X vector constants that must stay consistent with allocation policy, and array indexing assumptions for `vqs` vs admin queue. Test signals are build coverage under legacy enabled/disabled, admin legacy enabled/disabled, modern-only devices without device config, admin VQ negotiation, queue affinity operations, and SR-IOV helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy.c

## Purpose
`virtio_pci_legacy.c` adapts legacy virtio PCI devices to the generic virtio config API. It wraps the low-level legacy register helpers, creates legacy vrings using a 32-bit queue PFN, handles legacy config/status operations, and installs legacy transport callbacks into `struct virtio_pci_device`.

## Important APIs, types, and functions
- `vp_get_features()` and `vp_finalize_features()` negotiate the legacy 32-bit feature word.
- `vp_get()` and `vp_set()` access byte-oriented device-specific config space at `VIRTIO_PCI_CONFIG_OFF(msix_enabled)`.
- `vp_get_status()`, `vp_set_status()`, and `vp_reset()` read/write legacy device status and flush reset effects.
- `setup_vq()` creates and activates one legacy virtqueue and programs optional MSI-X queue vectors.
- `del_vq()` disables the queue vector, clears queue address, and deletes the vring.
- `virtio_pci_legacy_probe()` and `virtio_pci_legacy_remove()` bridge common PCI code to low-level legacy probe/remove.

## Control flow
Legacy probe calls `vp_legacy_probe()`, copies the ISR pointer and virtio id, assigns legacy `virtio_config_ops`, installs queue/config-vector callbacks, and marks the device legacy. Queue setup checks queue availability and inactive status, creates a vring with legacy alignment, validates that the descriptor address fits in a 32-bit PFN, writes the queue address, stores the notify register in `vq->priv`, and programs MSI-X if requested. Reset writes status 0, reads status to flush, then synchronizes all vectors.

## State and persistence behavior
The file stores no independent global state. Per-device state lives in `vp_dev->ldev`, callback pointers, `is_legacy`, `isr`, and per-queue `virtio_pci_vq_info`. Legacy config offsets depend on whether MSI-X is enabled because the legacy ABI moves device config space when MSI-X registers are present.

## Dependencies and integration points
It depends on `virtio_pci_common.h`, public `linux/virtio_pci_legacy.h`, the low-level helper functions from `virtio_pci_legacy_dev.c`, and common queue/interrupt code from `virtio_pci_common.c`. Upper virtio drivers see it only through `virtio_config_ops`.

## Risks and test signals
Risks include the 32-bit PFN limitation, only 32 feature bits, byte-wise config accesses, config offset changes with MSI-X, legacy memory barrier assumptions, and cleanup after vector programming failure. Test signals include transitional legacy probe, feature negotiation rejecting high bits, queue setup below and above PFN limits, MSI-X and INTx operation, config get/set offsets with MSI-X enabled, reset flushing callbacks, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy_dev.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy_dev.c

## Purpose
`virtio_pci_legacy_dev.c` is the exported low-level access layer for legacy virtio PCI devices. It validates legacy PCI IDs/revision, maps BAR0, configures DMA masks, and exposes helpers for legacy feature, status, queue, and MSI-X registers.

## Important APIs, types, and functions
- `vp_legacy_probe()` validates device id range `0x1000..0x103f`, ABI revision, DMA masks, BAR0 ownership, and maps the legacy I/O region.
- `vp_legacy_remove()` unmaps BAR0 and releases the region.
- `vp_legacy_get_features()`, `vp_legacy_get_driver_features()`, and `vp_legacy_set_features()` access host/guest feature registers.
- `vp_legacy_get_status()` and `vp_legacy_set_status()` access the status register.
- `vp_legacy_queue_vector()` and `vp_legacy_config_vector()` program MSI-X vectors and read back the result.
- `vp_legacy_set_queue_address()`, `vp_legacy_get_queue_enable()`, and `vp_legacy_get_queue_size()` select a queue and access queue PFN/size registers.

## Control flow
Probe is called after PCI enablement by common code. It rejects non-legacy IDs or wrong ABI revision, tries a 64-bit DMA mask with a coherent mask constrained by the legacy queue PFN width, falls back to 32-bit DMA, requests BAR0, maps it, sets `isr`, and derives the virtio id from PCI subsystem ids. Register helpers all perform direct I/O to offsets from `ldev->ioaddr`, selecting a queue before queue-specific access.

## State and persistence behavior
Persistent state is limited to `struct virtio_pci_legacy_device`: PCI device pointer, mapped I/O base, ISR address, and virtio id. The hardware registers hold negotiated features, status, queue PFNs, and MSI-X vector assignments until reset/remove.

## Dependencies and integration points
It depends on Linux PCI, module APIs, public virtio PCI legacy definitions, and the legacy transport glue in `virtio_pci_legacy.c`. The helper symbols are exported GPL so other kernel code can use the same low-level legacy abstraction.

## Risks and test signals
Risks include BAR0 request conflicts, DMA mask warnings that continue despite possible runtime failure, queue selection races if callers do not serialize queue-specific register access, 32-bit PFN limits, and strict legacy revision filtering. Test signals include probe rejection for non-legacy IDs/revisions, BAR request/unmap cleanup, feature/status read-write, queue size and enable detection, queue PFN programming, MSI-X vector readback, and DMA mask fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern.c

## Purpose
`virtio_pci_modern.c` adapts virtio 1.x PCI capabilities to the generic virtio config API. It handles extended feature negotiation, modern config access, vring activation, queue reset, shared-memory capabilities, admin virtqueue initialization/execution, SR-IOV member admin commands, and installation of modern transport callbacks into `struct virtio_pci_device`.

## Important APIs, types, and functions
- `vp_get_features()`, `vp_finalize_features()`, `vp_transport_features()`, and `vp_check_common_size()` negotiate modern features and validate common config size for optional fields.
- `vp_get()`, `vp_set()`, `vp_generation()`, `vp_get_status()`, `vp_set_status()`, and `vp_reset()` implement modern config ops.
- `setup_vq()`, `vp_active_vq()`, `vp_modern_find_vqs()`, `del_vq()`, `vp_modern_disable_vq_and_reset()`, and `vp_modern_enable_vq_after_reset()` manage modern virtqueues.
- `vp_modern_avq_done()`, `virtqueue_exec_admin_cmd()`, `vp_modern_admin_cmd_exec()`, and admin initialization helpers implement the admin virtqueue.
- Exported admin helpers include `virtio_pci_admin_has_dev_parts()`, `virtio_pci_admin_mode_set()`, object create/destroy, metadata get, device-parts get, and device-parts set.
- `vp_get_shm_region()` exposes shared-memory capability regions.
- `virtio_pci_modern_probe()` and `virtio_pci_modern_remove()` connect to the low-level modern device layer.

## Control flow
Modern probe calls `vp_modern_probe()`, chooses config ops with or without device-specific config space, installs callbacks, copies ISR/id, and initializes the admin VQ lock. Feature finalization lets vring and PCI transport code consume features, requires `VIRTIO_F_VERSION_1`, validates optional common config fields for notification data, ring reset, and admin VQ, then writes the negotiated feature array. When DRIVER_OK is set, `vp_modern_avq_activate()` queries supported admin commands, negotiates the command subset the driver can use, queries supported capabilities, and enables device-parts object limits when available.

Queue setup validates queue index/availability, creates a vring, writes queue size and descriptor/driver/device addresses, programs MSI-X if used, maps the queue notification location, and delays queue-enable until all queues are created. Queue reset removes the queue from interrupt lists, optionally breaks hardened notifications, synchronizes exclusive IRQs, waits for hardware reset completion in the low-level helper, then reactivates and relinks the queue on enable. Device reset writes status 0, waits until the device reports 0, completes unused admin commands with `-EIO`, and synchronizes vectors.

Admin command execution builds a header scatterlist, optional data, status buffer, and optional result buffer, adds them to the admin virtqueue under a spinlock, kicks, waits for completion, and maps admin status to Linux errors. Device-parts exported helpers resolve a VF to its PF virtio device, construct SR-IOV group admin commands, manage resource object ids with an IDA, and copy returned sizes/results to callers.

## State and persistence behavior
Persistent state lives in `struct virtio_pci_device` and its `mdev`/`admin_vq` members: mapped capability windows, queue callbacks, admin command bitmaps, supported capability bitmap, device-parts object limit, and allocated object ids. Queue reset mutates `vq->reset` and queue list membership. Device-parts object ids persist in the IDA until destroy or failed create cleanup. No disk persistence exists.

## Dependencies and integration points
This file depends on the low-level modern capability helpers in `virtio_pci_modern_dev.c`, common PCI queue/vector code, virtio ring, admin command UAPI structures, scatterlists, completions, PCI SR-IOV helpers, and shared-memory capability definitions. It exports admin APIs consumed by other VF/PF management paths.

## Risks and test signals
Risks include admin virtqueue deadlock or starvation on `-ENOSPC`, completing commands during reset, optional common config fields shorter than negotiated features, queue notification mapping failures, queue reset/list races with interrupts, IDA leaks on object lifecycle errors, unsupported admin status propagation, and SR-IOV PF/VF lifetime assumptions. Test signals include modern-only and transitional probe, extended feature negotiation, missing `VERSION_1` rejection, notification-data and ring-reset paths, admin VQ command list negotiation, device-parts object create/get/set/destroy, shared-memory region validation, queue reset disable/enable, MSI-X and INTx queue creation, and reset with pending admin commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern_dev.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern_dev.c

## Purpose
`virtio_pci_modern_dev.c` is the exported low-level modern virtio PCI capability layer. It discovers virtio vendor capabilities, maps common/ISR/notify/device config regions, validates ABI offsets, configures DMA masks, and provides typed helpers for modern feature, status, queue, MSI-X, notification, and admin-queue registers.

## Important APIs, types, and functions
- `vp_modern_map_capability()` validates BAR, length, offset, alignment, range, and maps a capability window.
- `virtio_pci_find_capability()` scans vendor capabilities for a requested virtio cfg type and records BAR ownership.
- `check_offsets()` build-time checks public virtio PCI ABI offsets against kernel struct layouts.
- `vp_modern_probe()` validates device id, discovers mandatory common/ISR/notify capabilities, optional device config, requests selected BARs, and maps register windows.
- `vp_modern_remove()` unmaps windows and releases selected BARs.
- `vp_modern_get_extended_features()`, `vp_modern_get_driver_extended_features()`, and `vp_modern_set_extended_features()` read/write feature banks.
- Status/config helpers include `vp_modern_generation()`, `vp_modern_get_status()`, and `vp_modern_set_status()`.
- Queue helpers include queue reset, vector, address, enable, size, queue count, notification mapping, admin queue number, and admin queue index.

## Control flow
Probe first validates ABI offsets, derives the virtio id either from an optional device-id callback or PCI IDs, then searches vendor capabilities. Absence of common config returns `-ENODEV` so common code can fall back to legacy. Missing ISR or notify capabilities is fatal. It sets DMA masks, finds optional device config, requests all BARs used by modern capabilities, maps common config large enough for modern optional admin fields, maps the ISR, reads notify multiplier/length/offset, either maps the whole notify area when it fits in one page or records the capability for per-queue mapping, and maps up to one page of device config if present.

Feature helpers iterate 32-bit banks to fill or write the full virtio feature array. Queue helpers select a queue in common config before reading/writing queue fields. Queue reset writes `queue_reset`, then sleeps until both reset and enable clear. Notification mapping uses the queue's notify offset and multiplier, validating against a pre-mapped notify window or mapping the per-queue 2-byte notification area from the notify capability.

## State and persistence behavior
Persistent state is stored in `struct virtio_pci_modern_device`: PCI device pointer, virtio id, modern BAR bitmask, mapped common/ISR/notify/device pointers, lengths, notify offset multiplier, notify physical address, optional notify capability offset, and optional DMA mask/device-id callback inputs. Hardware retains feature/status/queue register writes until reset.

## Dependencies and integration points
It depends on Linux PCI capability scanning and BAR mapping, public `linux/virtio_pci_modern.h`, virtio PCI UAPI layouts, delay helpers, and low-level `vp_ioread*/vp_iowrite*` accessors. `virtio_pci_modern.c` consumes these helpers to implement the generic virtio transport.

## Risks and test signals
Risks include malformed capabilities, BAR changes between scan and map, integer wraparound in offset/length arithmetic, optional notify area mapping lifetime, PAGE_SIZE assumptions for device config, sleeping waits for broken queue reset, and ABI layout drift. Test signals include modern probe with valid/invalid capabilities, transitional fallback when common config is absent, bad BAR/offset/alignment rejection, full vs per-queue notify mapping, feature bank read/write, queue reset completion, admin queue index/num reads, remove cleanup after partial mapping failure, and device config absence using nodev ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern_dev.c -->
