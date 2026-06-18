<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h` defines the common transmit pipeline: packet attributes, transmit frame/buffer queues, per-station transmit state, management frame allocation, queue mapping, aggregation accounting, and xmit APIs. The source was reviewed as a complete 491-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct pkt_attrib`, `struct xmit_priv`, `struct xmit_frame`, `struct xmit_buf`, `struct hw_xmit`, `struct tx_servq`, `struct sta_xmit_priv`, `rtw_alloc_xmitframe`, `rtw_free_xmitframe`, `rtw_alloc_xmitbuf`, `rtw_free_xmitbuf`, `rtw_xmit_classifier`, `rtw_xmitframe_enqueue`, `rtw_xmit`, `rtw_make_wlanhdr`, `rtw_xmitframe_coalesce`, `rtw_mgntframe_coalesce`, `dump_xframe`, `rtw_count_tx_stats`, and management frame allocation helpers.

## Control Flow

Netdev TX and MLME management paths create frames, fill attributes and 802.11 headers, classify by station/TID/AC, enqueue service queues, coalesce payloads, fill chip descriptors, and submit through HAL/SDIO.

## State and Persistence Behavior

`xmit_priv` owns frame and buffer pools, pending queues, hardware queue state, semaphores/tasklets, counters, and aggregation limits. Per-station transmit state tracks TID queues and sequence numbers.

## Dependencies and Integration Points

Uses `wifi.h`, `sta_info.h`, `rtw_security.h`, `rtw_qos.h`, `rtl8723b_xmit.h`, netdev skbs, and HAL transmit callbacks. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

TX path mixes untrusted skb data, security headers, and hardware descriptors. Queue lifetime, sequence numbers, aggregation sizes, and key/IV lengths must be correct.

## Test Signals

Data and management TX, encrypted traffic, WMM queue mapping, aggregation limits, netdev stop/wake, xmit thread shutdown, and packet coalescing length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h -->
