<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h` declares shared receive PHY-status processing structures inherited from the rtl8192c family for translating PHY status into signal metrics. The source was reviewed as a complete 37-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct phy_stat`, `struct phy_cck_rx_status`, `struct odm_phy_info`, and `rtl8192c_query_rx_phy_status`.

## Control Flow

RX descriptor handling passes raw PHY status, packet attributes, and station info into `rtl8192c_query_rx_phy_status` to update RSSI, signal quality, and per-station/link metrics.

## State and Persistence Behavior

Updates caller-owned `rx_pkt_attrib`, station state, and ODM/link statistics; no storage is declared here.

## Dependencies and Integration Points

Used by RTL8723B receive code and dynamic management code that still shares 8192C PHY-status decoding conventions. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

PHY status layouts are hardware-specific. Reusing rtl8192c helpers for rtl8723b requires field compatibility, especially CCK signal interpretation.

## Test Signals

RX PHY-status decode tests with CCK/OFDM/HT frames, RSSI sanity checks, and traffic tests across signal strengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h -->
