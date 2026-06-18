# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x.h

## Purpose
This header centralizes Yellow Carp ACP6x constants, data structures, and MMIO helpers used by the PCI parent, PDM DMA component, and machine support. It imports the ACP6x register-offset header and defines hardware limits, mode IDs, power/reset masks, PDM parameters, buffer sizes, and runtime PM delay.

## Important APIs, Types, And Functions
Important types are `struct pdm_dev_data`, `struct pdm_stream_instance`, and `union acp_pdm_dma_count`. Inline helpers `acp6x_readl()` and `acp6x_writel()` convert physical ACP register offsets into offsets from the mapped base by subtracting `ACP6x_PHY_BASE_ADDRESS`. It declares `snd_amd_acp_find_config(struct pci_dev *pci)`.

## Control Flow
The header has no control flow besides inline MMIO reads/writes. Its constants drive polling loops, PDM trigger decisions, and DMA buffer constraints in other files.

## State And Persistence
State definitions describe both software state (`capture_stream`, per-stream `bytescount`, DMA page count) and hardware state (power-gating status, interrupt bits, WOV/PDM enable bits). Actual persistence is owned by callers and hardware registers.

## Dependencies And Integration Points
It depends on `acp6x_chip_offset_byte.h`, Linux MMIO accessors, DMA address types, and PCI type declarations. It is shared between `pci-acp6x.c` and `acp6x-pdm-dma.c`, so register-base arithmetic changes affect both.

## Risks And Test Signals
The most important risk is the nonstandard `base_addr - ACP6x_PHY_BASE_ADDRESS` addressing contract: callers must pass `mapped_base + physical_offset`, not a normal offset. Test signals are correct register reads during PCI probe, successful power/reset sequencing, and DMA component operation without bogus MMIO accesses.
