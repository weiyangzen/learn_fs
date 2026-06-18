# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_module.c

## Purpose
Provides libipw module initialization/exit and the allocation/free routines for `libipw_device`-backed netdevices. It also initializes scan cache storage, default 802.11/security behavior, cfg80211 wiphy stubs, crypto plugins, and optional debug procfs controls.

## Important APIs, Types, and Functions
Public functions are `alloc_libipw`, `free_libipw`, and `libipw_networks_age`. Internal helpers include `libipw_networks_allocate`, `libipw_networks_free`, `libipw_networks_initialize`, debug proc handlers, `libipw_init`, and `libipw_exit`. Module metadata describes the `libipw` 802.11 data/management/control stack.

## Control Flow
`alloc_libipw()` allocates an Ethernet netdev with space for `struct libipw_device` plus driver-private tail data. For non-monitor devices it allocates a minimal wiphy, sets station/adhoc interface modes, and attaches `wireless_dev`. It allocates 128 network records, initializes free/active lists, sets default fragmentation/RTS/scan age values, enables host WEP encrypt/decrypt defaults, initializes the device spinlock and crypto info, and returns the netdev. Module init optionally creates `/proc/net/ieee80211/debug_level`, prints version/copyright, and initializes crypto modules in NULL, CCMP, TKIP, WEP order with rollback on failure. Exit removes proc entries and unregisters crypto in the reverse broad order used by this file.

## State and Persistence Behavior
Per-device state initialized here includes scan lists, default open WEP behavior, host crypto flags, 802.1X enablement, WPA/drop/privacy flags, and crypto timers. `libipw_networks_age()` artificially ages active scan records by subtracting jiffies under `ieee->lock`. Debug state is global: `debug`, `libipw_debug_level`, and `libipw_proc`.

## Dependencies and Integration Points
Depends on netdevice allocation, cfg80211 wiphy APIs, procfs/seq_file under `CONFIG_LIBIPW_DEBUG`, net namespace proc root, and crypto modules. ipw2100/ipw2200 call `alloc_libipw()` during probe and `free_libipw()` during remove; TX/RX and wext code rely on the defaults initialized here.

## Risks
The wiphy is intentionally skeletal and lacks device/channel details until the driver later fills them. Allocation failure paths must free partially allocated network and wiphy state. Crypto init rollback ordering must stay aligned with registered modules. `free_libipw()` must run after driver callbacks/work that may use `ieee` are stopped, because it frees crypto state, scan records, wiphy, and netdev memory.

## Test Signals
Module load/unload, non-monitor and monitor netdev allocation, wiphy registration consumers, allocation failure injection, scan cache initialization and aging, debug proc read/write, crypto init rollback, key delayed-deinit cleanup on free, and ipw2100/ipw2200 probe/remove are useful validation signals.
