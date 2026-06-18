# Group Research: group_1652_qemu_sources_virtualization_qemu_hw_virtio_virtio_pci_c_sources_vir_5639048e3d16

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/qemu` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-pci.c

## Purpose
Core QEMU virtio-over-PCI transport implementation. It exposes a `VirtIOPCIProxy` PCI device that owns a `VirtioBusState`, maps legacy and modern virtio PCI regions, handles PCI/MSI-X interrupt routing, migration state, ioeventfd/irqfd acceleration, reset, QOM type registration, and virtio bus callbacks.

## Main Responsibilities
- Implements legacy virtio PCI I/O BAR behavior: feature negotiation, queue PFN/address, queue select/notify, status, ISR, and MSI-X vector access (`virtio_ioport_write`, `virtio_ioport_read`, `virtio_pci_config_read/write`).
- Implements modern virtio PCI capabilities and regions: common config, ISR, device config, notify MMIO, optional notify PIO, and PCI CFG access capability.
- Bridges virtio bus callbacks to PCI transport behavior: notify, save/load config, save/load queue vectors, guest notifier setup, ioeventfd assignment, DMA address space lookup, IOMMU detection, and queue enabled state.
- Manages MSI-X vector usage and KVM irqfd routing for virtqueues and config interrupts.
- Registers generic, transitional, and non-transitional virtio PCI QOM types from `VirtioPCIDeviceTypeInfo`.

## Key Data and State
- `VirtIOPCIProxy` holds PCI device state, embedded virtio PCI bus, feature selectors (`dfselect`, `gfselect`), selected guest features, modern queue state array, BAR indices, modern region metadata, MSI-X vector count, and optional irqfd vector bookkeeping.
- `VirtIOPCIQueue` migration state stores queue size, enabled flag, descriptor/avail/used addresses, and runtime reset state for modern queues.
- `virtio_pci_id_info[]` maps virtio device IDs to legacy transitional PCI device IDs and PCI class IDs for selected device types.

## Initialization and Device Plug Flow
- `virtio_pci_realize()` sets default BAR layout: legacy I/O BAR 0, MSI-X BAR 1, optional modern PIO BAR 2, modern 64-bit memory BAR 4/5. It initializes modern region offsets and sizes, resolves `disable-legacy` auto behavior, initializes PCIe capabilities if needed, creates the virtio-pci bus, then delegates subclass realization.
- `virtio_pci_pre_plugged()` adds `VIRTIO_F_VERSION_1` for modern transport and always adds `VIRTIO_F_BAD_FEATURE`.
- `virtio_pci_device_plugged()` validates legacy/modern compatibility, sets PCI IDs/class/revision, maps modern capability regions when enabled, initializes MSI-X, installs PCI config read/write hooks, registers legacy BAR when needed, and initializes SR-IOV/ARI details on PCIe devices.
- `virtio_pci_device_unplugged()` stops ioeventfd and unmaps modern regions.

## Legacy Transport Behavior
- Legacy writes to `VIRTIO_PCI_GUEST_FEATURES` negotiate 32-bit features, with `VIRTIO_F_BAD_FEATURE` treated specially.
- Legacy `QUEUE_PFN` writes set queue address or reset the whole virtio-pci device when zero.
- Legacy status writes stop ioeventfd before clearing `DRIVER_OK`, restart it when setting `DRIVER_OK`, reset on status zero, and auto-enable PCI bus mastering for old Linux guest compatibility.
- Legacy device config access is routed through `virtio_config_read/write*`, with target-native config endianness handled explicitly.

## Modern Transport Behavior
- Modern common config reads expose selected device/guest feature words, MSI-X vectors, queue count, status, config generation, selected queue state, queue addresses, and queue reset state.
- Modern common config writes update feature selectors, build 64-bit feature arrays from 32-bit guest feature words, assign MSI-X vectors, update status, configure queue size/rings, enable queues, and reset individual queues.
- Queue notifications are handled by MMIO offset divided by notify multiplier or by optional PIO value.
- `virtio_pci_add_shm_cap()` adds 64-bit shared-memory PCI capabilities for devices that need shared memory windows.

## Interrupts and Acceleration
- `virtio_pci_notify()` uses MSI-X when enabled and falls back to legacy INTx via ISR bit 0.
- MSI-X vector assignment validates against `proxy->nvectors`, marks vectors used/un-used, and coordinates with irqfd if vectors change after `DRIVER_OK`.
- KVM irqfd support builds MSI routes with `accel_irqchip_add_msi_route()`, binds guest notifier eventfds to GSIs, updates routes on unmask, and releases virqs when vectors are unused.
- Guest notifier setup creates event notifiers for queues and config interrupts, configures irqfd/vector notifiers when available, and carefully unwinds on assignment errors.
- ioeventfd assignment registers/removes eventfds for modern MMIO notify, optional modern PIO notify, and legacy notify port.

## Migration and Reset
- Saves PCI state, MSI-X state, config vector, queue vectors, and modern transport state in VMState subsections.
- Modern migration state includes feature selectors, guest feature words, and per-queue modern configuration. A subsection covers feature words beyond the first 64 bits.
- Reset clears virtio bus state, unuses MSI-X vectors, clears negotiated guest features, and zeros modern queue cached configuration.
- Bus reset honors PCIe PM `No_Soft_Reset` while in D3hot.
- VM run/stop transitions start and stop ioeventfd; a migration compatibility flag can re-enable bus mastering for old migrated machines.

## Interfaces Exported
- `virtio_pci_get_trans_devid()`
- `virtio_pci_get_class_id()`
- `virtio_pci_add_shm_cap()`
- `virtio_pci_types_register()`
- `virtio_pci_optimal_num_queues()`

## Filesystem/Storage Relevance
This file is central for all PCI-attached virtio storage devices in this group and elsewhere: block, SCSI, pmem, fs, RNG, serial, and other devices rely on this transport for queue setup, DMA routing, notifications, interrupts, migration, and reset behavior.

## Notable Constraints and Risks
- PCI config capability access uses guest-controlled offsets/lengths and explicitly validates only 1/2/4-byte lengths, aligning offsets before dispatch.
- Legacy and modern mode compatibility checks are critical for migration and machine-type behavior.
- irqfd/MSI-X ordering is delicate: vector notifiers must be unset while guest notifiers still exist and set only after notifier assignment.
- Queue count helpers avoid exceeding MSI-X and `VIRTIO_QUEUE_MAX`, but individual devices still need correct fixed queue accounting.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.c

## Purpose
PCI wrapper for the virtio persistent memory device. It adapts `VirtIOPMEM` to the virtio-pci transport and implements QEMU’s `MemoryDeviceClass` interface for memory-device management and QMP reporting.

## Main Responsibilities
- `virtio_pmem_pci_realize()` forces virtio 1.0 mode via `virtio_pci_force_virtio_1()` and realizes the embedded `VirtIOPMEM` on the virtio-pci bus.
- Implements memory-device address accessors by forwarding the address to/from the embedded pmem device’s `VIRTIO_PMEM_ADDR_PROP`.
- Exposes the underlying memory region and plugged size through the `VirtIOPMEMClass` methods.
- Fills `MemoryDeviceInfo` with `VirtioPMEMDeviceInfo`, including the PCI device ID when present and detailed pmem information from the real virtio device.
- Registers `virtio-pmem-pci` using `virtio_pci_types_register()` with parent `TYPE_VIRTIO_MD_PCI`.

## Key Integration Points
- Depends on `virtio-pmem-pci.h`, `hw/mem/memory-device.h`, and the virtio-pmem class interface.
- Uses `virtio_instance_init_common()` to construct the embedded `TYPE_VIRTIO_PMEM` object inside the PCI wrapper.
- `MemoryDeviceClass` callbacks make this PCI device visible to the same memory hotplug/reporting infrastructure as other memory devices.

## Filesystem/Storage Relevance
This is the PCI transport-facing half of virtio-pmem. It makes host-backed persistent memory available to guests as a virtio PCI memory device, with address and size exposed to QEMU’s memory-device machinery.

## Notable Constraints
- The device is forced to modern virtio 1.0; no transitional/legacy type names are registered here.
- Most semantic validation is delegated to the embedded `VirtIOPMEM` device.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.h -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.h

## Purpose
Header defining the virtio-pmem PCI wrapper type.

## Main Contents
- Includes `virtio-md-pci.h`, `virtio-pmem.h`, and QOM object helpers.
- Declares `TYPE_VIRTIO_PMEM_PCI` as `"virtio-pmem-pci-base"`.
- Defines the `VIRTIO_PMEM_PCI` instance checker.
- Defines `struct VirtIOPMEMPCI`, which embeds:
  - `VirtIOMDPCI parent_obj`
  - `VirtIOPMEM vdev`

## Design Role
The wrapper extends the memory-device-aware virtio PCI base (`VirtIOMDPCI`) rather than plain `VirtIOPCIProxy`, allowing pmem to participate in memory-device address/region reporting while still carrying an embedded virtio pmem device.

## Filesystem/Storage Relevance
This type declaration is the structural link between virtio-pci transport, QEMU memory devices, and the persistent-memory virtio backend.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem.c

## Purpose
Implements the core virtio persistent memory device. It exposes a host memory backend as guest persistent memory and supports guest flush requests through a virtqueue.

## Main Responsibilities
- Defines `VirtIODeviceRequest` for one pmem request, including virtqueue element, backing fd, pmem/vdev pointers, request, and response.
- Handles flush requests by popping a virtqueue element, validating input/output SG presence, obtaining the host memory backend fd, and submitting an asynchronous worker.
- `worker_cb()` performs `fsync()` on the raw backing fd and writes a virtio-endian response status.
- `done_cb()` copies the response into the guest input SG, pushes the virtqueue element, notifies the guest, and frees request state.
- `virtio_pmem_get_config()` reports persistent memory start address and size in `struct virtio_pmem_config`.
- `virtio_pmem_realize()` validates `memdev`, rejects already mapped backends, marks the backend mapped, initializes virtio device ID `VIRTIO_ID_PMEM`, and creates one 128-entry request virtqueue.
- `virtio_pmem_unrealize()` unmarks the backend, deletes the queue, and cleans up virtio state.
- Provides class callbacks to fill QMP memory-device info and return the memory region.

## Properties
- `VIRTIO_PMEM_ADDR_PROP`: guest physical start address.
- `VIRTIO_PMEM_MEMDEV_PROP`: link to a `HostMemoryBackend`.

## Integration Points
- Uses `HostMemoryBackend` and `memory_region_get_fd()` for the actual host-backed storage/memory.
- Uses QEMU thread pool AIO for potentially blocking `fsync()`.
- Exposes `VirtIOPMEMClass` methods used by the PCI wrapper.
- Uses virtio endian helpers for config and response fields.

## Filesystem/Storage Relevance
The flush path is directly storage-relevant: guest persistence requests become host `fsync()` calls on the memory backend fd, making this file the core durability bridge for virtio-pmem.

## Notable Constraints and Risks
- `memdev` is mandatory and must not already be mapped.
- Flush request validation checks only that at least one out and one in SG are present; malformed request contents are not otherwise interpreted in this file.
- `fsync()` errors are collapsed to response value `1`, while success returns `0`.
- Correct durability depends on the backend memory region having a valid fd and host semantics matching persistent-memory expectations.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-pmem.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-qmp.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-qmp.c

## Purpose
Implements QMP helper and query functions for introspecting virtio devices, virtio status bits, virtio/vhost feature bitmaps, and vhost queue state.

## Main Responsibilities
- Provides static feature-description maps for virtio transport features, vhost-user protocol features, virtio config status bits, and many device-specific feature sets.
- Converts feature/status/protocol bitmaps into QAPI linked lists of descriptive strings, preserving unknown residual bits.
- Implements `qmp_x_query_virtio()` by recursively walking the QOM tree and collecting realized `TYPE_VIRTIO_DEVICE` instances.
- Implements `qmp_find_virtio_device()` to resolve a canonical QOM path to a realized `VirtIODevice`.
- Implements `qmp_x_query_virtio_status()` to report virtio device identity, feature sets, endian mode, queue count, status, ISR, selected queue, run/broken/disabled flags, bus name, notifier mask usage, and optional vhost state.
- Implements `qmp_x_query_virtio_vhost_queue_status()` to report one vhost virtqueue’s kick/call fds, descriptor/avail/used virtual pointers, physical addresses, sizes, and queue length.

## Feature Maps Covered
- Transport/ring: notify-on-empty, any-layout, version 1, IOMMU platform, packed ring, in-order, order-platform, SR-IOV, ring reset, indirect desc, event idx.
- Vhost-user protocol: multiqueue, log shmfd, RARP, reply ack, MTU, backend requests, cross-endian, crypto session, pagefault, config, fd passing, host notifier, inflight shmfd, reset, in-band notifications, mem slot configuration, status, shared object, device state.
- Device-specific maps include block, serial, GPU, input, net, SCSI, fs, i2c, vsock, balloon, crypto, IOMMU, mem, rng, and GPIO.
- Devices with no mapped features include 9P, PMEM, IOMEM, RPMSG, clock, WLAN/HWSIM, rproc serial, legacy memory balloon, CAIF, signal distribution, pstore, sound, Bluetooth, RPMB, video encoder/decoder, SCMI, Nitro secure module, watchdog, CAN, DMABUF, parameter service, and audio policy.

## Important Algorithms
- `CONVERT_FEATURES` scans a simple bitmap map, appends matched descriptions, clears matched bits, and leaves unknown bits in the local bitmap.
- `CONVERT_FEATURES_EX` does the same for extended virtio feature arrays using `virtio_has_feature_ex()` and `virtio_clear_feature_ex()`.
- `qmp_decode_features()` copies the source feature array, first strips known transport features, then strips device-specific features based on `device_id`, and finally reports remaining bits as unknown device features.

## Integration Points
- Uses QAPI types from `qapi/qapi-types-virtio.h` and QMP command declarations.
- Uses QOM traversal and object path resolution.
- When a device has vhost started, calls the virtio device class `get_vhost()` method and decodes vhost feature/protocol state.

## Filesystem/Storage Relevance
This is diagnostic and operational infrastructure for virtio storage-like devices, including virtio-blk, virtio-scsi, virtio-fs, and virtio-pmem. It helps inspect negotiated features and vhost queue state during debugging, migration analysis, and performance triage.

## Notable Constraints and Risks
- Unknown feature reporting depends on QAPI fields available for the first two 64-bit words, while the copied feature array can be larger.
- Several feature descriptions are manually maintained strings; typos or stale descriptions can mislead operators without affecting device behavior.
- `qmp_decode_features()` asserts unreachable on unknown virtio device IDs, so new IDs must be added here or explicitly listed as having no features.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-qmp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-qmp.h -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-qmp.h

## Purpose
Public header for virtio QMP helper functions.

## Main Contents
- Includes QAPI virtio types plus core virtio and vhost headers.
- Declares:
  - `qmp_find_virtio_device(const char *path)`
  - `qmp_decode_status(uint8_t bitmap)`
  - `qmp_decode_protocols(uint64_t bitmap)`
  - `qmp_decode_features(uint16_t device_id, const uint64_t *bitmap)`

## Integration Role
Allows other virtio QMP command implementations to reuse canonical path resolution and bitmap decoding logic instead of duplicating map traversal and QAPI object construction.

## Filesystem/Storage Relevance
Supports introspection for virtio storage and filesystem-adjacent devices by exposing decoded status and feature information to QMP command code.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-qmp.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-rng-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-rng-pci.c

## Purpose
PCI wrapper for the virtio random number generator device.

## Main Responsibilities
- Defines `VirtIORngPCI`, embedding `VirtIOPCIProxy` and `VirtIORNG`.
- Provides PCI wrapper properties:
  - `ioeventfd`, default enabled.
  - `vectors`, default unspecified.
- `virtio_rng_pci_realize()` defaults unspecified MSI-X vector count to `2`, then realizes the embedded `VirtIORNG` on the virtio-pci bus.
- Class initialization sets device category, PCI vendor/device IDs, revision, class ID, transport realization callback, and properties.
- Instance initialization constructs the embedded `TYPE_VIRTIO_RNG`.
- Registers generic, transitional, and non-transitional PCI type names.

## Integration Points
- Uses generic `virtio_pci_types_register()` for QOM type registration.
- Relies on the core `virtio-rng.c` implementation for actual entropy handling.
- Sets legacy PCI device ID `PCI_DEVICE_ID_VIRTIO_RNG` for transitional compatibility.

## Filesystem/Storage Relevance
Not filesystem-specific, but shares the same virtio-pci transport machinery used by storage devices. It is useful as a compact example of a simple virtio PCI wrapper.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-rng-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-rng.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-rng.c

## Purpose
Core virtio RNG device implementation. It supplies entropy from a QEMU RNG backend to guest-provided virtqueue buffers with rate limiting.

## Main Responsibilities
- Checks guest readiness using virtqueue readiness and `VIRTIO_CONFIG_S_DRIVER_OK`.
- Computes guest-requested input capacity using `virtqueue_get_avail_bytes()`.
- Requests entropy from the configured `RngBackend` and copies returned bytes into guest input SG buffers.
- Pushes completed buffers and notifies the guest.
- Implements quota/rate limiting using `max-bytes`, `period`, `quota_remaining`, and a virtual-clock timer.
- Retries processing on VM run-state changes and status changes.
- Creates a default builtin RNG backend when no `rng` property is supplied.
- Initializes virtio device ID `VIRTIO_ID_RNG` with one 8-entry virtqueue.
- Registers VMState containing generic virtio device state.

## Properties
- `max-bytes`: maximum entropy bytes per period, default `INT64_MAX`.
- `period`: rate-limit period in milliseconds, default `1 << 16`.
- `rng`: link to an `RngBackend`; if absent, a builtin backend child is created.

## Control Flow
- Guest kicks queue -> `handle_input()` -> `virtio_rng_process()`.
- `virtio_rng_process()` checks readiness, arms timer when needed, limits requested size by quota, and calls `rng_backend_request_entropy()`.
- Backend returns entropy -> `chr_read()` fills guest buffers, reduces quota, notifies guest, and continues processing if the queue remains non-empty.
- Timer expiry -> `check_rate_limit()` replenishes quota and resumes processing.

## Integration Points
- Uses QEMU runstate to avoid modifying virtqueues while CPUs are stopped.
- Uses QOM user-creatable completion for the default RNG backend.
- Uses virtio class callbacks for realize, unrealize, feature passthrough, and status update.

## Notable Constraints and Risks
- Rejects non-positive `period`.
- Rejects `max-bytes == 0` and values beyond `INT64_MAX`, compensating for property parsing limitations.
- Entropy delivery is paused when the VM is not running, then retried on resume.
- Rate limiting is based on virtual time, not wall-clock time.

## Filesystem/Storage Relevance
No direct filesystem role. It is part of the same virtio device family and demonstrates queue, runstate, migration, and backend-link patterns shared with storage-oriented virtio devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-rng.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-scsi-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-scsi-pci.c

## Purpose
PCI wrapper for the virtio SCSI controller device.

## Main Responsibilities
- Defines `VirtIOSCSIPCI`, embedding `VirtIOPCIProxy` and `VirtIOSCSI`.
- Provides PCI wrapper properties:
  - `ioeventfd`, default enabled.
  - `vectors`, default unspecified.
- `virtio_scsi_pci_realize()` auto-selects `num_queues` via `virtio_pci_optimal_num_queues()` when configured for automatic queue count.
- Defaults MSI-X vector count to `num_queues + VIRTIO_SCSI_VQ_NUM_FIXED + 1` when unspecified.
- Preserves command-line compatibility by setting the child bus name to `<proxy-id>.0` when the PCI proxy has an ID.
- Realizes the embedded `VirtIOSCSI` on the virtio-pci bus.
- Class initialization sets storage category, PCI vendor/device/class IDs, revision, transport realization callback, and properties.
- Registers generic, transitional, and non-transitional type names.

## Integration Points
- Uses `VirtIOSCSIConf` for queue configuration.
- Uses generic virtio-pci queue-count helper to balance vCPU count, MSI-X vector limits, and `VIRTIO_QUEUE_MAX`.
- Exposes PCI class `PCI_CLASS_STORAGE_SCSI`, making this a storage controller from the guest PCI perspective.

## Filesystem/Storage Relevance
This is the PCI transport binding for virtio-scsi, a major guest storage path. It determines queue scaling and MSI-X vector allocation, which directly affect SCSI I/O parallelism and interrupt behavior.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-scsi-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-serial-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-serial-pci.c

## Purpose
PCI wrapper for the virtio serial/console device.

## Main Responsibilities
- Defines `VirtIOSerialPCI`, embedding `VirtIOPCIProxy` and `VirtIOSerial`.
- `virtio_serial_pci_realize()` normalizes legacy-compatible PCI class codes, defaults unspecified vector count based on `max_virtserial_ports + 1`, preserves child bus name compatibility as `<proxy-id>.0`, and realizes the embedded `VirtIOSerial`.
- Provides PCI wrapper properties:
  - `ioeventfd`, default enabled.
  - `vectors`, default `2`.
  - `class`, allowing compatibility class-code override.
- Class initialization sets input category, PCI vendor/device IDs, revision, class ID, callback, and properties.
- Instance initialization constructs the embedded `TYPE_VIRTIO_SERIAL`.
- Registers generic, transitional, and non-transitional type names.

## Integration Points
- Relies on core `virtio-serial` implementation for port/device behavior.
- Uses `PCI_DEVICE_ID_VIRTIO_CONSOLE` for legacy/transitional identity.
- Uses generic virtio-pci registration and transport.

## Filesystem/Storage Relevance
No direct filesystem role, but virtio-serial frequently carries guest-agent and control channels used around storage/filesystem orchestration. It also shares the same PCI transport implementation as virtio storage devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-serial-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-stub.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-stub.c

## Purpose
Build-time stub for virtio QMP commands when virtio support is disabled.

## Main Responsibilities
- Defines `qmp_virtio_unsupported()` to set `Error` text `"Virtio is disabled"` and return `NULL`.
- Implements stub versions of:
  - `qmp_x_query_virtio()`
  - `qmp_x_query_virtio_status()`
  - `qmp_x_query_virtio_vhost_queue_status()`
  - `qmp_x_query_virtio_queue_status()`
  - `qmp_x_query_virtio_queue_element()`
- Each exported QMP function returns the common unsupported error.

## Integration Points
- Includes QAPI virtio command declarations so the symbols match the real virtio QMP implementation.
- Allows QEMU builds without virtio to satisfy QMP linkage while producing clear runtime errors for virtio introspection commands.

## Filesystem/Storage Relevance
Indirect. In non-virtio builds, virtio storage/filesystem introspection commands fail through this stub instead of being unavailable at link time or crashing.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-stub.c -->