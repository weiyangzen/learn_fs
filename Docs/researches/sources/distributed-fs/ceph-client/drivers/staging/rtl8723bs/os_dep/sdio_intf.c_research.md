# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_intf.c

Purpose: binds rtl8723bs to the Linux SDIO bus, handling device IDs, probe/remove, SDIO function setup, IRQ claim/release, interface callbacks, adapter allocation, suspend/resume, and module registration.

Important APIs/types/functions: `sdio_ids` lists supported Realtek SDIO IDs. `rtl8723bs_sdio_driver` provides `.probe`, `.remove`, and PM ops. Key helpers include `sd_sync_int_hdl()`, `sdio_alloc_irq()`, `sdio_free_irq()`, `sdio_init()`, `sdio_deinit()`, `sdio_dvobj_init()`, `sdio_dvobj_deinit()`, `rtw_set_hal_ops()`, `sd_intf_start()`, `sd_intf_stop()`, `rtw_sdio_if1_init()`, `rtw_sdio_if1_deinit()`, `rtw_drv_init()`, `rtw_dev_remove()`, `rtw_sdio_suspend()`, `rtw_sdio_resume()`, and module init/exit functions.

Control flow: module init registers the SDIO driver. Probe allocates a `dvobj_priv`, stores it as SDIO drvdata, enables the SDIO function, sets block size 512, allocates and initializes the adapter/netdev/HAL/io/software/cfg80211 state, configures MAC address, registers the netdev, and claims the SDIO IRQ. The IRQ handler tags the current thread in SDIO state to avoid nested host claiming, dispatches `sd_int_hdl()`, then clears the tag. Remove marks device removal, unregisters netdev/cfg80211, detects surprise removal with a test read, disables IPS/LPS, leaves power save, halts btcoex, deinitializes adapter resources, disables SDIO, and frees `dvobj`.

State and persistence: `dvobj_priv` persists as SDIO function driver data and owns `intf_data`, IRQ allocation flag, locks, and `if1`. `sdio_data` stores the function pointer, block size, block-mode flags, and current SDIO IRQ thread marker. Adapter state persists through the registered netdev until remove/deinit.

Dependencies and integration: uses Linux SDIO core, PM ops, Realtek HAL/chip/efuse/btcoex initialization, `os_intfs.c` netdev/software lifecycle, `sdio_ops_linux.c` bus operations, and cfg80211 wdev allocation.

Risks: `rtw_sdio_if1_init()` first allocates an adapter then `rtw_init_netdev(padapter)` creates a netdev using old private storage; ownership is subtle on failure. If `rtw_wdev_alloc()` fails, the return value is not checked before subsequent use. IRQ allocation occurs after netdev registration, so failure must deinit both paths. Remove assumes `sdio_get_drvdata(func)` is valid.

Test signals: bind/unbind supported SDIO IDs, block-size setup failure, IRQ claim/release failure, probe failure at HAL/io/software/wdev steps, remove during active traffic, suspend/resume, and surprise removal signaled by `-ENOMEDIUM`.
