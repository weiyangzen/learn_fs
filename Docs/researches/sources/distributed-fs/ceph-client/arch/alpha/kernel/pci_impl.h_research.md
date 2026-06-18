# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_impl.h

## Purpose
`pci_impl.h` is the private Alpha PCI implementation contract used by host bridge, platform vector, and IOMMU code in this directory. It centralizes default PCI I/O and memory allocation base constants, explains Alpha-specific interrupt swizzling assumptions, declares the shared PCI hose and IOMMU arena state, and exposes helper APIs used by board support files and common PCI initialization.

## Important APIs, Types, And Constants
- PCI resource constants include `EISA_DEFAULT_IO_BASE`, `DEFAULT_IO_BASE`, `XL_DEFAULT_MEM_BASE`, `APECS_AND_LCA_DEFAULT_MEM_BASE`, `MCPCIA_DEFAULT_MEM_BASE`, `T2_DEFAULT_MEM_BASE`, `DEFAULT_MEM_BASE`, `CIA_DEFAULT_MEM_BASE`, `IRONGATE_DEFAULT_MEM_BASE`, and `DEFAULT_AGP_APER_SIZE`. These encode host-bridge and board-specific limitations such as sparse-space reachability, HAE avoidance, and BIOS/VGA side effects around I/O addresses.
- `COMMON_TABLE_LOOKUP` is the shared table-driven IRQ mapping macro for many single-bus Alpha platform files. It maps PCI slot/pin to an IRQ table entry when `slot` and `pin` are inside caller-provided bounds.
- `struct pci_iommu_arena` is the core IOMMU allocation unit: it holds a spinlock, owning `pci_controller`, PTE table, DMA base, window size, next allocation pointer, and allocation alignment. Its PTE sentinel values `IOMMU_INVALID_PTE` and `IOMMU_RESERVED_PTE` are consumed by `pci_iommu.c`.
- SRM restore feature macros define whether `pci_restore_srm_config()` is a real external function or a no-op. This matters during reboot/halt paths that must put firmware-visible PCI state back.
- Externs expose `hose_head`, `hose_tail`, `pci_isa_hose`, `alpha_agpgart_size`, `common_init_pci()`, `alloc_pci_controller()`, `alloc_resource()`, `iommu_arena_new[_node]()`, `size_for_memory()`, and AGP/IOMMU reservation helpers.

## Control Flow And Integration
This header has no runtime control flow beyond macros, but it drives downstream behavior. Platform files include it to choose default resource bases and to use `COMMON_TABLE_LOOKUP` in their `pci_map_irq` implementations. `pci_iommu.c` implements the declared arena and AGP helpers. `process.c` calls `pci_restore_srm_config()` during SRM shutdown when restoration is enabled. Host bridge code and platform vectors depend on the global hose list and resource allocators declared here.

## State And Persistence
State is externalized: the header defines the shape of `pci_iommu_arena` and declares global hose pointers and AGP aperture size. Those are process-lifetime kernel structures, initialized during boot and used for DMA mappings until shutdown. There is no disk persistence; firmware-visible state can be restored through the conditional SRM restore hook.

## Dependencies And Integration Points
The header assumes Linux PCI types, Alpha `pci_controller` and machine-vector infrastructure, and Alpha-specific SRM/CIA configuration options. It is tightly coupled to `pci_iommu.c`, `bios32.c`/PCI setup code, host bridge sources, and board support files such as `sys_alcor.c` and `sys_cabriolet.c`.

## Risks
- Constants are board- and bridge-specific; changing them can break device resource assignment, sparse-space access, or firmware compatibility.
- `COMMON_TABLE_LOOKUP` depends on caller-local variables named `slot`, `pin`, `min_idsel`, `max_idsel`, `irqs_per_slot`, and `irq_tab`, so misuse can fail at compile time or silently map wrong interrupts.
- `struct pci_iommu_arena` is shared with low-level DMA code; field semantics and sentinel values must remain aligned with IOMMU allocator logic.

## Test Signals
- Alpha PCI boot logs showing expected I/O and memory resource assignment.
- PCI devices receive stable IRQs on each supported board.
- DMA tests through `alpha_pci_ops`, including AGP aperture reservation when enabled.
- SRM reboot/halt smoke tests on configurations with `ALPHA_RESTORE_SRM_SETUP`.
