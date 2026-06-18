<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h` declares OS-facing adapter lifecycle, netdev registration, driver thread startup/shutdown, timer cancellation, queue selection, IPS power transitions, and suspend/resume entry points. The source was reviewed as a complete 42-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `devobj_init`, `devobj_deinit`, `rtw_init_drv_sw`, `rtw_free_drv_sw`, `rtw_reset_drv_sw`, `rtw_dev_unload`, `rtw_start_drv_threads`, `rtw_stop_drv_threads`, `rtw_cancel_all_timer`, `rtw_init_netdev`, `rtw_unregister_netdevs`, `rtw_recv_select_queue`, `rtw_ips_pwr_up`, `rtw_ips_pwr_down`, `rtw_suspend_common`, `rtw_resume_common`, and `netdev_open`.

## Control Flow

Bus probe allocates the device object and adapter software, registers netdev/cfg80211 state, starts command/event/xmit threads, and unload/suspend paths reverse those steps while coordinating power transitions.

## State and Persistence Behavior

Manages the lifetime of `dvobj_priv`, `struct adapter`, netdev private state, driver timers, and worker threads, but the header itself is declarative.

## Dependencies and Integration Points

Tied to Linux netdev, SDIO bus probe/remove code, HAL init/deinit, command and transmit workers, and power-control helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Lifecycle ordering is critical; netdev unregistration, timer cancellation, thread stop, and power-down must not race with RX/TX callbacks.

## Test Signals

Module load/unload loops, netdev open/stop, suspend/resume, IPS transitions, and race testing with traffic during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h -->
