# Group Research: group_1651_qemu_sources_virtualization_qemu_hw_virtio_virtio_hmp_cmds_c_source_cbbfa0154d8a

Scope: `Docs/research_subset_a.md` only. Files read completely: all 14 listed QEMU virtio source/header files under `sources/virtualization/qemu/hw/virtio`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-hmp-cmds.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-hmp-cmds.c

Implements human monitor protocol (HMP) commands for inspecting virtio devices by formatting the QAPI `x-query-virtio*` results into monitor text.

Key entry points:
- `hmp_virtio_query()` lists all virtio devices returned by `qmp_x_query_virtio()`, showing QOM path and device name.
- `hmp_virtio_status()` prints device identity, lifecycle flags, queue counts, ISR/endianness, status bits, guest/host/backend feature sets, and optional vhost state.
- `hmp_vhost_queue_status()` prints vhost vring kick/call fds and descriptor/avail/used addresses, physical addresses, and sizes for one queue.
- `hmp_virtio_queue_status()` prints QEMU virtqueue state: queue index, inuse count, used index, notification state, optional last/shadow avail indices, and vring layout.
- `hmp_virtio_queue_element()` prints one queue element, including descriptor address/length/flags plus avail and used entries.

Formatting helpers:
- `hmp_virtio_dump_protocols()` prints known vhost protocol feature names and an optional unknown bitmask.
- `hmp_virtio_dump_status()` prints decoded virtio status names and optional unknown status bits.
- `hmp_virtio_dump_features()` prints transport, device, and unknown feature bitmaps, including the high/low 128-bit unknown-device-feature display.

Core mechanics:
- The file is intentionally presentation-only. It delegates discovery and state extraction to QAPI commands in `qapi/qapi-commands-virtio.h`.
- Each HMP command first calls the corresponding QMP query function, handles `Error`, then prints selected fields with `monitor_printf()`.
- Returned QAPI objects are released with their generated `qapi_free_*()` destructors.
- Optional QAPI fields such as `has_last_avail_idx`, `has_shadow_avail_idx`, `has_unknown_*`, and `vhost_dev` are checked before printing.

Important invariants:
- The HMP `path` and `queue` arguments are passed unchanged to QMP query functions; validation is expected in the QMP/backend query layer.
- Queue element lookup uses `index != -1` as the QAPI "index provided" flag.
- HMP output mirrors QAPI schema fields and has no independent synchronization around virtio state.

Filesystem/block relevance:
- This file is not a data path. It is operational inspection tooling for virtio devices, including queues used by virtio block, virtio-fs-related transports, and other virtual I/O devices.

Notable risks:
- Output can become stale immediately because it snapshots live device state without locking in this HMP layer.
- Formatting depends on QAPI structure stability; schema changes require corresponding HMP updates.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-hmp-cmds.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-input-host-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-input-host-pci.c

Provides the PCI wrapper type for the host-backed virtio input device.

Key entry points:
- `virtio_host_initfn()` embeds and initializes a `VirtIOInputHost` virtio device inside the PCI proxy object using `virtio_instance_init_common()`.
- `virtio_input_host_pci_register()` registers the type through `virtio_pci_types_register()`.

Core mechanics:
- Defines `TYPE_VIRTIO_INPUT_HOST_PCI` as `virtio-input-host-pci`.
- `VirtIOInputHostPCI` extends `VirtIOPCIProxy` and contains a `VirtIOInputHost vdev`.
- The `VirtioPCIDeviceTypeInfo` parent is `TYPE_VIRTIO_INPUT_PCI`, so common virtio-input PCI behavior comes from `virtio-input-pci.c`.

Important invariants:
- The embedded virtio device type is `TYPE_VIRTIO_INPUT_HOST`.
- No class-specific PCI IDs or properties are added here; it inherits the input PCI base behavior.

Filesystem/block relevance:
- No filesystem or block path involvement. This is a small virtio PCI transport binding for input devices.

Notable risks:
- Misregistration would make `virtio-input-host-pci` unavailable or incorrectly inherit input PCI behavior, but the file has no runtime logic beyond type initialization.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-input-host-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-input-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-input-pci.c

Defines the common virtio-input PCI base type and concrete PCI wrappers for keyboard, mouse, tablet, and multitouch virtio input devices.

Key entry points:
- `virtio_input_pci_realize()` forces virtio 1.0 mode and realizes the embedded `VirtIOInput` device on the proxy bus.
- `virtio_input_pci_class_init()` installs the default `vectors=2` property, assigns the realize hook, marks the device as input-category, and sets PCI class `PCI_CLASS_INPUT_OTHER`.
- HID-specific class initializers set keyboard and mouse PCI subclass IDs.
- `virtio_keyboard_initfn()`, `virtio_mouse_initfn()`, `virtio_tablet_initfn()`, and `virtio_multitouch_initfn()` initialize embedded `VirtIOInputHID` devices with their concrete virtio input type.
- `virtio_pci_input_register()` registers abstract base types and concrete PCI device types.

Core mechanics:
- `TYPE_VIRTIO_INPUT_PCI` is abstract and extends `TYPE_VIRTIO_PCI`.
- `TYPE_VIRTIO_INPUT_HID_PCI` is an abstract HID PCI layer for concrete HID-like input devices.
- Concrete generic PCI names are `virtio-keyboard-pci`, `virtio-mouse-pci`, `virtio-tablet-pci`, and `virtio-multitouch-pci`.
- All concrete wrappers delegate actual input protocol behavior to the embedded virtio input core device.

Important invariants:
- Virtio-input PCI is always forced to virtio 1.0 mode.
- The default vector count is 2.
- The concrete wrapper's embedded `vdev` type must match the advertised generic PCI name.

Filesystem/block relevance:
- No filesystem or block behavior. This is a virtio PCI transport binding pattern used elsewhere in QEMU.

Notable risks:
- PCI class IDs affect guest driver matching and device categorization.
- The file depends on `virtio_instance_init_common()` to correctly bind wrapper lifetime to the embedded virtio device.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-input-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-iommu-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-iommu-pci.c

Provides the PCI wrapper for the virtio IOMMU device and enforces machine/PCI topology constraints before realizing the embedded IOMMU.

Key entry points:
- `virtio_iommu_pci_realize()` validates hotplug-handler support, validates configured reserved-region types, requires root-bus placement, links the embedded device to the primary PCI bus, forces virtio 1.0, and realizes the virtio IOMMU.
- `virtio_iommu_pci_class_init()` installs properties, marks the device non-hotpluggable, sets category/revision/class, and wires the realize hook.
- `virtio_iommu_pci_instance_init()` initializes the embedded `VirtIOIOMMU`.
- `virtio_iommu_pci_register()` registers the PCI wrapper type.

Core mechanics:
- `VirtIOIOMMUPCI` extends `VirtIOPCIProxy` and embeds `VirtIOIOMMU vdev`.
- Properties include `class` mapped to `VirtIOPCIProxy.class_code` and an array property `reserved-regions` stored in the embedded IOMMU.
- The wrapper sets the embedded IOMMU's `primary-bus` link to the PCI bus it is plugged into.

Important invariants:
- `virtio-iommu-pci` must be on a root PCI bus.
- Reserved-region property types must be `VIRTIO_IOMMU_RESV_MEM_T_RESERVED` or `VIRTIO_IOMMU_RESV_MEM_T_MSI`.
- The machine must provide a hotplug handler so IOMMU interactions with PCI hotplug can be coordinated.
- The PCI wrapper itself is not hotpluggable.

Filesystem/block relevance:
- Indirectly relevant to virtualized storage because assigned and emulated PCI devices can route DMA through this IOMMU. It does not implement block I/O itself.

Notable risks:
- Incorrect placement or missing machine hotplug support is rejected at realize time.
- Reserved-region validation is done before the embedded device is realized, preventing unsupported region types from reaching the IOMMU core.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-iommu-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-iommu.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-iommu.c

Implements QEMU's virtio IOMMU device: domain/endpoint management, IOVA mappings, reserved-region reporting, PCI bus address-space integration, fault reporting, migration state, and IOMMU memory-region translation.

Key entry points:
- `virtio_iommu_device_realize()` initializes the virtio device, request/event queues, config ranges, feature bits, mutexes, PCI IOMMU ops, machine-done notifier, and reset hook.
- `virtio_iommu_handle_command()` consumes virtqueue requests and dispatches attach, detach, map, unmap, and probe commands.
- `virtio_iommu_translate()` implements `IOMMUMemoryRegionClass.translate` for DMA translation and fault reporting.
- `virtio_iommu_find_add_as()` implements PCI IOMMU address-space creation and returns per-device address spaces.
- `virtio_iommu_set_iommu_device()` and `virtio_iommu_unset_iommu_device()` integrate host IOMMU devices, host IOVA restrictions, and page-size masks.
- `virtio_iommu_get_config()` / `virtio_iommu_set_config()` expose and update virtio-iommu config, especially runtime bypass mode.
- `iommu_post_load()` reconstructs endpoint links and address-space mode after migration.

Domain and endpoint model:
- `VirtIOIOMMUDomain` stores a domain id, bypass flag, interval-keyed mapping tree, and attached endpoint list.
- `VirtIOIOMMUEndpoint` stores an endpoint id, current domain pointer, associated `IOMMUMemoryRegion`, and list linkage.
- Domains are keyed by integer id in `s->domains`; endpoints are keyed by SID in `s->endpoints`.
- Mapping keys are non-overlapping `VirtIOIOMMUInterval` ranges compared by overlap-aware `interval_cmp()`, so overlapping maps are rejected by lookup before insertion.

Command behavior:
- Attach validates flags, resolves endpoint, detaches from any previous domain, obtains or creates a compatible domain, switches the endpoint address space, and replays existing mappings to IOMMU notifiers.
- Detach validates endpoint/domain association, unmaps notifier state, removes empty domains, and deletes the endpoint record.
- Map validates flags, domain existence, non-bypass domain state, and non-overlap, then inserts a physical mapping and notifies attached endpoints.
- Unmap removes only mappings fully covered by the requested interval; partial overlap returns `VIRTIO_IOMMU_S_RANGE`.
- Probe fills endpoint reserved-memory properties into a fixed `VIOMMU_PROBE_SIZE` buffer.

PCI/IOMMU integration:
- `virtio_iommu_find_add_as()` lazily creates per-BDF `IOMMUDevice` objects with a root memory region containing both bypass and IOMMU subregions.
- `virtio_iommu_switch_address_space()` enables exactly one of bypass or remapping memory regions according to global bypass, endpoint attachment, and domain bypass state.
- `virtio_iommu_switch_address_space_all()` reapplies that choice across all known PCI devices.
- Host IOMMU devices can contribute allowed IOVA ranges; the code stores their inverse as reserved regions and rebuilds the endpoint reserved-region list together with machine-provided reserved regions.

Translation and notification:
- `virtio_iommu_translate()` starts with no permission, checks bypass, endpoint existence, reserved regions, domain attachment, domain bypass, mapping existence, and read/write permissions.
- MSI reserved regions are passed through; reserved memory regions fault.
- Missing endpoints/domains/mappings and permission failures report faults on the event queue via `virtio_iommu_report_fault()`.
- Map/unmap notifier events are split into aligned power-of-two chunks by `virtio_iommu_notify_map_unmap()`.
- Device IOTLB unmap notifier flags are explicitly unsupported.

Configuration and lifecycle:
- Realize validates `aw-bits` in `[32,64]`, derives input range, page size mask from granule mode, domain range, probe size, and supported feature bits.
- `boot-bypass` initializes `config.bypass`; system reset restores it, while ordinary device reset rebuilds domains/endpoints during the reset exit phase.
- Machine init completion freezes the selected granule so later host IOMMU page-size restrictions cannot invalidate it.
- Unrealize destroys hash tables/trees, mutex, virtqueues, reset hooks, and virtio state.

Migration:
- VMState migrates domains, mappings, endpoint lists, domain bypass state, and `config.bypass`.
- `reconstruct_endpoints()` reconnects loaded endpoint records to live IOMMU memory regions and repopulates `s->endpoints`.
- Post-load re-switches all address spaces because enabled memory regions are derived runtime state.

Important invariants:
- A domain id cannot be reused with a different bypass flag.
- Bypass domains cannot accept map/unmap requests.
- Mappings are stored as whole intervals; unmap does not split partially covered mappings.
- Address-space switching must happen after attach/detach and after bypass config changes.
- Host page-size restrictions can only narrow the page-size mask before the granule is frozen.
- Command request and response buffers are size-checked before use; malformed head/tail sizes trigger virtio device errors.

Filesystem/block relevance:
- This file controls DMA address translation for virtio and PCI devices, including virtual storage devices when routed through a virtio IOMMU. Correct mapping and fault behavior is critical for safe virtual block and filesystem I/O isolation.

Notable risks:
- The unmap implementation rejects partial overlaps rather than splitting mappings, which guest drivers must account for.
- Event queue exhaustion drops fault reporting after logging once.
- Host IOMMU alias handling is deliberately limited; pre-existing host reserved ranges cause aliased BDF rejection.
- `virtio_iommu_translate()` uses fault side effects during DMA translation, so missing event buffers can hide repeated guest faults after the first report.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-iommu.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-md-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-md-pci.c

Defines the abstract PCI base class for virtio-based memory devices and centralizes memory-device hotplug/unplug coordination.

Key entry points:
- `virtio_md_pci_pre_plug()` validates the generic `MemoryDeviceState` and then calls the bus hotplug handler's pre-plug hook when present.
- `virtio_md_pci_plug()` plugs the memory device first, then calls the bus hotplug handler and rolls memory-device state back if bus plug fails.
- `virtio_md_pci_unplug_request()` validates class support, bus support, and device-specific unplug preconditions, then forwards an async unplug request or performs synchronous unplug/unparent.
- `virtio_md_pci_unplug()` unplugs the memory device while still realized, then calls bus unplug handling, with best-effort recovery on failure.
- Type registration creates abstract `TYPE_VIRTIO_MD_PCI` as a `TYPE_VIRTIO_PCI` subclass implementing `TYPE_MEMORY_DEVICE`.

Core mechanics:
- `VirtIOMDPCIClass` can provide `unplug_request_check`; devices lacking it are considered non-unpluggable.
- The code distinguishes bus hotplug handlers from device hotplug state to enforce plug/unplug ordering.
- Memory-device state changes are coordinated with machine-level `memory_device_*()` helpers and bus-level `hotplug_handler_*()` hooks.

Important invariants:
- Hotplugged virtio memory devices require a bus hotplug handler.
- Plug order is memory-device first, bus handler second; unplug order is memory-device first while the device is still realized, then bus handler.
- If bus plug fails, the memory-device plug is undone.
- If bus unplug unexpectedly fails, the code tries to re-plug memory-device state.

Filesystem/block relevance:
- No direct filesystem or block behavior. It supports memory hotplug infrastructure used by virtio memory devices.

Notable risks:
- Unplug failure recovery is best effort and comments mark it as unexpected.
- Without a bus hotplug handler, hotunplug is rejected and unexpected direct unplug falls back to warning plus `qdev_unrealize()`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-md-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-md-stubs.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-md-stubs.c

Provides stub implementations for virtio memory-device PCI hotplug helpers when virtio-based memory devices are not supported in the build.

Key entry points:
- `virtio_md_pci_pre_plug()`
- `virtio_md_pci_plug()`
- `virtio_md_pci_unplug_request()`
- `virtio_md_pci_unplug()`

Core mechanics:
- Every function simply sets an error: `virtio based memory devices not supported`.
- Signatures match the real implementations in `virtio-md-pci.c`, allowing callers to link even when support is disabled.

Important invariants:
- These stubs do not mutate memory-device, bus, or hotplug state.
- Callers must treat the returned error as a hard unsupported-device condition.

Filesystem/block relevance:
- No filesystem or block behavior.

Notable risks:
- Build configurations using this file cannot hotplug or manage virtio-based memory devices; all such operations fail uniformly.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-md-stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.c

Implements the PCI wrapper and `MemoryDeviceClass` integration for the virtio-mem device.

Key entry points:
- `virtio_mem_pci_realize()` defaults `nvectors` to 2 when unspecified, forces virtio 1.0, and realizes the embedded `VirtIOMEM`.
- `virtio_mem_pci_get_addr()` / `virtio_mem_pci_set_addr()` proxy the memory-device address property to the embedded virtio-mem object.
- `virtio_mem_pci_get_memory_region()`, `virtio_mem_pci_decide_memslots()`, and `virtio_mem_pci_get_memslots()` delegate memory-region and memslot decisions to the embedded virtio-mem class.
- `virtio_mem_pci_fill_device_info()` allocates and fills QAPI `VirtioMEMDeviceInfo`, including the PCI device id when present.
- `virtio_mem_pci_size_change_notify()` emits `MEMORY_DEVICE_SIZE_CHANGE` QAPI events when the embedded plugged size changes.
- `virtio_mem_pci_unplug_request_check()` delegates unplug precondition checks to the embedded virtio-mem class.
- `virtio_mem_pci_get_requested_size()` / `virtio_mem_pci_set_requested_size()` expose requested-size as a wrapper property, blocking changes once pending unplug deletion is in progress.

Core mechanics:
- `VirtIOMEMPCI` extends the abstract `VirtIOMDPCI` base and embeds `VirtIOMEM vdev`.
- The wrapper implements the `MemoryDeviceClass` methods expected by machine hotplug code.
- Class properties include `ioeventfd` and `vectors`, with `vectors` defaulting to `DEV_NVECTORS_UNSPECIFIED`.
- Instance init registers a size-change notifier with the embedded virtio-mem device and adds wrapper aliases for block-size and current-size properties.

Important invariants:
- The PCI wrapper is registered with base type `virtio-mem-pci-base` and generic name `virtio-mem-pci`.
- The requested-size property cannot be changed after unplug request processing has marked the device pending deletion.
- The notifier is not removed explicitly because the wrapper and embedded virtio device are expected to disappear together.
- PCI class/revision are set to miscellaneous virtio PCI values.

Filesystem/block relevance:
- No direct filesystem or block logic. Virtio-mem affects guest physical memory availability, which can indirectly affect page cache and filesystem workloads.

Notable risks:
- The wrapper relies on the embedded virtio-mem class for most validation; wrapper property aliasing must remain consistent with core property names.
- Blocking requested-size changes during pending unplug avoids memory being re-hotplugged before device deletion completes.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.h -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.h

Declares the PCI wrapper state for virtio-mem.

Key contents:
- Defines `TYPE_VIRTIO_MEM_PCI` as `virtio-mem-pci-base`.
- Declares the `VirtIOMEMPCI` instance checker.
- Defines `struct VirtIOMEMPCI` with:
  - `VirtIOMDPCI parent_obj`
  - embedded `VirtIOMEM vdev`
  - `Notifier size_change_notifier`

Core mechanics:
- The header connects the generic virtio memory-device PCI base (`virtio-md-pci.h`) with the concrete virtio-mem device (`virtio-mem.h`).
- It is included by `virtio-mem-pci.c` to implement the wrapper methods.

Important invariants:
- `VirtIOMEMPCI` is a `VirtIOMDPCI` subclass, so it participates in the memory-device hotplug flow defined by the abstract base.
- The embedded virtio-mem object and notifier are owned by the PCI wrapper instance.

Filesystem/block relevance:
- No filesystem or block behavior.

Notable risks:
- Structure layout must match QOM type registration in `virtio-mem-pci.c`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem.c

Implements the virtio-mem device: guest-driven memory plug/unplug requests, block bitmap tracking, RAM discard management, dynamic memslot activation, migration state, device properties, and reset behavior.

Key entry points:
- `virtio_mem_device_realize()` validates the memory backend and properties, sets up discard management, initializes the block bitmap, virtio device, request queue, optional dynamic memslots, RAM migration registration, early migration state, and reset helper object.
- `virtio_mem_handle_request()` consumes guest requests from the virtqueue and dispatches plug, unplug, unplug-all, and state queries.
- `virtio_mem_state_change_request()` validates guest ranges, requested-size policy, current block state, and then changes block state.
- `virtio_mem_set_block_state()` performs the actual plug/unplug operation, including migration-busy checks, RAM discard/preallocation, listener notifications, bitmap updates, and dynamic memslot activation/deactivation.
- `virtio_mem_get_config()` exposes block size, NUMA node, requested size, plugged size, base address, region size, and usable region size.
- `virtio_mem_get_features()` advertises ACPI PXM, unplugged-inaccessible, and persistent-suspend features when applicable.
- RamDiscardManager methods expose plug/discard state to other QEMU subsystems.

Memory model:
- The memory backend is divided into fixed-size blocks tracked by `vmem->bitmap`; set bits are plugged, clear bits are unplugged.
- `vmem->size` is the current plugged size and `vmem->requested_size` is the target the guest may plug up to.
- `usable_region_size` can exceed requested size by an architecture-specific extent to help guests add full memory sections while only plugging part of them.
- Block size defaults are chosen from backend page size and transparent huge page expectations, with a hard minimum of 1 MiB.

Guest request behavior:
- `VIRTIO_MEM_REQ_PLUG` plugs an aligned range only if all blocks are currently unplugged and the result does not exceed requested size.
- `VIRTIO_MEM_REQ_UNPLUG` unplugs an aligned range only if all blocks are currently plugged.
- `VIRTIO_MEM_REQ_UNPLUG_ALL` discards all RAM, clears the bitmap, resets plugged size, notifies listeners, and shrinks usable region when possible.
- `VIRTIO_MEM_REQ_STATE` returns plugged, unplugged, or mixed for a valid aligned range.
- Invalid protocol buffer sizes or unknown request types call `virtio_error()`.

RAM discard and listener integration:
- Unplug uses `ram_block_discard_range()` and then notifies registered `RamDiscardListener`s of discarded sections.
- Plug can preallocate backend memory, activates dynamic memslots before notifications, notifies listeners of populated sections, and rolls back on notifier/preallocation failure.
- Registered listeners receive replay of already plugged sections; unregistering discards the listener's whole section if any memory is plugged.
- `is_populated`, `replay_populated`, and `replay_discarded` answer state by intersecting requested memory sections with the virtio-mem bitmap.

Dynamic memslots:
- With `dynamic-memslots=on`, the device creates an intermediate container memory region and per-slot aliases into the backend.
- Memslots are added only when needed for plugged memory and removed when fully unplugged.
- Memslot size is chosen before realize based on the machine limit, backend size, block size, and a minimum target of 1 GiB except for the last slot.
- Dynamic memslots require `unplugged-inaccessible=on`.

Migration:
- Early migration state can transfer immutable geometry and the bitmap before RAM migration starts.
- Sanity checks reject migration if address, backend region size, block size, or NUMA node changed.
- Post-load activates memslots for plugged ranges, replays populate notifications, discards unplugged memory, and handles preallocation before RAM migration when early migration is enabled.
- Migration-busy checks block plug/unplug while migration is running or incoming postcopy is active.
- Shared RAM ignored by QEMU migration skips discard/preallocation post-load handling.

Realize-time validation:
- Requires a memory backend that is unmapped, RAM, non-ROM, and backed by a RAMBlock.
- Rejects memory backends with their own preallocation enabled; virtio-mem has its own `prealloc` property.
- Validates NUMA node, rejects mlock, validates block/requested/address/backend-size alignment, and requires coordinated RAM discard.
- Initializes all backend memory as discarded except during incoming migration.
- Chooses `unplugged-inaccessible` automatically for legacy x86 guests based on whether the backend has a reliable shared zero page; non-legacy targets force it on.

Properties and QOM interfaces:
- Properties include address, NUMA node, prealloc, memory backend link, early migration, dynamic memslots, and legacy-target `unplugged-inaccessible`.
- Runtime properties expose current size, requested size, and block size.
- Requested size can change after realize if aligned and not larger than backend size; changes resize the usable region and trigger virtio config notification.
- Implements `TYPE_RAM_DISCARD_MANAGER`.

Reset and unplug:
- A dedicated `VirtioMemSystemReset` resettable object handles system reset, not simple device reset.
- Normal system resets attempt to unplug all memory; wakeup resets preserve plugged memory.
- Device unplug is allowed only when unplugged-inaccessible is on, current plugged size is zero, and requested size is zero.

Important invariants:
- Guest ranges must be block-size aligned, nonzero, non-overflowing, and within usable region.
- Plug/unplug operations are rejected while migration is busy.
- Bitmap state is updated after memory discard/populate operations and listener notifications succeed.
- `vmem->size` and size-change notifiers are updated only after successful state changes.
- Dynamic memslot deactivation occurs after bitmap state reflects unplugged blocks.
- Realize sets the memory region's discard manager before the region is exposed to address spaces.

Filesystem/block relevance:
- No block-device protocol is implemented, but this file controls guest RAM availability and discard/populate state. That can materially affect filesystem cache contents, memory hotplug behavior, and migration of workloads using virtual storage.

Notable risks:
- Plug can fail due to preallocation or listener errors and must discard any memory that may have been populated.
- Unplug depends on backend discard support; failures are reported as busy.
- Legacy `unplugged-inaccessible=off` is tolerated only for compatibility and blocks device unplug.
- Migration ordering is delicate because unplugged memory must not be migrated with stale or accidentally populated content.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mem.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mmio.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-mmio.c

Implements the virtio MMIO transport device and bus, including legacy and modern MMIO registers, queue setup, feature negotiation, interrupts, ioeventfd integration, migration state, and sysbus realization.

Key entry points:
- `virtio_mmio_read()` handles guest reads from virtio-mmio registers and device configuration space.
- `virtio_mmio_write()` handles guest writes for feature selection, queue configuration, notifications, interrupt ack, status changes, and config writes.
- `virtio_mmio_realizefn()` creates the virtio-mmio bus, IRQ, and MMIO region in legacy or modern endianness mode.
- `virtio_mmio_update_irq()` drives the sysbus IRQ based on the virtio device ISR.
- `virtio_mmio_reset()` and `virtio_mmio_soft_reset()` reset transport state and virtio bus/device state.
- `virtio_mmio_set_guest_notifiers()` configures event notifiers for virtqueues and config changes.
- `virtio_mmio_bus_class_init()` wires the virtio bus callbacks for notify, migration config, ioeventfd, guest notifiers, pre-plug, VM state changes, and device path.

Register behavior:
- With no backend device, reads return valid magic/version/vendor and zero for most other registers so guest probing sees no device id; writes are ignored.
- Device config space begins at `VIRTIO_MMIO_CONFIG` and uses legacy or modern config accessors depending on `force-legacy`.
- Non-config register accesses must be 32-bit; wrong-size accesses are logged as guest errors.
- Legacy mode supports `QUEUE_PFN`, `QUEUE_ALIGN`, and `GUEST_PAGE_SIZE`.
- Modern mode supports 64-bit split descriptor/avail/used addresses, queue-ready state, config generation, and 64-bit feature negotiation.

Queue and feature mechanics:
- `DEVICE_FEATURES_SEL` and `DRIVER_FEATURES_SEL` choose low/high feature words.
- Modern driver features are staged in `proxy->guest_features[]` and committed when `FEATURES_OK` is written to status.
- Queue size is written to QEMU's virtqueue and cached in `proxy->vqs[]` for modern mode.
- Modern `QUEUE_READY` installs cached queue addresses and enables the queue.
- `QUEUE_NOTIFY` optionally stores notification data shadow avail index when `VIRTIO_F_NOTIFICATION_DATA` is negotiated, then calls `virtio_queue_notify()`.

Interrupts and ioeventfd:
- `INTERRUPT_STATUS` reads the virtio ISR; `INTERRUPT_ACK` clears bits and updates IRQ.
- `virtio_mmio_update_irq()` asserts the IRQ when ISR is nonzero.
- `ioeventfd` registers eventfds on `VIRTIO_MMIO_QUEUE_NOTIFY`, unless record/replay mode disables fd-based ioevents.
- VM running/stopped callbacks start and stop ioeventfd.

Migration:
- Legacy transport config migration saves feature selectors and guest page shift.
- Modern extra-state subsection saves staged guest feature words and all per-queue modern state: queue size, enabled flag, descriptor/avail/used address words.
- Extra state is migrated only for non-legacy devices.

Type and bus behavior:
- `TYPE_VIRTIO_MMIO` is a sysbus device with properties `force-legacy` and `ioeventfd`.
- `TYPE_VIRTIO_MMIO_BUS` allows one child device and reports a path derived from the MMIO address.
- `virtio_mmio_pre_plugged()` adds `VIRTIO_F_VERSION_1` for non-legacy backends.
- The bus advertises variable vring alignment.

Important invariants:
- Legacy-only and modern-only registers are rejected with guest-error logs when accessed in the wrong mode.
- Status writes stop ioeventfd before clearing `DRIVER_OK` and restart it after setting `DRIVER_OK`.
- Writing status zero performs a transport soft reset.
- Guest notifier setup rolls back already assigned notifiers if a later assignment fails.
- Modern queue enabled state is transport state and must be migrated.

Filesystem/block relevance:
- This is a transport used by MMIO virtio devices, including storage-related virtio devices on non-PCI machines. Correct queue/register behavior is required for virtual block and filesystem transports.

Notable risks:
- Shared memory selector registers are effectively unimplemented and length reads return all ones to indicate no region.
- The code logs many guest misuse cases but often continues by returning zero or ignoring writes.
- KVM irqfd is explicitly not used here for guest notifiers.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-mmio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-net-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-net-pci.c

Provides the PCI wrapper for virtio-net.

Key entry points:
- `virtio_net_pci_realize()` chooses a default vector count from queue count, config interrupt, and control virtqueue, sets the netclient name, and realizes the embedded `VirtIONet`.
- `virtio_net_pci_class_init()` configures PCI ROM/vendor/device/revision/class metadata, SR-IOV VF user-creatable support, category, properties, and realize hook.
- `virtio_net_pci_instance_init()` initializes the embedded virtio-net device and aliases the wrapper `bootindex` property to the embedded device.
- `virtio_net_pci_register()` registers base, transitional, and non-transitional virtio-net PCI types.

Core mechanics:
- `VirtIONetPCI` extends `VirtIOPCIProxy` and embeds `VirtIONet vdev`.
- Default `vectors` is unspecified until realize; realize computes `2 * max(queue_pairs, 1) + 1 config + 1 control`.
- The PCI ROM is `efi-virtio.rom`; vendor/device are Red Hat/Qumranet virtio-net identifiers.
- Properties include `ioeventfd` and `vectors`.

Important invariants:
- Netclient naming uses the PCI wrapper device id and QOM type name.
- Transitional and non-transitional variants are registered by `virtio_pci_types_register()`.
- `bootindex` is owned by the embedded net device but exposed on the PCI wrapper.

Filesystem/block relevance:
- No filesystem or block logic. It is a network virtio PCI wrapper and a reference pattern for virtio PCI binding.

Notable risks:
- Incorrect vector calculation would affect multiqueue interrupt layout.
- Guest driver matching depends on PCI class/vendor/device and transitional type registration.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-net-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-nsm-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-nsm-pci.c

Provides the PCI wrapper for the AWS Nitro Secure Module virtio device.

Key entry points:
- `virtio_nsm_pci_realize()` forces virtio 1.0 and realizes the embedded `VirtIONSM` on the proxy bus.
- `virtio_nsm_pci_class_init()` installs the realize hook and marks the device as miscellaneous.
- `virtio_nsm_initfn()` initializes the embedded `TYPE_VIRTIO_NSM` device.
- `virtio_nsm_pci_register()` registers the PCI wrapper type.

Core mechanics:
- `VirtIONsmPCI` extends `VirtIOPCIProxy` and embeds `VirtIONSM vdev`.
- The registered base type is `virtio-nsm-pci-base`, with generic name `virtio-nsm-pci`.
- No additional PCI properties are defined in this file.

Important invariants:
- The wrapper always forces virtio 1.0 mode.
- Realize returns immediately if embedded device realization fails.

Filesystem/block relevance:
- No filesystem or block logic. It exposes a security/attestation device over virtio PCI.

Notable risks:
- The file is intentionally thin; device behavior and protocol validation live in `virtio-nsm.c`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-nsm-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-nsm.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-nsm.c

Implements a virtio AWS Nitro Secure Module (NSM) device with CBOR request parsing, CBOR responses, PCR state, random data, attestation document construction, virtqueue handling, migration of PCRs, and the `module-id` property.

Key entry points:
- `virtio_nsm_device_realize()` initializes default NSM identity/version/digest callbacks, creates the virtio device with `VIRTIO_ID_NITRO_SEC_MOD`, and adds a two-entry virtqueue.
- `handle_input()` consumes one request buffer and one response buffer from the virtqueue, validates buffer structure, builds the response, pushes both elements, and notifies the guest.
- `get_nsm_request_response()` enforces maximum request size, identifies the CBOR command, and calls the command handler.
- Command handlers implement `GetRandom`, `DescribeNSM`, `DescribePCR`, `ExtendPCR`, `LockPCR`, `LockPCRs`, and `Attestation`.
- `extend_pcr()` updates a PCR using SHA-384 over old PCR data concatenated with caller data.

Protocol dispatch:
- `get_nsm_request_cmd()` accepts two request forms: a root CBOR string for simple commands and a one-entry root map whose key is the command string for parameterized commands.
- The static `nsm_cmds[]` table maps command name, root type, and response function.
- Requests larger than `NSM_REQUEST_MAX_SIZE` return `InputTooLarge`.
- Unknown or malformed commands return `InvalidOperation`.

Virtqueue behavior:
- The device expects the first popped element to contain a nonempty outgoing request.
- It expects a second popped element containing an input response buffer exactly `NSM_RESPONSE_BUF_SIZE` bytes long.
- Request data is copied into a temporary contiguous buffer, and the serialized response is copied back to the input buffer.
- On success, the request element is pushed with used length 0 and the response element with the serialized response length.
- Structural virtqueue violations call `virtio_error()` and detach any popped elements.

Command behavior:
- `GetRandom` returns 256 bytes from `qemu_guest_getrandom_nofail()`.
- `DescribeNSM` returns digest string, max PCR count, module id, locked PCR indices, and version 1.0.0.
- `DescribePCR` parses an 8-bit `index`, validates it against `max_pcrs`, and returns PCR data and lock state.
- `ExtendPCR` parses 8-bit `index` and string/bytes `data`, rejects invalid or locked PCRs, extends the PCR, and returns the new digest.
- `LockPCR` parses an 8-bit `index`, rejects invalid or already locked PCRs, marks it locked, and returns a success string.
- `LockPCRs` parses an 8-bit `range`, validates it does not exceed `max_pcrs`, locks PCR indices below that range, and returns a success string.
- `Attestation` parses optional `public_key`, `user_data`, and `nonce` as byte/string/null properties and returns an attestation document.

Attestation document:
- The response wraps a serialized COSE Sign1-like array in a CBOR `Attestation.document` byte string.
- Protected header encodes algorithm `-1`; comments note the document is not actually signed.
- Unprotected header is an empty map.
- Payload includes module id, digest, millisecond timestamp, locked PCR map, placeholder certificate, placeholder CA bundle, public key, user data, and nonce.
- Signature is a 64-byte zero byte string.

CBOR and error handling:
- `error_response()` serializes a one-entry CBOR map containing an error string.
- Parsers use libcbor type checks and exact-width checks for integer fields expected as `CBOR_INT_8`.
- String and byte-string inputs are both accepted for PCR extend data and attestation properties.
- Serialization failure due to response size returns `InputTooLarge` or `BufferTooSmall` depending on command context.

State and migration:
- `VirtIONSM` stores `NSM_MAX_PCRS` PCR entries with lock flag and SHA-384-sized data.
- VMState migrates the PCR array via `vmstate_pcr_info_entry`.
- The top-level virtio device state is migrated through `VMSTATE_VIRTIO_DEVICE`.
- `module-id` is a QOM string property; if unset, realize uses a default module id string.

Important invariants:
- PCR indices must be below `vnsm->max_pcrs`.
- Locked PCRs cannot be extended or locked again through `LockPCR`.
- Request size is capped before parsers copy string/bytes payloads into fixed-size request structs.
- Response buffer size is fixed and enforced by virtqueue handling.
- The implementation models attestation structure but uses placeholder certificate/CA/signature data.

Filesystem/block relevance:
- No filesystem or block behavior. It is a virtio security device that may be present in virtual machines running filesystems or storage workloads.

Notable risks:
- Attestation is structurally generated but not cryptographically signed; the code explicitly uses zero placeholder signature and certificate data.
- Some parser paths ignore unknown map keys, so malformed requests with extra keys can still be accepted if required keys are valid.
- `handle_input()` requires request and response as separate virtqueue elements in sequence, which is stricter than many virtio device request layouts.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-nsm.c -->