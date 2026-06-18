# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_acp3x.h

## Purpose
This header provides Renoir ACP3x PDM driver constants, structures, MMIO helpers, and the machine-config declaration used by the Renoir PCI and PDM DMA drivers.

## Important APIs, Types, And Functions
It defines `ACP_DEVS`, physical/register bounds, PCI device ID, power/reset masks, PDM DMA masks, capture buffer sizes, `struct pdm_dev_data`, `struct pdm_stream_instance`, `union acp_pdm_dma_count`, `rn_readl()`, `rn_writel()`, and external declaration `snd_amd_acp_find_config()`.

## Control Flow
No executable control flow exists beyond inline MMIO helpers. The helpers subtract `ACP_PHY_BASE_ADDRESS` from absolute register constants so callers can use an ioremapped BAR base plus absolute-style offsets.

## State And Persistence Behavior
The declared structures define the PDM runtime state: active capture stream, IRQ number, MMIO base, per-stream DMA address, page count, and baseline byte count. Constants fix the DMIC capture profile to four periods of 4096..8192 bytes at 48 kHz stereo.

## Dependencies And Integration Points
It includes `rn_chip_offset_byte.h` for register offsets and is included by `rn-pci-acp3x.c`, `acp3x-pdm-dma.c`, and `acp3x-rn.c`. The external config helper connects this legacy driver with shared AMD ACP stack selection.

## Risks And Edge Cases
Like the Raven header, absolute offsets require consistent use of `rn_readl()`/`rn_writel()`. The header exposes only PDM-oriented state; I2S registers in the offset header are not used by this Renoir path. The PDM DAI advertises S24/S32 in C code while hardware constants emphasize S32 capture, so constraints should be checked at runtime.

## Test Signals
Compile all Renoir files, verify BAR-relative MMIO calculations, and validate DMA byte-count high/low composition through the union under long-running capture. Static analysis can check all callers use the inline helpers.
