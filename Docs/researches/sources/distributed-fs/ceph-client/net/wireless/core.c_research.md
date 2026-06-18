# sources/distributed-fs/ceph-client/net/wireless/core.c

## Purpose
This file is the central cfg80211 lifecycle and registration implementation. It creates and registers wiphy devices, validates driver capabilities, manages global registered-device lists, handles rfkill and network namespace changes, registers wireless netdevices, runs cfg80211 work queues, and initializes/exits the cfg80211 subsystem.

## Important APIs, types, and functions
Global state includes RCU-protected `cfg80211_rdev_list`, `cfg80211_rdev_list_generation`, `cfg80211_wq`, and the top debugfs directory. Public APIs include `wiphy_new_nm()`, `wiphy_register()`, `wiphy_unregister()`, `wiphy_free()`, `cfg80211_register_netdevice()`, `cfg80211_unregister_wdev()`, `cfg80211_shutdown_all_interfaces()`, `cfg80211_leave()`, `cfg80211_stop_link()`, and work helpers such as `wiphy_work_queue()`, delayed work, and hrtimer work variants.

Validation helpers enforce driver operation pairs, interface combinations, NAN/P2P/mesh/AP constraints, supported bands, rates, 6 GHz HE/EHT rules, vendor command policies, WoWLAN settings, regulatory flag combinations, AKM limits, and multi-radio allocation.

## Control flow
`wiphy_new_nm()` allocates `struct cfg80211_registered_device`, assigns a `phy%d` or requested name, initializes locks/lists/work items/rfkill/default parameters, and returns the embedded `struct wiphy`. `wiphy_register()` performs extensive sanity checks, initializes channel original flags, sets bitrate flags, allocates radio config, adds the device, links it into `cfg80211_rdev_list`, creates debugfs, notifies nl80211, registers regulatory state, marks registered, and registers rfkill. On failure it unwinds through the caller-visible lifecycle.

`wiphy_unregister()` waits for open interfaces to close, unregisters rfkill, removes the wiphy from userspace visibility, deletes debugfs and the RCU list entry, deregisters regulatory state, deletes the device, drains work, and frees auxiliary cfg80211 state. The netdevice notifier initializes wdevs on post-init, registers/unregisters interfaces, handles going-down leave/disconnect/scan cancellation, updates running counters on up/down, rejects pre-up when iftype or rfkill constraints fail, and handles WEXT or mesh compatibility starts.

Module init registers pernet operations, sysfs, netdevice notifier, nl80211, debugfs, regulatory support, and the ordered cfg80211 workqueue. Exit reverses those registrations.

## State and persistence
State is in memory: registered wiphys, wdev lists, opencounts, scan and scheduled scan requests, rfkill state, BSS lists, work queues, management registrations, DFS background work, and per-wdev event lists. There is no persistent storage, but sysfs/debugfs/netlink expose live state.

## Dependencies and integration points
This file integrates with nl80211, sysfs, debugfs, rfkill, regulatory core, netdevice notifier, pernet operations, WEXT compatibility, driver `cfg80211_ops`, and all mode-specific helpers. RTNL, wiphy mutexes, RCU, spinlocks, workqueues, delayed work, and hrtimers are central synchronization primitives.

## Risks
Registration ordering is high risk because userspace visibility must not occur before validation and initialization are complete. Unregister must drain work after removing discoverability to prevent use-after-free. Netdev notifier paths must balance opencount and running interface counters and must cancel scans, scheduled scans, CAC, PMSR, and disconnect work. Multi-radio and MLO paths add validation complexity.

## Test signals
Coverage should include wiphy registration failure injection, invalid capability matrices, namespace switching rollback, rfkill shutdown, netdev up/down/unregister, pending scan cancellation, workqueue cancellation/flush, module init failure unwinds, and debugfs/regulatory/nl80211 notification ordering.
