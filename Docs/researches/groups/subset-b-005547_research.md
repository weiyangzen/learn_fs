# Group Research: subset-b-005547

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_config.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_config.c

This file implements VFIO PCI configuration-space virtualization. Its purpose is to expose enough PCI config space to userspace device models while trapping or virtualizing fields that the host kernel must own: BAR registers, capability links, power management, INTx disable, MSI enable/addresses, FLR triggers, and selected error/power capability bits.

Important types and APIs are `struct perm_bits`, shared `cap_perms[]` and `ecap_perms[]`, per-device `vdev->pci_config_map`, `vdev->vconfig`, `vdev->rbar[]`, and exported entry points `vfio_pci_init_perm_bits()`, `vfio_pci_uninit_perm_bits()`, `vfio_config_init()`, `vfio_config_free()`, `vfio_pci_config_rw_single()`, `vfio_pci_config_rw()`, and `vfio_pci_core_range_intersect_range()`. The permission model separates virtualized bits from writable bits. Default handlers mix hardware reads/writes with `vconfig`, while raw, direct, and pure virtual handlers cover unassigned config holes, read-only capability exposure, and synthetic registers.

Control flow starts at module init through shared permission table allocation. Per device, `vfio_config_init()` allocates the byte-granular capability map and virtual config image, snapshots base config and BARs, fixes VF vendor/device and INTx pin behavior, builds standard capability coverage with `vfio_cap_init()`, and builds extended capability coverage with `vfio_ecap_init()`. User reads and writes enter through `vfio_pci_config_rw()`, which splits accesses into dword-aligned chunks contained within one capability, resolves the right `perm_bits`, and invokes the read/write callback.

State is persistent for the lifetime of an open VFIO PCI device: virtual config bytes track emulated bits, `rbar[]` records real BARs for reset recovery, `bardirty` triggers BAR sizing emulation, `msi_perm` is allocated per device for variable MSI capability shape, and `extended_caps` records whether extended config space is meaningful. Power and memory transitions use `memory_lock`; writes that clear memory enable, enter D3, or trigger FLR revoke DMA-bufs and zap mappings through core helpers.

Dependencies and integration points include PCI config accessors, VFIO region offsets, `vfio_pci_intx_mask/unmask()`, `vfio_pci_set_power_state()`, DMA-buf revocation hooks, and the BAR/mmap logic in `vfio_pci_core.c` and `vfio_pci_rdwr.c`. Risks concentrate around malformed or overlapping capabilities, partial user accesses, hardware reset behind VFIO's back, incorrect memory-enable virtualization for VFs, and failure to keep config state coherent across power and reset paths. Test signals include config read/write fuzzing at unaligned offsets, BAR sizing probes, MSI/MSI-X enable sequencing, PM capability writes to D-states, PCIe/AF FLR writes, VF devices with bogus INTx pins, and devices with variable vendor/DVSEC capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_core.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_core.c

This is the central VFIO PCI core implementation. It owns device initialization, registration, open/close enablement, ioctl dispatch, region and IRQ enumeration, mmap setup, reset coordination, runtime power management, SR-IOV VF token policy, AER request/error eventfd delivery, and module lifetime.

Important APIs include exported `vfio_pci_core_init_dev()`, `vfio_pci_core_register_device()`, `vfio_pci_core_enable()`, `vfio_pci_core_finish_enable()`, `vfio_pci_core_disable()`, `vfio_pci_core_close_device()`, `vfio_pci_core_ioctl()`, `vfio_pci_core_ioctl_feature()`, `vfio_pci_core_read/write()`, `vfio_pci_core_mmap()`, `vfio_pci_core_request()`, `vfio_pci_core_match()`, `vfio_pci_core_sriov_configure()`, and reset/power helpers. Local types include dummy resources for sub-page BAR reservation, VF token state, hot-reset group data, and traversal helpers for bus/slot reset walks.

Open control flow resumes runtime PM, clears bus mastering, enables the PCI device, attempts function reset, saves PCI state, probes INTx quirks, opens zPCI hooks, initializes virtual config, discovers MSI-X table metadata, detects VGA, and eagerly maps BARs. Close reverses the process: exit runtime PM low-power mode, restore D0, stop DMA, disable IRQs and ioeventfds, release device-specific regions, free config, unmap BARs, restore saved PCI state, attempt reset, and release runtime PM. Ioctls are split across device info, region info, IRQ info, IRQ setup, reset, hot reset, and ioeventfd. Reads/writes dispatch by VFIO region index, wrapping accesses with runtime PM get/put.

State includes module parameters (`nointxmask`, `disable_vga`, `disable_idle_d3`), per-device locks (`igate`, `irqlock`, `memory_lock`, `ioeventfds_lock`), BAR maps, dummy resources, region arrays, saved PCI state, runtime PM flags and wake eventfd, SR-IOV PF/VF token references, DMA-buf and ioeventfd lists, and xarray IRQ contexts. Persistence is kernel object lifetime only; userspace-visible state is carried through VFIO file descriptors and PCI config emulation.

Dependencies and integration points span VFIO core/group/cdev APIs, iommufd, PCI reset/runtime PM/SR-IOV/VGA/AtomicOps, zPCI, EEH, DMA-buf cleanup, interrupt helpers, config virtualization, BAR I/O, and device-specific wrappers such as virtio/xe. Risks include deadlocks around dev_set and memory locks, incomplete hot-reset ownership validation, stale BAR mmaps after memory disable/reset, runtime PM transitions racing with user config writes, SR-IOV PF/VF trust leakage, and mmap faults when memory decode or PM state changes. Test signals include open/close stress, hot reset with mixed owned/unowned devices, runtime low-power feature entry/exit with wake eventfds, mmap fault SIGBUS behavior, SR-IOV token matching, VF driver override capture, and ioeventfd teardown during close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_dmabuf.c

This file implements the optional VFIO PCI DMA-buf feature for exporting PCI BAR physical ranges as peer-to-peer DMA-bufs. It is primarily an interconnect path between VFIO PCI and iommufd/P2PDMA users that need a file descriptor representing device memory.

The central type is `struct vfio_pci_dma_buf`, which stores the exported `dma_buf`, owning `vfio_pci_core_device`, BAR physical vector, P2PDMA provider, range count, kref/completion used to drain active mappings, list membership, and revoked state. Important functions are DMA-buf ops `attach`, `map_dma_buf`, `unmap_dma_buf`, `release`, exported helpers `vfio_pci_dma_buf_iommufd_map()`, `vfio_pci_core_fill_phys_vec()`, `vfio_pci_core_get_dmabuf_phys()`, the uAPI feature handler `vfio_pci_core_feature_dma_buf()`, and lifecycle hooks `vfio_pci_dma_buf_move()` and `vfio_pci_dma_buf_cleanup()`.

Control flow for feature GET validates the VFIO feature request, copies range metadata from userspace, requires a valid BAR map, checks page alignment and overflow, asks device PCI ops for BAR physical vectors, pins the VFIO device registration, exports the DMA-buf, links it under `vdev->dmabufs`, and returns a DMA-buf fd. Attachment requires peer-to-peer and revocable attachments. Mapping converts the physical vector to an sg table while holding the DMA reservation lock and increments the kref; unmap frees the sg table and drops the kref.

State is tied to file lifetime and `vdev->memory_lock`. `revoked` is toggled when memory decode, power state, reset, or cleanup makes BAR access invalid. `vfio_pci_dma_buf_move()` invalidates mappings, waits for DMA reservation usage to drain, and uses the kref/completion to ensure active mappings are gone on revoke. Cleanup detaches live DMA-bufs from the device and drops registration references.

Dependencies include Linux DMA-buf, DMA reservation, P2PDMA provider APIs, VFIO feature validation, BAR setup in `vfio_pci_rdwr.c`, and memory decode helpers in config/core. Risks include exposing invalid physical ranges, overflow or non-page-aligned user ranges, stale mappings during reset or D3, active-file races during cleanup, and the temporary private iommufd interconnect only accepting one physical range. Test signals include invalid range fuzzing, mapping after revoke returning `-ENODEV`, cleanup with active DMA-buf fds, memory-enable toggles, reset and runtime PM transitions, and iommufd single-range physical extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_igd.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_igd.c

This file adds Intel integrated graphics device-specific VFIO regions. It exposes a read-only IGD OpRegion/VBT region and read-only host/LPC bridge config regions needed by guest graphics stacks, while virtualizing the OpRegion PCI config pointer to prevent userspace from modifying host firmware addresses.

Important types and functions include `struct igd_opregion_vbt`, `vfio_pci_igd_rw()`, `vfio_pci_igd_release()`, `vfio_pci_igd_opregion_init()`, `vfio_pci_igd_cfg_rw()`, `vfio_pci_igd_cfg_init()`, `vfio_pci_is_intel_display()`, and `vfio_pci_igd_init()`. Registered regions use `vfio_pci_core_register_dev_region()` with Intel vendor-specific region subtypes.

Control flow reads the physical OpRegion address from config offset `0xfc`, remaps the standard 8 KiB OpRegion, validates the signature and size, optionally maps extended VBT based on OpRegion version and RVDA/RVDS fields, registers a read-only VFIO region, writes the physical address into `vconfig`, and marks the config bytes as virtual-only. Reads patch OpRegion 2.0 with extended VBT to appear like contiguous 2.1-style data by modifying the reported version and RVDA exposure. Bridge config regions are discovered at domain 0 bus 0 function 0 and function 0x1f.0 and exposed through aligned config reads.

State is held in per-region data: mapped OpRegion pointer, optional extended VBT mapping, and referenced host/LPC `pci_dev` objects. Release callbacks unmap memory and put device references. There is no persistent storage outside the VFIO device lifetime.

Dependencies include PCI config access, `memremap/memunmap`, VFIO vendor region metadata, Intel host bridge layout assumptions, and `vfio_pci_config.c` virtual config maps. Risks include platform assumptions for domain/bus/function, malformed firmware OpRegion sizes, extended VBT address interpretation differences between OpRegion 2.0 and 2.1+, and reads spanning patched boundaries. Test signals include IGD devices with/without extended VBT, invalid signatures, bridge absence, partial reads around version/RVDA boundaries, region release, and verification that writes to these regions fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_igd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_intrs.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_intrs.c

This file implements VFIO PCI interrupt setup and delivery for INTx, MSI, MSI-X, PCIe error, and request channels. It translates VFIO `SET_IRQS` operations into Linux IRQ allocation, eventfd signaling, virqfd mask/unmask hooks, and optional IRQ bypass producers.

Important state is `struct vfio_pci_irq_ctx`, stored in `vdev->ctx` xarray by vector. It contains trigger eventfd, mask/unmask virqfds, IRQ name, masked state, and IRQ bypass producer. Public entry points are `vfio_pci_intx_mask()`, `vfio_pci_intx_unmask()`, and `vfio_pci_set_irqs_ioctl()`. Internal paths cover INTx request/free, MSI/MSI-X vector allocation, vector signal replacement, block setup, disable, and context-trigger setup for error/request eventfds.

Control flow is serialized by `vdev->igate`, with fast IRQ state protected by `vdev->irqlock`. INTx enable allocates vector 0 context, establishes initial mask state from virtual INTx disable, sets `irq_type` before `request_irq()`, and handles PCI 2.3 DisINTx versus IRQ-chip masking. INTx handler masks and signals userspace. MSI/MSI-X enable allocates vectors with memory decode temporarily enabled, then attaches eventfds per vector. Dynamic MSI-X can allocate a Linux IRQ at a vector on demand. Disabling tears down virqfds, IRQs, eventfds, and frees vectors.

State persists while interrupts are configured. `vdev->irq_type` selects the active interrupt family; `ctx->masked` records INTx automask state; eventfds hold userspace notification channels. Error and request triggers are RCU-protected eventfd wrappers managed through the core helper.

Dependencies include Linux IRQ/MSI APIs, eventfd, irq_bypass, virqfd, VFIO IRQ validation in core, PCI memory decode helpers, and config-space INTx virtualization. Risks include eventfd replacement with in-flight IRQs, shared INTx false positives, DisINTx state drifting from virtual state, dynamic MSI-X vector caching after reset, unsupported mask/unmask for MSI/MSI-X, and teardown races during close/reset. Test signals include VFIO `SET_IRQS` permutations, INTx mask/unmask eventfds, MSI-X dynamic allocation, vector replacement, disable by zero-count trigger, AER error signaling, request eventfd loopback, and close while interrupts fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_intrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_priv.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_priv.h

This private header defines the internal contract among VFIO PCI core implementation files. It declares capability sentinel IDs, ioeventfd limits and state, and cross-file helpers for interrupts, config virtualization, BAR/VGA I/O, power/memory locking, IGD, zPCI, and DMA-buf support.

The only concrete type defined here is `struct vfio_pci_ioeventfd`, which records a virqfd-backed MMIO/PIO write trigger: list node, owning `vfio_pci_core_device`, virqfd handle, target BAR address, write data, BAR position/index, access width, and whether memory decode must be tested. The rest of the file is prototypes plus conditional inline stubs for optional configs.

Integration is broad: `vfio_pci_core.c` calls config, IRQ, zPCI, DMA-buf, and memory helpers; `vfio_pci_config.c` calls interrupt and DMA-buf move hooks; `vfio_pci_rdwr.c` consumes the ioeventfd definition and memory helpers; optional IGD/zPCI/DMA-buf files are compiled behind config switches. The stubs preserve call sites when features are disabled, returning `-ENODEV`, `-ENOTTY`, `-EINVAL`, or no-op semantics as appropriate.

State and persistence behavior are indirect. This header standardizes ownership expectations: `memory_lock` protects BAR memory accessibility and DMA-buf revocation; `igate` protects eventfd replacement and IRQ setup; optional feature state is owned by the corresponding C files. There is no standalone persistent storage.

Risks are mostly contract drift: prototypes must match exported definitions, disabled-feature stubs must preserve caller assumptions, and helper semantics like `vfio_pci_memory_lock_and_enable()` must remain paired with restore/unlock. Test signals include allmodconfig/minimal config builds, feature-disabled builds for VGA/IGD/zPCI/DMA-buf, static analysis for lock pairing, and compile coverage for every implementation file that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_rdwr.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_rdwr.c

This file implements VFIO PCI BAR, ROM, VGA, and ioeventfd read/write mechanics. It performs width-aware MMIO/PIO access, excludes sensitive ranges such as MSI-X tables, validates memory decode state, and translates eventfd notifications into programmed device writes.

Important exported APIs are `vfio_pci_core_iowrite{8,16,32,64}()`, `vfio_pci_core_ioread{8,16,32,64}()`, `vfio_pci_core_do_io_rw()`, `vfio_pci_core_setup_barmap()`, `vfio_pci_bar_rw()`, optional `vfio_pci_vga_rw()`, and `vfio_pci_ioeventfd()`. Endianness is handled by mapping native accessors to little-endian or big-endian I/O helpers.

Control flow for normal BAR access resolves the VFIO region index, validates the requested offset and length, maps ROM specially, rejects invalid BARs, excludes MSI-X table bytes, then loops through aligned 8/4/2/1-byte transfers. Excluded reads return `0xff` bytes and excluded writes are dropped. MMIO transfers take `memory_lock` read-side when requested and fail if virtual memory enable or power state disallows access. VGA access maps legacy memory or I/O ports under the VGA arbiter and bypasses command-memory checking because it is non-BAR legacy probing space.

State includes eager BAR maps created by core enable, per-device MSI-X table location metadata, ioeventfd list/count protected by `ioeventfds_lock`, and virqfd registrations. `vfio_pci_ioeventfd()` only supports BAR offsets, rejects MSI-X table overlap, caps registrations, and stores enough metadata to issue the programmed write from either fast handler or fallback thread.

Dependencies include PCI resource metadata, `pci_iomap`, ROM mapping, VGA arbiter, user-copy helpers, virqfd, config/core memory lock helpers, and MSI-X metadata from core enable. Risks include access-width incompatibility on ROMs, stale barmaps after close, missing memory decode checks, user offsets crossing excluded ranges, ioeventfd duplicate handling, and lock contention forcing threaded writes. Test signals include unaligned BAR I/O, ROM reads larger than actual ROM, MSI-X table exclusion, memory-enable toggles returning `-EIO`, VGA legacy ranges, ioeventfd add/remove/duplicate/max-count cases, and close teardown with active ioeventfds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_rdwr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_zdev.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_zdev.c

This file provides IBM s390 zPCI-specific VFIO PCI integration. It adds zPCI capability records to `VFIO_DEVICE_GET_INFO` and registers/unregisters zPCI devices with KVM when a VFIO device is opened with a KVM context.

Important functions are `zpci_base_cap()`, `zpci_group_cap()`, `zpci_util_cap()`, `zpci_pfip_cap()`, `vfio_pci_info_zdev_add_caps()`, `vfio_pci_zdev_open_device()`, and `vfio_pci_zdev_close_device()`. The capability structures come from `linux/vfio_zdev.h`; platform data comes from `struct zpci_dev`.

Control flow for info capability creation converts the PCI device to `zpci_dev`, then appends base function, function group, optional utility string, and function path capabilities to the VFIO info capability chain. Open-device flow is no-op without KVM, but when `vdev->vdev.kvm` exists it invokes `zpci_kvm_hook.kvm_register` if available. Close mirrors this through `kvm_unregister`.

State is not owned here beyond KVM hook registration side effects. Capability data is copied out of the live zPCI device into temporary VFIO capability buffers. KVM registration persists during the VFIO device open interval and is unwound at close.

Dependencies include s390 zPCI headers, CLP data sizes, VFIO info capability helpers, KVM host hooks, and core open/info paths. Risks include missing zPCI conversion, unavailable KVM hooks, stale utility/path strings if platform data changes, and capability version/size mismatches. Test signals include zPCI and non-zPCI devices, KVM and non-KVM opens, absent hook callbacks, info buffer sizing with optional capabilities, and open/close ordering during core enable failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_zdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Kconfig

This Kconfig file defines the virtio-specific VFIO PCI variant. `VIRTIO_VFIO_PCI` is a tristate depending on `VIRTIO_PCI` and selecting `VFIO_PCI_CORE`; it targets virtio-net and virtio-block PCI VF devices and adds VFIO migration support when the SR-IOV PF supports the required virtio admin extensions. `VIRTIO_VFIO_PCI_ADMIN_LEGACY` is a boolean depending on both `VIRTIO_VFIO_PCI` and `VIRTIO_PCI_ADMIN_LEGACY`, defaulting to enabled, and adds legacy I/O access for virtio-net VFs.

The file integrates the virtio VFIO driver with the kernel build configuration. It documents that migration relies on dirty page tracking from IOMMU hardware exposed through IOMMUFD, and that unsupported PFs fall back to generic vfio-pci behavior. The legacy option enables transitional/legacy guest driver compatibility through PF-admin-mediated emulated BAR0 I/O.

State and persistence are build-time only. Selecting these options determines whether `main.o`, `migrate.o`, and optionally `legacy_io.o` are compiled. Risks include enabling migration without hardware/IOMMUFD dirty tracking support, users expecting functionality beyond VFIO generic passthrough when PF admin capabilities are missing, and legacy I/O being available only for currently supported virtio-net device IDs. Test signals include Kconfig dependency resolution, modular and built-in builds, configs without admin legacy support, and runtime probing on virtio VFs with and without migration/legacy admin capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Makefile

This Makefile builds the virtio VFIO PCI module. It emits `virtio-vfio-pci.o` when `CONFIG_VIRTIO_VFIO_PCI` is enabled, always links `main.o` and `migrate.o`, and conditionally links `legacy_io.o` when `CONFIG_VIRTIO_VFIO_PCI_ADMIN_LEGACY` is enabled.

Its integration point is purely with Kbuild. The object composition matches the Kconfig split: generic driver binding and migration are core module functionality, while legacy I/O emulation is optional. There is no runtime state in this file.

Risks are build composition issues: missing `legacy_io.o` would leave transitional ops unresolved only if the C code were not fully guarded, and missing `migrate.o` would remove migration ops referenced by `main.o`. Test signals are `make M=drivers/vfio/pci/virtio` under both legacy-enabled and legacy-disabled configs, plus module symbol checks for migration and legacy functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/common.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/common.h

This header defines the private data model for the virtio VFIO PCI variant. It extends `vfio_pci_core_device` with optional legacy BAR0 emulation state and live migration state, and declares cross-file functions implemented by `main.c`, `legacy_io.c`, and `migrate.c`.

Important types include migration file state enums, resume-load state enums, `struct virtiovf_data_buffer` for scatter-gather backed migration chunks, `struct virtiovf_migration_header` for stream records, `struct virtiovf_migration_file` for anonymous migration fd state, and `struct virtiovf_pci_core_device` as the driver-specific container. The device struct embeds `vfio_pci_core_device`, optional `bar0_virtual_buf`, BAR mutex, notify address metadata, shadow PCI command/BAR0 fields, migration capability flag, deferred reset flag, migration state mutex, reset spinlock, and active save/resume migration files.

State is split by feature. Legacy I/O state persists across device init/release and open/close for notify mapping. Migration state persists while the VFIO device exists and active migration files exist; reset paths can mark deferred cleanup. Function declarations provide a stable internal ABI for setting migratable ops, opening/closing migration, reset notification, legacy I/O region overrides, and config/BAR read-write wrappers.

Dependencies include Linux virtio, virtio PCI, VFIO PCI core, and optional `CONFIG_VIRTIO_VFIO_PCI_ADMIN_LEGACY`. Risks include struct layout assumptions through `container_of`, lock ordering between `state_mutex`, `reset_lock`, file locks, and VFIO/core reset locks, and conditional compilation mismatches. Test signals include build coverage with legacy enabled/disabled, migration state transitions, reset during active migration fd use, and legacy BAR0 read/write wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/legacy_io.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/legacy_io.c

This file implements admin-command-backed legacy I/O emulation for virtio-net PCI VFs that do not expose BAR0 but can be controlled through a supporting PF. It makes a modern VF look like a transitional virtio device to userspace/guest drivers by virtualizing config fields and intercepting BAR0 I/O.

Important functions are `virtiovf_issue_legacy_rw_cmd()`, `virtiovf_pci_bar0_rw()`, config wrappers `virtiovf_pci_read_config()` and `virtiovf_pci_write_config()`, exported `virtiovf_pci_core_read/write()`, `virtiovf_pci_ioctl_get_region_info()`, `virtiovf_open_legacy_io()`, `virtiovf_support_legacy_io()`, `virtiovf_init_legacy_io()`, `virtiovf_release_legacy_io()`, and `virtiovf_legacy_io_reset_done()`.

Control flow routes config-space reads through generic VFIO first, then patches device ID, revision, command I/O bit, BAR0, subsystem ID, and subsystem vendor ID where the requested range intersects those registers. Config writes shadow PCI command and BAR0 values before delegating to generic VFIO. BAR0 read/write checks the shadow I/O enable bit, resumes runtime PM, handles queue notify via the mapped notify address, and sends other common/device config accesses through virtio PCI admin legacy I/O commands. Region info for BAR0 reports the synthetic virtual size instead of a real PCI resource.

State includes the virtual BAR0 buffer, BAR mutex, notify BAR/offset/address, shadow `pci_cmd`, and shadow `pci_base_addr_0`. Init reads notify info through admin commands, computes a power-of-two virtual BAR0 size, allocates the buffer, and initializes locking. Open maps the notify BAR after core enable has established BAR maps. Reset clears `pci_cmd`.

Dependencies include virtio PCI admin legacy commands, VFIO core read/write and range intersection helper, runtime PM, BAR map setup, and virtio-net config sizing. Risks include only supporting virtio-net device `0x1041`, partial config writes to shadow fields, exposing I/O as enabled inconsistently with generic config state, notify BAR mapping lifetime, and PF admin command failures. Test signals include virtio-net VF with no BAR0, non-net virtio devices, legacy common/device config reads, queue notify writes, config range-intersection partial reads/writes, reset clearing I/O enable, and Kconfig-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/legacy_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/main.c

This file is the PCI driver wrapper for virtio VFIO PCI devices. It selects the right VFIO device ops based on VF capabilities, allocates the virtio-specific core device, registers it with VFIO PCI core, and wires reset notifications to migration and optional legacy I/O.

Important functions are `virtiovf_pci_open_device()`, `virtiovf_pci_close_device()`, optional `virtiovf_pci_init_device()`, `virtiovf_pci_core_release_dev()`, `virtiovf_pci_probe()`, `virtiovf_pci_remove()`, and `virtiovf_pci_aer_reset_done()`. Three operation tables exist: generic virtio VFIO, live-migration, and transitional legacy-plus-migration. The PCI ID table supports Red Hat/Qumranet virtio-net and virtio-block VF override IDs.

Probe control flow detects whether the PCI function is a VF, asks the optional legacy layer whether legacy I/O is supported, checks virtio admin device-parts support for migration, selects the matching `vfio_device_ops`, allocates `virtiovf_pci_core_device`, marks it migratable when applicable, stores drvdata, and registers with `vfio_pci_core_register_device()`. Open enables the core device, opens legacy I/O if present, opens migration, then finishes enablement. Close shuts down migration before core close. Remove unregisters and drops the VFIO device.

State is mostly in the allocated `virtiovf_pci_core_device`; this file chooses which callbacks expose and mutate that state. The PCI driver is `driver_managed_dma`, relying on VFIO/iommufd ownership rather than normal DMA API setup.

Dependencies include VFIO PCI core, virtio PCI admin helpers, optional legacy I/O, migration ops, PCI error handlers, and module PCI driver registration. Risks include selecting the wrong ops when both legacy and migration capabilities vary, leaving legacy resources initialized without matching release, open failure unwind after legacy setup, and reset notifications during active migration. Test signals include probe on PF versus VF, VF with migration only, VF with legacy plus migration, unsupported VF falling back to generic ops, open/close failure injection, remove after failed register, and AER reset-done callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/migrate.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/migrate.c

This file implements live migration for virtio VFIO PCI devices using virtio PCI admin device-parts objects. It supplies VFIO migration ops, anonymous save/resume files, pre-copy support, P2P stop mode transitions, and reset cleanup.

Important types are defined in `common.h`: `virtiovf_migration_file`, `virtiovf_data_buffer`, stream headers, and state enums. Major functions include page/buffer management (`virtiovf_add_migration_pages()`, `virtiovf_get_data_buffer()`), object management (`virtiovf_pci_alloc_obj_id/free_obj_id()`), save path (`virtiovf_pci_save_device_data()`, `virtiovf_read_device_context_chunk()`, `virtiovf_save_read()`, `virtiovf_precopy_ioctl()`), resume path (`virtiovf_pci_resume_device_data()`, `virtiovf_resume_write()` and its load-state helpers), migration state ops (`virtiovf_pci_set_device_state()`, `virtiovf_pci_get_device_state()`, `virtiovf_pci_get_data_size()`), and lifecycle hooks `virtiovf_set_migratable()`, `virtiovf_open_migration()`, `virtiovf_close_migration()`, `virtiovf_migration_reset_done()`.

Control flow follows VFIO migration arcs. Entering pre-copy or stop-copy creates a GET object id, reads device parts metadata, fetches chunks into SG-backed buffers, prefixes each chunk with a migration header, and returns a read-only stream fd. Pre-copy ioctl reports initial and dirty bytes and may rate-limit fresh device-part fetches. Entering resuming creates a SET object id and a write-only stream fd; writes parse record headers, skip optional unknown records, copy mandatory device-data chunks into SG pages after a resource-object command header, and submit them with `virtio_pci_admin_dev_parts_set()`. P2P transitions use `virtio_pci_admin_mode_set()` to set or clear stopped mode.

State is substantial and lock-sensitive. `state_mutex` protects VFIO migration state and active save/resume fds; each migration file has a file lock plus list lock; reset handling uses `reset_lock` and `deferred_reset` to avoid ABBA deadlocks with higher VFIO reset locks. Buffers are pooled on available lists and freed on fd disable/cleanup. Object ids persist only for active flows.

Dependencies include VFIO migration core, anonymous inodes/stream files, virtio PCI admin device parts/mode APIs, scatter-gather page allocation, ratelimit state, runtime reset callbacks from `main.c`, and dirty tracking assumptions documented in Kconfig. Risks include malformed migration streams, huge record sizes, SG end-marker manipulation, partial writes, state arc errors, fd cleanup during reset, stale object ids on cancellation, and pre-copy data changing faster than rate-limited refresh. Test signals include full state transition matrix, pre-copy ioctl behavior, stop-copy final data, resume with optional and unknown mandatory tags, MAX_LOAD_SIZE rejection, reset during active save/resume, repeated migration cancellation, and fault injection in admin commands and page allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Kconfig

This Kconfig file defines the Intel Xe-specific VFIO PCI variant. `XE_VFIO_PCI` is a tristate option depending on `DRM_XE` and `PCI_IOV`, selecting `VFIO_PCI_CORE`. Its help text describes a device-specific VFIO driver for Intel Graphics SR-IOV virtual functions that adds VFIO migration uAPI support on top of generic VFIO PCI behavior.

Integration is build-time: enabling this option compiles the Xe VFIO PCI module from the sibling Makefile. It relies on the Xe DRM driver and PCI SR-IOV support, so it is intentionally scoped to platforms where Xe virtual functions and their migration hooks exist.

There is no runtime state in this file. Risks are configuration mismatch and user expectation: selecting the option without supported Xe SR-IOV hardware or migration-capable Xe driver paths will not produce useful runtime behavior. Test signals include Kconfig dependency resolution with and without `DRM_XE`/`PCI_IOV`, module and built-in builds, and runtime probe tests on supported Intel Graphics VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Makefile

This Makefile builds the Intel Xe VFIO PCI variant. It emits `xe-vfio-pci.o` when `CONFIG_XE_VFIO_PCI` is enabled and links `main.o` into that module.

The integration point is Kbuild only. The file reflects a compact driver variant whose implementation is in `main.c` under the same directory, with VFIO PCI core selected by Kconfig. It has no runtime state or persistence behavior.

Risks are limited to build composition: the Kconfig option must select required VFIO PCI core support, and the referenced `main.o` must provide the PCI driver/module entry points. Test signals include `make M=drivers/vfio/pci/xe`, allmodconfig coverage, disabled-option builds, and module symbol/modinfo checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Makefile -->
