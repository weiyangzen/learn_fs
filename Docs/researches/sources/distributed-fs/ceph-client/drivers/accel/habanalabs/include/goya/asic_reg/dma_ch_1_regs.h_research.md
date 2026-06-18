<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 1. It mirrors the DMA channel 0 prototype at the channel 1 address range and provides named offsets for linear DMA, completion/error messaging, status, rate limiting, tensor DMA, and memory initialization state.

## Important APIs, Types, And Functions
- Channel 1 starts at `mmDMA_CH_1_CFG0` (`0x409000`) and follows the same register order as channel 0.
- Messaging/completion, LDMA, status, rate-limit, TDMA source, TDMA destination, and `MEM_INIT_BUSY` registers are all named with the `mmDMA_CH_1_*` prefix.
- The layout allows code to compute per-channel offsets from channel 0 or address channel 1 directly by symbolic name.

## Control Flow
The driver configures channel 1 by writing the same sequence used for channel 0: setup message/completion registers, source/destination/size, optional rate or TDMA fields, commit transfer, and poll status. Goya code also derives channel spacing from channel 0/1 register differences.

## State And Persistence Behavior
The registers are volatile DMA engine state. They persist only until reprogrammed or reset and represent channel 1 independent of channels 0 and 2.

## Dependencies And Integration Points
Integrates with shared DMA code, Goya command execution, completion signaling, and protection block setup. It relies on the same bit semantics documented by `dma_ch_0_masks.h` because the channel prototype is replicated.

## Risks And Edge Cases
If channel 1 spacing diverges from channel 0, arithmetic offset code can program the wrong registers. Concurrent use of multiple DMA channels requires distinct completion addresses and careful status polling. Generated symbolic names must remain aligned with the hardware channel order.

## Test Signals
Signals include channel 1 copy/memset tests, multi-channel DMA tests, completion writes from channel 1, status polling that clears independently from channel 0/2, and verification that computed channel offsets hit the same named registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h -->
