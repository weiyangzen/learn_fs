<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h

## Purpose
Auto-generated bitfield mask and shift definitions for Goya DMA channel 0. It describes configuration, completion/error messaging, linear DMA, status, rate limiting, tensor DMA, and memory-initialization status fields.

## Important APIs, Types, And Functions
- `DMA_CH_0_CFG0/CFG1` fields control read/write outstanding limits and read buffer size.
- `ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*` fields describe 32-bit low/high address and write-data values used for error and completion messages.
- `LDMA_*` fields describe source, destination, and transfer size registers.
- `COMIT_TRANSFER` fields control PCI ordering, completion enables, no-snoop, address increment disable, memset, tensor mode, and command control bits.
- `STS*` and address/size status fields expose busy, context fullness, transaction counts, and active transfer values.
- Rate-limit fields cover read/write enable, reset token, saturation, and timeout.
- `TDMA_*` fields define tensor DMA source/destination base, five ROI dimensions, valid elements, start offsets, and strides.
- `MEM_INIT_BUSY` exposes SBC data/metadata busy state.

## Control Flow
The header has no functions. Goya DMA setup code writes channel registers using these masks, commits transfers, and polls status bits such as `DMA_BUSY`. Completion and error-message fields are programmed so DMA can notify synchronization objects or interrupt paths.

## State And Persistence Behavior
Fields describe volatile DMA engine registers. Transfer descriptors and status exist only while DMA is configured or running. Completion addresses/data can affect host/device synchronization state outside the block.

## Dependencies And Integration Points
Pairs with `dma_ch_0_regs.h` for offsets and is reused conceptually for channels 1 and 2 because the DMA channel prototype is replicated. Integrates with Goya DMA initialization, command parser DMA validation, internal memory copy/fill, completion signaling, and security/protection setup.

## Risks And Edge Cases
Wrong commit bits can start an unintended transfer, omit completion, or write completion data to a wrong address. Address increment disable and memset bits change transfer semantics. Tensor DMA ROI fields are numerous and easy to mismatch. Polling only `DMA_BUSY` without checking context/status fields can miss error states.

## Test Signals
Signals include linear DMA copy and memset tests, completion SOB/message writes, error-message delivery, rate-limit programming behavior, tensor DMA ROI tests, and polling showing `DMA_BUSY` clears with expected status counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h -->
