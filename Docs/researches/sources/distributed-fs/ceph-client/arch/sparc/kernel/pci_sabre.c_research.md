# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sabre.c

## Purpose
SABRE/Hummingbird PCI controller support for UltraSPARC-IIi/IIe systems. It initializes a single supported controller, maps config/IOMMU resources, configures APB bridges, clears interrupts, and registers UE/CE/PCIERR handlers.

## Important APIs, Types, and Functions
`sabre_probe()` allocates PBM/IOMMU state, detects Hummingbird, maps controller registers, clears interrupt state, initializes PCI control/config space, parses `virtual-dma`, initializes IOMMU, and scans. `sabre_pbm_init()` uses shared PSYCHO common init with SABRE chip type. `sabre_scan_bus()` enforces single-controller support, scans bus 0, calls `apb_init()`, and registers errors. `sabre_ue_intr()` / `sabre_ce_intr()` log ECC/DMA errors. `sabre_register_error_handlers()` requests error IRQs and enables PCI error reporting.

## Control Flow
The driver matches `pci108e,a001` and `pci108e,a000`. Probe identifies Hummingbird from match data or CPU node, maps OF register windows, clears PCI/OBIO interrupt clear registers, enables controller features, initializes PSYCHO-style IOMMU, scans bus 0, fixes APB bridges, then registers error IRQs.

## State and Persistence
Global `hummingbird_p` and `sabre_root_bus` persist after probe. PBM/IOMMU and hardware registers hold runtime state. No persistent storage.

## Dependencies and Integration Points
Uses `psycho_common`, generic PCI scanning, OF/platform APIs, APB definitions, UPA register accessors, Linux IRQ APIs, and `sun4u_pci_ops`.

## Risks and Test Signals
Multiple controllers are unsupported. Unknown `virtual-dma` sizes abort. IRQ node selection differs by chip type. Test via SABRE boot logs, single bus scan, APB bridge config, and UE/CE/PCIERR logs with IOMMU diagnostics.
