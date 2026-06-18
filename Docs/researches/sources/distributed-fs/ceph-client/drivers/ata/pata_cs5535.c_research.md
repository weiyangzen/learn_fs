# sources/distributed-fs/ceph-client/drivers/ata/pata_cs5535.c

Purpose: NS/AMD CS5535 PATA driver for Geode systems where IDE timing controls live in model-specific registers rather than ordinary PCI config space.

Important APIs and control flow: `cs5535_cable_detect` reads PCI cable register `0x48`. `cs5535_set_piomode` uses `wrmsr` to program per-device PIO command/data timing MSRs, computes shared command timing from the slower device on the link, updates the peer timing if needed, and sets the DMA timing format bit. `cs5535_set_dmamode` reads the DMA timing MSR, preserves the PIO format bit, and writes fixed UDMA0-4 or MWDMA0-2 values. `cs5535_init_one` exposes only the primary port and registers through `ata_pci_bmdma_init_one`.

State, dependencies, and risks: state persists in Geode ATAC MSRs and PCI cable detect register. Dependencies include x86 MSR access through `<asm/msr.h>`, PCI IDs from NS/AMD, and libata BMDMA. Risks include MSR-only timing programming tying behavior to Geode-class CPUs, command timing shared between devices, no secondary port support, and UDMA limited to mode 4. Test signals are successful MSR read/write during mode setup, cable register reporting expected 40/80-wire state, peer command timing updates when mixed PIO devices exist, and primary-only host enumeration.
