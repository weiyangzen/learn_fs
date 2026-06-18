<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h` declares RTL8723B receive descriptor parsing, PHY status conversion, and RX buffer/frame handlers. The source was reviewed as a complete 95-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rxreport_8723b`, `rtl8723b_query_rx_desc_status`, `rtl8723b_process_phy_info`, `rtl8723b_query_rx_phy_status`, `rtl8723bs_init_recv_priv`, `rtl8723bs_free_recv_priv`, `rtl8723bs_recv_hdl`, and `rtl8723bs_recv_tasklet`.

## Control Flow

SDIO RX code reads packets into buffers, parses 8723B RX descriptors into `rx_pkt_attrib`, optionally decodes PHY info, and dispatches completed frames to the common receive path/tasklet.

## State and Persistence Behavior

Updates receive buffer queues, frame attributes, per-station RSSI/link quality, and adapter receive counters.

## Dependencies and Integration Points

Depends on `rtw_recv.h`, `rtl8723b_xmit.h` descriptor bit macros, `rtl8192c_recv.h` PHY status helpers, and SDIO receive operations. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Descriptor bit offsets and buffer alignment are critical. Bad packet length, shift, or driver-info parsing can cause memory corruption or dropped frames.

## Test Signals

RX descriptor decode coverage, fragmented/aggregated frame receive, PHY status RSSI sanity, tasklet under load, and malformed descriptor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h -->
