<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h` defines the common receive pipeline structures: RX packet attributes, PHY info, receive buffers, receive frames, reorder control, per-station receive state, receive queues, and RX helper APIs. The source was reviewed as a complete 457-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct recv_reorder_ctrl`, `struct stainfo_rxcache`, `struct signal_stat`, `struct phy_info`, `struct rx_pkt_attrib`, `struct recv_stat`, `struct recv_priv`, `struct sta_recv_priv`, `struct recv_buf`, `struct recv_frame_hdr`, `union recv_frame`, `rtw_alloc_recvframe`, `rtw_free_recvframe`, `rtw_enqueue_recvframe`, `rtw_dequeue_recvbuf`, `rtw_reordering_ctrl_timeout_handler`, `_rtw_init_recv_priv`, `_rtw_free_recv_priv`, `rtw_recv_entry`, and `mgt_dispatcher`.

## Control Flow

Bus-specific receive code fills buffers and frames, descriptor parsing fills attributes, security/defrag/reorder logic handles the frame, management frames are dispatched to MLME, and data frames are delivered to netdev.

## State and Persistence Behavior

`recv_priv` owns free/pending frame queues, skb queues, receive buffer queues, tasklets, counters, and signal statistics. Station receive state owns reorder/defrag queues and sequence caches.

## Dependencies and Integration Points

Depends on `ieee80211.h`, `wifi.h`, `sta_info.h`, `rtw_security.h`, `rtl8723b_recv.h`, Linux skb/tasklet primitives, and netdev delivery. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RX path is exposed to untrusted frames. Length, fragment, reorder, and decryption handling must be robust to malformed or replayed packets. Queue lifetime races matter during unload.

## Test Signals

RX fuzz/malformed frames, A-MPDU reorder timeout, fragmentation/defragmentation, software decrypt pending queue, management dispatch, and unload under RX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h -->
