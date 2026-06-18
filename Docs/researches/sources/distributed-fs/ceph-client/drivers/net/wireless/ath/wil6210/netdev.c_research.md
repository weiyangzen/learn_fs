# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/netdev.c

## Purpose
`netdev.c` bridges wil6210 private state to Linux net_device, wireless_dev, VIF allocation, NAPI polling, open/stop behavior, netdev registration, and teardown. It keeps hardware up only while at least one interface is active.

## Important APIs, Types, And Functions
`wil_has_other_active_ifaces()` and `wil_has_active_ifaces()` implement VIF activity checks. `wil_open()` and `wil_stop()` are netdev ops. NAPI poll functions handle legacy and EDMA RX/TX completion. Allocation/registration helpers include `wil_vif_alloc()`, `wil_if_alloc()`, `wil_if_free()`, `wil_vif_add()`, `wil_if_add()`, `wil_vif_remove()`, and `wil_if_remove()`.

## Control Flow
Opening the first active interface resumes runtime PM and calls `wil_up()`. Stopping the last active interface calls `wil_down()` and releases runtime PM. `wil_if_alloc()` creates cfg80211 state, initializes private state, allocates the main station-mode VIF, and stores `radio_wdev`. `wil_if_add()` registers the wiphy, allocates a dummy NAPI netdev, binds legacy or EDMA pollers, and registers the main netdev under RTNL/wiphy locks. Removal unregisters VIFs, synchronizes NAPI before clearing VIF references, deletes timers/work, removes NAPI, and unregisters wiphy.

## State And Persistence
The file owns VIF lifetime and netdev pointers in `wil->vifs[]`, `wil->main_ndev`, `wil->napi_ndev`, and `wil->radio_wdev`. Each VIF initializes timers, work items, probe-client queues, P2P work, broadcast ring marker, and queue-stopped state. NAPI state persists until `wil_if_remove()`.

## Dependencies And Integration Points
It depends on cfg80211 initialization/deinitialization, TX/RX backend functions, ethtool setup, PM wrappers, reset/up/down in `main.c`, WMI port allocation/deletion for non-main VIFs, P2P workers, key/probe-client workers, and net queue update helpers.

## Risks
VIF removal is race-prone: cfg80211 unregister can trigger callbacks before `wil->vifs[mid]` is cleared, and NAPI may still dereference VIFs until synchronized. Open/stop assumes active-interface accounting is accurate. Dummy netdev NAPI lifetime must stay aligned with wiphy/netdev registration failure paths.

## Test Signals
Create/remove multiple VIFs while traffic is active, first-open/last-stop PM transitions, EDMA and legacy NAPI completion, connect/scan/P2P timers during VIF teardown, failure injection in wiphy/netdev registration, and RTNL/wiphy lockdep coverage.
