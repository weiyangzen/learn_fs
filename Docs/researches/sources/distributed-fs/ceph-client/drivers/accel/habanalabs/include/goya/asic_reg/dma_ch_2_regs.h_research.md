<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 2. It mirrors the DMA channel prototype at the channel 2 address range and names registers for DMA configuration, messaging, linear and tensor transfers, status, rate limiting, and memory initialization.

## Important APIs, Types, And Functions
- Channel 2 starts at `mmDMA_CH_2_CFG0` (`0x411000`) and keeps the same register order as channels 0 and 1.
- `mmDMA_CH_2_ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*` configure error and completion messages.
- `mmDMA_CH_2_LDMA_*` and `COMIT_TRANSFER` program linear transfers.
- `mmDMA_CH_2_STS*`, active address/size status, and rate-limit registers expose channel state and throttling controls.
- `mmDMA_CH_2_TDMA_*` registers define tensor DMA geometry with five ROI slots on source and destination sides.

## Control Flow
Goya code can address channel 2 directly or calculate it from channel spacing. Runtime flow follows the common DMA pattern: configure, commit, poll, and handle completion/error messages. Security code can also include the channel 2 range in protected block programming.

## State And Persistence Behavior
Registers are volatile state for DMA channel 2. They are independent from other channels except where shared driver code computes offsets or schedules work across channels.

## Dependencies And Integration Points
Integrates with Goya DMA operations, command parser DMA handling, completion synchronization, memory initialization, and protection/security setup. Field meanings are shared with `dma_ch_0_masks.h`.

## Risks And Edge Cases
Wrong channel 2 offsets can silently operate on the wrong DMA engine or invalid MMIO. Multi-channel scheduling must not reuse completion registers unsafely. Tensor DMA fields are large and repetitive, making off-by-one ROI programming a practical risk.

## Test Signals
Signals include channel 2 DMA transfer success, independent busy/status behavior, correct completion/error message generation, multi-channel transfer coverage, and register offset checks against channels 0 and 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h -->
