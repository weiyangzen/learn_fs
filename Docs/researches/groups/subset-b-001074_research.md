# subset-b-001074 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/generic.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/generic.c

## Purpose

`generic.c` is the shared AGPGART backend implementation used by chipset-specific AGP bridge drivers. It owns generic `struct agp_memory` allocation/freeing, GATT creation and teardown, bind/unbind operations, AGP mode negotiation, device command programming, cache flushing, and generic AGP 3.x register setup. The file is not Ceph-specific despite the source tree prefix; it is Linux kernel graphics aperture infrastructure.

## Important APIs, Types, And Functions

- Global state: `agp_gatt_table` exposes the active GATT kernel table pointer, and `agp_memory_reserved` reduces advertised aperture capacity for reserved regions.
- Key and memory lifecycle: `agp_free_key()`, `agp_create_memory()`, `agp_allocate_memory()`, `agp_free_memory()`, `agp_generic_alloc_user()`, `agp_alloc_page_array()`, and `agp_free_page_array()` allocate keyed `struct agp_memory` objects and backing page arrays.
- Binding APIs: `agp_bind_memory()` and `agp_unbind_memory()` call the current bridge driver's `insert_memory` and `remove_memory`, update `is_bound`/`pg_start`, and maintain `bridge->mapped_list`.
- GATT helpers: `agp_generic_create_gatt_table()`, `agp_generic_free_gatt_table()`, `agp_generic_insert_memory()`, and `agp_generic_remove_memory()` implement a single-level GATT filled with scratch-page entries.
- Page helpers: `agp_generic_alloc_page()`, `agp_generic_alloc_pages()`, `agp_generic_destroy_page()`, and `agp_generic_destroy_pages()` manage DMA32 zeroed pages, AGP mapping attributes, refcounts, and `current_memory_agp`.
- Mode negotiation: `agp_collect_device_status()`, `agp_generic_enable()`, `agp_device_command()`, `get_agp_version()`, `agp_v2_parse_one()`, and `agp_v3_parse_one()` sanitize requested modes against bridge and VGA capabilities.
- AGP 3.x defaults: `agp3_generic_fetch_size()`, `agp3_generic_configure()`, `agp3_generic_tlbflush()`, `agp3_generic_cleanup()`, and exported `agp3_generic_sizes`.
- Utility hooks: `global_cache_flush()`, `agp_generic_mask_memory()`, `agp_generic_type_to_mask_type()`, and `agp_generic_find_bridge()`.

## Control Flow

Chipset modules allocate and register an `agp_bridge_data` whose `agp_bridge_driver` points back to these helpers. During bridge add, the backend fetches aperture size, allocates scratch/GATT resources, configures chipset registers, and later clients allocate memory via `agp_allocate_memory()`. Binding checks bounds and occupancy, flushes CPU caches if needed, writes masked page addresses into GATT slots, posts the final read, then calls the bridge TLB flush hook. Unbinding restores scratch-page entries and flushes again.

AGP enable flows through `agp_generic_enable()`: it reads bridge AGP status, finds an AGP VGA device, intersects requested mode with bridge/card capabilities, applies bridge errata flags, sets `AGPSTAT_AGP_ENABLE`, optionally invokes `agp_3_5_enable()` for AGP 3.5 isochronous setup, and writes commands to all AGP-capable PCI devices.

## State And Persistence Behavior

Persistent runtime state lives in `agp_bridge`, `agp_bridges`, each `agp_bridge_data`, `agp_memory` objects, the allocated GATT pages, page cache attributes, PCI config registers, and per-memory flags such as `is_flushed` and `is_bound`. The file updates `atomic_t current_memory_agp` as pages are allocated/freed and uses `mapped_lock` to track bound regions. Hardware-visible persistence is the GATT contents and AGP command/config state until cleanup, suspend reconfiguration, or module removal.

## Dependencies And Integration Points

This file depends on `agp.h`, `<linux/agp_backend.h>`, PCI config accessors, DMA/page APIs, `set_memory_uc/wb` on x86, and architecture AGP cache helpers. All chipset files in this work item call into it through `struct agp_bridge_driver` callbacks. User-visible AGP ioctls and DRM paths ultimately rely on these exported symbols for memory allocation, mode setup, and bind/unbind behavior.

## Risks And Edge Cases

Single-level generic GATT routines reject `LVL2_APER_SIZE`, so two-level chipsets must provide their own implementation. Many bounds checks explicitly guard integer overflow, but consumers still depend on correct `current_size` metadata. GATT entries are noted as unable to encode addresses over 4 GB in some paths. Global `agp_bridge` usage means this code is effectively written around a singleton bridge model even though bridge structs are passed through several APIs. Cache attribute transitions and scratch-page DMA visibility are high-risk areas, especially on non-x86 paths and during partial allocation failures.

## Test Signals

Build with representative AGP drivers enabled, boot/probe on supported hardware or emulation, and exercise allocation, bind, unbind, and free through AGP users. Useful signals include correct aperture reporting via `agp_copy_info()`, no `-EBUSY` on empty GATT ranges, successful TLB flushes, restored scratch entries after unbind, correct `current_memory_agp` accounting after error paths, and AGP mode logs matching bridge/card capabilities. Static analysis should focus on overflow, lock coverage around `mapped_list`, cache attribute restoration, and failure cleanup in GATT allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.c

## Purpose

`intel-agp.c` is the legacy Intel AGPGART PCI host-bridge driver. It supports pre-GEM Intel AGP chipsets and selects either a true AGP bridge driver or, for integrated GMCH graphics handled by `intel-gtt.c`, a fake AGP/GTT path.

## Important APIs, Types, And Functions

- Aperture size readers: `intel_fetch_size()`, `intel_8xx_fetch_size()`, and `intel_815_fetch_size()` parse Intel APSIZE variants.
- TLB and cleanup hooks: `intel_tlbflush()`, `intel_8xx_tlbflush()`, `intel_820_tlbflush()`, `intel_cleanup()`, `intel_8xx_cleanup()`, and `intel_820_cleanup()`.
- Chipset configuration hooks: `intel_configure()`, `intel_815_configure()`, `intel_820_configure()`, `intel_840_configure()`, `intel_845_configure()`, `intel_850_configure()`, `intel_860_configure()`, `intel_830mp_configure()`, and `intel_7505_configure()`.
- Static tables: Intel aperture-size arrays, `intel_generic_masks`, multiple `agp_bridge_driver` instances, and `intel_agp_chipsets[]`.
- PCI integration: `agp_intel_probe()`, `agp_intel_remove()`, `agp_intel_resume()`, `agp_intel_pci_table[]`, and `agp_intel_pci_driver`.

## Control Flow

The module registers `agpgart-intel` unless `agp_off` is set. Probe allocates a bridge, records the AGP capability offset, first calls `intel_gmch_probe()` to allow integrated graphics GTT ownership, then falls back to matching legacy host bridge IDs in `intel_agp_chipsets[]`. For real AGP paths it may assign BAR0 if firmware left the aperture unassigned, enables the PCI device, reads the mode register, stores bridge drvdata, and calls `agp_add_bridge()`. Configure hooks program APSIZE, aperture bus base, ATTBASE/GATT pointer, AGPCTRL, chipset enable bits, and error status registers. Resume simply reruns `bridge->driver->configure()`.

## State And Persistence Behavior

State is mostly stored in `agp_bridge_data`: selected driver, capability offset, current/previous aperture sizes, `gart_bus_addr`, `gatt_bus_addr`, mode, and optional `apbase_config` preservation for i845-style reconfiguration. Hardware state persists in Intel PCI config registers until cleanup or resume reprogramming. The driver relies on `generic.c` for GATT memory state and page accounting.

## Dependencies And Integration Points

The file depends on `agp.h`, `intel-agp.h`, generic AGP helpers, PCI IDs, and `<drm/intel/intel-gtt.h>`. Its main integration point is `intel_gmch_probe()`/`intel_gmch_remove()` in `intel-gtt.c`, which intercept integrated-GPU host bridges. It registers with the kernel PCI core and exports no direct APIs of its own.

## Risks And Edge Cases

The i815 path rejects GATT bus addresses that exceed reserved ATTBASE bits. Firmware may omit aperture BAR assignment, so probe contains early resource repair before `pci_enable_device()`. Several chipsets have unique enable and error registers, making table-to-driver selection high risk. GMCH probing can change the bridge driver path entirely; ordering with DRM/i915 and refcounted GTT ownership matters. Resume assumes `bridge->driver` is valid and reconfiguration is sufficient after power management.

## Test Signals

Compile with `CONFIG_AGP_INTEL`; verify `agpgart-intel` probes expected PCI IDs and logs the selected chipset. Hardware tests should check aperture BAR assignment, APSIZE restoration on cleanup, GATT ATTBASE programming, suspend/resume reconfiguration, and no regression in the integrated GMCH fake-AGP path. Static review should compare `agp_intel_pci_table[]` against `intel_agp_chipsets[]` and `intel_gtt_chipsets[]` for intentional coverage gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.h -->
# sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.h

## Purpose

`intel-agp.h` is the shared Intel AGP/GTT register and PCI ID definition header used by `intel-agp.c` and `intel-gtt.c`. It centralizes chipset-specific PCI config offsets, MMIO offsets, stolen-memory bitfields, PGETBL controls, GTT PTE flags, and older Intel host/GPU device IDs.

## Important APIs, Types, And Functions

The file defines no functions or structs. Its important definitions include:

- AGP config offsets: `INTEL_APSIZE`, `INTEL_ATTBASE`, `INTEL_AGPCTRL`, `INTEL_NBXCFG`, and chipset-specific error/status registers.
- i810/i830/i915/G33/G4x/i965 GTT and memory control bits: `I810_PGETBL_CTL`, `I810_PTE_*`, `I830_GMCH_*`, `I855_GMCH_GMS_*`, `I965_PGETBL_*`, `G33_GMCH_SIZE_*`, `G4x_GMCH_SIZE_*`, and `GFX_FLSH_CNTL`.
- BAR indexes: `I810_GMADR_BAR`, `I810_MMADR_BAR`, `I915_MMADR_BAR`, and `I915_PTE_BAR`.
- Intel PCI device IDs not supplied by generic PCI headers for host bridges and integrated graphics.

## Control Flow

There is no runtime control flow. `intel-agp.c` uses the PCI config offsets and IDs while probing/configuring legacy AGP host bridges. `intel-gtt.c` uses the MMIO offsets, PTE flags, stolen memory masks, and integrated graphics IDs to choose GTT drivers and program/read global GTT entries.

## State And Persistence Behavior

The header stores no state. Its constants describe persistent hardware registers and ABI-level device IDs. Incorrect constants would cause runtime state in PCI config space or MMIO GTT tables to be read or written incorrectly.

## Dependencies And Integration Points

The header is included after `agp.h` in both Intel implementation files. It integrates with Linux PCI ID matching, AGP bridge setup, DRM Intel GTT exports, stolen-memory detection, chipset flush setup, and PGETBL restoration on resume.

## Risks And Edge Cases

Several values encode hardware quirks, such as i815 ATTBASE reserved bits, G33/G4x VT-enabled GTT sizes, and i965 high-address PTE packing. A wrong bit mask can produce silent aperture size misdetection or GTT corruption. The header mixes host bridge IDs and graphics device IDs, so additions must preserve which table consumes each macro.

## Test Signals

Compile both Intel AGP and GTT paths. Validate probe tables resolve the intended host/GPU pairs, GTT size detection matches hardware documentation, stolen-memory logs match BIOS setup, and PTE read/write helpers round-trip expected physical addresses on i830 and i965-style entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-gtt.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/intel-gtt.c

## Purpose

`intel-gtt.c` implements Intel GMCH global GTT management for older integrated graphics. Historically it also exposes GTT mapping through a fake AGP bridge so old userspace Intel graphics stacks can bind pages through AGPGART. Modern DRM/i915 can call the exported GMCH helpers directly.

## Important APIs, Types, And Functions

- `struct intel_gtt_driver` abstracts chipset generation, DMA mask, setup/cleanup, PTE read/write, flag validation, and chipset flush hooks.
- `intel_private` stores the selected driver, bridge/GPU PCI devices, MMIO mappings, GTT base and sizes, scratch page, stolen memory, flush page resource, DMA/IOMMU state, and refcount.
- Setup and cleanup: `i810_setup()`, `i830_setup()`, `i9xx_setup()`, `intel_gtt_init()`, `intel_gtt_cleanup()`, `intel_gtt_setup_scratch_page()`, and `intel_gtt_teardown_scratch_page()`.
- PTE operations: `i810_write_entry()`, `i830_write_entry()`, `i965_write_entry()`, and matching read helpers.
- Exported DRM-facing APIs: `intel_gmch_probe()`, `intel_gmch_remove()`, `intel_gmch_enable_gtt()`, `intel_gmch_gtt_insert_page()`, `intel_gmch_gtt_insert_sg_entries()`, `intel_gmch_gtt_read_entry()`, `intel_gmch_gtt_clear_range()`, `intel_gmch_gtt_get()`, and `intel_gmch_gtt_flush()`.
- Fake AGP callbacks under `CONFIG_AGP_INTEL`: `intel_fake_agp_configure()`, `intel_fake_agp_insert_entries()`, `intel_fake_agp_remove_entries()`, `intel_fake_agp_alloc_by_type()`, and the `intel_fake_agp_driver`.

## Control Flow

`intel_gmch_probe()` selects an integrated graphics device either from an explicit GPU PCI device or by scanning known IDs. It optionally installs `intel_fake_agp_driver` into an AGP bridge for gen1 integrated chipsets, refcounts shared ownership, pins bridge/GPU devices, sets DMA masks for AGP callers, and calls `intel_gtt_init()`. Initialization maps chipset registers, determines mappable and total GTT entries, saves PGETBL state, maps the GTT WC if safe, detects stolen memory, allocates a scratch page, and records the graphics aperture bus address.

GTT insertion writes per-page DMA addresses into chipset-specific PTE format, posts the write, and runs a chipset flush hook when present. Fake AGP insertion lazily clears non-stolen mappable GTT on first access, validates flags and bounds, optionally DMA maps scatterlists when VT-d requires the DMA API, and stores SG state for unmap on removal. Removal clears entries back to the scratch page and unmaps SG mappings if needed.

## State And Persistence Behavior

`intel_private` is module-global and refcounted across fake AGP and DRM callers. Persistent hardware state includes PGETBL enable/base, GGTT PTE contents, chipset flush page resources, stolen-memory layout, and scratch-page mappings. GTT entries persist until explicitly cleared, GPU reset, or driver cleanup. `clear_fake_agp` ensures old AGP users do not inherit stale firmware or stolen-memory mappings beyond the stolen region.

## Dependencies And Integration Points

The file depends on `intel-agp.h`, `agp.h`, PCI resource APIs, DMA mapping, optional Intel IOMMU detection, MMIO mapping, and DRM's `drm/intel/intel-gtt.h` exported interface. It is called by `intel-agp.c` during Intel host-bridge probe and by DRM/i915 for direct GTT access. It integrates with chipset-specific cache flush mechanisms, CPU cache attribute APIs, and resource allocation for Intel flush pages.

## Risks And Edge Cases

The code contains a likely stale debug statement in `intel_gtt_unmap_memory()` referencing `mem` in a `DBG()` macro without a local `mem`; this is hidden unless AGP debug expands the macro. Refcounted cleanup is split: `intel_gmch_remove()` tears down scratch/device refs but does not call the full `intel_gtt_cleanup()` path unless fake AGP cleanup runs, so ownership order matters. VT-d on Ironlake disables WC mappings and can require DMA API mappings before inserting pages. GTT total and mappable size detection varies by generation and BIOS GMCH bits; wrong decoding can expose out-of-range entries. PTE packing differs between i830 and i965-style hardware, including high-address bit shifting.

## Test Signals

Build with and without `CONFIG_AGP_INTEL` and `CONFIG_INTEL_IOMMU`. Probe tests should confirm chipset selection, GTT total/mappable logs, stolen-memory detection, scratch-page setup, and DMA mask configuration. Functional tests should insert, read back, clear, and flush GTT entries for single pages and SG tables. Suspend/resume should verify `intel_gmch_enable_gtt()` restores PGETBL. Static tests should compile AGP debug enabled, audit refcount cleanup, and check GTT bounds for fake AGP insertion/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/intel-gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/isoch.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/isoch.c

## Purpose

`isoch.c` implements generic AGP 3.5 node setup for isochronous transfer support. It enumerates AGP 3.x devices behind a bridge, validates that they are compatible with AGP 3.x electrical mode, and allocates isochronous bandwidth/request-queue resources or falls back to non-isochronous queue allocation.

## Important APIs, Types, And Functions

- `struct agp_3_5_dev` tracks a candidate device, its AGP capability offset, and maximum bandwidth.
- `agp_3_5_dev_list_sort()` and `agp_3_5_dev_list_insert()` order devices by `maxbw`.
- `agp_3_5_isochronous_node_enable()` computes ISOCH_N, ISOCH_Y, and request queue allocations for target and master devices.
- `agp_3_5_nonisochronous_node_enable()` divides target request queue slots across masters.
- `agp_3_5_enable()` is the exported entry from generic AGP enable logic.

## Control Flow

`agp_generic_enable()` calls `agp_3_5_enable()` for AGP bridges with major version >= 3 and minor >= 5. The function reads target status, exits if isochronous support is not present, builds a list of AGP-capable display/multimedia devices, verifies each is AGP 3.x and in AGP 3.x mode, and then attempts isochronous setup. If bandwidth, ISOCH_N, or request queue capacity cannot satisfy all devices, it logs and falls back to non-isochronous queue partitioning.

## State And Persistence Behavior

All software lists and allocation arrays are temporary. Persistent effects are PCI config writes to target/master `AGPNICMD` and `AGPCMD` fields, which set payload size, isochronous transaction count, and request queue depth until reset or reconfiguration.

## Dependencies And Integration Points

The file depends on `agp.h`, PCI enumeration/config access, list helpers, and AGP register definitions from the private backend header. It is tightly integrated with `generic.c` mode negotiation and only runs during AGP enable for AGP 3.5-capable bridges.

## Risks And Edge Cases

The code assumes at least one eligible AGP master when dividing request queue slots; a bridge with isochronous support but no collected devices would risk division by zero. Enumeration scans all PCI devices and filters by class/capability rather than strictly by bus topology, relying on comments and class filtering to avoid unrelated devices. Resource allocation is approximate: it divides target resources evenly and gives remainders to the last sorted device. Capability walking and AGP 2.x rejection are critical to avoid programming incompatible devices.

## Test Signals

Useful signals include AGP 3.5 hardware logs, successful enable with multiple AGP 3.x masters, fallback logs when isochronous constraints are exceeded, and post-enable PCI config reads showing expected `AGPNICMD`/`AGPCMD` fields. Static tests should check `ndevs` zero handling, list cleanup on allocation failure, and capability-walk bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/isoch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/nvidia-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/nvidia-agp.c

## Purpose

`nvidia-agp.c` is the AGPGART bridge driver for NVIDIA nForce and nForce2 chipsets. It handles NVIDIA-specific aperture setup, AMD K7 IORR programming, ATTBASE directory programming, aperture MMIO mapping for TLB flushes, and adjusted insertion/removal for apertures below 64 MB.

## Important APIs, Types, And Functions

- `nvidia_private` stores secondary PCI functions, mapped aperture pointer, active entry count, page offset, and write-buffer control mask.
- `nvidia_fetch_size()`, `nvidia_configure()`, `nvidia_cleanup()`, and `nvidia_tlbflush()` implement chipset hooks.
- `nvidia_init_iorr()` programs AMD K7 IORR MSRs for the AGP aperture.
- `nvidia_insert_memory()` and `nvidia_remove_memory()` override generic GATT operations to account for NVIDIA page offset/active entries.
- `agp_nvidia_probe()`, `agp_nvidia_remove()`, `agp_nvidia_resume()`, and the PCI driver/table provide module integration.

## Control Flow

Probe locates required companion PCI functions `(0,1)`, `(0,2)`, and `(30,0)`, validates AGP capability, sets a chipset-specific write-buffer-control mask, allocates a bridge, and registers it. Configure writes APSIZE, aperture base/limit into multiple functions, programs CPU IORR, computes active entries and offset for sub-64 MB apertures, writes up to eight ATTBASE directory pointers, enables GART/GTLB control, and maps the aperture. Insert checks type and bounds against active entries minus reserved memory, verifies scratch/empty GATT slots at the NVIDIA offset, writes masked page entries, and flushes.

## State And Persistence Behavior

The driver persists companion PCI device references until module cleanup, writes NVIDIA GART state into PCI config registers, maps 33 pages of the aperture for flush reads, and stores GATT offsets in `nvidia_private`. It relies on generic AGP bridge state and allocated GATT pages. Cleanup disables GART/GTLB, unmaps aperture space, restores previous APSIZE, and reinitializes IORR for the previous aperture.

## Dependencies And Integration Points

Dependencies include x86 MSR access, PCI config/resource APIs, `agp.h`, generic AGP allocation/GATT helpers, and the global `agp_memory_reserved`. The file integrates with the AGP core through `nvidia_driver` callbacks and with CPU memory type/range behavior through AMD K7 IORR registers.

## Risks And Edge Cases

Missing companion functions abort probe. IORR programming is CPU-specific and can fail if no free IORR exists. Sub-64 MB apertures require special `pg_offset`; generic insertion would map the wrong GATT area. TLB flush waits up to three seconds on write-buffer-control bits and then uses repeated aperture reads, so hardware hangs or bad aperture mappings are visible. Error paths in probe can leave acquired companion device refs until module cleanup rather than immediate release.

## Test Signals

Test by probing nForce/nForce2 hardware, validating all companion functions are found, aperture base/limit registers match BAR resources, IORR setup succeeds, and 32 MB aperture insertion targets the correct offset. Exercise bind/unbind under load and watch for TLB flush timeout logs. Suspend/resume should re-run configuration without stale mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/nvidia-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/parisc-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/parisc-agp.c

## Purpose

`parisc-agp.c` implements HP Quicksilver AGPGART support for PA-RISC systems. It shares the SBA IOMMU page directory, discovers a Pluto/Quicksilver platform path, creates a fake PCI bridge device, and exposes a fixed-size AGP aperture whose GATT entries are PA-RISC I/O PDIR entries.

## Important APIs, Types, And Functions

- `parisc_agp_info` stores IOC/LBA MMIO bases, AGP capability offset, shared GATT pointer, GART base/size, I/O page size, and I/O pages per kernel page.
- `parisc_agp_fetch_size()`, `parisc_agp_configure()`, `parisc_agp_tlbflush()`, `parisc_agp_create_gatt_table()`, and `parisc_agp_free_gatt_table()` implement bridge callbacks.
- `parisc_agp_insert_memory()` and `parisc_agp_remove_memory()` write multiple I/O PDIR entries per kernel page when required.
- `parisc_agp_mask_memory()` builds a valid SBA PDIR entry including coherent index bits.
- `parisc_agp_enable()` performs PA-RISC MMIO AGP command programming.
- `agp_ioc_init()`, `agp_lba_init()`, `parisc_agp_setup()`, `find_quicksilver()`, and `parisc_agp_init()` handle platform discovery.

## Control Flow

Module init finds a Pluto SBA device and a child Quicksilver LBA. IOC init reads IOTLB page-size configuration, computes the GART window at the end of Pluto IOVA space, locates the shared PDIR, and requires an `SBA_AGPGART_COOKIE` reservation. LBA init locates AGP capability registers. Setup allocates a fake PCI device, allocates an AGP bridge with the PA-RISC driver, and registers it. Insert converts AGP page starts into I/O page starts, verifies empty PDIR slots, writes endian-correct masked entries, flushes each entry with `asm_io_fdc()`, and triggers IOC TLB invalidation.

## State And Persistence Behavior

Software state is the single `parisc_agp_info` instance and bridge registration. Hardware-visible state is shared SBA IOMMU PDIR content and IOC/LBA registers. `free_gatt_table()` restores the cookie in the first GATT entry rather than freeing memory, because the table belongs to the IOMMU. The driver sets `cant_use_aperture` to indicate CPU aperture access limitations.

## Dependencies And Integration Points

This file depends on PA-RISC platform headers, `sba_iommu`/rope platform structures, IOC register definitions, AGP core helpers, and PCI-style AGP command conventions. It integrates platform discovery rather than a normal PCI driver registration path.

## Risks And Edge Cases

Incorrect IOTLB page-size decoding or missing cookie disables the driver. For I/O page sizes smaller than kernel pages, insertion fans out each page into multiple entries, so off-by-one bounds are high impact. The driver assumes shared PDIR layout and Pluto constants. Endianness and coherent-index packing in `parisc_agp_mask_memory()` must match hardware exactly. `parisc_agp_init()` ignores the return from `parisc_agp_setup()` and returns zero once a Quicksilver path is found, which can hide setup failure from module init.

## Test Signals

Boot on PA-RISC Pluto/Quicksilver hardware, confirm GART size and sysfs/AGP registration, verify missing cookie disables support, bind/unbind memory and inspect PDIR entries, and check IOC `IOC_PCOM` TLB flushes complete. Static review should cover `parisc_agp_setup()` error propagation, fake PCI device lifetime, and I/O page fanout arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/parisc-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/sis-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/sis-agp.c

## Purpose

`sis-agp.c` is the AGPGART PCI driver for SiS host bridges. It supports older SiS AGP setup and can switch to generic AGP 3.x routines for bridges that advertise sufficiently new AGP versions or when forced by module parameter.

## Important APIs, Types, And Functions

- Module parameters: `agp_sis_force_delay` enables a delayed-enable workaround, and `agp_sis_agp_spec` forces SiS-specific or generic AGP3 setup.
- Core hooks: `sis_fetch_size()`, `sis_configure()`, `sis_cleanup()`, `sis_tlbflush()`, and `sis_delayed_enable()`.
- `sis_get_driver()` mutates `sis_driver` based on chipset workarounds and AGP version.
- PCI integration: `agp_sis_probe()`, `agp_sis_remove()`, `agp_sis_resume()`, PCI ID table, and `agp_sis_pci_driver`.

## Control Flow

Probe validates the AGP capability, allocates a bridge using `sis_driver`, reads AGP version/mode, calls `sis_get_driver()` to apply delay or AGP3 behavior, and registers the bridge. The SiS configure path programs TLB control, records aperture bus base, writes ATTBASE, and sets APSIZE. The delayed-enable path writes AGP commands to each AGP device and sleeps after programming the bridge on broken chipsets to avoid a transient rate-change failure.

## State And Persistence Behavior

The selected driver state is global because `sis_driver` is a mutable static structure. Hardware state persists in SiS PCI config registers `SIS_TLBCNTRL`, `SIS_ATTBASE`, `SIS_APSIZE`, and `SIS_TLBFLUSH`. Bridge state and GATT pages are managed by generic AGP helpers.

## Dependencies And Integration Points

The driver depends on Linux PCI IDs, AGP backend helpers, generic AGP3 helpers, and module parameters. It integrates with the AGP core through `agp_bridge_driver` callbacks and uses generic GATT insertion/removal.

## Risks And Edge Cases

Mutating the global `sis_driver` during probe can affect later devices if multiple SiS bridges existed. The AGP3 switch changes `size_type` to `U16_APER_SIZE`, but the `via`-style mismatch risk is avoided here because it points at `agp3_generic_fetch_size()`. Delay workaround selection depends on a short broken-chipset list unless forced. Resume calls the current global driver's configure method, so per-device configuration could be wrong after global mutation.

## Test Signals

Compile and probe supported SiS IDs, verify `agp_sis_agp_spec` modes select the intended callbacks, check delayed-enable logs and 10 ms bridge delay on 648/746 or forced mode, and validate bind/unbind through generic GATT routines. Static review should flag global driver mutation if multi-device support is relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/sis-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/sworks-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/sworks-agp.c

## Purpose

`sworks-agp.c` implements ServerWorks AGPGART support using a two-level GATT. It allocates a page directory plus per-directory GATT pages, maps ServerWorks MMIO registers, configures AGP aperture and caching behavior, and provides two-level insertion/removal and TLB flush hooks.

## Important APIs, Types, And Functions

- `struct serverworks_page_map` holds a real page and write-combining/uncached remapped pointer.
- `serverworks_private` tracks the secondary ServerWorks device, MMIO registers, GATT page array, scratch directory, and config register offsets.
- GATT lifecycle: `serverworks_create_page_map()`, `serverworks_free_page_map()`, `serverworks_create_gatt_pages()`, `serverworks_free_gatt_pages()`, `serverworks_create_gatt_table()`, and `serverworks_free_gatt_table()`.
- Runtime hooks: `serverworks_fetch_size()`, `serverworks_configure()`, `serverworks_cleanup()`, `serverworks_tlbflush()`, `serverworks_insert_memory()`, `serverworks_remove_memory()`, and `serverworks_agp_enable()`.
- PCI integration: `agp_serverworks_probe()`, `agp_serverworks_remove()`, table and module init/exit.

## Control Flow

Probe accepts documented ServerWorks HE/LE-style devices, rejects CNB20HE, finds function 1, validates 64-bit aperture/MMIO upper bits are zero, sets register offsets, allocates a bridge, and registers it. GATT creation allocates a page directory, a scratch directory filled with scratch entries, points all directory entries to the scratch directory, then allocates real second-level pages and installs their addresses. Configure maps MMIO, enables GART cache behavior, writes GATT base, sets command bits, enables AGP on the secondary device, flushes, reads AGP capability/mode, disables chipset caching bits, and enables a feature bit. Insertion maps AGP page offsets through directory/page offsets to second-level tables and writes masked entries.

## State And Persistence Behavior

Persistent state includes the allocated two-level GATT pages, scratch directory, `serverworks_private.registers` MMIO mapping, selected companion PCI device, and ServerWorks config/MMIO register contents. Removal restores entries to scratch values and flushes before and after clearing. Cleanup unmaps MMIO, while bridge teardown frees GATT pages.

## Dependencies And Integration Points

The file depends on x86 `set_memory_uc/wb`, PCI resource/config APIs, generic AGP memory helpers, and global AGP bridge state. It integrates with the AGP core as an `LVL2_APER_SIZE` driver because `generic.c` cannot manage two-level tables.

## Risks And Edge Cases

Page-map creation notes missing PCI posting flush after filling entries. Two-level indexing depends on `gart_bus_addr`; incorrect aperture base produces wrong directory selection. Probe rejects 64-bit upper bits rather than handling true 64-bit addresses. TLB flush loops can stall up to three seconds each for post and directory flush. Error cleanup must free partially allocated page maps and release companion device refs.

## Test Signals

Probe supported ServerWorks hardware and validate MMIO mapping, GATT base programming, and AGP enable logs. Bind/unbind across directory boundaries to test `GET_PAGE_DIR_IDX()`/`GET_GATT_OFF()` arithmetic. Watch for TLB post/dir flush timeout logs. Static tests should inspect partial allocation cleanup and resource lifetime around `svrwrks_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/sworks-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/uninorth-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/uninorth-agp.c

## Purpose

`uninorth-agp.c` implements Apple UniNorth and U3 AGPGART support for PowerPC systems. It handles Apple-specific GART registers, GATT allocation with non-cacheable mappings, revision-specific AGP command errata, optional platform power-management hooks, and module-parameter aperture sizing.

## Important APIs, Types, And Functions

- Global controls: `uninorth_rev`, `is_u3`, `scratch_value`, and module parameter `aperture`.
- Core hooks: `uninorth_fetch_size()`, `uninorth_configure()`, `uninorth_cleanup()`, `uninorth_tlbflush()`, `uninorth_insert_memory()`, `uninorth_remove_memory()`, and `uninorth_agp_enable()`.
- PM hooks under `CONFIG_PM`: `agp_uninorth_suspend()` and `agp_uninorth_resume()`.
- GATT lifecycle: `uninorth_create_gatt_table()`, `uninorth_free_gatt_table()`, `null_cache_flush()`, and `uninorth_priv.pages_arr`.
- Driver descriptors: `uninorth_agp_driver`, `u3_agp_driver`, `uninorth_agp_device_ids[]`.
- PCI integration: `agp_uninorth_probe()`, `agp_uninorth_remove()`, table and module init/exit.

## Control Flow

Probe matches Apple host bridges, locates AGP capability, identifies known UniNorth/U3 IDs, reads Open Firmware `device-rev` from `uni-n` or `u3`, registers platform AGP PM callbacks, allocates an AGP bridge, chooses U3 or UniNorth driver, sets fast-write errata, reads mode, and registers the bridge. GATT creation selects aperture size from the module parameter or default, allocates contiguous pages, marks pages reserved, creates a non-cacheable `vmap`, computes a chipset-specific scratch entry, and fills all GATT slots. Configure writes GART base/size, forces `gart_bus_addr` to zero for a hardware quirk, writes AGP base, and sets U3 dummy page if needed.

## State And Persistence Behavior

State includes GATT pages, the non-cacheable mapping, scratch value, revision flags, and bridge private data used during suspend/resume to save AGP command state. Hardware state persists in UniNorth/U3 GART and AGP command registers until cleanup or PM transitions. The driver marks `cant_use_aperture`, reflecting architecture/hardware access constraints.

## Dependencies And Integration Points

Dependencies include PowerPC Open Firmware APIs, `asm/uninorth.h`, `pmac_feature` AGP PM registration, `vmap`, cache flush primitives, and generic AGP helpers. It integrates with AGP core bridge registration and with video-driver-driven PM callbacks rather than standard PCI PM.

## Risks And Edge Cases

The driver intentionally sets `gart_bus_addr` to zero due to a UniNorth aperture bug, which is surprising to generic callers. U3 and older UniNorth scratch entry formats differ. Revision-specific errata disable AGP 4x or cap request depth. GATT allocation failure must unreserve/free pages and `pages_arr`; error path currently frees pages without clearing `PageReserved` if failure happens after marking but before `vmap` success. PM callbacks assume only one suspend is active via `dev_private_data`.

## Test Signals

On supported Apple PowerPC hardware, verify aperture module parameter parsing, GATT non-cacheable mapping creation, AGP enable command retry success, revision-specific logs/behavior, and suspend/resume through registered PM callbacks. Bind/unbind should show scratch-value occupancy checks and no stale GATT entries. Static review should cover GATT allocation cleanup after partial reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/uninorth-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/via-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/via-agp.c

## Purpose

`via-agp.c` is the AGPGART driver for VIA host bridges. It supports legacy AGP register layouts and an AGP3 register layout selected by `VIA_AGPSEL`, while using generic GATT allocation and memory insertion/removal.

## Important APIs, Types, And Functions

- Legacy hooks: `via_fetch_size()`, `via_configure()`, `via_cleanup()`, and `via_tlbflush()`.
- AGP3 hooks: `via_fetch_size_agp3()`, `via_configure_agp3()`, `via_cleanup_agp3()`, and `via_tlbflush_agp3()`.
- Driver descriptors: `via_driver` and `via_agp3_driver`.
- Device mapping: `via_agp_device_ids[]` and ordered `agp_via_pci_table[]`.
- Probe helpers: `check_via_agp3()`, `agp_via_probe()`, `agp_via_remove()`, and `agp_via_resume()`.

## Control Flow

Module init registers a PCI host-bridge driver. Probe uses the PCI ID table index to print a chipset name, allocates a bridge with the legacy driver, applies a KT400-disguised-as-KT266 check, reads AGP version, and calls `check_via_agp3()` for AGP3-capable bridges. Legacy configure writes APSIZE, records aperture bus base, enables GART control, and writes ATTBASE with low enable bits. AGP3 configure writes the AGP3 ATTBASE and enables GTLB/aperture bits in `VIA_AGP3_GARTCTRL`. Resume reruns the configure method matching the selected driver.

## State And Persistence Behavior

Persistent bridge state is standard `agp_bridge_data`; chipset state is in VIA PCI config registers. GATT allocation and entry state are handled by generic AGP helpers. Driver selection is per bridge pointer, unlike the mutable-global pattern used by SiS.

## Dependencies And Integration Points

The file depends on `agp.h`, PCI IDs, and generic AGP3 size tables/helpers for memory management and mode enable. It integrates with the AGP core via `agp_bridge_driver` callbacks and uses `agp_device_ids` for readable chipset names.

## Risks And Edge Cases

`via_agp3_driver` declares `size_type = U8_APER_SIZE` while its `aperture_sizes` points to `agp3_generic_sizes` and `via_fetch_size_agp3()` treats entries as `aper_size_info_16`; generic GATT creation uses `size_type`, so this mismatch is a notable correctness risk unless avoided by runtime path assumptions. `via_cleanup_agp3()` writes to `VIA_APSIZE` instead of `VIA_AGP3_APSIZE`, which may be intentional compatibility or a register bug. The name table and PCI table must remain in identical order. The KT400 disguise workaround depends on subsystem ID.

## Test Signals

Compile with VIA AGP enabled, probe legacy and AGP3 VIA hardware, verify name-table alignment, confirm AGP3 driver selection through `VIA_AGPSEL`, and run allocation/bind/unbind tests across the selected aperture size. Static tests should inspect the AGP3 `size_type` mismatch and cleanup register choice.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/via-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/apm-emulation.c -->
# sources/distributed-fs/ceph-client/drivers/char/apm-emulation.c

## Purpose

`apm-emulation.c` provides a BIOS-less `/dev/apm_bios` compatibility layer, originally for ARM, on top of Linux power-management notifiers. It lets legacy APM userspace read power events, acknowledge suspend requests, request suspend, and read `/proc/apm` status supplied by platform code.

## Important APIs, Types, And Functions

- `struct apm_queue` is a 16-event circular buffer.
- `enum apm_suspend_state` models per-file suspend acknowledgement state.
- `struct apm_user` is per-open state, including reader/writer/root flags, suspend result/state, and event queue.
- Exported hooks: `apm_get_power_status` function pointer and `apm_queue_event()`.
- Device operations: `apm_open()`, `apm_release()`, `apm_read()`, `apm_poll()`, and `apm_ioctl()`.
- PM/event machinery: `kapmd()`, `apm_suspend_notifier()`, `queue_event()`, and queue helpers.
- Init/exit: miscdevice `apm_device`, proc show function `proc_apm_show()`, PM notifier registration, `apm_setup()` boot parameter.

## Control Flow

Init creates `kapmd`, creates `/proc/apm` when procfs is enabled, registers `/dev/apm_bios`, and registers a PM notifier. External kernel code calls `apm_queue_event()`, which queues to `kapmd_queue` under spinlock and wakes `kapmd`. The thread forwards status-change events to all readers or calls `pm_suspend()` for suspend events. During PM suspend/hibernate prepare, the notifier queues suspend events to privileged reader/writer file handles, increments `suspend_acks_pending`, wakes readers, and waits up to five seconds for `APM_IOC_SUSPEND` acknowledgements. Post-suspend queues resume events and wakes acknowledged waiters.

## State And Persistence Behavior

State persists in the global user list, per-open event queues, suspend counters, inhibit counter, `kapmd_queue`, waitqueues, and exported power-status callback. The driver does not persist data across module unload. Event queues drop the oldest event on overflow and log only the first overflow.

## Dependencies And Integration Points

Dependencies include miscdevice, procfs/seq_file, PM notifier APIs, suspend core, freezer-aware waits, capability checks, and APM UAPI definitions. It integrates with platform code through `apm_get_power_status` and `apm_queue_event()`, and with legacy userspace through `/dev/apm_bios`, `APM_IOC_SUSPEND`, poll/read, and `/proc/apm`.

## Risks And Edge Cases

`apm_read()` waits interruptibly but does not check the wait return before reading the queue, so a signal can lead to a zero-length result rather than `-ERESTARTSYS`/`-EINTR`. Queue operations for per-user queues are protected by list locks for producer iteration and state mutex for suspend transitions, but individual queue head/tail updates are not separately locked against concurrent read and PM notifier access. Suspend acknowledgement has deliberate races around timeout: late ACKs become `-ETIMEDOUT`. Only users that opened the device with read/write and had `CAP_SYS_ADMIN` at open time participate in ACKs.

## Test Signals

Functional tests should open `/dev/apm_bios` as reader/writer root, inject `apm_queue_event()` from a platform/test module, verify read/poll events, request suspend via `APM_IOC_SUSPEND`, and test timeout behavior with multiple open handles. PM tests should watch `suspend_acks_pending`, resume events, and `/proc/apm` formatting with and without `apm_get_power_status`. Static analysis should focus on queue concurrency and interruptible wait semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/apm-emulation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/applicom.c -->
# sources/distributed-fs/ceph-client/drivers/char/applicom.c

## Purpose

`applicom.c` is a misc character driver for Applicom industrial communication boards, including PCI Applicom cards and parameter-specified ISA boards. It exposes `/dev/ac` for mailbox reads/writes and ioctl-based board status/control while coordinating with board shared memory and interrupts.

## Important APIs, Types, And Functions

- `struct applicom_board` tracks each board's physical shared-memory address, ioremapped RAM, receive/send waitqueue, IRQ, and spinlock.
- Module parameters: `irq` and `mem` support ISA board discovery.
- Board discovery/lifecycle: `ac_register_board()`, `applicom_init()`, and `applicom_exit()`.
- File operations: `ac_read()`, `ac_write()`, and `ac_ioctl()`.
- Interrupt path: `ac_interrupt()` scans all boards, clears board interrupt flags, validates ready bytes, and wakes read/write waiters.
- Helper: `do_ac_read()` copies a board mailbox into kernel buffers and writes acknowledgement fields back to board RAM.

## Control Flow

Init scans PCI devices of class `PCI_CLASS_OTHERS`, matches Applicom IDs, enables devices, maps BAR0 shared memory, validates the signature and board number, requests shared IRQs, and enables board interrupts. If `mem`/`irq` parameters are provided, it scans up to four ISA slots spaced by `LEN_RAM_IO`. After at least one board is registered it registers miscdevice minor `AC_MINOR` as `ac`.

`ac_write()` expects a packed `struct st_ram_io` plus `struct mailbox`, validates the board index with `array_index_nospec()`, waits until `DATA_FROM_PC_READY` becomes zero, writes mailbox bytes using byte accesses, fills ownership/destination fields, marks data ready, and interrupts the card. `ac_read()` scans boards until `DATA_TO_PC_READY == 2`, then reads the mailbox, acknowledges it to the card, copies data to userspace, and returns. `ac_ioctl()` implements legacy numeric commands for raw status, board identity, reset/interrupt manipulation, TIC updates, owner fields, board number setup, and diagnostic printing.

## State And Persistence Behavior

Persistent driver state includes the `apbs[]` board table, `numboards`, per-board waitqueues/spinlocks, mapped I/O memory, IRQ registrations, and error counters. Hardware state persists in the board shared-memory protocol bytes and mailboxes. The driver intentionally uses byte-wise MMIO because the board cannot handle word accesses.

## Dependencies And Integration Points

Dependencies include PCI enumeration, miscdevice, shared IRQs, waitqueues, spinlocks, `array_index_nospec()`, MMIO byte accessors, and UAPI structures from `applicom.h`. Integration is through `/dev/ac`, module parameters for ISA hardware, and board firmware's shared-memory protocol.

## Risks And Edge Cases

`ac_read()` computes `ret` from `do_ac_read()` but returns `tmp` after userspace copies; because `tmp` is `2`, successful reads appear to return 2 bytes rather than the full structure size, which is a notable behavioral risk unless legacy userspace expects it. PCI device references from `pci_get_class()` are not released for every continuing path in the scan loop. Sleep/wait setup in read/write manually manipulates task state and waitqueues; missed wakeups or signal paths require care. Ioctl command numbers are raw integers with broad hardware effects. Multiple ISA boards share one IRQ but only the first records it for free. Byte protocol fields above value 2 are treated as device errors.

## Test Signals

Build with Applicom support and verify PCI and ISA discovery paths. On hardware or a test shim, exercise exact-size read/write buffers, bad board numbers, interrupt wakeups for receive and send readiness, ioctl commands 0-6, and cleanup after failed registration. Static review should investigate the successful `ac_read()` return value, PCI refcounting, and waitqueue signal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/applicom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/applicom.h -->
# sources/distributed-fs/ceph-client/drivers/char/applicom.h

## Purpose

`applicom.h` defines the shared-memory register offsets and userspace-visible data layouts for the Applicom board driver. It is the protocol contract consumed by `applicom.c` and by user programs that read/write `/dev/ac`.

## Important APIs, Types, And Functions

The header defines no functions. Important constants are board RAM offsets such as `DATA_TO_PC_READY`, `DATA_FROM_PC_READY`, owner/destination TIC and card fields, `CONF_END_TEST`, `ERROR_CODE`, `PARAMETER_ERROR`, `VERS`, mailbox buffers `RAM_TO_PC`/`RAM_FROM_PC`, board identity fields, and interrupt bytes `RAM_IT_FROM_PC`/`RAM_IT_TO_PC`.

It defines two packed-by-layout C structs without explicit packing attributes:

- `struct mailbox`: command/status/user fields plus a 256-byte data payload; `applicom.c` transfers it byte-by-byte to and from board RAM.
- `struct st_ram_io`: a snapshot/control structure for low board RAM status bytes, identity/error fields, version, board number, and reserved data.

## Control Flow

There is no control flow. `applicom.c` uses the offsets for MMIO byte reads/writes in init, interrupt handling, read/write operations, and ioctl commands. Userspace buffer sizes are checked as `sizeof(struct st_ram_io) + sizeof(struct mailbox)`.

## State And Persistence Behavior

The header stores no state, but its offsets map directly to persistent board shared-memory state. Struct layout is ABI-relevant for `/dev/ac` read/write/ioctl behavior.

## Dependencies And Integration Points

It depends on fixed-width Linux integer typedefs being available through includers. It integrates with `applicom.c`, Applicom board firmware, and legacy userspace that builds buffers matching these structures.

## Risks And Edge Cases

The structs are not marked `__packed`; current field ordering likely avoids surprising padding for the intended ABI, but compiler/layout assumptions are still part of the contract. `NUMCARD_ACK_FROM_PC` is written as `0x010`, equivalent to `0x10`, which is visually easy to misread. Any offset change would break hardware protocol and userspace ABI. Endianness of multi-byte fields in `struct mailbox` is not converted by the driver.

## Test Signals

Compile ABI checks for `sizeof(struct st_ram_io)` and `sizeof(struct mailbox)` on supported architectures. Runtime tests should verify the driver's expected buffer length matches legacy userspace and that byte offsets read/write the intended board RAM locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/applicom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/bsr.c -->
# sources/distributed-fs/ceph-client/drivers/char/bsr.c

## Purpose

`bsr.c` is the IBM POWER Barrier Synchronization Register character driver. It discovers Open Firmware `ibm,bsr` nodes, creates one character device per BSR register/window, exposes size/stride/length attributes, and lets userspace `mmap()` cache-inhibited BSR hardware for fast synchronization.

## Important APIs, Types, And Functions

- `struct bsr_dev` stores physical address, mapped length, BSR byte size, stride, type/index, minor, cdev, device, and list node.
- Sysfs attributes: `bsr_size`, `bsr_stride`, and `bsr_length`.
- File operations: `bsr_open()` stores the selected `bsr_dev` in `private_data`; `bsr_mmap()` maps the hardware region noncached.
- Discovery/lifecycle: `bsr_add_node()`, `bsr_create_devs()`, `bsr_cleanup_devs()`, `bsr_init()`, and `bsr_exit()`.
- Global registries: `bsr_devs`, `total_bsr_devs`, `bsr_types[]`, `bsr_major`, and class `bsr_class`.

## Control Flow

Init finds the first `ibm,bsr` node, registers class `bsr`, allocates up to `BSR_MAX_DEVS` character minors, then iterates compatible nodes. For each node, `bsr_add_node()` reads matching `ibm,lock-stride` and `ibm,#lock-bytes` arrays, maps each `reg` resource to a `bsr_dev`, normalizes lengths between 4 KB and `PAGE_SIZE` down to 4 KB for sysfs, classifies by byte size, creates a cdev, and creates `/dev`/sysfs device names like `bsr8_0`. `mmap()` sets noncached page protection and maps either a 4 KB PFN for small regions or the full requested region if within `bsr_len`.

## State And Persistence Behavior

Persistent software state is the list of created BSR devices, allocated minors, class devices, and sysfs attributes. Hardware state is not owned by the driver; userspace writes directly to mapped BSR bytes. The driver does not serialize userspace access after mmap and does not persist data beyond device nodes.

## Dependencies And Integration Points

Dependencies include Open Firmware node/resource APIs, char device registration, sysfs device classes, noncached page protections, `remap_4k_pfn()`, and `io_remap_pfn_range()`. It integrates with IBM POWER firmware descriptions and userspace synchronization libraries that understand single-byte BSR writes and required `sync` barriers.

## Risks And Edge Cases

The hardware requires only single-byte writes, but the mmap interface cannot enforce access width; misuse can violate hardware rules. `BSR_MAX_DEVS` is fixed at 32, but `total_bsr_devs` is incremented by each node's property count without an explicit cap before `MKDEV()`/`cdev_add()`. Error cleanup removes all devices if any later node fails. `bsr_create_devs()` uses `of_find_compatible_node()` iteratively and must manage node references carefully. For 64 KB page kernels, regions larger than 4 KB but smaller than `PAGE_SIZE` are advertised as 4 KB and mapped through `remap_4k_pfn()`.

## Test Signals

Boot on POWER hardware or device-tree tests with `ibm,bsr` nodes. Verify character devices and sysfs attributes match `reg`, `ibm,lock-stride`, and `ibm,#lock-bytes`; mmap a 4 KB and larger region; confirm noncached mapping; and run a userspace synchronization loop using byte writes and full sync barriers. Static checks should validate minor overflow against `BSR_MAX_DEVS` and cleanup on partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/bsr.c -->
