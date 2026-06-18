# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/xmit_linux.c

Purpose: implements Linux skb/netdev transmit glue for rtl8723bs, including packet-file reads, xmit buffer memory allocation, skb completion, netdev queue flow control, multicast-to-unicast conversion in AP mode, and the netdev start-xmit entry.

Important APIs/types/functions: packet helpers are `rtw_remainder_len()`, `_rtw_open_pktfile()`, `_rtw_pktfile_read()`, and `rtw_endofpktfile()`. Resource helpers are `rtw_os_xmit_resource_alloc()` and `rtw_os_xmit_resource_free()`. Completion/scheduling helpers are `rtw_os_pkt_complete()`, `rtw_os_xmit_complete()`, and `rtw_os_xmit_schedule()`. TX entry points are `_rtw_xmit_entry()` and `rtw_xmit_entry()`.

Control flow: netdev calls `rtw_xmit_entry()`, which delegates to `_rtw_xmit_entry()`. The entry checks adapter up state, applies queue backpressure, optionally converts multicast/broadcast frames to per-station unicast copies in AP mode, then calls `rtw_xmit()`. Completion wakes subqueues if resource counts fall below thresholds and frees skb ownership. Scheduling completes `xmit_comp` when pending xmit buffers exist.

State and persistence: updates `xmitpriv` counters (`tx_drop`, queue accounting, free frame count), uses per-queue netdev stopped/wake state, and reads station association lists while converting multicast frames. `pkt_file` state is transient per skb.

Dependencies and integration: sits between Linux netdev ops in `os_intfs.c` and core Realtek transmit logic. Uses `sk_buff`, netdev subqueues, station management, AP MLME state, and SDIO xmit worker completions.

Risks: multicast-to-unicast copies can amplify traffic by associated-station count and depends on atomic skb allocation. Queue stop/wake thresholds depend on `NR_XMITFRAME` and `wifi_spec`. `_rtw_pktfile_read()` relies on skb cursor arithmetic and `skb_copy_bits()`. Dropped packets always return `NETDEV_TX_OK`, so upper layers will not retry.

Test signals: transmit while down, low-resource queue stop/wake, AP multicast conversion with multiple stations and allocation failure, skb completion freeing, packet-file short read, and pending-buffer scheduling.
