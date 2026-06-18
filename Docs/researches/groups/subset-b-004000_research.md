# subset-b-004000 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.c

## Purpose
This file is the OMAP/TI IOMMU driver implementation. It registers OMAP IOMMU platform devices with the generic Linux IOMMU core, manages OMAP hardware page tables and TLBs, services translation faults, and exposes paging-domain operations for OMAP client devices that reference one or more IOMMU phandles in device tree.

## Important APIs, Types, And Functions
The central types are declared in `omap-iommu.h`: `struct omap_iommu` for a hardware instance, `struct omap_iommu_domain` for a generic IOMMU domain, `struct omap_iommu_device` for per-domain per-IOMMU state, and `struct iotlb_entry` for OMAP CAM/RAM TLB entries. Driver entry points are `omap_iommu_probe()`, `omap_iommu_remove()`, and `omap_iommu_init()`. Generic IOMMU hooks are collected in `omap_iommu_ops` and include `domain_alloc_paging`, `probe_device`, `release_device`, `of_xlate`, `attach_dev`, `map_pages`, `unmap_pages`, `iova_to_phys`, and `free`.

Key translation helpers include `omap_iopgtable_store_entry()`, `iopgtable_clear_entry()`, `iopgtable_clear_entry_all()`, `iopgtable_lookup_entry()`, `iopgd_alloc_section()`, `iopgd_alloc_super()`, `iopte_alloc_page()`, and `iopte_alloc_large()`. Hardware control is routed through `omap2_iommu_enable()`, `omap2_iommu_disable()`, `iommu_enable()`, `iommu_disable()`, `flush_iotlb_page()`, and `flush_iotlb_all()`. Runtime/system PM support is in `omap_iommu_runtime_suspend()`, `omap_iommu_runtime_resume()`, and `omap_iommu_prepare()`. Legacy exported context helpers are `omap_iommu_save_ctx()`, `omap_iommu_restore_ctx()`, `omap_iommu_domain_activate()`, and `omap_iommu_domain_deactivate()`.

## Control Flow
At subsystem init, the driver creates the `iopte_cache` slab with 1 KiB alignment, initializes debugfs support, and registers the platform driver only if a matching OMAP IOMMU node exists. Probe validates DT-only use, allocates `struct omap_iommu`, maps MMIO registers, reads TLB-entry count and bus-error-back properties, optionally resolves DRA7 DSP syscon configuration, requests the shared IRQ, registers sysfs/IOMMU core state, enables runtime PM, and adds debugfs.

Client devices are discovered through `omap_iommu_probe_device()`, which parses the `iommus` phandle array, resolves each platform IOMMU, and stores a NULL-terminated `omap_iommu_arch_data` array in `dev_iommu_priv`. `omap_iommu_attach_dev()` allows only one client per domain. It allocates one aligned L1 page directory per attached IOMMU, maps each directory for DMA, enables each IOMMU through runtime PM, flushes TLBs, and records the generic domain in the hardware instance.

Mapping converts the requested size to OMAP page size encodings: 4 KiB, 64 KiB, 1 MiB, or 16 MiB. It builds an `iotlb_entry` and mirrors the page-table update into every IOMMU attached to the domain. On partial failure it clears already-installed entries. Unmap mirrors removal across all attached IOMMUs and returns zero if any instance reports an unmapped entry. Fault IRQ flow reads and clears `MMU_IRQSTATUS`, reports to the generic fault handler, disables further IRQs on unhandled faults, and logs the L1/L2 entry state for diagnosis.

## State And Persistence
Persistent runtime state lives in `struct omap_iommu`, the per-domain page directories, and slab-allocated L2 tables. Page directories are `kzalloc()` allocations attached to domains, DMA-mapped while the hardware is attached, and freed at detach/domain free. L2 tables are allocated from `iopte_cache`, DMA-mapped, linked through L1 entries, and freed when emptied. Hardware state includes `MMU_TTB`, `MMU_CNTL`, `MMU_LOCK`, CAM/RAM TLB entries, DRA7 DSP MMU syscon bits, and IRQ enable/status registers. Runtime PM suspend saves locked TLB entries in `cr_ctx` and disables/reset-idles the device; resume restores locked entries and reprograms the table base.

## Dependencies And Integration Points
The driver depends on Linux IOMMU core APIs, OF phandles, platform devices, runtime PM, DMA mapping, regmap/syscon for DRA7 DSP, OMAP platform reset/idle callbacks, debugfs helpers from the OMAP IOMMU support files, and `omap-iopgtable.h` descriptor helpers. It uses generic single-device groups and reports faults via `report_iommu_fault()`. The exported activation/context APIs preserve behavior for legacy OMAP clients such as OMAP3 ISP.

## Risks
The implementation assumes DMA and physical addresses are identical for L2 page-table mappings and warns/fails otherwise. Domain attach is single-client only, while a client can reference multiple IOMMUs, so multi-device sharing is deliberately constrained. Several paths call runtime PM and hardware register operations from mapping/TLB routines, so power-state ordering is important. Fault handling disables IRQs when faults are unhandled, which can hide later faults until recovery. Map/unmap consistency relies on mirrored programming across all attached IOMMUs; unmap does not verify every instance removed the same size. The source should be compile-checked carefully because low-level page-table and TLB code is sensitive to alignment, cache flushing, and locking.

## Test Signals
Useful checks include DT probe with each compatible string, attach/detach through a real OMAP client with one and multiple IOMMU phandles, map/unmap for all supported sizes, iova-to-phys translation for L1 section/supersection and L2 page/large-page entries, runtime suspend/resume with locked TLB context, DRA7 DSP syscon enable/disable, forced translation faults with generic fault callbacks, and DMA mapping failure injection for L1/L2 tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.h

## Purpose
This header defines the private OMAP IOMMU data model, MMIO register layout, bit fields, and page-size conversion helpers consumed by `omap-iommu.c` and related OMAP IOMMU support code.

## Important APIs, Types, And Functions
`struct omap_iommu` describes one hardware MMU instance: MMIO base, syscon handle, device pointer, attached domain, debugfs directory, IOTLB/page-table locks, current I/O page directory, DMA address, TLB count, saved register context, saved CAM/RAM entries, bus-error behavior, IOMMU core object, and power-state token. `struct omap_iommu_domain` embeds `struct iommu_domain` and tracks a single client device plus an array of `struct omap_iommu_device` entries. `struct omap_iommu_arch_data` is stored as per-client private data and binds a client to its IOMMU devices. `struct iotlb_entry`, `struct cr_regs`, and `struct iotlb_lock` model CAM/RAM entries and TLB lock register fields.

Register definitions cover `MMU_REVISION`, IRQ status/enable, walk/control, fault address, table base, lock, TLB load/CAM/RAM/flush/read registers, emulation fault address, and general-purpose bus-error-back control. Bit definitions cover IRQ categories, table-walk enable, MMU enable, CAM valid/preserved/page-size fields, RAM address/endian/element-size/mixed fields, and DRA7 DSP system MMU config.

## Control Flow
The header has no runtime control flow, but it encodes control decisions used by the C file. `for_each_iotlb_cr()` iterates hardware TLB entries by repeatedly invoking `__iotlb_read_cr()`. `get_cam_va_mask()`, `iopgsz_max()`, and `bytes_to_iopgsz()` drive size validation and CAM encoding in map/TLB paths.

## State And Persistence
The types in this header define all long-lived driver state: domain attachment, per-instance hardware context, saved TLB context across PM, and per-client private links. Register and bit definitions are stable ABI-like hardware contracts for OMAP IOMMU blocks.

## Dependencies And Integration Points
The header depends on `linux/bitops.h` and `linux/iommu.h`. It is tightly coupled to OMAP platform data, OMAP DT binding properties, and `omap-iopgtable.h` for descriptor layout.

## Risks
Incorrect register bit definitions would directly corrupt hardware programming. The private structs are shared between generic IOMMU paths, runtime PM, fault handling, and debug paths, so field lifetime and locking expectations must stay aligned with the implementation. The page-size macros only support the four OMAP hardware sizes; callers must reject other sizes.

## Test Signals
Compile coverage of `omap-iommu.c` is the main signal. Runtime signals include correct TLB iteration, correct page-size encoding for map requests, and successful suspend/resume context save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iopgtable.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/omap-iopgtable.h

## Purpose
This header defines the OMAP IOMMU page-table descriptor layout and index/translation helpers for the two-level OMAP hardware page table used by `omap-iommu.c`.

## Important APIs, Types, And Functions
The file defines L1 directory geometry with `IOPGD_SHIFT`, `IOPGD_SIZE`, `IOPGD_MASK`, `PTRS_PER_IOPGD`, and `IOPGD_TABLE_SIZE`; section and supersection geometry with `IOSECTION_*` and `IOSUPER_*`; and L2 page-table geometry with `IOPTE_SHIFT`, `IOLARGE_SHIFT`, `PTRS_PER_IOPTE`, and `IOPTE_TABLE_SIZE`. Descriptor encodings include `IOPGD_TABLE`, `IOPGD_SECTION`, `IOPGD_SUPER`, `IOPTE_SMALL`, and `IOPTE_LARGE`, with predicate macros for each kind.

`omap_iommu_translate()` combines a descriptor base address with an IOVA offset under a size mask. `iopgd_index()`, `iopgd_offset()`, `iopgd_page_paddr()`, `iopgd_page_vaddr()`, `iopte_index()`, and `iopte_offset()` locate page-directory and page-table entries.

## Control Flow
The header is macro and inline helper only. At runtime map/unmap/iova-to-phys paths use these helpers to choose L1 versus L2 descriptors, calculate table offsets, and translate descriptor values back to CPU physical addresses.

## State And Persistence
It defines no storage itself. It defines the layout of persistent OMAP page directories and L2 tables that are allocated, DMA-synchronized, and freed by the implementation.

## Dependencies And Integration Points
It depends on Linux bit helpers and assumes OMAP page tables are addressable through `phys_to_virt()` for L2 table access. It is consumed by OMAP IOMMU map, unmap, fault-dump, and iova-to-phys code.

## Risks
The macros assume 32-bit IOVA space and descriptor fields. `iopgd_page_vaddr()` assumes a direct physical-to-virtual mapping for page tables; platforms where DMA address, physical address, and CPU direct-map assumptions differ are risky. Incorrect size masks would cause either wrong physical translations or freeing the wrong entries.

## Test Signals
Exercise map/unmap and iova-to-phys for 4 KiB, 64 KiB, 1 MiB, and 16 MiB mappings. Boundary tests should cover L1/L2 index transitions and large/supersection alignment failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iopgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/Kconfig

## Purpose
This Kconfig fragment enables the RISC-V IOMMU driver family and its PCI transport support.

## Important APIs, Types, And Functions
`RISCV_IOMMU` is a boolean option defaulting to `RISCV`, constrained to `64BIT` and either native RISC-V or `COMPILE_TEST`, and dependent on `GENERIC_MSI_IRQ`. It selects `IOMMU_API`, `GENERIC_PT`, `IOMMU_PT`, and `IOMMU_PT_RISCV64`, which are required by `iommu.c` for generic page-table backed domains. `RISCV_IOMMU_PCI` defaults to yes when `RISCV_IOMMU` and `PCI_MSI` are enabled.

## Control Flow
There is no runtime flow. Build configuration determines whether `iommu.o` and platform support are built, and whether PCI support is included.

## State And Persistence
The file contributes persistent kernel build configuration only.

## Dependencies And Integration Points
It integrates the RISC-V IOMMU driver with the generic IOMMU API, generic page-table framework, RISC-V 64-bit page-table backend, generic MSI IRQ handling, and optional PCI MSI support.

## Risks
The driver assumes 64-bit RISC-V IOMMU page-table modes in the implementation, so relaxing `64BIT` or missing generic page-table selections would break compilation or runtime attach. PCI support is gated on `PCI_MSI`; systems with only platform IOMMU devices use the always-built platform object from the Makefile.

## Test Signals
Kconfig tests should cover native RISC-V builds, `COMPILE_TEST` builds, builds without `PCI_MSI`, and build dependency resolution for `GENERIC_PT` and `IOMMU_PT_RISCV64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/Makefile

## Purpose
This Makefile declares the object composition for RISC-V IOMMU support.

## Important APIs, Types, And Functions
It always builds `iommu.o` and `iommu-platform.o` into the enclosing object when the directory is selected. It adds `iommu-pci.o` only under `CONFIG_RISCV_IOMMU_PCI`.

## Control Flow
There is no runtime flow. The file establishes build-time linkage: platform support is part of core RISC-V IOMMU support, while PCI support is optional.

## State And Persistence
No runtime state. Build products persist according to kernel build configuration.

## Dependencies And Integration Points
It depends on the parent IOMMU Kbuild selecting this directory and on Kconfig supplying `CONFIG_RISCV_IOMMU_PCI`.

## Risks
Because `iommu-platform.o` is unconditional once the directory is built, platform-driver dependencies must remain available under the same Kconfig constraints. Optional PCI code must not be referenced unconditionally by core code.

## Test Signals
Build with `RISCV_IOMMU=y, RISCV_IOMMU_PCI=y` and with `RISCV_IOMMU_PCI` absent to confirm object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-bits.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-bits.h

## Purpose
This header is the RISC-V IOMMU hardware contract. It defines MMIO register offsets, bit fields, queue record layouts, device/process context layouts, MSI page-table entries, fault causes, transaction types, and inline command builders based on the RISC-V IOMMU architecture specification.

## Important APIs, Types, And Functions
Register definitions include capabilities, feature control, device directory table pointer, command/fault/page-request queue base/head/tail/CSR registers, interrupt pending/status/vector registers, performance-monitoring registers, translation request registers, and MSI configuration table registers. Capability fields advertise supported address-translation modes, MSI formats, endianness control, ATS, performance monitoring, process-directory widths, and interrupt generation mode.

Important data structures are `struct riscv_iommu_dc` for device contexts, `struct riscv_iommu_pc` for process contexts, `struct riscv_iommu_command` for command queue entries, `struct riscv_iommu_fq_record` for fault/event queue entries, `struct riscv_iommu_pq_record` for page-request queue entries, and `struct riscv_iommu_msipte` for MSI translation entries. Enums encode interrupt-generation settings, DDTP modes, HPM event IDs, first/second stage translation modes, fault causes, and fault transaction types.

Inline builders include `riscv_iommu_cmd_inval_vma()`, `riscv_iommu_cmd_inval_set_addr()`, `riscv_iommu_cmd_inval_set_pscid()`, `riscv_iommu_cmd_inval_set_gscid()`, `riscv_iommu_cmd_iofence()`, `riscv_iommu_cmd_iofence_set_av()`, `riscv_iommu_cmd_iodir_inval_ddt()`, `riscv_iommu_cmd_iodir_inval_pdt()`, `riscv_iommu_cmd_iodir_set_did()`, and `riscv_iommu_cmd_iodir_set_pid()`.

## Control Flow
The header has no standalone flow, but `iommu.c` depends on its command builders for IOTLB invalidation, IODIR invalidation, and IOFENCE synchronization. Probe code uses capability and FCTL fields to select interrupt mode and byte order. Queue code uses common queue CSR bits and index masks.

## State And Persistence
It defines the binary layout of persistent in-memory structures shared with hardware: DDT nodes, device contexts, process contexts, command queues, fault queues, page-request queues, and MSI page-table entries. It also defines hardware register state layout.

## Dependencies And Integration Points
The file uses Linux bitfield helpers and architecture page definitions. It is included by all RISC-V IOMMU implementation files and must remain synchronized with the RISC-V IOMMU spec and generic page-table code.

## Risks
A wrong field mask or command encoding can corrupt device-context setup or invalidate the wrong translations. The header includes future-facing definitions for features not fully implemented by `iommu.c` yet, such as PASID/SVA, ATS, page-request queue, and second-stage handling; users of those fields must add full invalidation and state-management support. Duplicated or misspelled symbolic definitions in this source should be caught by compile and style checks.

## Test Signals
Compile tests across 64-bit RISC-V and `COMPILE_TEST`, queue command encoding unit-style checks if available, hardware/QEMU boot with command/fault queue traffic, attach/detach with PSCID invalidation, and MSI/WSI interrupt-mode probe coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-pci.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-pci.c

## Purpose
This file binds RISC-V IOMMU hardware exposed as a PCI function. It performs PCI resource setup, MSI vector allocation, capability validation, and delegates common initialization/removal/shutdown to the shared RISC-V IOMMU core.

## Important APIs, Types, And Functions
`riscv_iommu_pci_probe()` enables the PCI device, validates BAR0 memory size, maps BAR0, allocates `struct riscv_iommu_device`, reads `CAPABILITIES` and `FCTL`, verifies MSI-capable interrupt generation, allocates MSI/MSI-X vectors, records Linux IRQ numbers, clears `FCTL.WSI` to select message-signaled mode, and calls `riscv_iommu_init()`. `riscv_iommu_pci_remove()` calls `riscv_iommu_remove()`. `riscv_iommu_pci_shutdown()` calls `riscv_iommu_disable()`. The PCI ID table includes QEMU Red Hat and Rivos device IDs.

## Control Flow
Probe is strictly staged: PCI enable, BAR validation/mapping, core struct allocation, capability read, interrupt-mode validation, vector allocation, FCTL programming, common core initialization. Remove unregisters and disables through shared core paths; shutdown performs best-effort translation disable without full teardown.

## State And Persistence
Per-device state is a `struct riscv_iommu_device` stored in PCI device drvdata. Register mappings are pcim-managed. IRQ vectors are allocated by PCI MSI APIs and stored in `iommu->irqs`.

## Dependencies And Integration Points
The file depends on PCI managed resource APIs, MSI APIs, RISC-V IOMMU bit definitions, and shared functions in `iommu.c`. It is built only when `CONFIG_RISCV_IOMMU_PCI` is true.

## Risks
The PCI path requires MSI or MSI-X; hardware exposing only WSI is rejected. It assumes BAR0 contains the complete RISC-V IOMMU register window. Interrupt count may be fewer than architectural causes, so core vector remapping must be correct. Shutdown only disables translation/queues and does not wait for all hardware state to quiesce.

## Test Signals
QEMU RISC-V IOMMU PCI probe, Rivos hardware probe, MSI and MSI-X vector allocation variants, BAR length failure tests, removal/unbind, and kexec/shutdown checks that translation is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-platform.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-platform.c

## Purpose
This file binds RISC-V IOMMU hardware exposed as a platform device through DT or ACPI. It maps registers, chooses MSI or wired-signaled interrupt delivery, programs MSI configuration table entries, and delegates common initialization to `iommu.c`.

## Important APIs, Types, And Functions
`riscv_iommu_write_msi_msg()` is the platform-MSI message writer; it masks MSI address bits to the hardware-supported field, writes address/data/control table entries, and unmasks the entry. `riscv_iommu_platform_probe()` allocates `struct riscv_iommu_device`, maps the register resource, reads capabilities/FCTL, selects interrupt mode from `CAPABILITIES.IGS`, configures OF or ACPI/IMSIC MSI domains, allocates platform MSI IRQs when possible, falls back to WSI if supported, sets or clears `FCTL.WSI`, and calls `riscv_iommu_init()`. Remove frees MSI IRQs when MSI mode was used after `riscv_iommu_remove()`. Shutdown calls `riscv_iommu_disable()`.

## Control Flow
Probe first determines the hardware interrupt-generation capability. For MSI or both, it attempts MSI-domain setup and vector allocation. If MSI fails and hardware supports only MSI, probe fails. If hardware supports both, it falls through to WSI setup. WSI setup counts platform IRQ resources, caps the count at the architectural interrupt count, records IRQs, and sets `FCTL.WSI`. The shared core then allocates queues, enables queues, configures the device directory, and registers with the IOMMU core.

## State And Persistence
State is stored in `struct riscv_iommu_device` in platform drvdata. MSI mode also creates platform MSI IRQ allocations and hardware MSI table entries. FCTL interrupt-mode state persists until remove or shutdown.

## Dependencies And Integration Points
The file integrates with OF platform probing, ACPI ID `RSCV0004`, IMSIC ACPI fwnode lookup, generic MSI domains, platform MSI allocation, and the shared RISC-V IOMMU core.

## Risks
MSI address truncation is warned but still programmed with a masked address, so platforms must ensure deliverable MSI addresses. ACPI MSI setup depends on IMSIC fwnode discovery. WSI fallback requires usable platform IRQ resources. Remove decides whether to free MSI IRQs from the post-init FCTL WSI bit, so FCTL state must reflect the selected mode.

## Test Signals
DT platform probe with MSI, ACPI platform probe with IMSIC MSI, forced MSI allocation failure with WSI fallback, WSI-only hardware, remove-time MSI free, and shutdown/kexec disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.c

## Purpose
This is the shared RISC-V IOMMU core. It manages hardware queues, device-directory tables, device contexts, generic RISC-V page-table backed domains, PSCID allocation, IOTLB invalidation, fault-queue reporting, device attach/detach, and registration with the Linux IOMMU core.

## Important APIs, Types, And Functions
The public entry points used by bus glue are `riscv_iommu_init()`, `riscv_iommu_remove()`, and `riscv_iommu_disable()`. Internal queue management is handled by `riscv_iommu_queue_alloc()`, `riscv_iommu_queue_enable()`, `riscv_iommu_queue_disable()`, `riscv_iommu_queue_send()`, `riscv_iommu_queue_wait()`, `riscv_iommu_queue_consume()`, and `riscv_iommu_queue_release()`. Command helpers are wrapped by `riscv_iommu_cmd_send()` and `riscv_iommu_cmd_sync()`. Fault handling is in `riscv_iommu_fltq_process()` and `riscv_iommu_fault()`.

Device-directory management centers on `riscv_iommu_iodir_alloc()`, `riscv_iommu_iodir_set_mode()`, `riscv_iommu_get_dc()`, `riscv_iommu_iodir_update()`, and `riscv_iommu_iodir_iotinval()`. Domain state is `struct riscv_iommu_domain`, embedding a generic page-table domain (`pt_iommu_riscv_64`) plus an RCU-protected bond list and PSCID. Device private state is `struct riscv_iommu_info`. Generic IOMMU hooks include paging, identity, and blocking attach paths plus `riscv_iommu_probe_device()`, `riscv_iommu_release_device()`, `riscv_iommu_device_group()`, and `riscv_iommu_of_xlate()`.

## Control Flow
Initialization configures command/fault queues, validates the initial DDTP state, fixes byte order if supported, programs interrupt vector routing, allocates the DDT root, allocates queue backing memory or maps fixed queue memory, enables command and fault queues with threaded IRQ handlers, switches DDTP to the maximum supported DDT mode, registers sysfs, optionally registers ACPI RIMT state, and registers the IOMMU core device.

Device probe obtains fwspec IDs, resolves the IOMMU from the fwnode device, rejects fail-over OFF/BARE mode, preallocates invalid device-context entries for every device ID, and stores private info. Paging-domain allocation chooses Sv39/Sv48/Sv57 based on capabilities, allocates a PSCID, initializes the generic RISC-V 64-bit page table with sign-extension, flush-range, and Svnapot 64 KiB features, and returns a domain with page-table ops. Attach verifies hardware page-table mode support, computes FSC and translation attributes, links the device into the domain bond list, updates device-context entries, unlinks the previous tracked domain, and records the new domain in private device info. Blocking and identity attach update the device context to invalid or BARE respectively and unlink any tracked paging domain.

IOTLB invalidation walks the domain bond list under RCU, sends one invalidation per IOMMU for the domain PSCID, optionally emits per-page invalidations for ranges below the current threshold, then sends IOFENCE.C commands and waits. Device-context updates first invalidate any existing valid context, synchronize, then write FSC/TA and TC.V last with a DMA write barrier, followed by IODIR and IOTINVAL commands.

## State And Persistence
Persistent state includes command and fault queue ring buffers, DDT root/pages, device contexts, PSCID namespace allocations, generic page tables, and domain bond lists. Queue indices are tracked with atomic unbounded producer/head/tail counters and hardware head/tail registers. Device-directory pages are devres-managed and freed with the device. Domain page tables and PSCIDs are freed in `riscv_iommu_free_paging_domain()`.

## Dependencies And Integration Points
The core depends on the RISC-V IOMMU register/data definitions, Linux IOMMU core, generic page-table IOMMU namespace, PCI group helpers for PCI devices, OF fwspec IDs, ACPI RIMT registration, devres, IDA PSCID allocation, threaded IRQs, RCU, and DMA/MMIO ordering primitives.

## Risks
Fault handling is currently report-only and does not recover beyond queue CSR clearing. Queue error recovery is explicitly incomplete. IOTLB range invalidation falls back to page-by-page commands below a threshold or whole-PSCID invalidation above it because range invalidations are not yet available. Attach updates valid device contexts and notes that doing so while a device is not quiesced may be disruptive. PASID/SVA, ATS, page-request queue, and second-stage support are mostly not implemented despite data definitions. Timeouts log hardware errors but many flows continue, so hardware non-response can leave stale translations.

## Test Signals
Boot/probe on platform and PCI RISC-V IOMMU implementations, attach/detach paging/identity/blocking domains, DMA map/unmap through generic page-table ops, PSCID reuse/free, DDT mode fallback, command/fault queue interrupts, injected fault queue records, kdump boot with previously enabled DDTP, big-endian FCTL handling, ACPI RIMT registration, and stress tests with concurrent map/unmap/attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.h

## Purpose
This header defines the shared RISC-V IOMMU core data structures and MMIO access wrappers used by PCI and platform bus glue plus the core implementation.

## Important APIs, Types, And Functions
`struct riscv_iommu_queue` stores queue producer/consumer shadows, mask, IRQ, active IOMMU pointer, base virtual address, physical address, register offsets, and queue ID. `struct riscv_iommu_device` embeds `struct iommu_device`, records the backing Linux device, MMIO register base, capabilities, FCTL state, interrupt vectors, command/fault queues, and device-directory table mode/root. The header declares `riscv_iommu_init()`, `riscv_iommu_remove()`, and `riscv_iommu_disable()`.

Access macros `riscv_iommu_readl()`, `riscv_iommu_readq()`, `riscv_iommu_writel()`, `riscv_iommu_writeq()`, `riscv_iommu_readq_timeout()`, and `riscv_iommu_readl_timeout()` provide relaxed MMIO reads/writes and polling wrappers over the mapped register window.

## Control Flow
The header does not implement flow, but it fixes the interface between `iommu-pci.c`, `iommu-platform.c`, and `iommu.c`: bus glue fills `struct riscv_iommu_device`, then calls `riscv_iommu_init()`; remove/shutdown call `riscv_iommu_remove()` or `riscv_iommu_disable()`.

## State And Persistence
The queue and device structs hold all persistent shared state across bus drivers and core operations: queue buffers, IRQ routing, capabilities, FCTL mode, and DDT root configuration.

## Dependencies And Integration Points
It includes Linux IOMMU types, fixed-width types, I/O polling helpers, and `iommu-bits.h`. It is the narrow internal ABI between transport-specific drivers and the common RISC-V IOMMU core.

## Risks
The MMIO helpers are relaxed; ordering must be added explicitly at call sites where hardware-visible memory updates precede doorbells or context-valid bits. The transport drivers must fully initialize capabilities, FCTL, IRQs, register base, and device pointer before calling init.

## Test Signals
Compile all RISC-V IOMMU objects together and test both platform and PCI paths, ensuring each initializes the struct fields required by the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/rockchip-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/rockchip-iommu.c

## Purpose
This file implements the Rockchip IOMMU driver. It manages Rockchip two-level page tables, hardware register banks, clocks/runtime PM, stall/paging commands, page-fault IRQs, and generic IOMMU domain operations for Rockchip display/media masters.

## Important APIs, Types, And Functions
`struct rk_iommu_domain` owns the directory table, DMA address, attached IOMMU list, locks, DMA device, and embedded generic domain. `struct rk_iommu` represents one platform IOMMU that may expose multiple MMU register banks and IRQs. `struct rk_iommu_ops` abstracts v1/v2 descriptor encoding, physical address extraction, DMA mask, and allocation flags. `struct rk_iommudata` stores the per-master IOMMU pointer and runtime PM device link.

Important helpers include descriptor encoders/extractors `rk_mk_dte()`, `rk_mk_dte_v2()`, `rk_mk_pte()`, `rk_mk_pte_v2()`, `rk_ops->pt_address()`, index helpers, register commands, `rk_iommu_enable_stall()`, `rk_iommu_disable_stall()`, `rk_iommu_enable_paging()`, `rk_iommu_disable_paging()`, and `rk_iommu_force_reset()`. Generic ops are `rk_iommu_attach_device()`, `rk_iommu_identity_attach()`, `rk_iommu_map()`, `rk_iommu_unmap()`, `rk_iommu_iova_to_phys()`, `rk_iommu_domain_alloc_paging()`, `rk_iommu_domain_free()`, `rk_iommu_probe_device()`, `rk_iommu_release_device()`, and `rk_iommu_of_xlate()`.

## Control Flow
Probe allocates the IOMMU instance, selects v1/v2 ops from the compatible string, maps all memory resources as MMU banks, counts IRQs, reads optional reset-disable property, prepares optional clocks, enables runtime PM, requests shared IRQs, sets the DMA mask, and registers the IOMMU core device. The first matched ops table becomes global `rk_ops`; mixed hardware versions in one kernel instance are rejected.

Domain allocation creates a 4 KiB directory table, maps it for DMA, initializes locks and the attached-IOMMU list, and exposes page sizes from 4 KiB up to one page table worth of contiguous PTEs. Attach first detaches from identity, links the IOMMU into the domain list, and if the hardware is powered, enables hardware by stalling, force-resetting, programming DT address for all banks, zapping cache, enabling IRQs, and enabling paging. Detach switches to identity, removes from the list, and disables hardware if powered.

Mapping obtains or allocates the relevant page table under `dt_lock`, refuses remapping over a valid PTE, writes contiguous PTEs, flushes table cache lines, and zaps first/last IOVA lines to remove stale DTE/PTE cachelines. Unmap clears valid PTEs until it sees an invalid entry, flushes table entries, then zaps the unmapped IOVA range across all powered IOMMUs attached to the domain. IRQ handling powers/clocks the device if active, logs page-fault or bus-error status per bank, calls `report_iommu_fault()` unless identity-attached, zaps cache, clears page fault, and acknowledges interrupts.

## State And Persistence
Persistent state includes the domain DT page, lazily allocated PT pages, DMA mappings, attached IOMMU list, runtime PM device links, prepared clocks, and per-IOMMU current domain pointer. Hardware state includes DTE_ADDR, command/status, IRQ masks, page-fault address, and auto-gating registers. Page tables are freed during domain free after warning if still attached.

## Dependencies And Integration Points
The driver integrates with OF platform bindings `rockchip,iommu` and `rockchip,rk3568-iommu`, runtime PM, clock bulk APIs, DMA mapping, generic single-device IOMMU groups, device links from masters to the IOMMU device, and generic fault reporting.

## Risks
Global `rk_ops` prevents mixing v1/v2 descriptor formats in one running driver instance. Page-table physical address extraction assumes `phys_to_virt()` access to allocated tables. TLB zap uses first/last optimization on map and full per-page loop on unmap; stale intermediate cachelines are assumed not to matter on map. Runtime PM means many operations skip powered-off IOMMUs and rely on resume reprogramming. Fault IRQ logging dereferences page tables from hardware-reported addresses, so corrupted DTE_ADDR/PTE state can affect diagnostics.

## Test Signals
Probe on v1 and rk3568-compatible v2 hardware, map/unmap across 4 KiB to 4 MiB sizes, remap rejection, runtime suspend/resume with attached domain, IRQ fault injection for read/write and bus error, multi-bank register programming, device-link PM ordering, optional clock absence, and reset-disabled boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/rockchip-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/s390-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/s390-iommu.c

## Purpose
This file implements Linux IOMMU operations for IBM s390 zPCI devices. It builds and maintains zPCI DMA translation tables, registers IOAT state with firmware/hypervisor interfaces, handles blocking and identity domains, tracks devices attached to paging domains, and exposes translation refresh and counters.

## Important APIs, Types, And Functions
`struct s390_domain` embeds `struct iommu_domain`, a device list, counters, root DMA table pointer, list lock, RCU head, and root table origin type. Table helpers calculate region/segment/page indexes, set table origins, validate/invalidate entries, set protection bits, and recover child table pointers. Slab caches are created by `dma_alloc_cpu_table_caches()`, with allocation/free helpers for region and page tables.

Table walk/update functions include `dma_walk_rf_table()`, `dma_walk_rs_table()`, `dma_get_seg_table_origin()`, `dma_get_page_table_origin()`, `dma_walk_region_tables()`, `dma_walk_cpu_trans()`, and `dma_update_cpu_trans()`. Domain and device operations include `s390_domain_alloc_paging()`, `s390_domain_free()`, `s390_iommu_attach_device()`, `blocking_domain_attach_device()`, `s390_attach_dev_identity()`, `s390_iommu_probe_device()`, `s390_iommu_get_resv_regions()`, `s390_iommu_map_pages()`, `s390_iommu_unmap_pages()`, `s390_iommu_iova_to_phys()`, and TLB sync functions. Exported zPCI integration points are `zpci_iommu_register_ioat()`, `zpci_get_iommu_ctrs()`, `zpci_init_iommu()`, and `zpci_destroy_iommu()`.

## Control Flow
Subsystem init forces DAC for IOMMU DMA, derives the aperture from high memory and the `s390_iommu_aperture=` parameter, and creates table caches. Device probe accepts only PCI devices, validates zPCI DMA aperture, sets shadow-on-flush for devices needing TLB refresh, initializes the per-device domain lock, and starts every device in the blocking domain.

Paging-domain allocation chooses an RTX/RSX/RFX root type based on requested aperture, zPCI supported table modes, and device DMA bounds, then initializes a 4 KiB-only domain. Attach first moves the device to blocking, registers the new IOAT using the root table origin and zPCI DMA range, updates `zdev->dma_table` and `zdev->s390_domain`, and adds the device to the domain list under RCU. Identity attach also goes through blocking first, then registers a zero IOTA pass-through IOAT.

Map validates 4 KiB page size, aperture bounds, and alignment, then walks/allocates translation tables and installs valid PTEs, marking entries protected when `IOMMU_WRITE` is absent. Unmap invalidates PTEs, adds the range to the gather, and updates counters. TLB sync and flush walk the attached zPCI device list and call `zpci_refresh_trans()` or full refresh, handling hypervisor memory pressure in sync-map by falling back to full refresh.

## State And Persistence
Persistent state lives in multi-level zPCI translation tables allocated from kmem caches, per-domain attached-device RCU lists, counters, and per-device `zdev->s390_domain`/`dma_table`/IOMMU core objects. Domain freeing is RCU-delayed so readers of attached devices and tables can finish. Boot parameters persist in static aperture configuration.

## Dependencies And Integration Points
The driver depends on s390 zPCI architecture definitions and operations from `asm/pci_dma.h`, generic IOMMU APIs, IOMMU DMA helper state, RCU lists, and zPCI firmware/hypervisor calls such as `zpci_register_ioat()`, `zpci_unregister_ioat()`, and `zpci_refresh_trans()`.

## Risks
Attach uses blocking as a fail-safe before registering a new IOAT; failures after blocking leave DMA blocked. Table allocation is concurrent and uses `cmpxchg`, so all table-entry encoding and validity tests must be exact. Refresh operations can fail or require full refresh fallback under hypervisor pressure. Aperture calculations mutate `zdev->end_dma`, so configuration affects reserved regions and domain geometry. Some error propagation from IOAT registration is intentionally suppressed for device error/removal states.

## Test Signals
s390 boot with zPCI devices, strict/deferred flush modes, varying `s390_iommu_aperture`, attach to paging/identity/blocking domains, 4 KiB map/unmap and iova-to-phys, zPCI refresh counters, device removal/error state IOAT registration behavior, and table cleanup under RCU after detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/s390-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/sprd-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/sprd-iommu.c

## Purpose
This file implements the Unisoc/SPRD IOMMU driver. It provides a simple one-device IOMMU model with a flat page table over a 256 MiB aperture, hardware programming for EX and VAU IP versions, TLB update hooks, and platform-driver registration.

## Important APIs, Types, And Functions
`struct sprd_iommu_device` stores the attached domain, hardware version, fault-protection page, MMIO base, device, IOMMU core object, and optional gate clock. `struct sprd_iommu_domain` stores a page-table lock, embedded generic domain, coherent page-table VA/PA, and attached SPRD device. Register helpers are `sprd_iommu_write()`, `sprd_iommu_read()`, `sprd_iommu_update_bits()`, and `sprd_iommu_get_version()`.

Domain/hardware helpers include `sprd_iommu_pgt_size()`, `sprd_iommu_first_vpn()`, `sprd_iommu_vpn_range()`, `sprd_iommu_first_ppn()`, `sprd_iommu_default_ppn()`, `sprd_iommu_hw_en()`, and `sprd_iommu_cleanup()`. Generic IOMMU ops are `sprd_iommu_domain_alloc_paging()`, `sprd_iommu_attach_device()`, `sprd_iommu_map()`, `sprd_iommu_unmap()`, `sprd_iommu_sync_map()`, `sprd_iommu_sync()`, `sprd_iommu_iova_to_phys()`, `sprd_iommu_probe_device()`, and `sprd_iommu_of_xlate()`.

## Control Flow
Probe maps the register resource, allocates a coherent 4 KiB protection page used as the default fault target, registers the IOMMU core device, enables the optional gate clock, reads the hardware version, and stores it. OF xlate resolves the IOMMU platform device and stores its driver data in the client device.

Domain allocation creates a 4 KiB-page-only domain with a forced 0..256 MiB aperture. The first attach lazily allocates a coherent page table sized for the aperture, stores the device pointer, disables hardware, programs first PPN, first VPN, VPN range, default PPN, then re-enables hardware. Map writes sequential PPNs into the flat table under a spinlock. Unmap zeros entries. Sync writes the EX or VAU update register with all ones to clear the hardware TLB buffer. Cleanup frees the coherent table and disables hardware.

## State And Persistence
Persistent state consists of a coherent flat PPN table per attached domain, a coherent protection page per hardware device, the hardware version, and optional clock state. The hardware stores first VPN/range, first PPN, default PPN, enable/gate bits, and update registers.

## Dependencies And Integration Points
The driver integrates with OF platform matching `sprd,iommu-v1`, Linux IOMMU core, coherent DMA allocation, optional clocks, and generic single-device IOMMU groups.

## Risks
The hardware model supports one client per SPRD IOMMU; attaching a different domain reprograms the single hardware table. There is no identity or blocking domain implementation in this file. The flat table has no valid/protection bits in software, so remap detection is absent and zero means unmapped/default behavior. Map ignores `pgsize` directly and assumes generic core supplies 4 KiB pages. Fault handling is not present, relying on default PPN behavior.

## Test Signals
Probe with EX and VAU versions, optional clock present/absent, attach/map/unmap/sync for 4 KiB pages, aperture-boundary rejection, iova-to-phys lookup, domain cleanup on free, and behavior of the protection page on invalid translations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/sprd-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/sun50i-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/sun50i-iommu.c

## Purpose
This file implements the Allwinner sun50i H6/H616 IOMMU driver. It manages a two-level 32-bit page table, permission-domain encoding, TLB/PTW invalidation, reset/clock control, fault IRQ handling, and generic IOMMU domain operations.

## Important APIs, Types, And Functions
`struct sun50i_iommu` stores the IOMMU core object, register lock, device, MMIO base, reset, clock, current domain, and L2 page-table slab pool. `struct sun50i_iommu_domain` embeds the generic domain, refcount, L1 directory table, DMA address, and attached IOMMU pointer. Descriptor helpers include DTE/PTE index extraction, `sun50i_mk_dte()`, `sun50i_mk_pte()`, `sun50i_dte_is_pt_valid()`, `sun50i_pte_is_page_valid()`, and PTE authority-control decoding.

Cache and hardware helpers include `sun50i_table_flush()`, `sun50i_iommu_zap_iova()`, `sun50i_iommu_zap_ptw_cache()`, `sun50i_iommu_zap_range()`, `sun50i_iommu_flush_all_tlb()`, `sun50i_iommu_enable()`, `sun50i_iommu_disable()`, `sun50i_iommu_alloc_page_table()`, and `sun50i_dte_get_page_table()`. IOMMU core hooks include domain allocation/free, attach/detach/identity attach, map/unmap, iova-to-phys, TLB sync, probe-device, and OF xlate. Fault handling is in `sun50i_iommu_irq()`, `sun50i_iommu_handle_pt_irq()`, `sun50i_iommu_handle_perm_irq()`, and `sun50i_iommu_report_fault()`.

## Control Flow
Probe allocates the IOMMU, initializes the register lock, starts in identity domain, creates a DMA32 slab cache for L2 page tables, maps MMIO, gets IRQ/clock/reset, registers the IOMMU core device, and requests the IRQ. Domain allocation creates a 4096-entry L1 directory table in DMA32 memory, sets a 4 KiB page size bitmap, and forces a 32-bit aperture.

Attach increments the domain refcount, detaches any old domain through identity attach, DMA-maps the L1 table, stores cross-pointers, deasserts reset, enables the clock, programs TTB, TLB prefetch, bypass disable, interrupt mask, permission-domain access-control registers, flushes all TLB state, enables auto-gating, and enables the IOMMU. Detach frees every valid L2 page table, disables hardware, unmaps the L1 table, and clears the domain pointer.

Mapping rejects physical addresses above 4 GiB, lazily allocates or races to install a 1 KiB L2 page table, rejects remapping a valid PTE, writes a single 4 KiB PTE with authority index derived from `IOMMU_READ`/`IOMMU_WRITE`, flushes the entry, and reports the mapped size. Unmap clears one valid PTE and flushes it. TLB sync-map zaps selected IOVA and PTW-cache entries under the hardware lock; generic unmap sync flushes all TLBs.

Fault IRQ flow reads global and L1/L2 status under the register lock, classifies invalid L1/L2 page faults versus permission faults, reports through `report_iommu_fault()`, zaps the faulting range, clears interrupt status, resets affected masters, and releases reset for all masters.

## State And Persistence
Persistent state includes the domain L1 directory, slab-allocated DMA-mapped L2 tables, refcounted domain attachment, current hardware domain pointer, reset/clock handles, and hardware permission-domain configuration. Hardware-visible table entries are explicitly DMA-synchronized after updates.

## Dependencies And Integration Points
The driver uses OF platform compatibles `allwinner,sun50i-h6-iommu` and `allwinner,sun50i-h616-iommu`, Linux IOMMU core, reset and clock frameworks, DMA mapping, `iommu-pages` allocation helpers, generic single-device groups, and generic fault reporting.

## Risks
The driver supports only 32-bit IOVA/physical addresses and 4 KiB mappings. Attach error handling does not propagate the return from `sun50i_iommu_attach_domain()` in `sun50i_iommu_attach_device()`, so enable failures deserve scrutiny. The refcount starts at one and is incremented on attach, making detach/free lifetime behavior important to test. TLB range zapping invalidates selected boundary addresses and PTW cache lines, while unmap sync flushes all; correctness depends on hardware cache behavior. Some fault classification defaults to read when direction cannot be inferred.

## Test Signals
Probe on H6/H616 DT, attach/detach with reset and clock sequencing, map/unmap/iova-to-phys for 4 KiB pages, remap rejection, >4 GiB physical-address rejection, TLB/PTW invalidation timeout handling, permission fault direction tests for RD/WR/NONE authority indices, invalid L1/L2 fault tests, runtime behavior with multiple masters, and domain refcount/lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/sun50i-iommu.c -->
