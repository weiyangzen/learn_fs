# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_sta_mgt.c

## Purpose
`rtw_sta_mgt.c` owns allocation, initialization, lookup, cleanup, and access-control checks for `struct sta_info` objects in the rtl8723bs driver. It provides a fixed-size station pool for client, AP, ad-hoc, and broadcast/multicast station entries. This file is central to all paths that need per-peer state: transmit queues, receive reorder control, security keys, association state, MAC IDs, AP power-save bitmaps, and ACL policy.

## Important APIs, Types, And Functions
The key public routines are `_rtw_init_sta_priv()`, `_rtw_free_sta_priv()`, `rtw_alloc_stainfo()`, `rtw_free_stainfo()`, `rtw_free_all_stainfo()`, `rtw_get_stainfo()`, `rtw_init_bcmc_stainfo()`, `rtw_get_bcmc_stainfo()`, and `rtw_access_ctrl()`. Helper functions `_rtw_init_stainfo()`, `kfree_all_stainfo()`, and `kfree_sta_priv_lock()` initialize or tear down station internals. Important structures include `struct sta_priv`, `struct sta_info`, per-station `sta_xmit_priv` and `sta_recv_priv`, `struct recv_reorder_ctrl`, `struct wlan_acl_pool`, and `struct rtw_wlan_acl_node`.

## Control Flow
Initialization allocates one aligned `NUM_STA` array with `vzalloc()`, initializes free queue and hash buckets, initializes every station object, and pushes all station objects onto `free_sta_queue`. `rtw_alloc_stainfo()` locks the station hash, pops a station from the free queue, resets it, copies the peer MAC, hashes it into `sta_hash`, increments `asoc_sta_count`, initializes receive sequence caches to `0xffff`, sets up ADDBA and reorder timers, initializes 16 reorder queues, seeds RSSI stats, unlocks, and allocates a MAC ID.

`rtw_free_stainfo()` clears linked state, drains per-station sleep and AC transmit queues while updating hardware queue accounting, removes the hash entry and decrements association count, synchronously deletes timers, drains all pending reorder queues back to the adapter receive free queue, notifies ODM for non-AP stations, releases MAC ID, removes auth-list membership, clears AP power-save fields and AID mapping, and returns the station to the free queue. `rtw_access_ctrl()` scans the ACL list and implements accept-unless-denied or deny-unless-accepted modes.

## State, Dependencies, And Integration
The station pool persists for adapter lifetime. Individual station records are recycled; allocation reinitializes most state, while free paths unlink lists and queued frames. `sta_priv` maintains hash buckets, association/auth lists, `sta_aid[]`, `sta_dz_bitmap`, and `tim_bitmap`. Transmit code depends on per-station queues, receive reorder logic depends on `recvreorder_ctrl[]`, security code resolves unicast keys through station lookup, WLAN utility code allocates/releases MAC IDs, and AP mode depends on AID/TIM/doze state.

## Risks And Test Signals
`rtw_free_xmitframe_queue()` is called while `pxmitpriv->lock` is held, so lock-order assumptions should be checked. `rtw_free_stainfo()` returns stations to `free_sta_queue` without taking that queue's own lock. `kfree_all_stainfo()` is effectively a no-op legacy scaffold. `asoc_sta_count` includes the broadcast/multicast station, which affects `rtw_free_all_stainfo()`. Tests should cover pool exhaustion, allocate/free/reallocate cycles, multicast lookup mapping, freeing stations with queued frames in all AC queues, reorder queue cleanup, AP sleep/TIM clearing, ACL modes, and lookup/free concurrency.
