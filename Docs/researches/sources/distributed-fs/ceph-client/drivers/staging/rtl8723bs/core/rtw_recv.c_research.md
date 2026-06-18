# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_recv.c

## Purpose

`rtw_recv.c` is the core receive pipeline for RTL8723BS. It initializes receive-frame pools, validates 802.11 control/management/data frames, handles duplicate and fragment reassembly, decrypts WEP/TKIP/AES payloads when needed, enforces 802.1X port control, converts 802.11 payloads to Ethernet skbs, handles A-MSDU and A-MPDU reorder delivery, forwards AP-mode traffic, updates RX statistics and signal averages, and dispatches management frames into `rtw_mlme_ext.c`.

The file is stateful but not persistent on disk. It mutates `recv_priv`, per-station receive state, security state, MLME link-detect counters, reorder queues, timers, and network stack skbs.

## Important APIs, types, and functions

Initialization and queue APIs include `_rtw_init_sta_recv_priv()`, `_rtw_init_recv_priv()`, `_rtw_free_recv_priv()`, `_rtw_alloc_recvframe()`, `rtw_alloc_recvframe()`, `rtw_free_recvframe()`, `_rtw_enqueue_recvframe()`, `rtw_enqueue_recvframe()`, `rtw_free_recvframe_queue()`, `rtw_free_uc_swdec_pending_queue()`, and recv-buffer enqueue/dequeue helpers.

Security and validation helpers include `rtw_handle_tkip_mic_err()`, `recvframe_chkmic()`, `decryptor()`, `portctrl()`, `recv_decache()`, `validate_recv_ctrl_frame()`, `recvframe_defrag()`, `recvframe_chk_defrag()`, `validate_recv_mgnt_frame()`, `validate_recv_data_frame()`, `validate_80211w_mgmt()`, and `validate_recv_frame()`.

Indication and aggregation helpers include `wlanhdr_to_ethhdr()`, `rtw_alloc_msdu_pkt()`, `rtw_recv_indicate_pkt()`, `amsdu_to_msdu()`, `check_indicate_seq()`, `enqueue_reorder_recvframe()`, `rtw_recv_indicatepkt()`, `recv_indicatepkts_in_order()`, `recv_indicatepkt_reorder()`, `rtw_reordering_ctrl_timeout_handler()`, `process_recv_indicatepkts()`, and the top-level `rtw_recv_entry()`.

The main data types are `union recv_frame`, `struct recv_frame_hdr`, `struct rx_pkt_attrib`, `struct recv_priv`, `struct sta_recv_priv`, `struct stainfo_rxcache`, `struct recv_reorder_ctrl`, `struct sta_info`, `struct security_priv`, and Linux `struct sk_buff`.

## Control flow

Receive setup allocates `NR_RECVFRAME` aligned `union recv_frame` objects with `vzalloc()`, links them onto `free_recv_queue`, initializes pending and software-decrypt queues, delegates HAL receive init, and starts the signal-stat timer. Freeing drains the unicast software-decrypt pending queue, frees attached skbs, releases the frame pool, and calls HAL cleanup.

The top-level data path is `rtw_recv_entry() -> recv_func()`. `recv_func()` first drains queued unicast frames that were waiting for TKIP key availability, then calls `recv_func_prehandle()` to validate frame control, address roles, station lookup, duplicate sequence, QoS fields, privacy flags, and encryption metadata. Some station-mode encrypted unicast frames are queued on `uc_swdec_pending_queue` until `busetkipkey` is ready, with a starvation escape when free frames drop below one quarter of the pool. Valid frames continue to `recv_func_posthandle()`.

`recv_func_posthandle()` decrypts when hardware did not or software decrypt is forced, performs fragment reassembly, applies 802.1X port control so blocked stations only pass EAPOL, updates RX statistics and LPS traffic checks, and delivers through `process_recv_indicatepkts()`. For HT mode, `recv_indicatepkt_reorder()` handles A-MPDU reorder windows; for non-HT mode, frames are converted directly to Ethernet and indicated.

Management frames are handled inside validation rather than the data indication pipeline. `validate_recv_frame()` calls `validate_80211w_mgmt()` for protected-management checks, then `validate_recv_mgnt_frame()`, which defragments, updates station management statistics, and calls `mgt_dispatcher()` in `rtw_mlme_ext.c`. The function then forces a non-success return so management frames are freed by the prehandle path and not indicated as data.

Control frames are mostly filtered. `validate_recv_ctrl_frame()` accepts only frames addressed to this device with known station info, counts control packets, and handles PS-Poll in AP mode by dequeuing a sleeping station's buffered frame, updating TIM, or sending a null data frame when no buffered packet remains. Control frames are also forced out of the data path after handling.

Data validation splits by ToDS/FromDS bits. `sta2sta_data_frame()` handles IBSS, station, AP, and MP address semantics for no-DS frames. `ap2sta_data_frame()` validates AP-to-station traffic for linked or linking station mode, rejects wrong BSSID and can issue deauth for class-3 errors, counts no-data frames, and has MP/AP special cases. `sta2ap_data_frame()` handles AP-mode station-to-AP traffic, validates BSSID, deauths non-associated stations, processes power-management and WMM-PS triggers, and counts no-data frames.

Decryption uses the IV key index, current security algorithm, and software cipher helpers. TKIP MIC verification is performed after defrag for privacy frames, using group or pairwise MIC keys, reporting Michael MIC failures through cfg80211 and legacy wireless event data, and enforcing group-key check state.

Ethernet indication first removes WLAN headers, IV/ICV, and RFC1042 or bridge-tunnel SNAP headers when appropriate. A-MSDU frames are split into sub-skbs up to `MAX_SUBFRAME_COUNT` with padding handling. AP-mode indication may bridge/forward frames back into the transmit path for associated local stations or multicast clones before delivering remaining traffic to the host stack with `eth_type_trans()` and `rtw_netif_rx()`.

Reorder control uses per-TID `recv_reorder_ctrl`. `check_indicate_seq()` maintains a 12-bit sequence window, `enqueue_reorder_recvframe()` inserts frames in sequence order and rejects duplicates, `recv_indicatepkts_in_order()` drains ready frames or forced timeout frames, and `rtw_reordering_ctrl_timeout_handler()` forces delivery when a gap remains past `REORDER_WAIT_TIME`.

Signal statistics are periodically smoothed by `rtw_signal_stat_timer_hdl()`. It consumes sampled average signal strength and quality, skips updates while surveying or not linked, supports a debug override, converts percentage to dBm, and rearms the timer.

## State and persistence behavior

Receive frame ownership moves among free, pending, software-decrypt, defrag, reorder, and indication paths. Each `union recv_frame` can own an skb until `rtw_recv_indicatepkt()` nulls the frame's `pkt` pointer after handoff. Per-station state includes duplicate sequence cache, defrag queue, reorder queues and timers, sleep queues, RX counters, QoS/UAPSD flags, and HT reorder state.

Security state includes TKIP countermeasure timestamps, group key installed/check flags, software decrypt configuration, hardware decrypt observations, and BIP/802.11w key availability. MLME state is updated indirectly via link-detect RX counters and management dispatch. No on-disk persistence exists.

## Dependencies and integration points

The module depends on `drv_types.h`, `rtw_recv.h`, cfg80211, Linux skb/list/timer primitives, local security helpers (`rtw_wep_decrypt()`, `rtw_tkip_decrypt()`, `rtw_aes_decrypt()`, `rtw_seccalctkipmic()`, `rtw_BIP_verify()`), station lookup, AP sleep-queue transmit helpers, MLME state helpers, `mgt_dispatcher()` from `rtw_mlme_ext.c`, `issue_deauth()`, `issue_qos_nulldata()`, `issue_nulldata_in_interrupt()`, LPS traffic checks from `rtw_pwrctrl.c`, HAL receive init/free and debug access, and netdevice receive/forwarding APIs.

It is tightly coupled to `rtw_mlme_ext.c`: management frames validated here drive auth, assoc, scan, beacon, action, and disconnect behavior there. It is also coupled to AP transmit buffering and power save through PS-Poll and WMM-PS handling.

## Risks and edge cases

`recv_func_posthandle()` increments `precvpriv->rx_drop` at the `_recv_data_drop` label even on the normal success fallthrough path. That makes the drop counter suspect for all successfully posthandled data frames and should be verified before using it as a reliability metric.

Length handling is security-sensitive. A-MSDU parsing checks subframe bounds, but malformed SNAP, short encrypted payloads, bogus QoS headers, fragment sequences, and protected-management frames should be fuzzed because many calculations subtract header, IV, ICV, MIC, or SNAP lengths from frame length.

Defrag and reorder queues manipulate receive-frame lists in paths where some spin locks are commented out because callers already hold locks or the code assumes single-threaded receive context. Any future parallel receive changes need careful lock auditing.

TKIP MIC handling relies on key-index timing exceptions for multicast frames and reports countermeasures only when `bdecrypted` is set. Rekey timing should be tested because false MIC errors can trigger countermeasures and dropped traffic.

AP-mode forwarding clones multicast skbs and may pass the original skb into transmit before optionally continuing with a clone. Ownership is subtle; regressions here can cause skb leaks, double frees, or local-delivery loss.

802.11w management validation allocates a temporary buffer for decrypted management body and rewrites the receive frame in place. Allocation failure, decrypt failure, and MME verification paths all drop the frame; protected deauth/disassoc/action coverage is important.

## Test signals

Useful tests include receive pool allocation/free under pressure, queue count consistency, malformed management/data/control frame rejection, ToDS/FromDS address validation in station/AP/IBSS/MP modes, duplicate sequence drops per TID, fragment reassembly success and failure, WEP/TKIP/AES software and hardware decrypt paths, TKIP MIC success/failure and countermeasure timing, 802.1X blocked station EAPOL-only behavior, PS-Poll and WMM-PS AP delivery, A-MSDU split with padding and max subframes, A-MPDU reorder in-order/out-of-order/timeout delivery, AP local forwarding and multicast clone behavior, management dispatch into scan/auth/assoc handlers, and signal-stat smoothing while linked, unlinked, surveying, and debug-forced.
