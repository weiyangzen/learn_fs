# subset-b-000847 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_common.c

## Purpose
Provides shared PCI host-controller services for SPARC PCI bus modules. It implements `sun4u_pci_ops` and `sun4v_pci_ops`, extracts Open Firmware PBM properties, turns OF `ranges` into Linux resources, reserves virtual-DMA windows, and supplies recursive PCI error-status scanners used by controller-specific interrupt handlers.

## Important APIs, Types, and Functions
- `sun4u_pci_ops` and `sun4v_pci_ops` are the PCI config-space operation tables consumed by PBM drivers.
- `sun4u_config_mkaddr()` builds memory-mapped config addresses from PBM config base, bus, devfn, and register width.
- `sun4u_read_pci_cfg_host()` and `sun4u_write_pci_cfg_host()` special-case host bridge config accesses where natural-size register access is required.
- `sun4v_read_pci_cfg()` and `sun4v_write_pci_cfg()` proxy config access through hypervisor calls declared in `pci_sun4v.h`.
- `pci_get_pbm_props()` imports `bus-range` and optional `ino-bitmap`.
- `pci_determine_mem_io_space()` parses OF PCI ranges into `io_space`, `mem_space`, and optional `mem64_space`, registers them under global resources, and calls `pci_register_iommu_region()`.
- `pci_scan_for_target_abort()`, `pci_scan_for_master_abort()`, and `pci_scan_for_parity_error()` recursively walk buses and clear/report PCI status bits.

## Control Flow
Controller probes initialize a `pci_pbm_info`, choose `sun4u_pci_ops` or `sun4v_pci_ops`, then call the property/resource helpers. Normal PCI core config reads and writes enter through the ops table. sun4u paths validate the bus range and use direct config-space loads/stores; sun4v paths build an HV PCI device identifier and invoke hypervisor accessors. Error interrupt handlers in PSYCHO/SABRE/SCHIZO call the scan helpers after latching controller error registers.

## State and Persistence
The file mutates only boot/runtime kernel state: PBM bus number bounds, `ino_bitmap`, resource descriptors, config-space base, address offsets, and allocated IOMMU resource descriptors. There is no persistent storage. Error scans clear device PCI status bits by writing the active error mask back to config space.

## Dependencies and Integration Points
Depends on Linux PCI/resource/OF APIs, SPARC PROM halt/printf paths, low-level config accessors from assembly/support code, and sun4v hypervisor wrappers. It integrates with every SPARC PBM driver through `pci_impl.h` declarations and with the generic PCI core through `struct pci_ops`.

## Risks and Edge Cases
- Missing OF `ranges` or MEM/IO ranges causes `prom_halt()`, so malformed firmware data is fatal.
- sun4u host bridge accesses intentionally split sub-word/word operations for hardware quirks; refactoring them into generic width accesses risks silent zero reads on Sabre-like hardware.
- `pci_get_pbm_props()` assumes `bus-range` exists and has enough cells.
- sun4v writes ignore hypervisor error status and always return `PCIBIOS_SUCCESSFUL`.
- MEM64 adjustment silently disables overlapping 64-bit windows if they collapse below 32-bit MEM.

## Test Signals
Useful signals are boot logs showing PCI IO/MEM/MEM64 ranges, successful PCI enumeration, valid config reads on host bridge device 0, absence of PROM halt on OF range parsing, and injected/observed PCI status bits being reported and cleared by target/master/parity scanners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_fire.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_fire.c

## Purpose
Implements the sun4u FIRE PCI Express host controller driver. It initializes FIRE PBM register state, IOMMU translation, MSI event queues, PCIe link/control registers, and platform-driver probing for compatible `pciex108e,80f0` nodes.

## Important APIs, Types, and Functions
- `fire_probe()` allocates `pci_pbm_info` and `iommu`, then calls `pci_fire_pbm_init()`.
- `pci_fire_pbm_init()` fills PBM fields, parses resources, initializes hardware/IOMMU/MSI, scans the PCI bus, and links the PBM into `pci_pbm_root`.
- `pci_fire_pbm_iommu_init()` programs FIRE IOMMU registers, invalidates TLB entries, initializes the software table, installs the TSB base, and enables translation/bypass/cache modes.
- MSI support defines `struct pci_msiq_entry` and `pci_fire_msiq_ops`.
- `pci_fire_dequeue_msi()`, `pci_fire_msi_setup()`, `pci_fire_msi_teardown()`, `pci_fire_msiq_alloc()`, and `pci_fire_msiq_build_irq()` implement the hardware-facing MSI queue contract used by `sparc64_pbm_msi_init()`.
- `pci_fire_hw_init()` programs parity, fatal reset, core interrupt, TLU, LPU, DMC, and PEC registers.

## Control Flow
At `subsys_initcall`, `fire_driver` registers and OF matching invokes `fire_probe()`. Probe allocates state and sets PBM register bases from the `reg` property. Initialization follows a fixed order: resource discovery, PBM properties, hardware register setup, IOMMU setup, MSI setup, bus scan, then root-list registration. MSI interrupts arrive on event queues; common MSI code calls FIRE ops to get/dequeue/set queue heads and dispatch Linux IRQs.

## State and Persistence
State lives in `pci_pbm_info`, the allocated IOMMU table, and a 512 KiB contiguous MSI queue block. Hardware state includes IOMMU control/TSB registers, MSI map/clear/event queue registers, MSI address registers, and many FIRE control registers. No disk-persistent state exists.

## Dependencies and Integration Points
Uses UPA register accessors, Linux OF/platform/PCI/MSI/IRQ APIs, `iommu_table_init()`, `build_irq()`, `sparc64_pbm_msi_init()`, and shared PCI helpers from `pci_common.c`. It integrates with generic MSI through `setup_msi_irq`/`teardown_msi_irq` callbacks installed by the common MSI layer.

## Risks and Edge Cases
- MSI queue allocation requires a large contiguous block; failure disables MSI.
- Event queue head/tail handling assumes queue IDs map directly to register offsets and queue memory layout.
- `pci_fire_msiq_build_irq()` contains a fixed interrupt-controller selection placeholder, so affinity/routing behavior is hardware-specific and fragile.
- No error interrupt handlers are registered; the file leaves a placeholder for FIRE error handling.
- IOMMU uses a hardcoded virtual DMA aperture because FIRE lacks a `virtual-dma` property.

## Test Signals
Boot should log `SUN4U PCIE Bus Module`, resource ranges, MSI queue properties, MSI queue physical address, and successful PCIe device enumeration. MSI tests should show interrupts delivered through `MSIQ` without queue overflow or invalid type errors. DMA tests should validate mapping/unmapping across the configured 32-bit aperture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_fire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_impl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_impl.h

## Purpose
Defines the internal SPARC PCI PBM abstraction shared by all controller drivers. It centralizes PBM topology, resources, IOMMU/streaming-buffer state, MSI queue state, bus scan hooks, and config-space operation declarations.

## Important APIs, Types, and Functions
- `struct pci_pbm_info` is the core per-PBM state object. It tracks sibling/root linkage, register bases, port/dev handles, chip type/version, OF platform device, resources, config-space metadata, PCI bus pointer, `pci_ops`, NUMA node, IOMMU pointer, streaming buffer, and optional MSI fields.
- `struct sparc64_msiq_ops` abstracts controller-specific MSI queue operations.
- `struct sparc64_msiq_cookie` binds an MSI queue IRQ to a PBM and queue ID.
- `PCI_STC_FLUSHFLAG_INIT()` and `PCI_STC_FLUSHFLAG_SET()` wrap streaming-buffer flush flag access.
- Exports declarations for `pci_get_pbm_props()`, `pci_scan_one_pbm()`, `pci_determine_mem_io_space()`, PCI error scanners, low-level config accessors, `sun4u_pci_ops`, `sun4v_pci_ops`, and poke fault state.

## Control Flow
Controller files allocate and populate `pci_pbm_info`, then call shared helpers and register the PBM into `pci_pbm_root`. The generic PCI core reaches controller config operations through `pbm->pci_ops`; DMA paths reach IOMMU state through `pbm->iommu`; MSI paths reach queue operations through `pbm->msi_ops`.

## State and Persistence
The header defines runtime-only in-memory state. Its root list fields (`next`, `sibling`, `pci_pbm_root`, `pci_num_pbms`) establish long-lived kernel topology after boot. MSI bitmaps, IRQ tables, and queue buffers are dynamically allocated by implementation files.

## Dependencies and Integration Points
Includes Linux PCI/MSI/spinlock types and SPARC `io`, `prom`, and `iommu` definitions. It is included by sun4u, sun4v, FIRE, PSYCHO, SABRE, SCHIZO, and MSI implementation files.

## Risks and Edge Cases
- `struct pci_pbm_info` is shared across many old hardware drivers; field semantics vary by controller, especially shared versus per-PBM IOMMU and config-space register width.
- MSI fields exist only under `CONFIG_PCI_MSI`, so implementation code must maintain ifdef symmetry.
- PBM chip type constants are integral ABI inside this source set; mismatches alter hardware-specific paths.

## Test Signals
Compile coverage across `CONFIG_PCI_MSI` enabled/disabled builds is important. Runtime validation comes from all controller probes correctly filling PBM fields, successful bus scans, DMA mapping through `pbm->iommu`, and MSI setup only when `msi_ops` are installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_msi.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_msi.c

## Purpose
Provides the common sparc64 PCI MSI layer above controller-specific MSI queue hardware. It parses MSI properties from OF, allocates software MSI state, brings up MSI queue IRQs, dispatches queued MSI messages, and installs per-PBM MSI setup/teardown callbacks.

## Important APIs, Types, and Functions
- `sparc64_pbm_msi_init()` is called by FIRE and sun4v controller drivers with their `sparc64_msiq_ops`.
- `sparc64_msiq_interrupt()` drains one MSI queue and calls `generic_handle_irq()` for each mapped MSI.
- `pick_msiq()` round-robins MSI queues per PBM under a spinlock.
- `alloc_msi()` and `free_msi()` manage the MSI bitmap.
- `sparc64_setup_msi_irq()` allocates a Linux IRQ, reserves an MSI number, programs controller MSI mapping, writes the device MSI message, and fills `msi_irq_table`.
- `sparc64_teardown_msi_irq()` finds the MSI number for an IRQ, calls controller teardown, clears state, frees bitmap and IRQ resources.
- `msi_bitmap_alloc()`, `msi_table_alloc()`, and `sparc64_bringup_msi_queues()` allocate software backing and request queue interrupts.

## Control Flow
During PBM probe, the controller-specific driver calls `sparc64_pbm_msi_init()`. The function reads OF properties such as `#msi-eqs`, `msi-eq-size`, `msi-eq-to-devino`, `#msi`, `msi-ranges`, `msi-data-mask`, `msix-data-width`, and `msi-address-ranges`. If every property and allocation succeeds, it allocates controller queue memory via ops, requests one interrupt per queue, logs the MSI layout, and installs callbacks in `pci_pbm_info`. At device MSI enable time, generic PCI MSI code calls the PBM setup callback; interrupts then drain via `sparc64_msiq_interrupt()`.

## State and Persistence
Runtime state includes `msi_bitmap`, `msi_irq_table`, `msiq_irq_cookies`, queue rotor, OF-derived ranges, and controller-owned `msi_queues`. There is no persistence. Teardown frees MSI numbers and IRQs but queue-wide cleanup is mostly on initialization failure or controller removal paths, which are not fully represented here.

## Dependencies and Integration Points
Depends on Linux interrupt, IRQ, PCI MSI, OF, and slab APIs. It relies on `pci_pbm_info` fields defined in `pci_impl.h` and delegates all hardware-specific queue operations to `sparc64_msiq_ops`.

## Risks and Edge Cases
- Any missing or malformed OF MSI property disables MSI for the whole PBM.
- `bringup_one_msi_queue()` does not unwind already requested queue IRQs if a later queue fails.
- `sparc64_teardown_msi_irq()` returns early after controller teardown error, leaving bitmap/IRQ cleanup undone.
- IRQ affinity is set by NUMA node only when `pbm->numa_node != -1`.
- `msi_irq_table` entries are zeroed rather than initialized to `~0U`, so IRQ zero conventions matter.

## Test Signals
MSI-capable boot should log queue counts, first MSI, data mask, address ranges, and queue physical address. Device tests should verify MSI enable writes correct 32-bit/64-bit message addresses, queue interrupts dispatch to device handlers, and repeated enable/disable does not leak MSI numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_psycho.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_psycho.c

## Purpose
Implements PSYCHO/U2P PCI controller support for sun4u systems. It handles controller/PBM hardware initialization, shared IOMMU and per-PBM streaming buffers, bus scanning, sibling PBM discovery, Starfire hookup, and uncorrectable/correctable/PCI error interrupt handling.

## Important APIs, Types, and Functions
- `psycho_probe()` allocates PBM state, finds or allocates the shared IOMMU, maps register bases, initializes controller hardware, initializes IOMMU once per sibling pair, and scans the PBM.
- `psycho_pbm_init()` calls common PSYCHO PBM setup, initializes streaming buffer state, then scans.
- `psycho_controller_hwinit()` enables PCI arbiters and applies a DMA write/PIO read synchronization erratum workaround.
- `psycho_pbm_strbuf_init()` programs per-PBM streaming-buffer registers and flush flag addresses.
- `psycho_ue_intr()` and `psycho_ce_intr()` latch, clear, and log UPA/ECC errors.
- `psycho_register_error_handlers()` requests UE, CE, and PCIERR interrupts and enables ECC/PCI error reporting.
- `pbm_config_busmastering()` writes host bridge cache-line and latency config values.

## Control Flow
The platform driver matches `pci108e,8000`. Probe determines PBM A/B from the `reg` address, finds a sibling by UPA portid, and shares its IOMMU when present. The first sibling initializes the hardware IOMMU and optional Starfire IRQ translation. Each PBM initializes its streaming buffer and scans its PCI bus. Error handlers are registered after scanning so the bus tree is available for PCI error diagnosis.

## State and Persistence
State is held in the PBM list, sibling pointers, shared IOMMU table, per-PBM streaming buffer registers/flush flags, and hardware error-control registers. Interrupt handlers clear latched AFSR bits and may invoke IOMMU diagnostics. No persistent storage exists.

## Dependencies and Integration Points
Uses `psycho_common.h` and `iommu_common.h` helper functions, shared config/resource helpers, UPA accessors, OF/platform APIs, Linux IRQ APIs, Starfire support, and generic PCI scanning.

## Risks and Edge Cases
- Two PBMs share one IOMMU; allocation/free error paths must not free a sibling-owned IOMMU.
- Error IRQ registration intentionally ignores some shared IRQ request results.
- Correctable error AFAR is defined at the same offset as CE AFSR in this source, so diagnosis depends on hardware alias semantics.
- Streaming buffer diagnostic operations are sensitive to dirty data and hardware state.
- Fatal PROM/property failures and shared interrupt behavior are difficult to test without matching hardware.

## Test Signals
Boot logs should show PSYCHO PBM versions, both sibling PBMs linked for dual-bus controllers, PCI bus enumeration, and registered error IRQs. Fault injection or hardware errors should log UE/CE/PCI details and IOMMU diagnostics without recursive interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_psycho.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sabre.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sabre.c

## Purpose
Implements SABRE/Hummingbird PCI controller support for UltraSPARC-IIi/IIe-class systems. It initializes the single supported controller, maps config/IOMMU resources, handles APB bridge setup, performs hardwired interrupt cleanup, and registers UE/CE/PCIERR error handlers.

## Important APIs, Types, and Functions
- `sabre_probe()` allocates `pci_pbm_info` and `iommu`, detects Hummingbird variants, maps controller registers, clears interrupt state, initializes PCI control, config space, virtual-DMA aperture, IOMMU, and PBM scanning.
- `sabre_pbm_init()` calls shared PSYCHO common PBM init with SABRE chip type and sets PCI AFSR/AFAR/CSR registers.
- `sabre_scan_bus()` enforces single-controller support, scans bus 0, initializes APB bridges, and registers errors.
- `apb_init()` configures Sun Simba bridge command/status/latency/bridge-control fields.
- `sabre_ue_intr()` and `sabre_ce_intr()` log and clear ECC/DMA errors, with UE invoking IOMMU diagnostics.
- `sabre_register_error_handlers()` maps error IRQ property entries to request_irq calls and enables PCI error reporting.

## Control Flow
The driver matches `pci108e,a001` and `pci108e,a000`. Probe determines whether it is Hummingbird via match data or CPU node name. It maps register windows from OF, clears PCI and OBIO interrupt clear registers, enables controller features, parses `virtual-dma`, initializes the shared PSYCHO-style IOMMU, then scans bus 0. After devices are known, APB bridge fixups and error IRQ registration run.

## State and Persistence
Global state includes `hummingbird_p` and `sabre_root_bus`; PBM and IOMMU state are long-lived after probe. Hardware registers for interrupt clear, PCI control, IOMMU, and error reporting are programmed at boot. There is no persistent storage.

## Dependencies and Integration Points
Uses shared `psycho_common` IOMMU/error helpers, generic PCI scanning, OF/platform APIs, APB bridge definitions, UPA register accessors, and Linux IRQ APIs. It uses `sun4u_pci_ops` through common PBM initialization.

## Risks and Edge Cases
- Multiple SABRE controllers are explicitly unsupported and only log an error before skipping additional scans.
- PROM `virtual-dma` sizes outside known values abort initialization.
- I/O resources above 64K and APB assumptions reflect old hardware constraints.
- Error IRQ registration depends on parent versus child OF node choice for SABRE chip type.
- Some register loops assume fixed interrupt-clear address ranges.

## Test Signals
Expected boot signals are one SABRE PBM, successful bus 0 scan, APB bridge devices configured, and no "Multiple controllers unsupported" message. Error handling can be validated by UE/CE/PCIERR logs and by seeing IOMMU diagnostics for translation-related errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sabre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_schizo.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_schizo.c

## Purpose
Implements SCHIZO, SCHIZO+, and TOMATILLO PCI controller support. It covers PCI config addressing, per-PBM IOMMU and streaming buffer initialization, controller-specific hardware tuning, sibling detection, bus scanning, and extensive UE/CE/PCI/Safari-JBUS error diagnostics.

## Important APIs, Types, and Functions
- `schizo_probe()` and `__schizo_init()` match compatible nodes and allocate PBM/IOMMU state.
- `schizo_pbm_init()` fills PBM identity/register fields, parses resources/properties, initializes hardware, IOMMU, streaming buffer, and PCI bus.
- `schizo_pbm_iommu_init()` configures per-PBM IOMMU registers, TSB table, context flush support, and software allocation pools.
- `schizo_pbm_strbuf_init()` enables streaming buffers for SCHIZO but skips TOMATILLO, which lacks streaming cache.
- `schizo_pbm_hw_init()` programs arbiter, parking, retry/timeout, TOMATILLO prefetch, and diagnostic controls.
- `schizo_ue_intr()`, `schizo_ce_intr()`, `schizo_pcierr_intr()`, and `schizo_safarierr_intr()` log and clear hardware error state.
- `schizo_check_iommu_error()` and `__schizo_check_stc_error_pbm()` enter diagnostic modes to dump IOMMU/STC tags and error lines.
- `schizo_register_error_handlers()` and `tomatillo_register_error_handlers()` route INOs to Linux IRQs and enable error masks.

## Control Flow
The match table is ordered to prefer TOMATILLO over older compatible strings. Probe determines chip type from match data, finds a sibling by portid rules, allocates a fresh per-PBM IOMMU, and calls PBM init. PBM init inserts the PBM into the root list early, sets `sun4u_pci_ops`, discovers OF ranges and PBM properties, initializes hardware/IOMMU/STC, scans the bus, and registers error handlers based on chip type and INO bitmap.

## State and Persistence
Long-lived state includes PBM root/sibling links, per-PBM IOMMU tables, optional streaming buffer flush flags, chip version/revision, sync registers, and resource windows. Static diagnostic buffers (`stc_error_buf`, `stc_tag_buf`, `stc_line_buf`) are protected by `stc_buf_lock` during STC dumps. Hardware error bits are cleared as interrupts are handled.

## Dependencies and Integration Points
Uses Linux OF/platform/PCI/IRQ/NUMA APIs, UPA register access, shared PCI common helpers, IOMMU table helpers, and generic PCI error scanners. It integrates with SPARC interrupt routing through INO bitmaps and with DMA through the SPARC IOMMU/streaming-buffer framework.

## Risks and Edge Cases
- STC diagnostics are explicitly dangerous: entering diagnostic mode and clearing tags can discard dirty streaming-buffer data if hardware state is unlucky.
- TOMATILLO sibling routing is partly heuristic, comparing port IDs with the low bit toggled.
- Error pending loops have finite limits and may log stale values if hardware never settles.
- Some Safari/JBUS errors are configured fatal while UNMAP is interrupting; incorrect masks can reset systems.
- PBM is linked into `pci_pbm_root` before all initialization succeeds, which can leave partial state visible on later failure.

## Test Signals
Boot should identify SCHIZO/SCHIZO+/TOMATILLO version and revision, enumerate each PBM, show resource ranges, and avoid error IRQ registration warnings. Hardware error testing should exercise UE/CE/PCI/JBUS paths, including target/master/parity recursive PCI scans and IOMMU/STC diagnostic logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_schizo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.c

## Purpose
Implements PCI controller, DMA mapping, IOMMU/ATU, MSI, and bus scanning support for sun4v virtualized SPARC systems. Unlike sun4u controllers, most hardware operations are hypervisor calls mediated by `pci_sun4v_asm.S`.

## Important APIs, Types, and Functions
- `pci_sun4v_probe()` negotiates PCI and ATU HV API versions, installs `sun4v_dma_ops`, allocates per-CPU IOMMU batch pages, PBM/IOMMU/ATU state, and calls `pci_sun4v_pbm_init()`.
- `pci_sun4v_pbm_init()` fills PBM fields, parses resources/properties, initializes IOMMU, MSI, bus scan, optional ATU, and root-list linkage.
- `struct iommu_batch` and helpers `iommu_batch_start/add/new_entry/end/flush()` batch HV IOMMU map operations with interrupts disabled.
- DMA ops `dma_4v_alloc_coherent()`, `free_coherent()`, `map_phys()`, `unmap_phys()`, `map_sg()`, and `unmap_sg()` implement Linux DMA API operations using legacy 32-bit IOMMU or 64-bit ATU IOTSB.
- `pci_sun4v_iommu_init()` initializes the legacy IOMMU bitmap and imports OBP mappings via `probe_existing_entries()`.
- `pci_sun4v_atu_init()` and `pci_sun4v_atu_alloc_iotsb()` configure 64-bit ATU IOTSB, bind devices, and initialize the ATU allocation map.
- MSI functions implement `sparc64_msiq_ops` through HV calls.

## Control Flow
The platform driver matches `SUNW,sun4v-pci`. The first probe negotiates HV groups for PCI and optionally ATU, then installs global DMA ops. Probe derives `devhandle` from the high bits of the first `reg` address, initializes per-CPU page-list storage once, allocates state, and initializes the PBM. DMA mappings choose legacy IOMMU when the DMA mask is 32-bit-compatible and ATU when available with a larger mask. MSI setup allocates queue memory, registers it with the HV, validates queue config, and uses common MSI dispatch.

## State and Persistence
Runtime state includes global negotiated HV API versions, `dma_ops`, per-CPU mapping batches, PBM root linkage, IOMMU bitmaps, optional ATU/IOTSB tables, queue memory, and OF-derived resource ranges. Existing OBP IOMMU entries are imported or demapped at boot depending on whether their real address is in available physical memory.

## Dependencies and Integration Points
Depends on Linux DMA map ops, PCI, MSI, OF/platform, percpu, IRQ, and SPARC hypervisor APIs. Integrates with `pci_common.c` through `sun4v_pci_ops`, with `pci_msi.c` through queue ops, and with assembly HV wrappers declared in `pci_sun4v.h`.

## Risks and Edge Cases
- `dma_4v_map_sg()` failure cleanup frees software ranges but has an explicit `XXX demap?` comment, indicating possible stale HV mappings on partial failure.
- ATU initialization failure falls back to legacy IOMMU, which may hide 64-bit DMA capability loss.
- Per-CPU batch allocation is one-shot; failures after some CPUs are allocated are not unwound.
- HV version differences strip unsupported map attributes for older VPCI.
- Queue/head offsets for sun4v MSI are byte offsets rather than entry indexes, unlike FIRE.
- `dma_4v_free_coherent()` only frees pages for `order < 10`, matching old allocation assumptions but requiring careful size behavior.

## Test Signals
Boot should log registered VPCI and optional ATU HV API versions, PBM NUMA node, resource ranges, imported OBP mappings when present, and MSI queue metadata. DMA validation should cover coherent, single, and scatterlist mappings with 32-bit and 64-bit masks, including ATU fallback. MSI tests should verify HV queue configuration and interrupt dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.h

## Purpose
Declares the sun4v PCI hypervisor-call wrapper interface used by `pci_common.c` and `pci_sun4v.c` for config space, IOMMU, MSI queue, MSI state, message, and ATU IOTSB operations.

## Important APIs, Types, and Functions
- IOMMU v1 calls: `pci_sun4v_iommu_map()`, `pci_sun4v_iommu_demap()`, and `pci_sun4v_iommu_getmap()`.
- Config accessors: `pci_sun4v_config_get()` and `pci_sun4v_config_put()`.
- MSI queue calls: `pci_sun4v_msiq_conf/info/getvalid/setvalid/getstate/setstate/gethead/sethead/gettail()`.
- MSI calls: `pci_sun4v_msi_getvalid/setvalid/getmsiq/setmsiq/getstate/setstate()`.
- Message calls: `pci_sun4v_msg_getmsiq/setmsiq/getvalid/setvalid()`.
- ATU/IOTSB v2 calls: `pci_sun4v_iotsb_conf/bind/map/demap()`.

## Control Flow
The header only declares functions. Runtime flow is from C code into assembly wrappers, then to `HV_FAST_TRAP`. Output pointer arguments receive HV return registers for mapping counts, attributes, queue information, or handles.

## State and Persistence
No state is defined here. The interface mutates hypervisor-owned PCI/IOMMU/MSI state and C-owned output variables in callers.

## Dependencies and Integration Points
Depends on Linux integer types for `u64`. The implementation lives in `pci_sun4v_asm.S`; users are `pci_common.c` for config access and `pci_sun4v.c` for DMA/IOMMU/MSI.

## Risks and Edge Cases
- Return conventions differ: some calls return status, some counts, and `pci_sun4v_iommu_map()` returns negative status on failure.
- Pointer outputs are written by assembly wrappers without C type checking beyond prototypes.
- Callers must negotiate the relevant HV API groups before invoking these functions.

## Test Signals
Build tests must ensure prototypes match assembly symbols. Runtime tests are indirect: successful config reads/writes, DMA mapping/demapping, IOTSB creation/binding, and MSI queue state operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v_asm.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v_asm.S

## Purpose
Implements low-level SPARC assembly wrappers around sun4v PCI hypervisor fast traps. These wrappers adapt register conventions between C callers and HV services for PCI config, IOMMU, MSI/MSIQ, message routing, and ATU IOTSB operations.

## Important APIs, Types, and Functions
- `ENTRY(pci_sun4v_iommu_map/demap/getmap)` wraps legacy IOMMU mapping services.
- `ENTRY(pci_sun4v_config_get/put)` wraps PCI config reads/writes and normalizes errors.
- `ENTRY(pci_sun4v_msiq_*)`, `ENTRY(pci_sun4v_msi_*)`, and `ENTRY(pci_sun4v_msg_*)` expose queue, MSI, and message control.
- `ENTRY(pci_sun4v_iotsb_conf/bind/map/demap)` exposes ATU IOTSB v2 calls.
- Every wrapper selects an `HV_FAST_PCI_*` trap number in `%o5` and executes `ta HV_FAST_TRAP`.

## Control Flow
C callers place arguments in SPARC outgoing registers. The wrapper may preserve an output pointer in `%g1` or shift pointer registers to avoid clobbering by HV return values, sets `%o5` to the HV function number, traps, stores output registers to caller-provided pointers, and returns status/data/count in `%o0`.

## State and Persistence
The file has no static state. It changes hypervisor-managed state and writes to memory addresses supplied by callers. Error normalization is local to wrappers such as config get/put and IOMMU map.

## Dependencies and Integration Points
Depends on `linux/linkage.h` for symbol macros and `asm/hypervisor.h` for trap numbers. It must stay ABI-compatible with declarations in `pci_sun4v.h` and assumptions in `pci_sun4v.c`.

## Risks and Edge Cases
- Register ordering is the entire contract; a prototype or HV ABI mismatch causes silent corruption.
- Some wrappers store output values even if HV status is nonzero, so callers must interpret status correctly.
- `pci_sun4v_config_get()` returns all ones on error to match PCI config semantics.
- `pci_sun4v_iommu_map()` returns negative status on nonzero status but mapped count on success, unlike several unsigned status wrappers.

## Test Signals
Build/link tests should confirm all declared symbols resolve. Runtime confidence comes from sun4v PCI enumeration, config access, DMA mappings with expected mapped/demapped counts, and MSI queue configuration succeeding through these wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pcic.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pcic.c

## Purpose
Implements MicroSPARC-IIep PCIC PCI controller support for 32-bit SPARC systems. It handles early controller probing, memory-mapped config access, hardcoded platform interrupt routing, PCI bus scanning/fixup, timer setup, NMI trap handling for speculative config faults, and a PCIC IRQ chip.

## Important APIs, Types, and Functions
- `struct pcic_ca2irq` and `struct pcic_sn2list` encode hardcoded system-name-to-PCI-interrupt routing maps.
- `pcic_probe()` maps PCIC register/config/IO windows from PROM, patches the NMI trap, selects the routing map, and marks the controller present.
- `pcic_read_config()` and `pcic_write_config()` implement bus-0-only PCI config access via PCIC address/data registers.
- `pcic_init()` disables IOTLB translation, expands PCI memory mapping, and scans the bus.
- `pcibios_fixup_bus()` attaches PROM cookies, remaps low I/O BARs into memory-space addresses, and fills IRQs.
- `pcic_fill_irq()` reads/programs PCIC interrupt select registers and builds Linux IRQs.
- `pci_time_init()` configures PCIC system timer and clocksource/clockevent hooks.
- `pcic_nmi()` handles speculative PIO NMIs during config reads.
- `pcic_build_device_irq()` allocates Linux IRQs and installs the `pcic_irq` chip.

## Control Flow
PCIC is probed before normal PCI init so interrupt routing exists early. The PCI subsystem later triggers `pcic_init()` via `subsys_initcall`, scans bus 0, and calls `pcibios_fixup_bus()` for discovered devices. Config reads disable local IRQs, write a config command, then speculatively read data; if an NMI records a PIO trap, the read returns all ones. Timer initialization binds the PCIC counter IRQ to the generic timer interrupt.

## State and Persistence
Static state includes `pcic0_up`, `pcic0`, `pcic_regs`, speculative trap flags, and timer dummy storage. Device fixups allocate per-device cookies. Hardware state includes PCIC config windows, DVMA control, memory BAR mapping, interrupt-select registers, interrupt masks, and timer/counter registers. No persistent storage exists.

## Dependencies and Integration Points
Depends on PROM APIs, SPARC timer/IRQ configuration, Swift cache flush, PCI core, OF node conversion, and low-level trap table symbols. It integrates with generic PCI via `pcic_ops` and architecture hooks such as `sparc_config.build_device_irq`.

## Risks and Edge Cases
- Interrupt routing is hardcoded by PROM root name; unknown systems enumerate but cannot route interrupts.
- Only bus 0 is supported; nonzero buses log and return.
- Low I/O BAR remapping mutates resources from I/O to MEM and sets placeholder end values, which is fragile.
- Several fatal paths spin forever or halt the PROM.
- NMI handling advances PC/NPC to skip faulting speculative reads; any mismatch with instruction layout is hazardous.
- `pcic_load_profile_irq()` is unimplemented.

## Test Signals
Expected boot signals include PCIC present, known system routing map selected, PCI bus 0 scanned, low I/O BARs remapped, and IRQs assigned/programmed. Timer tests should show working clock events. Config probing should not hang on absent devices but should return all ones through the NMI recovery path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pcic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pcr.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pcr.c

## Purpose
Provides generic sparc64 performance counter register infrastructure shared by perf, oprofile-style users, and the pseudo-NMI watchdog. It selects CPU-family-specific `pcr_ops`, negotiates sun4v perf hypervisor APIs, and supplies deferred work handling for high-PIL performance counter interrupts.

## Important APIs, Types, and Functions
- `const struct pcr_ops *pcr_ops` is exported for perf and watchdog code.
- `deferred_pcr_work_irq()` clears the deferred softint and runs `irq_work` at a lower interrupt level.
- `arch_irq_work_raise()` raises `PIL_DEFERRED_PCR_WORK`.
- Direct ops read/write `%pcr` and `%pic`, with a Blackbird erratum workaround in `direct_pic_write()`.
- Niagara/T-series ops (`n2_pcr_ops`, `n4_pcr_ops`, `n5_pcr_ops`, `m7_pcr_ops`) use direct register access or sun4v hypervisor perf register calls as appropriate.
- `register_perf_hsvc()` and `unregister_perf_hsvc()` manage HV API group registration.
- `pcr_arch_init()` chooses ops by `tlb_type` and `sun4v_chip_type`, then calls `nmi_init()`.

## Control Flow
Perf initialization calls `pcr_arch_init()`. On hypervisor systems, the code selects an HV perf group by chip type, registers HV API version 1.0, chooses PCR ops, and initializes NMI support. On cheetah/cheetah_plus it uses direct `%pcr/%pic` ops. Spitfire is rejected because it lacks usable profile counter overflow interrupts. High-PIL counter events that need normal IRQ-work semantics call into the deferred soft interrupt path.

## State and Persistence
Global runtime state includes `pcr_ops` and HV service group/version fields. PCR/PIC hardware registers and HV perf registers are modified through ops. No persistent storage exists.

## Dependencies and Integration Points
Depends on SPARC PIL/NMI/ASI/hypervisor support, irq_work, ftrace, CPU data, and PCR bit definitions. It integrates directly with `perf_event.c` and NMI watchdog code.

## Risks and Edge Cases
- Wrong chip-type mapping can register the wrong HV group or use incompatible PCR bit layout.
- Hypervisor register writes often ignore returned status after best-effort calls.
- N2 HT trace writes fall back to direct PCR writes if HV setperf fails.
- Counter interrupt context is high priority, so work must be deferred to avoid normal IRQ locking assumptions.

## Test Signals
Perf init should report supported PMU only when `pcr_arch_init()` succeeds. NMI watchdog and perf should not run concurrently on the same counters. Deferred irq_work should execute after performance counter interrupt paths raise the softint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/perf_event.c

## Purpose
Implements sparc64 hardware performance event support for the Linux perf subsystem. It maps generic/raw/cache perf events to SPARC PMU encodings, schedules limited hardware counters, programs PCR/PIC registers through `pcr_ops`, handles overflow NMIs, arbitrates with the NMI watchdog, and captures kernel/user callchains.

## Important APIs, Types, and Functions
- `struct cpu_hw_events` tracks per-CPU active events, encoded event values, current counter assignment, PCR shadow values, enable state, and transaction flags.
- `struct perf_event_map` encodes hardware event selector plus allowed PIC mask.
- `struct sparc_pmu` describes PMU generation behavior: event/cache maps, counter accessors, PCR field shifts/masks, trace bits, conflict flags, number of PCR/PIC registers, and max events.
- PMU descriptions cover Ultra3, Niagara1, Niagara2/3, Niagara4/5, and SPARC M7.
- `sparc_check_constraints()` assigns counter indexes and rejects conflicts for older two-counter chips.
- `sparc_pmu_event_init()`, `sparc_pmu_add()`, `sparc_pmu_del()`, `sparc_pmu_start()`, `sparc_pmu_stop()`, and `sparc_pmu_read()` implement the Linux `struct pmu` contract.
- `sparc_perf_event_update()` and `sparc_perf_event_set_period()` maintain counts and reload 32-bit counters.
- `perf_event_nmi_handler()` handles overflow notifications from the die notifier.
- `perf_callchain_kernel()` and `perf_callchain_user()` collect stack traces for samples.

## Control Flow
`pure_initcall(init_hw_perf_events)` calls `pcr_arch_init()`, selects a PMU based on `sparc_pmu_type`, registers a PMU named `cpu`, and installs an NMI die notifier. Event initialization maps attributes to hardware encodings, checks group constraints, grabs PMCs from the NMI watchdog, and sets default sample periods. Add/start/enable paths place events into per-CPU arrays, assign counters, build PCR values, and program PIC periods. On NMI, counters are updated, overflowed counters are reloaded, and perf overflow delivery is invoked.

## State and Persistence
Per-CPU `cpu_hw_events` is the main scheduler state. Global state includes `sparc_pmu`, `pmu`, `active_events`, and `pmc_grab_mutex`. PCR/PIC hardware state is shadowed in `cpuc->pcr[]`. Event counts live in perf `local64` fields. No disk-persistent state exists.

## Dependencies and Integration Points
Depends on Linux perf, kprobes, ftrace graph tracing, scheduler clock, atomic/mutex APIs, user access helpers, stack validation helpers, NMI infrastructure, and `pcr_ops` from `pcr.c`. It integrates with generic perf through `perf_pmu_register()` and with NMI notifications through `register_die_notifier()`.

## Risks and Edge Cases
- Older PMUs have shared PCR enable bits, so all hardware events in a group must have matching user/kernel/hypervisor excludes.
- Niagara1 has a hardwired/free-running upper counter, requiring unusual no-op event handling.
- T4+ disables hypervisor tracing because precise overflows are lost in HV mode.
- `sparc_pmu_commit_txn()` can return errors without clearing transaction flags in some failure paths.
- Overflow detection depends on 32-bit sign/overflow behavior (`val & (1ULL << 31)`).
- Perf and NMI watchdog share PMCs; incorrect grab/release accounting can leave watchdog disabled or counters corrupted.
- User callchain collection runs with page faults disabled and must restore fault state.

## Test Signals
Perf init should print the selected PMU type or no-support message. `perf stat` and sampling should work for supported generic events, reject unsupported/nonsense cache events, enforce group constraints, and restore the NMI watchdog after events are destroyed. NMI sampling should produce callchains without fault-state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pmc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pmc.c

## Purpose
Implements the Power Management Controller driver for SPARCstation Voyager. It maps the PMC register block and installs a Swift CPU idle callback that signals hardware idle state.

## Important APIs, Types, and Functions
- `pmc_probe()` maps the OF resource named `SUNW,pmc` and assigns `sparc_idle`.
- `pmc_swift_idle()` sets `PMC_IDLE_ON` in `PMC_IDLE_REG`, optionally toggling an AUXIO LED under debug.
- `pmc_readb()` and `pmc_writeb()` wrap SBus byte accesses.
- `pmc_driver` matches OF node name `SUNW,pmc`; `pmc_init()` registers it through `__initcall`.

## Control Flow
After SBus is initialized, `pmc_init()` registers the platform driver. Probe maps registers and, unless `PMC_NO_IDLE` is defined, replaces the architecture idle function with `pmc_swift_idle()`. Each idle entry writes the PMC idle bit.

## State and Persistence
Static `regs` stores the mapped I/O base. Runtime state is limited to the global `sparc_idle` function pointer and the PMC idle register. No persistent storage exists.

## Dependencies and Integration Points
Depends on OF platform probing, SBus I/O helpers, AUXIO debug support, and SPARC processor idle hooks.

## Risks and Edge Cases
- Probe does not provide a remove path or unmap registers.
- Replacing global `sparc_idle` assumes only one PMC and no competing idle provider.
- Hardware behavior is controlled by compile-time debug/disable macros, not runtime configuration.

## Test Signals
Boot should log `pmc: power management initialized`. On Voyager hardware, entering idle should write `PMC_IDLE_ON`; debug LED toggling can confirm idle callback execution if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/power.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/power.c

## Purpose
Implements a simple OF platform power-button/control-register driver. It maps a `power` node control register and, when the node advertises a button interrupt, requests an IRQ that triggers orderly shutdown.

## Important APIs, Types, and Functions
- `power_probe()` maps the first resource, logs the control register address, and conditionally registers the IRQ handler.
- `has_button_interrupt()` validates the IRQ value and requires a `button` property.
- `power_handler()` calls `orderly_poweroff(true)` and returns `IRQ_HANDLED`.
- `power_driver` matches OF node name `power` and is registered with `builtin_platform_driver()`.

## Control Flow
During built-in platform-driver registration, matching `power` nodes invoke `power_probe()`. Probe maps four bytes of control register and checks `op->archdata.irqs[0]`. If the IRQ is valid and the OF node has `button`, the handler is installed. Button interrupts then request an orderly userspace-assisted poweroff.

## State and Persistence
Static `power_reg` stores the mapped control register address but is not otherwise used in this file. Shutdown is delegated to the kernel reboot/poweroff subsystem. No persistent storage exists.

## Dependencies and Integration Points
Depends on OF/platform resources, SPARC I/O mapping, interrupt APIs, and Linux reboot orderly poweroff support.

## Risks and Edge Cases
- Probe does not check `of_ioremap()` failure before logging and continuing.
- `op->archdata.irqs[0]` is used without checking IRQ count.
- The handler has a FIXME to inspect hardware status registers, so every registered interrupt is treated as a button event.
- No remove/unmap path exists.

## Test Signals
Boot should log the `power` control register address. Systems with a valid button IRQ and `button` property should request the IRQ successfully. Pressing the power button should invoke `orderly_poweroff(true)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/power.c -->
