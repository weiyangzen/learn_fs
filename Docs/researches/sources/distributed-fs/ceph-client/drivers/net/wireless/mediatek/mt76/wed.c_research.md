# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/wed.c

## Purpose
Implements shared integration with MediaTek WED hardware offload. It provisions RX buffers and tokens, configures WED-backed DMA rings, toggles offload token ranges, bridges TC setup, and coordinates WED reset completion with mt76 DMA reset flow.

## Important APIs, Types, And Functions
Exports `mt76_wed_release_rx_buf()`, `mt76_wed_init_rx_buf()`, `mt76_wed_offload_enable()`, `mt76_wed_dma_setup()`, `mt76_wed_offload_disable()`, `mt76_wed_reset_complete()`, `mt76_wed_net_setup_tc()`, and `mt76_wed_dma_reset()`. Compile-time `CONFIG_NET_MEDIATEK_SOC_WED` gates the full RX-buffer and ring-setup implementation.

## Control Flow
RX buffer initialization allocates RXWI cache entries and page-pool buffers, writes WED buffer descriptors, consumes RX tokens, and encodes token/high DMA address bits. DMA setup inspects queue WED flags and type, then calls the appropriate WED ring setup for TX, TXFREE, RX, RRO data, MSDU page, or indication rings, temporarily clearing mt76 WED flags where software ring reset/fill must happen first. Offload enable shrinks the mt76 token range to reserve WED tokens and waits for outstanding WED tokens.

## State And Persistence
State includes RX token IDRs, RXWI cache objects, page-pool buffers, queue flags, `q->wed_regs`, `dev->token_size`, `dev->wed_token_count`, and reset completions `wed_reset`/`wed_reset_complete`. WED ring base registers persist in queue metadata after setup.

## Dependencies And Integration Points
Depends on mtk_wed_device APIs, mt76 DMA queue reset/fill, page-pool DMA addresses, mt76 token management in `tx.c`, TC offload integration, and queue flag conventions from mt76 DMA code.

## Risks
RX buffer initialization must unwind all tokens and pages on partial failure. Changing `token_size` while TX is active must be protected by `token_lock`. Ring setup mutates queue flags temporarily; failing to restore them would break later DMA logic. Reset completion has a fixed timeout and logs if WED firmware/hardware does not answer.

## Test Signals
WED active and inactive probe paths, TX/RX offload traffic, RX buffer release without leaks, token range restoration on disable, setup of all supported ring types, TC offload handoff, WED reset completion, and successful build with and without WED config.
