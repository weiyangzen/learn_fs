# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/xmit_osdep.h

Purpose: declares Linux OS-dependent transmit glue for rtl8723bs, including skb-backed packet parsing, netdev transmit entry points, xmit-buffer allocation, completion, and scheduling.

Important APIs/types/functions: `struct pkt_file` tracks an open `sk_buff` with current pointer, remaining length, and original buffer range. `NR_XMITFRAME` fixes the transmit frame pool size at 256. Public declarations include `_rtw_xmit_entry()`, `rtw_xmit_entry()`, `rtw_os_xmit_schedule()`, `rtw_os_xmit_resource_alloc()`, `rtw_os_xmit_resource_free()`, `_rtw_open_pktfile()`, `_rtw_pktfile_read()`, `rtw_remainder_len()`, `rtw_endofpktfile()`, `rtw_os_pkt_complete()`, and `rtw_os_xmit_complete()`.

Control flow: netdev code calls `rtw_xmit_entry()`, which delegates to `_rtw_xmit_entry()` in `xmit_linux.c`; packet parsing helpers expose sequential reads from the skb; completions free skb ownership and wake stopped queues; scheduling wakes the SDIO transmit worker through a completion.

State and persistence: no persistent state is stored in the header. `struct pkt_file` is transient per skb. Pool sizing via `NR_XMITFRAME` influences runtime backpressure thresholds.

Dependencies and integration: depends on kernel networking types and rtl8723bs core transmit structures. It is the boundary between Linux netdev callbacks and common driver transmit logic in `core/rtw_xmit.c` and HAL SDIO transmit workers.

Risks: callers must keep `pkt_file` cursor state consistent with skb lifetime and avoid reading beyond `pkt_len`. `NR_XMITFRAME` is baked into flow-control thresholds, so changing it alters queue-stop behavior.

Test signals: packet parsing tests should verify short reads and cursor advancement; transmit stress should cover queue stop/wake, skb completion, multicast conversion, and resource allocation failure.
