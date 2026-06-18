<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 0. It names registers for DMA configuration, error/completion messaging, linear transfer programming, status, rate limiting, tensor DMA source/destination geometry, and memory initialization status.

## Important APIs, Types, And Functions
- Base channel registers run from `mmDMA_CH_0_CFG0` through `mmDMA_CH_0_CFG2`.
- Messaging and completion registers include `ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*`.
- Linear DMA programming uses `LDMA_SRC_ADDR_*`, `LDMA_DST_ADDR_*`, `LDMA_TSIZE`, and `COMIT_TRANSFER`.
- Status registers include `STS0` through `STS4` and active source/destination address/size status.
- Rate limiting registers include separate read and write enable, token, saturation, and timeout registers.
- Tensor DMA registers start at `TDMA_CTL`, include source/destination base address pairs, five ROI slots per side, and end at `MEM_INIT_BUSY`.

## Control Flow
Driver code writes offsets from this header to program channel 0 or computes channel-relative offsets using channel spacing. A typical flow configures completion/error message addresses, writes source/destination/size, writes `COMIT_TRANSFER`, and polls status until not busy.

## State And Persistence Behavior
Registers hold volatile DMA channel state while transfers are pending or active. Status and active address registers reflect the last/current transfer until overwritten or reset.

## Dependencies And Integration Points
Pairs with `dma_ch_0_masks.h`. Integrates with Goya initialization, DMA engines, command submission, completion signaling, and protection/security logic that marks DMA channel MMIO ranges.

## Risks And Edge Cases
The name `COMIT_TRANSFER` is misspelled in the generated interface and must remain stable for consumers. Channel offsets are used arithmetically in some code, so channel 0 layout must stay congruent with channels 1 and 2. Writing stale completion addresses can corrupt synchronization state.

## Test Signals
Signals include successful channel 0 DMA transfers, completion writes to expected addresses, error interrupt/message behavior, status polling without timeout, and channel-offset calculations matching channel 1/2 layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h -->
