# Group Research: group_1649_qemu_sources_virtualization_qemu_hw_virtio_iothread_vq_mapping_c_so_8599f322515c

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/qemu`.

This group covers QEMU's virtio/vhost/vhost-user plumbing for IOThread queue mapping, vDPA assignment, vhost memory/IOTLB backends, shadow virtqueues, and many vhost-user device frontends including virtio-fs.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/iothread-vq-mapping.c -->
# File Research: sources/virtualization/qemu/hw/virtio/iothread-vq-mapping.c

## Purpose
Implements validation, application, and cleanup for mapping virtqueues to named QEMU `IOThread` objects.

## Key Behavior
- Validates every mapping entry references an existing `IOThread`.
- Rejects duplicate IOThread names in a single mapping list.
- Requires all mapping entries to either specify explicit `vqs` lists or none of them to specify `vqs`.
- For explicit mappings, verifies each virtqueue index is below `num_queues`, is assigned once, and that every queue has an assignment.
- For implicit mappings, assigns virtqueues to IOThreads round-robin.
- Stores the selected `AioContext` for each virtqueue in the caller-provided `vq_aio_context` array.
- Takes an object reference on each mapped IOThread during apply and releases it during cleanup.

## Filesystem/Storage Relevance
This is used by virtio devices that want multiple virtqueues serviced by separate AIO contexts. For storage-heavy devices such as virtio-blk, this determines queue parallelism and thread affinity.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/iothread-vq-mapping.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/meson.build -->
# File Research: sources/virtualization/qemu/hw/virtio/meson.build

## Purpose
Defines the Meson source sets for QEMU's `hw/virtio` subsystem.

## Key Behavior
- Always includes core virtio bus, config I/O, IOThread virtqueue mapping, `virtio.c`, and QMP support.
- Adds PCI, MMIO, crypto, IOMMU, vhost-vsock common, and vDPA device sources according to Kconfig/build options.
- When vhost support exists, includes common `vhost.c`, `vhost-backend.c`, and `vhost-iova-tree.c`.
- When vhost-user support exists, includes `vhost-user.c`, `vhost-user-base.c`, and optional vhost-user MMIO/PCI device stubs.
- Adds vDPA shadow virtqueue support when `have_vhost_vdpa` is true.
- Separates `virtio_pci_ss` for PCI transport frontends, then folds it into `system_virtio_ss` under `CONFIG_VIRTIO_PCI`.
- Adds stub implementations for builds without full vhost/virtio-md support.

## Filesystem/Storage Relevance
This file determines which virtio storage and filesystem devices are built, including virtio-blk PCI, vhost-user-blk PCI, vhost-user-fs, vhost-scsi, vhost-user-scsi, and vDPA device assignment.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/trace.h -->
# File Research: sources/virtualization/qemu/hw/virtio/trace.h

## Purpose
Includes the generated trace header for the `hw/virtio` subsystem.

## Key Behavior
- Single include of `trace/trace-hw_virtio.h`.
- Allows virtio source files in this directory to use generated tracepoints.

## Filesystem/Storage Relevance
Tracepoints are used in vhost-user and related device paths to debug memory mapping, migration, IOTLB, and notifier behavior.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vdpa-dev-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vdpa-dev-pci.c

## Purpose
Provides PCI transport glue for the generic `vhost-vdpa-device`.

## Key Behavior
- Defines `vhost-vdpa-device-pci-base` embedding `VirtIOPCIProxy` plus `VhostVdpaDevice`.
- Initializes the embedded virtio device with `TYPE_VHOST_VDPA_DEVICE`.
- Exposes `bootindex` as an alias to the child vDPA device.
- During post-init, derives PCI class code and transitional device ID from the actual vDPA virtio device ID.
- Sets MSI-X vector count to `num_queues + 1`, reserving one vector for config changes.
- Registers generic, transitional, and non-transitional PCI type names.

## Filesystem/Storage Relevance
This enables PCI assignment of arbitrary vDPA virtio devices, including storage-class vDPA devices when the kernel vDPA backend exposes them.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vdpa-dev-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vdpa-dev.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vdpa-dev.c

## Purpose
Implements generic vDPA-based virtio device assignment.

## Key Behavior
- Requires a `vhostdev` path and opens it read/write.
- Queries the vDPA device ID, maximum vring size, queue count, and config size through vhost-vDPA ioctls.
- Validates `queue-size` against backend limits and defaults to the backend maximum when unset.
- Initializes a `vhost_dev` with `VHOST_BACKEND_TYPE_VDPA` and a shared vDPA state containing the device fd and IOVA range.
- Fetches device configuration before calling `virtio_init()`.
- Creates one virtio queue per backend queue, using a dummy output handler because the vhost backend handles data path work.
- Implements start/stop through host notifier enablement, guest notifier binding, `vhost_dev_start()`, queue unmasking, and corresponding cleanup.
- Filters `VIRTIO_F_IOMMU_PLATFORM` based on the frontend-requested feature set.
- Marks the VMState as unmigratable.

## Filesystem/Storage Relevance
Generic vDPA assignment can expose hardware or kernel-accelerated virtio storage/network devices to guests while QEMU manages virtio transport, configuration, notifiers, and lifecycle.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vdpa-dev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-backend.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-backend.c

## Purpose
Provides vhost backend operations for kernel vhost and common device-IOTLB helper functions.

## Key Behavior
- Under `CONFIG_VHOST_KERNEL`, wraps kernel vhost ioctls in `vhost_kernel_call()`.
- Implements kernel backend init, cleanup, memslot limit discovery, feature get/set, owner setup, vring configuration, eventfd setup, SCSI endpoint operations, vsock operations, and worker operations.
- Supports extended feature arrays with fallback to legacy `VHOST_GET/SET_FEATURES`.
- Reads `/sys/module/vhost/parameters/max_mem_regions`, defaulting to 64 on failure or invalid values.
- Negotiates `VHOST_BACKEND_F_IOTLB_MSG_V2` when available.
- Reads kernel IOTLB miss/access messages from the vhost fd and forwards them to generic vhost handling.
- Sends device IOTLB update/invalidate messages in v1 or v2 message formats depending on backend capability.
- Exposes `kernel_ops` as the `VhostOps` table.
- Provides backend-independent helpers for updating, invalidating, and handling device IOTLB messages.

## Filesystem/Storage Relevance
Kernel vhost accelerates virtio storage/network paths. The IOTLB plumbing is especially important for IOMMU-backed DMA correctness in vhost storage and filesystem devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-backend.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.c

## Purpose
Implements `VhostIOVATree`, a helper for allocating and translating IOVA ranges used by vhost software live migration and shadow virtqueues.

## Main Structure
- `iova_first` / `iova_last`: allocatable device IOVA range, with low address zero avoided.
- `iova_taddr_map`: maps IOVA to translated host virtual addresses.
- `iova_map`: tracks allocated IOVA ranges.
- `gpa_iova_map`: maps guest physical addresses to IOVAs.

## Key Behavior
- Creates separate IOVA and GPA-backed interval trees.
- Avoids address zero by starting at at least one real host page.
- Finds IOVA mappings by translated host address or GPA.
- Allocates a new IOVA range, validates overflow and permissions, inserts into allocation tree, then inserts into the translated-address tree.
- Provides separate allocation/removal paths for HVA-backed and GPA-backed mappings.

## Filesystem/Storage Relevance
This supports address translation for vhost-vDPA/shadow virtqueue paths, where guest buffers must be represented as device-visible IOVA ranges during migration or mediated data path operation.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.h -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.h

## Purpose
Declares the `VhostIOVATree` interface used by vhost-vDPA and shadow virtqueue code.

## Key API
- Constructor/destructor: `vhost_iova_tree_new()`, `vhost_iova_tree_delete()`.
- Autoptr cleanup registration for GLib-managed cleanup.
- HVA-oriented lookup/allocation/removal: `find_iova`, `map_alloc`, `remove`.
- GPA-oriented lookup/allocation/removal: `find_gpa`, `map_alloc_gpa`, `remove_gpa`.

## Filesystem/Storage Relevance
This header exposes the mapping API needed for vhost shadow queues to translate guest storage or filesystem request buffers into backend-visible IOVA addresses.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-scsi-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-scsi-pci.c

## Purpose
Provides PCI transport binding for kernel `vhost-scsi`.

## Key Behavior
- Defines `vhost-scsi-pci-base` embedding `VirtIOPCIProxy` and `VHostSCSI`.
- Supports a `vectors` property defaulting to unspecified.
- Auto-selects SCSI queue count via `virtio_pci_optimal_num_queues()` when the virtio-scsi config requests automatic queues.
- Defaults MSI-X vectors to request queues plus fixed SCSI queues plus one config vector.
- Registers storage category, Red Hat virtio PCI vendor/device IDs, and SCSI class code.
- Adds a `bootindex` alias to the child vhost-scsi device.

## Filesystem/Storage Relevance
This is the PCI-facing entry point for SCSI devices accelerated through kernel vhost, allowing guest block devices to be served by a host SCSI target backend.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-scsi-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.c

## Purpose
Implements shadow virtqueues that sit between a guest virtqueue and a vhost device, allowing QEMU to relay descriptors and notifications while controlling address translation and migration behavior.

## Key Behavior
- Validates that transport feature bits are compatible with shadow virtqueue operation.
- Tracks free descriptor slots and descriptor chains in an internal split vring.
- Translates HVA-backed or GPA-backed guest buffers through `VhostIOVATree`.
- Writes translated out/in descriptor chains into the shadow vring and updates the shadow avail index with memory barriers.
- Kicks the hardware/backend notifier when event-index or no-notify logic says a kick is needed.
- Forwards guest available buffers until the queue is empty or SVQ descriptor space is exhausted.
- Caches one guest element in `next_guest_avail_elem` when the SVQ is full.
- Reads used elements from the device used ring, validates IDs and descriptor state, returns descriptors to the free list, and recovers the original `VirtQueueElement`.
- Pushes completed elements back to the guest virtqueue and notifies the guest call fd.
- Provides polling for synchronous wait paths.
- Manages guest kick fd, guest call fd, host call handler, shadow vring mmap allocation, and teardown.
- On stop, flushes pending used entries and unpops outstanding guest elements where possible.

## Filesystem/Storage Relevance
Shadow virtqueues are central to vhost-vDPA migration and mediated vhost operation. For storage and virtio-fs style devices, they preserve virtqueue semantics while QEMU remaps guest buffers into backend-visible address spaces.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.h -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.h

## Purpose
Declares the shadow virtqueue data structures and public API.

## Main Types
- `SVQDescState`: stores the original `VirtQueueElement` and number of descriptors exposed to the backend.
- `VhostShadowVirtqueueOps`: optional owner callback for custom available-buffer handling.
- `VhostShadowVirtqueue`: owns the shadow vring, host/guest event notifiers, original virtqueue pointer, virtio device, IOVA tree, descriptor state, descriptor free-list backup, callback hooks, and ring indices.

## Key API
- Feature validation and free-slot reporting.
- Add/push/poll data path functions.
- Kick/call fd setup and vring address/area-size accessors.
- Start/stop lifecycle and allocation/free helpers with GLib autoptr support.

## Filesystem/Storage Relevance
This API is the contract used by vhost-vDPA code to interpose QEMU-managed virtqueue translation and migration support in front of backend devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-stub.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-stub.c

## Purpose
Provides stub implementations when full vhost/vhost-user support is not built.

## Key Behavior
- Reports unlimited maximum/free memslots with `UINT_MAX`.
- Makes `vhost_user_init()` fail.
- Provides no-op cleanup and device-IOTLB toggle functions.

## Filesystem/Storage Relevance
Allows non-vhost QEMU builds to link while making vhost-user devices unavailable.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-stub.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-base.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-base.c

## Purpose
Implements an abstract base class for simple vhost-user virtio devices whose data path and configuration are delegated to an external daemon.

## Key Behavior
- Starts by enabling host notifiers, binding guest notifiers, setting acknowledged features, starting `vhost_dev`, and unmasking queues.
- Stops by stopping `vhost_dev`, unbinding guest notifiers, and disabling host notifiers.
- Uses virtio status transitions to start/stop the backend.
- Gets features directly from backend-advertised features, excluding the protocol feature bit.
- Optionally fetches and sets virtio config space through vhost-user config protocol.
- Installs a config notifier that raises virtio config-change interrupts.
- Realize path validates chardev and virtio ID, defaults queue count and queue size, initializes vhost-user state, initializes virtio, creates queues, initializes `vhost_dev`, and registers chardev event handlers.
- Handles chardev open by reconnecting and restoring started state.
- Handles chardev close through deferred `vhost_user_async_close()`.
- Unrealize stops, cleans up vhost, deletes queues, and releases virtio state.

## Filesystem/Storage Relevance
Many small vhost-user devices in this group subclass this base. The same pattern is useful for storage-adjacent daemons that implement virtio semantics outside QEMU.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-base.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-blk-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-blk-pci.c

## Purpose
Provides PCI transport binding for `vhost-user-blk`.

## Key Behavior
- Embeds `VHostUserBlk` inside a `VirtIOPCIProxy`.
- Exposes `class` and `vectors` PCI properties.
- Auto-selects queue count when `num_queues` requests automatic mode.
- Defaults vector count to number of queues plus one config vector.
- Registers storage category, virtio block PCI device ID, SCSI storage class code, and transitional/non-transitional type names.
- Adds `bootindex` alias to the child block device.

## Filesystem/Storage Relevance
This is the PCI frontend for block devices implemented by a vhost-user daemon, commonly used to move block I/O processing outside QEMU.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-blk-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-fs-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-fs-pci.c

## Purpose
Provides PCI transport glue for virtio-fs over vhost-user.

## Key Behavior
- Embeds `VHostUserFS` inside a `VirtIOPCIProxy`.
- Provides a `vectors` property defaulting to unspecified.
- Defaults vector count to request queues plus two extra vectors for config change and hiprio queue.
- Registers as storage category with `PCI_CLASS_STORAGE_OTHER`.
- Uses only a non-transitional PCI type name, `vhost-user-fs-pci`.
- Adds `bootindex` alias to the child filesystem device.

## Filesystem/Storage Relevance
This is the PCI attachment for virtio-fs, the most directly filesystem-related device in this group.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-fs-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-fs.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-fs.c

## Purpose
Implements QEMU's virtio-fs frontend using a vhost-user backend such as `virtiofsd`.

## Key Behavior
- Advertises virtio-fs relevant feature bits including version 1, indirect descriptors, event index, packed ring, IOMMU platform, ring reset, in-order, and notification data.
- Builds virtio config space from the filesystem tag and number of request queues.
- Validates mandatory `chardev`, non-empty `tag`, tag length, positive request queue count, power-of-two queue size, and maximum queue size.
- Initializes vhost-user state and virtio device ID `VIRTIO_ID_FS`.
- Creates one hiprio queue plus configured request queues.
- Initializes a `vhost_dev` with all virtio-fs queues.
- Starts/stops through guest notifier binding and `vhost_dev_start/stop`.
- Masks/polls guest notifiers while ignoring the special config interrupt index.
- Implements backend state save/load through `vhost_save_backend_state()` and `vhost_load_backend_state()`.
- Adds a VMState subsection for internal backend migration state and checks backend support before migration.
- Provides `chardev`, `tag`, `num-request-queues`, and `queue-size` properties.

## Filesystem/Storage Relevance
This is QEMU's virtio-fs device model: it exposes a shared host filesystem to the guest while delegating filesystem request processing to a vhost-user backend.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-gpio-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-gpio-pci.c

## Purpose
Provides PCI transport glue for the vhost-user GPIO virtio device.

## Key Behavior
- Embeds `VHostUserGPIO` in a `VirtIOPCIProxy`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-gpio-pci`.

## Filesystem/Storage Relevance
No direct filesystem behavior; follows the same vhost-user PCI wrapper pattern used by storage and filesystem frontends.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-gpio-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-gpio.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-gpio.c

## Purpose
Defines the vhost-user GPIO virtio device as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets fixed virtio ID `VIRTIO_ID_GPIO`.
- Uses two virtqueues.
- Sets config size to `struct virtio_gpio_config`.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; useful as a compact example of vhost-user-base device specialization.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-gpio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-i2c-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-i2c-pci.c

## Purpose
Provides PCI transport glue for the vhost-user I2C virtio device.

## Key Behavior
- Embeds `VHostUserI2C` inside a `VirtIOPCIProxy`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-i2c-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; shares the vhost-user PCI frontend pattern used by other virtio devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-i2c-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-i2c.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-i2c.c

## Purpose
Defines the vhost-user I2C virtio device as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets fixed virtio ID `VIRTIO_ID_I2C_ADAPTER`.
- Uses one virtqueue with size 4.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; demonstrates a minimal one-queue vhost-user-base device.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-i2c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-input-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-input-pci.c

## Purpose
Provides PCI transport binding for vhost-user input devices.

## Key Behavior
- Defines concrete PCI type `vhost-user-input-pci`.
- Inherits from `TYPE_VIRTIO_INPUT_PCI`.
- Embeds `VHostUserInput` and initializes it as `TYPE_VHOST_USER_INPUT`.
- Registers the type with `virtio_pci_types_register()`.

## Filesystem/Storage Relevance
No direct filesystem role; it is another vhost-user transport wrapper.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-input-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-input.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-input.c

## Purpose
Defines a vhost-user input device using `VHostUserBase`.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_INPUT`.
- Uses two virtqueues, queue size 4, and config size `virtio_input_config`.
- Marks VMState unmigratable.
- Registers input device category.

## Filesystem/Storage Relevance
No direct filesystem role; shares the same base-class data path lifecycle used by simpler vhost-user devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-input.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rng-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rng-pci.c

## Purpose
Provides PCI transport glue for vhost-user RNG.

## Key Behavior
- Embeds `VHostUserRNG`.
- Provides a `vectors` property defaulting to unspecified.
- Defaults vector count to one.
- Registers input category and PCI class `PCI_CLASS_OTHERS`.
- Uses non-transitional PCI type `vhost-user-rng-pci`.

## Filesystem/Storage Relevance
No direct filesystem behavior; follows the same vhost-user PCI model as storage wrappers.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rng-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rng.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rng.c

## Purpose
Defines vhost-user RNG as a simple `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_RNG`.
- Uses one virtqueue of size 4.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem behavior; another minimal vhost-user-base example.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rng.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rtc-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rtc-pci.c

## Purpose
Provides PCI transport glue for vhost-user RTC/clock.

## Key Behavior
- Embeds `VHostUserRTC`.
- Forces one MSI-X vector.
- Registers misc category and `PCI_CLASS_SYSTEM_RTC`.
- Uses non-transitional PCI type `vhost-user-rtc-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; this is a small vhost-user transport wrapper.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rtc-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rtc.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rtc.c

## Purpose
Defines vhost-user RTC/clock as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_CLOCK`.
- Uses two virtqueues, no config space, and queue size 1024.
- Marks VMState unmigratable.
- Registers misc device category.

## Filesystem/Storage Relevance
No direct filesystem role; demonstrates a base-class specialization with larger queues and no config region.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-rtc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scmi-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scmi-pci.c

## Purpose
Provides PCI transport glue for vhost-user SCMI.

## Key Behavior
- Embeds `VHostUserSCMI`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-scmi-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; follows the same virtio PCI wrapper conventions.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scmi-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scmi.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scmi.c

## Purpose
Implements the vhost-user SCMI virtio device with custom lifecycle logic rather than subclassing `VHostUserBase`.

## Key Behavior
- Advertises selected feature bits including version 1, notify-on-empty, indirect descriptors, event index, ring reset, and `VIRTIO_SCMI_F_P2A_CHANNELS`.
- Does not support `VIRTIO_SCMI_F_SHARED_MEMORY`.
- Starts by enabling host notifiers, binding guest notifiers, acknowledging features, starting vhost, and unmasking queues.
- Tracks `started_vu` because generic started-state checks are not sufficient for all stop paths.
- Refuses status transitions when the chardev/backend is not connected.
- Handles chardev open/close by toggling `connected` and restoring/stopping state.
- Creates command and event virtqueues, each size 256.
- Initializes `vhost_dev` with two queues and `VHOST_BACKEND_TYPE_USER`.
- Cleans up queues, vhost-user state, and virtio state on failure or unrealize.
- Marks VMState unmigratable.

## Filesystem/Storage Relevance
No direct filesystem role; useful contrast with `VHostUserBase` because it manually implements the same vhost-user lifecycle pieces.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scmi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scsi-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scsi-pci.c

## Purpose
Provides PCI transport binding for vhost-user SCSI.

## Key Behavior
- Embeds `VHostUserSCSI` inside `VirtIOPCIProxy`.
- Exposes a `vectors` property.
- Auto-selects queue count when virtio-scsi requests automatic queues.
- Defaults vector count to request queues plus fixed SCSI queues plus one config vector.
- Registers storage category, virtio SCSI PCI IDs, and SCSI storage class.
- Adds `bootindex` alias to the child vhost-user SCSI device.
- Registers generic, transitional, and non-transitional PCI types.

## Filesystem/Storage Relevance
This is the PCI frontend for a vhost-user SCSI backend, allowing guest SCSI block devices to be served by an external daemon.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-scsi-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-snd-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-snd-pci.c

## Purpose
Provides PCI transport glue for vhost-user sound.

## Key Behavior
- Embeds `VHostUserSound`.
- Forces one MSI-X vector.
- Registers sound category and multimedia audio PCI class.
- Uses non-transitional PCI type `vhost-user-snd-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; another small vhost-user PCI wrapper.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-snd-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-snd.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-snd.c

## Purpose
Defines vhost-user sound as a `VHostUserBase` specialization.

## Key Behavior
- Supports optional `VIRTIO_SND_F_CTLS` via a `controls` property that sets a host feature bit.
- Computes config size from feature-dependent virtio sound config bounds.
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_SOUND`.
- Uses four virtqueues and queue size 64.
- Marks VMState unmigratable and registers sound category.

## Filesystem/Storage Relevance
No direct filesystem role; shows feature-dependent config sizing in a vhost-user-base device.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-snd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-spi-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-spi-pci.c

## Purpose
Provides PCI transport glue for vhost-user SPI.

## Key Behavior
- Embeds `VHostUserSPI`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-spi-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; same transport pattern as other small vhost-user devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-spi-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-spi.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-spi.c

## Purpose
Defines vhost-user SPI as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_SPI`.
- Uses one virtqueue of size 4.
- Sets config size to `struct virtio_spi_config`.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; another minimal vhost-user-base specialization.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-spi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-test-device-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-test-device-pci.c

## Purpose
Provides PCI transport glue for the configurable vhost-user test device.

## Key Behavior
- Embeds `VHostUserBase` directly.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Initializes the child device as `TYPE_VHOST_USER_TEST_DEVICE`.
- Uses non-transitional PCI type `vhost-user-test-device-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; useful for prototyping arbitrary vhost-user backends, including storage experiments.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-test-device-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-test-device.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-test-device.c

## Purpose
Defines a concrete configurable vhost-user device for development and prototyping.

## Key Behavior
- Subclasses `VHostUserBase`.
- Lets users provide `chardev`, `virtio-id`, `vq_size`, `num_vqs`, and `config_size` properties.
- Leaves backend-specific configuration to the external vhost-user daemon.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
Can be used to prototype vhost-user devices, including storage-like devices, without adding a dedicated QEMU device model first.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-test-device.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-vsock-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-vsock-pci.c

## Purpose
Provides PCI transport binding for vhost-user vsock.

## Key Behavior
- Embeds `VHostUserVSock` inside `VirtIOPCIProxy`.
- Provides a `vectors` property defaulting to 3.
- Forces virtio 1.0 mode because older compatibility handling is not needed here.
- Registers misc category, virtio vsock PCI device ID, and communication-other PCI class.
- Registers generic and non-transitional PCI type names.

## Filesystem/Storage Relevance
No direct filesystem role, though vsock is often used as a guest-host communication channel adjacent to filesystem daemons and agents.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-vsock-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-vsock.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-vsock.c

## Purpose
Implements vhost-user vsock by combining vhost-user backend initialization with common vhost-vsock virtio logic.

## Key Behavior
- Filters backend features through a vhost-user vsock feature list, then delegates vsock-specific feature handling to common code.
- Caches `virtio_vsock_config` and returns it to the guest.
- Handles backend config-change notifications by refetching config and notifying the guest.
- Starts/stops through `vhost_vsock_common_start()` and `vhost_vsock_common_stop()` on virtio status transitions.
- Requires a `chardev`.
- Initializes vhost-user state, realizes common vsock state, registers config notifier, initializes `vhost_dev`, and fetches initial config.
- Cleans up vhost, common vsock state, and vhost-user state on unrealize or failure.
- Marks VMState unmigratable.

## Filesystem/Storage Relevance
No direct filesystem implementation, but vsock channels can support guest-host service communication used around filesystem and storage agents.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user-vsock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-user.c

## Purpose
Implements QEMU's vhost-user backend operations: protocol messages, memory table sharing, vring setup, backend request handling, migration/postcopy support, device config, crypto sessions, inflight descriptors, shared objects, and device-state migration.

## Protocol and Message Layer
- Defines frontend requests from `VHOST_USER_GET_FEATURES` through `VHOST_USER_CHECK_DEVICE_STATE`.
- Defines backend requests for IOTLB, config change, host notifier, and shared-object add/remove/lookup.
- Defines packed protocol payload structures for memory regions, memory add/remove, log sharing, config space, crypto sessions, vring areas, inflight state, shared objects, and device-state transfer.
- Reads and validates reply headers, protocol version flags, payload sizes, and expected request types.
- Writes messages with optional SCM_RIGHTS file descriptors through the chardev.
- Suppresses per-device requests on secondary `vhost_dev` instances when a virtio device is represented by multiple vhost devices.
- Implements reply-ack processing through `VHOST_USER_NEED_REPLY_MASK`.

## Memory and Postcopy
- Builds `VHOST_USER_SET_MEM_TABLE` messages by translating QEMU host addresses to memory regions, file descriptors, and mmap offsets.
- Tracks shadow memory regions so backends supporting `VHOST_USER_PROTOCOL_F_CONFIGURE_MEM_SLOTS` can receive incremental add/remove messages.
- Maintains RAMBlock and offset arrays needed for postcopy fault translation.
- Handles postcopy-specific memory table replies, backend client base addresses, and final acknowledgements.
- Registers a Linux userfaultfd postcopy handler that maps backend fault addresses back to RAMBlocks and requests pages.
- Provides a postcopy waker that wakes backend mappings when pages arrive.
- Implements postcopy advise, listen, and end protocol messages through migration notifiers.

## Vring and Notifier Handling
- Sends vring num/base/addr/endian/enable messages.
- Waits for backend replies where ordering matters, such as queue enablement and logging.
- Sends kick/call/error eventfds and waits for reply-ack when supported to avoid interrupt loss during fd replacement.
- Handles backend host-notifier messages by mapping a page-sized fd and installing it as a virtio host notifier memory region.
- Removes host notifier mappings with RCU-safe cleanup.

## Backend Request Channel
- Creates a socketpair for backend-initiated requests when `VHOST_USER_PROTOCOL_F_BACKEND_REQ` is negotiated.
- Handles backend IOTLB messages, config-change messages, host notifier updates, and shared-object operations.
- Sends backend request replies when requested or when shared-object lookup requires a response.

## Feature Negotiation and Lifecycle
- Initializes backend state by querying features and protocol features.
- Negotiates only QEMU-supported protocol bits and suppresses unsupported config or inflight features.
- Validates queue count, IOMMU requirements, RAM slot limits, and migration logging support.
- Sets a migration blocker when the backend lacks shared-memory dirty logging.
- Registers cleanup for backend channel, postcopy notifiers, postcopy fds, and tracked RAMBlock arrays.
- Exposes memory slot limit, private memslot policy, vq index mapping, device start status, reset status, and migration-done RARP behavior through `user_ops`.

## Device Services
- Gets and sets virtio config space through `VHOST_USER_GET_CONFIG` and `VHOST_USER_SET_CONFIG`.
- Sends device IOTLB messages with reply acknowledgement.
- Creates and closes vhost-user crypto sessions, copying bounded symmetric/asymmetric key material into protocol payloads.
- Gets and sets inflight shared-memory fds for inflight descriptor migration.
- Supports shared object lookup, including DMABUF forwarding and delegating lookup through another vhost device.
- Transfers backend device migration state using `SET_DEVICE_STATE_FD` and validates completion with `CHECK_DEVICE_STATE`.
- Provides `vhost_user_init()`, `vhost_user_cleanup()`, and deferred asynchronous close handling for devices using this backend.

## Filesystem/Storage Relevance
This is the central QEMU implementation used by vhost-user storage and filesystem devices such as vhost-user-blk, vhost-user-scsi, and virtio-fs. It controls how guest memory is shared with external daemons, how virtqueues are wired to eventfds, how IOMMU misses are serviced, and how backend state is migrated.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-user.c -->