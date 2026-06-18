<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h` maps Realtek OS abstraction to Linux kernel primitives including network queues, timers, sleep/delay, endian helpers, netdev private storage, and etherdev allocation. The source was reviewed as a complete 121-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `_set_timer`, `_cancel_timer_ex`, `rtw_netif_wake_queue`, `rtw_netif_start_queue`, `rtw_netif_stop_queue`, `rtw_signal_process`, `struct rtw_netdev_priv_indicator`, `rtw_netdev_priv`, `rtw_alloc_etherdev_with_old_priv`, and `rtw_alloc_etherdev`.

## Control Flow

Driver lifecycle and data paths call these inline wrappers whenever they need Linux netdev queue state, timers, or netdev-private adapter lookup.

## State and Persistence Behavior

Stores the adapter pointer in `netdev_priv` through `struct rtw_netdev_priv_indicator`; timer state is managed by Linux `timer_list` instances.

## Dependencies and Integration Points

Depends on Linux netdevice, timer, delay, list, endian, and signal APIs. It is included indirectly through `osdep_service.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Kernel API compatibility matters because timer and netdev APIs change across releases. Netdev private layout must be consistent for every allocation path.

## Test Signals

Build against the intended kernel tree, netdev queue transition tests, timer cancellation during unload, and netdev private pointer validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h -->
