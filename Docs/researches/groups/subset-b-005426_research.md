# Research: subset-b-005426

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_security.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_security.c

## Purpose
`rtw_security.c` implements the software security transforms used by the rtl8723bs staging driver when hardware encryption/decryption is unavailable or when management protection must be verified in software. It covers legacy WEP, TKIP key mixing and Michael MIC, CCMP/AES packet encryption and MIC verification, 802.11w BIP/CMAC verification, WEP key restoration, and TKIP countermeasure timeout handling. The file sits directly on the transmit and receive packet paths: `rtw_xmit.c` calls the WEP/TKIP/AES encryptors after frame coalescing, while receive paths call the corresponding decryptors and BIP verifier before accepting protected frames.

## Important APIs, Types, And Functions
The public surface includes `security_type_str()`, `rtw_wep_encrypt()`, `rtw_wep_decrypt()`, `rtw_tkip_encrypt()`, `rtw_tkip_decrypt()`, `rtw_aes_encrypt()`, `rtw_aes_decrypt()`, `rtw_BIP_verify()`, `omac1_aes_128()`, `rtw_sec_restore_wep_key()`, and `rtw_handle_tkip_countermeasure()`. TKIP MIC helpers (`rtw_secmicsetkey()`, `rtw_secmicappend()`, `rtw_secgetmic()`, `rtw_seccalctkipmic()`) expose the Michael MIC primitive used by both standalone checks and the transmit coalescer. Internal helpers include TKIP `phase1()`/`phase2()` key mixing, CCMP block builders (`construct_mic_iv()`, `construct_mic_header1()`, `construct_mic_header2()`, `construct_ctr_preload()`), `aes_cipher()`/`aes_decipher()`, `gf_mulx()`, and `omac1_aes_128_vector()`.

The code depends on driver structures such as `struct adapter`, `struct security_priv`, `struct pkt_attrib`, `struct rx_pkt_attrib`, `struct sta_info`, `union recv_frame`, `struct xmit_frame`, and `struct mlme_ext_priv`. It also uses Linux crypto primitives from `<crypto/aes.h>`, ARC4 contexts carried in `security_priv`, CRC32 helpers, unaligned endian helpers, jiffies timing, and 802.11 header macros from the Realtek driver headers.

## Control Flow
WEP encryption iterates each transmit fragment, derives the RC4 key from the IV plus the selected default key, computes little-endian ICV with `crc32_le()`, encrypts payload and ICV in place, and advances to the next aligned fragment. WEP decryption derives the receive key from the received key index, decrypts payload plus ICV, and computes but does not compare the ICV in the shown code.

TKIP transmit selects group or unicast temporal key, extracts the packet number from the IV, runs two-phase TKIP key mixing using transmitter address and PN, then RC4-encrypts payload plus ICV per fragment. TKIP receive resolves the transmitter station, rejects multicast traffic until the group key is installed, chooses group or station unicast key, decrypts, and compares the decrypted ICV. Missing group-key messages are rate-limited through static counters.

CCMP transmit constructs CCM nonce/AAD, computes the 8-byte MIC over header and payload, appends it, CTR-encrypts payload blocks, and encrypts the MIC. The decrypt path reverses CTR encryption, recomputes the encrypted MIC into a static scratch buffer, and compares it against the frame. BIP verification allocates an AAD buffer, copies management body and MMIE, enforces monotonically increasing IPN and matching BIP key id, zeroes the MIC field, computes AES-CMAC, and accepts only if the first 8 bytes match the frame tail.

## State And Persistence Behavior
Persistent state is stored in `adapter->securitypriv` keys, key masks, ARC4 contexts, group-key installation flags, BIP key/id fields, and TKIP countermeasure fields. `mlmeextpriv.mgnt_80211w_IPN_rx` is updated only after successful BIP verification to prevent replay. `rtw_sec_restore_wep_key()` replays WEP CAM programming based on `key_mask`. Several decrypt paths use static counters for no-group-key diagnostics; these are process-global rather than per-adapter and are only for debug logging.

## Dependencies And Integration Points
The file integrates with `rtw_xmit.c` through software encryption and TKIP MIC addition, with station management through `rtw_get_stainfo()`, with hardware CAM setup through `rtw_set_key()`, and with 802.11w management processing through `rtw_BIP_verify()`. It assumes packet attributes already contain correct header lengths, IV/ICV lengths, key indexes, RA/TA addresses, and encryption algorithm values from earlier parsing. It also assumes frame buffers have enough tail room for ICV/MIC insertion.

## Risks
`rtw_aes_decrypt()` appears to return `_FAIL` when `rtw_get_stainfo()` succeeds and later dereferences `stainfo` on the unicast branch when it would be NULL. That inversion is a high-value review target because it can reject valid unicast CCMP frames or crash if the branch is reachable. `aes_decipher()` uses a static `message[MAX_MSG_SIZE]` scratch buffer, which is not per-call and can race under concurrent receive contexts; when the length exceeds `MAX_MSG_SIZE`, the buffer is not copied but is still used for MIC construction. WEP decryption computes an ICV but does not compare it in this function. CCMP code is handwritten rather than using kernel AEAD/CCM APIs, so nonce/AAD edge cases, QoS/A4 header variants, and length arithmetic need careful testing. Static no-group-key counters are shared across adapters. Legacy algorithms are intentionally weak but still must not corrupt memory or accept invalid frames.

## Test Signals
Useful validation includes WEP/TKIP/CCMP known-answer tests for single and fragmented frames, RX tests for bad ICV/MIC rejection, BIP replay tests with decreasing/equal IPN, BIP wrong-key-id tests, QoS and A4 CCMP vectors, and concurrent decrypt stress to expose static scratch-buffer races. Integration tests should exercise group-key-not-yet-installed receive, WEP key restore after resume, TKIP countermeasure expiry before and after 60 seconds, and transmit paths where `pattrib->bswenc` toggles between hardware and software encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_sta_mgt.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_sta_mgt.c

## Purpose
`rtw_sta_mgt.c` owns allocation, initialization, lookup, cleanup, and access-control checks for `struct sta_info` objects in the rtl8723bs driver. It provides a fixed-size station pool for client, AP, ad-hoc, and broadcast/multicast station entries. This file is central to all paths that need per-peer state: transmit queues, receive reorder control, security keys, association state, MAC IDs, AP power-save bitmaps, and ACL policy.

## Important APIs, Types, And Functions
The key public routines are `_rtw_init_sta_priv()`, `_rtw_free_sta_priv()`, `rtw_alloc_stainfo()`, `rtw_free_stainfo()`, `rtw_free_all_stainfo()`, `rtw_get_stainfo()`, `rtw_init_bcmc_stainfo()`, `rtw_get_bcmc_stainfo()`, and `rtw_access_ctrl()`. Helper functions `_rtw_init_stainfo()`, `kfree_all_stainfo()`, and `kfree_sta_priv_lock()` initialize or tear down station internals. Inline offset helpers map between pool index and station pointer.

Important structures include `struct sta_priv`, `struct sta_info`, per-station `sta_xmit_priv` and `sta_recv_priv`, `struct recv_reorder_ctrl`, `struct wlan_acl_pool`, and `struct rtw_wlan_acl_node`. The file depends on queue/list helpers, spinlocks, timers, `NUM_STA`, `wifi_mac_hash()`, `rtw_alloc_macid()`, `rtw_release_macid()`, `rtw_free_xmitframe_queue()`, and receive-frame freeing.

## Control Flow
Initialization allocates one aligned `NUM_STA` array with `vzalloc()`, initializes free queue and hash buckets, initializes every station object, and pushes all station objects onto `free_sta_queue`. It also initializes association/auth lists, sleep/wakeup queues, AP TIM/Doze bitmaps, and timeouts.

`rtw_alloc_stainfo()` locks the station hash, pops a station from the free queue, resets it, copies the peer MAC, hashes it into `sta_hash`, increments `asoc_sta_count`, initializes receive sequence caches to `0xffff`, sets up ADDBA and reorder timers, initializes 16 reorder queues, seeds RSSI stats, unlocks, and allocates a MAC ID. `rtw_get_stainfo()` hashes a unicast address or maps multicast lookups to the broadcast address, then searches the protected hash list. `rtw_init_bcmc_stainfo()` allocates the broadcast/multicast station and forces mac id 1.

`rtw_free_stainfo()` clears linked state, drains per-station sleep and AC transmit queues while updating hardware queue accounting, removes the hash entry and decrements association count, synchronously deletes timers, drains all pending reorder queues back to the adapter receive free queue, notifies ODM for non-AP stations, releases MAC ID, removes auth-list membership, clears AP power-save fields and AID mapping, and finally returns the station to the free queue. `rtw_free_all_stainfo()` moves all non-broadcast stations to a temporary list before freeing them outside the hash lock.

## State And Persistence Behavior
The station pool persists for adapter lifetime. Individual station records are recycled; allocation reinitializes most state, while free paths are responsible for unlinking all list membership and releasing queued frames. `sta_priv` maintains `asoc_sta_count`, `sta_hash[]`, `sta_aid[]`, auth/assoc list counts, `sta_dz_bitmap`, and `tim_bitmap`. Per-station timers and reorder queues are initialized on allocation and deleted on free. ACL state persists in `stapriv.acl_list` and is read by `rtw_access_ctrl()` without mutation.

## Dependencies And Integration Points
Transmit code depends on `rtw_get_stainfo()` and per-station `sta_xmitpriv` queues. Receive reorder logic depends on `recvreorder_ctrl[]` setup and timer deletion. Security code resolves unicast keys through station lookup. WLAN utility code allocates/releases MAC IDs and updates station HT/rate state. AP mode depends on AID, TIM, doze bitmap, auth list, and broadcast station state. ODM/PHY logic receives station add/remove signals through `rtw_hal_set_odm_var()`.

## Risks
`rtw_free_xmitframe_queue()` is called while `pxmitpriv->lock` is held, and that helper takes the queue lock and frees frames, so lock-order assumptions should be checked against enqueue paths. `rtw_free_stainfo()` adds the station back to `free_sta_queue` without taking that queue's own lock, relying on surrounding hash or xmit locking patterns. `kfree_all_stainfo()` is effectively a no-op traversal and exists only as legacy lock cleanup scaffolding. `asoc_sta_count` includes the broadcast/multicast station, and `rtw_free_all_stainfo()` returns early when it equals one; regressions can happen if callers assume zero means no clients. Recycled `sta_info` objects make missing list deletion or timer cancellation especially dangerous.

## Test Signals
Validation should cover pool exhaustion, allocate/free/reallocate cycles, multicast lookup mapping to the BCMC station, freeing stations with queued frames in all AC queues, reorder queue cleanup with pending frames, timer deletion during adapter removal, AP station sleep/TIM state clearing on free, and ACL modes 0/1/2 with valid and invalid nodes. Concurrency tests should stress lookup while stations are being freed and repeated connect/disconnect cycles in AP and station modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_sta_mgt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_wlan_util.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_wlan_util.c

## Purpose
`rtw_wlan_util.c` is a shared 802.11 utility layer for rtl8723bs. It translates wireless modes to rate-adaptation IDs, manages supported/basic rates, controls channel and bandwidth hardware settings, owns CAM key-cache allocation helpers, handles WMM/HT/ERP association and beacon updates, validates beacon consistency, detects AP vendor IOT quirks, updates station rate/HT capabilities, processes ADDBA receive setup, handles TSF tracking, and allocates firmware MAC IDs.

## Important APIs, Types, And Functions
Rate and mode helpers include `networktype_to_raid_ex()`, `ratetbl_val_2wifirate()`, `ratetbl2rateset()`, `get_rate_set()`, `set_mcs_rate_by_mask()`, `update_basic_rate_table()`, and `update_basic_rate_table_soft_ap()`. Hardware control helpers include `Save_DM_Func_Flag()`, `Restore_DM_Func_Flag()`, `Switch_DM_Func()`, `set_msr()`, `r8723bs_select_channel()`, and `set_channel_bwmode()`.

CAM APIs include `invalidate_cam_all()`, `_write_cam()`, `_clear_cam_entry()`, `write_cam()`, `clear_cam_entry()`, `write_cam_cache()`, `clear_cam_cache()`, `rtw_camid_search()`, `rtw_camid_alloc()`, `rtw_camid_free()`, and `flush_all_cam_entry()`. Association/beacon handlers include `WMM_param_handler()`, `WMMOnAssocRsp()`, `HT_caps_handler()`, `HT_info_handler()`, `HTOnAssocRsp()`, `ERP_IE_handler()`, `VCS_update()`, `rtw_check_bcn_info()`, and `update_beacon_info()`. Other key exports are `is_ap_in_tkip()`, `support_short_GI()`, `check_assoc_AP()`, `update_IOT_info()`, `update_capinfo()`, `update_wireless_mode()`, `update_sta_support_rate()`, `process_addba_req()`, `update_TSF()`, `adaptive_early_32k()`, `rtw_alloc_macid()`, and `rtw_release_macid()`.

## Control Flow
Rate setup flows from network mode and AP IEs into rate tables, MCS masks, station `raid`, and HAL RA mask updates. Channel changes are serialized by `setch_mutex`; the code updates `dvobj_priv` operating channel/bandwidth/offset state before calling HAL channel setters. CAM programming writes six 32-bit words per entry to hardware and maintains a software cache protected by `cam_ctl->lock`; allocation reserves default-key CAM IDs for AP/ad-hoc group keys and otherwise searches/reuses matching entries or picks free entries starting at 4.

Association response handling parses WMM parameters into EDCA registers, updates ACM masks, and stores WMM queue ordering. HT capability and operation handlers merge AP capabilities with local defaults, set AMPDU factor/spacing, update bandwidth and secondary-channel offset, and notify rate adaptation when station bandwidth changes. Beacon validation constructs a temporary BSS descriptor from received beacon/probe response IEs, compares BSSID, channel, SSID, privacy, WPA/WPA2 protocol, pairwise/group cipher, and 802.1X mode against the current network, and only returns failure after three mismatches within a one-second observation window.

## State And Persistence Behavior
The file mutates `mlmeextpriv` operating channel, bandwidth, TSF, wireless mode, beacon delay histograms, and current network information. `mlme_ext_info` persists WMM, HT, ERP, capability, slot-time, FW station table, AP vendor, and association state. `dvobj_priv` persists shared channel and CAM state across interfaces. CAM cache and bitmap persist until explicit clear/free. MAC ID allocation persists in `dvobj->macid[]`; broadcast and own-MAC cases are special-cased. Beacon mismatch counters persist in `mlmepriv` to debounce disconnect decisions.

## Dependencies And Integration Points
This file is glue between MLME parsing, station management, security key programming, transmit QoS/protection, receive reorder setup, HAL register access, and firmware/H2C behavior. It calls many HAL hooks (`rtw_hal_set_hwreg()`, `rtw_hal_set_chan()`, `rtw_hal_set_chnl_bw()`, `rtw_hal_update_ra_mask()`, `SetHwReg8723BS()`), IE parsers (`rtw_get_ie()`, WPA/RSN parsers), queue/security helpers, and station lookup. `rtw_xmit.c` consumes WMM order, VCS settings, station basic rates, SGI, LDPC/STBC, and MAC IDs established here.

## Risks
IE walking frequently advances by `pIE->length + 2` and assumes the enclosing length is trustworthy; malformed short IEs can cause out-of-bounds reads in several helpers if callers do not prevalidate buffers. `rtw_camid_alloc()` sets bitmap bits while cache content is updated elsewhere, so allocation/write ordering matters during rekey. CAM IDs are limited and failures only warn and return -1, requiring all callers to handle no-room cases. Beacon validation intentionally tolerates transient mismatches, which reduces false disconnects but can delay detection of real AP changes. `update_sta_support_rate()` bounds the first supported-rate IE but only conditionally appends extended rates, so test malformed combinations. MAC ID 1 is reserved and release excludes it; incorrect BCMC station setup can leak IDs or break queue addressing.

## Test Signals
Good tests include channel/bandwidth transitions with lower/upper 40 MHz offsets, CAM allocation for pairwise and group keys with identical key IDs, CAM exhaustion, WMM parameter changes and ACM remapping, HT capability negotiation for AMPDU/LDPC/STBC/SGI, beacon mismatch debounce timing, malformed IE fuzzing, AP vendor OUI detection, ADDBA TID reorder enablement, TSF parsing, and MAC ID allocate/release across broadcast, own MAC, and normal peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_wlan_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_xmit.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_xmit.c

## Purpose
`rtw_xmit.c` implements the rtl8723bs transmit pipeline. It initializes and frees transmit frame/buffer pools, derives packet attributes from Ethernet SKBs, builds 802.11 headers and SNAP/LLC encapsulation, fragments/coalesces payloads, applies software security transforms, classifies frames into WMM access-category queues, handles AP power-save buffering and delivery, manages pending transmit buffers, runs the xmit thread, and provides submit-context helpers for synchronous TX completion/ACK waits.

## Important APIs, Types, And Functions
Initialization and allocation APIs include `_rtw_init_sta_xmit_priv()`, `_rtw_init_xmit_priv()`, `_rtw_free_xmit_priv()`, `rtw_alloc_xmitbuf()`, `rtw_alloc_xmitbuf_ext()`, `rtw_free_xmitbuf()`, `rtw_alloc_xmitframe()`, `rtw_alloc_xmitframe_ext()`, `rtw_alloc_xmitframe_once()`, `rtw_free_xmitframe()`, and `rtw_free_xmitframe_queue()`. Packet preparation is handled by `update_attrib()`, `update_attrib_sec_info()`, `update_attrib_phy_info()`, `update_attrib_vcs_info()`, `set_qos()`, `rtw_make_wlanhdr()`, `rtw_xmitframe_coalesce()`, `rtw_mgmt_xmitframe_coalesce()`, `xmitframe_addmic()`, and `xmitframe_swencrypt()`.

Queueing and execution APIs include `rtw_xmit()`, `rtw_xmit_classifier()`, `rtw_get_sta_pending()`, `rtw_alloc_hwxmits()`, `rtw_get_ff_hwaddr()`, `xmitframe_enqueue_for_sleeping_sta()`, `stop_sta_xmit()`, `wakeup_sta_to_xmit()`, `xmit_delivery_enabled_frames()`, pending-xmitbuf enqueue/dequeue helpers, `rtw_xmit_thread()`, `rtw_sctx_wait()`, and `rtw_ack_tx_wait()`.

## Control Flow
`_rtw_init_xmit_priv()` allocates aligned arrays for normal frames, normal buffers, management/ext frames, management/ext buffers, command buffers, and hardware queue descriptors. It initializes free queues, pending queues, completions, locks, WMM sequence defaults, ACK wait context, OS DMA resources, and HAL transmit state. Freeing reverses OS resource allocation and vfree/kfree ownership.

The main data path starts at `rtw_xmit()`: allocate an `xmit_frame`, parse the SKB into `pkt_attrib`, attach the SKB, set queue selection, optionally buffer for a sleeping AP client, and otherwise hand it to `rtw_hal_xmit()`. `update_attrib()` reads Ethernet headers, determines RA/TA based on station/AP/ad-hoc mode, detects DHCP/ICMP/EAPOL special packets, requests scan-deny or LPS exit for sensitive traffic, resolves the destination station, applies security and PHY attributes, and sets QoS priority/header format.

`rtw_xmitframe_coalesce()` builds the 802.11 frame in the transmit buffer: header, IV, SNAP, fragmented payload, optional ICV placeholder, TKIP MIC, software encryption, and VCS mode. Management coalescing adds 802.11w BIP MMIE for broadcast deauth/disassoc and CCMP-protects selected robust unicast management frames. Queue classification maps user priority to VO/VI/BE/BK service queues and hardware queue accounting. AP power-save paths move frames to per-station sleep queues, update TIM bits, then later deliver frames with More Data/EOSP handling.

## State And Persistence Behavior
`xmit_priv` owns long-lived free queues, pending queues, counters, buffer pools, WMM ordering, fragmentation threshold, ACK context, and completions. Per-station `sta_xmitpriv` owns AC service queues and sequence counters. Packet attributes carry transient per-frame state such as RA/TA, encryption, IV/ICV lengths, QoS priority, AMPDU, VCS, DHCP/ICMP markers, and software-encryption flags. AP power-save state is persisted in station sleep queues, `sleepq_len`, `sleepq_ac_len`, `sta_dz_bitmap`, and `tim_bitmap`.

## Dependencies And Integration Points
This file depends on station management for `rtw_get_stainfo()` and BCMC station access, security code for WEP/TKIP/AES and Michael MIC, WLAN utility code for protection updates and beacon/TIM updates, HAL transmit hooks (`rtw_hal_xmit()`, `rtw_hal_xmitframe_enqueue()`, `rtw_hal_xmit_thread_handler()`), OS resource alloc/free and SKB completion hooks, MLME state helpers, and LPS/scan-deny command paths. It is the main integration point where Ethernet packets become hardware-ready 802.11 frames.

## Risks
The initialization path has many allocations; on mid-function failure it returns `_FAIL` without locally unwinding already allocated resources, so caller cleanup expectations matter. `rtw_free_xmitframe_queue()` takes a queue lock and calls `rtw_free_xmitframe()`, which may take another free-queue lock and complete SKBs; lock ordering should be reviewed against enqueue and station-free paths. Several paths validate `pattrib->psta` by re-looking up RA; races with station removal can drop frames or expose stale station pointers if higher layers do not serialize. Management protection code has complex length and subtype rules and uses `GFP_ATOMIC`, so low-memory behavior should be checked. Software encryption assumes tail room and fragment length arithmetic are correct. AP sleep queue/TIM logic has multiple bitmaps and counters that can desynchronize under missed free/delivery paths.

## Test Signals
Tests should exercise pool exhaustion for frames and xmit buffers, init-failure unwinding, Ethernet-to-802.11 address mapping in station/AP/ad-hoc modes, QoS priority and ACM downgrade, DHCP/EAPOL special handling, fragmentation with WEP/TKIP/AES, TKIP MIC placement, BIP-protected broadcast management frames, CCMP-protected robust unicast management frames, AP sleeping-station buffering and wake delivery, U-APSD EOSP/more-data behavior, queue-to-hardware FIFO mapping, pending-xmitbuf survey filtering, xmit-thread termination, and ACK wait timeout/success paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Hal8723BReg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Hal8723BReg.h

## Purpose
`Hal8723BReg.h` is a small register-address definition header for RTL8723B-specific MAC/protocol/EDCA/WMAC registers. It does not implement behavior by itself; it provides symbolic addresses consumed by HAL and coexistence code so register programming can refer to named constants rather than raw offsets.

## Important APIs, Types, And Functions
The header exports only preprocessor constants. Defined addresses include C2H event metadata registers (`REG_C2HEVT_CMD_SEQ_88XX`, `REG_C2HEVT_CMD_LEN_88XX`), beacon/TXDMA control (`REG_DWBCN1_CTRL_8723B`), protocol/rate/aggregation registers (`REG_FWHW_TXQ_CTRL_8723B`, `REG_ARFR0_8723B`, `REG_ARFR1_8723B`, `REG_CCK_CHECK_8723B`, `REG_AMPDU_MAX_TIME_8723B`, `REG_AMPDU_MAX_LENGTH_8723B`, `REG_DATA_SC_8723B`, `REG_MAX_AGGR_NUM_8723B`), EDCA timing (`REG_PIFS_8723B`), and WMAC receive/protocol controls (`REG_RX_PKT_LIMIT_8723B`, `REG_TRXPTCL_CTL_8723B`). There are no types, inline functions, or variables.

## Control Flow
There is no runtime control flow. The include guard `__INC_HAL8723BREG_H` prevents duplicate definitions. Build-time inclusion makes these constants available to C files that perform MMIO through Realtek HAL read/write helpers.

## State And Persistence Behavior
The header has no state. Its constants describe hardware state locations; persistence depends entirely on code that writes those registers. For example, AMPDU, ARFR, and TX queue controls persist in device registers until changed by HAL, firmware, reset, suspend/resume, or coexistence mechanisms.

## Dependencies And Integration Points
The header integrates with RTL8723B HAL implementation files and Bluetooth coexistence code that read or write protocol and aggregation registers. `HalBtc8723b1Ant.c` writes raw offsets such as `0x430`, `0x434`, and `0x456`; those correspond conceptually to rate fallback and AMPDU controls also named here. The constants are chip-specific and should not be used for other Realtek generations without confirming register compatibility.

## Risks
The main risk is drift between symbolic constants and raw offsets used elsewhere. If one path uses `REG_AMPDU_MAX_TIME_8723B` while another hard-codes `0x456`, reviews can miss that both manipulate the same register. Incorrect register addresses can cause silent hardware misconfiguration. This header also defines only a subset of registers, so nearby code may still use magic constants.

## Test Signals
Build coverage should confirm the header compiles wherever included. Hardware validation should confirm that named registers map to expected RTL8723B behavior: C2H event parsing, ARFR restore, AMPDU max time/length changes, EDCA PIFS, RX packet limit, and protocol control. Static analysis can flag raw constants matching these addresses and suggest replacing them with symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Hal8723BReg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.c

## Purpose
`HalBtc8723b1Ant.c` implements the RTL8723B one-antenna Wi-Fi/Bluetooth coexistence policy. It monitors Wi-Fi and BT state, parses BT firmware reports, chooses coexistence algorithms for SCO/HID/A2DP/PAN/inquiry/high-priority Wi-Fi states, programs PTA/coexistence tables, adjusts PS-TDMA firmware parameters, controls antenna path switching, limits Wi-Fi TX/RX aggregation/rates, and handles notification entry points from power, scan, association, media, special-packet, BT-info, halt, PnP, and periodic events.

## Important APIs, Types, And Functions
The exported `EXhalbtc8723b1ant_*` functions are the module API: `PowerOnSetting`, `InitHwConfig`, `InitCoexDm`, `IpsNotify`, `LpsNotify`, `ScanNotify`, `ConnectNotify`, `MediaStatusNotify`, `SpecialPacketNotify`, `BtInfoNotify`, `HaltNotify`, `PnpNotify`, and `Periodical`. Internal state is held in static globals `GLCoexDm8723b1Ant`/`pCoexDm` and `GLCoexSta8723b1Ant`/`pCoexSta`, whose layouts are defined in `HalBtc8723b1Ant.h`.

Important internal helpers include RSSI hysteresis (`halbtc8723b1ant_BtRssiState()`), TX limiting (`UpdateRaMask`, `AutoRateFallbackRetry`, `RetryLimit`, `AmpduMaxTime`, `LimitedTx`), RX limiting (`LimitedRx`), BT/Wi-Fi counter monitoring, BT link profile parsing, algorithm selection, coexistence table programming, H2C commands for ignore-WLAN-active and PS-TDMA, LPS/RPWM power-save control, antenna path selection, action handlers for inquiry/HS/scan/connected/not-connected states, and the main `halbtc8723b1ant_RunCoexistMechanism()`.

## Control Flow
Power-on setup configures grant BT, WLAN_ACT, S0/S1 switch selection, local antenna inverse flags, and board antenna position based on interface and efuse-derived single-antenna path. Hardware init enables TBTT interrupt/counters, configures antenna path, disables or enables PS-TDMA depending on Wi-Fi-only mode, and initializes PTA table type 0. Coex-DM init resets software mechanism state, coex table, pop event count, and queries BT info.

Runtime notifications set high-priority Wi-Fi flags and then choose action handlers. Scan and connect notifications query BT info, handle multi-port and HS/inquiry shortcuts, then run not-connected scan/auth or connected scan/special-packet policies. Media connect backs up ARFR, retry limit, and AMPDU max time registers, sets CCK priority, and sends Wi-Fi channel/bandwidth to BT firmware by H2C 0x66. Special packet notification temporarily prioritizes DHCP/EAPOL/early ARP. BT info notification parses C2H report bytes into profile flags, retry count, RSSI, inquiry/page state, and BT busy status, updates the shared `btLinkInfo`, then runs the coexistence mechanism.

`halbtc8723b1ant_RunCoexistMechanism()` exits for manual/stop/IPS states, increases scan device count when BT is busy, handles multi-link/P2P GO, applies TX/RX limits when Wi-Fi and BT are both active, handles inquiry or HS overrides, then dispatches based on Wi-Fi connected/scan/link/roam/busy and BT status. Action handlers program PS-TDMA types and coex table types. ACL busy can enter auto TDMA duration adjustment, moving among PS-TDMA types based on BT retry counts and low-priority traffic.

## State And Persistence Behavior
`pCoexDm` persists current and previous coexistence decisions so repeated notifications do not rewrite unchanged registers or H2C commands. It stores backed-up ARFR/retry/AMPDU values, current algorithm, BT status, Wi-Fi channel info, TDMA parameters, power-save values, RA masks, coex table values, ARP count, and error flags. `pCoexSta` persists BT profile flags, IPS/LPS state, special-packet counters, priority counters, RSSI state, C2H history, retry/page/inquiry state, scan AP count, CRC counters, CCK lock state, coex table type, and forced LPS state. Some local static counters in monitor and TDMA-adjust helpers persist across periodic calls.

## Dependencies And Integration Points
The code is built around `struct btc_coexist` callback operations: `fBtcGet`, `fBtcSet`, `fBtcRead*`, `fBtcWrite*`, `fBtcFillH2c`, `fBtcSetRfReg`, `fBtcSetBtReg`, and local-register writes. It integrates with firmware H2C commands 0x60, 0x61, 0x63, 0x65, 0x66, 0x69, and 0x6E, hardware registers including PTA/coex table space around 0x6c0, counters at 0x770/0x774 and Wi-Fi CRC counters around 0xf84-0xfba, antenna switch registers, rate fallback registers, retry-limit register, and AMPDU max-time register. It is called by the broader Bluetooth coexistence framework whenever Wi-Fi or BT state changes.

## Risks
The module uses single static global state, so multi-adapter or concurrent interface scenarios depend on the broader driver ensuring only one relevant coexistence context. Many hardware writes are raw magic offsets, making register drift hard to audit. Notification order is significant: media disconnect resets CCK priority and ARP count, halt sets `bStopCoexDm`, and PnP wake must reinitialize hardware before querying BT. Auto TDMA adjustment uses static counters and retry heuristics that can oscillate or carry history across state changes if not reset. Some conditional branches look unreachable or misordered, such as checks for `bA2dpExist` before `bA2dpExist && bPanExist` in scan handlers. Callback failures are not surfaced; most operations assume register/H2C writes succeed.

## Test Signals
Validation requires event-sequence tests rather than isolated unit tests: IPS enter/leave, LPS enable/disable, scan start/finish while connected and disconnected, association start/finish, media connect/disconnect on 2.4 GHz and non-2.4 GHz channels, DHCP/EAPOL/ARP special packets, BT inquiry/page, HS mode, A2DP-only, HID-only, SCO, PAN, mixed profiles, multi-link/P2P GO, halt and PnP sleep/wake. Instrumentation should verify H2C payloads, coex table values, antenna path writes, backed-up register restore, TX/RX aggregation limits, BT busy flag updates, and that unchanged state suppresses redundant writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.h

## Purpose
`HalBtc8723b1Ant.h` defines the state, profile bit masks, enums, thresholds, and external notification API for the RTL8723B one-antenna Bluetooth coexistence module implemented by `HalBtc8723b1Ant.c`. It is the contract between the generic coexistence framework and the chip/profile-specific policy code.

## Important APIs, Types, And Functions
The header defines BT info profile bits for FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection presence. It defines `BT_INFO_8723B_1ANT_A2DP_BASIC_RATE()` to interpret the BT info extension, `BTC_RSSI_COEX_THRESH_TOL_8723B_1ANT` for RSSI hysteresis, and `BT_8723B_1ANT_WIFI_NOISY_THRESH` for scan-density decisions.

Enums classify BT info sources, BT status values, Wi-Fi status values, and coexistence algorithm IDs. `struct coex_dm_8723b_1ant` stores dynamic mechanism state: firmware mechanism flags, PS-TDMA settings, LPS/RPWM values, low-penalty RA state, coex table values, register backups, selected algorithm, BT status, Wi-Fi channel info, RA mask and retry/AMPDU policy types, ARP count, and error condition. `struct coex_sta_8723b_1ant` stores observed station/profile state: BT profile flags, IPS/LPS state, special packet count, BT/Wi-Fi counters, RSSI state, C2H BT info history, inquiry/page flags, retry/RSSI/ext fields, scan AP count, CRC counters, CCK lock state, coex table type, and forced LPS flag.

The exported API prototypes are `EXhalbtc8723b1ant_PowerOnSetting()`, `EXhalbtc8723b1ant_InitHwConfig()`, `EXhalbtc8723b1ant_InitCoexDm()`, `EXhalbtc8723b1ant_IpsNotify()`, `EXhalbtc8723b1ant_LpsNotify()`, `EXhalbtc8723b1ant_ScanNotify()`, `EXhalbtc8723b1ant_ConnectNotify()`, `EXhalbtc8723b1ant_MediaStatusNotify()`, `EXhalbtc8723b1ant_SpecialPacketNotify()`, `EXhalbtc8723b1ant_BtInfoNotify()`, `EXhalbtc8723b1ant_HaltNotify()`, `EXhalbtc8723b1ant_PnpNotify()`, and `EXhalbtc8723b1ant_Periodical()`.

## Control Flow
The header has no executable flow, but the API shape reflects the runtime state machine. Power and init calls establish antenna/coex defaults. Notification calls feed Wi-Fi power-save, scan, connection, media, and special-packet transitions into the coexistence mechanism. BT info notification feeds asynchronous C2H BT profile reports. Periodical notification drives counter monitoring and adaptive TDMA decisions.

## State And Persistence Behavior
The two structs are designed for persistent module-level state. `coex_dm` carries previous/current fields so the implementation can suppress redundant hardware writes and restore backed-up Wi-Fi register values. `coex_sta` carries observed profile and counter state across notifications and periodic ticks. Because the implementation instantiates these as static globals, the state is effectively singleton within the module.

## Dependencies And Integration Points
The header assumes common Realtek BTC definitions for `struct btc_coexist`, `BIT*` macros, boolean and integer typedefs, RSSI state constants, antenna/path constants, notification enum values, and Wi-Fi/BT status sources. It is included by the chip-specific coexistence C file and by callers that dispatch coexistence notifications. Its enums must stay synchronized with action tables and profile parsing in `HalBtc8723b1Ant.c`.

## Risks
Adding or reordering enum values can silently break action dispatch if implementation tables assume numeric values. The singleton-oriented state structs are not naturally multi-adapter safe. Struct fields are tightly coupled to firmware H2C formats and raw register decisions in the C file, so unused-looking fields may still be part of a state transition. The header has no include guard visible in the inspected content, so protection may rely on surrounding include patterns; duplicate inclusion should be checked in the full build context.

## Test Signals
Build tests should verify all prototypes match the C file and all required BTC typedefs/macros are available before inclusion. Behavioral tests should confirm each BT info bit maps to the expected `coex_sta` profile flags, each enum value triggers the intended action path, previous/current state suppression works, and periodical/notification sequences mutate `coex_dm` and `coex_sta` consistently across connect, scan, BT inquiry, A2DP/HID/SCO/PAN, IPS, halt, and PnP transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.h -->
