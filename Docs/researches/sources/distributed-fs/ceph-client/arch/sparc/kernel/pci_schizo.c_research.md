# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_schizo.c

## Purpose
SCHIZO, SCHIZO+, and TOMATILLO PCI controller support. Covers config addressing, per-PBM IOMMU and streaming buffer initialization, controller tuning, sibling detection, bus scanning, and extensive UE/CE/PCI/Safari-JBUS diagnostics.

## Important APIs, Types, and Functions
`schizo_probe()` / `__schizo_init()` match compatible nodes and allocate PBM/IOMMU state. `schizo_pbm_init()` fills identity/register fields, parses resources/properties, initializes hardware, IOMMU, STC, and bus. `schizo_pbm_iommu_init()` configures IOMMU registers, TSB, context flush, and allocation pools. `schizo_pbm_strbuf_init()` enables streaming buffers except on TOMATILLO. `schizo_pbm_hw_init()` programs arbiter, parking, timeout, retry, and TOMATILLO prefetch controls. Error handlers log and clear UE, CE, PCI, and Safari/JBUS state. Diagnostic helpers dump IOMMU/STC tags and errors.

## Control Flow
The match table prefers TOMATILLO over older compatible strings. Probe finds siblings by portid rules, allocates a per-PBM IOMMU, then calls PBM init. PBM init links the PBM early, sets `sun4u_pci_ops`, discovers OF ranges/properties, initializes hardware/IOMMU/STC, scans PCI, and registers error handlers according to chip type and INO bitmap.

## State and Persistence
Long-lived state includes PBM root/sibling links, per-PBM IOMMU tables, optional streaming-buffer flush flags, chip version/revision, sync registers, and resources. Static STC diagnostic buffers are protected by `stc_buf_lock`. No persistence.

## Dependencies and Integration Points
Uses Linux OF/platform/PCI/IRQ/NUMA APIs, UPA access, shared PCI helpers, IOMMU table helpers, and generic PCI error scanners.

## Risks and Test Signals
STC diagnostics can discard dirty streaming-buffer data if used at the wrong time. TOMATILLO sibling routing is heuristic. Safari/JBUS masks can reset systems if wrong. Test via SCHIZO/TOMATILLO boot logs, resource ranges, PCI enumeration, IRQ registration, and UE/CE/PCI/JBUS diagnostic paths.
