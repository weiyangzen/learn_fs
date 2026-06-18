<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h` defines RTL8723B transmit and receive descriptor bit layouts, descriptor accessor macros, queue-select values, hardware rate IDs, and SDIO transmit entry points. The source was reviewed as a complete 421-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct txdesc_8723b`, `SET_TX_DESC_*_8723B`, `GET_RX_STATUS_DESC_*_8723B`, `DESC8723B_RATE*`, `RX_HAL_IS_CCK_RATE_8723B`, `rtl8723b_update_txdesc`, `rtl8723b_fill_fake_txdesc`, `rtl8723bs_hal_xmit`, `rtl8723bs_mgnt_xmit`, `rtl8723bs_hal_xmitframe_enqueue`, `rtl8723bs_xmit_buf_handler`, `BWMapping_8723B`, and `SCMapping_8723B`.

## Control Flow

Common xmit code fills `xmit_frame` attributes; the 8723B transmit path translates them into little-endian descriptors, queues SDIO buffers, and a transmit thread drains pending buffers to the device.

## State and Persistence Behavior

Descriptor memory, transmit buffers, SDIO TX sequence fields, aggregation metadata, retry/rate settings, queue selection, and ownership bits are mutable hardware-facing state.

## Dependencies and Integration Points

Depends on endian bit helpers, `rtw_xmit.h`, `rtw_recv.h`, SDIO TX ops, HAL rate/bandwidth state, and security settings. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Descriptor packing errors are high risk: own/length/offset/rate/security bits control DMA/FIFO behavior. Endianness and unaligned access must be correct on all supported architectures.

## Test Signals

TX descriptor byte-level checks, management/data/null frame transmission, aggregation and queue stress, encrypted traffic, and SDIO TX thread shutdown under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h -->
