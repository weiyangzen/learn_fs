# subset-b-005431

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wlan_bssdef.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wlan_bssdef.h

Purpose: defines the rtl8723bs driver's NDIS-style 802.11 BSS, SSID, authentication, encryption, network, beacon, and power-save data structures used by MLME, cfg80211 translation, scan cache, and connection setup.

Important APIs/types/functions: constants include `MAX_IE_SZ`, SSID/rate lengths, `MIC_CHECK_TIME`, `NUM_PRE_AUTH_KEY`, and `NUM_PMKID_CACHE`. Core types are `struct ndis_802_11_ssid`, `enum ndis_802_11_network_type`, `struct ndis_802_11_conf`, `enum ndis_802_11_network_infrastructure`, `struct ndis_802_11_wep`, `struct wlan_phy_info`, `struct wlan_bcn_info`, `struct wlan_bssid_ex`, and `struct wlan_network`. The inline `get_wlan_bssid_ex_sz()` computes the variable-size BSS record length by subtracting the fixed IE array capacity and adding the active IE length.

Control flow: this header has no active runtime flow beyond the inline size helper. It shapes scan/connect control flow by placing `struct wlan_bssid_ex network` as the last major payload inside `struct wlan_network`, letting scan queues carry list metadata plus a full BSS descriptor.

State and persistence: all state is in caller-owned structures. `struct wlan_network` persists scan results with `last_scanned`, `fixed`, `aid`, `join_res`, raw IEs, and parsed beacon metadata. Security state is represented as NDIS auth/encryption enums and WEP/PMKID constants consumed by `security_priv`.

Dependencies and integration: depends on kernel/list and Ethernet types from surrounding rtl8723bs headers. Used by MLME, cfg80211, AP, security, and command paths to translate between firmware/Realtek NDIS-like state and Linux wireless abstractions.

Risks: `struct wlan_bssid_ex` is packed and embeds a fixed `ies[MAX_IE_SZ]`; callers must validate `ie_length` before copying. `get_wlan_bssid_ex_sz()` trusts `ie_length`, so corrupted scan data can produce oversized lengths if not guarded by readers. Several enums include "Max" sentinels that are not valid runtime modes.

Test signals: scan and association tests should exercise SSID length bounds, IE length truncation/rejection, WEP key sizing, WPA/WPA2 parsed beacon metadata, PMKID cache size assumptions, and cfg80211 BSS reporting from `struct wlan_network`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wlan_bssdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/xmit_osdep.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/xmit_osdep.h

Purpose: declares Linux OS-dependent transmit glue for rtl8723bs, including skb-backed packet parsing, netdev transmit entry points, xmit-buffer allocation, completion, and scheduling.

Important APIs/types/functions: `struct pkt_file` tracks an open `sk_buff` with current pointer, remaining length, and original buffer range. `NR_XMITFRAME` fixes the transmit frame pool size at 256. Public declarations include `_rtw_xmit_entry()`, `rtw_xmit_entry()`, `rtw_os_xmit_schedule()`, `rtw_os_xmit_resource_alloc()`, `rtw_os_xmit_resource_free()`, `_rtw_open_pktfile()`, `_rtw_pktfile_read()`, `rtw_remainder_len()`, `rtw_endofpktfile()`, `rtw_os_pkt_complete()`, and `rtw_os_xmit_complete()`.

Control flow: netdev code calls `rtw_xmit_entry()`, which delegates to `_rtw_xmit_entry()` in `xmit_linux.c`; packet parsing helpers expose sequential reads from the skb; completions free skb ownership and wake stopped queues; scheduling wakes the SDIO transmit worker through a completion.

State and persistence: no persistent state is stored in the header. `struct pkt_file` is transient per skb. Pool sizing via `NR_XMITFRAME` influences runtime backpressure thresholds.

Dependencies and integration: depends on kernel networking types and rtl8723bs core transmit structures. It is the boundary between Linux netdev callbacks and common driver transmit logic in `core/rtw_xmit.c` and HAL SDIO transmit workers.

Risks: callers must keep `pkt_file` cursor state consistent with skb lifetime and avoid reading beyond `pkt_len`. `NR_XMITFRAME` is baked into flow-control thresholds, so changing it alters queue-stop behavior.

Test signals: packet parsing tests should verify short reads and cursor advancement; transmit stress should cover queue stop/wake, skb completion, multicast conversion, and resource allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/xmit_osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/ioctl_cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/ioctl_cfg80211.c

Purpose: implements rtl8723bs integration with Linux cfg80211/nl80211, translating kernel wireless operations into Realtek MLME/security/HAL commands and reporting scan, connect, AP, station, and management-frame events back to cfg80211.

Important APIs/types/functions: static capability tables include cipher suites, 2.4 GHz channels, rates, management frame subtype masks, and optional WoWLAN stub. Exported driver helpers include `rtw_ieee80211_channel_to_frequency()`, `rtw_cfg80211_inform_bss()`, `rtw_cfg80211_check_bss()`, connect/disconnect indication helpers, scan completion helpers, AP station association/disassociation notifications, action-frame RX forwarding, `rtw_cfg80211_init_wiphy()`, `rtw_wdev_alloc()`, `rtw_wdev_unregister()`, and `rtw_wdev_free()`. The central dispatch object is `static struct cfg80211_ops rtw_cfg80211_ops`.

Control flow: allocation starts in `rtw_wdev_alloc()`, which creates a `wiphy`, preinitializes cfg80211 capabilities, applies regulatory setup, registers the wiphy, allocates `wireless_dev`, and binds it to the netdev. cfg80211 callbacks then drive mode changes, scans, connections, key installation, AP beacon setup, station deletion/dumping, virtual monitor interface creation, and management TX. Scan requests are stored under `scan_req_lock`, translated into Realtek SSID/channel arrays, issued via `rtw_sitesurvey_cmd()`, and completed through `cfg80211_scan_done()`. Connection setup resets `securitypriv`, parses WPA/WPA2/WPS IEs, applies ciphers/AKM/auth, handles WEP keys, then calls `rtw_set_802_11_connect()`. AP setup validates beacon data through `rtw_check_beacon_data()` and updates hidden SSID/SSID copies.

State and persistence: persistent driver state is in `securitypriv` (cipher/auth, WEP keys, WPA IEs, WPS IE, PMKID cache, group/pairwise keys), `mlmepriv` (firmware state, scan queue, current network, WPS probe IE, roam count), `mlmeextpriv` (operating channel/bandwidth, sequence numbers, hidden SSID), `rtw_wdev_priv` (active scan request, monitor netdev, power management flag, block flag), and `stapriv` (associated stations). PMKID entries persist in a ring bounded by `NUM_PMKID_CACHE`.

Dependencies and integration: depends on cfg80211, netdevice, ieee80211 channel/rate/BSS APIs, Realtek MLME/security/AP helpers, HAL channel control, transmit management-frame helpers, and `wifi_regd.c` regulatory hooks. It is invoked from SDIO/netdev setup in `os_intfs.c` and `sdio_intf.c`.

Risks: many callbacks are partial stubs (`get_key`, tx power, stop AP, add/change station), so user space may observe success without full behavior. Key copy paths depend on cfg80211-provided lengths and fixed Realtek key buffers; malformed lengths need careful coverage. Scan state must be completed exactly once under lock to avoid cfg80211 warnings. Monitor TX accepts only radiotap length 14 and rewrites 802.11 data frames into Ethernet-like skb layout, which is fragile. Several paths return generic `-1` rather than precise errno values.

Test signals: exercise `iw` scan/connect/disconnect, WPA/WPA2/WEP association, WPS IEs, PMKSA add/delete/flush, AP start/change beacon, station deauth, monitor interface add/remove, action-frame TX/RX, suspend scan abort, and cfg80211 teardown with an in-flight scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/ioctl_cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/os_intfs.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/os_intfs.c

Purpose: provides the rtl8723bs Linux netdev/module interface: module parameters, registry default loading, net_device operations, queue selection, software initialization/free, driver thread lifecycle, netdev open/close, power-save transitions, suspend/resume, and unload.

Important APIs/types/functions: module parameters populate `registry_priv` via `loadparam()`. Netdev operations are collected in `rtw_netdev_ops`. Public setup/lifecycle functions include `rtw_init_netdev_name()`, `rtw_init_netdev()`, `rtw_unregister_netdevs()`, `rtw_start_drv_threads()`, `rtw_stop_drv_threads()`, `devobj_init()`, `devobj_deinit()`, `rtw_init_drv_sw()`, `rtw_free_drv_sw()`, `rtw_cancel_all_timer()`, `rtw_drv_register_netdev()`, `netdev_open()`, `rtw_ips_pwr_up()`, `rtw_ips_pwr_down()`, `rtw_dev_unload()`, `rtw_suspend_common()`, and `rtw_resume_common()`.

Control flow: probe code allocates a netdev with `rtw_init_netdev()`, loads module defaults into the adapter registry, initializes software blocks via `rtw_init_drv_sw()`, then registers the netdev. `netdev_open()` serializes hardware bring-up with `hw_init_mutex`, initializes HAL, starts command/xmit/SDIO transmit threads, starts the interface, initializes wiphy runtime data, starts dynamic-check timers, and wakes net queues. Close stops queues, leaves power save, disassociates, frees association and scan state, and aborts scan. Suspend cancels timers, denies power-save transitions, stops command processing, notifies btcoex, disconnects or flushes AP clients, unloads hardware, and deinitializes the interface. Resume reinitializes the interface/IRQ, resets software counters/state, opens the netdev, attaches carrier, and triggers roaming or AP restore.

State and persistence: module parameters persist as globals and are copied into per-adapter `registry_priv`. Adapter state includes `bup`, `net_closed`, `netif_up`, `bDriverStopped`, `bSurpriseRemoved`, `bCardDisableWOHSM`, thread handles/completions, netdev stats, timers, `dvobj_priv` locks, and pwrctrl suspend/IPS flags. Software block state is allocated and freed across cmd/evt/mlme/mlmeext/xmit/recv/sta/pwrctrl/HAL subsystems.

Dependencies and integration: integrates with Linux module parameters, netdev, skb priority/DSCP classification, kthreads, timers, mutexes, cfg80211 helpers, HAL init/deinit, SDIO interface callbacks installed by `sdio_intf.c`, btcoex notifications, and Realtek MLME/power APIs.

Risks: open error paths can leave partially started resources unless all callers unwind consistently. Thread start waits on command-thread completion and later stop waits on completions, so missed completions can hang removal. Suspend returns early after setting `bInSuspend` when the adapter is already down, which requires resume paths to tolerate state. `rtw_net_set_mac_address()` only updates EEPROM MAC before `bup`, not netdev visible address.

Test signals: cover module parameter loading, netdev register/unregister, open/close loops, thread startup failure, queue selection for DSCP and VLAN priority values, IPS power up/down, suspend/resume while linked, AP suspend, surprise removal, and teardown with timers/scans active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/os_intfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/osdep_service.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/osdep_service.c

Purpose: supplies small Linux service abstractions used by rtl8723bs for status conversion, skb receive submission, netdev private allocation, replaceable buffers, and a simple circular pointer buffer.

Important APIs/types/functions: `RTW_STATUS_CODE()` maps negative Linux errnos to `_FAIL` and nonnegative values to `_SUCCESS`. `_rtw_netif_rx()` sets `skb->dev` and submits to `netif_rx()`. `rtw_alloc_etherdev()` and `rtw_alloc_etherdev_with_old_priv()` allocate 4-queue Ethernet devices with a `rtw_netdev_priv_indicator`; `rtw_free_netdev()` frees the private adapter allocation and netdev. `rtw_buf_free()` and `rtw_buf_update()` manage owned byte buffers. Circular-buffer helpers are `rtw_cbuf_full()`, `rtw_cbuf_empty()`, `rtw_cbuf_push()`, `rtw_cbuf_pop()`, and `rtw_cbuf_alloc()`.

Control flow: allocation wraps `alloc_etherdev_mq()`, stores a private pointer and size in the indicator, and optionally `vzalloc()`s adapter private storage. Buffer update duplicates the new source first, then swaps the caller's pointer/length and frees the original. Circular push/pop only update read/write indexes modulo size and do no locking.

State and persistence: netdev private storage persists until `rtw_free_netdev()`. Replaceable buffers persist in caller-owned pointer/length pairs. `struct rtw_cbuf` stores size, read/write cursors, and a flexible array of pointers.

Dependencies and integration: used by netdev setup in `os_intfs.c`, receive path handoff to the kernel network stack, and any subsystem needing a tiny lock-free FIFO under externally controlled producer/consumer rules.

Risks: `rtw_cbuf_*` is explicitly lock-free and unsafe for arbitrary multi-producer/multi-consumer use. `rtw_buf_update()` drops the original even if `kmemdup()` fails for a non-empty source, replacing it with NULL/0. `rtw_free_netdev()` returns without freeing the `net_device` if `pnpi->priv` is NULL, so callers must understand ownership for old-priv netdevs.

Test signals: allocation/free tests should cover normal and old-private netdevs, failed adapter allocation, buffer update with NULL/empty/source allocation failure, circular-buffer wrap/full/empty edges, and receive path skb device assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/osdep_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_intf.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_intf.c

Purpose: binds rtl8723bs to the Linux SDIO bus, handling device IDs, probe/remove, SDIO function setup, IRQ claim/release, interface callbacks, adapter allocation, suspend/resume, and module registration.

Important APIs/types/functions: `sdio_ids` lists supported Realtek SDIO IDs. `rtl8723bs_sdio_driver` provides `.probe`, `.remove`, and PM ops. Key helpers include `sd_sync_int_hdl()`, `sdio_alloc_irq()`, `sdio_free_irq()`, `sdio_init()`, `sdio_deinit()`, `sdio_dvobj_init()`, `sdio_dvobj_deinit()`, `rtw_set_hal_ops()`, `sd_intf_start()`, `sd_intf_stop()`, `rtw_sdio_if1_init()`, `rtw_sdio_if1_deinit()`, `rtw_drv_init()`, `rtw_dev_remove()`, `rtw_sdio_suspend()`, `rtw_sdio_resume()`, and module init/exit functions.

Control flow: module init registers the SDIO driver. Probe allocates a `dvobj_priv`, stores it as SDIO drvdata, enables the SDIO function, sets block size 512, allocates and initializes the adapter/netdev/HAL/io/software/cfg80211 state, configures MAC address, registers the netdev, and claims the SDIO IRQ. The IRQ handler tags the current thread in SDIO state to avoid nested host claiming, dispatches `sd_int_hdl()`, then clears the tag. Remove marks device removal, unregisters netdev/cfg80211, detects surprise removal with a test read, disables IPS/LPS, leaves power save, halts btcoex, deinitializes adapter resources, disables SDIO, and frees `dvobj`.

State and persistence: `dvobj_priv` persists as SDIO function driver data and owns `intf_data`, IRQ allocation flag, locks, and `if1`. `sdio_data` stores the function pointer, block size, block-mode flags, and current SDIO IRQ thread marker. Adapter state persists through the registered netdev until remove/deinit.

Dependencies and integration: uses Linux SDIO core, PM ops, Realtek HAL/chip/efuse/btcoex initialization, `os_intfs.c` netdev/software lifecycle, `sdio_ops_linux.c` bus operations, and cfg80211 wdev allocation.

Risks: `rtw_sdio_if1_init()` first allocates an adapter then `rtw_init_netdev(padapter)` creates a netdev using old private storage; ownership is subtle on failure. If `rtw_wdev_alloc()` fails, the return value is not checked before subsequent use. IRQ allocation occurs after netdev registration, so failure must deinit both paths. Remove assumes `sdio_get_drvdata(func)` is valid.

Test signals: bind/unbind supported SDIO IDs, block-size setup failure, IRQ claim/release failure, probe failure at HAL/io/software/wdev steps, remove during active traffic, suspend/resume, and surprise removal signaled by `-ENOMEDIUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_intf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_ops_linux.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_ops_linux.c

Purpose: implements rtl8723bs Linux SDIO CMD52/CMD53 read/write primitives and host-claim handling for register and memory access.

Important APIs/types/functions: `rtw_sdio_claim_host_needed()` suppresses nested `sdio_claim_host()` while running in the driver's SDIO IRQ thread. `rtw_sdio_set_irq_thd()` records that IRQ thread. Byte/register operations include `_sd_cmd52_read()`, `sd_cmd52_read()`, `_sd_cmd52_write()`, `sd_cmd52_write()`, `sd_read8()`, `sd_read32()`, `sd_write8()`, and `sd_write32()`. Bulk operations are `_sd_read()`, `sd_read()`, `_sd_write()`, and `sd_write()`.

Control flow: public wrappers resolve adapter/dvobj/sdio_func, skip work on surprise removal, conditionally claim the SDIO host, call the underscore variant, then release the host. CMD52 helpers loop byte-by-byte. CMD53 helpers use byte access for 1-2 byte transfers and `sdio_memcpy_fromio()`/`sdio_memcpy_toio()` for larger transfers. 32-bit read/write retries up to `SD_IO_TRY_CNT`, reset continual I/O error state on success, and mark `bSurpriseRemoved` on shutdown/device errors or excessive continual errors.

State and persistence: uses `sdio_data->sys_sdio_irq_thd` to track IRQ context and adapter `bSurpriseRemoved` to short-circuit future I/O. Continual I/O error counters live in `dvobj_priv` and are updated through helper calls.

Dependencies and integration: called by Realtek IO/HAL layers after `rtw_init_io_priv()` installs SDIO ops. Depends on Linux SDIO core and driver error accounting helpers.

Risks: many helpers return zero or no-op when `bSurpriseRemoved` is set, which can look like success to callers. 8-bit and bulk paths do not retry like 32-bit paths. Caller-provided buffers must be DMA-safe for CMD53 as documented. Incorrect IRQ-thread tagging could deadlock through recursive host claims.

Test signals: test byte and bulk reads/writes, 1/2-byte CMD53 fallbacks, host-claim suppression inside IRQ handler, retry behavior for transient `sdio_readl/writel` failures, continual I/O error threshold, and surprise removal errors `-ESHUTDOWN`/`-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_ops_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/wifi_regd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/wifi_regd.c

Purpose: supplies rtl8723bs cfg80211 regulatory-domain setup and channel flag application for 2.4 GHz operation.

Important APIs/types/functions: `rtw_regdom_rd` is a custom world-like regulatory domain with active channels 1-11 and passive channels 12-13. `_rtw_reg_apply_flags()` disables all wiphy channels then re-enables channels present in the driver's channel plan, setting `IEEE80211_CHAN_NO_IR` for passive scan. Public entry points are `rtw_regd_init()` and `rtw_reg_notifier()`.

Control flow: `rtw_wdev_alloc()` calls `rtw_regd_init()`, which stores the notifier, sets custom regulatory flags, applies `rtw_regdom_rd`, then hard-applies channel flags from `mlmeextpriv.channel_set`. Later regulatory notifications call `_rtw_reg_notifier_apply()`, which reapplies the same driver channel-plan flags.

State and persistence: regulatory state persists in `wiphy` flags, custom regdomain, channel flags, and the adapter `mlmeextpriv.channel_set/max_chan_nums` generated elsewhere from the registry/efuse channel plan.

Dependencies and integration: depends on cfg80211 regulatory APIs, `rtw_ieee80211_channel_to_frequency()` from cfg80211 glue, and adapter lookup via `wiphy_to_adapter()`.

Risks: the request contents are ignored, so country-specific updates do not alter the base domain beyond the driver's hard channel plan. Channel 14 is not in the custom regdomain even though frequency conversion supports it. All bands are disabled first, which is safe only because this chip exposes 2.4 GHz here.

Test signals: verify channels enabled for a representative channel plan, passive/no-IR behavior for channels 12-13, notifier reapplication after regulatory events, and absence of enabled channels not present in `channel_set`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/wifi_regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/xmit_linux.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/xmit_linux.c

Purpose: implements Linux skb/netdev transmit glue for rtl8723bs, including packet-file reads, xmit buffer memory allocation, skb completion, netdev queue flow control, multicast-to-unicast conversion in AP mode, and the netdev start-xmit entry.

Important APIs/types/functions: packet helpers are `rtw_remainder_len()`, `_rtw_open_pktfile()`, `_rtw_pktfile_read()`, and `rtw_endofpktfile()`. Resource helpers are `rtw_os_xmit_resource_alloc()` and `rtw_os_xmit_resource_free()`. Completion/scheduling helpers are `rtw_os_pkt_complete()`, `rtw_os_xmit_complete()`, and `rtw_os_xmit_schedule()`. TX entry points are `_rtw_xmit_entry()` and `rtw_xmit_entry()`.

Control flow: netdev calls `rtw_xmit_entry()`, which delegates to `_rtw_xmit_entry()`. The entry checks adapter up state, applies queue backpressure, optionally converts multicast/broadcast frames to per-station unicast copies in AP mode, then calls `rtw_xmit()`. Completion wakes subqueues if resource counts fall below thresholds and frees skb ownership. Scheduling completes `xmit_comp` when pending xmit buffers exist.

State and persistence: updates `xmitpriv` counters (`tx_drop`, queue accounting, free frame count), uses per-queue netdev stopped/wake state, and reads station association lists while converting multicast frames. `pkt_file` state is transient per skb.

Dependencies and integration: sits between Linux netdev ops in `os_intfs.c` and core Realtek transmit logic. Uses `sk_buff`, netdev subqueues, station management, AP MLME state, and SDIO xmit worker completions.

Risks: multicast-to-unicast copies can amplify traffic by associated-station count and depends on atomic skb allocation. Queue stop/wake thresholds depend on `NR_XMITFRAME` and `wifi_spec`. `_rtw_pktfile_read()` relies on skb cursor arithmetic and `skb_copy_bits()`. Dropped packets always return `NETDEV_TX_OK`, so upper layers will not retry.

Test signals: transmit while down, low-resource queue stop/wake, AP multicast conversion with multiple stations and allocation failure, skb completion freeing, packet-file short read, and pending-buffer scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/xmit_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Kconfig

Purpose: declares the kernel configuration option for the Silicon Motion SM750 framebuffer staging driver.

Important APIs/types/functions: `config FB_SM750` is a tristate option named "Silicon Motion SM750 framebuffer support". It depends on `FB`, `PCI`, and `HAS_IOPORT`, and selects framebuffer helper operations `FB_MODE_HELPERS`, `FB_CFB_FILLRECT`, `FB_CFB_COPYAREA`, and `FB_CFB_IMAGEBLIT`.

Control flow: no runtime flow; Kconfig controls whether `CONFIG_FB_SM750` is absent, built-in, or module. The help text identifies module name `sm750fb`.

State and persistence: selected config persists in the kernel build configuration and determines object inclusion by the Makefile.

Dependencies and integration: integrates with the staging drivers Kconfig tree, PCI framebuffer infrastructure, I/O port availability, and cfb helper implementations.

Risks: selecting cfb helpers pulls in software framebuffer operations and assumes the legacy fbdev subsystem. `HAS_IOPORT` is required because SM750LE mode setup uses x86-style VGA I/O paths in some code paths.

Test signals: build coverage for `CONFIG_FB_SM750=m` and `=y`, dependency resolution without `PCI` or `HAS_IOPORT`, and module name/load tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Makefile

Purpose: defines how the SM750 framebuffer driver is built when `CONFIG_FB_SM750` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_FB_SM750) += sm750fb.o` creates the composite driver object. `sm750fb-objs` lists component objects: core fbdev/PCI files, hardware setup, acceleration, cursor handling, chip/power/mode/display helpers, and software I2C.

Control flow: no runtime flow; kbuild links the listed objects into `sm750fb.o` in order when the config is enabled.

State and persistence: build state is kbuild-generated. The object list is the persistent source of which implementation files are included in the module/built-in driver.

Dependencies and integration: integrates with Linux kbuild and the Kconfig option. It ensures DDK helper files are linked with `sm750.c`, `sm750_hw.c`, `sm750_accel.c`, and `sm750_cursor.c`.

Risks: omitting a helper object causes unresolved symbols; stale object lists can include dead staging code or miss newly split helpers.

Test signals: compile the driver as module and built-in, verify no unresolved symbols, and inspect `modinfo sm750fb` after module build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750.h -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750.h

Purpose: aggregate public DDK header for SM750 framebuffer helper modules.

Important APIs/types/functions: includes `ddk750_reg.h`, `ddk750_mode.h`, `ddk750_chip.h`, `ddk750_display.h`, `ddk750_power.h`, and `ddk750_swi2c.h` under include guard `DDK750_H__`.

Control flow: no runtime flow; including this header exposes register definitions, chip/PLL helpers, display routing, power gating, mode timing, and software I2C declarations.

State and persistence: no state, but it centralizes compile-time dependencies and expands the visible API surface for consumers.

Dependencies and integration: used by SM750 driver source that wants the complete helper interface rather than including narrower headers.

Risks: broad includes increase coupling and rebuild scope. Changes to low-level register headers propagate widely through this aggregate.

Test signals: compile coverage for every translation unit including `ddk750.h`, include-order checks, and duplicate-definition guard validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.c -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.c

Purpose: implements SM750/SM718 chip identification, clock/PLL programming, framebuffer memory size detection, and top-level hardware initialization.

Important APIs/types/functions: exported helpers are `sm750_get_chip_type()`, `sm750_set_chip_type()`, `ddk750_get_vm_size()`, `ddk750_init_hw()`, `sm750_calc_pll_value()`, and `sm750_format_pll_reg()`. Internal helpers set main chip clock, memory clock, and master clock. A static `enum logical_chip_type chip` stores detected chip type.

Control flow: PCI probe code sets chip type from device/revision. Hardware init forces power mode 0, enables display/localmem gates, sets VGA graphics/PLL mode, programs requested chip/memory/master clocks, optionally resets local memory, and optionally disables 2D/video/alpha/DMA engines. PLL calculation searches valid N/M/divider combinations for the closest frequency and formats register fields for PLL control registers.

State and persistence: chip type persists in the file-static `chip`. Clock, gate, reset, and engine state persists in MMIO registers. `ddk750_get_vm_size()` reads local memory size from hardware straps/registers, with SM750LE hardcoded to 64 MiB.

Dependencies and integration: uses `peek32()`/`poke32()` from `ddk750_chip.h`, register masks from `ddk750_reg.h`, power-gate helpers from `ddk750_power.c`, and architecture I/O for SM750LE VGA mode setup under x86.

Risks: global chip type assumes a single active device. Clock programming writes hardware registers directly and must respect chip-specific fixed clocks on SM750LE. PLL search uses integer math and frequency limits; incorrect inputs can produce zero or approximate clocks. Memory reset after clock change can hang if sequenced incorrectly.

Test signals: identify SM718/SM750/SM750LE/unknown devices, verify PLL outputs for common pixel/core clocks, check memory-size detection, run init with reset and engine-off flags, and test SM750LE fixed-clock paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.h -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.h

Purpose: declares SM750 chip helper APIs, chip and clock enums, PLL/init structures, and MMIO read/write helpers.

Important APIs/types/functions: `DEFAULT_INPUT_CLOCK`, `SM750LE_REVISION_ID`, external `void __iomem *mmio750`, inline `peek32()`/`poke32()`, `enum logical_chip_type`, `enum clock_type`, `struct pll_value`, `struct initchip_param`, and prototypes for chip type, PLL, framebuffer memory, and hardware init functions.

Control flow: inline MMIO helpers add register offsets to `mmio750` and call `readl()`/`writel()`. Other declarations are implemented by `ddk750_chip.c`.

State and persistence: `mmio750` is an externally owned mapped MMIO base that must remain valid for every helper using `peek32()`/`poke32()`. Init parameters describe desired hardware state but are caller-owned.

Dependencies and integration: includes Linux I/O, ioport, and uaccess headers plus SM750 register definitions. Used by chip, power, display, mode, acceleration, and core framebuffer setup code.

Risks: no null or bounds checks on `mmio750`; calling helpers before mapping MMIO can fault. `struct initchip_param` uses small integer MHz fields and flag semantics that callers must fill correctly.

Test signals: compile users of all prototypes, validate MMIO base setup before calls, and test init parameters across zero/no-change and nonzero clock values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.c -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.c

Purpose: programs SM750 logical display output routing, timing/plane enable state, panel power sequencing, DAC, and DPMS through register operations.

Important APIs/types/functions: public `ddk750_set_logical_disp_out(enum disp_output output)` applies bit-encoded output selections. Internal helpers are `set_display_control()`, `primary_wait_vertical_sync()`, and `sw_panel_power_sequence()`.

Control flow: the public function checks usage bits in the `disp_output` value and conditionally updates panel path, CRT path, primary timing/plane, secondary timing/plane, panel sequence, DAC power, and DPMS. Enabling display timing turns on timing before plane and repeatedly writes until non-reserved bits match. Panel power sequencing toggles FPEN, DATA, and VBIASEN with vertical-sync waits.

State and persistence: display routing and power state persist in `PANEL_DISPLAY_CTRL`, `CRT_DISPLAY_CTRL`, `SYSTEM_CTRL`, and `MISC_CTRL` registers. The function has no software state.

Dependencies and integration: uses register definitions, `peek32()`/`poke32()`, `set_DAC()` macro from `ddk750_power.h`, and `ddk750_set_dpms()`. Called by higher-level framebuffer output setup.

Risks: vertical-sync waits poll hardware and can stall if guard checks miss a bad state, though the helper skips waiting when PLL/timing is off. The panel sequence uses OR-only updates for enable bits, so off sequencing may not clear fields as expected. Encoded enum values combine data and usage masks, making invalid combinations possible.

Test signals: route LCD/CRT outputs through primary/secondary paths, toggle timing/plane on and off, verify DAC/DPMS bits, test with PLL off, and read back register values after repeated writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.h -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.h

Purpose: defines bit-encoded SM750 logical display output selections and declares the display-routing API.

Important APIs/types/functions: macros define offsets, masks, usage bits, and encoded values for panel-to-primary/secondary, CRT-to-primary/secondary, primary/secondary timing-plane enable, panel sequence, dual TFT, DAC, and DPMS. `enum disp_output` provides common output recipes such as `do_LCD1_PRI`, `do_LCD1_SEC`, `do_LCD2_PRI`, `do_LCD2_SEC`, `do_CRT_PRI`, and `do_CRT_SEC`. Public API is `ddk750_set_logical_disp_out()`.

Control flow: no runtime flow in the header; `ddk750_display.c` interprets usage bits to decide which hardware fields to update.

State and persistence: encoded constants represent desired hardware register changes but store no state.

Dependencies and integration: relies on `BIT()` and register semantics from the SM750 headers. Used by framebuffer output configuration to select active heads.

Risks: the low 16 bits carry values while shifted masks in high bits indicate usage; callers can OR incompatible recipes and request inconsistent routing. Some output comments mention DVI/DSUB behavior tied to DAC control, so board wiring assumptions matter.

Test signals: compile each enum recipe, verify expected register writes for every recipe, and test invalid or combined recipes defensively at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.c -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.c

Purpose: programs SM750 primary or secondary display timing registers and pixel PLLs for a requested video mode.

Important APIs/types/functions: public `ddk750_set_mode_timing(struct mode_parameter *parm, enum clock_type clock)` computes PLL values and calls internal `program_mode_registers()`. SM750LE-specific `display_control_adjust_SM750LE()` sets auto-centering and chooses one of fixed display clocks.

Control flow: mode setup initializes a `pll_value` with the default input clock and requested clock type, calculates the closest PLL for `parm->pixel_clock`, applies SM750LE VGA graphics mode if needed, then programs either secondary CRT registers or primary panel registers. For secondary timing it writes `CRT_PLL_CTRL`, horizontal/vertical totals and syncs, then display control bits. For primary timing it writes `PANEL_PLL_CTRL`, panel timing registers, and repeatedly writes display control until non-reserved bits match.

State and persistence: programmed mode persists entirely in hardware PLL, timing, auto-centering, and display-control registers. No software mode cache is kept in this file.

Dependencies and integration: depends on `ddk750_reg.h`, `ddk750_mode.h`, `ddk750_chip.h`, `sm750_calc_pll_value()`, `sm750_format_pll_reg()`, chip type detection, and architecture I/O for SM750LE.

Risks: mode parameters are trusted; zero or invalid totals/sync positions can underflow register fields because the code subtracts one. SM750LE only maps selected resolutions to fixed clocks and falls back to VGA clock. Busy readback loops can run up to 1000 iterations. There is no validation against framebuffer memory pitch or output routing.

Test signals: set primary and secondary modes for common resolutions, SM750LE fixed-clock modes, invalid timing rejection at higher layers, PLL register formatting, sync polarity bits, and readback convergence of panel display control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.h -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.h

Purpose: declares SM750 mode timing data structures and the timing programming entry point.

Important APIs/types/functions: `enum spolarity` represents positive/negative polarity. `struct mode_parameter` carries horizontal timing, vertical timing, pixel clock, horizontal/vertical refresh frequencies, and panel clock phase polarity. Public API is `ddk750_set_mode_timing()`.

Control flow: no runtime flow in the header; callers populate `mode_parameter` and pass a `clock_type` from `ddk750_chip.h`.

State and persistence: `mode_parameter` is caller-owned transient state describing a target hardware mode.

Dependencies and integration: includes `ddk750_chip.h` for `enum clock_type`. Used by mode-setting code in the framebuffer driver and implemented by `ddk750_mode.c`.

Risks: the structure has no explicit validation or units annotations beyond field names; callers must ensure totals, display ends, sync starts, widths, and clocks are hardware-valid.

Test signals: compile mode callers, validate conversions from fbdev mode structures into `mode_parameter`, and test both polarity values and primary/secondary clock types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.c -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.c

Purpose: manages SM750 display power management, chip power modes, and clock gates for major engines.

Important APIs/types/functions: public functions are `ddk750_set_dpms()`, `sm750_set_power_mode()`, `sm750_set_current_gate()`, `sm750_enable_2d_engine()`, `sm750_enable_dma()`, `sm750_enable_gpio()`, and `sm750_enable_i2c()`. Internal `get_power_mode()` selects current gate register context.

Control flow: DPMS writes either `CRT_DISPLAY_CTRL` fields on SM750LE or `SYSTEM_CTRL` fields on other chips. Power mode ignores changes on SM750LE, otherwise updates `POWER_MODE_CTRL` mode bits and oscillator/validation clock bits. Current gate writes to `MODE1_GATE` when in mode 1, else `MODE0_GATE`. Engine enable helpers read `CURRENT_GATE`, set or clear their gate bits, and write back via `sm750_set_current_gate()`.

State and persistence: power mode, DPMS, and gate state persist in hardware registers. No software cache is kept.

Dependencies and integration: uses chip detection from `ddk750_chip.c`, MMIO helpers, and register masks. Called by hardware init, display output code, acceleration setup, GPIO/I2C users, and suspend-like paths.

Risks: read-modify-write gate operations can race if multiple contexts manipulate gates without external locking. SM750LE silently ignores power-mode changes. Gate writes depend on current power mode, so callers must set power mode before gate configuration.

Test signals: verify DPMS on SM750 and SM750LE, power mode 0/1/sleep transitions, gate toggles for 2D/DMA/GPIO/I2C, and init sequences that enable display/localmem before mode setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.h -->
# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.h

Purpose: declares SM750 power-management types, DAC macro, and gate/power function prototypes.

Important APIs/types/functions: `enum dpms` defines CRT DPMS on/standby/suspend/off values. `set_DAC(off)` read-modify-writes `MISC_CTRL_DAC_POWER_OFF`. Prototypes expose DPMS, power mode, current gate, and engine gate helpers.

Control flow: the only inline behavior is `set_DAC(off)`, which directly updates the DAC power-off bit in `MISC_CTRL`; other behavior is implemented in `ddk750_power.c`.

State and persistence: no software state. Macro/function calls persist changes in hardware registers.

Dependencies and integration: relies on `poke32()`, `peek32()`, `MISC_CTRL`, and `MISC_CTRL_DAC_POWER_OFF` definitions from included chip/register headers through users. Used by display routing and hardware init.

Risks: `set_DAC` is a multi-statement macro without `do { } while (0)`, so it is unsafe in conditional contexts without braces. It performs direct read-modify-write with no locking.

Test signals: compile macro call sites, verify DAC bit behavior, and cover all DPMS enum values through `ddk750_set_dpms()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.h -->
