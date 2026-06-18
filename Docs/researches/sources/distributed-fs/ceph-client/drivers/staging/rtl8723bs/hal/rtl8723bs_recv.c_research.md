# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_recv.c

Purpose: this file implements the RTL8723BS SDIO receive-buffer lifecycle, RX descriptor parsing, PHY status processing, C2H packet dispatch, and tasklet-driven delivery to the common receive stack.

Important APIs and functions: `rtl8723bs_init_recv_priv` allocates and initializes `NR_RECVBUFF` receive buffers and sets up `recv_tasklet`; `rtl8723bs_free_recv_priv` kills the tasklet and frees buffers. `rtl8723bs_recv_tasklet` is the main parser. Helpers include `update_recvframe_attrib`, `update_recvframe_phyinfo`, `rtl8723bs_c2h_packet_handler`, `try_alloc_recvframe`, `rx_crc_err`, and `pkt_exceeds_tail`.

Control flow: SDIO interrupt handling reads RX FIFO data into a `recv_buf` and schedules this tasklet. The tasklet dequeues buffers, walks each packed descriptor/payload sequence, allocates a `recv_frame`, parses `rxreport_8723b`, checks CRC policy and tail bounds, allocates an aligned skb, copies packet bytes after descriptor/driver-info/shift offset, optionally removes FCS, and dispatches normal frames to `rtw_recv_entry`. C2H packets are handled inline for CCX TX reports or forwarded to C2H workqueue commands.

State and persistence: receive buffer queues and skb ownership live in `recv_priv`. PHY-derived RSSI is written to `sta_info.rssi` and aggregate signal stats. `hal_com_data.ReceiveConfig` controls CRC/FCS/BA-SSN behavior. No on-disk persistence exists.

Dependencies and integration: depends on SDIO interrupt/RX FIFO code in `sdio_ops.c`, descriptor bit layouts, ODM `odm_phy_status_query`, station/MLME helpers, common receive queues, and C2H handlers from `rtl8723b_hal_init.c`.

Risks and test signals: length validation is critical because descriptor fields determine copy offsets. On `sd_recv_rxfifo` allocation/read failures, buffers can be temporarily unavailable; repeated allocation failures in the DPC stop RX draining. Tasklet code must avoid leaking skbs/frames on CRC, ICV, C2H, and allocation error paths. Tests should stress aggregated RX buffers, malformed descriptors, CRC policy, QoS alignment, fragmented first packets, C2H packets, AP-mode RSSI updates, and free/init symmetry.
