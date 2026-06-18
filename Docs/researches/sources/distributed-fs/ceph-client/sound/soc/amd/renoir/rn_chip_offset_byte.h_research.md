# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_chip_offset_byte.h

## Purpose
This register header enumerates ACP3.1/Renoir absolute byte offsets for DMA, AXI2AXI ATU, clock/reset, miscellaneous interrupt/error registers, PGFSM, scratch space, audio buffers, I2S/TDM, BT/TDM, and WOV/PDM blocks.

## Important APIs, Types, And Functions
It contains macro definitions only. Important groups for the active Renoir driver path are `ACP_EXTERNAL_INTR_*`, `ACP_PGFSM_*`, `ACP_SOFT_RESET`, `ACP_CONTROL`, `ACP_CLKMUX_SEL`, `ACP_SCRATCH_REG_0`, `ACPAXI2AXI_*`, and WOV/PDM registers such as `ACP_WOV_PDM_ENABLE`, `ACP_WOV_RX_RINGBUFADDR`, and linear position counters.

## Control Flow
There is no control flow. The macros are consumed through `rn_acp3x.h` helpers and PDM/PCI code.

## State And Persistence Behavior
The header has no runtime state but defines where the driver persists hardware state: power status, interrupt masks/status, DMA PTEs in scratch, ring-buffer configuration, PDM enable/DMA enable bits, FIFO flush, gain/misc control, and linear counters.

## Dependencies And Integration Points
The offsets are absolute around `0x1240000`; `rn_readl()` and `rn_writel()` convert them to BAR-relative accesses. The Renoir PDM DMA driver depends on the WOV block definitions, while the PCI parent depends on PGFSM and clock/reset definitions.

## Risks And Edge Cases
Unused I2S/BT register definitions may not be validated by the Renoir DMIC-only path. Any mismatch between absolute offsets and `ACP_PHY_BASE_ADDRESS` would misprogram MMIO. Because this is a low-level register contract, errors usually surface as probe timeouts, missing interrupts, or silent audio capture failure.

## Test Signals
Build coverage plus hardware register tracing during power-on/reset, PDM start/stop, PTE programming, interrupt mask changes, and pointer reads. Long capture tests can validate the linear counter offsets.
