# subset-b-005545 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/vduse_dev.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/vduse_dev.c

## Purpose

`vduse_dev.c` implements VDUSE, the kernel side of userspace-backed vDPA devices. It exposes `/dev/vduse/control` for creating and destroying device instances, `/dev/vduse/$name` for the userspace device process to exchange control messages and eventfds, and a vDPA management device named `vduse` so the vDPA bus can instantiate the prepared device. The implementation is a bridge between virtio/vdpa configuration operations, userspace request/response messages, eventfd kicks/interrupts, and VDUSE IOVA domains with optional bounce-buffer backed user memory.

## Important APIs, Types, and Functions

Core state lives in `struct vduse_dev`, which owns the device identity, feature bits, config space copy, status/generation, virtqueue array, address-space array, vq groups, message queues, work items, and locks. `struct vduse_virtqueue` tracks per-vq addresses, queue size, split/packed state, readiness, kickfd, callback, irq affinity, and sysfs kobject. `struct vduse_as` wraps a `vduse_iova_domain`, optional pinned user bounce memory, and `mem_lock`; `struct vduse_vq_group` maps a vq group to an address space under an rwlock.

The userspace protocol is centered on `vduse_dev_msg_sync()`, `vduse_dev_read_iter()`, and `vduse_dev_write_iter()`. The vDPA surface is `vduse_vdpa_config_ops`, with queue address/kick/callback/ready/state, feature/status/config, reset, map, group-asid, and map-token callbacks. DMA mapping for virtio uses `vduse_map_ops`, which forwards map/unmap/sync/coherent allocation operations to the group's current IOVA domain. Control ioctls include `VDUSE_GET_API_VERSION`, `VDUSE_SET_API_VERSION`, `VDUSE_CREATE_DEV`, and `VDUSE_DESTROY_DEV`; device ioctls include IOTLB fd/info queries, config update, vq setup/info/kickfd/irq injection, and UMEM registration.

## Control Flow

Module init registers the VDUSE class, allocates a char-device major, installs the control cdev at minor 0, installs per-device cdev coverage for remaining minors, creates high-priority IRQ workqueues, initializes the VDUSE IOVA subsystem, and registers a vDPA management device. Userspace opens `/dev/vduse/control`, negotiates API version, and calls `VDUSE_CREATE_DEV`. Creation validates reserved fields, feature constraints, device type, group/as counts, queue count, and config size, allocates the `vduse_dev`, IDR minor, config copy, vq groups, address spaces, `/dev/vduse/$name`, and per-vq sysfs objects.

Userspace then opens `/dev/vduse/$name`. vDPA device creation occurs later through the management-device `dev_add` callback: the named VDUSE device must exist and every virtqueue must have a nonzero `num_max`; domains are created, split across `bounce_size / nas`, and `_vdpa_register_device()` publishes the device. vDPA operations enqueue synchronous messages when userspace must perform work, for example status changes, IOTLB updates, and vq state reads. Userspace reads a request from `send_list`, which moves it to `recv_list`, writes a matching response by request id, and wakes the waiting kernel caller.

Data movement maps through the vDPA map token. Each virtqueue resolves to a group, a group resolves to an address space, and the address space owns the IOVA domain. API v0 has one group/asid; API v1 supports multiple groups and address spaces and can rebind a group via `VDUSE_SET_VQ_GROUP_ASID`. UMEM registration pins user pages for the full bounce-map range, enforces `RLIMIT_MEMLOCK`, charges `mm->pinned_vm`, and installs those pages into the domain's bounce map. Deregistration removes the bounce pages, dirties/unpins them, drops the mm reference, and frees the page array.

## State and Persistence Behavior

State is in-kernel and per-module, not file backed. The global `vduse_idr` maps minors to live `vduse_dev` objects under `vduse_lock`. Each device persists until `VDUSE_DESTROY_DEV`, which refuses busy devices with a registered vDPA instance or connected userspace endpoint, resets queues, destroys the class device, removes the IDR entry, frees config/vqs/domains/name/groups, and drops the module reference.

Reset clears driver status/features, increments config generation, removes config and queue callbacks, flushes IRQ/kick work, resets queue addresses/state/ready flags, drops kickfds, and resets bounce maps while preserving coherent mappings that are later freed through the coherent free callback. A message timeout marks the device broken, fails all queued messages, wakes poll/read waiters, and prevents further device ioctls. Releasing `/dev/vduse/$name` deregisters all UMEM, moves in-flight `recv_list` messages back to `send_list` so a reconnecting process can answer them, and marks the endpoint disconnected.

## Dependencies and Integration Points

The file integrates with the vDPA core (`vdpa_alloc_device`, `_vdpa_register_device`, `vdpa_mgmtdev_register`), virtio config and ring state, eventfd, character devices, sysfs/kobjects, workqueues, IDR, UIO iterators, pinned user pages, and the local `iova_domain.h` helpers. It depends on VDUSE UAPI structs from `uapi/linux/vduse.h`, vhost IOTLB maps, and virtio feature definitions for block, net, and fs devices. The only allowed device ids are block, net, and fs; net additionally requires `CAP_NET_ADMIN` at creation.

## Risks and Edge Cases

The message protocol has several ordering-sensitive lists under `msg_lock`. Partial `copy_to_iter()` requeues a message, while a timeout removes it and marks the whole device broken; tests need races between timeout, userspace response, release, and poll. UMEM registration increments `pinned_vm` by requested `npages` after `pin_user_pages()` returns `pinned`; this assumes the full pin succeeded and relies on prior equality checks. `vduse_vq_update_effective_cpu()` loops until it finds an online CPU or resets to `IRQ_UNBOUND`; affinity masks are validated through sysfs, but unexpected CPU hotplug behavior deserves coverage.

Feature validation is intentionally restrictive because config space is read-only to the vDPA driver: block WCE and net CTRL_VQ are rejected, net requires modern virtio, and every device must advertise `VIRTIO_F_ACCESS_PLATFORM`. API-version compatibility is another risk: v0 callers must not set groups/asids, while v1 callers must provide valid nonzero group/as counts and zero reserved fields.

## Test Signals

Useful tests include API version negotiation, create/destroy validation, duplicate names, busy destroy, open exclusivity, message request/response, timeout-to-broken behavior, reconnect with `recv_list` requeue, vq setup for API v0/v1, kickfd assignment/deassignment and queued kicks, config IRQ and vq IRQ injection, sysfs irq affinity parsing, bounce-size changes before and after domain allocation, UMEM pin/deregistration, IOTLB fd/info queries, multiple ASID group rebinding, reset cleanup, and module init/exit failure unwinds. vDPA integration should verify a created device can be registered only after all queues are configured and that DMA map/unmap/sync callbacks use the active group address space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/vduse_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/Makefile

## Purpose

This Makefile builds the virtio-pci vDPA bridge driver. When `CONFIG_VP_VDPA` is enabled, it adds `vp_vdpa.o` to the kernel build.

## Important APIs, Types, and Functions

There are no functions or types. The only build rule is `obj-$(CONFIG_VP_VDPA) += vp_vdpa.o`, which connects the Kconfig option to `vp_vdpa.c`.

## Control Flow

Kbuild evaluates the `obj-*` assignment while descending into `drivers/vdpa/virtio_pci`. If `CONFIG_VP_VDPA=y`, the object is built into the kernel; if `m`, it becomes a module; if unset, the file is not compiled.

## State and Persistence Behavior

The file has no runtime state or persistence. Its only persistent effect is on the generated kernel or module artifact.

## Dependencies and Integration Points

It depends on the surrounding Kbuild tree selecting this directory and on the `CONFIG_VP_VDPA` option being defined elsewhere. Its integration target is the `vp_vdpa.c` module.

## Risks and Edge Cases

The main risk is build drift: if the source filename or Kconfig symbol changes, this Makefile must change with it. Since the directory contains a single object, there is little ordering risk.

## Test Signals

Build with `CONFIG_VP_VDPA=y`, `m`, and unset to verify built-in, module, and excluded outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/vp_vdpa.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/vp_vdpa.c

## Purpose

`vp_vdpa.c` exposes modern virtio-pci devices through the vDPA framework. It probes only dynamically matched PCI ids, wraps the `virtio_pci_modern_device` accessors in `vdpa_config_ops`, registers a vDPA management device, and lets userspace instantiate a vDPA device over hardware virtqueues and notification BARs.

## Important APIs, Types, and Functions

`struct vp_vdpa` stores the `vdpa_device`, modern virtio-pci device pointer, per-vring notification/IRQ state, config callback, cached provisioned device features, MSI-X vector counts, and queue count. `struct vp_vring` stores a notify pointer, physical notify address, callback, MSI-X name, and IRQ. `struct vp_vdpa_mgmtdev` binds one PCI device to a vDPA management device and its active vDPA instance.

The core vDPA callbacks are `vp_vdpa_get_device_features()`, `vp_vdpa_set_driver_features()`, `vp_vdpa_get_status()`, `vp_vdpa_set_status()`, `vp_vdpa_reset()`, queue address/size/ready callbacks, config read/write callbacks, notification/kick callbacks, and `vp_vdpa_get_vq_irq()`. `vp_vdpa_request_irq()` allocates MSI-X vectors after callbacks are known; `vp_vdpa_free_irq()` detaches vectors and frees IRQs.

## Control Flow

PCI probe allocates the management wrapper, a `virtio_pci_modern_device`, and a two-entry virtio id table, enables the PCI device, calls `vp_modern_probe()`, fills management-device ids/features/max-vqs, sets bus mastering, and registers the management device. `dev_add` allocates a `vp_vdpa`, assigns the PCI device as `vmap.dma_dev`, reads queue count and device features, optionally applies a user-provisioned feature subset, maps every queue notify area with `vp_modern_map_vq_notify()`, initializes IRQ fields to `VIRTIO_MSI_NO_VECTOR`, and registers the vDPA device.

Queue operations write directly to modern virtio-pci common/notify registers. Kicks write either 16-bit queue id or 32-bit notification data to the queue's notify area. Config reads loop on `config_generation` until stable. When the vDPA status transitions to `DRIVER_OK`, `vp_vdpa_request_irq()` counts queues with callbacks, allocates one MSI-X vector per such queue plus one config vector, requests IRQs, and programs queue/config vectors. Reset writes status zero and frees IRQ resources if the device had reached `DRIVER_OK`.

## State and Persistence Behavior

Runtime state is held in the PCI driver data and active `vp_vdpa` instance. Hardware state is in the virtio-pci registers: status, feature negotiation, queue size/address/enable, queue vectors, config vector, and notify BAR writes. `device_features` is cached so vDPA reports the provisioned subset rather than the raw hardware mask. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on the virtio-pci modern helper API, PCI MSI-X allocation, vDPA core, virtio ring/config definitions, and vDPA netlink management paths. It uses devres for IRQ-vector cleanup registration and devm allocations for vrings/IRQs. The PCI driver has a NULL static id table, so binding relies on dynamic ids or driver override.

## Risks and Edge Cases

Virtqueue state save is not supported by virtio-pci; `get_vq_state()` returns `-EOPNOTSUPP`, and `set_vq_state()` only accepts an initial split or packed state before a queue is enabled. This blocks live migration and start/stop semantics. IRQ allocation is deferred until `DRIVER_OK`, so callback registration order matters; failures in `vp_vdpa_request_irq()` leave status unchanged but emit `WARN_ON(1)`. `pci_alloc_irq_vectors()` is called with exact min/max; devices unable to provide the exact count fail. Config read bounds are assumed valid by callers.

## Test Signals

Test probe/remove with dynamic ids, feature-subset provisioning, queue notify mapping failures, `_vdpa_register_device()` failure, `DRIVER_OK` IRQ setup, reset IRQ teardown, queue callback and config callback delivery, notification-area reporting, packed and split initial state acceptance, and rejection of non-initial queue states. Build with `CONFIG_VP_VDPA=m` and exercise unbind/remove while a vDPA device is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/vp_vdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/Kconfig

## Purpose

This Kconfig file defines the top-level VFIO framework options and includes bus-specific VFIO submenus. It controls whether VFIO core support, legacy group/container access, cdev/iommufd access, no-IOMMU support, virqfd, debugfs, and PCI/platform/mdev/fsl-mc/cdx drivers are available.

## Important APIs, Types, and Functions

The main option is `menuconfig VFIO`. It selects `IOMMU_API` and `INTERVAL_TREE`, conditionally selects `VFIO_GROUP`, `VFIO_DEVICE_CDEV`, and `VFIO_CONTAINER`, and includes help text describing VFIO as a secure userspace device-driver framework. Suboptions define `VFIO_DEVICE_CDEV`, `VFIO_GROUP`, `VFIO_CONTAINER`, `VFIO_IOMMU_TYPE1`, `VFIO_IOMMU_SPAPR_TCE`, `VFIO_NOIOMMU`, `VFIO_VIRQFD`, and `VFIO_DEBUGFS`.

## Control Flow

Configuration flow is conditional on `VFIO`. If VFIO is enabled, users can select the cdev interface when IOMMUFD is available without SPAPR TCE, the traditional group interface, the legacy container interface, no-IOMMU mode, and debugfs. The file then sources bus-specific Kconfig files and `virt/lib/Kconfig`.

## State and Persistence Behavior

The file creates build-time configuration state only. Its choices persist in `.config` and determine which objects are built and which runtime interfaces exist.

## Dependencies and Integration Points

It ties VFIO to IOMMUFD, SPAPR TCE, architecture-specific IOMMU drivers, DEBUG_FS, and bus-specific VFIO directories. The options map directly to object lists in `drivers/vfio/Makefile`.

## Risks and Edge Cases

The conditional defaults decide user ABI availability. For example, `VFIO_DEVICE_CDEV` defaults on only when groups are not selected, `VFIO_CONTAINER` depends on groups, and no-IOMMU requires group support. Misconfigured dependencies could expose no usable VFIO access path or accidentally disable the legacy ABI expected by userspace.

## Test Signals

Kconfig tests should cover VFIO with IOMMUFD enabled/disabled, SPAPR TCE, no-IOMMU, DEBUG_FS, and each bus submenu. Build configs should verify that selected symbols pull the intended objects and that mutually dependent cdev/group/container paths remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/Makefile

## Purpose

This Makefile builds the VFIO core and dispatches to VFIO bus subdirectories. It assembles `vfio.o` from core components based on selected feature symbols and builds legacy IOMMU backends and bus drivers.

## Important APIs, Types, and Functions

The main object is `vfio.o`, always containing `vfio_main.o` when `CONFIG_VFIO` is set. Conditional pieces include `device_cdev.o`, `group.o`, `iommufd.o`, `container.o`, `virqfd.o`, and `debugfs.o`. Standalone objects include `vfio_iommu_type1.o` and `vfio_iommu_spapr_tce.o`. Subdirectories include `pci/`, `platform/`, `mdev/`, `fsl-mc/`, and `cdx/`.

## Control Flow

Kbuild includes each object or directory according to its corresponding `CONFIG_*` symbol. This mirrors the top-level Kconfig split between cdev, group, IOMMUFD, container, virqfd, debugfs, and bus support.

## State and Persistence Behavior

No runtime state exists in the Makefile. It controls the final linkage shape of built-in objects or modules.

## Dependencies and Integration Points

The object list must match symbols declared in `drivers/vfio/Kconfig` and exported functions expected by VFIO bus drivers. It is also the integration point for legacy IOMMU backend modules.

## Risks and Edge Cases

The highest risk is inconsistent feature composition. For example, building a bus driver that expects physical iommufd helpers requires `iommufd.o`; legacy group paths require `group.o` and often `container.o`. Missing conditional objects produce link failures or unavailable ABIs.

## Test Signals

Build matrix coverage should include VFIO with only cdev/IOMMUFD, with legacy group/container, with debugfs, with no-IOMMU, and with each bus subdirectory enabled as built-in and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/cdx/Kconfig

## Purpose

This Kconfig file defines VFIO support for devices on the CDX bus.

## Important APIs, Types, and Functions

The only symbol is `VFIO_CDX`, a tristate option depending on `CDX_BUS` and selecting `EVENTFD`.

## Control Flow

When selected, the CDX VFIO driver is built and can bind CDX devices for userspace access through VFIO. If `CDX_BUS` is unavailable, the option is hidden.

## State and Persistence Behavior

It provides build-time state in `.config`; no runtime state is declared here.

## Dependencies and Integration Points

It integrates the CDX bus with VFIO and eventfd-backed interrupts. The Makefile maps it to `vfio-cdx.o`.

## Risks and Edge Cases

The feature is useless without CDX bus support and generic MSI support affects whether the interrupt implementation is included. Userspace expectations depend on VFIO core options selected at the top level.

## Test Signals

Build with `CDX_BUS=y/m`, `VFIO_CDX=y/m`, and without `CONFIG_GENERIC_MSI_IRQ` to verify interrupt stubs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/cdx/Makefile

## Purpose

This Makefile builds the CDX VFIO module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_VFIO_CDX) += vfio-cdx.o` enables the module. `vfio-cdx-objs := main.o` is always included, and `intr.o` is added only under `CONFIG_GENERIC_MSI_IRQ`.

## Control Flow

Kbuild links `main.o` for the base VFIO CDX driver and conditionally links MSI/eventfd support. Without generic MSI IRQ support, `private.h` supplies no-op stubs.

## State and Persistence Behavior

No runtime state exists. It controls compiled object composition.

## Dependencies and Integration Points

It must match `VFIO_CDX` in Kconfig and the conditional prototypes in `private.h`.

## Risks and Edge Cases

If `intr.o` is excluded, IRQ ioctls return `-EINVAL`; that behavior is intentional but should be visible to userspace tests.

## Test Signals

Build both with and without `CONFIG_GENERIC_MSI_IRQ`, and verify symbol resolution for `vfio_cdx_set_irqs_ioctl()` and `vfio_cdx_irqs_cleanup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/intr.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/cdx/intr.c

## Purpose

`intr.c` implements CDX MSI interrupt delivery for the VFIO CDX driver. It converts VFIO `VFIO_DEVICE_SET_IRQS` trigger requests into CDX MSI allocation, Linux IRQ requests, and eventfd signaling.

## Important APIs, Types, and Functions

`vfio_cdx_msi_enable()` allocates `struct vfio_cdx_irq` entries, enables MSI on the CDX device, allocates MSI domain IRQs, records virtual IRQ numbers, and stores `msi_count`. `vfio_cdx_msi_set_vector_signal()` binds or unbinds one vector to an eventfd and request_irq handler. `vfio_cdx_msi_set_block()` applies a range atomically enough to unwind previously configured entries on failure. `vfio_cdx_msi_disable()` tears down all vectors and disables MSI. The exported entry points are `vfio_cdx_set_irqs_ioctl()` and `vfio_cdx_irqs_cleanup()`.

## Control Flow

For `VFIO_IRQ_SET_DATA_EVENTFD`, the first trigger request lazily enables MSI for `cdx_dev->num_msi` vectors and then binds eventfds for the requested range. Later eventfd changes reuse the allocated vector array. A zero-count `DATA_NONE` request disables all MSI state. For `DATA_NONE` or `DATA_BOOL` trigger actions with existing vectors, the driver injects software eventfd signals rather than changing hardware configuration.

## State and Persistence Behavior

Interrupt state is held in `vdev->cdx_irqs`, per-vector `irq_no`, `trigger`, and allocated name strings, plus `vdev->msi_count`. This state lasts while the VFIO device is open or until userspace disables interrupts. Cleanup frees IRQ handlers, eventfd references, MSI domain IRQs, disables CDX MSI, frees the vector array, and resets counts.

## Dependencies and Integration Points

The file depends on the CDX bus MSI helpers (`cdx_enable_msi`, `cdx_disable_msi`), MSI domain allocation, `msi_get_virq`, Linux IRQ APIs, eventfd, and VFIO IRQ-set validation performed by `main.c`.

## Risks and Edge Cases

Range validation must avoid `start + count` overflow against `num_msi`/`msi_count`; the current code checks only normal unsigned addition. Rebinding a vector frees the previous IRQ and eventfd before acquiring the new eventfd, so a failed new bind leaves the vector disabled. `vfio_cdx_msi_disable()` calls `vfio_cdx_msi_set_block()` before testing `cdx_irqs`; with `msi_count == 0` this is harmless because count is zero.

## Test Signals

Exercise full enable, partial eventfd range bind, vector rebind, vector unbind with fd < 0, software trigger with `DATA_NONE` and `DATA_BOOL`, zero-count disable, allocation failure unwinds, IRQ handler eventfd signaling, and close-device cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/cdx/main.c

## Purpose

`main.c` implements the VFIO bus driver for CDX devices. It wraps CDX resources as VFIO regions, exposes MSI IRQs through VFIO ioctls, handles device reset and bus-master control, maps MMIO regions to userspace, and registers/unregisters CDX devices with VFIO.

## Important APIs, Types, and Functions

`vfio_cdx_ops` is the VFIO device-ops table. It provides init/release, open/close, ioctl, region-info caps, device-feature, mmap, and iommufd physical bind/attach support. `vfio_cdx_open_device()` snapshots CDX resources into `struct vfio_cdx_region`, sets read/write/mmap flags, resets the device, and probes bus-master clear support. `vfio_cdx_ioctl()` handles `GET_INFO`, `GET_IRQ_INFO`, `SET_IRQS`, and `RESET`; `vfio_cdx_ioctl_feature()` handles `VFIO_DEVICE_FEATURE_BUS_MASTER`. `vfio_cdx_mmap()` decodes the high-bit region index and remaps page-aligned resources.

## Control Flow

Probe allocates a `struct vfio_cdx_device`, registers it as a VFIO group device, and stores it in driver data. Open allocates a region table sized by `cdx_dev->res_count`, derives secure mmap eligibility only for page-aligned address and size, marks read and optionally write permissions, resets the device, and attempts `cdx_clear_master()` to determine BME control support. Userspace obtains device info, region info, IRQ info, and then maps or controls regions. Close frees the region table, resets the device again, and cleans up IRQs.

## State and Persistence Behavior

The driver maintains per-open region metadata and per-device IRQ/BME support state in `struct vfio_cdx_device`. Device reset and bus-master feature operations affect hardware state. There is no persistent storage; state is reconstructed on open and destroyed on close/remove.

## Dependencies and Integration Points

It depends on the CDX bus, CDX reset/master APIs, VFIO core, iommufd physical helpers, VFIO IRQ validation, Linux MM APIs, and optional `intr.c` MSI support. The CDX driver uses `CDX_DEVICE_DRIVER_OVERRIDE(..., CDX_ID_F_VFIO_DRIVER_OVERRIDE)` and `driver_managed_dma = true`.

## Risks and Edge Cases

Open allocates regions and resets before checking bus-master support; if `cdx_clear_master()` fails, BME feature ioctls become unsupported but open still succeeds. Close does not clear `vdev->regions` after `kfree()`, though the open/close lifetime should make reuse impossible. MMAP checks permissions and page alignment but relies on the region metadata being valid for the current open. IRQ info reports only one IRQ index representing all MSI vectors.

## Test Signals

Test probe/remove, open reset, resource flag translation, page-aligned and unaligned mmap eligibility, read-only write denial, region offset encoding, IRQ info with zero/nonzero MSI count, set-IRQ validation paths, reset ioctl, bus-master set/clear feature success and unsupported cases, iommufd bind/attach, and close cleanup after partially configured IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/private.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/cdx/private.h

## Purpose

`private.h` defines the CDX VFIO driver's private data structures, region-offset encoding, BME flag, and interrupt helper prototypes or stubs.

## Important APIs, Types, and Functions

`VFIO_CDX_OFFSET_SHIFT` is 40, so VFIO region offsets encode the region index in the upper address bits. `vfio_cdx_index_to_offset()` converts a region index to VFIO offset. `struct vfio_cdx_irq` stores MSI vector metadata, eventfd trigger, and IRQ name. `struct vfio_cdx_region` stores flags, resource type, physical address, and size. `struct vfio_cdx_device` embeds `struct vfio_device`, region table, IRQ lock, IRQ array, flags, and MSI count.

## Control Flow

The header has no runtime control flow. When `CONFIG_GENERIC_MSI_IRQ` is enabled, it declares the real interrupt helpers; otherwise, it provides static stubs returning `-EINVAL` and doing no cleanup.

## State and Persistence Behavior

It defines state layout but owns none directly. The layouts persist for the lifetime of the loaded module ABI between `main.c` and `intr.c`.

## Dependencies and Integration Points

It depends on mutex definitions and, through users, CDX/VFIO/eventfd types. It is the shared contract between the CDX VFIO open/mmap/ioctl path and the optional MSI implementation.

## Risks and Edge Cases

The 40-bit offset split caps index encoding assumptions and must remain aligned with `vfio_cdx_mmap()`. Conditional interrupt stubs mean the same driver can build without MSI support but userspace `SET_IRQS` will fail.

## Test Signals

Compile both MSI and non-MSI configurations, validate offset encode/decode for several region indexes, and confirm `BME_SUPPORT` gating works with the embedded flags field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/cdx/private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/container.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/container.c

## Purpose

`container.c` implements the legacy VFIO container device `/dev/vfio/vfio`. Containers collect one or more VFIO groups and attach them to a selected VFIO IOMMU backend, enabling userspace DMA mappings, page pinning, and DMA read/write for traditional group-based VFIO.

## Important APIs, Types, and Functions

`struct vfio_container` tracks a kref, attached group list, group rwsem, selected `vfio_iommu_driver`, backend data, and no-IOMMU mode. IOMMU backend registration is done by `vfio_register_iommu_driver()` and `vfio_unregister_iommu_driver()`. File operations expose `VFIO_GET_API_VERSION`, `VFIO_CHECK_EXTENSION`, `VFIO_SET_IOMMU`, and backend ioctl passthrough. Group entry points include `vfio_container_attach_group()`, `vfio_group_detach_container()`, `vfio_group_use_container()`, and `vfio_group_unuse_container()`. Device helpers call backend `register_device`, `unregister_device`, `pin_pages`, `unpin_pages`, and `dma_rw`.

## Control Flow

Opening `/dev/vfio/vfio` allocates an empty container. `VFIO_CHECK_EXTENSION` either asks the selected backend or probes all registered backends that are allowed for the container's current no-IOMMU mode. `VFIO_SET_IOMMU` requires at least one attached group and no existing backend, finds a backend whose `CHECK_EXTENSION` matches the arg, opens it, attaches every group in the container, then records the backend/data. Attaching a group claims DMA ownership for real IOMMU groups, rejects mixing real and no-IOMMU groups, optionally attaches the group to an already selected backend, marks the group as using the container, adds it to the list, and takes a container reference.

Detach removes the group from the backend, releases DMA ownership, removes it from the container list, and if it was the last group releases the backend and module reference, returning the container to an unprivileged unset state. Group use increments `container_users` and gets the group file only after an IOMMU backend is selected.

## State and Persistence Behavior

Container state persists across file references and group/device fds through kref references. The backend is intentionally released when the last group detaches. No-IOMMU containers can only use the built-in no-IOMMU backend, and real containers cannot mix with no-IOMMU groups. There is no file-backed persistence; DMA ownership and mappings live in the IOMMU backend.

## Dependencies and Integration Points

This file integrates with `group.c`, IOMMU group DMA ownership, legacy VFIO IOMMU backends, `vfio_noiommu`, CAP_SYS_RAWIO checks, misc device registration, and VFIO device-driver helper APIs. `vfio_container_init()` registers `/dev/vfio/vfio` and optionally registers no-IOMMU ops.

## Risks and Edge Cases

The container/group locking contract is critical: callers must hold `group->group_lock` around attach/detach/use/unuse, while container state is protected by `group_lock` rwsem. Backend selection iterates modules under `iommu_drivers_lock` and uses `try_module_get()`; failure unwinds must detach already attached groups in reverse. No-IOMMU support intentionally taints security expectations and must never mix with real IOMMU groups. Page pin/unpin helpers assume a valid backend and enforce `VFIO_PIN_PAGES_MAX_ENTRIES`.

## Test Signals

Test open/release, extension probing before and after backend selection, set-IOMMU without groups, duplicate set-IOMMU, attach/detach with and without existing backend, mixed no-IOMMU/real rejection, CAP_SYS_RAWIO enforcement, backend open/attach failure unwind, last-group backend release, group use before set-IOMMU rejection, device register/unregister callbacks, pin/unpin limit checks, DMA read/write passthrough, and init/cleanup with no-IOMMU enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/debugfs.c

## Purpose

`debugfs.c` provides optional VFIO debugfs support, mainly for devices with migration support. It creates a top-level `debugfs/vfio` directory and per-device subdirectories containing migration state and feature files.

## Important APIs, Types, and Functions

`vfio_debugfs_create_root()` and `vfio_debugfs_remove_root()` manage the global root. `vfio_device_debugfs_init()` creates a directory named after the VFIO device's underlying device and, when `vdev->mig_ops` exists, creates a `migration` directory with `state` and `features` seqfiles. `vfio_device_debugfs_exit()` removes the per-device tree. Readers are `vfio_device_state_read()` and `vfio_device_features_read()`.

## Control Flow

The state reader calls `migration_get_state()` and prints one of the known `VFIO_DEVICE_STATE_*` names. The feature reader prints supported migration feature strings based on `migration_flags` and dirty-tracking presence. Debugfs creation is typically called by VFIO core after a device is registered; vendor drivers can add children under the per-device migration directory.

## State and Persistence Behavior

Only debugfs dentries are stored, with each device keeping `vdev->debug_root`. The files reflect live driver state and have no persistence beyond debugfs.

## Dependencies and Integration Points

It depends on `CONFIG_VFIO_DEBUGFS`, debugfs, seq_file, VFIO migration ops, and device-managed seqfile helpers. HiSilicon ACC uses the created `migration` directory for vendor-specific debug files.

## Risks and Edge Cases

State reading assumes `vdev->mig_ops` remains valid while the debugfs file is open. The build-time `BUILD_BUG_ON` catches enum range drift for known migration state names. Debugfs is diagnostic only; user-visible ABI must not rely on it.

## Test Signals

Enable `CONFIG_VFIO_DEBUGFS`, register devices with and without migration ops, read state/features in every migration state, verify dirty-tracking string emission when `log_ops` exists, and confirm recursive removal on unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/device_cdev.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/device_cdev.c

## Purpose

`device_cdev.c` implements the VFIO device character-device path `/dev/vfio/devices/vfioX`. This is the newer IOMMUFD-centric interface where userspace opens a device cdev directly, binds it to an iommufd, and attaches or detaches IO address spaces without first opening a legacy VFIO group.

## Important APIs, Types, and Functions

`vfio_init_device_cdev()` assigns the device cdev number and initializes `device->cdev`. `vfio_device_fops_cdev_open()` creates a `vfio_device_file`, stores it as file private data, and points file mappings at the device pseudo-inode mapping. `vfio_df_ioctl_bind_iommufd()` handles `VFIO_DEVICE_BIND_IOMMUFD`, including token UUID checks, iommufd context acquisition, KVM reference capture, device open, device id return, and access grant publication. `vfio_df_unbind_iommufd()` closes and unbinds on file release. `vfio_df_ioctl_attach_pt()` and `vfio_df_ioctl_detach_pt()` call device ops for IOAS attach/detach, including PASID variants. `vfio_cdev_init()` and cleanup allocate the major/minor range.

## Control Flow

Opening a device cdev only allocates a device file and pins registration; actual device access is blocked until bind succeeds. Bind is rejected for group-backed device files, blocks legacy group opens through `vfio_device_block_group()`, serializes on the device set lock, verifies the device is not already open through this file, checks optional token UUID, gets an iommufd context from the user fd, obtains a safe KVM reference, opens the VFIO device, copies the device id back to userspace, marks `device->cdev_opened`, and uses release-store to publish `access_granted`. Failure unwinds close, KVM, iommufd, lock, and group block state.

Attach/detach parse fixed-size UAPI structs, validate flags, optionally parse PASID fields, and call the relevant VFIO device ops under `dev_set->lock`. If attaching succeeds but copying the resulting `pt_id` fails, the code detaches before returning `-EFAULT`.

## State and Persistence Behavior

The file manages transient per-open `vfio_device_file` state: `iommufd`, `devid`, KVM reference, and `access_granted`. Device-wide `cdev_opened` and legacy group block counts prevent simultaneous incompatible access paths. Nothing is file-backed; IOAS attachments live in the iommufd/device binding.

## Dependencies and Integration Points

It depends on VFIO core device-file helpers, IOMMUFD context APIs, token matching from device ops, KVM reference helpers, cdev allocation, and physical/emulated iommufd ops implemented in `iommufd.c`.

## Risks and Edge Cases

The cdev path must remain mutually exclusive with the group path. Bind blocks group access before opening and must always unblock on failure or unbind. `access_granted` uses release/acquire semantics with generic VFIO fops, so any changes must preserve ordering. PASID attach copy-to-user failure detaches through `device->ops->detach_ioas()` even when the attach was PASID-specific; this path should be checked against device ops expectations. Token UUID matching has three modes: no token support, required no-token match, and explicit user UUID.

## Test Signals

Test cdev open during unregister, bind with invalid fd/flags/argsz, token success/failure, duplicate bind, group-file rejection, group-open mutual exclusion, iommufd context failure, open-device failure unwind, attach/detach IOAS, attach/detach PASID, copy-to-user failure detach, unbind on release, and memory-ordering access checks in read/write/mmap/ioctl after bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/device_cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Kconfig

## Purpose

This Kconfig file enables VFIO support for NXP/Freescale QorIQ DPAA2 Management Complex devices on the fsl-mc bus.

## Important APIs, Types, and Functions

`VFIO_FSL_MC` is a tristate option under a menu that depends on `FSL_MC_BUS`. It selects `EVENTFD` for interrupt delivery.

## Control Flow

When selected, Kbuild includes the fsl-mc VFIO driver so fsl-mc devices can be passed to userspace through VFIO.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

The option depends on the fsl-mc bus and maps to the fsl-mc Makefile. It also relies on VFIO core being enabled by the surrounding top-level Kconfig inclusion.

## Risks and Edge Cases

The feature is bus-specific and only useful when fsl-mc objects exist. Interrupt support assumes eventfd.

## Test Signals

Build with `FSL_MC_BUS` and `VFIO_FSL_MC` as module and built-in, and verify the resulting module links `vfio_fsl_mc.o` and `vfio_fsl_mc_intr.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Makefile

## Purpose

This Makefile builds the VFIO driver for fsl-mc bus devices.

## Important APIs, Types, and Functions

`vfio-fsl-mc-y := vfio_fsl_mc.o vfio_fsl_mc_intr.o` composes the module, and `obj-$(CONFIG_VFIO_FSL_MC) += vfio-fsl-mc.o` enables it.

## Control Flow

Kbuild links the main fsl-mc VFIO implementation with its interrupt helper when `CONFIG_VFIO_FSL_MC` is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The file ties the Kconfig symbol to the two implementation objects and uses dual GPL/BSD SPDX metadata.

## Risks and Edge Cases

Object list drift would break symbols between `vfio_fsl_mc.c` and `vfio_fsl_mc_intr.c`.

## Test Signals

Compile `CONFIG_VFIO_FSL_MC=y` and `m` to verify object composition and exported internal helper resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc.c

## Purpose

`vfio_fsl_mc.c` implements VFIO access for NXP/Freescale Management Complex bus devices, including DPRC containers and child objects. It exposes MC object regions, command portal read/write operations, reset, interrupts, MMIO mapping, iommufd physical binding, and DPRC container scanning/driver-override handling.

## Important APIs, Types, and Functions

`vfio_fsl_mc_ops` is the VFIO device-ops table. Key functions are `vfio_fsl_mc_open_device()`, `vfio_fsl_mc_close_device()`, `vfio_fsl_mc_ioctl()`, `vfio_fsl_mc_read()`, `vfio_fsl_mc_write()`, `vfio_fsl_mc_mmap()`, `vfio_fsl_mc_reset_device()`, `vfio_fsl_mc_init_device()`, `vfio_fsl_mc_scan_container()`, and the fsl-mc driver probe/remove functions. `vfio_fsl_mc_bus_notifier()` helps force children of a VFIO-bound DPRC toward the VFIO driver.

## Control Flow

Probe allocates a VFIO device, registers it with VFIO, scans a DPRC container if applicable, and stores driver data. Init assigns the device set: DPRCs use themselves, non-DPRC children use their parent, so related objects share VFIO serialization. DPRC init registers a bus notifier and performs `dprc_setup()` to open the container and allocate an MC portal; non-DPRC init reuses the parent `mc_io`.

Open allocates region metadata from `obj_desc.region_count`, disables mmap for DPRC portals, marks page-aligned non-DPRC regions mmap-capable, and sets read/write flags from fsl-mc resources. Userspace ioctls obtain device info, IRQ info, configure IRQs through `vfio_fsl_mc_intr.c`, or reset the object. Reads and writes are restricted to 64-byte offset-zero command portal accesses; writes submit an MC command and poll for completion, while reads fetch the 8 qwords in reverse order. Close unmaps regions, resets the object, cleans IRQs, and cleans the container IRQ pool.

## State and Persistence Behavior

Per-device state includes `mc_dev`, bus notifier, region table with optional `ioaddr` mappings, interrupt gate mutex, and IRQ array managed by the companion file. DPRC scans can create/remove child devices and set driver overrides; reset operations affect MC object hardware state. No state is file-backed.

## Dependencies and Integration Points

The driver integrates with VFIO core, IOMMUFD physical helpers, fsl-mc object APIs, DPRC setup/scan/remove/reset, MC command portal layout, Linux MMIO remapping, eventfd interrupts, and fsl-mc bus notifications. It sets `driver_managed_dma = true`.

## Risks and Edge Cases

Portal read/write requires exactly 64 bytes at offset zero; partial or misaligned userspace accesses fail. `vfio_fsl_mc_send_command()` uses fixed udelay polling up to 5 seconds, which can block the calling task. DPRC close resets before IRQ cleanup and then cleans the parent container IRQ pool; failure ordering should be tested. The bus notifier sets driver override on new children but only warns if a non-VFIO driver binds. Region `ioaddr` mappings are lazy and cleaned on close.

## Test Signals

Test DPRC and non-DPRC probe/init, container scan failure unwind, region flag generation, mmap denial for DPRC, command portal 64-byte read/write, command timeout, reset ioctl, IRQ setup/cleanup, close with reset failure warning, bus notifier driver override, remove with child cleanup, and iommufd attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_intr.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_intr.c

## Purpose

`vfio_fsl_mc_intr.c` implements eventfd-backed IRQ configuration for fsl-mc VFIO devices.

## Important APIs, Types, and Functions

`vfio_fsl_mc_irqs_allocate()` allocates per-IRQ metadata and fsl-mc IRQs. `vfio_set_trigger()` binds or unbinds one MC IRQ to an eventfd and Linux IRQ handler. `vfio_fsl_mc_set_irq_trigger()` validates VFIO IRQ trigger operations, populates the parent container IRQ pool, allocates device IRQs, and handles eventfd assignment or software trigger. Public functions are `vfio_fsl_mc_set_irqs_ioctl()` and `vfio_fsl_mc_irqs_cleanup()`.

## Control Flow

`VFIO_DEVICE_SET_IRQS` arrives in the main file under `vdev->igate`. For a trigger action, this file either disables one index for zero-count `DATA_NONE`, or requires `start == 0` and `count == 1`. It populates the container IRQ pool under `dev_set->lock`, lazily allocates device IRQs, then either binds an eventfd, signals an existing eventfd, or conditionally signals based on a bool byte. Cleanup unbinds every configured IRQ, frees fsl-mc IRQs, frees the metadata array, and clears it.

## State and Persistence Behavior

State resides in `vdev->mc_irqs`; each element stores flags, count, trigger, and name. fsl-mc IRQ resources live in `mc_dev->irqs` and the parent container IRQ pool. All are transient and released on close or explicit cleanup.

## Dependencies and Integration Points

It depends on eventfd, Linux IRQ APIs, fsl-mc IRQ allocation/free, parent container IRQ-pool helpers, VFIO IRQ-set validation by the caller, and `vfio_fsl_mc_private.h`.

## Risks and Edge Cases

Index validation is mostly delegated to the caller, but `vfio_fsl_mc_set_irq_trigger()` directly indexes `mc_irqs[index]`; bad validation would be serious. If `eventfd_ctx_fdget()` fails after allocating a name, the name is freed and trigger remains unset. If `request_irq()` fails, the eventfd is dropped. The container IRQ pool is populated for each setup request and cleaned in close.

## Test Signals

Test devices with zero IRQs, lazy allocation, eventfd bind/unbind, software triggers, bool triggers, invalid start/count, IRQ-pool population failure, fsl-mc IRQ allocation failure, request_irq failure, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_private.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_private.h

## Purpose

This private header defines VFIO fsl-mc offset encoding, per-region/per-IRQ metadata, per-device state, and interrupt helper prototypes.

## Important APIs, Types, and Functions

`VFIO_FSL_MC_OFFSET_SHIFT` is 40, with macros to convert VFIO offsets to region indexes and indexes back to offsets. `struct vfio_fsl_mc_irq` stores eventfd trigger and IRQ name. `struct vfio_fsl_mc_region` stores VFIO flags, fsl-mc type bits, physical address, size, and lazy `ioaddr`. `struct vfio_fsl_mc_device` embeds `vfio_device` and stores `mc_dev`, notifier, regions, interrupt mutex, and IRQ array.

## Control Flow

The header has no runtime flow. It defines the shared interface between `vfio_fsl_mc.c` and `vfio_fsl_mc_intr.c`.

## State and Persistence Behavior

It defines transient in-kernel state. Region mappings and IRQ eventfds are allocated during open/IRQ setup and freed on close.

## Dependencies and Integration Points

It depends on fsl-mc and VFIO types through the including C files and declares interrupt setup/cleanup functions used by the main driver.

## Risks and Edge Cases

The offset shift must match mmap/read/write region-index decoding. Lazy `ioaddr` lifetime requires every mapped region to be unmapped in cleanup.

## Test Signals

Compile both implementation files together, validate offset/index conversions, and exercise lazy mapping cleanup for every region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/group.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/group.c

## Purpose

`group.c` implements the legacy VFIO group device `/dev/vfio/$GROUP` and group lifecycle. VFIO groups collect devices sharing an IOMMU group, expose ioctls to set a container or iommufd compatibility context, provide device fds by name, and coordinate mutual exclusion with the direct cdev path.

## Important APIs, Types, and Functions

Key routines are `vfio_group_ioctl_set_container()`, `vfio_group_ioctl_unset_container()`, `vfio_group_ioctl_get_device_fd()`, `vfio_group_ioctl_get_status()`, `vfio_device_open_file()`, `vfio_df_group_open()`, `vfio_df_group_close()`, `vfio_device_block_group()`, `vfio_device_unblock_group()`, `vfio_device_set_group()`, `vfio_device_remove_group()`, `vfio_device_group_register()`, and `vfio_group_init()/cleanup()`. Global state tracks `group_list`, `group_lock`, an IDA for minors, and the char-device major.

## Control Flow

Group creation happens when a VFIO device registers. The driver finds an existing group by `iommu_group` or allocates a new cdev-backed group; no-IOMMU can synthesize an IOMMU group and taint the kernel. Opening `/dev/vfio/$GROUP` requires active drivers, CAP_SYS_RAWIO for no-IOMMU, no cdev-opened devices, and no existing group open. `SET_CONTAINER` accepts either a legacy container fd or an iommufd; the latter creates a compatibility IOAS. `GET_DEVICE_FD` finds the device by driver match or device name, allocates a `vfio_device_file`, opens the device under group and device-set locks, attaches a compat IOAS for iommufd groups on first open, and returns an anon inode device fd.

On group fd release, any attached legacy container or iommufd is detached and the group becomes unopened. When the final driver leaves a group, `vfio_device_remove_group()` removes the cdev, detaches any container, nulls the IOMMU group to block new users, drops references, and frees the group device.

## State and Persistence Behavior

Groups persist while at least one VFIO device driver is registered in the group. State includes the underlying `iommu_group`, device list, group/container/iommufd pointers, container user count, KVM pointer, open group file, cdev open count, and driver refcount. This is all in-kernel lifetime state. No-IOMMU groups are synthetic and removed when the device unregisters.

## Dependencies and Integration Points

The file integrates legacy containers from `container.c`, iommufd compatibility helpers, VFIO device-file core, KVM pointer handling, IOMMU group APIs, anon inodes, character devices, and exported helpers used by KVM/SPAPR and other VFIO code.

## Risks and Edge Cases

The group path and cdev path are mutually exclusive through `opened_file` and `cdev_device_open_cnt`. Races around unregister are handled by `drivers` refcount and group locks; tests should stress device removal during group open/get-device-fd. With iommufd compatibility, `GET_STATUS` can show viable before `GET_DEVICE_FD` fails due to DMA-owner claim, as documented in comments. No-IOMMU access must enforce CAP_SYS_RAWIO and reject compat IOAS use. The device fd holds references transferred from device registration and group file references.

## Test Signals

Test group creation/reuse, duplicate device in group warning path, no-IOMMU synthetic group creation and taint, group open exclusivity, cdev/group mutual exclusion, status flags before/after container/iommufd, set/unset container, get-device-fd success/failure, KVM reference capture/release, iommufd compat attach, group remove while users exist, SPAPR `vfio_file_iommu_group()`, and cleanup with empty group list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/iommufd.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/iommufd.c

## Purpose

`iommufd.c` provides VFIO helper operations for binding devices to IOMMUFD and attaching IO address spaces. It supports physical-device bindings and emulated/mdev-style access bindings, plus legacy group compatibility IOAS helpers.

## Important APIs, Types, and Functions

Compatibility helpers include `vfio_iommufd_device_has_compat_ioas()`, `vfio_df_iommufd_bind()`, `vfio_iommufd_compat_attach_ioas()`, and `vfio_df_iommufd_unbind()`. Physical-device helpers are `vfio_iommufd_physical_bind()`, `vfio_iommufd_physical_unbind()`, `vfio_iommufd_physical_attach_ioas()`, `vfio_iommufd_physical_detach_ioas()`, and PASID attach/detach variants. Emulated-device helpers are `vfio_iommufd_emulated_bind()`, `vfio_iommufd_emulated_unbind()`, `vfio_iommufd_emulated_attach_ioas()`, and detach. Exported query helpers expose a device's IOMMUFD context and device id.

## Control Flow

Physical bind calls `iommufd_device_bind()` on `vdev->dev`, stores the iommufd device, and initializes a PASID IDA. Attach either attaches or replaces the non-PASID IOAS and sets `iommufd_attached`. PASID attach tracks attached PASIDs in an IDA and replaces an existing PASID or attaches a new one. Physical unbind detaches all PASIDs, detaches the non-PASID IOAS if present, unbinds the iommufd device, and clears the pointer.

Emulated bind creates an `iommufd_access` object with unmap callback `vfio_emulated_unmap()`, which forwards to driver `dma_unmap` when present. Emulated attach/replace uses `iommufd_access_attach()` or replace and marks `iommufd_attached`; detach calls `iommufd_access_detach()`.

## State and Persistence Behavior

State is stored in `struct vfio_device`: `iommufd_device`, `iommufd_access`, `iommufd_attached`, and PASID IDA. Attachments persist for the open VFIO device file and are destroyed on unbind/close. No file-backed persistence exists.

## Dependencies and Integration Points

The file imports the `IOMMUFD` and `IOMMUFD_VFIO` namespaces and depends on VFIO device ops, iommufd device/access APIs, IOMMU group checks, and the device-set lock held by callers.

## Risks and Edge Cases

Every function assumes `dev_set->lock` where stated. Physical unbind loops through all PASIDs and must run before destroying the IDA users. `vfio_iommufd_get_dev_id()` distinguishes an owned device with no id (`-ENOENT`) from a device not owned by the context (`-ENODEV`). No-IOMMU returns success for bind/attach compatibility without creating real translations, relying on higher-level CAP and IOAS checks.

## Test Signals

Test physical bind/unbind, attach/replace/detach, PASID attach/replace/detach, unbind with active PASIDs, emulated bind/attach/detach/unmap callback, compat IOAS attach for group path, no-IOMMU shortcuts, exported device id query for same context/group context/unowned context, and lockdep coverage for device-set locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/iommufd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/Kconfig

## Purpose

This Kconfig file declares the mediated device core symbol used by VFIO and mdev-capable parent drivers.

## Important APIs, Types, and Functions

`VFIO_MDEV` is a tristate symbol with no prompt in this file, so it is selected by other features rather than normally chosen directly by users.

## Control Flow

When enabled, Kbuild builds the mdev core bus, sysfs, and driver-registration support.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

The symbol maps to `drivers/vfio/mdev/Makefile` and the exported mdev APIs used by parent/device drivers.

## Risks and Edge Cases

Because the option has no prompt, missing selects from consumers can silently omit mdev infrastructure.

## Test Signals

Build consumers that select mdev and ensure `mdev.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/Makefile

## Purpose

This Makefile builds the mediated device core module.

## Important APIs, Types, and Functions

`mdev-y` is composed from `mdev_core.o`, `mdev_sysfs.o`, and `mdev_driver.o`; `obj-$(CONFIG_VFIO_MDEV) += mdev.o` enables the aggregate object.

## Control Flow

Kbuild links the core lifecycle, sysfs, and bus/driver files into one module or built-in object.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies and Integration Points

The object list is the build contract for the mdev core exported APIs and bus type.

## Risks and Edge Cases

Dropping one object breaks exported helper resolution or mdev sysfs behavior.

## Test Signals

Build `CONFIG_VFIO_MDEV=y` and `m`, and verify mdev parent registration and driver registration link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_core.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_core.c

## Purpose

`mdev_core.c` implements the mediated device core lifecycle. It lets a parent device register supported mdev types, lets userspace create/remove mdev instances through sysfs, attaches the selected mdev driver explicitly, and removes all children during parent unregister.

## Important APIs, Types, and Functions

Exported APIs are `mdev_register_parent()`, `mdev_unregister_parent()`, `mdev_device_create()`, and `mdev_device_remove()`. Global state includes `mdev_list`, `mdev_list_lock`, and a compatibility class. Internal helpers are `mdev_device_remove_common()`, `mdev_device_remove_cb()`, and `mdev_device_release()`.

## Control Flow

Parent registration initializes `unreg_sem`, stores the parent device, mdev driver, type array, and available instance count, creates sysfs type files, creates a class compatibility link, logs registration, and emits a `KOBJ_CHANGE` uevent. Creation parses through sysfs in `mdev_sysfs.c`, checks duplicate UUIDs under `mdev_list_lock`, reserves an available instance when no dynamic `get_available` callback exists, allocates and initializes an `mdev_device`, takes a type kobject reference, adds it to the global list, names it by UUID, obtains a read lock on the parent unregister semaphore, adds the device, explicitly attaches the parent's mdev driver, creates mdev sysfs links, marks it active, and releases the semaphore.

Removal verifies the device is in the global list and active, marks it inactive, obtains the unregister semaphore read lock, removes sysfs links, deletes the device, and drops the initialization reference. Parent unregister takes the write lock, removes the compatibility link, removes every mdev child with the callback, removes parent sysfs, releases the lock, and emits an unregister uevent.

## State and Persistence Behavior

Mdev instances persist as kernel devices named by UUID until removed or until the parent unregisters. Instance accounting is either dynamic through driver `get_available()` or atomic `available_instances`. The global list enforces UUID uniqueness across all mdevs. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on the mdev bus from `mdev_driver.c`, sysfs helpers from `mdev_sysfs.c`, class compatibility links, kobject uevents, UUIDs, and parent-driver callbacks.

## Risks and Edge Cases

The parent unregister semaphore prevents creation/removal races with parent teardown. A failed `device_driver_attach()` or sysfs link creation must delete the device and eventually restore instance counts through release. `mdev_device_remove()` returns `-EAGAIN` if another removal already marked the device inactive. Global UUID uniqueness can reject duplicates across different parents.

## Test Signals

Test parent registration/unregistration, sysfs type creation failure unwind, duplicate UUID rejection, available-instance exhaustion/restoration, creation during unregister, attach failure unwind, sysfs link failure unwind, remove idempotence, parent unregister removing active children, uevents, and module init/exit bus/class registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_driver.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_driver.c

## Purpose

`mdev_driver.c` defines the mdev bus type and exported driver registration helpers.

## Important APIs, Types, and Functions

`mdev_bus_type` has name `mdev`, probe/remove callbacks, and a `match` callback that always returns 0. `mdev_register_driver()` validates `device_api`, assigns the bus, and registers the driver. `mdev_unregister_driver()` unregisters it. Probe/remove dispatch to optional `mdev_driver` callbacks.

## Control Flow

Mdev devices are not auto-bound by matching. Instead, `mdev_device_create()` explicitly calls `device_driver_attach()` with the parent-selected driver. During attach, `mdev_probe()` invokes the driver probe callback. During device removal or driver unregistration, `mdev_remove()` invokes the optional remove callback.

## State and Persistence Behavior

The file defines bus/driver registration state only. Per-device lifecycle state is in `mdev_core.c`.

## Dependencies and Integration Points

It integrates Linux driver core bus registration with mdev parent/device APIs. `mdev_bus_type` is exported via private header for core device initialization.

## Risks and Edge Cases

The no-auto-match design is intentional; changing it could bind mdev devices to unintended drivers. `device_api` is required because userspace and VFIO need to know what kind of device API the mdev implements.

## Test Signals

Register a driver without `device_api` and expect `-EINVAL`; create an mdev and verify explicit attach calls probe; remove and unregister drivers to verify remove callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_private.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_private.h

## Purpose

This private header shares mdev bus, sysfs, and device lifecycle declarations among the mdev core source files.

## Important APIs, Types, and Functions

It declares `mdev_bus_type`, `mdev_device_groups`, type conversion macros, parent sysfs helpers, mdev sysfs helpers, and internal create/remove functions.

## Control Flow

There is no runtime flow. The declarations connect `mdev_core.c`, `mdev_driver.c`, and `mdev_sysfs.c`.

## State and Persistence Behavior

The header owns no state; it defines access to shared mdev structures.

## Dependencies and Integration Points

It depends on public mdev types and Linux container macros through included users. It is internal to the mdev module.

## Risks and Edge Cases

Macro correctness matters for kobject/attribute container conversions. Misuse would corrupt sysfs show/store context.

## Test Signals

Compile all mdev objects with sparse/build warnings and exercise every sysfs attribute path that uses the conversion macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_sysfs.c

## Purpose

`mdev_sysfs.c` creates the userspace sysfs interface for mediated device types and instances. It exposes supported type attributes, creation entry points, per-type device links, and per-mdev removal.

## Important APIs, Types, and Functions

`struct mdev_type_attribute` wraps kobject attributes with mdev-type show/store callbacks. Core type attributes are `create`, `device_api`, `name`, `available_instances`, and optional `description`. Public helpers are `parent_create_sysfs_files()`, `parent_remove_sysfs_files()`, `mdev_create_sysfs_files()`, and `mdev_remove_sysfs_files()`. The per-mdev device attribute is write-only `remove`.

## Control Flow

Parent registration creates a `mdev_supported_types` kset under the parent device and adds each type kobject named from the parent driver string and type sysfs name. Each type gets core attributes and a `devices` kobject. Writing a UUID string to `create` parses it and calls `mdev_device_create()`. After a device is added, `mdev_create_sysfs_files()` links the mdev under the type's `devices` directory and links the mdev back to its `mdev_type`. Writing nonzero to the mdev `remove` attribute uses `device_remove_file_self()` and then calls `mdev_device_remove()`.

## State and Persistence Behavior

Sysfs kobjects and links persist while the parent/type/mdev exists. The type kobject holds a parent device reference until release. No persistent storage exists; created mdevs are kernel devices.

## Dependencies and Integration Points

The file depends on sysfs/kobject APIs, GUID parsing, mdev parent/type structures, mdev lifecycle functions, and optional parent driver callbacks such as `show_description()` and `get_available()`.

## Risks and Edge Cases

UUID input length is tightly constrained to canonical string length plus optional newline. Type removal must remove `devices_kobj`, delete the type kobject, and drop references in the right order. If creating the second sysfs link fails, the first is removed. `remove_store()` relies on `device_remove_file_self()` to avoid racing removal of the attribute being written.

## Test Signals

Test type kset creation failure, per-type add failure unwind, attribute visibility without `show_description`, UUID parsing failures, duplicate and valid create, available instance reporting with static and dynamic providers, link creation/removal, self-remove behavior, and parent removal with active type/device links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/Kconfig

## Purpose

This Kconfig file defines VFIO support for PCI devices, including the common PCI core, generic vfio-pci driver, optional architecture/device extensions, dmabuf support, and vendor-specific variant drivers.

## Important APIs, Types, and Functions

Core symbols include `VFIO_PCI_CORE`, `VFIO_PCI_INTX`, and `VFIO_PCI`. Optional generic extensions include `VFIO_PCI_VGA`, `VFIO_PCI_IGD`, `VFIO_PCI_ZDEV_KVM`, and `VFIO_PCI_DMABUF`. It sources Kconfig files for mlx5, ISM, HiSilicon, pds, virtio, nvgrace-gpu, qat, and xe variant drivers.

## Control Flow

When `PCI` is available and top-level VFIO sources this menu, users can enable generic PCI VFIO or specific variant drivers. Variant drivers generally select `VFIO_PCI_CORE` and provide device-specific behavior while reusing common VFIO PCI helpers.

## State and Persistence Behavior

The file creates `.config` build state only.

## Dependencies and Integration Points

It integrates VFIO with PCI, IRQ bypass, virqfd, architecture features such as x86 VGA/IGD and s390 KVM, PCI P2PDMA/dmabuf, and vendor subdirectories.

## Risks and Edge Cases

The generic and variant driver split relies on correct selects. Enabling a variant without core support would fail, so each sub-Kconfig must select `VFIO_PCI_CORE`. Architecture-conditional extensions should remain hidden where unsupported.

## Test Signals

Build generic vfio-pci with and without VGA/IGD/zPCI/dmabuf and build each variant driver as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/Makefile

## Purpose

This Makefile builds the VFIO PCI core, the generic vfio-pci driver, and vendor/device-specific VFIO PCI variant subdirectories.

## Important APIs, Types, and Functions

`vfio-pci-core-y` includes `vfio_pci_core.o`, `vfio_pci_intrs.o`, `vfio_pci_rdwr.o`, and `vfio_pci_config.o`, with optional `vfio_pci_zdev.o` and `vfio_pci_dmabuf.o`. `vfio-pci-y` includes `vfio_pci.o` and optional `vfio_pci_igd.o`. Subdirectories are selected for mlx5, ism, hisilicon, pds, virtio, nvgrace-gpu, qat, and xe.

## Control Flow

Kbuild links the common PCI core object when `CONFIG_VFIO_PCI_CORE` is set, the generic driver when `CONFIG_VFIO_PCI` is set, and each variant directory according to its symbol.

## State and Persistence Behavior

There is no runtime state; it controls build linkage.

## Dependencies and Integration Points

The object composition must match Kconfig symbols and exported functions used by variant drivers such as ISM and HiSilicon.

## Risks and Edge Cases

Variant drivers depend on the core object exports. Missing optional objects can break architecture-specific paths, for example zPCI or dmabuf support.

## Test Signals

Build with each PCI VFIO symbol on/off and as modules to verify object composition and subdirectory traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Kconfig

## Purpose

This Kconfig file enables the HiSilicon ACC VFIO PCI variant driver, which adds live migration support for HiSilicon accelerator virtual functions.

## Important APIs, Types, and Functions

`HISI_ACC_VFIO_PCI` is a tristate option depending on ARM64 or 64-bit compile test, PCI MSI, and HiSilicon QM/HPRE/SEC2/ZIP crypto drivers. It selects `VFIO_PCI_CORE`.

## Control Flow

When selected, the hisilicon subdirectory builds `hisi-acc-vfio-pci.o`, allowing supported Huawei accelerator VFs to bind through driver override and reuse VFIO PCI core.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

It ties the variant to hardware crypto drivers that provide PF/QM access needed for migration, plus PCI MSI and VFIO PCI core.

## Risks and Edge Cases

Migration support depends on PF driver availability and hardware generation. Kconfig dependencies ensure compile-time access to PF helper symbols but do not guarantee runtime PF binding.

## Test Signals

Build on ARM64 and COMPILE_TEST 64-bit configs with required crypto drivers enabled, and verify unsupported architectures hide the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Makefile

## Purpose

This Makefile builds the HiSilicon ACC VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_HISI_ACC_VFIO_PCI) += hisi-acc-vfio-pci.o` enables the aggregate object, and `hisi-acc-vfio-pci-y := hisi_acc_vfio_pci.o` supplies its implementation.

## Control Flow

Kbuild compiles the driver when the Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The Makefile maps Kconfig to the single implementation file and depends on VFIO PCI core being selected by Kconfig.

## Risks and Edge Cases

Filename or symbol drift would break the variant build.

## Test Signals

Build `CONFIG_HISI_ACC_VFIO_PCI=y` and `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.c

## Purpose

`hisi_acc_vfio_pci.c` is a VFIO PCI variant driver for HiSilicon SEC/HPRE/ZIP accelerator VFs. It reuses VFIO PCI core for normal access and, when the VF has a suitable PF/QM backend, adds VFIO live migration support by saving/restoring queue-manager register state, queue context DMA addresses, and match metadata through VFIO migration files.

## Important APIs, Types, and Functions

Hardware helpers read/write QM registers and mailboxes: `qm_get_vft()`, `qm_get_sqc()`, `qm_get_cqc()`, `qm_get_regs()`, `qm_set_regs()`, `pf_qm_get_qp_num()`, `vf_qm_cache_wb()`, `vf_qm_func_stop()`, and `hisi_acc_check_int_state()`. Migration data helpers are `vf_qm_get_match_data()`, `vf_qm_check_match()`, `vf_qm_read_data()`, `vf_qm_state_save()`, and `vf_qm_load_data()`.

Migration file operations include resume write, save read, and precopy ioctl helpers. State-machine entry points are `hisi_acc_vfio_pci_set_device_state()`, `hisi_acc_vfio_pci_get_device_state()`, and `hisi_acc_vfio_pci_get_data_size()`. VFIO ops are split into migration-capable `hisi_acc_vfio_pci_migrn_ops` and generic `hisi_acc_vfio_pci_ops`. Probe selects migration ops only for supported VFs with an accessible PF QM version at least `QM_HW_V3`.

## Control Flow

Probe identifies PF QM data by VF device id and PF driver, chooses migration ops when possible, allocates a `hisi_acc_vf_core_device`, registers it with VFIO PCI core, and creates vendor debugfs. Open enables the PCI core and, for migration ops, initializes VF QM access. Old hardware maps the full VF BAR2 and hides the migration half from userspace; newer hardware uses a PF BAR2 migration region offset by VF id. Close disables migration files, clears `dev_opened`, unmaps old-mode BAR2, and closes VFIO PCI core.

Migration follows VFIO's state graph. RUNNING to PRE_COPY opens a read migration file containing match data. PRE_COPY to STOP_COPY stops the VF, checks interrupt/RAS state, writes back cache, and fills the save file with full state. RUNNING to STOP stops without opening a file. STOP to STOP_COPY opens a stop-copy save file. STOP to RESUMING opens a write migration file; RESUMING to STOP loads received state and closes files. STOP to RUNNING restarts the device if restored state was ready. Reset handlers serialize with PF reset state and reset VF migration state after AER reset.

## State and Persistence Behavior

Persistent runtime state lives in `struct hisi_acc_vf_core_device`: VFIO PCI core device, migration state, VF/PF pci devices, PF/VF QM handles, hardware mode, VF id, VF QM state, migration file pointers, debug migration copy, reset flag, and open/state mutexes. Migration payload state is `struct acc_vf_data`, including magic/version, qp count/base, device id, isolation config, QM register snapshots, interrupt masks, EQ/AEQ registers, reserved registers, and DMA base addresses. No data is file-backed beyond anonymous migration file descriptors returned to userspace.

## Dependencies and Integration Points

The driver depends on VFIO PCI core, VFIO migration core, IOMMUFD physical helpers, HiSilicon QM/SEC/HPRE/ZIP PF driver helpers, PCI SR-IOV VF identification, PCI AER reset callbacks, debugfs, anon inodes, eventfd headers, and hardware register definitions in its header. It supports Huawei SEC, HPRE, and ZIP VFs through `PCI_DRIVER_OVERRIDE_DEVICE_VFIO`.

## Risks and Edge Cases

Migration correctness depends on exact hardware state sequencing. Stop must pause QM, verify PF/VF interrupt state is idle, and write back cache before reading registers. Resume validates magic/version, device id, qp count, and isolation state before accepting the stream; if only match data is present, it can complete without loading queue state. BAR2 filtering is critical in old VF-control mode so userspace cannot access the migration control half. Migration files can be disabled asynchronously by state transitions and close; file operations must return `-ENODEV` after disable.

The code returns `-EFAULT` to userspace when `vf_qm_check_match()` fails during resume write, even though the cause may be semantic mismatch. Reset prepare spins up to `QM_RESET_WAIT_TIMEOUT` milliseconds waiting for PF reset ownership. Debugfs reads require the device to be open because `io_base` is otherwise unavailable.

## Test Signals

Test probe with and without PF driver data, hardware mode selection, BAR2 region-size filtering, read/write/mmap denial of migration BAR space, open/close migration setup, every VFIO migration state transition, precopy ioctl byte counts, save file read bounds, resume write bounds and match failures, V1 and V2 migration magic handling, stop-device interrupt busy cases, cache writeback timeout, resume with missing DMA addresses, AER reset prepare/done, debugfs output, and remove cleanup after active migration files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.h

## Purpose

This header defines HiSilicon ACC VFIO PCI migration register constants, migration payload layout, migration file state, and per-device private state.

## Important APIs, Types, and Functions

It defines QM mailbox timeouts, cache writeback registers, interrupt status registers, VFT registers, queue context register offsets, migration version/magic constants, and migration region offsets/sizes. `enum hw_drv_mode` distinguishes VF-controlled and PF-controlled migration register placement. `struct acc_vf_data` is the migration stream payload and includes match metadata, saved QM registers, and queue context DMA addresses. `struct hisi_acc_vf_migration_file` wraps anonymous migration file state. `struct hisi_acc_vf_core_device` extends `vfio_pci_core_device` with migration, PF/VF QM, reset, open, and debug state.

## Control Flow

The header has no executable flow but defines the data consumed by save/restore and BAR filtering in the implementation.

## State and Persistence Behavior

`acc_vf_data` is the transient migration state serialized through VFIO migration file descriptors. Device private state persists for the lifetime of the VFIO device registration and open sessions.

## Dependencies and Integration Points

It depends on `linux/hisi_acc_qm.h` for QM definitions and on VFIO PCI core through the embedding implementation. The magic/version fields provide compatibility between migration stream versions.

## Risks and Edge Cases

The layout of `struct acc_vf_data` is ABI-relevant for migration. `QM_MATCH_SIZE` controls when resume has enough data to validate source/destination compatibility; changing field order before that offset changes compatibility behavior. Register constants must match hardware generation and old/new migration-control placement.

## Test Signals

Validate `sizeof(struct acc_vf_data)`, `QM_MATCH_SIZE`, V1/V2 magic handling, BAR2 size constants, and old/new hardware mode register offsets in migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Kconfig

## Purpose

This Kconfig file enables the IBM ISM VFIO PCI variant driver for s390.

## Important APIs, Types, and Functions

`ISM_VFIO_PCI` is a tristate option depending on `S390` and selecting `VFIO_PCI_CORE`.

## Control Flow

When selected, the ISM variant driver builds and can bind IBM Internal Shared Memory PCI devices through VFIO.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

It integrates the variant with s390 zPCI behavior and VFIO PCI core.

## Risks and Edge Cases

The driver is architecture-specific because it relies on zPCI load/store instructions and ISM device constraints.

## Test Signals

Build on s390 with `ISM_VFIO_PCI=y/m` and verify the option is unavailable elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Makefile

## Purpose

This Makefile builds the IBM ISM VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ISM_VFIO_PCI) += ism-vfio-pci.o` enables the aggregate object, and `ism-vfio-pci-y := main.o` supplies its implementation.

## Control Flow

Kbuild compiles the ISM variant when the Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies and Integration Points

It maps Kconfig to the implementation file and relies on VFIO PCI core being selected.

## Risks and Edge Cases

Object-name drift would break module creation.

## Test Signals

Build as built-in and module on s390.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/main.c

## Purpose

`main.c` implements the s390 IBM Internal Shared Memory VFIO PCI variant. It reuses VFIO PCI core but overrides region offsets and read/write paths because ISM devices cannot use PCI MIO instructions and require PCISTB store-block writes for BAR access.

## Important APIs, Types, and Functions

`struct ism_vfio_pci_core_device` extends `vfio_pci_core_device` with a store-block kmem cache. `ISM_READ()` generates `ism_read8/16/32/64()` wrappers using `__zpci_load()`. `ism_vfio_pci_do_io_r()` performs aligned function-handle-based reads; `ism_vfio_pci_do_io_w()` uses `__zpci_store_block()` with cache-allocated, page-aligned buffers. `ism_vfio_pci_rw()` dispatches config and BAR access. `ism_vfio_pci_ioctl_get_region_info()` reports region offsets using a 48-bit offset shift. `ism_pci_ops` is the VFIO ops table.

## Control Flow

Probe allocates the extended device, stores core driver data, and registers with VFIO PCI core. Init creates a per-function store-block kmem cache named by zPCI function id and sized/aligned to `zdev->maxstbl`, then calls core init. Open enables and finishes VFIO PCI core. Reads and writes decode the high 48-bit-style region index: config space uses common single-access config helpers because zPCI config access must not use MIO, while BAR access uses explicit zPCI load/store-block operations. Remove unregisters core and drops the device reference.

## State and Persistence Behavior

Runtime state is the per-device store-block cache and VFIO PCI core state. BAR/config accesses affect device hardware. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on s390 zPCI internals, VFIO PCI private/core helpers, kmem cache APIs with usercopy metadata, and IOMMUFD physical helper ops through its VFIO ops.

## Risks and Edge Cases

BAR write size must be no larger than `zdev->maxstbl` and cannot cross a page boundary. The custom offset shift is 48 bits, larger than generic VFIO PCI's shift, to represent ISM's huge BAR0 write space. The read path chooses the widest aligned load possible; unaligned or small reads degrade to narrower loads. Mmap is not supplied, so access is via read/write.

## Test Signals

Test config read/write, BAR0 huge offset encoding, aligned and unaligned reads, writes at max store-block size, page-crossing write rejection, absent BAR rejection, kmem cache creation/destruction, core registration failure unwind, and probe/remove on IBM ISM device ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Kconfig

## Purpose

This Kconfig file enables the MLX5 VFIO PCI variant driver, primarily for migration support on Mellanox/NVIDIA MLX5 devices.

## Important APIs, Types, and Functions

`MLX5_VFIO_PCI` is a tristate option depending on `MLX5_CORE`, selecting `VFIO_PCI_CORE` and `IOMMUFD_DRIVER`.

## Control Flow

When selected, the mlx5 VFIO PCI variant is built from the mlx5 subdirectory and can provide device-specific migration behavior using VFIO PCI core.

## State and Persistence Behavior

Only build-time configuration state is represented.

## Dependencies and Integration Points

It integrates MLX5 core support, VFIO PCI core, and IOMMUFD driver support.

## Risks and Edge Cases

The variant depends on MLX5 core APIs and IOMMUFD infrastructure, so mismatched dependencies would produce link or runtime feature issues.

## Test Signals

Build with `MLX5_CORE` and `MLX5_VFIO_PCI` enabled as module and built-in, and verify `IOMMUFD_DRIVER` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Makefile

## Purpose

This Makefile builds the MLX5 VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_MLX5_VFIO_PCI) += mlx5-vfio-pci.o` enables the aggregate object, and `mlx5-vfio-pci-y := main.o cmd.o` links the main driver and command helpers.

## Control Flow

Kbuild compiles and links the MLX5 VFIO PCI module when its Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The Makefile maps MLX5 VFIO PCI Kconfig to the implementation objects and assumes those files provide the command and main-driver pieces.

## Risks and Edge Cases

Object-list drift between main and command helper files would break migration command support or symbol resolution.

## Test Signals

Build `CONFIG_MLX5_VFIO_PCI=y` and `m` and verify both `main.o` and `cmd.o` are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Makefile -->
