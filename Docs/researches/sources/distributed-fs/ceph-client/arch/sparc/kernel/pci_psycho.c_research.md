# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_psycho.c

## Purpose
PSYCHO/U2P PCI controller support for sun4u systems. It handles controller/PBM hardware initialization, shared IOMMU and per-PBM streaming buffers, bus scanning, sibling PBM discovery, Starfire hookup, and UE/CE/PCI error interrupts.

## Important APIs, Types, and Functions
`psycho_probe()` allocates PBM state, finds or allocates the shared IOMMU, maps register bases, initializes hardware/IOMMU, and scans. `psycho_pbm_init()` calls common PBM setup, initializes the streaming buffer, then scans. `psycho_controller_hwinit()` enables arbiters and applies a synchronization erratum workaround. `psycho_pbm_strbuf_init()` programs per-PBM streaming-buffer registers. `psycho_ue_intr()` / `psycho_ce_intr()` latch, clear, and log ECC/UPA errors. `psycho_register_error_handlers()` registers UE, CE, and PCIERR IRQs and enables error reporting.

## Control Flow
The driver matches `pci108e,8000`. Probe determines PBM A/B from `reg`, finds a sibling by UPA portid, shares the IOMMU when present, initializes the IOMMU only once, optionally hooks Starfire, initializes per-PBM streaming buffer state, scans PCI, then registers error handlers.

## State and Persistence
State includes PBM list/sibling pointers, shared IOMMU table, streaming buffer register addresses and flush flags, and hardware error-control registers. IRQ handlers clear latched error bits. No persistence.

## Dependencies and Integration Points
Uses `psycho_common.h`, `iommu_common.h`, shared PCI helpers, UPA accessors, OF/platform APIs, Linux IRQ APIs, Starfire support, and generic PCI scanning.

## Risks and Test Signals
Two PBMs share one IOMMU, making failure paths delicate. Shared IRQ request results are partly ignored. Streaming-buffer diagnostics are hardware-sensitive. Test via PSYCHO PBM logs, sibling linking, PCI enumeration, IRQ registration, and UE/CE/PCI diagnostic logging.
