# Research: subset-b-004995

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/eisa.c

## Purpose
This file provides PA-RISC platform support for the Mongoose and Wax EISA bus adapters. It bridges EISA-style I/O port access, 8259-compatible interrupt handling, EEPROM discovery, and Linux EISA root registration into the PA-RISC `parisc_driver` model. It also exposes EISA port helpers for non-PCI builds and accepts the `eisa_irq_edge=` boot option for ISA cards installed in EISA slots.

## Important APIs, Types, And Functions
The main persistent object is the singleton `eisa_dev`, which embeds `struct pci_hba_data`, the EEPROM physical address, and an `eisa_root_device`. Port operations are `eisa_in8/16/32()` and `eisa_out8/16/32()`, backed by `eisa_permute()` and GSC MMIO accesses. Interrupt support is implemented by `eisa_mask_irq()`, `eisa_unmask_irq()`, `eisa_irq()`, `init_eisa_pic()`, and the `eisa_interrupt_type` irq chip. Probe and registration are handled by `eisa_probe()` and `parisc_eisa_init()`. Polarity helpers `eisa_make_irq_level()` and `eisa_make_irq_edge()` are called by the EEPROM enumerator and boot-parameter parser.

## Control Flow
`parisc_eisa_init()` registers a driver matching Mongoose and Wax bus adapters. `eisa_probe()` claims the EISA memory and I/O resources, registers the host bridge, requests the parent PA-RISC IRQ, installs irq chips for IRQs 0-15, sets `EISA_bus`, resolves and maps the EEPROM address, calls `eisa_enumerator()` to parse configured slots, initializes the PIC, and finally registers an EISA root device when enumeration succeeds. Runtime I/O uses `eisa_permute()` to translate legacy port numbers into the PA-RISC EISA MMIO window. Interrupt delivery enters through the Wax/Mongoose IRQ, reads the EISA interrupt acknowledge register, masks and acknowledges the selected 8259 line, calls `generic_handle_irq()`, then unmasks the line.

## State And Persistence
Driver state is global and effectively permanent after boot: the single adapter object, `eisa_eeprom_addr`, `master_mask`, `slave_mask`, `eisa_irq_level`, and `eisa_irq_configured`. Hardware state includes claimed address windows, the mapped EEPROM, PIC mask registers, and edge/level trigger registers. There is no removal path; failures during probe unwind IRQ/resource mapping only up to the failing point.

## Dependencies And Integration Points
This code depends on PA-RISC GSC MMIO helpers, `parisc_device` matching, CCIO resource routing, PCI HBA registration infrastructure, Linux generic IRQ handling, Linux EISA core registration, and the EISA EEPROM/enumerator interfaces. `eisa_eeprom.c` consumes `eisa_eeprom_addr`, and `eisa_enumerator.c` calls the IRQ polarity helpers before `init_eisa_pic()` programs the trigger registers.

## Risks
The driver assumes only one EISA adapter because the hardware cannot be flexed. PIC programming and the mask cache must remain synchronized under `eisa_irq_lock`; otherwise interrupts can be lost or left enabled. Error unwinding does not release every resource in every failure case, which is acceptable for boot-only hardware but risky for refactors. The boot parser loops on invalid values without advancing the cursor, so malformed input is worth checking carefully. EEPROM-derived IRQ polarity and user-forced edge polarity can conflict, producing warnings but still applying the last setting.

## Test Signals
Useful signals are adapter discovery logs, successful resource claims, `/proc/ioports` and `/proc/iomem` EISA ranges, registered EISA slots, readable EEPROM, and successful interrupt delivery for both ISA edge-triggered and EISA level-triggered cards. Regression tests should stress IRQ 2 cascade handling, boot-time `eisa_irq_edge=10,11`, failed EEPROM mapping, and slot enumeration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/eisa_eeprom.c

## Purpose
This file exposes the PA-RISC EISA adapter EEPROM as a read-only misc character device named `eisa_eeprom`. It gives userspace a bounded byte stream over the firmware/configuration EEPROM that `eisa.c` mapped during adapter probe.

## Important APIs, Types, And Functions
The public surface is the misc device `eisa_eeprom_dev` with file operations `eisa_eeprom_llseek()`, `eisa_eeprom_read()`, `eisa_eeprom_open()`, and `eisa_eeprom_release()`. The implementation relies on global `eisa_eeprom_addr` from the EISA bus driver and the fixed EEPROM length `HPEE_MAX_LENGTH`.

## Control Flow
Module initialization checks whether `eisa_eeprom_addr` is set; if not, it returns `-ENODEV`, so the device appears only after EISA adapter probe mapped the EEPROM. Open rejects write mode. Reads clamp the requested range to `HPEE_MAX_LENGTH`, allocate a temporary kernel buffer, copy bytes one by one from the MMIO EEPROM with `readb()`, advance `*ppos`, and then copy the snapshot to userspace. Seeking is delegated to `fixed_size_llseek()`.

## State And Persistence
The file owns no persistent hardware state. It observes the mapped EEPROM and uses the file position as per-open state. EEPROM contents are firmware/hardware configuration data and are not modified by this driver.

## Dependencies And Integration Points
It depends on the EISA core mapping `eisa_eeprom_addr`, PA-RISC `asm/eisa_eeprom.h` layout constants, Linux miscdevice registration, and `copy_to_user()` semantics. It is a diagnostic/export layer over the same EEPROM data consumed by `eisa_enumerator.c`.

## Risks
The read path allocates `count` bytes with `kmalloc()` after clamping to the small EEPROM size; future size changes could make large reads more expensive. Reads are not locked against unmap, but the EISA adapter is boot-time-only and has no removal path. Returning zero for negative or out-of-range positions follows simple EOF behavior but means invalid negative offsets do not report `-EINVAL`.

## Test Signals
Test by confirming `/dev/eisa_eeprom` registration on EISA systems, rejection of write opens, bounded seek behavior, short reads at EOF, and byte-for-byte consistency with the enumerator’s EEPROM parsing. Fault-injection signals include `kmalloc()` failure returning `-ENOMEM` and `copy_to_user()` failure returning `-EFAULT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa_enumerator.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/eisa_enumerator.c

## Purpose
This file parses HP PA-RISC EISA EEPROM records, enables detected boards, claims their memory and I/O resources, initializes configured ports, and records IRQ polarity for the EISA PIC setup. It is the platform-specific discovery pass that runs before the Linux EISA core independently enumerates the root bus.

## Important APIs, Types, And Functions
The entry point is `eisa_enumerator()`. EEPROM decoding helpers include `get_8()`, `get_16()`, `get_24()`, `get_32()`, and `print_eisa_id()`. Per-record handlers are `configure_memory()`, `configure_irq()`, `configure_dma()`, `configure_port()`, `configure_port_init()`, `configure_choise()`, `configure_type_string()`, and `configure_function()`. Slot-level orchestration is split between `init_slot()` and `parse_slot_config()`.

## Control Flow
`eisa_enumerator()` copies the entire EEPROM into a static buffer using `gsc_readb()`, reads the EEPROM header, and walks each configured slot. For each slot, `init_slot()` optionally reads the slot ID from the EISA product ID port, verifies it against EEPROM expectations, and enables the board if supported. If the slot has in-range configuration data, `parse_slot_config()` walks function records, skips disabled or free-form functions, and consumes sections in the order implied by flags: type, memory, IRQ, DMA, I/O port, and port initialization. Memory and port sections allocate `struct resource` objects and call `request_resource()` under the EISA HBA parent resources; IRQ sections call `eisa_make_irq_level()` or `eisa_make_irq_edge()`.

## State And Persistence
The enumerator persists resource reservations and hardware side effects. Resource objects allocated for claimed EISA memory/I/O ranges intentionally survive for the lifetime of the booted kernel. Port-init records perform immediate `inb/outb/inw/outw/inl/outl` operations. IRQ polarity is stored indirectly in `eisa.c` global trigger-state variables before the PIC is initialized.

## Dependencies And Integration Points
It depends on the EEPROM record definitions in `asm/eisa_eeprom.h`, EISA I/O helpers routed through PA-RISC port access, Linux resource trees, and the EISA PIC trigger helpers in `eisa.c`. The returned slot count becomes `eisa_root_device.slots` in `eisa_probe()`.

## Risks
The parser trusts EEPROM lengths heavily and has only coarse length mismatch checks after walking each function. Several record types are incomplete or noted as TODOs: free-form configuration, CRC validation, masked port init details, and memory decode modes beyond the implemented form. Resource allocation failures return immediately but already-claimed earlier resources are not unwound. `configure_port()` computes `end` as base plus size plus one, which should be reviewed against Linux resource inclusive-end convention. Port-init with masks has suspicious operand grouping in some reads and is marked unverified by the original code.

## Test Signals
Good signals include correct EISA ID logging, expected resource reservations, initialized IRQ polarity before `init_eisa_pic()`, and slot count matching EEPROM header. Tests should cover absent cards, ID mismatches, disabled functions, free-form functions, malformed lengths, memory/port claim collisions, and multi-function cards with mixed memory, IRQ, DMA, and port-init records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/eisa_enumerator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/gsc.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/gsc.c

## Purpose
This file provides common interrupt and setup infrastructure for PA-RISC GSC ASICs such as ASP, LASI, and Wax. It allocates transaction-based interrupt targets, demultiplexes local ASIC interrupt bits into Linux IRQs, implements a shared IRQ chip for local GSC lines, and walks child devices to assign platform IRQs.

## Important APIs, Types, And Functions
Exported APIs are `gsc_alloc_irq()`, `gsc_claim_irq()`, `gsc_asic_intr()`, `gsc_find_local_irq()`, `gsc_assign_irq()`, `gsc_asic_assign_irq()`, `gsc_fixup_irqs()`, and `gsc_common_setup()`. The IRQ chip `gsc_asic_interrupt_type` provides mask/unmask and SMP affinity support. `struct gsc_asic` and `struct gsc_irq` are declared in `gsc.h`.

## Control Flow
ASIC drivers allocate or claim a transaction IRQ with `gsc_alloc_irq()`/`gsc_claim_irq()`, request that IRQ with `gsc_asic_intr()` as the handler, call `gsc_common_setup()` to initialize local IRQ mappings and reserve the ASIC HPA range, then call `gsc_fixup_irqs()` with a chip-specific mapping callback. At runtime, `gsc_asic_intr()` reads `OFFSET_IRR`, finds each set bit, looks up the assigned global IRQ in `global_irq[]`, and calls `generic_handle_irq()`. Mask/unmask callbacks convert a Linux IRQ back to a local bit and update the ASIC interrupt mask register.

## State And Persistence
Each `gsc_asic` stores its HPA, EIM value, transaction interrupt tuple, and a 32-entry local-to-global IRQ map. `gsc_assign_irq()` uses a static monotonically increasing IRQ allocator from `GSC_IRQ_BASE` to `GSC_IRQ_MAX`. Register programming in IMR/IAR persists in hardware until reboot or later mask changes.

## Dependencies And Integration Points
The file depends on PA-RISC transaction IRQ allocation (`txn_*`, `cpu_*` helpers), generic IRQ dispatch, `parisc_device` hierarchy traversal, and GSC MMIO read/write helpers. LASI, ASP, Wax, and related drivers use this file to route child device interrupts.

## Risks
`gsc_find_local_irq()` returns `NO_IRQ` when a mapping is absent; mask/unmask shifts by that value if called on an unmapped IRQ, so callers must only install valid mappings. The debug print in mask/unmask references `imr` before assignment when debugging is enabled. `gsc_assign_irq()` has global static state and no locking, but it runs during early platform initialization. Affinity changes assume the ASIC supports IAR reprogramming except for ASP revision `0x70`.

## Test Signals
Test signals include successful child IRQ assignment, IRR demultiplexing for multiple simultaneous local bits, mask/unmask register updates, SMP affinity migration on supported ASICs, and correct handling of faulty path recursion in `gsc_fixup_irqs()`. Lockdep and IRQ tracing are useful around nested `generic_handle_irq()` dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/gsc.h -->
# sources/distributed-fs/ceph-client/drivers/parisc/gsc.h

## Purpose
This private header defines the shared register offsets, constants, data structures, and function prototypes used by PA-RISC GSC ASIC drivers.

## Important APIs, Types, And Functions
Register offsets are `OFFSET_IRR`, `OFFSET_IMR`, `OFFSET_IPR`, `OFFSET_ICR`, and `OFFSET_IAR`. `GSC_EIM_WIDTH` defines the transaction interrupt width. `struct gsc_irq` stores transaction address/data and Linux IRQ number. `struct gsc_asic` stores parent device, HPA, chip identity, EIM, allocated IRQ tuple, and a 32-line IRQ map. The header declares `gsc_common_setup()`, `gsc_alloc_irq()`, `gsc_claim_irq()`, `gsc_assign_irq()`, `gsc_find_local_irq()`, `gsc_fixup_irqs()`, `gsc_asic_assign_irq()`, and `gsc_asic_intr()`.

## Control Flow
This file has no executable control flow. It establishes the contract followed by `gsc.c` and chip drivers such as `lasi.c`: a chip driver fills `struct gsc_asic`, allocates a parent transaction IRQ, registers `gsc_asic_intr()`, initializes common state, and assigns local IRQs to child `parisc_device` nodes.

## State And Persistence
The structures declared here describe persistent per-ASIC interrupt state stored by chip drivers. The header itself owns no storage.

## Dependencies And Integration Points
It includes Linux interrupt declarations and PA-RISC hardware/device definitions. It is intentionally local to `drivers/parisc` and aligns with the GSC register model used by LASI/ASP/Wax-style bridge drivers.

## Risks
The fixed 32-entry `global_irq` array encodes an architectural assumption shared by all users. Any chip with a wider local interrupt register would need a new contract. The header has no include guard in the shown file, so repeated inclusion depends on current include patterns not causing duplicate declarations with side effects.

## Test Signals
Compile coverage is the main signal for this header. Runtime signals come from users: valid local IRQ assignment, correct register offsets, and stable ABI between `gsc.c` and chip-specific drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/hppb.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/hppb.c

## Purpose
This file is the HP-PB bus driver for NOVA and K-Class PA-RISC systems. It claims GeckoBoa bus-controller MMIO windows so downstream HP-PB bus space is represented in the kernel resource tree.

## Important APIs, Types, And Functions
The local state type is `struct hppb_card`, containing the controller HPA, claimed MMIO resource, and a linked-list pointer. The driver entry points are `hppb_probe()` and `hppb_init()`, registered through a PA-RISC device table for GeckoBoa BCPORT devices.

## Control Flow
At `arch_initcall`, `hppb_init()` registers the `gecko_boa` PA-RISC driver. `hppb_probe()` appends or reuses a `hppb_card` entry, records the device HPA, reads the bus low/high MMIO bounds from the controller’s `bc_module` registers via `gsc_readl()`, and calls `ccio_request_resource()` to claim the resulting memory range. It logs whether the range was claimed and returns zero so the platform device is considered handled.

## State And Persistence
The file maintains a simple linked list rooted in `hppb_card_head`; entries persist for the lifetime of the system. Claimed resources remain inserted in the CCIO/iomem resource tree. There is no removal or cleanup path.

## Dependencies And Integration Points
It depends on PA-RISC parisc-driver matching, GSC MMIO reads, CCIO resource routing, and `struct bc_module` layout from architecture headers. It shares the `iommu.h` CCIO abstraction used by other PA-RISC bus code.

## Risks
The linked list is unsynchronized but populated only during early device discovery. If allocation of a second card fails, probe returns `1` rather than a conventional negative errno. The driver only logs resource-claim failure and still returns success, which may hide overlapping or invalid platform resource descriptions.

## Test Signals
Signals include GeckoBoa discovery logs, correct `io_io_low`/`io_io_high` decoding, resource tree entries labeled `HP-PB Bus`, and no conflicts with CCIO-managed regions. Multi-controller systems should verify list allocation and logging for each bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/hppb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iommu-helpers.h -->
# sources/distributed-fs/ceph-client/drivers/parisc/iommu-helpers.h

## Purpose
This header contains common inline scatter-gather DMA mapping helpers for PA-RISC IOMMU drivers. It separates SG coalescing and I/O page-directory filling so SBA, CCIO, and similar controllers can share the algorithm while supplying controller-specific range allocation and PDIR entry programming callbacks.

## Important APIs, Types, And Functions
`iommu_coalesce_chunks()` walks an SG list, detects virtually contiguous chunks within device segment limits, allocates IOVA ranges through a callback, and marks stream starts using `PIDE_FLAG` in `sg_dma_address()`. `iommu_fill_pdir()` consumes those markers, programs PDIR entries through `iommu_io_pdir_entry()`, and rewrites the SG list into DMA-visible address/length pairs.

## Control Flow
Mapping is a two-pass process. The first pass starts a DMA stream at each SG head, clears previous DMA fields, extends the stream while virtual addresses are contiguous, page-boundary conditions are valid, and max segment size/boundary limits are respected, then allocates a PDIR range and stores the index plus original offset in the stream head. The second pass walks the original SG entries, starts a new output DMA entry whenever `PIDE_FLAG` is seen, initializes the final DMA address, accumulates lengths into the coalesced entry, and calls the supplied PDIR writer for each I/O page.

## State And Persistence
The helpers mutate the caller’s scatterlist in place. Temporary state is encoded in `sg_dma_address()` and `sg_dma_len()` between passes. Persistent hardware state is created only through the caller’s callbacks.

## Dependencies And Integration Points
The helpers depend on Linux scatterlist accessors, DMA segment-size/boundary helpers, PA-RISC IOVP constants, `PIDE_FLAG`, optional `ZX1_SUPPORT`, and controller-specific `struct ioc` fields such as `pdir_base` and `ibase`. `sba_iommu.c` includes this file after defining the required macros and callback types.

## Risks
The implementation assumes SG entries expose meaningful kernel virtual addresses via `sg_virt()`, which is central to PA-RISC coherence handling. Incorrect `PIDE_FLAG` definitions or DMA address reuse would corrupt stream boundaries. The second pass deliberately decrements `dma_sg` before the loop for speed, making off-by-one changes risky. Boundary and segment calculations must stay aligned with DMA API expectations.

## Test Signals
Test with single-entry, multi-entry contiguous, non-contiguous, offset, max-segment, and segment-boundary SG lists. Verify returned mapping count, final `sg_dma_address()`/`sg_dma_len()` values, PDIR entry count, and correct behavior with non-zero IOVA bases under `ZX1_SUPPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iommu-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iommu.h -->
# sources/distributed-fs/ceph-client/drivers/parisc/iommu.h

## Purpose
This header provides the PA-RISC bus-to-IOMMU lookup and abstracts CCIO/SBA resource and IOMMU hooks for platform bus drivers.

## Important APIs, Types, And Functions
`parisc_walk_tree()` returns the nearest `struct pci_hba_data` cached in a device’s `platform_data` or inherited from an ancestor. `GET_IOC()` returns the `struct ioc` IOMMU pointer stored in that HBA. The header declares or stubs `ccio_get_iommu()`, `ccio_request_resource()`, `ccio_allocate_resource()`, and declares `sba_get_iommu()`.

## Control Flow
Runtime lookup first checks `dev->platform_data`; if missing, it walks parent devices until an ancestor with HBA data is found, then caches that pointer back on the original device. DMA mapping paths call `GET_IOC()` to reach the correct controller. Resource-request users call CCIO helpers when configured or generic iomem resource insertion/allocation when CCIO support is absent.

## State And Persistence
The only mutation is caching inherited HBA data in `dev->platform_data`. That makes later DMA/resource lookups faster but assumes the device hierarchy and HBA association are stable.

## Dependencies And Integration Points
This file integrates PA-RISC PCI HBA data with IOMMU drivers, LBA/EISA/HP-PB resource management, and the generic DMA mapping code. It depends on Linux PCI resources and PA-RISC `parisc_device` declarations.

## Risks
Caching in `platform_data` can conflict with other code if a child device expects to own that field for unrelated data. `GET_IOC()` returns `NULL` when no HBA data is found, so DMA operations must handle that path. Stubbed CCIO helpers insert resources directly into `iomem_resource`, which changes behavior on non-CCIO builds.

## Test Signals
Signals include DMA mapping succeeding for PCI children whose HBA data is inherited from a bridge, CCIO-enabled and CCIO-disabled builds compiling, and resource requests landing under the expected parent tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iosapic.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/iosapic.c

## Purpose
This file manages PA-RISC I/O SAPIC interrupt routing for PCI line interrupts. It reads firmware Interrupt Routing Tables, registers integrated I/O SAPIC blocks exposed by LBA host bridges, translates PCI interrupt pins into I/O SAPIC input lines, allocates CPU transaction IRQs, and programs I/O SAPIC redirection table entries.

## Important APIs, Types, And Functions
External entry points are `iosapic_register()`, `iosapic_fixup_irq()`, and on 64-bit builds `iosapic_serial_irq()`. Initialization is `iosapic_init()` and `iosapic_load_irt()`. Routing helpers include `irt_find_irqline()`, `iosapic_xlate_pin()`, `iosapic_set_irt_data()`, `iosapic_rd_irt_entry()`, and `iosapic_wr_irt_entry()`. The IRQ chip `iosapic_interrupt_type` supplies mask, unmask, ack, eoi, and SMP affinity callbacks.

## Control Flow
At boot, `iosapic_init()` loads the firmware IRT through PAT PDC or legacy PDC calls. LBA probe later calls `iosapic_register()` with the integrated I/O SAPIC HPA and mapped address; registration verifies that the HPA exists in the IRT, reads the SAPIC version, allocates one `vector_info` per IRdT entry, and links the SAPIC into `iosapic_list`. During PCI bus fixup, `iosapic_fixup_irq()` translates the device’s interrupt pin, handles SuperIO quirks, locates the matching IRT entry, allocates a transaction IRQ for the SAPIC input if not already allocated, fills EOI data, claims the CPU IRQ with the I/O SAPIC irq chip, and assigns `pcidev->irq`. Unmasking programs the redirection entry from the saved IRT polarity/trigger data and transaction address/data, then sends an EOI.

## State And Persistence
Global state includes the firmware IRT pointer/count and the linked list of registered I/O SAPICs. Each `iosapic_info` persists mapped register base, HPA, version, vector count, and `vector_info` array. Each vector persists its IRT entry, transaction IRQ/address/data, EOI register/data, and INTIN number. Hardware redirection table entries persist until mask/unmask/affinity changes.

## Dependencies And Integration Points
The driver depends on PDC/PAT firmware interfaces, PCI interrupt-pin semantics, PA-RISC transaction IRQ helpers, CPU IRQ claim/eoi helpers, Linux IRQ core, LBA host bridge registration, SuperIO quirks, and `iosapic_private.h` structures. `lba_pci.c` relies on it during `lba_fixup_bus()`.

## Risks
The code assumes a single global IRT outside future multi-cell support. Many failures are handled by `BUG_ON()` or `panic()`, reflecting early boot expectations. If an IRT entry is missing, PCI devices may be left without usable interrupts. Vector allocation currently happens during PCI enumeration for every present device rather than when a driver requests the IRQ. Polarity/trigger correctness depends entirely on firmware IRT data. Affinity updates rewrite only the destination half and must preserve the low entry correctly.

## Test Signals
Signals include successful IRT loading, I/O SAPIC registration per LBA, correct IRQ assignment for devices behind PCI-PCI bridges, shared INTIN reuse without duplicate allocation, correct level-low programming, EOI delivery, SMP affinity migration, and SuperIO USB/legacy routing. Negative tests include devices with `INTERRUPT_PIN=0`, missing IRT entries, and legacy firmware without I/O SAPIC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iosapic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iosapic_private.h -->
# sources/distributed-fs/ceph-client/drivers/parisc/iosapic_private.h

## Purpose
This private header defines the firmware routing-table and runtime state structures used exclusively by the PA-RISC I/O SAPIC driver.

## Important APIs, Types, And Functions
`struct irt_entry` describes 16-byte firmware I/O SAPIC routing entries: type, length, interrupt type, polarity/trigger, source PCI device/pin, source bus/segment, destination INTIN, and destination SAPIC address. Constants define IRT type/length, vectored interrupt value, polarity and trigger encodings, and masks for PCI source fields. `struct vector_info` stores per-INTIN runtime state. `struct iosapic_info` stores per-controller runtime state. Optional IA64-only SAPIC structures are retained under `__IA64__`.

## Control Flow
This header has no executable flow. `iosapic.c` fills `irt_entry` arrays from firmware, attaches one `vector_info` to each hardware INTIN, and links `iosapic_info` objects as LBAs register integrated SAPICs.

## State And Persistence
The declared structures hold persistent boot-time routing and runtime IRQ programming state. `vector_info` includes both firmware-derived routing (`irte`) and Linux/CPU IRQ data (`txn_irq`, `txn_addr`, `txn_data`, `eoi_addr`, `eoi_data`).

## Dependencies And Integration Points
The header is private to `drivers/parisc/iosapic.c` and mirrors PDC/PAT firmware table layout. Its fields feed Linux IRQ chip data and PCI IRQ fixup.

## Risks
The comments warn that structure field order matters for 64-bit packing. Any change to `struct irt_entry` layout can break direct firmware table decoding. Multi-cell support is stubbed but not active, so adding platforms with multiple routing tables would need structural changes.

## Test Signals
Compile-time structure layout and runtime IRT decoding are the primary signals. Debug dumps in `iosapic.c` should show expected 16-byte entries and matching SAPIC addresses/INTINs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/iosapic_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/lasi.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/lasi.c

## Purpose
This file is the driver for the LASI GSC bus adapter ASIC. It initializes the LASI interrupt controller, maps child devices to local interrupt lines, registers chassis LED support for LASI-based machines, and provides a power-off callback using the LASI power control register.

## Important APIs, Types, And Functions
Key functions are `lasi_choose_irq()`, `lasi_init_irq()`, optional `lasi_led_init()`, `lasi_power_off()`, `lasi_init_chip()`, and `lasi_init()`. It uses `struct gsc_asic` plus GSC helper APIs from `gsc.c`.

## Control Flow
At `arch_initcall`, the PA-RISC driver matches LASI bus adapters. Probe allocates a `gsc_asic`, records HPA/name/version, initializes chassis LEDs when configured, masks LASI interrupts and clears pending state, resets selected onboard devices, allocates a transaction IRQ, requests it with `gsc_asic_intr()`, writes the EIM to LASI’s IAR, calls `gsc_common_setup()`, walks child devices with `gsc_fixup_irqs()` using `lasi_choose_irq()`, and registers a sys-off power-off handler. `lasi_choose_irq()` maps known child `sversion` values to local IRQ bit numbers and calls `gsc_asic_assign_irq()`.

## State And Persistence
Per-chip state is the allocated `gsc_asic` and its local IRQ map. Hardware state includes masked/unmasked LASI interrupt bits, device reset writes, the IAR transaction target, LED register selection, and power control behavior. There is no removal path.

## Dependencies And Integration Points
LASI depends on GSC common interrupt infrastructure, PA-RISC PDC address validation, LED registration from `led.c`, reboot/sys-off infrastructure, and `parisc_device` child enumeration. It provides IRQs to onboard serial, LAN, SCSI, audio, PS/2, floppy, and other LASI-attached devices.

## Risks
The child IRQ mapping is a hard-coded table by `sversion` and one `hw_path` special case; new or misidentified devices receive no IRQ. Device reset writes are intentionally selective because firmware already initialized some devices. The power-off handler writes hardware and may not return. Error paths free allocated IRQ/state only for early failures before successful setup.

## Test Signals
Signals include LASI version log, successful parent IRQ request, child device IRQ assignment, IMR/IAR programming, functional onboard devices, LED registration on supported machines, and system power-off through LASI. Regression tests should cover Mirage/Electra LED address offsets and Gecko single-LED behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/lasi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/lba_pci.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/lba_pci.c

## Purpose
This file is the PCI Lower Bus Adapter host-bridge driver for PA-RISC systems using Elroy, Mercury, and Quicksilver LBAs. It implements PCI config-space access workarounds, I/O port accessors, firmware resource discovery, PCI root-bus creation, I/O SAPIC interrupt fixup, and host-bridge resource registration.

## Important APIs, Types, And Functions
PCI config ops are `elroy_cfg_read/write()` and `mercury_cfg_read/write()`, with helper workarounds in `lba_rd_cfg()` and `lba_wr_cfg()`. PCI BIOS integration is `lba_fixup_bus()` in `lba_bios_ops`. Resource discovery is split between `lba_pat_resources()` and `lba_legacy_resources()`. Hardware setup is `lba_hw_init()`. Probe is `lba_driver_probe()`. I/O port ops are `lba_astro_port_ops` and, on 64-bit PAT systems, `lba_pat_port_ops`. `lba_set_iregs()` is exported to SBA initialization to program LBA IBASE/IMASK routing. PCI quirks hide unusable Diva/Tosca onboard devices.

## Control Flow
`lba_init()` registers the PA-RISC bridge driver. Probe maps LBA registers, identifies chip revision, selects config ops, registers the integrated I/O SAPIC, allocates `struct lba_device`, registers HBA data, initializes hardware, discovers I/O/MMIO/bus resources through PAT or legacy firmware paths, truncates colliding LMMIO ranges, builds a root-bus resource list, creates the PCI root bus, scans children, optionally assigns PAT resources, enables later probe skipping on fragile Elroy config cycles, and adds discovered devices. During bus fixup, resources are claimed, device BARs are virtualized/claimed, PCI bridges are initialized, and non-bridge devices receive IRQs through `iosapic_fixup_irq()`.

## State And Persistence
Per-LBA state includes hardware revision, mapped register base, HBA resources, bus-number resource, I/O port translation base, IOSAPIC handle, IOMMU pointer from SBA, and flags such as `LBA_FLAG_SKIP_PROBE`. Global state includes `astro_iop_base`, `lba_next_bus`, and selected global PCI port/bios hooks. Hardware state includes LBA error config, arbitration masks, hard/soft fail mode, PCI reset state, and IBASE/IMASK registers programmed by SBA.

## Dependencies And Integration Points
The driver depends on PA-RISC PDC/PAT firmware, Linux PCI core root-bus APIs, I/O SAPIC IRQ routing, SBA IOMMU/resource helpers, PA-RISC HBA structures, and architecture register definitions in `asm/ropes.h`. It is the central integration point between platform firmware and normal Linux PCI enumeration.

## Risks
Elroy config access is highly workaround-sensitive: early revisions require disabling DMA arbitration, smart mode, probe writes, and error-status clearing to avoid fatal master aborts. PAT and legacy resource discovery have different address translations and collision behavior. Resource collisions can be truncated or logged without hard failure. Global PCI port hooks assume compatible host-bridge ordering. The `global_ioc_cnt` style issue is in SBA, but LBA relies on correct SBA parent initialization for DMA. Hiding devices by zeroing `dev->device` is effective but non-obvious to later fixups.

## Test Signals
Signals include root bus creation, stable config reads without HPMC, correct bus numbering, resource trees for I/O/LMMIO/ELMMIO, successful BAR claims, IRQ assignment through IOSAPIC, functional devices behind PCI-PCI bridges, PAT resource assignment for uninitialized devices, and correct I/O port access on both legacy and PAT firmware. Tests should include early Elroy revisions, Mercury/Quicksilver, C8000 LMMIO extension, and Diva/Tosca quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/lba_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/led.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/led.c

## Purpose
This file implements chassis LED and LCD support for HP PA-RISC machines. It discovers PDC-reported display hardware or accepts later LASI/ASP registration, exposes LED class devices with standard triggers, updates hardware-specific LED/LCD registers in software, and writes shutdown messages on reboot/halt/poweroff.

## Important APIs, Types, And Functions
The exported platform API is `register_led_driver()`, and the user-facing LCD helper is `lcd_print()`. Hardware writers are `led_ASP_driver()`, `led_LASI_driver()`, `led_LCD_driver()`, and `lcd_print_now()`. LED class integration uses `struct hppa_led`, `struct hppa_drvdata`, `set_led()`, `hppa_led_generic_probe()`, `platform_led_probe()`, and `platform_led_remove()`. Initialization is split between `early_led_init()` and `startup_leds()`.

## Control Flow
`early_led_init()` prepares a default Linux release string, handles KittyHawk-specific LCD defaults, otherwise queries `pdc_chassis_info()`, validates returned data, and calls `register_led_driver()`. `register_led_driver()` selects the correct hardware writer, records command/data registers, registers the platform LED driver, and installs a reboot notifier. Later `startup_leds()` registers the `platform-leds` device and reserves display MMIO regions. LED class brightness updates call `set_led()`, update the global bitmap, and invoke the selected hardware writer. LCD text changes set `lcd_new_text` and are flushed either immediately for LCD-only devices or during LED updates for combined LCD/LED devices.

## State And Persistence
Global state tracks display type, last LED bitmap, pending LCD text, LCD text buffer, KittyHawk no-LED flag, PDC LCD information, and the selected writer function. Registered LED class devices and MMIO resource reservations persist for the boot. Hardware state is entirely software-maintained through repeated register writes.

## Dependencies And Integration Points
The driver integrates PDC chassis info, PA-RISC GSC register writes, Linux LED class triggers, platform devices/drivers, reboot notifiers, LASI/ASP bridge discovery, and the power driver’s `lcd_print()` shutdown message. It avoids registering LEDs when running under QEMU.

## Risks
There is a single global LED/LCD backend; later registration attempts fail once `led_func_ptr` is set. Hardware command timing relies on PDC-provided microsecond delays. LCD writes are not protected by a lock, so concurrent messages/brightness changes can interleave. Platform driver registration happens before the platform device is registered, which is intentional but order-sensitive. `platform_register_drivers()` return value is ignored.

## Test Signals
Signals include PDC LCD/LED discovery logs, sysfs LEDs under `/sys/class/leds/`, working heartbeat/disk/network/panic triggers, correct LCD boot and shutdown messages, requested MMIO regions, no LED registration on QEMU, and correct KittyHawk/LASI/ASP hardware behavior. Test unknown PDC models, disabled `act_enable`, and machines where LASI registers LEDs after PDC discovery fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/pdc_stable.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/pdc_stable.c

## Purpose
This file exposes HP PA-RISC PDC Stable Storage through sysfs under `/sys/firmware/stable`. It provides read/write access to boot paths, path layers, autoboot/autosearch flags, OS-dependent storage areas, and diagnostic fields while caching firmware path entries in kernel objects.

## Important APIs, Types, And Functions
Core state is `struct pdcspath_entry`, which stores a stable-storage address, name, cached `pdc_module_path`, mapped Linux device, lock, readiness flag, and kobject. Path operations include `pdcspath_fetch()`, `pdcspath_store()`, `pdcspath_hwpath_read/write()`, `pdcspath_layer_read/write()`, and generic kobject show/store wrappers. Root sysfs attributes are implemented by `pdcs_size_read()`, `pdcs_autoboot_read/write()`, `pdcs_autosearch_read/write()`, `pdcs_timer_read()`, `pdcs_osid_read()`, `pdcs_osdep1_read/write()`, `pdcs_diagnostic_read()`, `pdcs_fastsize_read()`, and `pdcs_osdep2_read/write()`. Module lifecycle is `pdc_stable_init()`/`pdc_stable_exit()`.

## Control Flow
Initialization queries stable-storage size, rejects machines with less than 96 bytes, reads OSID, creates `/sys/firmware/stable`, installs root attributes, creates a `paths` kset, then fetches and registers the primary, alternative, console, and keyboard path entries. Each registered path gets `hwpath` and `layer` files plus a `device` symlink when a matching kernel device is found. Path writes parse user text, validate hardware paths by resolving to a real device, update cached state under a write lock, call `pdc_stable_write()`, and refresh the symlink. Flag and OS-dependent writes require `CAP_SYS_ADMIN`; OS-dependent writes also require Linux OSID.

## State And Persistence
The driver caches firmware data in `pdcspath_entry` objects but writes changes back to PDC Stable Storage, making them persistent across reboot. `pdcs_size` and `pdcs_osid` are initialized once. Read/write locks protect each path entry’s cached state. Sysfs kobjects and links persist until module exit.

## Dependencies And Integration Points
It depends on PDC stable-storage calls, PA-RISC hardware path conversion helpers, sysfs/kobject infrastructure, Linux capabilities, firmware kobject, and device model links. It exposes boot configuration to userspace tools and can affect firmware boot behavior.

## Risks
Writes can persistently corrupt firmware boot paths or OS-dependent data if parsing or user intent is wrong; warnings acknowledge limited recovery after failed PDC writes. Hardware path validation checks existence but not whether the target is a sensible boot device. Layer writes are less validated than hardware path writes. Some sysfs files trigger PDC calls and can be expensive. `pdcs_osdep2_read()` can print many lines into a single sysfs buffer if firmware reports a large optional area.

## Test Signals
Signals include `/sys/firmware/stable` creation, correct size/OSID reporting, path directories and device symlinks, successful readback after changing a path or layer, permission failures for unprivileged writes, and PDC read/write error propagation. Reboot validation should confirm persistent autoboot/autosearch/path changes match firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/pdc_stable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/power.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/power.c

## Purpose
This file implements the HP PA-RISC soft power switch driver. It enables the firmware soft-power facility, polls the power button in a kernel thread, exposes a sysctl to disable handling, prints LCD feedback, requests orderly shutdown, and re-enables firmware power-button behavior on panic.

## Important APIs, Types, And Functions
Important functions are `process_shutdown()`, `kpowerswd()`, `parisc_panic_event()`, `qemu_power_off()`, `power_init()`, and `power_exit()`. Sysctl registration is handled by `init_power_sysctl()` and `power_sysctl_table`, exposing `kernel/soft-power`. The driver uses architecture-specific diagnostic-register access macros for Gecko-style machines.

## Control Flow
`init_power_sysctl()` registers the sysctl at arch init. `power_init()` asks PDC for the soft-power register, enables the firmware soft-power button, reports the detected mode, registers a QEMU sys-off handler when appropriate, starts `kpowerswd()` when polling is useful, and registers a panic notifier. The polling thread sleeps according to `pwrsw_enabled`, reads either the soft-power MMIO bit or Gecko diagnostic register bit, resets an in-progress shutdown if released early, or calls `process_shutdown()` while held. After a configured hold interval, `process_shutdown()` writes an LCD message and sends `SIGINT` to CAD/init, falling back to `machine_power_off()` if signaling fails.

## State And Persistence
Persistent runtime state is `shutdown_timer`, `power_task`, and the sysctl-backed `pwrsw_enabled`. Hardware state includes PDC soft-power enablement and, on QEMU, a firmware power-off MMIO write. Panic handling calls `pdc_soft_power_button_panic(0)` to re-enable direct switch-off behavior.

## Dependencies And Integration Points
The file depends on PDC soft-power calls, PA-RISC GSC/DIAG register access, kernel threads, sysctl, panic notifier chain, reboot/sys-off framework, CAD signal delivery, and `lcd_print()` from the chassis display driver.

## Risks
Polling rather than interrupts means button response depends on scheduler progress and `HZ`. The Gecko diagnostic bit may not reset on some machines, noted by the code. `power_exit()` calls `kthread_stop(power_task)` without a visible NULL guard, but this is mostly relevant to modular unload. The sysctl path in the comment differs from the registered name: the table registers `soft-power` under `kernel`.

## Test Signals
Signals include PDC detection logs, sysctl presence and enable/disable behavior, hold-to-shutdown timing, abort message on early release, LCD shutdown message, CAD signal delivery, QEMU power-off behavior, and panic-path re-enablement. Tests should cover Gecko and MMIO-register machines separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/sba_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/sba_iommu.c

## Purpose
This file is the PA-RISC System Bus Adapter IOMMU driver for Astro, Ike, REO, Pluto, and related IOC hardware. It initializes I/O page directories, allocates IOVA ranges, implements the platform DMA mapping API, programs LBA IBASE/IMASK registers, exposes diagnostic procfs files, and reports LMMIO routing ranges to PCI host bridges.

## Important APIs, Types, And Functions
DMA operations are collected in `sba_ops`: `sba_dma_supported()`, `sba_alloc()`, `sba_free()`, `sba_map_phys()`, `sba_unmap_phys()`, `sba_map_sg()`, and `sba_unmap_sg()`. IOVA allocation helpers include `sba_search_bitmap()`, `sba_alloc_range()`, `sba_free_range()`, `sba_io_pdir_entry()`, and `sba_mark_invalid()`. Initialization helpers include `sba_alloc_pdir()`, `setup_ibase_imask()`, `sba_ioc_init_pluto()`, `sba_ioc_init()`, `sba_hw_init()`, `sba_common_init()`, and `sba_driver_callback()`. External integration APIs are `sba_get_iommu()`, `sba_directed_lmmio()`, and `sba_distributed_lmmio()`.

## Control Flow
`sba_init()` registers the PA-RISC IOA/BCPORT driver. Probe maps the SBA, identifies the chip revision, allocates `struct sba_device`, initializes IOC locks, reads PAT resources if applicable, resets risky firmware-initialized devices when needed, configures IOC control and rope hard-fail behavior, initializes one or two IOCs, allocates PDIRs/resource bitmaps, sets `hppa_dma_ops`, and creates procfs diagnostics. DMA mapping allocates aligned IOVA bitmap ranges under `res_lock`, writes little-endian valid PDIR entries with coherence index data, syncs FDC operations when required, and returns an IOVA. Unmapping clears valid bits, purges the I/O TLB through `IOC_PCOM`, frees bitmap ranges, and flushes purge writes. SG mapping shares the common two-pass coalesce/fill helpers from `iommu-helpers.h`.

## State And Persistence
Global state includes `sba_list`, `global_ioc_cnt`, `ioc_needs_fdc`, `piranha_bad_128k`, and optional AGP reservation state. Each IOC persists `ioc_hpa`, `pdir_base`, `pdir_size`, `res_map`, search hints, base/mask fields, locks, and optional statistics. Hardware state includes IOC PDIR base, IBASE/IMASK, page-size config, PCOM purges, rope controls, and LBA IBASE/IMASK routing programmed via child LBA callbacks.

## Dependencies And Integration Points
The driver depends on Linux DMA map ops, scatterlist APIs, PA-RISC PDC/PAT/model data, page-zero firmware records, LBA register programming through `lba_set_iregs()`, Linux procfs, IOMMU bitmap boundary helpers, and architecture-specific cache/IO flush instructions. LBA uses `sba_get_iommu()` and LMMIO routing helpers during PCI setup.

## Risks
This is hardware-workaround-heavy code. Wrong PDIR alignment or resource bitmap state can cause DMA data corruption or IOMMU faults. PA8700/Piranha bad-region handling depends on physical allocation behavior. `global_ioc_cnt` calculation uses a suspicious boolean condition that may not count Astro/Pluto as intended. DMA map/unmap paths assume the device can be resolved to an IOC; null devices are rejected or BUG. SG coalescing depends on virtual contiguity and correct segment-boundary math. Procfs diagnostic functions only show the first IOC.

## Test Signals
Signals include successful SBA discovery, DMA API operation for PCI devices, stress tests for map/unmap single and SG, no PDIR bitmap leaks, correct IOTLB purges, stable operation with USB reset paths, LBA resource routing correctness, `/proc/bus/runway/sba_iommu` or `/proc/bus/mckinley/sba_iommu` output, and high-load network/storage DMA tests. Hardware-specific tests should cover Astro, Ike/REO, Pluto, PA8700 bug cases, and AGP reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/sba_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/superio.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/superio.c

## Purpose
This file supports the National Semiconductor NS87560 Super I/O controller used in HP B/C/J-class workstations. It works around the chip’s non-standard PCI interrupt routing, programs its legacy PIC and internal routing registers, fixes IDE PCI class mode, registers serial and parallel legacy devices, and lets normal IDE/USB drivers bind their functions.

## Important APIs, Types, And Functions
Core functions are `superio_interrupt()`, `superio_init()` as a final PCI fixup, `superio_mask_irq()`, `superio_unmask_irq()`, `superio_fixup_irq()`, `superio_serial_init()`, `superio_parport_init()`, `superio_fixup_pci()` as an early PCI fixup, and `superio_probe()`. State is held in global `struct superio_device sio_dev` from `asm/superio.h`. The IRQ chip is `superio_interrupt_type`.

## Control Flow
PCI IRQ fixup calls `superio_fixup_irq()` during IOSAPIC processing. Function 1, the legacy I/O bridge, is saved and returns no local IRQ; function 2, USB, is saved and returns a SuperIO-local USB IRQ; function 0, IDE, returns the IDE local IRQ. A final PCI fixup on function 1 calls `superio_init()` once both function 1 and USB are known. It borrows the IOSAPIC IRQ found for USB INTD as the parent interrupt for the legacy PIC, rewrites USB to its local IRQ, reads BARs, claims PIC/ACPI I/O regions, enables the LIO PCI function, writes routing config dwords, initializes both 8259 PICs, powers the USB regulator, requests the parent IRQ, and marks the PIC enabled. The parent IRQ handler polls PIC1, dispatches the highest local IRQ with `generic_handle_irq()`, and sends a specific EOI.

## State And Persistence
`sio_dev` stores PCI device pointers, BAR bases for serial/parallel/floppy/ACPI, and whether the legacy interrupt path is enabled. The driver installs irq chips for local IRQs 0-15 and hardware PIC masks persist through mask/unmask operations. Serial and parport registrations persist through their respective subsystems.

## Dependencies And Integration Points
The file integrates PCI fixup ordering, IOSAPIC SuperIO special handling, Linux IRQ core, 8259-style port I/O, serial 8250 early setup, parport PC probing, IDE/USB device binding, and HP-specific SuperIO constants. It is tightly coupled to `iosapic.c` through `is_superio_device()` and `superio_fixup_irq()`.

## Risks
Initialization order is critical: the legacy PIC must be configured before IDE and USB drivers use interrupts. Many failures call `BUG()` because there is little recovery once PCI fixups are in progress. Only IRQs 1,3,4,5,6,7 are accepted; IRQ 2 and slave PIC interrupts are treated as errors. The handler polls only the master PIC and treats some no-active cases as spurious. BAR/resource claims are not checked for failure. The source contains an unserious debug message in an unreachable default branch, but it has no runtime effect unless an unexpected device ID reaches probe.

## Test Signals
Signals include SuperIO discovery log with parent IRQ, correct serial/parallel/floppy/ACPI BARs, USB regulator enabled, functioning ttyS0/ttyS1, parallel port probe, IDE native-mode fixup, USB IRQ remapping, and local IRQ mask/unmask behavior. Regression tests should verify final fixup runs after both LIO and USB functions are saved and that spurious IRQ7 handling does not break active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/superio.c -->
